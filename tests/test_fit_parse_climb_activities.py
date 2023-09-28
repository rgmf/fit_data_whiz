from datetime import datetime

from ..parse import FitParser
from ..definitions import (
    ROCK_CLIMBING_SPORT,
    BOULDERING_SUB_SPORT
)
from ..parsers.results.stats import FitActivity, FitClimbActivity, FitClimb
from ..parsers.results.result import FitResult, FitError
from ..definitions import ClimbResult


def assert_parse_without_errors(path_file: str) -> FitResult:
    fit_parse = FitParser(path_file)
    activity: FitResult = fit_parse.parse()
    assert not isinstance(activity, FitError)
    assert isinstance(activity, FitActivity)
    return activity


def assert_sport(activity: FitActivity, expected_sport: str, expected_sub_sport: str) -> None:
    assert activity.sport == expected_sport
    assert activity.sub_sport == expected_sub_sport


def assert_is_climb_activity_with_minimal_required_stats(activity: FitActivity) -> None:
    """It asserts is a climb activity and it has required stats.

    Required stats are:
    - name
    - sport
    - sub sport
    - time data
    """
    assert isinstance(activity, FitClimbActivity)

    assert activity.name is not None
    assert activity.sport is not None
    assert activity.sub_sport is not None

    assert activity.time is not None
    assert isinstance(activity.time.timestamp, datetime)
    assert isinstance(activity.time.start_time, datetime)
    assert isinstance(activity.time.elapsed, float)
    assert isinstance(activity.time.timer, float)


def assert_climbs_data(climbs: list[FitClimb]) -> None:
    assert climbs is not None
    assert len(climbs) > 0


def test_fit_parse_bouldering():
    activity = assert_parse_without_errors("tests/files/bouldering.fit")
    assert_sport(activity, ROCK_CLIMBING_SPORT, BOULDERING_SUB_SPORT)
    assert_is_climb_activity_with_minimal_required_stats(activity)
    assert_climbs_data(activity.climbs)


def test_fit_parse_bouldering_with_18_climbs():
    activity = assert_parse_without_errors("tests/files/bouldering_18_climbs.fit")
    assert_sport(activity, ROCK_CLIMBING_SPORT, BOULDERING_SUB_SPORT)
    assert_is_climb_activity_with_minimal_required_stats(activity)
    assert_climbs_data(activity.climbs)

    assert len([
        c for c in activity.climbs if c.result in [ClimbResult.COMPLETED, ClimbResult.ATTEMPTED]
    ]) == 18
