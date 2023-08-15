import pytest

from datetime import datetime

from ..parse import FitParse, FitFileIdMesg, FitSessionMesg, Messages


def test_fit_file_id_mesg_dataclass_all_fields():
    fit_file_id_mesg = FitFileIdMesg.from_dict({
        "type": "activity",
        "serial_number": 12345,
        "time_created": datetime.now(),
        "manufacturer": "fit",
        "product": 1,
        "garmin_product": "garming"
    })
    assert isinstance(fit_file_id_mesg, FitFileIdMesg)


def test_fit_file_id_mesg_dataclass_only_needed_fields():
    fit_file_id_mesg = FitFileIdMesg.from_dict({"type": "activity"})
    assert isinstance(fit_file_id_mesg, FitFileIdMesg)


def test_fit_file_id_mesg_dataclass_fields_needed_error():
    with pytest.raises(ValueError):
        FitFileIdMesg.from_dict({"t": "activity"})


def test_fit_session_mesg_dataclass_all_fields():
    fit_session_mesg = FitSessionMesg.from_dict({
        "message_index": 1, "timestamp": datetime.now(), "start_time": datetime.now(),
        "total_elapsed_time": 1.0, "total_timer_time": 1.0, "sport_profile_name": "1",
        "sport": "1", "sub_sport": "1", "start_position_lat": 1, "start_position_long": 1,
        "end_position_lat": 1, "end_position_long": 1, "first_lap_index": 1, "num_laps": 1,
        "total_distance": 1.0, "total_cycles": 1, "total_strides": 1, "enhanced_avg_speed": 1.0,
        "avg_speed": 1.0, "enhanced_max_speed": 1.0, "max_speed": 1.0, "avg_heart_rate": 1.0,
        "max_heart_rate": 1.0, "avg_cadence": 1.0, "avg_running_cadence": 1.0, "max_cadence": 1.0,
        "max_running_cadence": 1.0, "total_calories": 1.0, "total_ascend": 1.0,
        "total_descend": 1.0, "avg_temperature": 1.0, "max_temperature": 1.0,
        "min_temperature": 1.0, "enhanced_avg_respiration_rate": 1.0,
        "enhanced_max_respiration_rate": 1.0, "enhanced_min_rspiration_rate": 1.0,
        "training_load_peak": 1.0, "total_training_effect": 1.0,
        "total_anaerobic_training_effect": 1.0, "avg_fractional_cadence": 1.0,
        "max_fractional_cadence": 1.0, "total_fractional_ascent": 1.0,
        "total_fractional_descent": 1.0, "total_grit": 1.0, "avg_flow": 1.0
    })
    assert isinstance(fit_session_mesg, FitSessionMesg)


def test_fit_session_mesg_dataclass_only_needed_fields():
    fit_session_mesg = FitSessionMesg.from_dict({
        "message_index": 1, "timestamp": datetime.now(), "start_time": datetime.now(),
        "total_elapsed_time": 1.0, "total_timer_time": 1.0, "sport_profile_name": "1",
        "sport": "1", "sub_sport": "1"
    })
    assert isinstance(fit_session_mesg, FitSessionMesg)


def test_fit_session_mesg_dataclass_fields_needed_error():
    with pytest.raises(ValueError):
        FitSessionMesg.from_dict({"message_index": 1})


def test_fit_session_mesg_dataclass_need_sub_sport():
    with pytest.raises(ValueError):
        FitSessionMesg.from_dict({
            "message_index": 1, "timestamp": datetime.now(), "start_time": datetime.now(),
            "total_elapsed_time": 1.0, "total_timer_time": 1.0, "sport_profile_name": "1",
            "sport": "1", "start_position_lat": 1, "start_position_long": 1, "end_position_lat": 1,
            "end_position_long": 1, "first_lap_index": 1, "num_laps": 1, "total_distance": 1.0,
            "total_cycles": 1, "total_strides": 1, "enhanced_avg_speed": 1.0, "avg_speed": 1.0,
            "enhanced_max_speed": 1.0, "max_speed": 1.0, "avg_heart_rate": 1.0,
            "max_heart_rate": 1.0, "avg_cadence": 1.0, "avg_running_cadence": 1.0,
            "max_cadence": 1.0, "max_running_cadence": 1.0, "total_calories": 1.0,
            "total_ascend": 1.0, "total_descend": 1.0, "avg_temperature": 1.0,
            "max_temperature": 1.0, "min_temperature": 1.0, "enhanced_avg_respiration_rate": 1.0,
            "enhanced_max_respiration_rate": 1.0, "enhanced_min_rspiration_rate": 1.0,
            "training_load_peak": 1.0, "total_training_effect": 1.0,
            "total_anaerobic_training_effect": 1.0, "avg_fractional_cadence": 1.0,
            "max_fractional_cadence": 1.0, "total_fractional_ascent": 1.0,
            "total_fractional_descent": 1.0, "total_grit": 1.0, "avg_flow": 1.0
        })


def test_fit_parse():
    fit_parse = FitParse()
    fit_parse.parse("tests/files/running_with_3x1km_workout.fit")

    messages = fit_parse.get_messages()

    assert Messages.file_id in messages
    assert messages[Messages.file_id] is not None
    assert len(messages[Messages.file_id]) == 1

    assert Messages.session in messages
    assert messages[Messages.session] is not None
    assert len(messages[Messages.session]) == 1
