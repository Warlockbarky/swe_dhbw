from controller.file_access_flow import file_access_flow


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
        self._selected_index = 0

    def show_error(self, msg: str):
        self.errors.append(msg)

    def get_selected_index(self):
        return self._selected_index


class DummyStack:
    def __init__(self):
        self.current = None

    def setCurrentWidget(self, widget):
        self.current = widget


class Controller:
    pass


def test_end_to_end_download(qtbot, fake_backend, tmp_path, monkeypatch):
    view = DummyView()

    controller = Controller()
    controller.api_base_url = fake_backend.base_url
    controller.auth_token = "token"
    controller.settings = DummySettings()
    controller.datei_liste_view = view
    controller.login_view = object()
    controller.stack = DummyStack()
    controller.visible_file_records = [{"id": 1, "name": "report.pdf"}]

    monkeypatch.setattr(
        "controller.file_access_flow.resolve_download_dir",
        lambda settings, view: tmp_path,
    )

    flow = file_access_flow(controller)
    local = flow.ensure_local_file(controller.visible_file_records[0])

    assert local is not None
    assert local.exists()
    assert local.read_bytes() == b"PDF-DATA"
