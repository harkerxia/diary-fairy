import os
import json
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "configs", "bot_config.json")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts", "bot_prompts")

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = json.load(file)

def load_prompt(filename):
    path = os.path.join(PROMPTS_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

BASE_SYSTEM_PROMPT = load_prompt("system_prompt.md") + "\n\n"
IMAGE_PROMPT = load_prompt("image_prompt.md") + "\n\n"
MINI_SUMMARY_PROMPT = load_prompt("mini_summary_prompt.md") + "\n\n"
MEGA_SUMMARY_PROMPT = load_prompt("mega_summary_prompt.md") + "\n\n"

DIRS = {k: (v if os.path.isabs(v) else os.path.join(BASE_DIR, v)) for k, v in config["path"].items()}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)
    