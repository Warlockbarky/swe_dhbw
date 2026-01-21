from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QPushButton, QFileDialog

from View.Hauptoberflaeche import Hauptoberflaeche


class PfadView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.path_edit = QLineEdit()
        self.btn_browse = QPushButton("Durchsuchen…")
        self.btn_ok = QPushButton("OK")
        self.btn_ok.setEnabled(False)
        self.__pfad_fenster_erstellen()
        self.btn_browse.clicked.connect(self.__browse)
        self.path_edit.textChanged.connect(self.__update_ok_button)
    def __pfad_fenster_erstellen(self):
        print("pfadFensterErstellen")
        self.path_edit.setPlaceholderText("Pfad eingeben oder über 'Durchsuchen…' auswählen")
        self.root.addWidget(self.path_edit)
        self.root.addWidget(self.btn_browse)
        self.root.addWidget(self.btn_ok)
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