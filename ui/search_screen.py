import threading
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from roku import search_history

# ── Android speech recognizer (graceful desktop fallback) ─────────────────────
try:
    from jnius import autoclass, cast
    from android.activity import bind as activity_bind
    from android.activity import unbind as activity_unbind

    Intent           = autoclass('android.content.Intent')
    RecognizerIntent = autoclass('android.speech.RecognizerIntent')
    Activity         = autoclass('org.kivy.android.PythonActivity')

    _SPEECH_AVAILABLE = True
except ImportError:
    _SPEECH_AVAILABLE = False

_SPEECH_REQUEST_CODE = 42


class SearchScreen(Screen):
    """
    Type text or speak via the Android mic and send it to the Roku
    character-by-character using Lit_ ECP keypresses.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sending = False
        self._last_sent = ""  # tracks text from previous send in this session

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_enter(self):
        self._set_status("Type or speak your search, then tap Send.")
        self.ids.search_input.focus = True
        self.ids.mic_button.disabled = not _SPEECH_AVAILABLE
        self._load_history()
        if _SPEECH_AVAILABLE:
            activity_bind(on_activity_result=self._on_speech_result)
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.RECORD_AUDIO])
            except Exception:
                pass

    def on_leave(self):
        if _SPEECH_AVAILABLE:
            try:
                activity_unbind(on_activity_result=self._on_speech_result)
            except Exception:
                pass

    # ── Button callbacks ──────────────────────────────────────────────────────

    def do_send(self):
        if self._sending:
            return
        text = self.ids.search_input.text.strip()
        if not text:
            self._set_status("Nothing to send — type something first.")
            return
        self._sending = True
        self.ids.search_input.text = ""  # clear immediately to block any duplicate trigger
        self.ids.send_button.disabled = True
        self._set_status(f"Sending '{text}'…")
        threading.Thread(target=self._send_worker, args=(text,), daemon=True).start()

    def do_mic(self):
        if not _SPEECH_AVAILABLE:
            self._set_status("Microphone is only available on Android.")
            return
        self._set_status("Listening…")
        try:
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Say what you want to search for")
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            current_activity = cast('android.app.Activity', Activity.mActivity)
            current_activity.startActivityForResult(intent, _SPEECH_REQUEST_CODE)
        except Exception as e:
            self._set_status(f"Could not open microphone: {e}")

    def do_clear(self):
        self.ids.search_input.text = ""
        self._set_status("Cleared.")

    def do_clear_history(self):
        search_history.clear()
        self._load_history()
        self._set_status("History cleared.")

    def go_back(self):
        self.manager.current = "remote"

    # ── Background worker ─────────────────────────────────────────────────────

    def _send_worker(self, text: str):
        client = App.get_running_app().roku_client
        if client is None:
            Clock.schedule_once(lambda dt: self._finish_send(False, "Not connected to a Roku."))
            return
        # Second search onwards: clear previous text + a buffer for any TV autocomplete chars
        if self._last_sent:
            for _ in range(len(self._last_sent) + 20):
                client.keypress("Backspace")

        ok = client.send_text(text)
        if ok:
            self._last_sent = text
            search_history.add(text)
        msg = f"Done — press OK on remote to search" if ok else "Send failed — check WiFi and try again."
        Clock.schedule_once(lambda dt: self._finish_send(ok, msg))

    def _finish_send(self, ok: bool, msg: str):
        self._sending = False
        self.ids.send_button.disabled = False
        self._set_status(msg)

    # ── Android speech result ─────────────────────────────────────────────────

    def _on_speech_result(self, request_code, result_code, intent_data):
        if request_code != _SPEECH_REQUEST_CODE:
            return
        RESULT_OK = -1
        if result_code != RESULT_OK or intent_data is None:
            Clock.schedule_once(lambda dt: self._set_status("No speech detected. Try again."))
            return
        try:
            results = intent_data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if results and results.size() > 0:
                spoken = results.get(0)
                Clock.schedule_once(lambda dt: self._fill_from_speech(spoken))
            else:
                Clock.schedule_once(lambda dt: self._set_status("Could not understand. Try again."))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._set_status(f"Speech error: {e}"))

    def _fill_from_speech(self, text: str):
        self.ids.search_input.text = text
        self._set_status(f"Heard: '{text}' — tap Send to type it on your TV.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _load_history(self):
        self.ids.history_list.clear_widgets()
        for term in search_history.load():
            btn = Button(
                text=term,
                size_hint_y=None,
                height="44dp",
                font_size="14sp",
                bold=False,
                background_normal='',
                background_down='',
                background_color=(0.1, 0.1, 0.2, 1),
                color=(0.75, 0.75, 0.9, 1),
                halign="left",
            )
            btn.bind(
                size=lambda w, s: setattr(w, "text_size", (s[0] - 24, s[1])),
                on_press=lambda _, t=term: self._fill_history(t),
            )
            self.ids.history_list.add_widget(btn)

    def _fill_history(self, text: str):
        self.ids.search_input.text = text
        self._set_status(f"Tap Send to search for '{text}'")

    def _set_status(self, msg: str):
        self.ids.status_label.text = msg
