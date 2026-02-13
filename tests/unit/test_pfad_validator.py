import os
from pathlib import Path

from model import pfad_validator as pfad_validator_module
from model import fehlertyp


def test_pruefe_pfad_success(tmp_path):
    validator = pfad_validator_module.pfad_validator()
    ok, ft, msg = validator.pruefe_pfad(tmp_path)
    assert ok is True
    assert ft is None
    assert msg == ""


def test_pruefe_pfad_failure(tmp_path):
    validator = pfad_validator_module.pfad_validator()
    missing = tmp_path / "missing"
    ok, ft, msg = validator.pruefe_pfad(missing)
    assert ok is False
    assert ft is fehlertyp.pfad_fehler
    assert "Pfad existiert nicht" in msg


def test_pruefe_schreibrechte_failure(monkeypatch, tmp_path):
    validator = pfad_validator_module.pfad_validator()

    def raise_perm(*args, **kwargs):
        raise PermissionError("no")

    monkeypatch.setattr(Path, "touch", raise_perm)
    ok, ft, msg = validator.pruefe_schreibrechte(tmp_path)
    assert ok is False
    assert ft is fehlertyp.schreibrechte_fehler
    assert "Keine Schreibrechte" in msg


def test_pruefe_speicherplatz_minimum(monkeypatch, tmp_path):
    validator = pfad_validator_module.pfad_validator()

    class FakeStat:
        f_bavail = 1
        f_frsize = 1

    monkeypatch.setattr(os, "statvfs", lambda _: FakeStat())
    ok, ft, msg = validator.pruefe_speicherplatz(tmp_path, min_bytes=100)
    assert ok is False
    assert ft is fehlertyp.speicherplatz_fehler
    assert "Zu wenig" in msg


def test_pruefe_speicherplatz_success(monkeypatch, tmp_path):
    validator = pfad_validator_module.pfad_validator()

    class FakeStat:
        f_bavail = 200
        f_frsize = 2

    monkeypatch.setattr(os, "statvfs", lambda _: FakeStat())
    ok, ft, msg = validator.pruefe_speicherplatz(tmp_path, min_bytes=100)
    assert ok is True
    assert ft is None
    assert msg == ""
