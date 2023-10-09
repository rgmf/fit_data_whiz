import pytest

from datetime import datetime, timezone

from pydantic import ValidationError

from fit_data_whiz.fit.models import FileIdModel, SessionModel, SplitModel


def test_fit_file_id_all_fields():
    fit_file_id = FileIdModel(**{
        "type": "activity",
        "serial_number": 12345,
        "time_created": datetime.now(),
        "manufacturer": "fit",
        "product": 1,
        "garmin_product": "garming"
    })
    assert isinstance(fit_file_id, FileIdModel)


def test_fit_file_id_only_needed_fields():
    fit_file_id = FileIdModel(**{"type": "activity"})
    assert isinstance(fit_file_id, FileIdModel)


def test_fit_file_id_fields_needed_error():
    with pytest.raises(ValidationError):
        FileIdModel(**{"t": "activity"})


def test_fit_session_all_fields():
    fit_session = SessionModel(**{
        "message_index": 1, "timestamp": datetime.now(), "start_time": datetime.now(),
        "total_elapsed_time": 1.0, "total_timer_time": 1.0, "sport_profile_name": "1",
        "sport": "1", "sub_sport": "1", "start_position_lat": 1, "start_position_long": 1,
        "end_position_lat": 1, "end_position_long": 1, "first_lap_index": 1, "num_laps": 1,
        "total_distance": 1.0, "total_cycles": 1, "total_strides": 1, "enhanced_avg_speed": 1.0,
        "avg_speed": 1.0, "enhanced_max_speed": 1.0, "max_speed": 1.0, "avg_heart_rate": 1.0,
        "max_heart_rate": 1.0, "avg_cadence": 1.0, "avg_running_cadence": 1.0, "max_cadence": 1.0,
        "max_running_cadence": 1.0, "total_calories": 1.0, "total_ascent": 1.0,
        "total_descent": 1.0, "avg_temperature": 1.0, "max_temperature": 1.0,
        "min_temperature": 1.0, "enhanced_avg_respiration_rate": 1.0,
        "enhanced_max_respiration_rate": 1.0, "enhanced_min_rspiration_rate": 1.0,
        "training_load_peak": 1.0, "total_training_effect": 1.0,
        "total_anaerobic_training_effect": 1.0, "avg_fractional_cadence": 1.0,
        "max_fractional_cadence": 1.0, "total_fractional_ascent": 1.0,
        "total_fractional_descent": 1.0, "total_grit": 1.0, "avg_flow": 1.0
    })
    assert isinstance(fit_session, SessionModel)


def test_fit_session_only_needed_fields():
    fit_session = SessionModel(**{
        "message_index": 1, "timestamp": datetime.now(), "start_time": datetime.now(),
        "total_elapsed_time": 1.0, "total_timer_time": 1.0, "sport_profile_name": "1",
        "sport": "1", "sub_sport": "1"
    })
    assert isinstance(fit_session, SessionModel)


def test_fit_session_fields_needed_error():
    with pytest.raises(ValidationError):
        SessionModel(**{"message_index": 1})


def test_fit_session_need_sub_sport():
    with pytest.raises(ValidationError):
        SessionModel(**{
            "message_index": 1, "timestamp": datetime.now(), "start_time": datetime.now(),
            "total_elapsed_time": 1.0, "total_timer_time": 1.0, "sport_profile_name": "1",
            "sport": "1", "start_position_lat": 1, "start_position_long": 1, "end_position_lat": 1,
            "end_position_long": 1, "first_lap_index": 1, "num_laps": 1, "total_distance": 1.0,
            "total_cycles": 1, "total_strides": 1, "enhanced_avg_speed": 1.0, "avg_speed": 1.0,
            "enhanced_max_speed": 1.0, "max_speed": 1.0, "avg_heart_rate": 1.0,
            "max_heart_rate": 1.0, "avg_cadence": 1.0, "avg_running_cadence": 1.0,
            "max_cadence": 1.0, "max_running_cadence": 1.0, "total_calories": 1.0,
            "total_ascent": 1.0, "total_descent": 1.0, "avg_temperature": 1.0,
            "max_temperature": 1.0, "min_temperature": 1.0, "enhanced_avg_respiration_rate": 1.0,
            "enhanced_max_respiration_rate": 1.0, "enhanced_min_rspiration_rate": 1.0,
            "training_load_peak": 1.0, "total_training_effect": 1.0,
            "total_anaerobic_training_effect": 1.0, "avg_fractional_cadence": 1.0,
            "max_fractional_cadence": 1.0, "total_fractional_ascent": 1.0,
            "total_fractional_descent": 1.0, "total_grit": 1.0, "avg_flow": 1.0
        })


def test_fit_split_with_all_data_with_str_keys():
    fit_split = SplitModel(**{
        "253": 1035017335,
        "total_elapsed_time": 186.824,
        "total_timer_time": 186.824,
        "7": 0,
        "start_time": datetime(2022, 10, 18, 7, 51, 54, tzinfo=timezone.utc),
        "27": 1035014100,
        "28": 15,
        "70": 3,
        "254": 0,
        "79": 4,
        "split_type": "climb_active",
        "11": 31,
        "12": 69,
        "15": 88,
        "16": 100,
        "32": 28,
        "33": 28,
        "34": 27,
        "69": 9,
        "71": 3
    })
    assert isinstance(fit_split, SplitModel)
    assert fit_split.avg_hr is not None
    assert fit_split.max_hr is not None
    assert fit_split.total_calories is not None
    assert fit_split.difficulty is not None
    assert fit_split.result is not None
    assert fit_split.discarded is None


def test_fit_split_with_only_needed_data():
    fit_split = SplitModel(**{
        "total_elapsed_time": 186.824,
        "total_timer_time": 186.824,
        "start_time": datetime(2022, 10, 18, 7, 51, 54, tzinfo=timezone.utc),
        "split_type": "climb_active"
    })
    assert isinstance(fit_split, SplitModel)
    assert fit_split.avg_hr is None
    assert fit_split.max_hr is None
    assert fit_split.total_calories is None
    assert fit_split.difficulty is None
    assert fit_split.result is None
    assert fit_split.discarded is None


def test_fit_split_with_bad_data_typeh():
    with pytest.raises(ValidationError):
        SplitModel(**{
            "total_elapsed_time": 186.824,
            "total_timer_time": 186.824,
            "start_time": 200034,
            "split_type": 1
        })
