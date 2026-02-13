import io

from PyPDF2 import PdfReader
from PyQt6.QtCore import QObject, pyqtSignal

from controller.ki_analyzer import ki_analyzer


def extract_text_from_downloaded_content(*, file_name: str, content_type: str, content_bytes: bytes) -> str:
    if file_name.lower().endswith(".pdf") or content_type.startswith("application/pdf"):
        reader = PdfReader(io.BytesIO(content_bytes))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        content = "\n".join([page for page in pages if page])
    else:
        content = content_bytes.decode("utf-8", errors="replace")

    if not content.strip():
        raise RuntimeError("Datei enthaelt keinen lesbaren Text.")

    return content


class chat_worker(QObject):
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(
        self,
        *,
        mode: str,
        payload: dict,
        analyzer: ki_analyzer,
        api_base_url: str,
        auth_token: str,
        ai_prefs: str,
    ):
        super().__init__()
        self.mode = mode
        self.payload = payload
        self.analyzer = analyzer
        self.api_base_url = api_base_url
        self.auth_token = auth_token
        self.ai_prefs = ai_prefs

    def run(self):
        try:
            if self.mode == "chat":
                result = self._run_chat()
            else:
                raise ValueError("Unknown worker mode")
            self.finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))

    def _run_chat(self) -> dict:
        messages = self.payload["messages"]
        assistant_text = self.analyzer.chat(messages)
        return {"mode": "chat", "assistant": assistant_text}
