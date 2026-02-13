import math

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QWidget

from view.hauptoberflaeche import hauptoberflaeche


class gradient_label(QLabel):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._phase = 0.0

    def set_phase(self, phase: float):
        self._phase = phase
        self.update()

    def paintEvent(self, _event):  # pylint: disable=invalid-name
        text = self.text()
        if not text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        hue_shift = (self._phase * 10.0) % 360
        start = QColor.fromHsv(int((260 + hue_shift) % 360), 200, 245)
        mid = QColor.fromHsv(int((220 + hue_shift) % 360), 210, 235)
        end = QColor.fromHsv(int((285 + hue_shift) % 360), 190, 250)

        rect = self.rect()
        width = max(120, rect.width())
        center = (math.sin(self._phase) + 1.0) * 0.5
        left = max(0.0, min(0.7, center - 0.25))
        right = min(1.0, left + 0.45)

        gradient = QLinearGradient(0, 0, width, 0)
        gradient.setColorAt(0.0, start)
        gradient.setColorAt(left, mid)
        gradient.setColorAt(right, end)
        gradient.setColorAt(1.0, start)

        painter.setPen(QPen(gradient, 0))
        painter.drawText(rect, self.alignment(), text)


class menue_view(hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self._dot_timer = QTimer(self)
        self._dot_timer.timeout.connect(self.__tick_loading)
        self._dot_index = 0
        self._gradient_timer = QTimer(self)
        self._gradient_timer.timeout.connect(self.__tick_gradient)
        self._gradient_phase = 0.0
        self.title = QLabel("OMAS Moodle Anwendung")
        self.title.setObjectName("SplashTitle")
        self.greeting_prefix = QLabel("")
        self.greeting_prefix.setObjectName("SplashGreetingPrefix")
        self.greeting_name = gradient_label("")
        self.greeting_name.setObjectName("SplashGreetingName")
        self.greeting_row = QWidget()
        self.greeting_row.setVisible(False)
        self.subtitle = QLabel("Initialisiere Anwendung")
        self.subtitle.setObjectName("SplashSubtitle")
        self.progress = QProgressBar()
        self.progress.setObjectName("SplashProgress")
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.__menue_fenster_erstellen()

    def __menue_fenster_erstellen(self):
        self.__oberflaeche_bauen()
        self.mittig_auf_bildschirm()
    def __oberflaeche_bauen(self):
        row_layout = QHBoxLayout(self.greeting_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        row_layout.addWidget(self.greeting_prefix)
        row_layout.addWidget(self.greeting_name)
        self.root.addStretch()
        self.root.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.greeting_row, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        self.root.addWidget(self.progress)
        self.root.addStretch()

    def start_loading(self):
        self.subtitle.setText("Initialisiere Anwendung")
        self.greeting_row.setVisible(False)
        self.progress.setVisible(True)
        self._dot_index = 0
        self._dot_timer.start(400)
        self._gradient_timer.stop()
        self.greeting_name.set_phase(0.0)

    def show_greeting(self, username: str | None):
        self._dot_timer.stop()
        self.progress.setVisible(False)
        if username:
            self.greeting_prefix.setText("Willkommen,")
            self.greeting_name.setText(username)
            self.greeting_name.setVisible(True)
        else:
            self.greeting_prefix.setText("Willkommen!")
            self.greeting_name.setText("")
            self.greeting_name.setVisible(False)
        self.greeting_row.setVisible(True)
        self.subtitle.setText("Schoen, dass du da bist.")
        if username:
            self._gradient_phase = 0.0
            self._gradient_timer.start(80)
        else:
            self._gradient_timer.stop()

    def __tick_loading(self):
        dots = "." * (self._dot_index % 4)
        self.subtitle.setText(f"Initialisiere Anwendung{dots}")
        self._dot_index += 1

    def __tick_gradient(self):
        if not self.greeting_name.isVisible():
            self._gradient_timer.stop()
            return
        self._gradient_phase += 0.22
        self.greeting_name.set_phase(self._gradient_phase)
