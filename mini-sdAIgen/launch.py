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

# Environment Detection
def detect_environment():
    if Path('/kaggle/working').exists():
        return 'Kaggle', Path('/kaggle/working')
    elif Path('/content').exists():
        return 'Colab', Path('/content')
    else:
        return 'Local', Path('.')

ENV_NAME, ROOT_DIR = detect_environment()
print(f"Detected Environment: {ENV_NAME}")

# Update core paths dynamically
import core.paths
core.paths.DEFAULT_COMFY_ROOT = ROOT_DIR / "ComfyUI"
core.paths.DEFAULT_MODELS_ROOT = core.paths.DEFAULT_COMFY_ROOT / "models"
core.paths.DEFAULT_NODES_ROOT = core.paths.DEFAULT_COMFY_ROOT / "custom_nodes"

# Re-map the PREFIX_MAP with new roots
core.paths.PREFIX_MAP = {
    '$unet': core.paths.DEFAULT_MODELS_ROOT / "unet",
    '$clip': core.paths.DEFAULT_MODELS_ROOT / "clip",
    '$vae': core.paths.DEFAULT_MODELS_ROOT / "vae",
    '$lora': core.paths.DEFAULT_MODELS_ROOT / "loras",
    '$cnet': core.paths.DEFAULT_MODELS_ROOT / "controlnet",
    '$ups': core.paths.DEFAULT_MODELS_ROOT / "upscale_models",
    '$ad': core.paths.DEFAULT_MODELS_ROOT / "adetailer",
    '$vis': core.paths.DEFAULT_MODELS_ROOT / "clip_vision",
    '$ext': core.paths.DEFAULT_NODES_ROOT, 
    '$emb': core.paths.DEFAULT_MODELS_ROOT / "embeddings",
    '$diff': core.paths.DEFAULT_MODELS_ROOT / "diffusers",
}

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

def start_comfyui():
    """Starts ComfyUI with optional Ngrok tunnel"""
    
    # 1. Setup Ngrok if token exists
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            ngrok_token = settings.get('ngrok_token')
            
        if ngrok_token:
            print("Starting Ngrok Tunnel...")
            try:
                from pyngrok import ngrok, conf
                conf.get_default().auth_token = ngrok_token
                public_url = ngrok.connect(8188).public_url
                print(f"\n>>> ComfyUI Public URL: {public_url} <<<\n")
            except ImportError:
                 print("PyNgrok not installed. Tunnel skipped.")
            except Exception as e:
                print(f"Ngrok Error: {e}")
        else:
            print("No Ngrok token found. Local access only.")

    # 2. Launch ComfyUI
    comfy_main = core.paths.DEFAULT_COMFY_ROOT / "main.py"
    if comfy_main.exists():
        print(f"Launching ComfyUI from {comfy_main}...")
        # Use subprocess to run it, effectively blocking this script
        # In a notebook, we might want to run this in a cell directly, but 
        # for a script-based approach, this is how we do it.
        # We use sys.executable to ensure we use the same python
        import subprocess
        import sys
        
        args = [sys.executable, str(comfy_main), "--listen", "--port", "8188"]
        subprocess.run(args)
    else:
        print(f"ComfyUI main.py not found at {comfy_main}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--launch":
        start_comfyui()
    else:
        run_download()
