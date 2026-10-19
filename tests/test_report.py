import json
from datetime import datetime

from streamstats.report import create_report, write_report


def make_stats():
    return {
        "total_events": 3,
        "by_level": {"INFO": 1, "ERROR": 2, "DEBUG": 0, "WARNING": 0, "CRITICAL": 0},
        "by_source": {
            "db": {"total": 2, "error": 2},
            "app": {"total": 1, "error": 0},
        },
        "first_timestamp": datetime(2026,1,1,10,0),
        "last_timestamp": datetime(2026,1,1,10,5),
        "skipped_invalid": 1,
    }

def test_report_by_source():
    r = create_report(make_stats())
    assert r["by_source"] == {"db": 2, "app": 1}

def test_report_top_error_sources():
    r = create_report(make_stats())
    assert r["top_error_sources"] == {"db": 2}

def test_report_iso_timestamps():
    r = create_report(make_stats())
    assert r["first_timestamp"] == "2026-01-01T10:00:00"
    assert r["last_timestamp"] == "2026-01-01T10:05:00"

def test_report_empty_timestamps_none():
    s = make_stats()
    s["first_timestamp"] = None
    s["last_timestamp"] = None
    r = create_report(s)
    assert r["first_timestamp"] is None
    assert r["last_timestamp"] is None

def test_report_sorted():
    s = make_stats()
    s["by_source"] = {
        "db": {"total": 1, "error": 3},
        "web": {"total": 1, "error": 3},
    }
    r = create_report(s)
    keys = list(r["top_error_sources"].keys())
    assert keys == ["db", "web"]

def test_write_report_to_console(capsys):
    r = {"x": 1}
    write_report(r, None)
    captured = capsys.readouterr()
    assert '"x": 1' in captured.out

def test_write_report_to_file(tmp_path):
    r = {"x": 1}
    p = tmp_path / "report.json"
    write_report(r, str(p))
    assert p.exists()
    assert json.loads(p.read_text(encoding="utf-8")) == {"x": 1}