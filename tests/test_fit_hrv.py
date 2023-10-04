from datetime import datetime

from ..parse import FitParser
from ..parsers.results.stats import FitHrv


def hrv(path_file: str) -> None:
    fit_parse: FitParser = FitParser(path_file)
    hrv: FitHrv = fit_parse.parse()

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
        assert isinstance(v.datetime_utc, datetime)
        assert isinstance(v.value, float)


def test_hrv():
    hrv("tests/files/hrv1.fit")
    hrv("tests/files/hrv2.fit")
