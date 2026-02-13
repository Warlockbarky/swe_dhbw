import json
from pathlib import Path

from PyQt6.QtCore import QStandardPaths

from controller.user_settings_store import user_settings_store


def test_settings_store_sanitizes_username(monkeypatch, tmp_path):
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        lambda _: str(tmp_path),
    )
    store = user_settings_store("app")
    path = store._get_settings_path("user:name")
    assert path.name == "user_name_settings.json"


def test_settings_store_save_and_load(monkeypatch, tmp_path):
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        lambda _: str(tmp_path),
    )
    store = user_settings_store("app")
    store.save("user1", {"theme": "Light"})
    loaded = store.load("user1")
    assert loaded == {"theme": "Light"}


def test_settings_store_exists(monkeypatch, tmp_path):
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        lambda _: str(tmp_path),
    )
    store = user_settings_store("app")
    assert store.exists("user1") is False
    store.save("user1", {"k": 1})
    assert store.exists("user1") is True


def test_settings_store_load_returns_empty_on_corruption(monkeypatch, tmp_path):
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        lambda _: str(tmp_path),
    )
    store = user_settings_store("app")
    path = store._get_settings_path("user1")
    path.write_text("{bad}", encoding="utf-8")
    assert store.load("user1") == {}


def test_settings_store_save_ignores_empty_username(monkeypatch, tmp_path):
    monkeypatch.setattr(
        QStandardPaths,
        "writableLocation",
        lambda _: str(tmp_path),
    )
    store = user_settings_store("app")
    store.save("", {"theme": "Light"})
    assert list(Path(tmp_path).glob("*_settings.json")) == []
