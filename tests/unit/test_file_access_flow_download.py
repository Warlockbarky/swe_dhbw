from pathlib import Path

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
        self.save_path = ""

    def show_error(self, msg: str):
        self.errors.append(msg)

    def get_selected_index(self):
        return self._selected_index

    def prompt_save_path(self, suggested_name: str, default_dir: str = ""):
        return self.save_path


class DummyStack:
    def __init__(self):
        self.current = None

    def setCurrentWidget(self, widget):
        self.current = widget


class DummyController:
    def __init__(self):
        self.api_base_url = "http://example"
        self.auth_token = "token"
        self.settings = DummySettings()
        self.datei_liste_view = DummyView()
        self.login_view = object()
        self.stack = DummyStack()
        self.visible_file_records = []


class FakeResponse:
    def __init__(self, status_code=200, content=b"data"):
        self.status_code = status_code
        self.content = content

    def iter_content(self, chunk_size=8192):
        yield self.content


def test_on_download_missing_auth():
    controller = DummyController()
    controller.auth_token = None
    flow = file_access_flow(controller)
    flow.on_download_clicked()
    assert controller.datei_liste_view.errors


def test_on_download_invalid_selection():
    controller = DummyController()
    controller.visible_file_records = []
    flow = file_access_flow(controller)
    flow.on_download_clicked()
    assert controller.datei_liste_view.errors


def test_on_download_missing_file_id():
    controller = DummyController()
    controller.visible_file_records = [{"name": "doc"}]
    flow = file_access_flow(controller)
    flow.on_download_clicked()
    assert controller.datei_liste_view.errors


def test_on_download_cancelled():
    controller = DummyController()
    controller.visible_file_records = [{"id": 1, "name": "doc"}]
    controller.datei_liste_view.save_path = ""
    flow = file_access_flow(controller)
    flow.on_download_clicked()
    assert controller.datei_liste_view.errors == []


def test_on_download_success(monkeypatch, tmp_path):
    controller = DummyController()
    controller.visible_file_records = [{"id": 1, "name": "doc.txt"}]
    controller.datei_liste_view.save_path = str(tmp_path / "doc.txt")

    monkeypatch.setattr(
        "controller.file_access_flow.requests.get",
        lambda *a, **k: FakeResponse(200, b"payload"),
    )

    flow = file_access_flow(controller)
    flow.on_download_clicked()

    assert Path(controller.datei_liste_view.save_path).read_bytes() == b"payload"


def test_on_download_unauthorized(monkeypatch, tmp_path):
    controller = DummyController()
    controller.visible_file_records = [{"id": 1, "name": "doc.txt"}]
    controller.datei_liste_view.save_path = str(tmp_path / "doc.txt")

    monkeypatch.setattr(
        "controller.file_access_flow.requests.get",
        lambda *a, **k: FakeResponse(401, b""),
    )

    flow = file_access_flow(controller)
    flow.on_download_clicked()

    assert controller.stack.current == controller.login_view
    assert controller.datei_liste_view.errors
