import json
import os

MAX_HISTORY = 10


def _path() -> str:
    from kivy.app import App
    return os.path.join(App.get_running_app().user_data_dir, "search_history.json")


def load() -> list:
    """Return list of recent searches, newest first."""
    try:
        with open(_path()) as f:
            return json.load(f)
    except Exception:
        return []


def add(text: str) -> None:
    """Add a search term, remove duplicates, keep newest MAX_HISTORY entries."""
    history = load()
    history = [h for h in history if h.lower() != text.lower()]  # remove duplicate
    history.insert(0, text)                                        # newest first
    history = history[:MAX_HISTORY]
    with open(_path(), "w") as f:
        json.dump(history, f)
