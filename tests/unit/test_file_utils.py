from datetime import datetime

from controller import file_utils


def test_normalize_file_records_handles_non_list():
    assert file_utils.normalize_file_records(None) == []
    assert file_utils.normalize_file_records({"id": 1}) == []


def test_normalize_file_records_extracts_fields():
    payload = [
        {"id": 1, "filename": "report.pdf", "size": 10, "created_at": "2024-01-01"},
        {"id": 2, "name": "notes.txt", "file_size": 2048, "updated_at": "2024-01-02"},
        "raw",
    ]
    records = file_utils.normalize_file_records(payload)
    assert records[0]["id"] == 1
    assert records[0]["name"] == "report.pdf"
    assert records[0]["size"] == 10
    assert records[1]["name"] == "notes.txt"
    assert records[1]["size"] == 2048
    assert records[2]["name"] == "raw"


def test_parse_iso_datetime():
    now = datetime(2024, 1, 1, 12, 0, 0)
    assert file_utils.parse_iso_datetime(now) == now
    assert file_utils.parse_iso_datetime("2024-01-01T12:00:00Z").year == 2024
    assert file_utils.parse_iso_datetime("bad") == datetime.min


def test_file_extension():
    assert file_utils.file_extension("Report.PDF") == "pdf"
    assert file_utils.file_extension("archive") == ""
    assert file_utils.file_extension(None) == ""


def test_format_size():
    assert file_utils.format_size(None) == ""
    assert file_utils.format_size("bad") == ""
    assert file_utils.format_size(0) == "0 B"
    assert file_utils.format_size(1024) == "1.0 KB"
    assert file_utils.format_size(1024 * 1024) == "1.0 MB"


def test_format_date():
    now = datetime(2024, 1, 2, 3, 4)
    assert file_utils.format_date(now) == "2024-01-02 03:04"
    assert file_utils.format_date("2024-01-02T03:04:00Z") == "2024-01-02 03:04"
    assert file_utils.format_date("bad") == "bad"
    assert file_utils.format_date("") == ""
