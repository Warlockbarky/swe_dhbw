from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QListWidget, QPushButton, QTextEdit

from View.Hauptoberflaeche import Hauptoberflaeche


class DateiListeView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.list_widget = QListWidget()
        self.btn_refresh = QPushButton("Aktualisieren")
        self.btn_download = QPushButton("Download")
        self.btn_ai_summary = QPushButton("KI Summary")
        self.summary_view = QTextEdit()
        self.summary_view.setReadOnly(True)
        self.__fenster_erstellen()

    def __fenster_erstellen(self):
        self.root.addWidget(self.list_widget)
        self.root.addWidget(self.btn_refresh, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.btn_download, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.btn_ai_summary, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.summary_view)
        self.mittig_auf_bildschirm()

    def set_items(self, items: list[str]):
        self.list_widget.clear()
        self.list_widget.addItems(items)
        self.summary_view.clear()

    def get_btn_refresh(self):
        return self.btn_refresh

    def get_btn_download(self):
        return self.btn_download

    def get_btn_ai_summary(self):
        return self.btn_ai_summary

    def get_selected_index(self) -> int:
        return self.list_widget.currentRow()

    def prompt_save_path(self, suggested_name: str) -> str:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Datei speichern",
            suggested_name,
        )
        return path

    def set_summary(self, text: str):
        self.summary_view.setPlainText(text)
