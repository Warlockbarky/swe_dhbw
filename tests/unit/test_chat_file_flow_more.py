from controller.chat_file_flow import chat_file_flow


class DummyChatView:
    def __init__(self):
        self.errors = []
        self.selected = []
        self.cleared = False
        self.temp_checked = None
        self.temp_enabled = None

    def show_error(self, msg: str):
        self.errors.append(msg)

    def set_selected_files(self, names):
        self.selected = list(names)

    def clear_chat(self):
        self.cleared = True

    def clear_chat_input(self):
        pass

    def set_temp_chat_checked(self, checked: bool):
        self.temp_checked = bool(checked)

    def set_temp_chat_enabled(self, enabled: bool):
        self.temp_enabled = bool(enabled)


class DummyHistoryView:
    def __init__(self):
        self.errors = []

    def show_error(self, msg: str):
        self.errors.append(msg)


class DummyChatCoreFlow:
    def __init__(self):
        self.persisted = False
        self.rendered = False

    def persist_current_chat(self):
        self.persisted = True

    def render_chat_messages(self, messages):
        self.rendered = True


class DummyController:
    def __init__(self):
        self.api_base_url = "http://example"
        self.auth_token = "token"
        self.visible_file_records = []
        self.chat_file_context = []
        self.chat_file_meta = []
        self.chat_view = DummyChatView()
        self.history_view = DummyHistoryView()
        self.chat_core_flow = DummyChatCoreFlow()
        self.is_temp_chat = False
        self.chat_started = True
        self.current_chat_id = "chat-1"
        self.stack = type("Stack", (), {"setCurrentWidget": lambda *a, **k: None})()


def test_on_chat_select_files_requires_auth():
    controller = DummyController()
    controller.auth_token = None
    flow = chat_file_flow(controller)
    flow.on_chat_select_files_clicked()
    assert controller.chat_view.errors


def test_set_chat_files_empty_persists():
    controller = DummyController()
    flow = chat_file_flow(controller)
    flow.set_chat_files([])
    assert controller.chat_file_context == []
    assert controller.chat_core_flow.persisted is True


def test_open_history_entry_success(monkeypatch):
    controller = DummyController()
    flow = chat_file_flow(controller)

    history = [
        {"id": "1", "messages": [{"role": "user", "content": "Hi"}], "files": [{"id": 1, "name": "doc.txt"}]}
    ]

    monkeypatch.setattr(
        flow,
        "load_chat_file_contexts",
        lambda records: [{"id": 1, "name": "doc.txt", "content": "text"}],
    )

    flow.open_history_entry(history, 0)
    assert controller.chat_messages == [{"role": "user", "content": "Hi"}]
    assert controller.chat_view.selected == ["doc.txt"]


def test_open_history_entry_failure(monkeypatch):
    controller = DummyController()
    flow = chat_file_flow(controller)

    history = [
        {"id": "1", "messages": [], "files": [{"id": 1, "name": "doc.txt"}]}
    ]

    def raise_error(*args, **kwargs):
        raise RuntimeError("bad")

    monkeypatch.setattr(flow, "load_chat_file_contexts", raise_error)

    flow.open_history_entry(history, 0)
    assert controller.chat_view.selected == []
    assert controller.history_view.errors
