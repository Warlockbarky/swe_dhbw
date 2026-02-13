import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SUPPORT = ROOT / "tests" / "support"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if SUPPORT.exists() and str(SUPPORT) not in sys.path:
    sys.path.insert(0, str(SUPPORT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class DummySettings:
    def __init__(self, initial=None):
        self.store = dict(initial or {})

    def value(self, key, default=None, type=str):
        if key not in self.store:
            return default
        val = self.store[key]
        if type is None:
            return val
        try:
            return type(val)
        except Exception:
            return val

    def setValue(self, key, value):
        self.store[key] = value

    def remove(self, key):
        keys = [k for k in self.store if k == key or k.startswith(f"{key}/")]
        for k in keys:
            self.store.pop(k, None)


class DummyStack:
    def __init__(self):
        self.current = None

    def setCurrentWidget(self, widget):
        self.current = widget


class DummyView:
    def __init__(self):
        self.errors = []
        self.items = []
        self._selected_index = -1
        self._selected_indices = []
        self._checked_indices = []
        self._all_checked = False
        self.prompt_save_path_value = ""
        self.prompt_open_file_value = ""

    def show_error(self, message):
        self.errors.append(message)

    def set_items(self, items):
        self.items = list(items)

    def get_selected_index(self):
        return self._selected_index

    def get_selected_indices(self):
        return list(self._selected_indices)

    def get_checked_indices(self):
        return list(self._checked_indices)

    def set_all_checked(self, checked: bool):
        self._all_checked = bool(checked)

    def are_all_checked(self) -> bool:
        return bool(self._all_checked)

    def prompt_save_path(self, suggested_name: str, default_dir: str = "") -> str:
        return self.prompt_save_path_value

    def prompt_open_file(self, default_dir: str = "") -> str:
        return self.prompt_open_file_value


class DummyChatView(DummyView):
    def __init__(self):
        super().__init__()
        self.chat_input = ""
        self.selected_files = []
        self.send_enabled = True
        self.temp_chat_checked = False
        self.temp_chat_enabled = True
        self.messages = []

    def clear_chat(self):
        self.messages = []

    def clear_chat_input(self):
        self.chat_input = ""

    def set_selected_files(self, names):
        self.selected_files = list(names)

    def get_chat_input(self) -> str:
        return self.chat_input

    def add_message(self, role, text, stream=False):
        self.messages.append((role, text, stream))

    def set_send_enabled(self, enabled: bool):
        self.send_enabled = bool(enabled)

    def start_loading(self):
        pass

    def stop_loading_and_stream(self, text: str):
        self.add_message("assistant", text, stream=True)

    def set_temp_chat_checked(self, checked: bool):
        self.temp_chat_checked = bool(checked)

    def set_temp_chat_enabled(self, enabled: bool):
        self.temp_chat_enabled = bool(enabled)

    def refresh_message_sizes(self):
        pass


@pytest.fixture()
def dummy_settings():
    return DummySettings()


@pytest.fixture()
def dummy_view():
    return DummyView()


@pytest.fixture()
def dummy_chat_view():
    return DummyChatView()


@pytest.fixture()
def fake_backend():
    from fake_backend import FakeBackendServer

    server = FakeBackendServer()
    server.start()
    try:
        yield server
    finally:
        server.stop()
