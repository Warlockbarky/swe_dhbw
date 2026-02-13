import os

import pytest

from controller.ki_analyzer import ki_analyzer


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="OK"):
        self.status_code = status_code
        self._payload = payload or {"choices": [{"message": {"content": "Hi"}}]}
        self.text = text

    def json(self):
        return self._payload


def test_chat_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(ki_analyzer, "_load_dotenv", lambda self: None)
    analyzer = ki_analyzer()
    with pytest.raises(ValueError):
        analyzer.chat([{"role": "user", "content": "Hi"}])


def test_chat_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")

    def fake_post(url, headers=None, json=None, timeout=None):
        assert "Authorization" in headers
        assert json["model"]
        return FakeResponse()

    monkeypatch.setattr("controller.ki_analyzer.requests.post", fake_post)
    analyzer = ki_analyzer(max_wiederholungen=1)
    result = analyzer.chat([{"role": "user", "content": "Hello"}])
    assert result == "Hi"
