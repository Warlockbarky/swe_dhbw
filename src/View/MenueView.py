from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

from View.Hauptoberflaeche import Hauptoberflaeche


class MenueView(Hauptoberflaeche):
    btn_start = None
    btn_stop = None
    def __init__(self):
        super().__init__()
        self.__menue_fenster_erstellen()

    def __menue_fenster_erstellen(self):
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.fenstergrößen_fixierung()
        self.__oberflaeche_bauen()
        self.mittig_auf_bildschirm()
    def __oberflaeche_bauen(self):
        self.root.addStretch()
        self.root.addWidget(self.btn_start, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.btn_stop, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addStretch()
    def get_btn_start(self):
        return self.btn_start
    def get_btn_stop(self):
        return self.btn_stop