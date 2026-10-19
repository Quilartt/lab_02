from datetime import datetime

import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.parsers import make_event


def valid_raw():
    return {
        "timestamp": "2026-10-13T10:00:00",
        "level": "INFO",
        "source": "app",
        "message": "started",
    }


def test_valid_event():
    event = make_event(valid_raw(), line_number=2, file_number=1)
    assert event["level"] == "INFO"
    assert event["source"] == "app"
    assert event["message"] == "started"
    assert event["timestamp"] == datetime(2026, 10, 13, 10, 0, 0)


def test_missing_timestamp():
    raw = valid_raw()
    raw.pop("timestamp")
    with pytest.raises(InvalidTimestampError):
        make_event(raw, line_number=2, file_number=1)


def test_invalid_timestamp_format():
    raw = valid_raw()
    raw["timestamp"] = "not-a-date"
    with pytest.raises(InvalidTimestampError):
        make_event(raw, line_number=2, file_number=1)


def test_invalid_timestamp_cause():
    #Проверяем, что исходная ValueError сохранена через 'from e'
    raw = valid_raw()
    raw["timestamp"] = "not-a-date"
    with pytest.raises(InvalidTimestampError) as exc_info:
        make_event(raw, line_number=2, file_number=1)
    assert exc_info.value.__cause__ is not None


def test_invalid_level():
    raw = valid_raw()
    raw["level"] = "NOTICE"
    with pytest.raises(InvalidEventError):
        make_event(raw, line_number=2, file_number=1)


def test_empty_source_raises():
    raw = valid_raw()
    raw["source"] = ""
    with pytest.raises(InvalidEventError):
        make_event(raw, line_number=2, file_number=1)


def test_non_dict():
    with pytest.raises(InvalidEventError):
        make_event(["not", "a", "dict"], line_number=2, file_number=1)


def test_unicode_preserved():
    raw = valid_raw()
    raw["message"] = "Ошибка подключения к БД"
    raw["source"] = "база"
    event = make_event(raw, line_number=2, file_number=1)
    assert event["message"] == "Ошибка подключения к БД"
    assert event["source"] == "база"