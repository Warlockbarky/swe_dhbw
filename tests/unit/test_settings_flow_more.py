from controller.settings_flow import settings_flow


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


class DummyView:
    def __init__(self):
        self.applied = []

    def apply_theme(self, theme: str, palette: str):
        self.applied.append((theme, palette))


class DummyUserSettingsStore:
    def __init__(self, exists=False, data=None):
        self._exists = exists
        self._data = data or {}
        self.saved = None

    def exists(self, username: str) -> bool:
        return self._exists

    def load(self, username: str) -> dict:
        return dict(self._data)

    def save(self, username: str, values: dict):
        self.saved = dict(values)


class DummyController:
    def __init__(self, user_store):
        self.settings = DummySettings()
        self.start_view = DummyView()
        self.login_view = DummyView()
        self.pfad_view = DummyView()
        self.datei_liste_view = DummyView()
        self.chat_view = DummyView()
        self.history_view = DummyView()
        self.user_settings_store = user_store
        self.current_username = "user"


def test_handle_first_login_settings_existing_user():
    user_store = DummyUserSettingsStore(exists=True, data={"theme": "Dark", "palette": "Blue"})
    controller = DummyController(user_store)
    flow = settings_flow(controller)

    flow.handle_first_login_settings()

    assert controller.settings.value("ui/theme") == "Dark"
    assert controller.settings.value("ui/palette") == "Blue"


def test_show_first_time_settings_dialog_accept(monkeypatch):
    user_store = DummyUserSettingsStore(exists=False)
    controller = DummyController(user_store)
    flow = settings_flow(controller)

    class DummyDialog:
        class DialogCode:
            Accepted = 1

        def __init__(self, parent=None):
            self.values = {}

        def set_values(self, values: dict):
            self.values = values

        def exec(self):
            return self.DialogCode.Accepted

        def get_values(self):
            return {"theme": "Dark", "palette": "Blue"}

    monkeypatch.setattr("controller.settings_flow.settings_dialog", DummyDialog)

    flow.show_first_time_settings_dialog()

    assert user_store.saved["theme"] == "Dark"
    assert controller.settings.value("ui/theme") == "Dark"


def test_show_first_time_settings_dialog_cancel(monkeypatch):
    user_store = DummyUserSettingsStore(exists=False)
    controller = DummyController(user_store)
    flow = settings_flow(controller)

    class DummyDialog:
        class DialogCode:
            Accepted = 1

        def __init__(self, parent=None):
            self.values = {}

        def set_values(self, values: dict):
            self.values = values

        def exec(self):
            return 0

        def get_values(self):
            return {"theme": "Dark"}

    monkeypatch.setattr("controller.settings_flow.settings_dialog", DummyDialog)

    flow.show_first_time_settings_dialog()

    assert controller.settings.value("ui/theme") == "Light"
