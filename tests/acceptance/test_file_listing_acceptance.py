from controller.file_list_flow import file_list_flow


class FakeView:
    def __init__(self):
        self.errors = []
        self.items = []

    def show_error(self, msg: str):
        self.errors.append(msg)

    def set_items(self, items):
        self.items = list(items)

    def clear_chat(self):
        pass

    def clear_chat_input(self):
        pass

    def set_selected_files(self, names):
        pass


class FakeStack:
    def __init__(self):
        self.current = None

    def setCurrentWidget(self, widget):
        self.current = widget


class FakeFileMutationFlow:
    def __init__(self):
        self.called = False

    def sync_files_to_folder(self):
        self.called = True


class FakeController:
    def __init__(self):
        self.auth_token = "token"
        self.api_base_url = "http://example"
        self.file_records = []
        self.visible_file_records = []
        self.file_sort_mode = "Name (A-Z)"
        self.file_search_query = ""
        self.chat_messages = ["old"]
        self.current_chat_id = "old"
        self.chat_file_context = ["old"]
        self.chat_file_meta = ["old"]
        self.datei_liste_view = FakeView()
        self.login_view = FakeView()
        self.chat_view = FakeView()
        self.stack = FakeStack()
        self.file_mutation_flow = FakeFileMutationFlow()


def test_acceptance_load_files_and_reset_chat(monkeypatch):
    controller = FakeController()
    flow = file_list_flow(controller)

    class FakeResponse:
        status_code = 200

        def json(self):
            return [{"id": 1, "name": "report.pdf"}]

    monkeypatch.setattr(
        "controller.file_list_flow.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    flow.load_files_and_show()
    assert controller.file_records
    assert controller.datei_liste_view.items == ["1: report.pdf"]
    assert controller.chat_messages == []
    assert controller.current_chat_id is None
    assert controller.file_mutation_flow.called is True
    assert controller.stack.current == controller.datei_liste_view
