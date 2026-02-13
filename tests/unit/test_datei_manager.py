from dataclasses import dataclass
from pathlib import Path

from controller.datei_manager import datei_manager


@dataclass(frozen=True)
class ValidatorResult:
    ok: bool
    fehlertyp: object | None = None
    msg: str = ""


class StubValidator:
    def __init__(self, ok=True):
        self.ok = ok

    def pruefe_pfad(self, p: Path):
        return self.ok, None, ""

    def pruefe_schreibrechte(self, p: Path):
        return self.ok, None, ""

    def pruefe_speicherplatz(self, p: Path):
        return self.ok, None, ""


def test_setze_und_pruefe_pfad_sets_target(tmp_path):
    validator = StubValidator(ok=True)
    manager = datei_manager(validator)
    res = manager.setze_und_pruefe_pfad(str(tmp_path))
    assert res.ok is True
    assert res.pfad == tmp_path.resolve()
    assert manager.get_zielpfad() == tmp_path.resolve()


def test_get_zielpfad_requires_set():
    manager = datei_manager(StubValidator())
    try:
        manager.get_zielpfad()
        assert False, "Expected RuntimeError"
    except RuntimeError:
        assert True


def test_speichere_datei_writes_bytes(tmp_path):
    validator = StubValidator(ok=True)
    manager = datei_manager(validator)
    manager.setze_und_pruefe_pfad(str(tmp_path))
    target = manager.speichere_datei("nested/file.txt", b"data")
    assert target.exists()
    assert target.read_bytes() == b"data"
