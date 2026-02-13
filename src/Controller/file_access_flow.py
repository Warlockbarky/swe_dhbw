"""File download and local open operations."""

from datetime import datetime
from pathlib import Path

import requests
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from controller.file_path_service import resolve_download_dir
from controller.file_utils import format_date, format_size


class file_access_flow:
    """Handles downloading files and opening cached local copies."""
    def __init__(self, controller):
        self.controller = controller

    def on_download_clicked(self):
        if not self.controller.auth_token:
            self.controller.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return

        idx = self.controller.datei_liste_view.get_selected_index()
        if idx < 0 or idx >= len(self.controller.visible_file_records):
            self.controller.datei_liste_view.show_error(
                "Bitte eine Datei aus der Liste auswaehlen."
            )
            return

        record = self.controller.visible_file_records[idx]
        file_id = record.get("id")
        if file_id is None:
            self.controller.datei_liste_view.show_error(
                "Ausgewaehlter Eintrag hat keine Datei-ID."
            )
            return

        suggested_name = record.get("name") or f"file_{file_id}"
        default_dir = self.controller.settings.value("files/default_dir", "", type=str)
        save_path = self.controller.datei_liste_view.prompt_save_path(
            suggested_name, default_dir
        )
        if not save_path:
            return

        try:
            resp = requests.get(
                f"{self.controller.api_base_url}/files/{file_id}/download",
                headers={"Authorization": f"Bearer {self.controller.auth_token}"},
                timeout=30,
                stream=True,
            )
        except requests.RequestException as exc:
            self.controller.datei_liste_view.show_error(f"Download fehlgeschlagen: {exc}")
            return

        if resp.status_code == 200:
            try:
                with open(save_path, "wb") as handle:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            handle.write(chunk)
            except OSError as exc:
                self.controller.datei_liste_view.show_error(
                    f"Datei konnte nicht gespeichert werden: {exc}"
                )
                return
            return

        if resp.status_code == 401:
            self.controller.datei_liste_view.show_error(
                "Sitzung abgelaufen. Bitte erneut einloggen."
            )
            self.controller.stack.setCurrentWidget(self.controller.login_view)
            return

        if resp.status_code == 403:
            self.controller.datei_liste_view.show_error("Kein Zugriff auf diese Datei.")
            return

        if resp.status_code == 404:
            self.controller.datei_liste_view.show_error("Datei nicht gefunden.")
            return

        self.controller.datei_liste_view.show_error(
            f"Download fehlgeschlagen (HTTP {resp.status_code})."
        )

    def on_file_open_requested(self, row: int):
        if not self.controller.auth_token:
            self.controller.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return
        if row < 0 or row >= len(self.controller.visible_file_records):
            self.controller.datei_liste_view.show_error(
                "Bitte eine Datei aus der Liste auswaehlen."
            )
            return
        record = self.controller.visible_file_records[row]
        local_path = self.ensure_local_file(record)
        if local_path is None:
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(local_path))):
            self.controller.datei_liste_view.show_error("Datei konnte nicht geoeffnet werden.")

    def get_local_file_info(self, record: dict) -> dict:
        """Return local metadata if a cached file exists, otherwise empty dict.

        Args:
            record (dict): File record with name and id fields.

        Returns:
            dict: Size/created metadata or an empty dict when missing.
        """
        target_dir = resolve_download_dir(self.controller.settings, self.controller.datei_liste_view)
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
        created_label = format_date(datetime.fromtimestamp(created_ts)) if created_ts else ""
        return {
            "size": format_size(stat.st_size),
            "created": created_label,
        }

    def ensure_local_file(self, record: dict) -> Path | None:
        target = resolve_download_dir(self.controller.settings, self.controller.datei_liste_view)
        if target is None:
            return None
        file_id = record.get("id")
        name = record.get("name") or ""
        safe_name = Path(name).name or (f"file_{file_id}" if file_id is not None else "")
        if not safe_name:
            self.controller.datei_liste_view.show_error(
                "Ausgewaehlter Eintrag hat keine Datei-ID."
            )
            return None
        dest = target / safe_name
        if dest.exists():
            # Reuse cached files to avoid redundant downloads.
            return dest

        try:
            resp = requests.get(
                f"{self.controller.api_base_url}/files/{file_id}/download",
                headers={"Authorization": f"Bearer {self.controller.auth_token}"},
                timeout=60,
                stream=True,
            )
        except requests.RequestException as exc:
            self.controller.datei_liste_view.show_error(f"Download fehlgeschlagen: {exc}")
            return None

        if resp.status_code == 401:
            self.controller.datei_liste_view.show_error(
                "Sitzung abgelaufen. Bitte erneut einloggen."
            )
            self.controller.stack.setCurrentWidget(self.controller.login_view)
            return None

        if resp.status_code == 403:
            self.controller.datei_liste_view.show_error("Kein Zugriff auf diese Datei.")
            return None

        if resp.status_code == 404:
            self.controller.datei_liste_view.show_error("Datei nicht gefunden.")
            return None

        if resp.status_code != 200:
            self.controller.datei_liste_view.show_error(
                f"Download fehlgeschlagen (HTTP {resp.status_code})."
            )
            return None

        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(dest, "wb") as handle:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        handle.write(chunk)
        except OSError as exc:
            self.controller.datei_liste_view.show_error(
                f"Datei konnte nicht gespeichert werden: {exc}"
            )
            return None

        return dest
