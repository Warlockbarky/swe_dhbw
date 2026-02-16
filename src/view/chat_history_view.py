"""Chat history view for browsing and managing past sessions."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
)

from view.hauptoberflaeche import hauptoberflaeche


class chat_history_view(hauptoberflaeche):
    """Lists chat sessions and exposes selection helpers."""
    request_open = pyqtSignal(int)
    sort_changed = pyqtSignal(str)
    request_rename = pyqtSignal()
    search_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.list_widget = QListWidget()
        self.btn_open = QPushButton("Oeffnen")
        self.btn_delete = QPushButton("Loeschen")
        self.btn_rename = QPushButton("Umbenennen")
        self.btn_select_all = QPushButton("Alle auswaehlen")
        self.btn_back = QPushButton("Zurueck")
        self.sort_combo = QComboBox()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Chat suchen...")
        self.sort_combo.addItems(
            [
                "Datum (neu-alt)",
                "Datum (alt-neu)",
                "Name (A-Z)",
                "Name (Z-A)",
            ]
        )
        self.btn_open.setObjectName("PrimaryButton")
        self.btn_delete.setObjectName("DangerButton")
        self.btn_rename.setObjectName("SecondaryButton")
        self.btn_select_all.setObjectName("GhostButton")
        self.btn_back.setObjectName("SecondaryButton")
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_widget.itemDoubleClicked.connect(self.__on_item_double_clicked)
        self.sort_combo.currentTextChanged.connect(self.sort_changed.emit)
        self.search_input.textChanged.connect(self.search_changed.emit)
        self.btn_rename.clicked.connect(self.request_rename.emit)
        self.__fenster_erstellen()

    def __fenster_erstellen(self):
        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self.search_input)
        actions.addWidget(self.sort_combo)
        actions.addWidget(self.btn_open)
        actions.addWidget(self.btn_delete)
        actions.addWidget(self.btn_rename)
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

    def get_btn_rename(self):
        return self.btn_rename

    def get_btn_select_all(self):
        return self.btn_select_all

    def get_btn_back(self):
        return self.btn_back

    def get_sort_mode(self) -> str:
        return self.sort_combo.currentText()

    def get_search_query(self) -> str:
        return self.search_input.text().strip()

    def __on_item_double_clicked(self, item):
        row = self.list_widget.row(item)
        self.request_open.emit(row)
