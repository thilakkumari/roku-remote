import time
import urllib.parse
import requests
import xml.etree.ElementTree as ET
from typing import List

from .models import RokuDevice, RokuApp


class RokuClient:
    """Wraps all Roku ECP (External Control Protocol) REST API calls."""

    def __init__(self, device: RokuDevice, timeout: int = 3):
        self.device = device
        self.timeout = timeout

    def keypress(self, key: str) -> bool:
        """Send a single keypress to the Roku. Returns True on success."""
        try:
            r = requests.post(
                f"{self.device.base_url}/keypress/{key}",
                timeout=self.timeout
            )
            return r.status_code == 200
        except requests.RequestException:
            return False

    def send_text(self, text: str, char_delay: float = 0.05) -> bool:
        """Type a string on the Roku one character at a time via Lit_ keypresses."""
        for char in text:
            encoded = urllib.parse.quote(char, safe='')
            if not self.keypress(f"Lit_{encoded}"):
                return False
            if char_delay > 0:
                time.sleep(char_delay)
        return True

    def get_apps(self) -> List[RokuApp]:
        """Return the list of all installed apps/channels."""
        try:
            r = requests.get(
                f"{self.device.base_url}/query/apps",
                timeout=self.timeout
            )
            r.raise_for_status()
            root = ET.fromstring(r.text)
            return [
                RokuApp(
                    app_id=app.get('id', ''),
                    name=app.text or '',
                    version=app.get('version', '')
                )
                for app in root.findall('app')
            ]
        except Exception:
            return []

    def launch_app(self, app_id: str) -> bool:
        """Launch an app by its ID. Returns True on success."""
        try:
            r = requests.post(
                f"{self.device.base_url}/launch/{app_id}",
                timeout=self.timeout
            )
            return r.status_code == 200
        except requests.RequestException:
            return False

    def get_device_info(self) -> dict:
        """Return basic device info as a dictionary."""
        try:
            r = requests.get(
                f"{self.device.base_url}/query/device-info",
                timeout=self.timeout
            )
            root = ET.fromstring(r.text)
            return {child.tag: child.text for child in root}
        except Exception:
            return {}
