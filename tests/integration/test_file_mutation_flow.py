from pathlib import Path

from controller.file_mutation_flow import file_mutation_flow


class FakeDateiManager:
    def __init__(self, target: Path):
        self.target = target

    def setze_und_pruefe_pfad(self, _):
        class Result:
            ok = True
            fehlertyp = None
            msg = ""

        return Result()

    def get_zielpfad(self):
        return self.target


class FakeView:
    def __init__(self):
        self.errors = []

    def show_error(self, msg: str):
        self.errors.append(msg)


class FakeStack:
    def __init__(self):
        self.current = None

    def setCurrentWidget(self, widget):
        self.current = widget


class FakeController:
    def __init__(self, target: Path):
        self.settings = object()
        self.datei_liste_view = FakeView()
        self.login_view = object()
        self.stack = FakeStack()
        self.auth_token = "token"
        self.api_base_url = "http://example"
        self.file_records = []
        self.datei_manager = FakeDateiManager(target)


class FakeResponse:
    def __init__(self, status_code=200, content=b"data"):
        self.status_code = status_code
        self._content = content

    def iter_content(self, chunk_size=8192):
        yield self._content


def test_sync_files_to_folder_writes_files(monkeypatch, tmp_path):
    controller = FakeController(tmp_path)
    controller.file_records = [{"id": 1, "name": "note.txt"}]
    flow = file_mutation_flow(controller)

    monkeypatch.setattr(
        "controller.file_mutation_flow.resolve_download_dir",
        lambda settings, view: tmp_path,
    )
    monkeypatch.setattr(
        "controller.file_mutation_flow.requests.get",
        lambda *args, **kwargs: FakeResponse(200, b"hello"),
    )

    flow.sync_files_to_folder()
    assert (tmp_path / "note.txt").read_bytes() == b"hello"


def test_sync_files_to_folder_handles_unauthorized(monkeypatch, tmp_path):
    controller = FakeController(tmp_path)
    controller.file_records = [{"id": 1, "name": "note.txt"}]
    flow = file_mutation_flow(controller)

    monkeypatch.setattr(
        "controller.file_mutation_flow.resolve_download_dir",
        lambda settings, view: tmp_path,
    )
    monkeypatch.setattr(
        "controller.file_mutation_flow.requests.get",
        lambda *args, **kwargs: FakeResponse(401, b""),
    )

    flow.sync_files_to_folder()
    assert controller.datei_liste_view.errors
    assert controller.stack.current == controller.login_view
