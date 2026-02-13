from controller.file_mutation_flow import file_mutation_flow


class DummySettings:
    def __init__(self):
        self.store = {"files/default_dir": ""}

    def value(self, key, default=None, type=str):
        if key not in self.store:
            return default
        value = self.store[key]
        if type is None:
            return value
        try:
            return type(value)
        except Exception:
            return value


class DummyView:
    def __init__(self):
        self.errors = []
        self._selected_indices = []
        self._checked_indices = []

    def show_error(self, msg: str):
        self.errors.append(msg)

    def get_selected_indices(self):
        return list(self._selected_indices)

    def get_checked_indices(self):
        return list(self._checked_indices)


class DummyStack:
    def __init__(self):
        self.current = None

    def setCurrentWidget(self, widget):
        self.current = widget


class DummyFileListFlow:
    def __init__(self):
        self.called = False

    def load_files_and_show(self):
        self.called = True


class DummyController:
    def __init__(self):
        self.settings = DummySettings()
        self.datei_liste_view = DummyView()
        self.login_view = object()
        self.stack = DummyStack()
        self.auth_token = "token"
        self.api_base_url = "http://example"
        self.file_list_flow = DummyFileListFlow()
        self.visible_file_records = []


class FakeResponse:
    def __init__(self, status_code=204):
        self.status_code = status_code


def test_delete_unauthorized(monkeypatch):
    controller = DummyController()
    controller.visible_file_records = [{"id": 1, "name": "doc"}]
    controller.datei_liste_view._selected_indices = [0]

    monkeypatch.setattr(
        "controller.file_mutation_flow.QMessageBox.question",
        lambda *a, **k: __import__("PyQt6.QtWidgets").QtWidgets.QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(
        "controller.file_mutation_flow.requests.delete",
        lambda *a, **k: FakeResponse(401),
    )

    flow = file_mutation_flow(controller)
    flow.on_delete_clicked()

    assert controller.stack.current == controller.login_view


def test_delete_success(monkeypatch):
    controller = DummyController()
    controller.visible_file_records = [{"id": 1, "name": "doc"}]
    controller.datei_liste_view._selected_indices = [0]

    monkeypatch.setattr(
        "controller.file_mutation_flow.QMessageBox.question",
        lambda *a, **k: __import__("PyQt6.QtWidgets").QtWidgets.QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(
        "controller.file_mutation_flow.requests.delete",
        lambda *a, **k: FakeResponse(204),
    )

    flow = file_mutation_flow(controller)
    flow.on_delete_clicked()

    assert controller.file_list_flow.called is True
