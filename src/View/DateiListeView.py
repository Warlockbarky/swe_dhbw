import os

from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QListWidget, QPushButton, QVBoxLayout

from View.Hauptoberflaeche import Hauptoberflaeche


class DateiListeView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.list_widget = QListWidget()
        self.btn_refresh = QPushButton("Aktualisieren")
        self.btn_history = QPushButton("Chat History")
        self.btn_settings = QPushButton("Settings")
        self.btn_upload = QPushButton("Upload")
        self.btn_download = QPushButton("Download")
        self.btn_delete = QPushButton("Delete")
        self.btn_ai_summary = QPushButton("KI Chat")
        self.list_widget.setMinimumHeight(140)
        self.__fenster_erstellen()

    def __fenster_erstellen(self):
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        sidebar.addWidget(self.btn_refresh)
        sidebar.addWidget(self.btn_history)
        sidebar.addWidget(self.btn_upload)
        sidebar.addWidget(self.btn_download)
        sidebar.addWidget(self.btn_delete)
        sidebar.addWidget(self.btn_ai_summary)
        sidebar.addStretch()
        sidebar.addWidget(self.btn_settings)

        content = QHBoxLayout()
        content.setSpacing(16)
        content.addLayout(sidebar, stretch=0)
        content.addWidget(self.list_widget, stretch=1)

        self.root.addLayout(content)
        self.mittig_auf_bildschirm()

    def set_items(self, items: list[str]):
        self.list_widget.clear()
        self.list_widget.addItems(items)

    def get_btn_refresh(self):
        return self.btn_refresh

    def get_btn_download(self):
        return self.btn_download

    def get_btn_history(self):
        return self.btn_history

    def get_btn_settings(self):
        return self.btn_settings

    def get_btn_upload(self):
        return self.btn_upload

    def get_btn_delete(self):
        return self.btn_delete

    def get_btn_ai_summary(self):
        return self.btn_ai_summary

    def get_selected_index(self) -> int:
        return self.list_widget.currentRow()

    def prompt_save_path(self, suggested_name: str, default_dir: str = "") -> str:
        initial = os.path.join(default_dir, suggested_name) if default_dir else suggested_name
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Datei speichern",
            initial,
        )
        return path

    def prompt_open_file(self, default_dir: str = "") -> str:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Datei hochladen",
            default_dir,
        )
        return path

