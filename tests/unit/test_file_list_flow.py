from controller.file_list_flow import file_list_flow


class FakeFileAccessFlow:
    def __init__(self, info=None):
        self.info = info or {}

    def get_local_file_info(self, record):
        return dict(self.info)


class FakeView:
    def __init__(self):
        self.items = []
        self.errors = []

    def set_items(self, items):
        self.items = list(items)

    def show_error(self, msg: str):
        self.errors.append(msg)


class FakeController:
    def __init__(self):
        self.file_sort_mode = "Name (A-Z)"
        self.file_search_query = ""
        self.file_records = []
        self.visible_file_records = []
        self.datei_liste_view = FakeView()
        self.file_access_flow = FakeFileAccessFlow(
            {"size": "1 KB", "created": "2024-01-01 00:00"}
        )


def test_sorted_file_records_by_name():
    controller = FakeController()
    flow = file_list_flow(controller)
    records = [
        {"id": 1, "name": "b.txt"},
        {"id": 2, "name": "a.txt"},
    ]
    controller.file_sort_mode = "Name (Z-A)"
    sorted_records = flow.sorted_file_records(records)
    assert [r["name"] for r in sorted_records] == ["b.txt", "a.txt"]


def test_sorted_file_records_by_date():
    controller = FakeController()
    flow = file_list_flow(controller)
    controller.file_sort_mode = "Datum (alt-neu)"
    records = [
        {"id": 1, "name": "a", "created_at": "2024-01-02T00:00:00"},
        {"id": 2, "name": "b", "created_at": "2024-01-01T00:00:00"},
    ]
    sorted_records = flow.sorted_file_records(records)
    assert [r["id"] for r in sorted_records] == [2, 1]


def test_refresh_file_list_view_filters():
    controller = FakeController()
    flow = file_list_flow(controller)
    controller.file_records = [
        {"id": 1, "name": "report.pdf"},
        {"id": 2, "name": "notes.txt"},
    ]
    controller.file_search_query = "report"
    flow.refresh_file_list_view()
    assert controller.visible_file_records[0]["name"] == "report.pdf"
    assert controller.datei_liste_view.items == ["1: report.pdf"]


def test_on_file_details_requested_out_of_bounds():
    controller = FakeController()
    flow = file_list_flow(controller)
    controller.visible_file_records = []
    flow.on_file_details_requested(0)
    assert controller.datei_liste_view.errors


def test_on_file_details_requested_success():
    controller = FakeController()
    flow = file_list_flow(controller)
    controller.visible_file_records = [{"id": 1, "name": "report.pdf"}]
    flow.on_file_details_requested(0)
    assert controller.datei_liste_view.errors
    message = controller.datei_liste_view.errors[-1]
    assert "Name:" in message
    assert "ID:" in message
