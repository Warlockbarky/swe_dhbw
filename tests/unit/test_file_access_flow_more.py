from controller.file_access_flow import file_access_flow


class DummySettings:
    def __init__(self):
        self.store = {"files/default_dir": ""}

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


class DummyView:
    def __init__(self):
        self.errors = []
        self._selected_index = 0

    def show_error(self, msg: str):
        self.errors.append(msg)

    def get_selected_index(self):
        return self._selected_index

    def prompt_save_path(self, suggested_name: str, default_dir: str = ""):
        return ""


class DummyStack:
    def __init__(self):
        self.current = None

    def setCurrentWidget(self, widget):
        self.current = widget


class DummyController:
    def __init__(self):
        self.api_base_url = "http://example"
        self.auth_token = None
        self.settings = DummySettings()
        self.datei_liste_view = DummyView()
        self.login_view = object()
        self.stack = DummyStack()
        self.visible_file_records = []


def test_on_download_requires_auth():
    controller = DummyController()
    flow = file_access_flow(controller)
    flow.on_download_clicked()
    assert controller.datei_liste_view.errors
