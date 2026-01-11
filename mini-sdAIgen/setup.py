import os
import subprocess
import sys
from pathlib import Path

def install_system_deps():
    if sys.platform == "linux":
        try:
            # Check aria2c quietly
            subprocess.run(["aria2c", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Installing aria2c...")
            subprocess.run(["apt-get", "update", "-qq"], check=True)
            subprocess.run(["apt-get", "install", "-y", "-qq", "aria2"], check=True)

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

    # 5. Helper Libraries (SageAttention, PyNgrok, Triton)
    print("Checking Essential Libraries...")
    
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

    # SageAttention (Install from GitHub for V2 support)
    try:
        print("Installing SageAttention (from GitHub)...")
        # Using git+https to get latest version (V2+) which might not be on PyPI
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "git+https://github.com/thu-ml/SageAttention.git", "--no-build-isolation"], check=True)
    except subprocess.CalledProcessError as e:
        print(f">> Error installing SageAttention: {e}")
        print(">> Note: SageAttention compilation requires CUDA toolkit and proper environment.")

    print("Setup Complete.")

if __name__ == "__main__":
    setup_environment()
