from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

from View.Hauptoberflaeche import Hauptoberflaeche


class MenueView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.setFixedSize(600, 300)
        # Setze Fenstergröße fest und nicht vergrößer/verkleinerbar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._oberflaeche_bauen()
        self._mittig_auf_bildschirm()


    def _mittig_auf_bildschirm(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
    def _oberflaeche_bauen(self):
        self.root.addStretch()
        self.root.addWidget(self.btn_start, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.btn_stop, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addStretch()
