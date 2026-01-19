import sys
from PyQt6.QtWidgets import QApplication

from View.MenueView import MenueView

class LoginController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.start_view = MenueView()

    def run(self):
        self.start_view.show_UI()
        self.start_view.btn_start.clicked.connect(self.starte_login)
        #self.start_view.btn_stop.clicked.connect(self.exit)
    def starte_login(self):
        print("starteLogin")
    def exit(self):
        sys.exit(self.app.exec())
    def pruefe_login(self):
        print("pruefeLogin")
        # Return True just for demo purposes. Function will be implemented later
        return True

    def starte_sitzung(self):
        print("starteSitzung")

    def zeige_fehler(self):
        print("zeigeFehler")
