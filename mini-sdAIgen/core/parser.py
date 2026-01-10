import re
from pathlib import Path
from .paths import PREFIX_MAP

def parse_empowerment_text(text: str) -> list:
    """
    Parses the text from the Empowerment widget.
    
    Args:
        text (str): Multiline string containing tags and URLs.
                   Example:
                   $unet
                   https://site.com/model.safetensors
                   $lora
                   https://site.com/lora.safetensors[my_lora.safetensors]
                   
    Returns:
        list: A list of dictionaries, each containing:
              {
                  'url': str,
                  'destination': Path,
                  'filename': str or None
              }
    """
    lines = text.split('\n')
    current_destination = None
    results = []
    
    # Pre-compile regex for filename extraction [filename]
    filename_pattern = re.compile(r'\[(.*?)\]$') # Match [content] at end of string

    for line in lines:
        line = line.strip()
        
        # Skip empty lines and full comments
        if not line or line.startswith('#'):
            continue
            
        # Remove inline comments (e.g. "url # comment")
        # Be careful not to remove # in URLs if that's possible (rare but good to be safe)
        # For now, simple split on space+# might be safer than just #
        if ' #' in line:
            line = line.split(' #')[0].strip()
        elif line.startswith('#'): # Handle case where # was at start (already handled but safe)
            continue
            
        # Check for tags
        if line.startswith('$'):
            # Allow for tag params potentially in future, but for now exact match
            tag = line.split()[0] 
            if tag in PREFIX_MAP:
                current_destination = PREFIX_MAP[tag]
                continue
        
        # If we have a destination, treat as URL
        if current_destination:
            # Handle [filename] syntax
            filename = None
            match = filename_pattern.search(line)
            if match:
                filename = match.group(1)
                line = line[:match.start()].strip() # Remove the [filename] part from URL
            
            # Simple validation: looks like a URL?
            if line.startswith('http'):
                results.append({
                    'url': line,
                    'destination': current_destination,
                    'filename': filename
                })
                
    return results
