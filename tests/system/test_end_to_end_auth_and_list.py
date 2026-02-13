from controller.auth_flow import auth_flow
from controller.file_list_flow import file_list_flow
from view.datei_liste_view import datei_liste_view
from view.login_view import login_view


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


class DummyChatView:
    def clear_chat(self):
        pass

    def clear_chat_input(self):
        pass

    def set_selected_files(self, names):
        pass


class FakeSettingsFlow:
    def handle_first_login_settings(self):
        pass


class FakeFileMutationFlow:
    def sync_files_to_folder(self):
        pass


class Controller:
    pass


def test_end_to_end_login_and_list(qtbot, fake_backend):
    login = login_view()
    datei_view = datei_liste_view()
    qtbot.addWidget(login)
    qtbot.addWidget(datei_view)

    errors = []
    login.show_error = lambda msg: errors.append(msg)
    datei_view.show_error = lambda msg: errors.append(msg)

    login.set_username("user")
    login.set_password("pass")

    controller = Controller()
    controller.api_base_url = fake_backend.base_url
    controller.auth_token = None
    controller.current_username = None
    controller.settings = DummySettings()
    controller.settings_flow = FakeSettingsFlow()
    controller.file_records = []
    controller.visible_file_records = []
    controller.file_sort_mode = "Name (A-Z)"
    controller.file_search_query = ""
    controller.chat_messages = []
    controller.current_chat_id = None
    controller.chat_file_context = []
    controller.chat_file_meta = []
    controller.login_view = login
    controller.datei_liste_view = datei_view
    controller.chat_view = DummyChatView()
    controller.stack = DummyStack()
    controller.file_mutation_flow = FakeFileMutationFlow()

    controller.file_list_flow = file_list_flow(controller)
    flow = auth_flow(controller)

    flow.on_login_clicked()

    assert controller.auth_token == "token"
    assert controller.datei_liste_view.list_widget.count() == 2
    assert controller.stack.current == controller.datei_liste_view
    assert not errors
