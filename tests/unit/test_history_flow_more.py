from controller.history_flow import history_flow


class DummyHistoryService:
    def __init__(self, history):
        self._history = list(history)

    def load(self):
        return list(self._history)

    def save(self, history):
        self._history = list(history)

    def sort(self, history, mode):
        return list(history)

    def format_items(self, history):
        return [item.get("title", "") for item in history]


class DummyView:
    def __init__(self):
        self.errors = []
        self._selected_index = -1
        self.items = []

    def show_error(self, msg: str):
        self.errors.append(msg)

    def get_selected_index(self):
        return self._selected_index

    def set_items(self, items):
        self.items = list(items)


class DummyChatFileFlow:
    def __init__(self):
        self.opened = False

    def open_history_entry(self, history, idx):
        self.opened = True


class DummyController:
    def __init__(self, history):
        self.history_service = DummyHistoryService(history)
        self.history_view = DummyView()
        self.visible_history_entries = list(history)
        self.history_sort_mode = "Datum (neu-alt)"
        self.history_search_query = ""
        self.chat_file_flow = DummyChatFileFlow()
        self.stack = type("Stack", (), {"setCurrentWidget": lambda *a, **k: None})()


def test_on_history_clicked_sets_items():
    controller = DummyController([{"id": "1", "title": "Chat"}])
    flow = history_flow(controller)
    flow.on_history_clicked()
    assert controller.history_view.items == ["Chat"]


def test_on_history_open_clicked_valid():
    controller = DummyController([{"id": "1", "title": "Chat"}])
    controller.history_view._selected_index = 0
    flow = history_flow(controller)
    flow.on_history_open_clicked()
    assert controller.chat_file_flow.opened is True
