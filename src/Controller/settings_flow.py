from View.SettingsDialog import SettingsDialog


class SettingsFlow:
    def __init__(self, controller):
        self.controller = controller

    def on_settings_clicked(self):
        dialog = SettingsDialog(self.controller.datei_liste_view)
        dialog.set_values(self.get_settings_values())
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        values = dialog.get_values()
        self.save_settings_values(values)
        self.apply_theme_values(values)

    def get_settings_values(self) -> dict:
        settings = self.controller.settings
        return {
            "theme": settings.value("ui/theme", "Light", type=str),
            "palette": settings.value("ui/palette", "Emerald", type=str),
            "default_path": settings.value("files/default_dir", "", type=str),
            "ai_tone": settings.value("ai/tone", "Neutral", type=str),
            "ai_format": settings.value("ai/format", "Markdown", type=str),
            "ai_length": settings.value("ai/length", "Medium", type=str),
            "ai_notes": settings.value("ai/notes", "", type=str),
        }

    def save_settings_values(self, values: dict):
        settings = self.controller.settings
        settings.setValue("ui/theme", values.get("theme", "Light"))
        settings.setValue("ui/palette", values.get("palette", "Emerald"))
        settings.setValue("files/default_dir", values.get("default_path", ""))
        settings.setValue("ai/tone", values.get("ai_tone", "Neutral"))
        settings.setValue("ai/format", values.get("ai_format", "Markdown"))
        settings.setValue("ai/length", values.get("ai_length", "Medium"))
        settings.setValue("ai/notes", values.get("ai_notes", ""))

    def apply_theme_values(self, values: dict):
        theme = (values.get("theme") or "Light").lower()
        palette = (values.get("palette") or "Emerald").lower()
        for view in (
            self.controller.start_view,
            self.controller.login_view,
            self.controller.pfad_view,
            self.controller.datei_liste_view,
            self.controller.chat_view,
            self.controller.history_view,
        ):
            view.apply_theme(theme, palette)

    def apply_saved_theme(self):
        self.apply_theme_values(self.get_settings_values())

    def build_ai_preferences(self) -> str:
        values = self.get_settings_values()
        parts = [
            f"Tone: {values.get('ai_tone', 'Neutral')}",
            f"Format: {values.get('ai_format', 'Markdown')}",
            f"Length: {values.get('ai_length', 'Medium')}",
        ]
        notes = values.get("ai_notes", "")
        if notes:
            parts.append(f"Notes: {notes}")
        return "\n".join(parts)

    def handle_first_login_settings(self):
        if self.controller.user_settings_store.exists(self.controller.current_username or ""):
            user_settings = self.controller.user_settings_store.load(
                self.controller.current_username or ""
            )
            self.apply_user_settings_values(user_settings)
        else:
            self.show_first_time_settings_dialog()

    def show_first_time_settings_dialog(self):
        dialog = SettingsDialog(self.controller.datei_liste_view)
        dialog.set_values(self.get_default_settings_values())

        if dialog.exec() != dialog.DialogCode.Accepted:
            values = self.get_default_settings_values()
        else:
            values = dialog.get_values()

        self.controller.user_settings_store.save(self.controller.current_username or "", values)
        self.save_settings_values(values)
        self.apply_theme_values(values)

    def apply_user_settings_values(self, user_settings: dict):
        if user_settings:
            self.save_settings_values(user_settings)
            self.apply_theme_values(user_settings)

    @staticmethod
    def get_default_settings_values() -> dict:
        return {
            "theme": "Light",
            "palette": "Emerald",
            "default_path": "",
            "ai_tone": "Neutral",
            "ai_format": "Markdown",
            "ai_length": "Medium",
            "ai_notes": "",
        }
