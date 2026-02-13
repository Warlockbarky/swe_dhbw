from controller.chat_history_service import chat_history_service


class FakeSettings:
    def __init__(self, initial=None):
        self.store = dict(initial or {})

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


def test_load_handles_invalid_json():
    settings = FakeSettings({"chat/history": "{bad}"})
    service = chat_history_service(settings)
    assert service.load() == []


def test_save_and_load_roundtrip():
    settings = FakeSettings()
    service = chat_history_service(settings)
    history = [{"id": "1", "title": "Chat"}]
    service.save(history)
    assert service.load() == history


def test_sorting_modes():
    settings = FakeSettings()
    service = chat_history_service(settings)
    history = [
        {"id": "1", "title": "B", "updated_at": "2024-01-02T00:00:00"},
        {"id": "2", "title": "A", "updated_at": "2024-01-01T00:00:00"},
    ]
    assert [e["id"] for e in service.sort(history, "Name (A-Z)")] == ["2", "1"]
    assert [e["id"] for e in service.sort(history, "Name (Z-A)")] == ["1", "2"]
    assert [e["id"] for e in service.sort(history, "Datum (alt-neu)")] == ["2", "1"]
    assert [e["id"] for e in service.sort(history, "Datum (neu-alt)")] == ["1", "2"]


def test_format_items():
    settings = FakeSettings()
    service = chat_history_service(settings)
    history = [{"title": "Chat", "updated_at": "2024-01-01"}, {"title": "X"}]
    assert service.format_items(history) == ["Chat  (2024-01-01)", "X"]


def test_create_and_update_chat_session():
    settings = FakeSettings({"chat/history": "[]"})
    service = chat_history_service(settings)
    chat_id = service.create_chat_session(title="Chat", files=[{"id": 1}])
    history = service.load()
    assert history[0]["id"] == chat_id
    service.update_chat_session(chat_id=chat_id, messages=[{"role": "user"}], files=[])
    updated = service.load()[0]
    assert updated["messages"] == [{"role": "user"}]
    assert updated["files"] == []
