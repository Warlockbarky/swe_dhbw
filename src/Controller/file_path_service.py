from pathlib import Path


def resolve_download_dir(settings, view) -> Path | None:
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
