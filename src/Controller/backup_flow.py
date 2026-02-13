"""Backup flow for validating path selection and triggering backup."""


class backup_flow:
    """Validates the target path before executing the backup."""
    def __init__(self, controller):
        self.controller = controller

    def on_pfad_ok(self):
        pfad_str = self.controller.pfad_view.get_path()
        res = self.controller.datei_manager.setze_und_pruefe_pfad(pfad_str)
        if not res.ok:
            self.controller.pfad_view.show_error(f"{res.fehlertyp}: {res.msg}")
            return
        self.controller.backup_manager.starte_backup()
