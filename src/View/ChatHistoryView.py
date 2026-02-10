from PyQt6.QtWidgets import QHBoxLayout, QListWidget, QPushButton, QVBoxLayout

from View.Hauptoberflaeche import Hauptoberflaeche


class ChatHistoryView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.list_widget = QListWidget()
        self.btn_open = QPushButton("Oeffnen")
        self.btn_delete = QPushButton("Loeschen")
        self.btn_back = QPushButton("Zurueck")
        self.__fenster_erstellen()

    def __fenster_erstellen(self):
        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self.btn_open)
        actions.addWidget(self.btn_delete)
        actions.addStretch()
        actions.addWidget(self.btn_back)

        self.root.addWidget(self.list_widget)
        self.root.addLayout(actions)
        self.mittig_auf_bildschirm()

    def set_items(self, items: list[str]):
        self.list_widget.clear()
        self.list_widget.addItems(items)

    def get_selected_index(self) -> int:
        return self.list_widget.currentRow()

    def get_btn_open(self):
        return self.btn_open

    def get_btn_delete(self):
        return self.btn_delete

    def get_btn_back(self):
        return self.btn_back
