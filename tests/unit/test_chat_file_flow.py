from controller.chat_file_flow import chat_file_flow


class DummyController:
    def __init__(self):
        self.api_base_url = "http://example"
        self.auth_token = "token"
        self.visible_file_records = []
        self.chat_file_context = []
        self.chat_file_meta = []
        self.chat_view = type("View", (), {"show_error": lambda *a, **k: None, "set_selected_files": lambda *a, **k: None})()


def test_load_chat_file_contexts_requires_id():
    controller = DummyController()
    flow = chat_file_flow(controller)
    try:
        flow.load_chat_file_contexts([{"name": "doc"}])
        assert False, "Expected RuntimeError"
    except RuntimeError:
        assert True


def test_download_file_text_errors(monkeypatch):
    controller = DummyController()
    flow = chat_file_flow(controller)

    class Resp:
        def __init__(self, status_code):
            self.status_code = status_code
            self.headers = {"Content-Type": "text/plain"}
            self.content = b""

    monkeypatch.setattr("controller.chat_file_flow.requests.get", lambda *a, **k: Resp(401))
    try:
        flow.download_file_text(1, "doc.txt")
        assert False
    except RuntimeError:
        assert True

    monkeypatch.setattr("controller.chat_file_flow.requests.get", lambda *a, **k: Resp(403))
    try:
        flow.download_file_text(1, "doc.txt")
        assert False
    except RuntimeError:
        assert True

    monkeypatch.setattr("controller.chat_file_flow.requests.get", lambda *a, **k: Resp(404))
    try:
        flow.download_file_text(1, "doc.txt")
        assert False
    except RuntimeError:
        assert True


def test_download_file_text_limits_size(monkeypatch):
    controller = DummyController()
    flow = chat_file_flow(controller)

    class Resp:
        status_code = 200
        headers = {"Content-Type": "text/plain"}
        content = b"data"

    monkeypatch.setattr("controller.chat_file_flow.requests.get", lambda *a, **k: Resp())
    monkeypatch.setattr(
        "controller.chat_file_flow.extract_text_from_downloaded_content",
        lambda **k: "x" * 13000,
    )

    result = flow.download_file_text(1, "doc.txt")
    assert len(result) == 12000
