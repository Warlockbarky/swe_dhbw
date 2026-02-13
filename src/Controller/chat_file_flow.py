import requests
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QVBoxLayout,
)

from controller.chat_worker import extract_text_from_downloaded_content


class chat_file_flow:
    def __init__(self, controller):
        self.controller = controller

    def on_chat_select_files_clicked(self):
        if not self.controller.auth_token:
            self.controller.chat_view.show_error("Bitte zuerst einloggen.")
            return

        records = self.prompt_select_files()
        if records is None:
            return

        if not records:
            self.set_chat_files([])
            return

        try:
            self.set_chat_files(records)
        except RuntimeError as exc:
            self.controller.chat_view.show_error(str(exc))

    def on_chat_clear_files_clicked(self):
        self.set_chat_files([])

    def prompt_select_files(self) -> list[dict] | None:
        if not self.controller.visible_file_records:
            self.controller.chat_view.show_error("Keine Dateien verfuegbar.")
            return None

        dialog = QDialog(self.controller.chat_view)
        dialog.setWindowTitle("Dateien auswaehlen")
        layout = QVBoxLayout(dialog)
        info = QLabel("Waehle eine oder mehrere Dateien fuer den Chat.")
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        selected_ids = {str(item.get("id")) for item in self.controller.chat_file_meta}
        for record in self.controller.visible_file_records:
            file_id = record.get("id")
            name = record.get("name") or "Datei"
            label = f"{file_id}: {name}" if file_id is not None else str(name)
            list_widget.addItem(label)
            if file_id is not None and str(file_id) in selected_ids:
                list_widget.item(list_widget.count() - 1).setSelected(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(info)
        layout.addWidget(list_widget)
        layout.addWidget(buttons)

        if dialog.exec() != dialog.DialogCode.Accepted:
            return None

        records = []
        for item in list_widget.selectedIndexes():
            idx = item.row()
            if 0 <= idx < len(self.controller.visible_file_records):
                records.append(self.controller.visible_file_records[idx])
        return records

    def set_chat_files(self, records: list[dict]):
        if not records:
            self.controller.chat_file_context = []
            self.controller.chat_file_meta = []
            self.controller.chat_view.set_selected_files([])
            if (
                not self.controller.is_temp_chat
                and self.controller.chat_started
                and self.controller.current_chat_id
            ):
                self.controller.chat_core_flow.persist_current_chat()
            return

        contexts = self.load_chat_file_contexts(records)
        self.controller.chat_file_context = contexts
        self.controller.chat_file_meta = [
            {"id": record.get("id"), "name": record.get("name")}
            for record in records
        ]
        names = [record.get("name") or f"file_{record.get('id')}" for record in records]
        self.controller.chat_view.set_selected_files(names)
        if (
            not self.controller.is_temp_chat
            and self.controller.chat_started
            and self.controller.current_chat_id
        ):
            self.controller.chat_core_flow.persist_current_chat()

    def load_chat_file_contexts(self, records: list[dict]) -> list[dict]:
        contexts = []
        for record in records:
            file_id = record.get("id")
            if file_id is None:
                raise RuntimeError("Ausgewaehlter Eintrag hat keine Datei-ID.")
            name = record.get("name") or f"file_{file_id}"
            text = self.download_file_text(file_id, name)
            contexts.append({"id": file_id, "name": name, "content": text})
        return contexts

    def download_file_text(self, file_id: str | int, name: str) -> str:
        resp = requests.get(
            f"{self.controller.api_base_url}/files/{file_id}/download",
            headers={"Authorization": f"Bearer {self.controller.auth_token}"},
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
        return content[:max_chars]

    def open_history_entry(self, history: list[dict], idx: int):
        self.controller.is_temp_chat = False
        self.controller.chat_started = True
        entry = history[idx]
        self.controller.current_chat_id = entry.get("id")
        self.controller.chat_messages = entry.get("messages", [])
        self.controller.chat_file_meta = entry.get("files", [])
        if self.controller.chat_file_meta:
            try:
                self.controller.chat_file_context = self.load_chat_file_contexts(
                    self.controller.chat_file_meta
                )
            except RuntimeError as exc:
                self.controller.chat_file_context = []
                self.controller.chat_file_meta = []
                self.controller.chat_view.set_selected_files([])
                self.controller.history_view.show_error(str(exc))
            else:
                names = [
                    record.get("name") or f"file_{record.get('id')}"
                    for record in self.controller.chat_file_meta
                ]
                self.controller.chat_view.set_selected_files(names)
        else:
            self.controller.chat_file_context = []
            self.controller.chat_view.set_selected_files([])
        self.controller.chat_view.clear_chat()
        self.controller.chat_core_flow.render_chat_messages(self.controller.chat_messages)
        self.controller.stack.setCurrentWidget(self.controller.chat_view)
        self.controller.chat_view.set_temp_chat_checked(False)
        self.controller.chat_view.set_temp_chat_enabled(False)
