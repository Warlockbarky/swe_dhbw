from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication


class Hauptoberflaeche(QWidget):
    def __init__(self, title: str = "", width: int = 400, height: int = 300):
        super().__init__()
        self.setFixedSize(width, height)
        self.root = QVBoxLayout(self)
        if title:
            self.root.addWidget(QLabel(title))
    def mittig_auf_bildschirm(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def show_error(self, msg: str):
        print("ERROR:", msg)
    def show_UI(self):
        self.show()
