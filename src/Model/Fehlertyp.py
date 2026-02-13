"""Custom exception hierarchy for application-specific errors."""


class app_error(Exception):
    """Basisklasse für alle Anwendungsfehler."""


class pfad_fehler(app_error):
    """Fehler im Zusammenhang mit Pfaden."""


class login_fehler(app_error):
    """Fehler beim Login oder bei der Authentifizierung."""


class zeit_fehler(app_error):
    """Fehler mit Zeitbezug (Timeouts, etc.)."""


class schreibrechte_fehler(app_error):
    """Fehler bei fehlenden Schreibrechten."""


class speicherplatz_fehler(app_error):
    """Fehler bei zu wenig Speicherplatz."""


kein_pfad = pfad_fehler
