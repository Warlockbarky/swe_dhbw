class AppError(Exception):
    """Basisklasse für alle Anwendungsfehler"""
    pass


class PfadFehler(AppError):
    pass


class LoginFehler(AppError):
    pass


class ZeitFehler(AppError):
    pass
