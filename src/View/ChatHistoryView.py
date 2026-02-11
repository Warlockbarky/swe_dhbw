from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from View.Hauptoberflaeche import Hauptoberflaeche


class ChatHistoryView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.list_widget = QListWidget()
        self.btn_open = QPushButton("Oeffnen")
        self.btn_delete = QPushButton("Loeschen")
        self.btn_select_all = QPushButton("Alle auswaehlen")
        self.btn_back = QPushButton("Zurueck")
        self.btn_open.setObjectName("PrimaryButton")
        self.btn_delete.setObjectName("DangerButton")
        self.btn_select_all.setObjectName("GhostButton")
        self.btn_back.setObjectName("SecondaryButton")
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.__fenster_erstellen()

    def __fenster_erstellen(self):
        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self.btn_open)
        actions.addWidget(self.btn_delete)
        actions.addWidget(self.btn_select_all)
        actions.addStretch()
        actions.addWidget(self.btn_back)

        self.root.addWidget(self.list_widget)
        self.root.addLayout(actions)
        self.mittig_auf_bildschirm()

    def set_items(self, items: list[str]):
        self.list_widget.clear()
        for text in items:
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)

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

    def get_btn_open(self):
        return self.btn_open

    def get_btn_delete(self):
        return self.btn_delete

    def get_btn_select_all(self):
        return self.btn_select_all

    def get_btn_back(self):
        return self.btn_back
