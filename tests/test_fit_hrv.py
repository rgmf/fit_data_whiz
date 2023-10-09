from datetime import datetime

from fit_data_whiz.whiz import FitDataWhiz
from fit_data_whiz.fit.results import FitHrv


def assert_is_an_hrv(path_file: str) -> None:
    whiz = FitDataWhiz(path_file)
    hrv = whiz.parse()

    assert isinstance(hrv, FitHrv)
    assert isinstance(hrv.datetime_utc, datetime)
    assert isinstance(hrv.weekly_average, float)
    assert isinstance(hrv.last_night_average, float)
    assert isinstance(hrv.last_night_5_min_high, float)
    assert isinstance(hrv.baseline_low_upper, float)
    assert isinstance(hrv.baseline_balanced_lower, float)
    assert isinstance(hrv.baseline_balanced_upper, float)
    assert isinstance(hrv.status, str)
    assert len(hrv.values) > 0
    for v in hrv.values:
        assert isinstance(v.timestamp, datetime)
        assert v.value is None or isinstance(v.value, int)


def test_hrv():
    assert_is_an_hrv("tests/files/hrv1.fit")
    assert_is_an_hrv("tests/files/hrv2.fit")
