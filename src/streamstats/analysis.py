from typing import Any


def zero_stats() -> dict[str, Any]:
    """Инициализация статистики"""
    stats = {
    "total_events": 0,
    "by_level": {"CRITICAL": 0, 
                 "DEBUG": 0,
                 "ERROR": 0, 
                 "INFO": 0, 
                 "WARNING": 0},
    "by_source": {},
    "first_timestamp": None,
    "last_timestamp": None,
    "skipped_invalid": 0
    }
    return stats


def update_stat(event: dict[str, Any], stats: dict[str, Any]) -> None:
    """Обновление статистики"""
    stats["total_events"] += 1

    level = event["level"]
    stats["by_level"][level] += 1

    source = event["source"]
    if source not in stats["by_source"]:
        stats["by_source"][source] = {"total": 0, "error": 0}
    stats["by_source"][source]["total"] += 1
    if level in ["ERROR", "CRITICAL"]:
        stats["by_source"][source]["error"] += 1

    if (stats["first_timestamp"] is None
        or event["timestamp"] < stats["first_timestamp"]):
        stats["first_timestamp"] = event["timestamp"]

    if (stats["last_timestamp"] is None 
        or event["timestamp"] > stats["last_timestamp"]):
        stats["last_timestamp"] = event["timestamp"]
