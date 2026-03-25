import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen
from roku import usage


class AppCard(ButtonBehavior, BoxLayout):
    """A tappable card showing a channel logo on top and name below."""

    def __init__(self, app, base_url, launch_cb, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = "110dp"
        self.padding = "6dp"
        self.spacing = "4dp"

        # Dark card background
        with self.canvas.before:
            Color(0.1, 0.1, 0.2, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Channel logo
        icon_url = f"{base_url}/query/icon/{app.app_id}"
        logo = AsyncImage(
            source=icon_url,
            size_hint_y=0.65,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(logo)

        # Channel name
        name_label = Label(
            text=app.name,
            font_size="12sp",
            bold=True,
            color=(0.88, 0.88, 0.95, 1),
            size_hint_y=0.35,
            halign="center",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        name_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.add_widget(name_label)

        self.bind(on_press=lambda _: launch_cb(app))

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


class AppsScreen(Screen):
    """Shows all installed Roku channels with logo + name. Tap to launch."""

    def on_enter(self):
        self.ids.status_label.text = "Loading apps..."
        self.ids.apps_grid.clear_widgets()
        threading.Thread(target=self._load_apps, daemon=True).start()

    def _load_apps(self):
        client = App.get_running_app().roku_client
        apps = client.get_apps() if client else []
        Clock.schedule_once(lambda dt: self._show_apps(apps))

    def _show_apps(self, apps):
        if not apps:
            self.ids.status_label.text = "Could not load apps — check WiFi"
            return

        client = App.get_running_app().roku_client
        base_url = client.device.base_url if client else ""

        self.ids.status_label.text = f"{len(apps)} apps installed"
        counts = usage.load()
        for app in sorted(apps, key=lambda a: (-counts.get(a.app_id, 0), a.name.lower())):
            card = AppCard(app=app, base_url=base_url, launch_cb=self._launch)
            self.ids.apps_grid.add_widget(card)

    def _launch(self, app):
        self.ids.status_label.text = f"Launching {app.name}..."
        usage.increment(app.app_id)
        client = App.get_running_app().roku_client
        threading.Thread(
            target=lambda: client.launch_app(app.app_id),
            daemon=True
        ).start()
        self.manager.current = "remote"

    def go_back(self):
        self.manager.current = "remote"
