from PyQt6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from view.hauptoberflaeche import hauptoberflaeche


class pfad_view(hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.path_edit = QLineEdit()
        self.btn_browse = QPushButton("Durchsuchen…")
        self.btn_ok = QPushButton("OK")
        self.btn_browse.setObjectName("GhostButton")
        self.btn_ok.setObjectName("PrimaryButton")
        self.btn_ok.setEnabled(False)
        self.__pfad_fenster_erstellen()
        self.btn_browse.clicked.connect(self.__browse)
        self.path_edit.textChanged.connect(self.__update_ok_button)
    def __pfad_fenster_erstellen(self):
        print("pfadFensterErstellen")
        self.path_edit.setPlaceholderText("Pfad eingeben oder über 'Durchsuchen…' auswählen")
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        title = QLabel("Arbeitsordner")
        title.setObjectName("SectionTitle")
        card_layout.addWidget(title)

        label_path = QLabel("Pfad")
        label_path.setObjectName("FieldLabel")
        card_layout.addWidget(label_path)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(self.path_edit)
        row.addWidget(self.btn_browse)
        card_layout.addLayout(row)

        card_layout.addWidget(self.btn_ok)

        self.root.addStretch()
        self.root.addWidget(card)
        self.root.addStretch()
        self.mittig_auf_bildschirm()
    def __update_ok_button(self, text: str):
        self.btn_ok.setEnabled(bool(text.strip()))
    def __browse(self):
        #Ordnerauswahl(wenn du Dateien willst: getOpenFileName)
        folder = QFileDialog.getExistingDirectory(self, "Ordner auswählen")
        if folder:
            self.path_edit.setText(folder)
    def get_path(self):
        return self.path_edit.text().strip()
    def get_btn_ok(self):
        return self.btn_ok
