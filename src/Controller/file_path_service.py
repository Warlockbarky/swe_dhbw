"""Utilities for resolving a writable download directory."""

from pathlib import Path


def resolve_download_dir(settings, view) -> Path | None:
    """Pick a writable download directory or report an error via the view.

    Args:
        settings: QSettings-like object for persisted preferences.
        view: View instance used to surface errors.

    Returns:
        Path | None: Resolved directory path or None when unavailable.
    """
    configured = settings.value("files/default_dir", "", type=str).strip()
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.append(Path.home() / "Downloads")

    for candidate in candidates:
        try:
            candidate = candidate.expanduser().resolve()
        except Exception:
            continue
        if candidate.exists() and candidate.is_dir():
            return candidate

    view.show_error("Kein gueltiger Download-Ordner gefunden.")
    return None
