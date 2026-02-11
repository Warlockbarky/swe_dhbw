import io
import json
import sys
from datetime import datetime
from pathlib import Path

import requests
from PyPDF2 import PdfReader
from PyQt6.QtCore import QObject, QSettings, QThread, QTimer, pyqtSignal, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
)

from View.MenueView import MenueView
from View.LoginView import LoginView
from View.PfadView import PfadView
from View.DateiListeView import DateiListeView
from View.ChatView import ChatView
from View.ChatHistoryView import ChatHistoryView
from View.SettingsDialog import SettingsDialog

from Model.PfadValidator import PfadValidator
from Controller.DateiManager import DateiManager
from Controller.BackupManager import BackupManager
from Controller.KIAnalyzer import KIAnalyzer


class _ChatWorker(QObject):
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(
        self,
        *,
        mode: str,
        payload: dict,
        analyzer: KIAnalyzer,
        api_base_url: str,
        auth_token: str,
        ai_prefs: str,
    ):
        super().__init__()
        self.mode = mode
        self.payload = payload
        self.analyzer = analyzer
        self.api_base_url = api_base_url
        self.auth_token = auth_token
        self.ai_prefs = ai_prefs

    def run(self):
        try:
            if self.mode == "summary":
                result = self._run_summary()
            elif self.mode == "chat":
                result = self._run_chat()
            else:
                raise ValueError("Unknown worker mode")
            self.finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))

    def _run_summary(self) -> dict:
        file_id = self.payload["file_id"]
        name = self.payload["name"]
        resp = requests.get(
            f"{self.api_base_url}/files/{file_id}/download",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            timeout=30,
        )
        if resp.status_code == 401:
            raise RuntimeError("Sitzung abgelaufen. Bitte erneut einloggen.")
        if resp.status_code == 403:
            raise RuntimeError("Kein Zugriff auf diese Datei.")
        if resp.status_code == 404:
            raise RuntimeError("Datei nicht gefunden.")
        if resp.status_code != 200:
            raise RuntimeError(f"Datei konnte nicht geladen werden (HTTP {resp.status_code}).")

        content_type = resp.headers.get("Content-Type", "").lower()
        if name.lower().endswith(".pdf") or content_type.startswith("application/pdf"):
            reader = PdfReader(io.BytesIO(resp.content))
            pages = [(page.extract_text() or "").strip() for page in reader.pages]
            content = "\n".join([p for p in pages if p])
        else:
            content = resp.content.decode("utf-8", errors="replace")

        if not content.strip():
            raise RuntimeError("Datei enthaelt keinen lesbaren Text.")

        max_chars = 12000
        trimmed = content[:max_chars]
        system_msg = (
            "You are a helpful assistant. Use the provided file context when relevant. "
            "If the question is not about the file, answer normally."
        )
        if self.ai_prefs:
            system_msg = f"{system_msg}\n\nUser preferences:\n{self.ai_prefs}"
        context_msg = f"File name: {name}\n\nFile content:\n{trimmed}"
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": context_msg},
        ]
        summary_prompt = "Bitte gib eine kurze Zusammenfassung des Dateiinhalts."
        messages.append({"role": "user", "content": summary_prompt})
        assistant_text = self.analyzer.chat(messages)
        return {"mode": "summary", "messages": messages, "assistant": assistant_text}

    def _run_chat(self) -> dict:
        messages = self.payload["messages"]
        assistant_text = self.analyzer.chat(messages)
        return {"mode": "chat", "assistant": assistant_text}

class FlowController:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.api_base_url = "http://localhost:8000"
        self.auth_token = None
        self.file_records = []
        self.ki_analyzer = KIAnalyzer()
        self.chat_messages = []
        self.current_chat_id = None
        self.is_temp_chat = False
        self.chat_started = False
        self.chat_file_context = []
        self.chat_file_meta = []
        self._chat_thread = None
        self._chat_worker = None
        self.settings = QSettings("swe_dhbw", "swe_dhbw")

        self.start_view = MenueView()
        self.login_view = LoginView()
        self.pfad_view = PfadView()
        self.datei_liste_view = DateiListeView()
        self.chat_view = ChatView()
        self.history_view = ChatHistoryView()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.start_view)
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.pfad_view)
        self.stack.addWidget(self.datei_liste_view)
        self.stack.addWidget(self.chat_view)
        self.stack.addWidget(self.history_view)

        # Controller/Model verdrahten
        self.pfad_validator = PfadValidator()
        self.datei_manager = DateiManager(self.pfad_validator)
        self.backup_manager = BackupManager(self.datei_manager)

        self.__setup_connections()
        self.__load_saved_credentials()
        self.__apply_saved_theme()

    def run(self):
        self.stack.setCurrentWidget(self.start_view)
        self.stack.show()
        self.__start_splash()
        return self.app.exec()

    def __setup_connections(self):
        self.login_view.get_btn_login().clicked.connect(self.__on_login_clicked)
        self.login_view.get_btn_register().clicked.connect(self.__on_register_clicked)

        self.datei_liste_view.get_btn_refresh().clicked.connect(self.__load_files_and_show)
        self.datei_liste_view.get_btn_history().clicked.connect(self.__on_history_clicked)
        self.datei_liste_view.get_btn_settings().clicked.connect(self.__on_settings_clicked)
        self.datei_liste_view.get_btn_logout().clicked.connect(self.__on_logout_clicked)
        self.datei_liste_view.get_btn_upload().clicked.connect(self.__on_upload_clicked)
        self.datei_liste_view.get_btn_download().clicked.connect(self.__on_download_clicked)
        self.datei_liste_view.get_btn_delete().clicked.connect(self.__on_delete_clicked)
        self.datei_liste_view.get_btn_ai_summary().clicked.connect(self.__on_ai_summary_clicked)
        self.datei_liste_view.get_btn_select_all().clicked.connect(self.__on_files_select_all_clicked)
        self.datei_liste_view.request_open.connect(self.__on_file_open_requested)
        self.datei_liste_view.request_details.connect(self.__on_file_details_requested)

        self.chat_view.get_btn_send().clicked.connect(self.__on_chat_send_clicked)
        self.chat_view.get_btn_back().clicked.connect(self.__on_chat_back_clicked)
        self.chat_view.get_btn_select_files().clicked.connect(self.__on_chat_select_files_clicked)
        self.chat_view.get_btn_clear_files().clicked.connect(self.__on_chat_clear_files_clicked)

        self.history_view.get_btn_open().clicked.connect(self.__on_history_open_clicked)
        self.history_view.get_btn_delete().clicked.connect(self.__on_history_delete_clicked)
        self.history_view.get_btn_select_all().clicked.connect(self.__on_history_select_all_clicked)
        self.history_view.get_btn_back().clicked.connect(self.__on_history_back_clicked)
        self.history_view.request_open.connect(self.__on_history_open_requested)

        self.pfad_view.get_btn_ok().clicked.connect(self.__on_pfad_ok)

    def __starte_login(self):
        self.stack.setCurrentWidget(self.login_view)
        self.__maybe_auto_login()

    def __start_splash(self):
        self.start_view.start_loading()
        QTimer.singleShot(1500, self.__show_greeting)

    def __show_greeting(self):
        remember = bool(self.settings.value("auth/remember", False, type=bool))
        username = self.settings.value("auth/username", "", type=str) if remember else ""
        username = username.strip() or None
        self.start_view.show_greeting(username)
        QTimer.singleShot(2200, self.__starte_login)

    def __on_login_clicked(self):
        username = self.login_view.get_username()
        password = self.login_view.get_password()

        if not username or not password:
            self.login_view.show_error("Bitte Benutzername und Passwort eingeben.")
            return

        try:
            resp = requests.post(
                f"{self.api_base_url}/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"username": username, "password": password},
                timeout=10,
            )
        except requests.RequestException as exc:
            self.login_view.show_error(f"Login fehlgeschlagen: {exc}")
            return

        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            if not token:
                self.login_view.show_error("Login fehlgeschlagen: Token fehlt in der Antwort.")
                return
            self.auth_token = token
            self.__save_credentials(username, password)
            self.__load_files_and_show()
            return

        if resp.status_code == 401:
            self.login_view.show_error("Login fehlgeschlagen: Ungueltige Zugangsdaten.")
            return

        self.login_view.show_error(
            f"Login fehlgeschlagen (HTTP {resp.status_code}). Bitte erneut versuchen."
        )

    def __on_settings_clicked(self):
        dialog = SettingsDialog(self.datei_liste_view)
        dialog.set_values(self.__get_settings_values())
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        values = dialog.get_values()
        self.__save_settings_values(values)
        self.__apply_theme_values(values)

    def __on_logout_clicked(self):
        self.auth_token = None
        self.file_records = []
        self.settings.remove("auth")
        self.datei_liste_view.set_items([])
        self.login_view.set_username("")
        self.login_view.set_password("")
        self.login_view.set_remember_checked(False)
        self.stack.setCurrentWidget(self.login_view)

    def __load_saved_credentials(self):
        remember = bool(self.settings.value("auth/remember", False, type=bool))
        if not remember:
            return
        username = self.settings.value("auth/username", "", type=str)
        password = self.settings.value("auth/password", "", type=str)
        if username:
            self.login_view.set_username(username)
        if password:
            self.login_view.set_password(password)
        self.login_view.set_remember_checked(True)

    def __maybe_auto_login(self):
        remember = bool(self.settings.value("auth/remember", False, type=bool))
        if not remember:
            return
        username = self.login_view.get_username()
        password = self.login_view.get_password()
        if not username or not password:
            return
        QTimer.singleShot(0, self.__on_login_clicked)

    def __save_credentials(self, username: str, password: str):
        if self.login_view.get_remember_checked():
            self.settings.setValue("auth/remember", True)
            self.settings.setValue("auth/username", username)
            self.settings.setValue("auth/password", password)
        else:
            self.settings.remove("auth")

    def __on_register_clicked(self):
        username = self.login_view.get_username()
        password = self.login_view.get_password()

        if not username or not password:
            self.login_view.show_error("Bitte Benutzername und Passwort eingeben.")
            return

        try:
            resp = requests.post(
                f"{self.api_base_url}/register",
                json={"username": username, "password_hash": password},
                timeout=10,
            )
        except requests.RequestException as exc:
            self.login_view.show_error(f"Registrierung fehlgeschlagen: {exc}")
            return

        if resp.status_code == 400:
            self.login_view.show_error("Registrierung fehlgeschlagen: Benutzername existiert bereits.")
            return

        if resp.status_code >= 400:
            self.login_view.show_error(
                f"Registrierung fehlgeschlagen (HTTP {resp.status_code}). Bitte erneut versuchen."
            )
            return

        print("Registrierung erfolgreich. Bitte einloggen.")

    def __load_files_and_show(self):
        if not self.auth_token:
            self.login_view.show_error("Bitte zuerst einloggen.")
            return

        try:
            resp = requests.get(
                f"{self.api_base_url}/files/",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=10,
            )
        except requests.RequestException as exc:
            self.login_view.show_error(f"Dateiliste konnte nicht geladen werden: {exc}")
            return

        if resp.status_code == 200:
            data = resp.json()
            self.file_records = self.__normalize_file_records(data)
            items = self.__format_file_labels(self.file_records)
            self.datei_liste_view.set_items(items)
            self.chat_messages = []
            self.current_chat_id = None
            self.chat_file_context = []
            self.chat_file_meta = []
            self.chat_view.clear_chat()
            self.chat_view.clear_chat_input()
            self.chat_view.set_selected_files([])
            self.__sync_files_to_folder()
            self.stack.setCurrentWidget(self.datei_liste_view)
            return

        if resp.status_code == 401:
            self.login_view.show_error("Sitzung abgelaufen. Bitte erneut einloggen.")
            self.stack.setCurrentWidget(self.login_view)
            return

        self.login_view.show_error(
            f"Dateiliste konnte nicht geladen werden (HTTP {resp.status_code})."
        )

    @staticmethod
    def __normalize_file_records(data):
        if not isinstance(data, list):
            return []

        records = []
        for item in data:
            if isinstance(item, dict):
                file_id = item.get("id")
                name = (
                    item.get("filename")
                    or item.get("name")
                    or item.get("original_filename")
                    or item.get("path")
                )
                records.append(
                    {
                        "id": file_id,
                        "name": name,
                        "size": item.get("size")
                        or item.get("file_size")
                        or item.get("filesize"),
                        "created_at": item.get("created_at")
                        or item.get("created")
                        or item.get("uploaded_at"),
                        "updated_at": item.get("updated_at")
                        or item.get("modified_at")
                        or item.get("updated"),
                    }
                )
            else:
                records.append({"id": None, "name": str(item)})

        return records

    @staticmethod
    def __format_file_labels(records):
        items = []
        for record in records:
            file_id = record.get("id")
            name = record.get("name") or "Datei"
            if file_id is not None:
                label = f"{file_id}: {name}"
            else:
                label = str(name)
            items.append(label)
        return items

    @staticmethod
    def __format_size(value) -> str:
        try:
            size = int(value)
        except (TypeError, ValueError):
            return ""
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size_float = float(size)
        while size_float >= 1024 and unit_index < len(units) - 1:
            size_float /= 1024.0
            unit_index += 1
        if unit_index == 0:
            return f"{int(size_float)} {units[unit_index]}"
        return f"{size_float:.1f} {units[unit_index]}"

    @staticmethod
    def __format_date(value) -> str:
        if not value:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M")
        try:
            text = str(value).replace("Z", "+00:00")
            parsed = datetime.fromisoformat(text)
            return parsed.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return str(value)

    def __on_download_clicked(self):
        if not self.auth_token:
            self.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return

        idx = self.datei_liste_view.get_selected_index()
        if idx < 0 or idx >= len(self.file_records):
            self.datei_liste_view.show_error("Bitte eine Datei aus der Liste auswaehlen.")
            return

        record = self.file_records[idx]
        file_id = record.get("id")
        if file_id is None:
            self.datei_liste_view.show_error("Ausgewaehlter Eintrag hat keine Datei-ID.")
            return

        suggested_name = record.get("name") or f"file_{file_id}"
        default_dir = self.settings.value("files/default_dir", "", type=str)
        save_path = self.datei_liste_view.prompt_save_path(suggested_name, default_dir)
        if not save_path:
            return

        try:
            resp = requests.get(
                f"{self.api_base_url}/files/{file_id}/download",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=30,
                stream=True,
            )
        except requests.RequestException as exc:
            self.datei_liste_view.show_error(f"Download fehlgeschlagen: {exc}")
            return

        if resp.status_code == 200:
            try:
                with open(save_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except OSError as exc:
                self.datei_liste_view.show_error(f"Datei konnte nicht gespeichert werden: {exc}")
                return
            print(f"Datei gespeichert: {save_path}")
            return

        if resp.status_code == 401:
            self.datei_liste_view.show_error("Sitzung abgelaufen. Bitte erneut einloggen.")
            self.stack.setCurrentWidget(self.login_view)
            return

        if resp.status_code == 403:
            self.datei_liste_view.show_error("Kein Zugriff auf diese Datei.")
            return

        if resp.status_code == 404:
            self.datei_liste_view.show_error("Datei nicht gefunden.")
            return

        self.datei_liste_view.show_error(
            f"Download fehlgeschlagen (HTTP {resp.status_code})."
        )

    def __on_file_details_requested(self, row: int):
        if row < 0 or row >= len(self.file_records):
            self.datei_liste_view.show_error("Bitte eine Datei aus der Liste auswaehlen.")
            return

        record = self.file_records[row]
        name = record.get("name") or "Datei"
        file_id = record.get("id")
        local_info = self.__get_local_file_info(record)
        size_label = local_info.get("size") or self.__format_size(record.get("size")) or "Unbekannt"
        created_label = local_info.get("created") or self.__format_date(record.get("created_at")) or "Unbekannt"

        details = [
            f"Name: {name}",
            f"ID: {file_id if file_id is not None else 'Unbekannt'}",
            f"Groesse: {size_label}",
            f"Erstellt: {created_label}",
        ]
        self.datei_liste_view.show_error("Dateidetails\n\n" + "\n".join(details))

    def __get_local_file_info(self, record: dict) -> dict:
        target_dir = self.__resolve_download_dir()
        if target_dir is None:
            return {}
        name = record.get("name") or ""
        file_id = record.get("id")
        safe_name = Path(name).name or (f"file_{file_id}" if file_id is not None else "")
        if not safe_name:
            return {}
        local_path = target_dir / safe_name
        if not local_path.exists():
            return {}
        try:
            stat = local_path.stat()
        except OSError:
            return {}
        created_ts = getattr(stat, "st_birthtime", None)
        if created_ts is None:
            created_ts = stat.st_mtime
        created_label = self.__format_date(datetime.fromtimestamp(created_ts)) if created_ts else ""
        return {
            "size": self.__format_size(stat.st_size),
            "created": created_label,
        }

    def __sync_files_to_folder(self):
        target = self.__resolve_download_dir()
        if target is None:
            return

        res = self.datei_manager.setze_und_pruefe_pfad(str(target))
        if not res.ok:
            self.datei_liste_view.show_error(f"{res.fehlertyp}: {res.msg}")
            return

        for record in self.file_records:
            file_id = record.get("id")
            if file_id is None:
                continue
            name = record.get("name") or f"file_{file_id}"
            safe_name = Path(name).name or f"file_{file_id}"
            dest = self.datei_manager.get_zielpfad() / safe_name
            if dest.exists():
                continue

            try:
                resp = requests.get(
                    f"{self.api_base_url}/files/{file_id}/download",
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    timeout=60,
                    stream=True,
                )
            except requests.RequestException as exc:
                self.datei_liste_view.show_error(f"Download fehlgeschlagen: {exc}")
                continue

            if resp.status_code == 401:
                self.datei_liste_view.show_error("Sitzung abgelaufen. Bitte erneut einloggen.")
                self.stack.setCurrentWidget(self.login_view)
                return

            if resp.status_code != 200:
                self.datei_liste_view.show_error(
                    f"Download fehlgeschlagen (HTTP {resp.status_code})."
                )
                continue

            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except OSError as exc:
                self.datei_liste_view.show_error(f"Datei konnte nicht gespeichert werden: {exc}")
                continue

    def __resolve_download_dir(self) -> Path | None:
        configured = self.settings.value("files/default_dir", "", type=str).strip()
        candidates = []
        if configured:
            candidates.append(Path(configured))
        candidates.append(Path.home() / "Downloads")

        for candidate in candidates:
            try:
                candidate = candidate.expanduser().resolve()
            except Exception:
                continue
            if candidate.exists() and candidate.is_dir():
                return candidate

        self.datei_liste_view.show_error("Kein gueltiger Download-Ordner gefunden.")
        return None

    def __on_upload_clicked(self):
        if not self.auth_token:
            self.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return

        default_dir = self.settings.value("files/default_dir", "", type=str)
        path = self.datei_liste_view.prompt_open_file(default_dir)
        if not path:
            return

        try:
            with open(path, "rb") as f:
                resp = requests.post(
                    f"{self.api_base_url}/files/upload",
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    files={"file": f},
                    timeout=60,
                )
        except OSError as exc:
            self.datei_liste_view.show_error(f"Datei konnte nicht gelesen werden: {exc}")
            return
        except requests.RequestException as exc:
            self.datei_liste_view.show_error(f"Upload fehlgeschlagen: {exc}")
            return

        if resp.status_code == 401:
            self.datei_liste_view.show_error("Sitzung abgelaufen. Bitte erneut einloggen.")
            self.stack.setCurrentWidget(self.login_view)
            return

        if resp.status_code >= 400:
            self.datei_liste_view.show_error(
                f"Upload fehlgeschlagen (HTTP {resp.status_code})."
            )
            return

        self.__load_files_and_show()

    def __on_delete_clicked(self):
        if not self.auth_token:
            self.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return

        checked_rows = self.datei_liste_view.get_checked_indices()
        selected_rows = self.datei_liste_view.get_selected_indices()
        selected_rows = sorted(set(checked_rows or selected_rows))
        if not selected_rows:
            self.datei_liste_view.show_error("Bitte eine Datei aus der Liste auswaehlen.")
            return

        records = []
        for row in selected_rows:
            if 0 <= row < len(self.file_records):
                records.append(self.file_records[row])

        if not records:
            self.datei_liste_view.show_error("Bitte eine Datei aus der Liste auswaehlen.")
            return

        if len(records) == 1:
            record = records[0]
            file_id = record.get("id")
            name = record.get("name") or f"file_{file_id}"
            confirm_text = f"Soll die Datei '{name}' wirklich geloescht werden?"
        else:
            confirm_text = f"Sollen {len(records)} Dateien wirklich geloescht werden?"

        confirm = QMessageBox.question(
            self.datei_liste_view,
            "Dateien loeschen",
            confirm_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        errors: list[str] = []
        for record in records:
            file_id = record.get("id")
            if file_id is None:
                errors.append("Ausgewaehlter Eintrag hat keine Datei-ID.")
                continue
            try:
                resp = requests.delete(
                    f"{self.api_base_url}/files/{file_id}",
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    timeout=30,
                )
            except requests.RequestException as exc:
                errors.append(f"Loeschen fehlgeschlagen: {exc}")
                continue

            if resp.status_code == 401:
                self.datei_liste_view.show_error("Sitzung abgelaufen. Bitte erneut einloggen.")
                self.stack.setCurrentWidget(self.login_view)
                return

            if resp.status_code == 403:
                errors.append("Kein Zugriff auf diese Datei.")
                continue

            if resp.status_code == 404:
                errors.append("Datei nicht gefunden.")
                continue

            if resp.status_code >= 400:
                errors.append(f"Loeschen fehlgeschlagen (HTTP {resp.status_code}).")
                continue

        self.__load_files_and_show()
        if errors:
            self.datei_liste_view.show_error("\n".join(errors))

    def __on_files_select_all_clicked(self):
        select_all = not self.datei_liste_view.are_all_checked()
        self.datei_liste_view.set_all_checked(select_all)

    def __on_file_open_requested(self, row: int):
        if not self.auth_token:
            self.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return
        if row < 0 or row >= len(self.file_records):
            self.datei_liste_view.show_error("Bitte eine Datei aus der Liste auswaehlen.")
            return
        record = self.file_records[row]
        local_path = self.__ensure_local_file(record)
        if local_path is None:
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(local_path))):
            self.datei_liste_view.show_error("Datei konnte nicht geoeffnet werden.")

    def __on_ai_summary_clicked(self):
        if not self.auth_token:
            self.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return
        self.is_temp_chat = False
        self.chat_started = False
        self.chat_view.clear_chat()
        self.chat_view.clear_chat_input()
        self.chat_file_context = []
        self.chat_file_meta = []
        self.chat_view.set_selected_files([])
        self.current_chat_id = None
        self.stack.setCurrentWidget(self.chat_view)
        self.chat_view.set_send_enabled(True)
        self.chat_view.set_temp_chat_checked(False)
        self.chat_view.set_temp_chat_enabled(True)

    def __on_chat_send_clicked(self):
        text = self.chat_view.get_chat_input().strip()
        if not text:
            return

        if not self.chat_started:
            self.is_temp_chat = self.chat_view.is_temp_chat_checked()
            if not self.is_temp_chat and not self.current_chat_id:
                self.current_chat_id = self.__new_chat_session(title="Chat")
            self.chat_started = True
            self.chat_view.set_temp_chat_enabled(False)

        self.chat_view.add_message("user", text)
        self.chat_view.clear_chat_input()
        self.chat_messages.append({"role": "user", "content": text})
        self.chat_view.set_send_enabled(False)
        self.chat_view.start_loading()
        self.__start_chat_worker(
            mode="chat",
            payload={"messages": self.__build_chat_request_messages()},
        )

    def __on_chat_back_clicked(self):
        if self.is_temp_chat:
            self.current_chat_id = None
            self.chat_messages = []
            self.chat_file_context = []
            self.chat_file_meta = []
            self.chat_view.clear_chat()
            self.chat_view.clear_chat_input()
            self.chat_view.set_selected_files([])
            self.chat_view.set_temp_chat_checked(False)
            self.chat_view.set_temp_chat_enabled(True)
            self.chat_started = False
        self.stack.setCurrentWidget(self.datei_liste_view)

    def __on_history_clicked(self):
        items = self.__format_history_items(self.__load_history())
        self.history_view.set_items(items)
        self.stack.setCurrentWidget(self.history_view)

    def __on_history_open_clicked(self):
        self.is_temp_chat = False
        self.chat_started = True
        history = self.__load_history()
        idx = self.history_view.get_selected_index()
        if idx < 0 or idx >= len(history):
            self.history_view.show_error("Bitte einen Verlauf auswaehlen.")
            return
        self.__open_history_entry(history, idx)

    def __on_history_open_requested(self, row: int):
        history = self.__load_history()
        if row < 0 or row >= len(history):
            self.history_view.show_error("Bitte einen Verlauf auswaehlen.")
            return
        self.__open_history_entry(history, row)

    def __open_history_entry(self, history: list[dict], idx: int):
        self.is_temp_chat = False
        self.chat_started = True
        entry = history[idx]
        self.current_chat_id = entry.get("id")
        self.chat_messages = entry.get("messages", [])
        self.chat_file_meta = entry.get("files", [])
        if self.chat_file_meta:
            try:
                self.chat_file_context = self.__load_chat_file_contexts(self.chat_file_meta)
            except RuntimeError as exc:
                self.chat_file_context = []
                self.chat_file_meta = []
                self.chat_view.set_selected_files([])
                self.history_view.show_error(str(exc))
            else:
                names = [
                    record.get("name") or f"file_{record.get('id')}"
                    for record in self.chat_file_meta
                ]
                self.chat_view.set_selected_files(names)
        else:
            self.chat_file_context = []
            self.chat_view.set_selected_files([])
        self.chat_view.clear_chat()
        self.__render_chat_messages(self.chat_messages)
        self.stack.setCurrentWidget(self.chat_view)
        self.chat_view.set_temp_chat_checked(False)
        self.chat_view.set_temp_chat_enabled(False)

    def __on_history_delete_clicked(self):
        history = self.__load_history()
        checked_rows = self.history_view.get_checked_indices()
        selected_rows = self.history_view.get_selected_indices()
        selected_rows = sorted(set(checked_rows or selected_rows))
        if not selected_rows:
            self.history_view.show_error("Bitte einen Verlauf auswaehlen.")
            return

        entries = [history[row] for row in selected_rows if 0 <= row < len(history)]
        if not entries:
            self.history_view.show_error("Bitte einen Verlauf auswaehlen.")
            return

        if len(entries) == 1:
            title = entries[0].get("title") or "Chat"
            confirm_text = f"Soll der Chat '{title}' wirklich geloescht werden?"
        else:
            confirm_text = f"Sollen {len(entries)} Chats wirklich geloescht werden?"

        confirm = QMessageBox.question(
            self.history_view,
            "Chat loeschen",
            confirm_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        removed_ids = {entry.get("id") for entry in entries}
        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(history):
                history.pop(row)
        self.__save_history(history)
        if self.current_chat_id in removed_ids:
            self.current_chat_id = None
            self.chat_messages = []
            self.chat_file_context = []
            self.chat_file_meta = []
            self.chat_view.clear_chat()
            self.chat_view.set_selected_files([])
        self.history_view.set_items(self.__format_history_items(history))

    def __on_history_select_all_clicked(self):
        select_all = not self.history_view.are_all_checked()
        self.history_view.set_all_checked(select_all)

    def __ensure_local_file(self, record: dict) -> Path | None:
        target = self.__resolve_download_dir()
        if target is None:
            return None
        file_id = record.get("id")
        name = record.get("name") or ""
        safe_name = Path(name).name or (f"file_{file_id}" if file_id is not None else "")
        if not safe_name:
            self.datei_liste_view.show_error("Ausgewaehlter Eintrag hat keine Datei-ID.")
            return None
        dest = target / safe_name
        if dest.exists():
            return dest

        try:
            resp = requests.get(
                f"{self.api_base_url}/files/{file_id}/download",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=60,
                stream=True,
            )
        except requests.RequestException as exc:
            self.datei_liste_view.show_error(f"Download fehlgeschlagen: {exc}")
            return None

        if resp.status_code == 401:
            self.datei_liste_view.show_error("Sitzung abgelaufen. Bitte erneut einloggen.")
            self.stack.setCurrentWidget(self.login_view)
            return None

        if resp.status_code == 403:
            self.datei_liste_view.show_error("Kein Zugriff auf diese Datei.")
            return None

        if resp.status_code == 404:
            self.datei_liste_view.show_error("Datei nicht gefunden.")
            return None

        if resp.status_code != 200:
            self.datei_liste_view.show_error(
                f"Download fehlgeschlagen (HTTP {resp.status_code})."
            )
            return None

        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        except OSError as exc:
            self.datei_liste_view.show_error(f"Datei konnte nicht gespeichert werden: {exc}")
            return None

        return dest

    def __on_history_back_clicked(self):
        self.stack.setCurrentWidget(self.datei_liste_view)

    def __start_chat_worker(self, *, mode: str, payload: dict):
        if self._chat_thread is not None and self._chat_thread.isRunning():
            return
        thread = QThread()
        worker = _ChatWorker(
            mode=mode,
            payload=payload,
            analyzer=self.ki_analyzer,
            api_base_url=self.api_base_url,
            auth_token=self.auth_token or "",
            ai_prefs=self.__build_ai_preferences(),
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self.__on_chat_worker_finished)
        worker.failed.connect(self.__on_chat_worker_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(self.__on_chat_thread_finished)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(worker.deleteLater)
        self._chat_thread = thread
        self._chat_worker = worker
        thread.start()

    def __on_chat_worker_finished(self, result: dict):
        mode = result.get("mode")
        assistant_text = result.get("assistant", "")
        if mode == "summary":
            self.chat_messages = result.get("messages", [])
            if assistant_text:
                self.chat_messages.append({"role": "assistant", "content": assistant_text})
        else:
            if assistant_text:
                self.chat_messages.append({"role": "assistant", "content": assistant_text})

        self.chat_view.set_send_enabled(True)
        self.chat_view.stop_loading_and_stream(assistant_text)
        if not self.is_temp_chat and self.chat_started and self.current_chat_id:
            self.__persist_current_chat()

    def __on_chat_worker_failed(self, message: str):
        self.chat_view.set_send_enabled(True)
        self.chat_view.stop_loading_and_stream("")
        self.datei_liste_view.show_error(f"KI Chat fehlgeschlagen: {message}")

    def __on_chat_thread_finished(self):
        self._chat_thread = None
        self._chat_worker = None

    def __on_chat_select_files_clicked(self):
        if not self.auth_token:
            self.chat_view.show_error("Bitte zuerst einloggen.")
            return

        records = self.__prompt_select_files()
        if records is None:
            return

        if not records:
            self.__set_chat_files([])
            return

        try:
            self.__set_chat_files(records)
        except RuntimeError as exc:
            self.chat_view.show_error(str(exc))

    def __on_chat_clear_files_clicked(self):
        self.__set_chat_files([])

    def __prompt_select_files(self) -> list[dict] | None:
        if not self.file_records:
            self.chat_view.show_error("Keine Dateien verfuegbar.")
            return None

        dialog = QDialog(self.chat_view)
        dialog.setWindowTitle("Dateien auswaehlen")
        layout = QVBoxLayout(dialog)
        info = QLabel("Waehle eine oder mehrere Dateien fuer den Chat.")
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        selected_ids = {str(item.get("id")) for item in self.chat_file_meta}
        for record in self.file_records:
            file_id = record.get("id")
            name = record.get("name") or "Datei"
            label = f"{file_id}: {name}" if file_id is not None else str(name)
            list_widget.addItem(label)
            if file_id is not None and str(file_id) in selected_ids:
                list_widget.item(list_widget.count() - 1).setSelected(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(info)
        layout.addWidget(list_widget)
        layout.addWidget(buttons)

        if dialog.exec() != dialog.DialogCode.Accepted:
            return None

        records = []
        for item in list_widget.selectedIndexes():
            idx = item.row()
            if 0 <= idx < len(self.file_records):
                records.append(self.file_records[idx])
        return records

    def __set_chat_files(self, records: list[dict]):
        if not records:
            self.chat_file_context = []
            self.chat_file_meta = []
            self.chat_view.set_selected_files([])
            if not self.is_temp_chat and self.chat_started and self.current_chat_id:
                self.__persist_current_chat()
            return

        contexts = self.__load_chat_file_contexts(records)
        self.chat_file_context = contexts
        self.chat_file_meta = [
            {"id": record.get("id"), "name": record.get("name")}
            for record in records
        ]
        names = [record.get("name") or f"file_{record.get('id')}" for record in records]
        self.chat_view.set_selected_files(names)
        if not self.is_temp_chat and self.chat_started and self.current_chat_id:
            self.__persist_current_chat()

    def __load_chat_file_contexts(self, records: list[dict]) -> list[dict]:
        contexts = []
        for record in records:
            file_id = record.get("id")
            if file_id is None:
                raise RuntimeError("Ausgewaehlter Eintrag hat keine Datei-ID.")
            name = record.get("name") or f"file_{file_id}"
            text = self.__download_file_text(file_id, name)
            contexts.append({"id": file_id, "name": name, "content": text})
        return contexts

    def __download_file_text(self, file_id: str | int, name: str) -> str:
        resp = requests.get(
            f"{self.api_base_url}/files/{file_id}/download",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            timeout=30,
        )
        if resp.status_code == 401:
            raise RuntimeError("Sitzung abgelaufen. Bitte erneut einloggen.")
        if resp.status_code == 403:
            raise RuntimeError("Kein Zugriff auf diese Datei.")
        if resp.status_code == 404:
            raise RuntimeError("Datei nicht gefunden.")
        if resp.status_code != 200:
            raise RuntimeError(f"Datei konnte nicht geladen werden (HTTP {resp.status_code}).")

        content_type = resp.headers.get("Content-Type", "").lower()
        if name.lower().endswith(".pdf") or content_type.startswith("application/pdf"):
            reader = PdfReader(io.BytesIO(resp.content))
            pages = [(page.extract_text() or "").strip() for page in reader.pages]
            content = "\n".join([p for p in pages if p])
        else:
            content = resp.content.decode("utf-8", errors="replace")

        if not content.strip():
            raise RuntimeError("Datei enthaelt keinen lesbaren Text.")

        max_chars = 12000
        return content[:max_chars]

    def __build_chat_request_messages(self) -> list[dict]:
        system_msg = (
            "You are a helpful assistant. Use the provided file context when relevant. "
            "If the question is not about the file, answer normally."
        )
        ai_prefs = self.__build_ai_preferences()
        if ai_prefs:
            system_msg = f"{system_msg}\n\nUser preferences:\n{ai_prefs}"

        messages = [{"role": "system", "content": system_msg}]
        for entry in self.chat_file_context:
            name = entry.get("name") or "Datei"
            content = entry.get("content") or ""
            context_msg = f"File name: {name}\n\nFile content:\n{content}"
            messages.append({"role": "user", "content": context_msg})

        messages.extend(self.chat_messages)
        return messages

    def __get_settings_values(self) -> dict:
        return {
            "theme": self.settings.value("ui/theme", "Light", type=str),
            "palette": self.settings.value("ui/palette", "Emerald", type=str),
            "default_path": self.settings.value("files/default_dir", "", type=str),
            "ai_tone": self.settings.value("ai/tone", "Neutral", type=str),
            "ai_format": self.settings.value("ai/format", "Markdown", type=str),
            "ai_length": self.settings.value("ai/length", "Medium", type=str),
            "ai_notes": self.settings.value("ai/notes", "", type=str),
        }

    def __save_settings_values(self, values: dict):
        self.settings.setValue("ui/theme", values.get("theme", "Light"))
        self.settings.setValue("ui/palette", values.get("palette", "Emerald"))
        self.settings.setValue("files/default_dir", values.get("default_path", ""))
        self.settings.setValue("ai/tone", values.get("ai_tone", "Neutral"))
        self.settings.setValue("ai/format", values.get("ai_format", "Markdown"))
        self.settings.setValue("ai/length", values.get("ai_length", "Medium"))
        self.settings.setValue("ai/notes", values.get("ai_notes", ""))

    def __apply_theme_values(self, values: dict):
        theme = (values.get("theme") or "Light").lower()
        palette = (values.get("palette") or "Emerald").lower()
        for view in (
            self.start_view,
            self.login_view,
            self.pfad_view,
            self.datei_liste_view,
            self.chat_view,
            self.history_view,
        ):
            view.apply_theme(theme, palette)

    def __apply_saved_theme(self):
        self.__apply_theme_values(self.__get_settings_values())

    def __build_ai_preferences(self) -> str:
        values = self.__get_settings_values()
        parts = [
            f"Tone: {values.get('ai_tone', 'Neutral')}",
            f"Format: {values.get('ai_format', 'Markdown')}",
            f"Length: {values.get('ai_length', 'Medium')}",
        ]
        notes = values.get("ai_notes", "")
        if notes:
            parts.append(f"Notes: {notes}")
        return "\n".join(parts)

    def __new_chat_session(self, *, title: str) -> str:
        if self.is_temp_chat:
            return ""
        chat_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.current_chat_id = chat_id
        self.chat_messages = []
        self.chat_file_context = []
        self.chat_file_meta = []
        history = self.__load_history()
        history.insert(0, {
            "id": chat_id,
            "title": title,
            "messages": [],
            "files": [],
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        })
        self.__save_history(history)
        return chat_id

    def __persist_current_chat(self):
        if not self.current_chat_id:
            return
        history = self.__load_history()
        for entry in history:
            if entry.get("id") == self.current_chat_id:
                entry["messages"] = list(self.chat_messages)
                entry["files"] = list(self.chat_file_meta)
                entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
                break
        self.__save_history(history)

    def __render_chat_messages(self, messages: list[dict]):
        for msg in messages:
            role = msg.get("role")
            if role not in {"user", "assistant"}:
                continue
            text = str(msg.get("content") or "")
            self.chat_view.add_message(role, text, stream=False)
        self.chat_view.refresh_message_sizes()

    def __load_history(self) -> list[dict]:
        raw = self.settings.value("chat/history", "[]", type=str)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if isinstance(data, list):
            return data
        return []

    def __save_history(self, history: list[dict]):
        self.settings.setValue("chat/history", json.dumps(history))

    @staticmethod
    def __format_history_items(history: list[dict]) -> list[str]:
        items = []
        for entry in history:
            title = entry.get("title") or "Chat"
            updated = entry.get("updated_at") or ""
            if updated:
                items.append(f"{title}  ({updated})")
            else:
                items.append(str(title))
        return items

    def __on_pfad_ok(self):
        pfad_str = self.pfad_view.get_path()

        res = self.datei_manager.setze_und_pruefe_pfad(pfad_str)
        if not res.ok:
            # aktuell nur print – du kannst hier auch QMessageBox nutzen
            self.pfad_view.show_error(f"{res.fehlertyp}: {res.msg}")
            return

        # Wenn ok -> Backup starten
        self.backup_manager.starte_backup()
