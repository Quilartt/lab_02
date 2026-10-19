import json
import os
import subprocess
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data"


def run_cli(*args):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, "-m", "streamstats", *args],
        capture_output=True, text=True, encoding="utf-8", env=env, check=False,
    )


def test_cli_empty_file():
    result = run_cli("analyze", str(DATA / "empty.csv"), "--format", "csv")
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["total_events"] == 0
    assert report["by_source"] == {}


def test_cli_csv_valid():
    result = run_cli("analyze", str(DATA / "events_valid.csv"), "--format", "csv")
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["total_events"] == 12
    assert report["by_source"] == {"api": 3, "db": 4, "auth": 1, "web": 2, "worker": 2}
    assert report["by_level"]["ERROR"] == 3
    assert report["top_error_sources"] == {"db": 2, "api": 1, "auth": 1, "web": 1}
    assert report["first_timestamp"] == "2026-10-06T10:00:00+00:00"
    assert report["last_timestamp"] == "2026-10-06T10:10:00+00:00"


def test_cli_jsonl_valid():
    result = run_cli("analyze", str(DATA / "events_valid.jsonl"), "--format", "jsonl")
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["total_events"] == 10
    assert report["by_source"] == {"api": 3, "db": 3, "auth": 1, "web": 2, "worker": 1}


def test_cli_csv_jsonl_equivalent():
    csv_result = run_cli("analyze", str(DATA / "equivalent.csv"), "--format", "csv")
    jsonl_result = run_cli("analyze", str(DATA / "equivalent.jsonl"), "--format", "jsonl")
    csv_report = json.loads(csv_result.stdout)
    jsonl_report = json.loads(jsonl_result.stdout)
    assert csv_report["total_events"] == jsonl_report["total_events"]
    assert csv_report["by_source"] == jsonl_report["by_source"]
    assert csv_report["top_error_sources"] == jsonl_report["top_error_sources"]


def test_cli_invalid_csv_without_skip():
    result = run_cli("analyze", str(DATA / "events_invalid.csv"), "--format", "csv")
    assert result.returncode == 2


def test_cli_invalid_csv_with_skip():
    result = run_cli(
        "analyze", str(DATA / "events_invalid.csv"),
        "--format", "csv", "--skip-invalid",
    )
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["total_events"] == 5
    assert report["skipped_invalid"] == 5


def test_cli_invalid_jsonl_without_skip():
    result = run_cli("analyze", str(DATA / "events_invalid.jsonl"), "--format", "jsonl")
    assert result.returncode == 2


def test_cli_invalid_jsonl_with_skip():
    result = run_cli(
        "analyze", str(DATA / "events_invalid.jsonl"),
        "--format", "jsonl", "--skip-invalid",
    )
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["total_events"] == 5
    assert report["skipped_invalid"] == 5


def test_cli_multiple_files():
    result = run_cli(
        "analyze",
        str(DATA / "events_valid.csv"),
        str(DATA / "events_valid.jsonl"),
        "--format", "csv", "jsonl",
    )
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["total_events"] == 22  # 12 + 10


def test_cli_cyrillic():
    for name, fmt in [("events_valid.csv", "csv"), ("events_valid.jsonl", "jsonl")]:
        result = run_cli("analyze", str(DATA / name), "--format", fmt)
        assert result.returncode == 0
        report = json.loads(result.stdout)
        assert report["skipped_invalid"] == 0


def test_cli_output_to_file(tmp_path):
    out = tmp_path / "report.json"
    result = run_cli(
        "analyze", str(DATA / "events_valid.jsonl"),
        "--format", "jsonl", "--output", str(out),
    )
    assert result.returncode == 0
    assert out.exists()
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["total_events"] == 10