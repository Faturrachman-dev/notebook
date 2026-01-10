from pathlib import Path

# Base paths (will be adjusted dynamically in launch.py, but defaults for testing)
DEFAULT_COMFY_ROOT = Path("/root/ComfyUI")  # Standard Kaggle/Colab path
DEFAULT_MODELS_ROOT = DEFAULT_COMFY_ROOT / "models"
DEFAULT_NODES_ROOT = DEFAULT_COMFY_ROOT / "custom_nodes"

# Tag Mapping to Directories
PREFIX_MAP = {
    '$unet': DEFAULT_MODELS_ROOT / "unet",
    '$clip': DEFAULT_MODELS_ROOT / "clip",
    '$vae': DEFAULT_MODELS_ROOT / "vae",
    '$lora': DEFAULT_MODELS_ROOT / "loras",
    '$cnet': DEFAULT_MODELS_ROOT / "controlnet",
    '$ups': DEFAULT_MODELS_ROOT / "upscale_models",
    '$ad': DEFAULT_MODELS_ROOT / "adetailer",
    '$vis': DEFAULT_MODELS_ROOT / "clip_vision",
    '$ext': DEFAULT_NODES_ROOT, 
    # Extra ones found in sdAIgen but maybe not explicitly requested, nice to have
    '$emb': DEFAULT_MODELS_ROOT / "embeddings",
    '$diff': DEFAULT_MODELS_ROOT / "diffusers",
}
