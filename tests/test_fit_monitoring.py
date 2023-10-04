from datetime import datetime, timedelta, date

from ..parse import FitParser
from ..parsers.results.result import FitResult
from ..parsers.results.stats import FitMonitor, FitMonitoringInfo


def monitoring(path_file: str) -> None:
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


def test_monitoring():
    monitoring("tests/files/monitor1_with_all.fit")
    monitoring("tests/files/monitor2_with_all.fit")
    # monitoring("tests/files/monitor2/M9R00000.FIT")
    # monitoring("tests/files/monitor2/M9RB3400.FIT")
    # monitoring("tests/files/monitor2/M9S00000.FIT")
    # monitoring("tests/files/monitor2/M9SC0715.FIT")
    # monitoring("tests/files/monitor2/M9T00000.FIT")
    # monitoring("tests/files/monitor2/M9U00000.FIT")
    # monitoring("tests/files/monitor2/MA100000.FIT")
    # monitoring("tests/files/monitor2/MA1A1222.FIT")
    # monitoring("tests/files/monitor2/MA1B5812.FIT")
    # monitoring("tests/files/monitor2/MA200000.FIT")
    # monitoring("tests/files/monitor2/MA300000.FIT")
    # monitoring("tests/files/monitor2/MA3C0247.FIT")
