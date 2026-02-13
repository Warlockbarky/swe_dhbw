from pathlib import Path

from controller.file_path_service import resolve_download_dir


class FakeSettings:
    def __init__(self, configured: str):
        self.configured = configured

    def value(self, key, default=None, type=str):
        if key == "files/default_dir":
            return self.configured
        return default


class FakeView:
    def __init__(self):
        self.errors = []

    def show_error(self, msg: str):
        self.errors.append(msg)


def test_resolve_download_dir_prefers_configured(tmp_path):
    configured = tmp_path / "downloads"
    configured.mkdir()
    settings = FakeSettings(str(configured))
    view = FakeView()
    result = resolve_download_dir(settings, view)
    assert result == configured.resolve()
    assert view.errors == []


def test_resolve_download_dir_falls_back_to_home(monkeypatch, tmp_path):
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    settings = FakeSettings("")
    view = FakeView()
    result = resolve_download_dir(settings, view)
    assert result == downloads.resolve()


def test_resolve_download_dir_returns_none_and_errors(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    settings = FakeSettings("/missing")
    view = FakeView()
    result = resolve_download_dir(settings, view)
    assert result is None
    assert view.errors
