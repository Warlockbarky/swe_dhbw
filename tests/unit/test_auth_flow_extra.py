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

    def show_error(self, msg: str):
        self.errors.append(msg)


class DummyStack:
    def __init__(self):
        self.current = None

    def setCurrentWidget(self, widget):
        self.current = widget


class DummyStartView:
    def __init__(self):
        self.loading_called = False
        self.greeting = None

    def start_loading(self):
        self.loading_called = True

    def show_greeting(self, username):
        self.greeting = username


class DummyController:
    def __init__(self):
        self.settings = DummySettings()
        self.login_view = DummyLoginView()
        self.stack = DummyStack()
        self.start_view = DummyStartView()


def test_load_saved_credentials_sets_fields():
    controller = DummyController()
    controller.settings.setValue("auth/remember", True)
    controller.settings.setValue("auth/username", "user")
    controller.settings.setValue("auth/password", "pass")

    flow = auth_flow(controller)
    flow.load_saved_credentials()

    assert controller.login_view.get_username() == "user"
    assert controller.login_view.get_password() == "pass"
    assert controller.login_view.get_remember_checked() is True


def test_maybe_auto_login_calls(monkeypatch):
    controller = DummyController()
    controller.settings.setValue("auth/remember", True)
    controller.login_view.set_username("user")
    controller.login_view.set_password("pass")

    called = {"count": 0}

    def fake_single_shot(ms, func):
        called["count"] += 1
        func()

    monkeypatch.setattr("controller.auth_flow.QTimer.singleShot", fake_single_shot)

    flow = auth_flow(controller)
    flow.on_login_clicked = lambda: called.__setitem__("login", True)
    flow.maybe_auto_login()

    assert called.get("login") is True


def test_start_splash_shows_greeting(monkeypatch):
    controller = DummyController()
    controller.settings.setValue("auth/remember", False)

    def fake_single_shot(ms, func):
        func()

    monkeypatch.setattr("controller.auth_flow.QTimer.singleShot", fake_single_shot)

    flow = auth_flow(controller)
    flow.start_splash()

    assert controller.start_view.loading_called is True
    assert controller.start_view.greeting is None
    assert controller.stack.current == controller.login_view


def test_register_requires_credentials():
    controller = DummyController()
    flow = auth_flow(controller)
    flow.on_register_clicked()
    assert controller.login_view.errors
