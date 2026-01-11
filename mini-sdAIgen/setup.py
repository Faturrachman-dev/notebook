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
        
        # Downgrade 2.8+ to 2.5.1 (Stable) for SageAttention support
        if "2.8" in torch.__version__:
            print(">> Detected unstable PyTorch 2.8. Downgrading to 2.5.1+cu124 for stability & SageAttention...")
            # Uninstall current
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"], check=False)
            
            # Install Stable 2.5.1
            install_cmd = [
                sys.executable, "-m", "pip", "install", 
                "torch==2.5.1", "torchvision==0.20.1", "torchaudio==2.5.1", 
                "--index-url", "https://download.pytorch.org/whl/cu124"
            ]
            subprocess.run(install_cmd, check=True)
            print(">> PyTorch downgraded successfully.")
            
            print(">> PyTorch downgraded successfully.")
            print(">> IMPORTANT: You MUST restart the Jupyter Kernel after this setup for changes to take effect.")
            
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
        
    # SageAttention Cleanup (Always needed to fix ABI crash)
    try:
        if importlib.util.find_spec("sageattention") is not None:
            print("Cleaning up broken SageAttention...")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "sageattention"], check=False)
            print(">> SageAttention uninstalled.")
    except Exception:
        pass

    # Flash Attention Best-Effort Install
    # Since SageAttention failed, user requested Flash Attention.
    # We try typical pre-compiled wheels for Torch 2.5 + CUDA 12.x
    print("Attempting to install Flash Attention 2...")
    
    fa_urls = [
         # Official Dao-AILab (v2.7.0.post2 for cu123 - usually compat with 12.4)
         "https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.0.post2/flash_attn-2.7.0.post2+cu123torch2.5cxx11abiFALSE-cp312-cp312-linux_x86_64.whl",
         # Kijai's Wheel (Guessing filename based on patterns)
         "https://huggingface.co/Kijai/PrecompiledWheels/resolve/main/flash_attn-2.7.0.post2+cu124torch2.5.1cxx11abiFALSE-cp312-cp312-linux_x86_64.whl" 
    ]
    
    local_fa_wheel = "flash_attn.whl"
    fa_installed = False
    
    import importlib.util
    if importlib.util.find_spec("flash_attn") is None:
        for url in fa_urls:
            try:
                print(f"Downloading FlashAttn wheel: {url} ...")
                subprocess.run(["aria2c", "-q", "-x", "4", "-o", local_fa_wheel, url], check=True)
                
                print(f"Installing {local_fa_wheel}...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-q", local_fa_wheel], check=True)
                print(">> Flash Attention installed successfully!")
                fa_installed = True
                Path(local_fa_wheel).unlink(missing_ok=True)
                break
            except subprocess.CalledProcessError:
                print("   -> Failed (Download or Install error)")
                Path(local_fa_wheel).unlink(missing_ok=True)
        
        if not fa_installed:
             print(">> Warning: Flash Attention wheels failed. SeedVR will use SDPA (Native PyTorch Attention).")
    else:
        print(">> Flash Attention already installed.")

    print("Setup Complete.")

if __name__ == "__main__":
    setup_environment()
