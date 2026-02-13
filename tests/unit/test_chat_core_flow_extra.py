from controller.chat_core_flow import chat_core_flow


class DummyChatView:
    def __init__(self):
        self.cleared = False
        self.chat_input_cleared = False
        self.selected = []
        self.send_enabled = None
        self.temp_checked = None
        self.temp_enabled = None

    def clear_chat(self):
        self.cleared = True

    def clear_chat_input(self):
        self.chat_input_cleared = True

    def set_selected_files(self, names):
        self.selected = list(names)

    def set_send_enabled(self, enabled: bool):
        self.send_enabled = enabled

    def set_temp_chat_checked(self, checked: bool):
        self.temp_checked = checked

    def set_temp_chat_enabled(self, enabled: bool):
        self.temp_enabled = enabled

    def stop_loading_and_stream(self, text: str):
        pass


class DummyHistoryService:
    def __init__(self):
        self.updated = False

    def update_chat_session(self, *, chat_id: str, messages: list[dict], files: list[dict]):
        self.updated = True


class DummySettingsFlow:
    def build_ai_preferences(self) -> str:
        return "Tone: Neutral"


class DummyController:
    def __init__(self):
        self.auth_token = "token"
        self.chat_view = DummyChatView()
        self.datei_liste_view = object()
        self.stack = type("Stack", (), {"setCurrentWidget": lambda *a, **k: None})()
        self.is_temp_chat = False
        self.chat_started = False
        self.current_chat_id = None
        self.chat_messages = []
        self.chat_file_context = []
        self.chat_file_meta = []
        self.history_service = DummyHistoryService()
        self.settings_flow = DummySettingsFlow()


def test_on_ai_summary_clicked_resets_state():
    controller = DummyController()
    controller.chat_started = True
    controller.is_temp_chat = True
    controller.chat_messages = [{"role": "user"}]
    controller.chat_file_context = [{"id": 1}]
    controller.chat_file_meta = [{"id": 1}]

    flow = chat_core_flow(controller)
    flow.on_ai_summary_clicked()

    assert controller.chat_messages == [{"role": "user"}]
    assert controller.chat_file_context == []
    assert controller.chat_file_meta == []
    assert controller.chat_view.send_enabled is True


def test_on_chat_worker_finished_persists(monkeypatch):
    controller = DummyController()
    controller.chat_started = True
    controller.current_chat_id = "chat-1"

    flow = chat_core_flow(controller)

    called = {"persist": False}

    def fake_persist():
        called["persist"] = True

    monkeypatch.setattr(flow, "persist_current_chat", fake_persist)

    flow.on_chat_worker_finished({"assistant": "Hi"})

    assert controller.chat_messages[-1]["role"] == "assistant"
    assert called["persist"] is True
