from src.View.Hauptoberflaeche import Hauptoberflaeche


class LoginController:
    Oberflaeche = Hauptoberflaeche()
    def __init__(self):
        login_status = False
        fehlermeldung = ""
        self.starteLoginProzess()
    def starteLoginProzess(self):
        print("starte LoginProzess")
        self.Oberflaeche.anzeigen()
    def pruefeLogin(self):
        print("pruefeLogin")
    def starteSitzung(self):
        print("starteSitzung")
    def zeigeFehler(self):
        print("zeigeFehler")
