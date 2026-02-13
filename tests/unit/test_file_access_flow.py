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

    def show_error(self, msg: str):
        self.errors.append(msg)

    def get_selected_index(self):
        return self._selected_index


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
        self.headers = {"Content-Type": "application/octet-stream"}

    def iter_content(self, chunk_size=8192):
        yield self.content


def test_get_local_file_info(tmp_path, monkeypatch):
    controller = DummyController()
    flow = file_access_flow(controller)

    monkeypatch.setattr(
        "controller.file_access_flow.resolve_download_dir",
        lambda settings, view: tmp_path,
    )

    target = tmp_path / "report.pdf"
    target.write_bytes(b"data")

    info = flow.get_local_file_info({"id": 1, "name": "report.pdf"})
    assert info["size"]
    assert info["created"]


def test_ensure_local_file_uses_cache(tmp_path, monkeypatch):
    controller = DummyController()
    flow = file_access_flow(controller)

    monkeypatch.setattr(
        "controller.file_access_flow.resolve_download_dir",
        lambda settings, view: tmp_path,
    )

    cached = tmp_path / "report.pdf"
    cached.write_bytes(b"data")

    def fail_request(*args, **kwargs):
        raise AssertionError("should not download")

    monkeypatch.setattr("controller.file_access_flow.requests.get", fail_request)

    local = flow.ensure_local_file({"id": 1, "name": "report.pdf"})
    assert local == cached


def test_ensure_local_file_unauthorized(tmp_path, monkeypatch):
    controller = DummyController()
    flow = file_access_flow(controller)

    monkeypatch.setattr(
        "controller.file_access_flow.resolve_download_dir",
        lambda settings, view: tmp_path,
    )
    monkeypatch.setattr(
        "controller.file_access_flow.requests.get",
        lambda *a, **k: FakeResponse(401),
    )

    local = flow.ensure_local_file({"id": 1, "name": "report.pdf"})
    assert local is None
    assert controller.stack.current == controller.login_view


def test_ensure_local_file_download_success(tmp_path, monkeypatch):
    controller = DummyController()
    flow = file_access_flow(controller)

    monkeypatch.setattr(
        "controller.file_access_flow.resolve_download_dir",
        lambda settings, view: tmp_path,
    )
    monkeypatch.setattr(
        "controller.file_access_flow.requests.get",
        lambda *a, **k: FakeResponse(200, b"payload"),
    )

    local = flow.ensure_local_file({"id": 1, "name": "report.pdf"})
    assert local is not None
    assert local.read_bytes() == b"payload"
