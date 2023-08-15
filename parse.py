from datetime import datetime
from dataclasses import dataclass, field, fields
from typing import List
from enum import StrEnum

from garmin_fit_sdk import Decoder, Stream, Profile


class FitException(Exception):
    def __init__(self, message, filename: str):
        super().__init__(f"Error found in FIT file {filename}: {message}")


class NotSupportedFitFileException(FitException):
    def __init__(self, filename: str, file_type: str):
        super().__init__(
            message=f"The FIT file {file_type} is not supported",
            filename=filename
        )


class NotSupportedFitSportException(FitException):
    def __init__(self, filename: str, sport: str, sub_sport: str):
        super().__init__(
            message=f"The FIT file describes a not supported sport: {sport} ({sub_sport})",
            filename=filename
        )


class NotFitSessionFoundException(FitException):
    def __init__(self, filename):
        super().__init__(
            message="Not found 'session' into FIT file",
            filename=filename
        )


def can_build_mesg(datacls, data: dict) -> bool:
    missing_fields = [f.name for f in fields(datacls) if f.default and f.name not in data]
    return len(missing_fields) == 0


@dataclass(init=False)
class FitFileIdMesg:
    file_type: str = field(metadata={"dataclass_field": "type"})
    serial_number: int | None = None
    time_created: datetime | None = None
    manufacturer: str | None = None
    product: int | None = None
    garmin_product: str | None = None

    @classmethod
    def from_dict(cls, d: dict) -> "FitFileIdMesg":
        if "type" in d:
            d["file_type"] = d["type"]
            del d["type"]

        if not can_build_mesg(cls, d):
            raise ValueError(
                "Incomplete data to build a FIT file message: "
                f"{', '.join([n for n in d.keys()])}"
            )

        fit_file_id_mesg = FitFileIdMesg()
        field_names = [f.name for f in fields(cls) if f.name in d.keys()]
        for name in field_names:
            fit_file_id_mesg.__setattr__(name, d[name])
        return fit_file_id_mesg


@dataclass(init=False)
class FitSessionMesg:
    message_index: int
    timestamp: datetime
    start_time: datetime
    total_elapsed_time: float
    total_timer_time: float
    sport_profile_name: str
    sport: str
    sub_sport: str

    start_position_lat: int | None = None
    start_position_long: int | None = None
    end_position_lat: int | None = None
    end_position_long: int | None = None

    first_lap_index: int | None = None
    num_laps: int | None = None

    total_distance: float | None = None
    total_cycles: int | None = None
    total_strides: int | None = None
    enhanced_avg_speed: float | None = None
    avg_speed: float | None = None
    enhanced_max_speed: float | None = None
    max_speed: float | None = None
    avg_heart_rate: float | None = None
    max_heart_rate: float | None = None
    avg_cadence: float | None = None
    avg_running_cadence: float | None = None
    max_cadence: float | None = None
    max_running_cadence: float | None = None
    total_calories: float | None = None
    total_ascend: float | None = None
    total_descend: float | None = None
    avg_temperature: float | None = None
    max_temperature: float | None = None
    min_temperature: float | None = None
    enhanced_avg_respiration_rate: float | None = None
    enhanced_max_respiration_rate: float | None = None
    enhanced_min_respiration_rate: float | None = None

    training_load_peak: float | None = None
    total_training_effect: float | None = None
    total_anaerobic_training_effect: float | None = None

    avg_fractional_cadence: float | None = None
    max_fractional_cadence: float | None = None
    total_fractional_ascent: float | None = None
    total_fractional_descent: float | None = None

    total_grit: float | None = None
    avg_flow: float | None = None

    @classmethod
    def from_dict(cls, d: dict) -> "FitSessionMesg":
        if not can_build_mesg(cls, d):
            raise ValueError(
                "Incomplete data to build a FIT session message: "
                f"{', '.join([n for n in d.keys()])}"
            )

        fit_session_mesg = FitSessionMesg()
        field_names = [field.name for field in fields(cls) if field.name in d.keys()]
        for name in field_names:
            fit_session_mesg.__setattr__(name, d[name])
        return fit_session_mesg


class Messages(StrEnum):
    """
    Messages from Garmin FIT Profile standard supported/needed by this program.

    The str values are the keys of Profile["mesg_num"] dictionary where all FIT
    messages are.
    """
    file_id = "FILE_ID"
    sport = "SPORT"
    training_file = "TRAINING_FILE"
    workout = "WORKOUT"
    workout_step = "WORKOUT_STEP"
    record = "RECORD"
    lap = "LAP"
    set = "SET"
    time_in_zone = "TIME_IN_ZONE"
    session = "SESSION"
    activity = "ACTIVITY"


class FitParse:
    def __init__(self):
        self._messages = {str(name): [] for name in list(Messages)}
        self._errors = None

    def parse(self, file_path: str):
        stream = Stream.from_file(file_path)
        decoder = Decoder(stream)
        _, self._errors = decoder.read(mesg_listener=self._mesg_listener)

    def get_messages(self) -> List[dict]:
        return self._messages

    def _mesg_listener(self, mesg_num: int, mesg: dict):
        for name, num in Profile["mesg_num"].items():
            self._add_message_if_supported(mesg_num, num, name, mesg)

    def _add_message_if_supported(
            self, mesg_num: int, profile_num: int, mesg_name: str, mesg_data: dict
    ):
        if mesg_num != profile_num or mesg_name not in list(Messages):
            return

        if mesg_name == Messages.file_id:
            self._messages[mesg_name].append(FitFileIdMesg.from_dict(mesg_data))
        elif mesg_name == Messages.session:
            self._messages[mesg_name].append(FitSessionMesg.from_dict(mesg_data))
