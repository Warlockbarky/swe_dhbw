"""Helpers for normalizing and presenting file metadata."""

from datetime import datetime
from pathlib import Path


def normalize_file_records(data):
    """Normalize API responses into a consistent file record structure.

    Args:
        data: Raw API payload.

    Returns:
        list[dict]: Normalized file record dictionaries.
    """
    if not isinstance(data, list):
        return []

    records = []
    for item in data:
        if isinstance(item, dict):
            file_id = item.get("id")
            name = (
                item.get("filename")
                or item.get("name")
                or item.get("original_filename")
                or item.get("path")
            )
            records.append(
                {
                    "id": file_id,
                    "name": name,
                    "size": item.get("size")
                    or item.get("file_size")
                    or item.get("filesize"),
                    "created_at": item.get("created_at")
                    or item.get("created")
                    or item.get("uploaded_at"),
                    "updated_at": item.get("updated_at")
                    or item.get("modified_at")
                    or item.get("updated"),
                }
            )
        else:
            records.append({"id": None, "name": str(item)})

    return records


def parse_iso_datetime(value) -> datetime:
    """Parse various ISO-like timestamp formats with safe fallback.

    Args:
        value: Timestamp value or ISO-like string.

    Returns:
        datetime: Parsed timestamp or datetime.min on failure.
    """
    if not value:
        return datetime.min
    if isinstance(value, datetime):
        return value
    try:
        text = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(text)
    except (ValueError, TypeError):
        # Keep sorting deterministic even for malformed timestamps.
        return datetime.min


def file_extension(name: str) -> str:
    suffix = Path(name or "").suffix.lower()
    return suffix[1:] if suffix.startswith(".") else suffix


def format_size(value) -> str:
    """Return a human-readable file size string.

    Args:
        value: File size in bytes.

    Returns:
        str: Human-friendly size label or empty string when unknown.
    """
    try:
        size = int(value)
    except (TypeError, ValueError):
        return ""
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size_float = float(size)
    while size_float >= 1024 and unit_index < len(units) - 1:
        size_float /= 1024.0
        unit_index += 1
    if unit_index == 0:
        return f"{int(size_float)} {units[unit_index]}"
    return f"{size_float:.1f} {units[unit_index]}"


def format_date(value) -> str:
    """Return a compact date string or empty string when unknown.

    Args:
        value: Datetime or ISO-like string.

    Returns:
        str: Formatted date label or empty string when unavailable.
    """
    if not value:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    try:
        text = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        return parsed.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return str(value)
