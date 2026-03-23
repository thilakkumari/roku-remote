import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Triangle, RoundedRectangle
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen


class ArrowButton(Button):
    """
    A D-pad arrow button that draws a solid triangle using Kivy canvas instructions.
    This is 100% reliable — no Unicode or font dependency.
    direction: 'up' | 'down' | 'left' | 'right'
    """
    direction = StringProperty('up')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)   # we draw our own background
        self.valign = 'bottom'
        self.halign = 'center'
        self.padding = (0, 8, 0, 6)
        self.font_size = '10sp'
        self.bold = True
        self.color = (0.55, 0.55, 0.72, 1)     # subtle label colour
        self.bind(pos=self._redraw, size=self._redraw, direction=self._redraw)

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Button background
            Color(0.12, 0.12, 0.22, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[8])

            # Arrow triangle — drawn in the upper ~60% of the button
            Color(0.88, 0.88, 0.96, 1)
            cx = self.x + self.width / 2
            cy = self.y + self.height * 0.50    # vertical centre of button
            s = min(self.width, self.height) * 0.26  # arrow "radius"

            if self.direction == 'up':
                Triangle(points=[
                    cx,       cy + s,
                    cx - s,   cy - s * 0.65,
                    cx + s,   cy - s * 0.65,
                ])
            elif self.direction == 'down':
                Triangle(points=[
                    cx,       cy - s,
                    cx - s,   cy + s * 0.65,
                    cx + s,   cy + s * 0.65,
                ])
            elif self.direction == 'left':
                Triangle(points=[
                    cx - s,        cy,
                    cx + s * 0.65, cy + s,
                    cx + s * 0.65, cy - s,
                ])
            elif self.direction == 'right':
                Triangle(points=[
                    cx + s,        cy,
                    cx - s * 0.65, cy + s,
                    cx - s * 0.65, cy - s,
                ])


class RemoteScreen(Screen):
    """Main remote control screen — D-pad, media controls, volume."""

    def press_key(self, key: str):
        """Send an ECP keypress in a background thread."""
        self.ids.status_label.text = f"Sending {key}..."
        threading.Thread(target=self._send_key, args=(key,), daemon=True).start()

    def _send_key(self, key: str):
        client = App.get_running_app().roku_client
        if client is None:
            Clock.schedule_once(
                lambda dt: setattr(self.ids.status_label, "text", "Not connected")
            )
            return
        success = client.keypress(key)
        msg = f"{key} sent" if success else f"{key} failed — check WiFi"
        Clock.schedule_once(lambda dt: setattr(self.ids.status_label, "text", msg))

    def go_to_apps(self):
        self.manager.current = "apps"

    def go_to_discovery(self):
        self.manager.current = "discovery"
