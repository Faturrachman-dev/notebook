import ipywidgets as widgets
from IPython.display import display, clear_output
import json
from pathlib import Path

SETTINGS_PATH = Path('settings.json')

class MiniWidgets:
    def __init__(self):
        self.header = widgets.HTML("<h2>Mini-sdAIgen Configuration</h2>")
        
        # API Tokens
        self.hf_token = widgets.Text(description="HF Token:", placeholder="HuggingFace Token")
        self.civitai_token = widgets.Text(description="CivitAI Token:", placeholder="CivitAI Token")
        self.ngrok_token = widgets.Text(description="Ngrok Token:", placeholder="Ngrok Authtoken")
        
        # Empowerment Mode
        self.empowerment_label = widgets.HTML("<h3>Empowerment Mode (Custom URLs)</h3>")
        self.empowerment_text = widgets.Textarea(
            placeholder="Enter tags and URLs here...\n$unet\nhttps://...\n$lora\nhttps://...",
            layout=widgets.Layout(width='100%', height='300px')
        )
        
        # Actions
        self.save_btn = widgets.Button(
            description="Save Settings",
            button_style='success', # 'success', 'info', 'warning', 'danger' or ''
            icon='save'
        )
        self.save_btn.on_click(self.save_settings)
        
        self.output = widgets.Output()

    def display(self):
        container = widgets.VBox([
            self.header,
            self.hf_token,
            self.civitai_token,
            self.ngrok_token,
            self.empowerment_label,
            self.empowerment_text,
            self.save_btn,
            self.output
        ])
        display(container)
        self.load_settings()

    def save_settings(self, b):
        data = {
            'huggingface_token': self.hf_token.value,
            'civitai_token': self.civitai_token.value,
            'ngrok_token': self.ngrok_token.value,
            'empowerment_text': self.empowerment_text.value
        }
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(data, f, indent=4)
            
        with self.output:
            clear_output()
            print("Settings saved to settings.json!")

    def load_settings(self):
        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, 'r') as f:
                    data = json.load(f)
                    self.hf_token.value = data.get('huggingface_token', '')
                    self.civitai_token.value = data.get('civitai_token', '')
                    self.ngrok_token.value = data.get('ngrok_token', '')
                    self.empowerment_text.value = data.get('empowerment_text', '')
            except Exception as e:
                with self.output:
                    print(f"Error loading settings: {e}")

def show_widgets():
    ui = MiniWidgets()
    ui.display()
