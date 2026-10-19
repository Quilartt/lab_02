import json
from typing import Any

from streamstats.errors import StreamStatsError


def create_report(stats: dict[str, Any]) -> dict[str, Any]:
    """Собирает dict для JSON-отчёта,"""
    report_source = {key: value["total"] for key, value in stats["by_source"].items()}
    errors = [(key, value["error"]) for key, value in stats["by_source"].items() if value["error"] > 0]
    sorted_errors = sorted(errors, key=lambda x: (-x[1], x[0]))
    top5 = dict(sorted_errors[:5])    
    return {
        "total_events": stats["total_events"],
        "by_level": stats["by_level"],
        "by_source": report_source,
        "top_error_sources": top5,
        "first_timestamp": stats["first_timestamp"].isoformat() if stats["first_timestamp"] is not None else None,
        "last_timestamp": stats["last_timestamp"].isoformat() if stats["last_timestamp"] is not None else None,
        "skipped_invalid": stats["skipped_invalid"]
        }


def write_report(report: dict[str, Any], output: str | None) -> None:
    """Выводит отчёт"""
    text = json.dumps(report, ensure_ascii=False, indent=2)
    
    if output is None:
        print(text)
    else:
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(text)
                f.write("\n")
        except OSError as e:
            raise StreamStatsError(f"Не удалось записать отчёт в {output}: {e}") from e