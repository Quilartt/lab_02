from datetime import datetime

from streamstats.analysis import update_stat, zero_stats


def test_zero_stats():
    s = zero_stats()
    assert s["total_events"] == 0
    assert s["by_source"] == {}
    assert s["by_level"]["INFO"] == 0
    assert s["by_level"]["CRITICAL"] == 0
    assert s["first_timestamp"] is None
    assert s["last_timestamp"] is None
    assert s["skipped_invalid"] == 0


def test_update_stat_total():
    s = zero_stats()
    update_stat({"timestamp": datetime(2026,1,1,10,0), "level": "INFO",
                 "source": "app", "message": "x"}, s)
    assert s["total_events"] == 1
    assert s["by_level"]["INFO"] == 1
    assert s["by_source"]["app"]["total"] == 1
    assert s["by_source"]["app"]["error"] == 0


def test_update_stat_tracks_error():
    s = zero_stats()
    update_stat({"timestamp": datetime(2026,1,1), "level": "ERROR",
                 "source": "db", "message": "fail"}, s)
    assert s["by_source"]["db"]["error"] == 1


def test_update_stat_critical_error():
    s = zero_stats()
    update_stat({"timestamp": datetime(2026,1,1), "level": "CRITICAL",
                 "source": "db", "message": ""}, s)
    assert s["by_source"]["db"]["error"] == 1


def test_update_stat_first_last():
    s = zero_stats()
    update_stat({"timestamp": datetime(2026,1,1,10,5), "level": "INFO",
                 "source": "a", "message": ""}, s)
    update_stat({"timestamp": datetime(2026,1,1,10,0), "level": "INFO",
                 "source": "a", "message": ""}, s)
    update_stat({"timestamp": datetime(2026,1,1,10,9), "level": "INFO",
                 "source": "a", "message": ""}, s)
    assert s["first_timestamp"] == datetime(2026,1,1,10,0)
    assert s["last_timestamp"] == datetime(2026,1,1,10,9)

