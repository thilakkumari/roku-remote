import json
import os


def _path() -> str:
    from kivy.app import App
    return os.path.join(App.get_running_app().user_data_dir, "app_usage.json")


def load() -> dict:
    """Return {app_id: launch_count} dict. Returns empty dict on any error."""
    try:
        with open(_path()) as f:
            return json.load(f)
    except Exception:
        return {}


def increment(app_id: str) -> None:
    """Increment the launch count for app_id and save to disk."""
    counts = load()
    counts[app_id] = counts.get(app_id, 0) + 1
    with open(_path(), "w") as f:
        json.dump(counts, f)
