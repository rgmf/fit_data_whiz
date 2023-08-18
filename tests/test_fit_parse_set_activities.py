from typing import List
from datetime import datetime

from ..parse import FitActivityParser
from ..definitions import (
    TRAINING_SPORT,
    STRENGTH_TRAINING_SUB_SPORT,
    ExcerciseCategories
)
from ..stats import FitActivity, FitSetActivity, FitSet


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

    assert "SET" in messages
    assert messages["SET"] is not None
    assert len(messages["SET"]) > 0


def assert_is_set_activity_with_minimal_required_stats(activity: FitActivity) -> None:
    """It asserts is a set activity and it has required stats.

    Required stats are:
    - name
    - sport
    - sub sport
    - time data
    """
    assert isinstance(activity, FitSetActivity)

    assert activity.name is not None
    assert activity.sport is not None
    assert activity.sub_sport is not None

    assert activity.time is not None
    assert isinstance(activity.time.timestamp, datetime)
    assert isinstance(activity.time.start_time, datetime)
    assert isinstance(activity.time.elapsed, float)
    assert isinstance(activity.time.timer, float)


def assert_required_set_data(s: FitSet) -> None:
    assert s.order is not None and isinstance(s.order, int)
    assert s.excercise is not None and isinstance(s.excercise, str)
    assert s.time is not None
    assert isinstance(s.time.timestamp, datetime)
    assert isinstance(s.time.start_time, datetime)
    assert isinstance(s.time.elapsed, float)
    assert isinstance(s.time.timer, float)


def assert_sets_data(sets: list[FitSet]) -> None:
    assert sets is not None
    assert len(sets) > 0

    for set_ in sets:
        assert_required_set_data(set_)


def test_fit_parse_training():
    messages, activity, errors = assert_parse_without_errors("tests/files/training_strength.fit")
    assert not errors
    assert_messages(messages, TRAINING_SPORT, STRENGTH_TRAINING_SUB_SPORT)
    assert_is_set_activity_with_minimal_required_stats(activity)
    assert_sets_data(activity.sets)


def test_fit_parse_training_with_20_sets():
    messages, activity, errors = assert_parse_without_errors(
        "tests/files/training_4pull_up_3push_up_3curl_3bench_press_1deadlift_1sit_up_5unknown.fit"
    )
    assert not errors
    assert_messages(messages, TRAINING_SPORT, STRENGTH_TRAINING_SUB_SPORT)
    assert_is_set_activity_with_minimal_required_stats(activity)
    assert_sets_data(activity.sets)

    rest: int = 20
    work: int = 20
    assert len([c for c in activity.sets]) == rest + work
    assert len([c for c in activity.sets if c.excercise == ExcerciseCategories.REST]) == 20
    assert len([c for c in activity.sets if c.excercise != ExcerciseCategories.REST]) == 20
