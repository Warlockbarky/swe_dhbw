from controller.history_flow import history_flow


class DummyHistoryService:
    def __init__(self, history):
        self._history = list(history)
        self.saved = None

    def load(self):
        return list(self._history)

    def save(self, history):
        self.saved = list(history)
        self._history = list(history)

    def sort(self, history, mode):
        return list(history)

    def format_items(self, history):
        return [item.get("title", "") for item in history]


class DummyView:
    def __init__(self):
        self.errors = []
        self._selected_index = -1
        self._selected_indices = []
        self._checked_indices = []
        self.items = []

    def show_error(self, msg: str):
        self.errors.append(msg)

    def get_selected_index(self):
        return self._selected_index

    def get_selected_indices(self):
        return list(self._selected_indices)

    def get_checked_indices(self):
        return list(self._checked_indices)

    def set_items(self, items):
        self.items = list(items)

    def set_all_checked(self, checked: bool):
        pass


class DummyChatFileFlow:
    def open_history_entry(self, history, idx):
        pass


class DummyController:
    def __init__(self, history):
        self.history_service = DummyHistoryService(history)
        self.history_view = DummyView()
        self.datei_liste_view = object()
        self.chat_view = type("Chat", (), {"clear_chat": lambda *a, **k: None, "set_selected_files": lambda *a, **k: None})()
        self.chat_file_flow = DummyChatFileFlow()
        self.visible_history_entries = list(history)
        self.history_sort_mode = "Datum (neu-alt)"
        self.history_search_query = ""
        self.current_chat_id = None
        self.chat_messages = []
        self.chat_file_context = []
        self.chat_file_meta = []
        self.stack = type("Stack", (), {"setCurrentWidget": lambda *a, **k: None})()


def test_delete_requires_selection():
    controller = DummyController([{"id": "1", "title": "Chat"}])
    flow = history_flow(controller)
    flow.on_history_delete_clicked()
    assert controller.history_view.errors


def test_delete_confirmed(monkeypatch):
    controller = DummyController([
        {"id": "1", "title": "Chat"},
        {"id": "2", "title": "Other"},
    ])
    controller.history_view._selected_indices = [0]

    monkeypatch.setattr(
        "controller.history_flow.QMessageBox.question",
        lambda *a, **k: __import__("PyQt6.QtWidgets").QtWidgets.QMessageBox.StandardButton.Yes,
    )

    flow = history_flow(controller)
    flow.on_history_delete_clicked()

    assert controller.history_service.saved is not None
    assert len(controller.history_service.saved) == 1


def test_rename_empty_rejected(monkeypatch):
    controller = DummyController([{"id": "1", "title": "Chat"}])
    controller.history_view._selected_index = 0

    monkeypatch.setattr("controller.history_flow.QInputDialog.getText", lambda *a, **k: ("", True))

    flow = history_flow(controller)
    flow.on_history_rename_clicked()
    assert controller.history_view.errors


def test_rename_success(monkeypatch):
    controller = DummyController([{"id": "1", "title": "Chat"}])
    controller.history_view._selected_index = 0

    monkeypatch.setattr("controller.history_flow.QInputDialog.getText", lambda *a, **k: ("New", True))

    flow = history_flow(controller)
    flow.on_history_rename_clicked()
    assert controller.history_service.saved[0]["title"] == "New"
