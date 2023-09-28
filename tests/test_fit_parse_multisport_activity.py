from datetime import datetime

from ..parse import FitParser
from ..parsers.results.result import FitResult, FitError
from ..parsers.results.stats import (
    FitMultisportActivity,
    FitDistanceActivity,
    FitTransitionActivity
)
from ..definitions import (
    RUNNING_SPORT,
    CYCLING_SPORT,
    TRANSITION_SPORT,
    GENERIC_SUB_SPORT,
    ROAD_SUB_SPORT
)
from .test_fit_parse_distance_activities import assert_is_distance_activity_with_required_stats


def assert_parse_without_errors(path_file: str) -> FitResult:
    fit_parse = FitParser(path_file)
    activity: FitResult = fit_parse.parse()
    assert not isinstance(activity, FitError)
    assert isinstance(activity, FitMultisportActivity)
    return activity


def assert_is_transition_activity_with_required_stats(activity: FitTransitionActivity) -> None:
    """It asserts is a transition activity and it has required stats.

    Required stats are:
    - name
    - sport
    - sub sport
    - time data
    """
    assert isinstance(activity, FitTransitionActivity)

    assert activity.name is not None
    assert activity.sport is not None
    assert activity.sub_sport is not None

    assert activity.time is not None
    assert isinstance(activity.time.timestamp, datetime)
    assert isinstance(activity.time.start_time, datetime)
    assert isinstance(activity.time.elapsed, float)
    assert isinstance(activity.time.timer, float)


def assert_duathlon(activity: FitMultisportActivity, sports: list[tuple]) -> None:
    assert isinstance(activity, FitMultisportActivity)
    assert len(activity.fit_activities) == 5
    assert isinstance(activity.fit_activities[0], FitDistanceActivity)
    assert isinstance(activity.fit_activities[1], FitTransitionActivity)
    assert isinstance(activity.fit_activities[2], FitDistanceActivity)
    assert isinstance(activity.fit_activities[3], FitTransitionActivity)
    assert isinstance(activity.fit_activities[4], FitDistanceActivity)

    for a, st in zip(activity.fit_activities, sports):
        assert a.sport == st[0]
        assert a.sub_sport == st[1]
        if isinstance(a, FitTransitionActivity):
            assert_is_transition_activity_with_required_stats(a)
        else:
            assert_is_distance_activity_with_required_stats(a)


def test_fit_parse_multisport_duathlon():
    activity = assert_parse_without_errors("tests/files/duathlon.fit")
    assert_duathlon(
        activity,
        [
            (RUNNING_SPORT, GENERIC_SUB_SPORT),
            (TRANSITION_SPORT, GENERIC_SUB_SPORT),
            (CYCLING_SPORT, ROAD_SUB_SPORT),
            (TRANSITION_SPORT, GENERIC_SUB_SPORT),
            (RUNNING_SPORT, GENERIC_SUB_SPORT)
        ]
    )
