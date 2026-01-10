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
    
    print("Setup complete! You can now run the widgets.")

if __name__ == "__main__":
    setup_environment()
