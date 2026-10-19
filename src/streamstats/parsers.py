from datetime import datetime
from typing import Any

from streamstats.errors import InvalidEventError, InvalidTimestampError


def make_event(
    raw: dict[str, Any], line_number: int, file_number: int
) -> dict[str, Any]:
    """Форматирует событие"""
    if not isinstance(raw, dict):
        raise InvalidEventError(
            f"Событие должно быть объектом, строка {line_number} файла {file_number}")
    timestamp_raw = raw.get("timestamp")
    level_raw = raw.get("level")
    source_raw = raw.get("source")
    message_raw = raw.get("message")

    if not isinstance(timestamp_raw, str) or not timestamp_raw:
        raise InvalidTimestampError(
            f"Поле 'timestamp': некорректное значение '{timestamp_raw}', строка {line_number}, файл {file_number}"
        )
    if level_raw not in ["CRITICAL", 
                         "DEBUG", 
                         "ERROR", 
                         "INFO", 
                         "WARNING"]:
        raise InvalidEventError(
            f"Поле 'level': некорректное значение '{level_raw}', строка {line_number} в файле {file_number}"
        )
    else:
        level = level_raw

    if not isinstance(source_raw, str) or not source_raw:
        raise InvalidEventError(
            f"Поле 'source': некорректное значение '{source_raw}', строка {line_number} в файле {file_number}"
        )
    else:
        source = source_raw

    if not isinstance(message_raw, str):
        raise InvalidEventError(
            f"Некорректное сообщение {message_raw}, строка {line_number} в файле {file_number}")
    else:
        message = message_raw

    try:
        timestamp = datetime.fromisoformat(timestamp_raw)
    except ValueError as e:
        raise InvalidTimestampError(
            f"Неверный формат записи времени  {timestamp_raw}, строка {line_number} в файле {file_number}"
        ) from e

    return {
        "timestamp": timestamp,
        "level": level,
        "source": source,
        "message": message,
    }


