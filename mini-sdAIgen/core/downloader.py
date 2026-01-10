import subprocess
import os
from pathlib import Path

class Downloader:
    def __init__(self, api_tokens=None):
        self.api_tokens = api_tokens or {}
        
    def download_item(self, item: dict):
        url = item['url']
        destination = item['destination']
        filename = item['filename']
        
        # Create directory
        os.makedirs(destination, exist_ok=True)
        
        if 'drive.google.com' in url:
            self._download_gdown(url, destination, filename)
        else:
            self._download_aria2(url, destination, filename)

    def _download_aria2(self, url, destination, filename):
        # Basic aria2c command construction
        cmd = [
            'aria2c',
            '--console-log-level=error',
            '--summary-interval=10',
            '-c', '-x16', '-s16', '-k1M', '-j5',
            '--allow-overwrite=true',
            f'-d "{destination}"',
            f'"{url}"'
        ]
        
        # Add Authorization header if HF token present and URL is HF
        if 'huggingface.co' in url and self.api_tokens.get('huggingface'):
             cmd.insert(1, f'--header="Authorization: Bearer {self.api_tokens["huggingface"]}"')

        # Filename override
        if filename:
            cmd.append(f'-o "{filename}"')
            
        command_str = " ".join(cmd)
        print(f"Executing: {command_str}")
        try:
            subprocess.run(command_str, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading {url}: {e}")

    def _download_gdown(self, url, destination, filename):
        # gdown implementation
        # Gdown is tricky with output directories sometimes, best to CD
        # But for simplicity here, we try to use -O
        
        # If filename is NOT provided, gdown attempts to guess it.
        # If we want to save to a specific directory `destination`, 
        # `gdown` typically accepts -O <output_path> (file or dir).
        
        target = destination
        if filename:
            target = destination / filename
            
        cmd = [
            'gdown',
            '--fuzzy',
            f'"{url}"',
            '-O', f'"{target}"'
        ]
        
        command_str = " ".join(cmd)
        print(f"Executing: {command_str}")
        try:
            subprocess.run(command_str, shell=True, check=True)
        except subprocess.CalledProcessError as e:
             print(f"Error downloading {url}: {e}")

    def download_batch(self, items: list):
        print(f"Starting batch download of {len(items)} items...")
        for item in items:
            self.download_item(item)
