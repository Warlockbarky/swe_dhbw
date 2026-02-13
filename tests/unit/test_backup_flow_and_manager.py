from pathlib import Path

from controller.backup_flow import backup_flow
from controller.backup_manager import backup_manager


class DummyDateiManager:
    def __init__(self, target: Path | None):
        self.target = target

    def get_zielpfad(self):
        if self.target is None:
            raise RuntimeError("missing")
        return self.target

    def speichere_datei(self, rel_name: str, data: bytes) -> Path:
        path = self.target / rel_name
        path.write_bytes(data)
        return path


class DummyPfadView:
    def __init__(self, path_value: str = ""):
        self.path_value = path_value
        self.errors = []

    def get_path(self):
        return self.path_value

    def show_error(self, msg: str):
        self.errors.append(msg)


class DummyController:
    def __init__(self, path_value: str, result_ok: bool):
        self.pfad_view = DummyPfadView(path_value)
        self.datei_manager = type("DM", (), {"setze_und_pruefe_pfad": lambda *a, **k: type("R", (), {"ok": result_ok, "fehlertyp": "err", "msg": "bad"})()})()
        self.backup_manager = type("BM", (), {"starte_backup": lambda *a, **k: None})()


def test_backup_manager_no_path():
    manager = backup_manager(DummyDateiManager(None))
    result = manager.starte_backup()
    assert result.ok is False


def test_backup_manager_success(tmp_path):
    manager = backup_manager(DummyDateiManager(tmp_path))
    result = manager.starte_backup()
    assert result.ok is True
    assert result.ziel_datei is not None
    assert result.ziel_datei.exists()


def test_backup_flow_shows_error():
    controller = DummyController("/tmp", result_ok=False)
    flow = backup_flow(controller)
    flow.on_pfad_ok()
    assert controller.pfad_view.errors
