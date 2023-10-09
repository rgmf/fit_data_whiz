from datetime import datetime, timedelta

from fit_data_whiz.whiz import FitDataWhiz
from fit_data_whiz.fit.results import FitSleep, FitSleepLevel


def sleep(path_file: str) -> None:
    whiz = FitDataWhiz(path_file)
    sleep: FitSleep = whiz.parse()

    assert isinstance(sleep, FitSleep)
    assert len(sleep.dates) == 2
    assert sleep.dates[1] - sleep.dates[0] == timedelta(days=1)
    assert isinstance(sleep.combined_awake_score, int)
    assert isinstance(sleep.awake_time_score, int)
    assert isinstance(sleep.awakenings_count_score, int)
    assert isinstance(sleep.deep_sleep_score, int)
    assert isinstance(sleep.sleep_duration_score, int)
    assert isinstance(sleep.light_sleep_score, int)
    assert isinstance(sleep.overall_sleep_score, int)
    assert isinstance(sleep.sleep_quality_score, int)
    assert isinstance(sleep.sleep_recovery_score, int)
    assert isinstance(sleep.rem_sleep_score, int)
    assert isinstance(sleep.sleep_restlessness_score, int)
    assert isinstance(sleep.awakenings_count, int)
    assert isinstance(sleep.interruptions_score, int)
    assert isinstance(sleep.average_stress_during_sleep, float)
    assert len(sleep.levels) > 0
    for level in sleep.levels:
        assert isinstance(level, FitSleepLevel)
        assert isinstance(level.datetime_utc, datetime)
        assert isinstance(level.datetime_local, datetime)
        assert isinstance(level.level, str)


def test_sleep():
    sleep("tests/files/sleep1.fit")
    sleep("tests/files/sleep2.fit")
