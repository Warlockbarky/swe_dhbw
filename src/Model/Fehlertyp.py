class app_error(Exception):
    """Basisklasse für alle Anwendungsfehler"""
    pass


class pfad_fehler(app_error):
    pass


class login_fehler(app_error):
    pass


class zeit_fehler(app_error):
    pass


class schreibrechte_fehler(app_error):
    pass


class speicherplatz_fehler(app_error):
    pass


KEIN_PFAD = pfad_fehler
