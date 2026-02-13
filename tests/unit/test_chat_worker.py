import types

import pytest

from controller import chat_worker


def test_extract_text_from_text_payload():
    content = chat_worker.extract_text_from_downloaded_content(
        file_name="note.txt",
        content_type="text/plain",
        content_bytes=b"hello",
    )
    assert content == "hello"


def test_extract_text_from_pdf_payload(monkeypatch):
    class FakePage:
        def extract_text(self):
            return "Page"

    class FakeReader:
        def __init__(self, _):
            self.pages = [FakePage()]

    monkeypatch.setattr(chat_worker, "PdfReader", FakeReader)
    content = chat_worker.extract_text_from_downloaded_content(
        file_name="note.pdf",
        content_type="application/pdf",
        content_bytes=b"%PDF-1.4",
    )
    assert content == "Page"


def test_extract_text_empty_raises(monkeypatch):
    class FakePage:
        def extract_text(self):
            return ""

    class FakeReader:
        def __init__(self, _):
            self.pages = [FakePage()]

    monkeypatch.setattr(chat_worker, "PdfReader", FakeReader)
    with pytest.raises(RuntimeError):
        chat_worker.extract_text_from_downloaded_content(
            file_name="note.pdf",
            content_type="application/pdf",
            content_bytes=b"%PDF-1.4",
        )
