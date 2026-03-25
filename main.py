import os

# Fix SSL certificate path for requests on Android
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
except ImportError:
    pass

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.lang import Builder

# Set global app background to dark navy
Window.clearcolor = (0.05, 0.05, 0.1, 1)

# Load all KV layout files before importing screen classes
Builder.load_file('ui/discovery_screen.kv')
Builder.load_file('ui/remote_screen.kv')
Builder.load_file('ui/apps_screen.kv')
Builder.load_file('ui/search_screen.kv')

from ui.discovery_screen import DiscoveryScreen
from ui.remote_screen import RemoteScreen
from ui.apps_screen import AppsScreen
from ui.search_screen import SearchScreen


class RokuRemoteApp(App):
    """
    Main application class.
    roku_client is set on this singleton after the user selects a device
    so that all screens can access it via App.get_running_app().roku_client
    """
    roku_client = None

    def build(self):
        self.title = "Roku Remote"
        self.icon = "assets/icon.png"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(DiscoveryScreen(name='discovery'))
        sm.add_widget(RemoteScreen(name='remote'))
        sm.add_widget(AppsScreen(name='apps'))
        sm.add_widget(SearchScreen(name='search'))
        return sm


if __name__ == '__main__':
    RokuRemoteApp().run()
