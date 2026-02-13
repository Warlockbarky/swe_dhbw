import json
from datetime import datetime

from PyQt6.QtCore import QSettings


class chat_history_service:
    def __init__(self, settings: QSettings):
        self.settings = settings

    def load(self) -> list[dict]:
        raw = self.settings.value("chat/history", "[]", type=str)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if isinstance(data, list):
            return data
        return []

    def save(self, history: list[dict]):
        self.settings.setValue("chat/history", json.dumps(history))

    def sort(self, history: list[dict], mode: str) -> list[dict]:
        entries = list(history)
        if mode == "Datum (alt-neu)":
            entries.sort(key=lambda e: self._parse_iso_datetime(e.get("updated_at")))
            return entries
        if mode == "Name (A-Z)":
            entries.sort(key=lambda e: str(e.get("title") or "").lower())
            return entries
        if mode == "Name (Z-A)":
            entries.sort(key=lambda e: str(e.get("title") or "").lower(), reverse=True)
            return entries

        entries.sort(key=lambda e: self._parse_iso_datetime(e.get("updated_at")), reverse=True)
        return entries

    @staticmethod
    def format_items(history: list[dict]) -> list[str]:
        items = []
        for entry in history:
            title = entry.get("title") or "Chat"
            updated = entry.get("updated_at") or ""
            if updated:
                items.append(f"{title}  ({updated})")
            else:
                items.append(str(title))
        return items

    def create_chat_session(self, *, title: str, files: list[dict]) -> str:
        chat_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        history = self.load()
        history.insert(
            0,
            {
                "id": chat_id,
                "title": title,
                "messages": [],
                "files": list(files),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            },
        )
        self.save(history)
        return chat_id

    def update_chat_session(self, *, chat_id: str, messages: list[dict], files: list[dict]):
        history = self.load()
        for entry in history:
            if entry.get("id") == chat_id:
                entry["messages"] = list(messages)
                entry["files"] = list(files)
                entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
                break
        self.save(history)

    @staticmethod
    def _parse_iso_datetime(value) -> datetime:
        if not value:
            return datetime.min
        if isinstance(value, datetime):
            return value
        try:
            text = str(value).replace("Z", "+00:00")
            return datetime.fromisoformat(text)
        except (ValueError, TypeError):
            return datetime.min
