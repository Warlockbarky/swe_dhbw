from datetime import datetime

from controller.file_utils import parse_iso_datetime


def test_parse_iso_datetime_invalid_is_stable():
    assert parse_iso_datetime("not-a-date") == datetime.min
