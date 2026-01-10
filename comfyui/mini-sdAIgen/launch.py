import sys
import os
import json
from pathlib import Path

# Ensure we can import local modules
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from core.parser import parse_empowerment_text
from core.downloader import Downloader
from ui.widgets import show_widgets

SETTINGS_PATH = Path('settings.json')

def run_download():
    if not SETTINGS_PATH.exists():
        print("No settings.json found! Please configure widgets and save first.")
        return

    with open(SETTINGS_PATH, 'r') as f:
        settings = json.load(f)

    # 1. Parse Text
    text = settings.get('empowerment_text', '')
    if not text:
        print("No Empowerment text found. Skipping downloads.")
    else:
        print("Parsing Empowerment text...")
        items = parse_empowerment_text(text)
        print(f"Found {len(items)} items to download.")
        
        # 2. Initialize Downloader
        tokens = {
            'huggingface': settings.get('huggingface_token'),
            'civitai': settings.get('civitai_token')
        }
        downloader = Downloader(api_tokens=tokens)
        
        # 3. Execute
        downloader.download_batch(items)
        
    print("Download process finished.")

if __name__ == "__main__":
    pass
