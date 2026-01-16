import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

class Hauptoberflaeche:
    app = QApplication(sys.argv)
    window = QWidget()
    def __init__(self):
        print("Hauptoberflaeche")
    def anzeigen(self):
        print("anzeigen")
        self.window.setWindowTitle('StudyAssistant - MVP Start')
        self.window.setGeometry(100, 100, 400, 200)
        label = QLabel('StudyAssistant is initializing...', parent=self.window)
        label.move(100, 80)
        self.window.show()
        sys.exit(self.app.exec())
    def ladeHauptmenue(self):
        print("lade Hauptmenue")
