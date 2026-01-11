import os
import subprocess
import sys
from pathlib import Path

def install_system_deps():
    if sys.platform == "linux":
        # 1. Aria2c
        try:
            subprocess.run(["aria2c", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Installing aria2c...")
            subprocess.run(["apt-get", "update", "-qq"], check=True)
            subprocess.run(["apt-get", "install", "-y", "-qq", "aria2"], check=True)
            
        # 2. Upgrade libstdc++6 for SageAttention (GLIBCXX fix)
        # We run this blindly or check if we can. Just running install is safe and fast if already newest.
        try:
             # Check if we have the PPA (hacky check, or just add it always - it's idempotent-ish)
             # To be safe and fast, we only do this if we suspect we need it. 
             # Let's just do it. It adds ~5-10s but ensures SageAttention works.
             print("Ensuring latest libstdc++6...")
             subprocess.run(["add-apt-repository", "-y", "ppa:ubuntu-toolchain-r/test"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
             subprocess.run(["apt-get", "install", "-y", "-qq", "libstdc++6"], check=True)
        except Exception:
             pass # Might fail if not root or apt locked, but we try.

def install_python_deps():
    print("Installing Python dependencies...")
    reqs = ["ipywidgets", "gdown"]
    # Quiet install
    subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + reqs, check=True)
    # Enable widgets extension quietly
    subprocess.run(["jupyter", "nbextension", "enable", "--py", "widgetsnbextension"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def setup_environment():
    # 1. Detect Environment
    if os.path.exists("/kaggle/working"):
        print("Detected Kaggle environment.")
    elif os.path.exists("/content"):
        print("Detected Colab environment.")
    else:
        print("Detected Local/Other environment.")

    # 2. Install Deps
    install_system_deps()
    install_python_deps()
    
    # 3. Install ComfyUI if missing
    comfy_path = Path("/root/ComfyUI")
    if not comfy_path.exists():
        if sys.platform == "linux":
            print("Installing ComfyUI...")
            subprocess.run(["git", "clone", "-q", "https://github.com/comfyanonymous/ComfyUI", str(comfy_path)], check=True)
            
            # Smart Dependency Install
            req_path = comfy_path / "requirements.txt"
            if req_path.exists():
                print("Installing ComfyUI Dependencies...")
                with open(req_path, 'r') as f:
                    reqs = f.readlines()
                
                filtered_reqs = []
                for r in reqs:
                    pkg = r.strip().split('=')[0].split('<')[0].split('>')[0]
                    # Filter out heavy/pre-installed packages
                    if pkg.lower() not in ['torch', 'torchvision', 'torchaudio', 'cupy-cuda12x', 'cupy-cuda11x']:
                         filtered_reqs.append(r)
                
                temp_reqs = Path("temp_reqs.txt")
                with open(temp_reqs, 'w') as f:
                    f.writelines(filtered_reqs)
                
                subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(temp_reqs)], check=True)
                temp_reqs.unlink()

            # Fix SQLAlchemy (Always run on fresh install)
            print("Fixing SQLAlchemy...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "sqlalchemy", "--upgrade", "--force-reinstall"], check=True)

    # 4. Check & Install Custom Nodes (Runs even if ComfyUI exists)
    if comfy_path.exists():
        custom_nodes = comfy_path / "custom_nodes"
        
        # A. ComfyUI-Manager
        manager_path = custom_nodes / "ComfyUI-Manager"
        if not manager_path.exists():
            print("Installing ComfyUI-Manager...")
            subprocess.run(["git", "clone", "-q", "https://github.com/ltdrdata/ComfyUI-Manager", str(manager_path)], check=True)
        # Always check Manager reqs
        man_reqs = manager_path / "requirements.txt"
        if man_reqs.exists():
             subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(man_reqs)], check=False)

        # B. SeedVR2 Upscaler
        seed_path = custom_nodes / "ComfyUI-SeedVR2_VideoUpscaler"
        if not seed_path.exists():
            print("Installing SeedVR2 Upscaler...")
            subprocess.run(["git", "clone", "-q", "https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler", str(seed_path)], check=True)
        # Always check SeedVR reqs
        seed_reqs = seed_path / "requirements.txt"
        if seed_reqs.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(seed_reqs)], check=False)

    # 5. Helper Libraries (PyNgrok, Triton)
    print("Checking Essential Libraries...")
    
    # Check Environment & Downgrade if needed
    try:
        import torch
        print(f"Current Environment: Torch {torch.__version__} | CUDA {torch.version.cuda}")
        
        # Downgrade 2.8/2.9+ to 2.7.1 (Stable)
        if "2.8" in torch.__version__ or "2.9" in torch.__version__:
            print(f">> Detected unstable PyTorch {torch.__version__}. Downgrading to 2.7.1+cu126 for stability...")
            # Uninstall current
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio", "xformers"], check=False)
            
            # Install Stable 2.7.1 (CUDA 12.6)
            install_cmd = [
                sys.executable, "-m", "pip", "install", 
                "torch==2.7.1", "torchvision==0.22.1", "torchaudio==2.7.1", 
                "--index-url", "https://download.pytorch.org/whl/cu126"
            ]
            subprocess.run(install_cmd, check=True)
            print(">> PyTorch downgraded to 2.7.1 successfully.")
            print(">> IMPORTANT: You MUST restart the Jupyter Kernel after this setup.")
            
    except ImportError:
        print("Environment: Torch not imported.")

    # PyNgrok
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyngrok"], check=True)
    except subprocess.CalledProcessError:
        print(">> Error installing pyngrok.")

    # Triton
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "triton>=3.0.0"], check=True)
    except subprocess.CalledProcessError:
        print(">> Error installing triton.")
        
    # Flash Attention / SageAttention / Xformers Strategy
    # User Request: Use ONLY native SDPA (Scaled Dot Product Attention).
    # We clean up any previous conflicting optimized attention libraries.
    
    print("Optimization: Using Native SDPA (Best stability).")
    try:
        # Cleanup SageAttention if present (it was causing ABI crashes)
        if importlib.util.find_spec("sageattention") is not None:
             subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "sageattention"], check=False)
             
        # Cleanup Xformers if present (User requested only SDPA)
        if importlib.util.find_spec("xformers") is not None:
             subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "xformers"], check=False)
             
    except Exception:
        pass

    print("Setup Complete. Using Native SDPA.")
    
    # 6. Pre-download SeedVR Models (Fixes Timeout Error)
    print("Pre-downloading SeedVR Models (15GB+) to avoid runtime timeouts...")
    seed_model_dir = comfy_path / "models" / "SEEDVR2"
    seed_model_dir.mkdir(parents=True, exist_ok=True)
    
    models_to_download = [
        ("seedvr2_ema_7b_fp16.safetensors", "https://huggingface.co/numz/SeedVR2_comfyUI/resolve/main/seedvr2_ema_7b_fp16.safetensors"),
        ("ema_vae_fp16.safetensors", "https://huggingface.co/numz/SeedVR2_comfyUI/resolve/main/ema_vae_fp16.safetensors")
    ]
    
    for filename, url in models_to_download:
        dest = seed_model_dir / filename
        if not dest.exists():
            print(f"Downloading {filename}...")
            try:
                subprocess.run(["aria2c", "-x", "8", "-s", "8", "-k", "1M", "-o", filename, "-d", str(seed_model_dir), url], check=True)
                print(f">> {filename} downloaded successfully.")
            except subprocess.CalledProcessError:
                print(f">> Error downloading {filename}. You may need to manual download.")
        else:
            print(f">> {filename} already exists.")

if __name__ == "__main__":
    setup_environment()
