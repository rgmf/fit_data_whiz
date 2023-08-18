import pytest
from typing import List
from datetime import datetime

from ..parse import FitActivityParser
from ..definitions import (
    RUNNING_SPORT,
    WALKING_SPORT,
    HIKING_SPORT,
    CYCLING_SPORT,
    GENERIC_SUB_SPORT,
    TRAIL_SUB_SPORT,
    ROAD_SUB_SPORT,
    MOUNTAIN_SUB_SPORT
)
from ..stats import FitActivity, FitDistanceActivity


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

    assert "RECORD" in messages
    assert messages["RECORD"] is not None
    assert len(messages["RECORD"]) > 0


def assert_is_distance_activity_with_required_stats(activity: FitActivity) -> None:
    """It asserts is a distance activity and it has required stats.

    Required stats are:
    - name
    - sport
    - sub sport
    - time data
    - total distance
    - speed
    """
    assert isinstance(activity, FitDistanceActivity)

    assert activity.name is not None
    assert activity.sport is not None
    assert activity.sub_sport is not None

    assert activity.time is not None
    assert isinstance(activity.time.timestamp, datetime)
    assert isinstance(activity.time.start_time, datetime)
    assert isinstance(activity.time.elapsed, float)
    assert isinstance(activity.time.timer, float)

    assert activity.total_distance is not None
    assert activity.speed is not None
    assert isinstance(activity.speed.max, float)
    assert isinstance(activity.speed.avg, float)


def test_fit_parse_walking():
    messages, activity, errors = assert_parse_without_errors("tests/files/walking.fit")
    assert not errors
    assert_messages(messages, WALKING_SPORT, GENERIC_SUB_SPORT)
    assert_is_distance_activity_with_required_stats(activity)


def test_fit_parse_hiking():
    messages, activity, errors = assert_parse_without_errors("tests/files/hiking.fit")
    assert not errors
    assert_messages(messages, HIKING_SPORT, GENERIC_SUB_SPORT)
    assert_is_distance_activity_with_required_stats(activity)


def test_fit_parse_running():
    messages, activity, errors = assert_parse_without_errors("tests/files/running.fit")
    assert not errors
    assert_messages(messages, RUNNING_SPORT, GENERIC_SUB_SPORT)
    assert_is_distance_activity_with_required_stats(activity)


def test_fit_parse_trail_running():
    messages, activity, errors = assert_parse_without_errors("tests/files/trail_running.fit")
    assert not errors
    assert_messages(messages, RUNNING_SPORT, TRAIL_SUB_SPORT)
    assert_is_distance_activity_with_required_stats(activity)


def test_fit_parse_road_cycling():
    messages, activity, errors = assert_parse_without_errors("tests/files/road_cycling.fit")
    assert not errors
    assert_messages(messages, CYCLING_SPORT, ROAD_SUB_SPORT)
    assert_is_distance_activity_with_required_stats(activity)


@pytest.mark.skip(reason="The activity is not a mountain biking one")
def test_fit_parse_mountain_cycling():
    messages, activity, errors = assert_parse_without_errors("tests/files/mountain_biking.fit")
    assert not errors
    assert_messages(messages, CYCLING_SPORT, MOUNTAIN_SUB_SPORT)
    assert_is_distance_activity_with_required_stats(activity)
