from controller.chat_core_flow import chat_core_flow


class FakeSettingsFlow:
    def build_ai_preferences(self) -> str:
        return "Tone: Friendly"


class FakeController:
    def __init__(self):
        self.settings_flow = FakeSettingsFlow()
        self.chat_file_context = [
            {"id": 1, "name": "doc.txt", "content": "Hello"}
        ]
        self.chat_messages = [{"role": "user", "content": "Hi"}]


def test_build_chat_request_messages_includes_context():
    controller = FakeController()
    flow = chat_core_flow(controller)
    messages = flow.build_chat_request_messages()
    assert messages[0]["role"] == "system"
    assert "Tone: Friendly" in messages[0]["content"]
    assert any("File name: doc.txt" in m["content"] for m in messages)
    assert messages[-1]["content"] == "Hi"
