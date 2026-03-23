import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen


class AppsScreen(Screen):
    """
    Shows all installed Roku channels/apps.
    Tapping an app sends a launch command to the Roku.
    """

    def on_enter(self):
        """Load apps every time this screen is opened."""
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

        self.ids.status_label.text = f"{len(apps)} apps installed"
        for app in sorted(apps, key=lambda a: a.name.lower()):
            btn = Button(
                text=app.name,
                size_hint_y=None,
                height="56dp",
                font_size="14sp",
                bold=True,
                background_normal='',
                background_down='',
                background_color=(0.1, 0.1, 0.2, 1),
                color=(0.88, 0.88, 0.95, 1)
            )
            btn.bind(on_press=lambda x, a=app: self._launch(a))
            self.ids.apps_grid.add_widget(btn)

    def _launch(self, app):
        self.ids.status_label.text = f"Launching {app.name}..."
        client = App.get_running_app().roku_client
        threading.Thread(
            target=lambda: client.launch_app(app.app_id),
            daemon=True
        ).start()

    def go_back(self):
        self.manager.current = "remote"
