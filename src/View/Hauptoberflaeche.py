from PyQt6.QtWidgets import QWidget, QLabel

class Hauptoberflaeche(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudyAssistant - MVP Start")
        self.setGeometry(100, 100, 400, 200)

        label = QLabel("StudyAssistant is initializing...", self)
        label.move(100, 80)

    def anzeigen(self):
        self.show()
