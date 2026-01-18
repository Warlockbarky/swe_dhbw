from PyQt6.QtWidgets import QWidget, QVBoxLayout

class Hauptoberflaeche(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudyAssistant")
        self.resize(400, 300)
        self.layout = QVBoxLayout(self)

    def setInhalt(self, widget: QWidget):
        while self.layout.count():
            self.layout.takeAt(0).widget().deleteLater()
        self.layout.addWidget(widget)
