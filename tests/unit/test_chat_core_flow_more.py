from controller.chat_core_flow import chat_core_flow


class DummyChatView:
    def __init__(self):
        self.chat_input = ""
        self.messages = []
        self.send_enabled = True
        self.temp_chat_checked = False
        self.temp_chat_enabled = True

    def get_chat_input(self):
        return self.chat_input

    def clear_chat_input(self):
        self.chat_input = ""

    def add_message(self, role, text, stream=False):
        self.messages.append((role, text, stream))

    def set_send_enabled(self, enabled: bool):
        self.send_enabled = bool(enabled)

    def start_loading(self):
        pass

    def stop_loading_and_stream(self, text: str):
        self.messages.append(("assistant", text, True))

    def clear_chat(self):
        self.messages = []

    def set_selected_files(self, names):
        pass

    def set_temp_chat_checked(self, checked: bool):
        self.temp_chat_checked = bool(checked)

    def set_temp_chat_enabled(self, enabled: bool):
        self.temp_chat_enabled = bool(enabled)

    def refresh_message_sizes(self):
        pass

    def is_temp_chat_checked(self):
        return self.temp_chat_checked


class DummyHistoryService:
    def __init__(self):
        self.created = False

    def create_chat_session(self, *, title: str, files: list[dict]):
        self.created = True
        return "chat-1"

    def update_chat_session(self, *, chat_id: str, messages: list[dict], files: list[dict]):
        pass


class DummySettingsFlow:
    def build_ai_preferences(self) -> str:
        return "Tone: Neutral"


class DummyController:
    def __init__(self):
        self.auth_token = "token"
        self.chat_view = DummyChatView()
        self.datei_liste_view = DummyChatView()
        self.stack = type("Stack", (), {"setCurrentWidget": lambda *a, **k: None})()
        self.chat_started = False
        self.is_temp_chat = False
        self.current_chat_id = None
        self.chat_messages = []
        self.chat_file_context = []
        self.chat_file_meta = []
        self.history_service = DummyHistoryService()
        self.settings_flow = DummySettingsFlow()
        self._chat_thread = None
        self._chat_worker = None


def test_on_chat_send_starts_session(monkeypatch):
    controller = DummyController()
    controller.chat_view.chat_input = "Hello"
    flow = chat_core_flow(controller)

    captured = {}

    def fake_start_chat_worker(*, mode: str, payload: dict):
        captured["mode"] = mode
        captured["payload"] = payload

    monkeypatch.setattr(flow, "start_chat_worker", fake_start_chat_worker)

    flow.on_chat_send_clicked()

    assert controller.chat_started is True
    assert controller.current_chat_id == "chat-1"
    assert controller.chat_messages
    assert controller.chat_view.send_enabled is False
    assert captured["mode"] == "chat"


def test_on_chat_back_resets_temp_chat():
    controller = DummyController()
    controller.is_temp_chat = True
    controller.chat_started = True
    controller.chat_messages = [{"role": "user", "content": "Hi"}]
    controller.chat_file_meta = [{"id": 1}]
    flow = chat_core_flow(controller)

    flow.on_chat_back_clicked()

    assert controller.current_chat_id is None
    assert controller.chat_messages == []
    assert controller.chat_file_meta == []
    assert controller.chat_started is False
