import json
import os

APP_DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "EducationSpaceJunior")
SETTINGS_FILE = os.path.join(APP_DATA_DIR, "settings.json")

DEFAULT_URL = "https://junior.educationspace.com"
DEFAULT_PASSCODE = "1234"


def _ensure_dir():
    os.makedirs(APP_DATA_DIR, exist_ok=True)


def setup_logging():
    import sys
    _ensure_dir()
    log_file = os.path.join(APP_DATA_DIR, "debug.log")
    try:
        sys.stdout = open(log_file, "a", encoding="utf-8", buffering=1)
        sys.stderr = sys.stdout
        print("\n--- Application Start ---")
    except Exception:
        pass


def load_settings() -> dict:
    """Load all settings from disk, returning defaults if missing."""
    if not os.path.exists(SETTINGS_FILE):
        return {
            "urls": [{"label": "Education Space Junior", "url": DEFAULT_URL}],
            "passcode": DEFAULT_PASSCODE,
        }
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "urls" not in data:
            data["urls"] = [{"label": "Education Space Junior", "url": DEFAULT_URL}]
        if "passcode" not in data:
            data["passcode"] = DEFAULT_PASSCODE
        return data
    except Exception:
        return {
            "urls": [{"label": "Education Space Junior", "url": DEFAULT_URL}],
            "passcode": DEFAULT_PASSCODE,
        }


def save_settings(settings: dict):
    """Persist settings to disk."""
    _ensure_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
