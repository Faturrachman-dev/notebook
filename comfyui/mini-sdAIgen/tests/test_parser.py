import unittest
from pathlib import Path
import sys
import os

# Add parent directory to path so we can import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.paths import PREFIX_MAP, DEFAULT_MODELS_ROOT
# We haven't created this yet, so this test file will fail to import if we ran it now
# from core.parser import parse_empowerment_text

class TestTagParser(unittest.TestCase):
    def setUp(self):
        # We will import here to avoid import errors before the file exists
        from core.parser import parse_empowerment_text
        self.parse = parse_empowerment_text

    def test_single_tag_single_url(self):
        text = """
        $ckpt
        https://example.com/model.safetensors
        """
        # Note: In our simplified version, $ckpt is not in the requested list map 
        # from url-instruction.md ($unet is), but let's assume we map standard ones too 
        # or stick strictly to the user request.
        # Let's test with a requested tag.
        text = """
        $unet
        https://example.com/model.safetensors
        """
        result = self.parse(text)
        expected_dir = PREFIX_MAP['$unet']
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['url'], 'https://example.com/model.safetensors')
        self.assertEqual(result[0]['destination'], expected_dir)

    def test_multiple_tags(self):
        text = """
        $lora
        https://site.com/lora1.safetensors
        https://site.com/lora2.safetensors
        
        $cnet
        https://site.com/controlnet.pth
        """
        result = self.parse(text)
        self.assertEqual(len(result), 3)
        
        # Check loras
        loras = [x for x in result if x['destination'] == PREFIX_MAP['$lora']]
        self.assertEqual(len(loras), 2)
        
        # Check cnet
        cnets = [x for x in result if x['destination'] == PREFIX_MAP['$cnet']]
        self.assertEqual(len(cnets), 1)

    def test_custom_filename_syntax(self):
        # sdAIgen supports [filename.ext] syntax
        text = """
        $lora
        https://site.com/badname[goodname.safetensors]
        """
        result = self.parse(text)
        self.assertEqual(result[0]['filename'], 'goodname.safetensors')
        self.assertEqual(result[0]['url'], 'https://site.com/badname')

    def test_comments_and_empty_lines(self):
        text = """
        # This is a comment
        $vae
             
        https://site.com/vae.pt  # Inline comment
        """
        result = self.parse(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['url'], 'https://site.com/vae.pt')

if __name__ == '__main__':
    unittest.main()
