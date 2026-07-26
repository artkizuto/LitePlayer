import json
import os

FILE = "settings.json"

DEFAULT = {
    "volume": 50,
    "shuffle": False,
    "loop": False,
    "playlists": [],
    "background_type": "app_default",
    "background_file": "",
    "background_color": "#808080",
    "background_opacity": 20,
    "background_mode": "Fit",
    "developer_unlocked": False
}


def load_settings():
    # Start with a copy of the default settings
    settings = DEFAULT.copy()
    
    if not os.path.exists(FILE):
        return settings
        
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            user_settings = json.load(f)
            
        # Merge loaded settings with defaults. 
        # Missing keys in the JSON will automatically fall back to DEFAULT.
        for key in DEFAULT:
            if key in user_settings:
                settings[key] = user_settings[key]
                
        return settings
    except Exception:
        return settings


def save_settings(settings):
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving settings: {e}")


def is_developer_unlocked():
    return load_settings().get("developer_unlocked", False)


def set_developer_unlocked(value: bool):
    settings = load_settings()
    settings["developer_unlocked"] = value
    save_settings(settings)