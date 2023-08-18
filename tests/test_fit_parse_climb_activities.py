from typing import List
from datetime import datetime

from ..parse import FitActivityParser
from ..definitions import (
    ROCK_CLIMBING_SPORT,
    BOULDERING_SUB_SPORT
)
from ..stats import FitActivity, FitClimbActivity, FitClimb
from ..definitions import ClimbResult


def assert_parse_without_errors(path_file: str) -> tuple:
    fit_parse = FitActivityParser()
    fit_parse.parse(path_file)

    messages = fit_parse.get_messages()
    activity = fit_parse.get_activity()
    errors = fit_parse.get_errors()

    assert not fit_parse.has_errors()
    assert len(errors) == 0

    return messages, activity, errors


def assert_messages(messages: List[dict], expected_sport: str, expected_sub_sport: str) -> None:
    assert "FILE_ID" in messages
    assert messages["FILE_ID"] is not None
    assert len(messages["FILE_ID"]) == 1

    assert "SESSION" in messages
    assert messages["SESSION"] is not None
    assert len(messages["SESSION"]) == 1
    assert messages["SESSION"][0].sport == expected_sport
    assert messages["SESSION"][0].sub_sport == expected_sub_sport

    assert "SPLIT" in messages
    assert messages["SPLIT"] is not None
    assert len(messages["SPLIT"]) > 0


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
    messages, activity, errors = assert_parse_without_errors("tests/files/bouldering.fit")
    assert not errors
    assert_messages(messages, ROCK_CLIMBING_SPORT, BOULDERING_SUB_SPORT)
    assert_is_climb_activity_with_minimal_required_stats(activity)
    assert_climbs_data(activity.climbs)


def test_fit_parse_bouldering_with_18_climbs():
    messages, activity, errors = assert_parse_without_errors(
        "tests/files/bouldering_18_climbs.fit"
    )
    assert not errors
    assert_messages(messages, ROCK_CLIMBING_SPORT, BOULDERING_SUB_SPORT)
    assert_is_climb_activity_with_minimal_required_stats(activity)
    assert_climbs_data(activity.climbs)

    assert len([
        c for c in activity.climbs if c.result in [ClimbResult.COMPLETED, ClimbResult.ATTEMPTED]
    ]) == 18
