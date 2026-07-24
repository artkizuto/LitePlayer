import json
import os

FILE = "settings.json"

DEFAULT = {
    "volume": 50,
    "shuffle": False,
    "loop": False,
    "playlists": []
}


def load_settings():
    if not os.path.exists(FILE):
        return DEFAULT
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT


def save_settings(settings):
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving settings: {e}")