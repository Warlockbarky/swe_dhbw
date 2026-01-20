import sys
from PyQt6.QtWidgets import QApplication

from View.LoginView import LoginView
from View.MenueView import MenueView
from View.PfadView import PfadView


class LoginController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.start_view = MenueView()
        self.login_view = LoginView()
        self.pfad_view = PfadView()

    def run(self):
        self.start_view.get_btn_start().clicked.connect(self.__starte_login)
        self.start_view.get_btn_stop().clicked.connect(self.app.quit)
        self.start_view.show_UI()
        return self.app.exec()
    def __starte_login(self):
        print("starteLogin")
        self.start_view.deleteLater()
        self.start_view = None
        self.login_view.show_UI()
        self.login_view.get_btn_login().clicked.connect(self.__on_login_clicked)
    def __on_login_clicked(self):
        print("onLoginClicked")
        if self.__pruefe_login():
            self.__starte_pfad_auswahl()
        else: self.__zeige_fehler()
    def __exit(self):
        print("beenden des Programms")
        sys.exit(self.app.exec())
    def __pruefe_login(self):
        print("pruefeLogin")
        # Hier würden gewissen Moodle API Aufrufe stattfinden, allerdings ist dies aktuell nicht möglich
        # True zurückgeben, damit trotzdem weitergearbeitet werden kann
        return True

    def __starte_pfad_auswahl(self):
        print("pfad auswählen")
        self.login_view.deleteLater()
        self.login_view = None
        self.pfad_view.show_UI()
        self.pfad_view.get_btn_ok().clicked.connect(self.__pruefe_pfad)

    def __pruefe_pfad(self):
        print("pruefePfad")
        self.pfad_pruefen = self.pfad_view.get_path()
    def __zeige_fehler(self):
        print("zeigeFehler")