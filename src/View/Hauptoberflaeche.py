from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class Hauptoberflaeche(QWidget):
    def __init__(self, title: str = ""):
        super().__init__()
        self.root = QVBoxLayout(self)
        if title:
            self.root.addWidget(QLabel(title))
    def show_error(self, msg: str):
        print("ERROR:", msg)
    def show_UI(self):
        self.show()
