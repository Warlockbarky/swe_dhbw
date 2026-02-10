from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.setModal(True)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])

        self.palette_combo = QComboBox()
        self.palette_combo.addItems(["Emerald", "Blue", "Slate"])

        self.default_path = QLineEdit()
        self.btn_browse = QPushButton("Browse")

        self.ai_tone = QComboBox()
        self.ai_tone.addItems(["Neutral", "Friendly", "Formal", "Concise"])

        self.ai_format = QComboBox()
        self.ai_format.addItems(["Markdown", "Plain", "Markdown+Code"])

        self.ai_length = QComboBox()
        self.ai_length.addItems(["Short", "Medium", "Detailed"])

        self.ai_notes = QLineEdit()

        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")

        self.__build_ui()

    def __build_ui(self):
        form = QFormLayout()
        form.addRow("Theme", self.theme_combo)
        form.addRow("Palette", self.palette_combo)

        path_row = QHBoxLayout()
        path_row.addWidget(self.default_path)
        path_row.addWidget(self.btn_browse)
        form.addRow("Default save path", path_row)

        form.addRow("AI tone", self.ai_tone)
        form.addRow("AI format", self.ai_format)
        form.addRow("AI length", self.ai_length)
        form.addRow("AI notes", self.ai_notes)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.btn_cancel)
        actions.addWidget(self.btn_save)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(actions)

        self.btn_browse.clicked.connect(self.__choose_path)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self.accept)

    def __choose_path(self):
        path = QFileDialog.getExistingDirectory(self, "Ordner waehlen")
        if path:
            self.default_path.setText(path)

    def set_values(self, values: dict):
        self.theme_combo.setCurrentText(values.get("theme", "Light"))
        self.palette_combo.setCurrentText(values.get("palette", "Emerald"))
        self.default_path.setText(values.get("default_path", ""))
        self.ai_tone.setCurrentText(values.get("ai_tone", "Neutral"))
        self.ai_format.setCurrentText(values.get("ai_format", "Markdown"))
        self.ai_length.setCurrentText(values.get("ai_length", "Medium"))
        self.ai_notes.setText(values.get("ai_notes", ""))

    def get_values(self) -> dict:
        return {
            "theme": self.theme_combo.currentText(),
            "palette": self.palette_combo.currentText(),
            "default_path": self.default_path.text().strip(),
            "ai_tone": self.ai_tone.currentText(),
            "ai_format": self.ai_format.currentText(),
            "ai_length": self.ai_length.currentText(),
            "ai_notes": self.ai_notes.text().strip(),
        }
