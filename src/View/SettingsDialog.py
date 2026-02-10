from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.setModal(True)
        self.setObjectName("SettingsDialog")
        self.setMinimumWidth(520)

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

    @staticmethod
    def _build_field(label_text: str, field: QWidget) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)
        label = QLabel(label_text)
        label.setObjectName("FieldLabel")
        layout.addWidget(label)
        layout.addWidget(field)
        return layout

    def __build_ui(self):
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_cancel.setObjectName("SecondaryButton")
        self.btn_browse.setObjectName("GhostButton")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        general_card = QFrame()
        general_card.setObjectName("Card")
        general_layout = QVBoxLayout(general_card)
        general_layout.setContentsMargins(16, 16, 16, 16)
        general_layout.setSpacing(12)
        title_general = QLabel("Appearance")
        title_general.setObjectName("SectionTitle")
        general_layout.addWidget(title_general)
        general_layout.addLayout(self._build_field("Theme", self.theme_combo))
        general_layout.addLayout(self._build_field("Palette", self.palette_combo))

        path_row = QWidget()
        path_layout = QHBoxLayout(path_row)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(8)
        path_layout.addWidget(self.default_path)
        path_layout.addWidget(self.btn_browse)
        general_layout.addLayout(self._build_field("Default save path", path_row))

        ai_card = QFrame()
        ai_card.setObjectName("Card")
        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setContentsMargins(16, 16, 16, 16)
        ai_layout.setSpacing(12)
        title_ai = QLabel("AI preferences")
        title_ai.setObjectName("SectionTitle")
        ai_layout.addWidget(title_ai)
        ai_layout.addLayout(self._build_field("AI tone", self.ai_tone))
        ai_layout.addLayout(self._build_field("AI format", self.ai_format))
        ai_layout.addLayout(self._build_field("AI length", self.ai_length))
        ai_layout.addLayout(self._build_field("AI notes", self.ai_notes))

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addStretch()
        actions.addWidget(self.btn_cancel)
        actions.addWidget(self.btn_save)

        layout.addWidget(general_card)
        layout.addWidget(ai_card)
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
