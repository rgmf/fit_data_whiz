from datetime import datetime, timedelta, date

from ..parse import FitParser
from ..parsers.results.result import FitResult
from ..parsers.results.stats import FitMonitor, FitMonitoringInfo


def assert_monitoring_data(path_file: str) -> None:
    fit_parse: FitParser = FitParser(path_file)
    monitor: FitResult = fit_parse.parse()

    assert isinstance(monitor, FitMonitor)
    assert isinstance(monitor.monitoring_info, FitMonitoringInfo)

    local_datetime: datetime = monitor.monitoring_info.datetime_utc + timedelta(seconds=7200)
    local_date: date = date(
        year=local_datetime.year,
        month=local_datetime.month,
        day=local_datetime.day
    )

    # Monitoring Info
    assert monitor.monitoring_info.monitoring_day == local_date
    assert "walking" in monitor.monitoring_info.activities
    assert "running" in monitor.monitoring_info.activities
    assert type(monitor.monitoring_info.resting_metabolic_rate) is int
    assert monitor.monitoring_info.resting_metabolic_rate > 0

    # Monitorings
    assert len(monitor.monitorings) > 0

    # Calories
    assert monitor.metabolic_calories is not None
    assert monitor.active_calories is not None
    assert monitor.total_calories is not None

    # All data: day date, steps, heart rate, respiration rate and stress levels.
    assert monitor.day_date is not None
    assert monitor.fit_steps is not None
    assert len(monitor.fit_heart_rates) > 0
    assert monitor.resting_heart_rate is not None
    assert len(monitor.respiration_rates) > 0
    assert len(monitor.stress_levels) > 0
    assert isinstance(monitor.activity_intensities, list)


def assert_activity_intensities(path_file: str, moderate_min: int, vigorous_min: int) -> None:
    fit_parse: FitParser = FitParser(path_file)
    monitor: FitMonitor = fit_parse.parse()

    assert sum([m.moderate for m in monitor.activity_intensities]) == moderate_min
    assert sum([m.vigorous for m in monitor.activity_intensities]) == vigorous_min


def test_monitoring_with_all():
    assert_monitoring_data("tests/files/monitor1_with_all.fit")
    assert_monitoring_data("tests/files/monitor2_with_all.fit")
    # assert_monitoring_data("tests/files/monitor2/M9R00000.FIT")
    # assert_monitoring_data("tests/files/monitor2/M9RB3400.FIT")
    # assert_monitoring_data("tests/files/monitor2/M9S00000.FIT")
    # assert_monitoring_data("tests/files/monitor2/M9SC0715.FIT")
    # assert_monitoring_data("tests/files/monitor2/M9T00000.FIT")
    # assert_monitoring_data("tests/files/monitor2/M9U00000.FIT")
    # assert_monitoring_data("tests/files/monitor2/MA100000.FIT")
    # assert_monitoring_data("tests/files/monitor2/MA1A1222.FIT")
    # assert_monitoring_data("tests/files/monitor2/MA1B5812.FIT")
    # assert_monitoring_data("tests/files/monitor2/MA200000.FIT")
    # assert_monitoring_data("tests/files/monitor2/MA300000.FIT")
    # assert_monitoring_data("tests/files/monitor2/MA3C0247.FIT")


def test_activity_intensities():
    assert_activity_intensities(
        "tests/files/monitor1_with_all.fit",
        moderate_min=0,
        vigorous_min=0
    )
    assert_activity_intensities(
        "tests/files/monitor_with_intensities.fit",
        moderate_min=26,
        vigorous_min=2
    )
