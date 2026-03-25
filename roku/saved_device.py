import json
import os


def _path() -> str:
    from kivy.app import App
    return os.path.join(App.get_running_app().user_data_dir, "saved_device.json")


def save(device) -> None:
    with open(_path(), "w") as f:
        json.dump({"name": device.name, "ip": device.ip, "port": device.port}, f)


def load():
    """Return saved RokuDevice or None if nothing saved."""
    try:
        with open(_path()) as f:
            data = json.load(f)
        from roku.models import RokuDevice
        return RokuDevice(name=data["name"], ip=data["ip"], port=data.get("port", 8060))
    except Exception:
        return None


def clear() -> None:
    try:
        os.remove(_path())
    except Exception:
        pass
