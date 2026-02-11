import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QVBoxLayout,
)

from View.Hauptoberflaeche import Hauptoberflaeche


class DateiListeView(Hauptoberflaeche):
    request_details = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.list_widget = QListWidget()
        self.btn_refresh = QPushButton("Aktualisieren")
        self.btn_history = QPushButton("Chat History")
        self.btn_settings = QPushButton("Settings")
        self.btn_logout = QPushButton("Logout")
        self.btn_upload = QPushButton("Upload")
        self.btn_download = QPushButton("Download")
        self.btn_delete = QPushButton("Delete")
        self.btn_ai_summary = QPushButton("KI Chat")
        self.btn_select_all = QPushButton("Alle auswaehlen")
        self.btn_upload.setObjectName("PrimaryButton")
        self.btn_download.setObjectName("SecondaryButton")
        self.btn_delete.setObjectName("DangerButton")
        self.btn_select_all.setObjectName("GhostButton")
        self.btn_refresh.setObjectName("GhostButton")
        self.btn_history.setObjectName("GhostButton")
        self.btn_settings.setObjectName("GhostButton")
        self.btn_logout.setObjectName("DangerButton")
        self.btn_ai_summary.setObjectName("SecondaryButton")
        self.list_widget.setMinimumHeight(140)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.__show_context_menu)
        self.__fenster_erstellen()

    def __fenster_erstellen(self):
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("Sidebar")
        sidebar = QVBoxLayout(sidebar_frame)
        sidebar.setContentsMargins(12, 12, 12, 12)
        sidebar.setSpacing(8)
        sidebar.addWidget(self.btn_refresh)
        sidebar.addWidget(self.btn_history)
        sidebar.addWidget(self.btn_upload)
        sidebar.addWidget(self.btn_download)
        sidebar.addWidget(self.btn_delete)
        sidebar.addWidget(self.btn_ai_summary)
        sidebar.addWidget(self.btn_select_all)
        sidebar.addStretch()
        sidebar.addWidget(self.btn_settings)
        sidebar.addWidget(self.btn_logout)

        content = QHBoxLayout()
        content.setSpacing(16)
        content.addWidget(sidebar_frame, stretch=0)
        content.addWidget(self.list_widget, stretch=1)

        self.root.addLayout(content)
        self.mittig_auf_bildschirm()

    def set_items(self, items: list[str]):
        self.list_widget.clear()
        for text in items:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)

    def get_btn_refresh(self):
        return self.btn_refresh

    def get_btn_download(self):
        return self.btn_download

    def get_btn_history(self):
        return self.btn_history

    def get_btn_settings(self):
        return self.btn_settings

    def get_btn_logout(self):
        return self.btn_logout

    def get_btn_upload(self):
        return self.btn_upload

    def get_btn_delete(self):
        return self.btn_delete

    def get_btn_ai_summary(self):
        return self.btn_ai_summary

    def get_btn_select_all(self):
        return self.btn_select_all

    def get_selected_index(self) -> int:
        return self.list_widget.currentRow()

    def get_selected_indices(self) -> list[int]:
        return [item.row() for item in self.list_widget.selectedIndexes()]

    def get_checked_indices(self) -> list[int]:
        indices = []
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                indices.append(row)
        return indices

    def set_all_checked(self, checked: bool):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item is not None:
                item.setCheckState(state)

    def are_all_checked(self) -> bool:
        if self.list_widget.count() == 0:
            return False
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item is None or item.checkState() != Qt.CheckState.Checked:
                return False
        return True

    def __show_context_menu(self, position):
        item = self.list_widget.itemAt(position)
        if item is None:
            return
        menu = QMenu(self)
        action = menu.addAction("Details anzeigen")
        selected_action = menu.exec(self.list_widget.mapToGlobal(position))
        if selected_action == action:
            row = self.list_widget.row(item)
            self.request_details.emit(row)

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

