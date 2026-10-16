from datetime import datetime


from src.streamstats.errors import InvalidTimestampError, InvalidEventError


def make_event(raw: dict[str, str], line_number: int):
    timestamp_raw = raw.get("timestamp") 
    level_raw = raw.get("level") 
    source_raw = raw.get("source")
    message_raw = raw.get("message")
 
    if not isinstance(timestamp_raw, str) or not timestamp_raw:
        raise InvalidTimestampError("Некорректная дата время")
    
    if level_raw not in ["CRITICAL", 
                 "DEBUG",
                 "ERROR", 
                 "INFO", 
                 "WARNING"]:
        raise InvalidEventError(f"Неверное состояние события, строка {line_number}")
    else:
        level = level_raw

    if not isinstance(source_raw, str) or not source_raw:
        raise InvalidEventError(f"Некорректный источник данных, строка {line_number}")
    else:
        source = source_raw

    if not isinstance(message_raw, str):
        raise InvalidEventError(f"Некорректное сообщение, строка {line_number}")
    else:
        message = message_raw
         

    try:
        timestamp = datetime.fromisoformat(timestamp_raw)
    except ValueError as e:
        raise InvalidTimestampError(f"Неверный формат записи времени  {timestamp_raw}, строка {line_number}")
        

    return {'timestamp': timestamp,
            'level': level,
            'source': source,
            'message': message} 

 