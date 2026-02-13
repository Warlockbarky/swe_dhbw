import requests
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox


class auth_flow:
    def __init__(self, controller):
        self.controller = controller

    def start_login(self):
        self.controller.stack.setCurrentWidget(self.controller.login_view)
        self.maybe_auto_login()

    def start_splash(self):
        self.controller.start_view.start_loading()
        QTimer.singleShot(1500, self.show_greeting)

    def show_greeting(self):
        settings = self.controller.settings
        remember = bool(settings.value("auth/remember", False, type=bool))
        username = settings.value("auth/username", "", type=str) if remember else ""
        username = username.strip() or None
        self.controller.start_view.show_greeting(username)
        QTimer.singleShot(2200, self.start_login)

    def on_login_clicked(self):
        username = self.controller.login_view.get_username()
        password = self.controller.login_view.get_password()

        if not username or not password:
            self.controller.login_view.show_error("Bitte Benutzername und Passwort eingeben.")
            return

        try:
            resp = requests.post(
                f"{self.controller.api_base_url}/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"username": username, "password": password},
                timeout=10,
            )
        except requests.RequestException as exc:
            self.controller.login_view.show_error(f"Login fehlgeschlagen: {exc}")
            return

        if resp.status_code == 200:
            self.controller.current_username = username
            self.controller.settings_flow.handle_first_login_settings()
            data = resp.json()
            token = data.get("access_token")
            if not token:
                self.controller.login_view.show_error(
                    "Login fehlgeschlagen: Token fehlt in der Antwort."
                )
                return
            self.controller.auth_token = token
            self.save_credentials(username, password)
            self.controller.file_list_flow.load_files_and_show()
            return

        if resp.status_code == 401:
            self.controller.login_view.show_error(
                "Login fehlgeschlagen: Ungueltige Zugangsdaten."
            )
            return

        self.controller.login_view.show_error(
            f"Login fehlgeschlagen (HTTP {resp.status_code}). Bitte erneut versuchen."
        )

    def on_register_clicked(self):
        username = self.controller.login_view.get_username()
        password = self.controller.login_view.get_password()

        if not username or not password:
            self.controller.login_view.show_error("Bitte Benutzername und Passwort eingeben.")
            return

        try:
            resp = requests.post(
                f"{self.controller.api_base_url}/register",
                json={"username": username, "password_hash": password},
                timeout=10,
            )
        except requests.RequestException as exc:
            self.controller.login_view.show_error(f"Registrierung fehlgeschlagen: {exc}")
            return

        if resp.status_code == 400:
            self.controller.login_view.show_error(
                "Registrierung fehlgeschlagen: Benutzername existiert bereits."
            )
            return

        if resp.status_code >= 400:
            self.controller.login_view.show_error(
                f"Registrierung fehlgeschlagen (HTTP {resp.status_code}). Bitte erneut versuchen."
            )
            return

        QMessageBox.information(
            self.controller.login_view,
            "Registrierung erfolgreich",
            "Der Benutzer wurde erfolgreich registriert. Bitte jetzt einloggen.",
        )

    def on_logout_clicked(self):
        self.controller.auth_token = None
        self.controller.current_username = None
        self.controller.file_records = []
        self.controller.visible_file_records = []
        self.controller.visible_history_entries = []
        self.controller.settings.remove("auth")
        self.controller.datei_liste_view.set_items([])
        self.controller.login_view.set_username("")
        self.controller.login_view.set_password("")
        self.controller.login_view.set_remember_checked(False)
        self.controller.stack.setCurrentWidget(self.controller.login_view)

    def load_saved_credentials(self):
        settings = self.controller.settings
        remember = bool(settings.value("auth/remember", False, type=bool))
        if not remember:
            return
        username = settings.value("auth/username", "", type=str)
        password = settings.value("auth/password", "", type=str)
        if username:
            self.controller.login_view.set_username(username)
        if password:
            self.controller.login_view.set_password(password)
        self.controller.login_view.set_remember_checked(True)

    def maybe_auto_login(self):
        settings = self.controller.settings
        remember = bool(settings.value("auth/remember", False, type=bool))
        if not remember:
            return
        username = self.controller.login_view.get_username()
        password = self.controller.login_view.get_password()
        if not username or not password:
            return
        QTimer.singleShot(0, self.on_login_clicked)

    def save_credentials(self, username: str, password: str):
        if self.controller.login_view.get_remember_checked():
            self.controller.settings.setValue("auth/remember", True)
            self.controller.settings.setValue("auth/username", username)
            self.controller.settings.setValue("auth/password", password)
        else:
            self.controller.settings.remove("auth")
