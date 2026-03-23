import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from roku.discovery import discover_rokus
from roku.client import RokuClient


class DiscoveryScreen(Screen):
    """
    First screen shown at app launch.
    Scans the local WiFi network for Roku devices via SSDP,
    then lets the user select one to control.
    """

    def on_enter(self):
        """Auto-start discovery when this screen becomes active."""
        self.start_discovery()

    def start_discovery(self):
        self.ids.status_label.text = "Searching for Roku devices..."
        self.ids.device_list.clear_widgets()
        # Network calls MUST run in a background thread — never block Kivy's UI thread
        threading.Thread(target=self._run_discovery, daemon=True).start()

    def _run_discovery(self):
        devices = discover_rokus(timeout=5.0)
        # UI updates MUST go back to the main thread via Clock.schedule_once
        Clock.schedule_once(lambda dt: self._show_devices(devices))

    def _show_devices(self, devices):
        if not devices:
            self.ids.status_label.text = (
                "No Roku found.\n\n"
                "Make sure your phone and Roku\n"
                "are on the same WiFi network,\n"
                "then tap Search again."
            )
            return

        # Auto-connect if there's only one device — no need to make the user tap
        if len(devices) == 1:
            self._select_device(devices[0])
            return

        self.ids.status_label.text = f"Found {len(devices)} device(s) — tap to connect"
        for device in devices:
            btn = Button(
                text=str(device),
                size_hint_y=None,
                height="56dp",
                font_size="16sp",
                bold=True,
                background_normal='',
                background_down='',
                background_color=(0.12, 0.12, 0.22, 1),
                color=(0.92, 0.92, 0.96, 1)
            )
            btn.bind(on_press=lambda x, d=device: self._select_device(d))
            self.ids.device_list.add_widget(btn)

    def _select_device(self, device):
        app = App.get_running_app()
        app.roku_client = RokuClient(device)
        self.manager.current = "remote"
