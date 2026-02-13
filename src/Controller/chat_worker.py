import io

import requests
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
            if self.mode == "summary":
                result = self._run_summary()
            elif self.mode == "chat":
                result = self._run_chat()
            else:
                raise ValueError("Unknown worker mode")
            self.finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))

    def _run_summary(self) -> dict:
        file_id = self.payload["file_id"]
        name = self.payload["name"]
        resp = requests.get(
            f"{self.api_base_url}/files/{file_id}/download",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            timeout=30,
        )
        if resp.status_code == 401:
            raise RuntimeError("Sitzung abgelaufen. Bitte erneut einloggen.")
        if resp.status_code == 403:
            raise RuntimeError("Kein Zugriff auf diese Datei.")
        if resp.status_code == 404:
            raise RuntimeError("Datei nicht gefunden.")
        if resp.status_code != 200:
            raise RuntimeError(f"Datei konnte nicht geladen werden (HTTP {resp.status_code}).")

        content = extract_text_from_downloaded_content(
            file_name=name,
            content_type=resp.headers.get("Content-Type", "").lower(),
            content_bytes=resp.content,
        )

        max_chars = 12000
        trimmed = content[:max_chars]
        system_msg = (
            "You are a helpful assistant. Use the provided file context when relevant. "
            "If the question is not about the file, answer normally."
        )
        if self.ai_prefs:
            system_msg = f"{system_msg}\n\nUser preferences:\n{self.ai_prefs}"
        context_msg = f"File name: {name}\n\nFile content:\n{trimmed}"
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": context_msg},
        ]
        summary_prompt = "Bitte gib eine kurze Zusammenfassung des Dateiinhalts."
        messages.append({"role": "user", "content": summary_prompt})
        assistant_text = self.analyzer.chat(messages)
        return {"mode": "summary", "messages": messages, "assistant": assistant_text}

    def _run_chat(self) -> dict:
        messages = self.payload["messages"]
        assistant_text = self.analyzer.chat(messages)
        return {"mode": "chat", "assistant": assistant_text}
