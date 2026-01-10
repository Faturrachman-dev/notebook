import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We will implement this nexxt
from core.downloader import Downloader

class TestDownloader(unittest.TestCase):
    def setUp(self):
        self.downloader = Downloader()

    @patch('subprocess.run')
    def test_aria2_command_generation_standard(self, mock_run):
        item = {
            'url': 'https://example.com/model.safetensors',
            'destination': Path('/root/models/unet'),
            'filename': None
        }
        self.downloader.download_item(item)
        
        # Verify subprocess called
        self.assertTrue(mock_run.called)
        args, _ = mock_run.call_args
        command = args[0]
        
        # Check for key aria2c flags
        self.assertIn('aria2c', command)
        self.assertIn('-x16', command) 
        self.assertIn('https://example.com/model.safetensors', command)
        # Normalize path separators for Windows/Linux compatibility in tests
        expected_path = str(Path('/root/models/unet'))
        self.assertIn(f'-d "{expected_path}"', command)

    @patch('subprocess.run')
    def test_aria2_command_with_filename(self, mock_run):
        item = {
            'url': 'https://example.com/model.safetensors',
            'destination': Path('/root/models/unet'),
            'filename': 'custom_name.safetensors'
        }
        self.downloader.download_item(item)
        
        args, _ = mock_run.call_args
        command = args[0]
        self.assertIn('-o "custom_name.safetensors"', command)

    @patch('subprocess.run')
    def test_gdown_command(self, mock_run):
        item = {
            'url': 'https://drive.google.com/file/d/12345/view',
            'destination': Path('/root/models/lora'),
            'filename': None
        }
        self.downloader.download_item(item)
        
        args, _ = mock_run.call_args
        command = args[0]
        
        self.assertIn('gdown --fuzzy', command)
        # GDown usually needs us to cd into the dir first, or use full paths?
        # The original code did: cd to dir, then run gdown.
        # Let's see how we implement it.
        # Ideally the test expects what we decide to implement.
        # Assuming we handle directory switching or full path output (gdown -O fullpath)

if __name__ == '__main__':
    unittest.main()
