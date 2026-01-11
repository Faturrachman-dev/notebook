import os
import subprocess
import sys

def install_system_deps():
    print("Installing system dependencies...")
    # Check for aria2c
    try:
        subprocess.run(["aria2c", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("aria2c already installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("aria2c not found.")
        if sys.platform.startswith("linux"):
            print("Installing aria2 via apt-get...")
            subprocess.run(["apt-get", "update", "-y"], check=False)
            subprocess.run(["apt-get", "install", "-y", "aria2"], check=True)
        elif sys.platform == "win32":
            print("Please install aria2c manually on Windows (e.g., 'winget install aria2' or 'choco install aria2').")
        else:
            print("Please install aria2 manually for your OS.")

def install_python_deps():
    print("Installing Python dependencies...")
    pkgs = ["ipywidgets", "gdown"]
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + pkgs)

def setup_environment():
    # Detect environment
    if os.path.exists("/kaggle/working"):
        print("Detected Kaggle environment.")
    elif os.path.exists("/content"):
        print("Detected Colab environment.")
    else:
        print("Detected Local/Other environment.")

    install_system_deps()
    install_python_deps()
    
    # Enable widgets extension if needed (older environments)
    # subprocess.run(["jupyter", "nbextension", "enable", "--py", "widgetsnbextension"], check=False)
    
    # 3. Install ComfyUI if missing
    comfy_path = Path("/root/ComfyUI")
    if not comfy_path.exists():
        if sys.platform == "linux":
            print("Installing ComfyUI...")
            subprocess.run(["git", "clone", "https://github.com/comfyanonymous/ComfyUI", str(comfy_path)], check=True)
            
            # Smart Dependency Install
            req_path = comfy_path / "requirements.txt"
            if req_path.exists():
                print("Installing ComfyUI Dependencies (Smart)...")
                with open(req_path, 'r') as f:
                    reqs = f.readlines()
                
                filtered_reqs = []
                for r in reqs:
                    pkg = r.strip().split('=')[0].split('<')[0].split('>')[0]
                    if pkg.lower() in ['torch', 'torchvision', 'torchaudio', 'cupy-cuda12x', 'cupy-cuda11x']:
                        print(f"Skipping {pkg} (assuming pre-installed)")
                    else:
                        filtered_reqs.append(r)
                
                temp_reqs = Path("temp_reqs.txt")
                with open(temp_reqs, 'w') as f:
                    f.writelines(filtered_reqs)
                
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(temp_reqs)], check=True)
                temp_reqs.unlink()
    else:
        print("ComfyUI already installed.")

    # 4. Install ComfyUI-Manager (Always check)
    if comfy_path.exists():
        manager_path = comfy_path / "custom_nodes" / "ComfyUI-Manager"
        if not manager_path.exists():
            print("Installing ComfyUI-Manager...")
            subprocess.run(["git", "clone", "https://github.com/ltdrdata/ComfyUI-Manager", str(manager_path)], check=True)
        
        # Install Manager Requirements
        man_reqs = manager_path / "requirements.txt"
        if man_reqs.exists():
            print("Installing ComfyUI-Manager Requirements...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(man_reqs)], check=False)

        # Debug: List custom_nodes
        print(f"Contents of {comfy_path}/custom_nodes:")
        subprocess.run(["ls", "-R", str(comfy_path / "custom_nodes")], check=False)

    # 5. Apply Fixes (Always check)
    # Fix SQLAlchemy - FORCE REINSTALL
    print("Fixing SQLAlchemy...")
    subprocess.run([sys.executable, "-m", "pip", "install", "sqlalchemy", "--upgrade", "--force-reinstall"], check=True)
    
    # Install PyNgrok
    subprocess.run([sys.executable, "-m", "pip", "install", "pyngrok"], check=True)
            
    print("Setup Complete.")

if __name__ == "__main__":
    setup_environment()
