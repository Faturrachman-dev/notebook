# Technical Research Summary

## 1. Widget System (`widgets-en.py`)
The user interface is built using `ipywidgets` and injected directly into the notebook cell.

### Data Flow
1.  **Selection**: Users interact with dropdowns (Models, VAEs) and checkboxes.
2.  **Configuration**: The state is aggregated into a dictionary.
3.  **Persistence**: Clicking "Save" serializes this dictionary to a `settings.json` file.
4.  **Execution**: Subsequent scripts read this JSON to know what to do.

### "Empowerment" Mode
This is a custom-built parser found in `widgets.py`. It switches the UI from discrete fields to a single `TextArea`.
*   **Purpose**: Allows efficient batch pasting of links from sites like CivitAI.
*   **Parsing Logic**:
    *   Detects "tags" beginning with `$` (e.g., `$ckpt`, `$lora`, `$ext`).
    *   Associates all subsequent URLs with that tag until a new tag is found.
    *   These tags map directly to target directories defined in `downloading-en.py`.

## 2. Download Manager (`modules/Manager.py`)
An advanced wrapper around command-line download tools.

### Strategies
*   **Aria2c**: The default for most URLs. Configured with 16 connections (`-x16`) and split downloading (`-s16`) for optimal speed in cloud environments.
*   **Gdown**: Specifically triggered for `drive.google.com` links to handle Google Drive's cookies and confirmation prompts.
*   **Curl**: A fallback mechanism.

### Features
*   **Auto-Unzip**: Detects `.zip` extensions and automatically extracts them to a folder of the same name.
*   **CivitAI Integration**: 
    *   Uses `CivitaiAPI.py` to validate tokens.
    *   Fetches metadata (filename, preview image).
    *   Automatically downloads preview images alongside models if running in ComfyUI mode.
*   **Symlink Management**: For Colab users, it creates symlinks to Google Drive (`/content/drive/MyDrive/sdAIgen`) to persist models across runtime resets.

## 3. ComfyUI Specifics
The system has special handling for ComfyUI:
*   **Custom Nodes**: The "Extensions" tag (`$ext`) logic detects git repositories and clones them into `custom_nodes`.
*   **Model Paths**: It ensures models are placed in the specific `models/checkpoints`, `models/loras`, etc., expected by ComfyUI's folder structure.
*   **Updates**: It includes logic to check for dependency updates (`requirements.txt`) specifically for custom nodes.
