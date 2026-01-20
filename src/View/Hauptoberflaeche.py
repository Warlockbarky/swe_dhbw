from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication


class Hauptoberflaeche(QWidget):
    def __init__(self, title: str = ""):
        super().__init__()
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
