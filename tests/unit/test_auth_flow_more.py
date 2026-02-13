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


class DummyController:
    def __init__(self):
        self.settings = DummySettings()
        self.login_view = DummyLoginView()


def test_save_credentials_remember_true():
    controller = DummyController()
    controller.login_view.set_remember_checked(True)
    flow = auth_flow(controller)
    flow.save_credentials("user", "pass")
    assert controller.settings.value("auth/remember", type=bool) is True
    assert controller.settings.value("auth/username") == "user"


def test_save_credentials_remember_false():
    controller = DummyController()
    controller.login_view.set_remember_checked(False)
    controller.settings.setValue("auth/remember", True)
    flow = auth_flow(controller)
    flow.save_credentials("user", "pass")
    assert controller.settings.value("auth/remember", False) is False
