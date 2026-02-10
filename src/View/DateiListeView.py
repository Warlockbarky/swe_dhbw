from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QLineEdit, QListWidget, QPushButton, QTextEdit

from View.Hauptoberflaeche import Hauptoberflaeche


class DateiListeView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.list_widget = QListWidget()
        self.btn_refresh = QPushButton("Aktualisieren")
        self.btn_download = QPushButton("Download")
        self.btn_ai_summary = QPushButton("KI Chat")
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Nachricht an die KI...")
        self.btn_send = QPushButton("Senden")
        self.__fenster_erstellen()

    def __fenster_erstellen(self):
        self.root.addWidget(self.list_widget)
        self.root.addWidget(self.btn_refresh, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.btn_download, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.btn_ai_summary, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.chat_view)
        self.root.addWidget(self.chat_input)
        self.root.addWidget(self.btn_send, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mittig_auf_bildschirm()

    def set_items(self, items: list[str]):
        self.list_widget.clear()
        self.list_widget.addItems(items)
        self.chat_view.clear()
        self.chat_input.clear()

    def get_btn_refresh(self):
        return self.btn_refresh

    def get_btn_download(self):
        return self.btn_download

    def get_btn_ai_summary(self):
        return self.btn_ai_summary

    def get_btn_send(self):
        return self.btn_send

    def get_selected_index(self) -> int:
        return self.list_widget.currentRow()

    def prompt_save_path(self, suggested_name: str) -> str:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Datei speichern",
            suggested_name,
        )
        return path

    def append_chat(self, role: str, text: str):
        prefix = "AI" if role == "assistant" else "Du"
        self.chat_view.append(f"{prefix}: {text}")

    def get_chat_input(self) -> str:
        return self.chat_input.text()

    def clear_chat_input(self):
        self.chat_input.clear()

    def clear_chat(self):
        self.chat_view.clear()
