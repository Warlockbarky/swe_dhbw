import types

import requests

from controller.auth_flow import auth_flow


class DummySettings:
    def __init__(self):
        self.store = {}

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

    def setValue(self, key, value):
        self.store[key] = value

    def remove(self, key):
        keys = [k for k in self.store if k == key or k.startswith(f"{key}/")]
        for k in keys:
            self.store.pop(k, None)


class DummyStack:
    def __init__(self):
        self.current = None

    def setCurrentWidget(self, widget):
        self.current = widget


class DummyLoginView:
    def __init__(self):
        self._username = ""
        self._password = ""
        self._remember = False
        self.errors = []

    def get_username(self):
        return self._username

    def get_password(self):
        return self._password

    def set_username(self, value: str):
        self._username = value

    def set_password(self, value: str):
        self._password = value

    def get_remember_checked(self) -> bool:
        return self._remember

    def set_remember_checked(self, checked: bool):
        self._remember = bool(checked)

    def show_error(self, message: str):
        self.errors.append(message)


class DummyFileListFlow:
    def __init__(self):
        self.called = False

    def load_files_and_show(self):
        self.called = True


class DummySettingsFlow:
    def __init__(self):
        self.called = False

    def handle_first_login_settings(self):
        self.called = True


class DummyController:
    def __init__(self):
        self.api_base_url = "http://example"
        self.auth_token = None
        self.current_username = None
        self.settings = DummySettings()
        self.login_view = DummyLoginView()
        self.datei_liste_view = type(
            "ListView", (), {"set_items": lambda *a, **k: None}
        )()
        self.stack = DummyStack()
        self.file_list_flow = DummyFileListFlow()
        self.settings_flow = DummySettingsFlow()


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {"access_token": "token"}

    def json(self):
        return self._payload


def test_login_requires_credentials():
    controller = DummyController()
    flow = auth_flow(controller)
    flow.on_login_clicked()
    assert controller.login_view.errors


def test_login_success_sets_token(monkeypatch):
    controller = DummyController()
    controller.login_view.set_username("user")
    controller.login_view.set_password("pass")
    controller.login_view.set_remember_checked(True)

    def fake_post(*args, **kwargs):
        return FakeResponse(200, {"access_token": "token"})

    monkeypatch.setattr("controller.auth_flow.requests.post", fake_post)
    flow = auth_flow(controller)
    flow.on_login_clicked()

    assert controller.auth_token == "token"
    assert controller.current_username == "user"
    assert controller.file_list_flow.called is True
    assert controller.settings_flow.called is True
    assert controller.settings.value("auth/username") == "user"


def test_login_invalid_credentials(monkeypatch):
    controller = DummyController()
    controller.login_view.set_username("user")
    controller.login_view.set_password("bad")

    monkeypatch.setattr("controller.auth_flow.requests.post", lambda *a, **k: FakeResponse(401))
    flow = auth_flow(controller)
    flow.on_login_clicked()
    assert any("Login fehlgeschlagen" in msg for msg in controller.login_view.errors)


def test_register_success(monkeypatch):
    controller = DummyController()
    controller.login_view.set_username("user")
    controller.login_view.set_password("pass")

    monkeypatch.setattr("controller.auth_flow.requests.post", lambda *a, **k: FakeResponse(201))
    messages = []
    monkeypatch.setattr("controller.auth_flow.QMessageBox.information", lambda *a, **k: messages.append("ok"))

    flow = auth_flow(controller)
    flow.on_register_clicked()
    assert messages == ["ok"]


def test_register_existing_user(monkeypatch):
    controller = DummyController()
    controller.login_view.set_username("existing")
    controller.login_view.set_password("pass")

    monkeypatch.setattr("controller.auth_flow.requests.post", lambda *a, **k: FakeResponse(400))
    flow = auth_flow(controller)
    flow.on_register_clicked()
    assert controller.login_view.errors


def test_logout_clears_state():
    controller = DummyController()
    controller.auth_token = "token"
    controller.current_username = "user"
    controller.settings.setValue("auth/remember", True)
    controller.settings.setValue("auth/username", "user")
    controller.login_view.set_username("user")
    controller.login_view.set_password("pass")
    controller.login_view.set_remember_checked(True)

    flow = auth_flow(controller)
    flow.on_logout_clicked()
    assert controller.auth_token is None
    assert controller.current_username is None
    assert controller.login_view.get_username() == ""
    assert controller.login_view.get_password() == ""
    assert controller.login_view.get_remember_checked() is False
