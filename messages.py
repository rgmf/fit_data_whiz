from .exceptions import UncompleteMessageException, NotSupportedFitFileException


# @dataclass(init=False)
# class FitFileIdMesg:
#     file_type: str = field(metadata={"dataclass_field": "type"})
#     serial_number: int | None = None
#     time_created: datetime | None = None
#     manufacturer: str | None = None
#     product: int | None = None
#     garmin_product: str | None = None

#     @classmethod
#     def from_dict(cls, d: dict) -> Self:
#         if "type" in d:
#             d["file_type"] = d["type"]
#             del d["type"]

#         if not can_build_mesg(cls, d):
#             raise UncompleteMessageException("file_id", d.keys())

#         if d["file_type"].lower() != "activity":
#             raise NotSupportedFitFileException(d["file_type"])

#         fit_file_id_mesg = FitFileIdMesg()
#         field_names = [f.name for f in fields(cls) if f.name in d.keys()]
#         for name in field_names:
#             fit_file_id_mesg.__setattr__(name, d[name])
#         return fit_file_id_mesg


class FitMesg:
    __slots__ = ("needed_attrs",)

    def __init__(self):
        self.needed_attrs = []

    def can_build_mesg(self, data: dict) -> bool:
        missing_fields = [f for f in self.needed_attrs if f not in data]
        return len(missing_fields) == 0


class FitFileIdMesg(FitMesg):
    __slots__ = (
        "file_type", "serial_number", "time_created", "manufacturer", "product", "garmin_product"
    )

    def __init__(self, d: dict):
        if "type" in d:
            d["file_type"] = d["type"]
            del d["type"]

        self.needed_attrs = ["file_type"]

        if not self.can_build_mesg(d):
            raise UncompleteMessageException("file_id", list(d.keys()))

        if d["file_type"].lower() != "activity":
            raise NotSupportedFitFileException(d["file_type"])

        for attr in self.__slots__:
            if attr in d:
                setattr(self, attr, d[attr])
            else:
                setattr(self, attr, None)


# @dataclass(init=False)
# class FitSessionMesg:
#     message_index: int
#     timestamp: datetime
#     start_time: datetime
#     total_elapsed_time: float
#     total_timer_time: float
#     sport: str
#     sub_sport: str

#     start_position_lat: int | None = None
#     start_position_long: int | None = None
#     end_position_lat: int | None = None
#     end_position_long: int | None = None

#     first_lap_index: int | None = None
#     num_laps: int | None = None

#     sport_profile_name: str | None = None
#     sport_index: int | None = None

#     total_distance: float | None = None
#     total_cycles: int | None = None
#     total_strides: int | None = None
#     enhanced_avg_speed: float | None = None
#     avg_speed: float | None = None
#     enhanced_max_speed: float | None = None
#     max_speed: float | None = None
#     avg_heart_rate: float | None = None
#     max_heart_rate: float | None = None
#     avg_cadence: float | None = None
#     avg_running_cadence: float | None = None
#     max_cadence: float | None = None
#     max_running_cadence: float | None = None
#     total_calories: float | None = None
#     total_ascent: float | None = None
#     total_descent: float | None = None
#     avg_temperature: float | None = None
#     max_temperature: float | None = None
#     min_temperature: float | None = None
#     enhanced_avg_respiration_rate: float | None = None
#     enhanced_max_respiration_rate: float | None = None
#     enhanced_min_respiration_rate: float | None = None

#     training_load_peak: float | None = None
#     total_training_effect: float | None = None
#     total_anaerobic_training_effect: float | None = None

#     avg_fractional_cadence: float | None = None
#     max_fractional_cadence: float | None = None
#     total_fractional_ascent: float | None = None
#     total_fractional_descent: float | None = None

#     @classmethod
#     def from_dict(cls, d: dict) -> Self:
#         if not can_build_mesg(cls, d):
#             raise UncompleteMessageException("session", d.keys())

#         fit_session_mesg = FitSessionMesg()
#         field_names = [field.name for field in fields(cls) if field.name in d.keys()]
#         for name in field_names:
#             fit_session_mesg.__setattr__(name, d[name])
#         return fit_session_mesg


class FitSessionMesg(FitMesg):
    __slots__ = (
        "message_index", "timestamp", "start_time", "total_elapsed_time", "total_timer_time",
        "sport", "sub_sport", "start_position_lat", "start_position_long", "end_position_lat",
        "end_position_long", "first_lap_index", "num_laps", "sport_profile_name", "sport_index",
        "total_distance", "total_cycles", "total_strides", "enhanced_avg_speed", "avg_speed",
        "enhanced_max_speed", "max_speed", "avg_heart_rate", "max_heart_rate", "avg_cadence",
        "avg_running_cadence", "max_cadence", "max_running_cadence", "total_calories",
        "total_ascent", "total_descent", "avg_temperature", "max_temperature", "min_temperature",
        "enhanced_avg_respiration_rate", "enhanced_max_respiration_rate",
        "enhanced_min_respiration_rate", "training_load_peak", "total_training_effect",
        "total_anaerobic_training_effect", "avg_fractional_cadence", "max_fractional_cadence",
        "total_fractional_ascent", "total_fractional_descent"
    )

    def __init__(self, d: dict):
        self.needed_attrs = [
            "message_index",
            "timestamp",
            "start_time",
            "total_elapsed_time",
            "total_timer_time",
            "sport",
            "sub_sport"
        ]

        if not self.can_build_mesg(d):
            raise UncompleteMessageException("session", list(d.keys()))

        for attr in self.__slots__:
            if attr in d:
                setattr(self, attr, d[attr])
            else:
                setattr(self, attr, None)


# @dataclass(init=False)
# class FitRecordMesg:
#     timestamp: datetime
#     position_lat: int | None = None
#     position_long: int | None = None
#     altitude: float | None = None
#     enhanced_altitude: float | None = None
#     heart_rate: int | None = None
#     cadence: int | None = None
#     distance: float | None = None
#     enhanced_distance: float | None = None
#     speed: float | None = None
#     enhanced_speed: float | None = None
#     power: int | None = None
#     grade: int | None = None
#     resistance: int | None = None
#     time_from_course: int | None = None
#     cycle_length: int | None = None
#     temperature: int | None = None
#     cycles: int | None = None
#     total_cycles: int | None = None
#     gps_accuracy: int | None = None
#     vertical_speed: int | None = None
#     calories: int | None = None
#     fractional_cadence: int | None = None
#     step_length: int | None = None
#     absolute_pressure: int | None = None
#     respiration_rate: int | None = None
#     enhanced_respiration_rate: int | None = None
#     current_stress: int | None = None
#     ascent_rate: int | None = None

#     @classmethod
#     def from_dict(cls, d: dict) -> Self:
#         if not can_build_mesg(cls, d):
#             raise UncompleteMessageException("record", d.keys())

#         fit_record_mesg = FitRecordMesg()
#         field_names = [f.name for f in fields(cls) if f.name in d.keys()]
#         for name in field_names:
#             fit_record_mesg.__setattr__(name, d[name])
#         return fit_record_mesg


class FitRecordMesg(FitMesg):
    __slots__ = (
        "timestamp", "position_lat", "position_long", "altitude", "enhanced_altitude",
        "heart_rate", "cadence", "distance", "enhanced_distance", "speed", "enhanced_speed",
        "power", "grade", "resistance", "time_from_course", "cycle_length", "temperature",
        "cycles", "total_cycles", "gps_accuracy", "vertical_speed", "calories",
        "fractional_cadence", "step_length", "absolute_pressure", "respiration_rate",
        "enhanced_respiration_rate", "current_stress", "ascent_rate"
    )

    def __init__(self, d: dict):
        self.needed_attrs = ["timestamp"]

        if not self.can_build_mesg(d):
            raise UncompleteMessageException("record", list(d.keys()))

        for attr in self.__slots__:
            if attr in d:
                setattr(self, attr, d[attr])
            else:
                setattr(self, attr, None)


# @dataclass(init=False)
# class FitLapMesg:
#     message_index: int | None = None

#     sport: str | None = None
#     sub_sport: str | None = None

#     start_position_lat: int | None = None
#     start_position_long: int | None = None
#     end_position_lat: int | None = None
#     end_position_long: int | None = None

#     total_elapsed_time: float | None = None
#     total_timer_time: float | None = None
#     total_moving_time: float | None = None

#     total_distance: float | None = None

#     timestamp: datetime | None = None
#     start_time: datetime | None = None

#     avg_speed: float | None = None
#     enhanced_avg_speed: float | None = None
#     max_speed: float | None = None
#     enhanced_max_speed: float | None = None

#     avg_heart_rate: int | None = None
#     max_heart_rate: int | None = None
#     min_heart_rate: int | None = None

#     avg_cadence: int | None = None
#     avg_running_cadence: int | None = None
#     max_cadence: int | None = None
#     max_running_cadence: int | None = None

#     total_ascent: int | None = None
#     total_descent: int | None = None
#     avg_altitude: float | None = None
#     enhanced_avg_altitude: float | None = None
#     max_altitude: float | None = None
#     enhanced_max_altitude: float | None = None
#     min_altitude: float | None = None
#     enhanced_min_altitude: float | None = None
#     avg_grade: int | None = None
#     avg_pos_grade: int | None = None
#     avg_neg_grade: int | None = None
#     max_pos_grade: int | None = None
#     max_neg_grade: int | None = None

#     wkt_step_index: int | None = None

#     event: str | None = None
#     event_type: str | None = None

#     total_cycles: int | None = None
#     total_strides: int | None = None
#     total_strokes: int | None = None

#     total_calories: int | None = None
#     total_fat_calories: int | None = None

#     intensity: int | None = None
#     lap_trigger: int | None = None
#     gps_accuracy: int | None = None

#     avg_temperature: int | None = None
#     max_temperature: int | None = None
#     min_tempearture: int | None = None

#     avg_respiration_rate: int | None = None
#     enhanced_avg_respiration_rate: int | None = None
#     max_respiration_rate: int | None = None
#     enhanced_max_respiration_rate: int | None = None

#     @classmethod
#     def from_dict(cls, d: dict) -> Self:
#         if not can_build_mesg(cls, d):
#             raise UncompleteMessageException("lap", d.keys())

#         fit_lap_mesg = FitLapMesg()
#         field_names = [f.name for f in fields(cls) if f.name in d.keys()]
#         for name in field_names:
#             fit_lap_mesg.__setattr__(name, d[name])
#         return fit_lap_mesg


class FitLapMesg(FitMesg):
    __slots__ = (
        "message_index", "sport", "sub_sport", "start_position_lat", "start_position_long",
        "end_position_lat", "end_position_long", "total_elapsed_time", "total_timer_time",
        "total_moving_time", "total_distance", "timestamp", "start_time", "avg_speed",
        "enhanced_avg_speed", "max_speed", "enhanced_max_speed", "avg_heart_rate",
        "max_heart_rate", "min_heart_rate", "avg_cadence", "avg_running_cadence", "max_cadence",
        "max_running_cadence", "total_ascent", "total_descent", "avg_altitude",
        "enhanced_avg_altitude", "max_altitude", "enhanced_max_altitude", "min_altitude",
        "enhanced_min_altitude", "avg_grade", "avg_pos_grade", "avg_neg_grade", "max_pos_grade",
        "max_neg_grade", "wkt_step_index", "event", "event_type", "total_cycles", "total_strides",
        "total_strokes", "total_calories", "total_fat_calories", "intensity", "lap_trigger",
        "gps_accuracy", "avg_temperature", "max_temperature", "min_temperature",
        "avg_respiration_rate", "enhanced_avg_respiration_rate", "max_respiration_rate",
        "enhanced_max_respiration_rate"
    )

    def __init__(self, d: dict):
        self.needed_attrs = ["message_index", "timestamp"]

        if not self.can_build_mesg(d):
            raise UncompleteMessageException("lap", list(d.keys()))

        for attr in self.__slots__:
            if attr in d:
                setattr(self, attr, d[attr])
            else:
                setattr(self, attr, None)


# @dataclass(init=False)
# class FitSetMesg:
#     timestamp: datetime
#     duration: float | None = None
#     repetitions: int | None = None
#     weight: float | None = None
#     set_type: str | None = None
#     start_time: datetime | None = None
#     category: List[str] | None = None
#     category_subtype: List[str | int] | None = None
#     weight_display_unit: str | None = None
#     message_index: int | None = None
#     wkt_step_index: int | None = None

#     @classmethod
#     def from_dict(cls, d: dict) -> Self:
#         if not can_build_mesg(cls, d):
#             raise UncompleteMessageException("set", d.keys())

#         fit_set_mesg = FitSetMesg()
#         field_names = [f.name for f in fields(cls) if f.name in d.keys()]
#         for name in field_names:
#             fit_set_mesg.__setattr__(name, d[name])
#         return fit_set_mesg


class FitSetMesg(FitMesg):
    __slots__ = (
        "timestamp", "duration", "repetitions", "weight", "set_type", "start_time", "category",
        "category_subtype", "weight_display_unit", "message_index", "wkt_step_index"
    )

    def __init__(self, d: dict):
        self.needed_attrs = ["timestamp"]

        if not self.can_build_mesg(d):
            raise UncompleteMessageException("set", list(d.keys()))

        for attr in self.__slots__:
            if attr in d:
                setattr(self, attr, d[attr])
            else:
                setattr(self, attr, None)


# @dataclass(init=False)
# class FitSplitMesg:
#     split_type: str
#     total_elapsed_time: float
#     total_timer_time: float
#     start_time: datetime

#     # I figured out what this fields are in my activities recorded with a
#     # Garmin Fenix 6s. For example: in split messages there's a key which value
#     # is 15 with heart rate's average.
#     avg_hr: int | None = field(metadata={"fit_field_key": "15"}, default=None)
#     max_hr: int | None = field(metadata={"fit_field_key": "16"}, default=None)
#     total_calories: int | None = field(metadata={"fit_field_key": "28"}, default=None)
#     difficulty: int | None = field(metadata={"fit_field_key": "70"}, default=None)
#     result: int | None = field(
#         metadata={"fit_field_key": "71"}, default=None
#     )  # completed (3) or try (2)
#     discarded: int | None = field(
#         metadata={"fit_field_key": "80"}, default=None
#     )  # discarded (0)

#     @classmethod
#     def from_dict(cls, d: dict) -> Self:
#         # Look for "hidden" fit field keys in the dictionary to tranform them
#         # to the field names in this dataclass.
#         for f in fields(cls):
#             field_name = f.metadata.get("fit_field_key", "-1")
#             if int(field_name) in d:
#                 value = d.pop(int(field_name))
#             elif field_name in d:
#                 value = d.pop(field_name)
#             else:
#                 value = None
#             d[f.name] = value

#         if not can_build_mesg(cls, d):
#             raise UncompleteMessageException("split", d.keys())

#         fit_split_mesg = FitSplitMesg()
#         field_names = [f.name for f in fields(cls) if f.name in d.keys()]
#         for name in field_names:
#             fit_split_mesg.__setattr__(name, d[name])
#         return fit_split_mesg


class FitSplitMesg(FitMesg):
    __slots__ = (
        "split_type", "total_elapsed_time", "total_timer_time", "start_time", "avg_hr", "max_hr",
        "total_calories", "difficulty", "result", "discarded"
    )

    def __init__(self, d: dict):
        self.needed_attrs = ["split_type", "total_elapsed_time", "total_timer_time", "start_time"]

        if not self.can_build_mesg(d):
            raise UncompleteMessageException("split", list(d.keys()))

        # I figured out what this fields are in my activities recorded with a
        # Garmin Fenix 6s. For example: in split messages there's a key which value
        # is 15 with heart rate's average.
        special_attr: dict[str, str] = {
            "avg_hr": "15",
            "max_hr": "16",
            "total_calories": "28",
            "difficulty": "70",
            "result": "71",          # completed (3) or try (2)
            "discarded": "80"        # discarded (0)
        }

        for name, code in special_attr.items():
            if code in d:
                setattr(self, name, d[code])
            elif int(code) in d:
                setattr(self, name, d[int(code)])
            else:
                setattr(self, name, None)

        for attr in self.__slots__:
            if attr in d:
                setattr(self, attr, d[attr])
            elif attr not in special_attr:
                setattr(self, attr, None)


# @dataclass(init=False)
# class FitWorkoutMesg:
#     message_index: int | None = None
#     sport: str | None = None
#     sub_sport: str | None = None
#     capabilities: int | None = None
#     num_valid_steps: int | None = None
#     wkt_name: str | None = None
#     pool_length: int | None = None
#     pool_length_unit: str | None = None

#     @classmethod
#     def from_dict(cls, d: dict) -> Self:
#         if not can_build_mesg(cls, d):
#             raise UncompleteMessageException("workout", d.keys())

#         fit_workout_mesg = FitWorkoutMesg()
#         field_names = [f.name for f in fields(cls) if f.name in d.keys()]
#         for name in field_names:
#             fit_workout_mesg.__setattr__(name, d[name])
#         return fit_workout_mesg


class FitWorkoutMesg(FitMesg):
    __slots__ = (
        "message_index", "sport", "sub_sport", "capabilities", "num_valid_steps", "wkt_name",
        "pool_length", "pool_length_unit"
    )

    def __init__(self, d: dict):
        self.needed_attrs = ["message_index"]

        if not self.can_build_mesg(d):
            raise UncompleteMessageException("workout", list(d.keys()))

        for attr in self.__slots__:
            if attr in d:
                setattr(self, attr, d[attr])
            else:
                setattr(self, attr, None)


# @dataclass(init=False)
# class FitWorkoutStepMesg:
#     message_index: int

#     wkt_step_name: str | None = None

#     duration_type: str | None = None
#     duration_value: int | None = None
#     duration_time: float | None = None
#     duration_distance: float | None = None
#     duration_hr: int | None = None
#     duration_calories: int | None = None
#     duration_step: int | None = None
#     duration_power: int | None = None
#     duration_reps: int | None = None

#     target_type: str | None = None
#     target_value: int | None = None
#     target_speed_zone: int | None = None
#     target_hr_zone: int | None = None
#     target_cadence_zone: int | None = None
#     target_power_zone: int | None = None
#     target_stroke_type: int | None = None

#     repeat_steps: int | None = None
#     repeat_time: float | None = None
#     repeat_distance: float | None = None
#     repeat_calories: int | None = None
#     repeat_hr: int | None = None
#     repeat_power: int | None = None

#     custom_target_value_low: int | None = None
#     custom_target_speed_low: float | None = None
#     custom_target_heart_rate_low: int | None = None
#     custom_target_cadence_low: int | None = None
#     custom_target_power_low: int | None = None
#     custom_target_value_high: int | None = None
#     custom_target_speed_high: float | None = None
#     custom_target_heart_rate_high: int | None = None
#     custom_target_cadence_high: int | None = None
#     custom_target_power_high: int | None = None

#     intensity: str | None = None
#     notes: str | None = None

#     exercise_category: str | None = None
#     exercise_name: int | None = None
#     exercise_weight: float | None = None

#     weight_display_unit: str | None = None

#     secondary_target_type: str | None = None
#     secondary_target_value: int | None = None
#     secondary_target_speed_zone: int | None = None
#     secondary_target_hr_zone: int | None = None
#     secondary_target_cadence_zone: int | None = None
#     secondary_target_power_zone: int | None = None
#     secondary_target_stroke_type: int | None = None

#     secondary_custom_target_value_low: int | None = None
#     secondary_custom_target_speed_low: float | None = None
#     secondary_custom_target_heart_rate_low: int | None = None
#     secondary_custom_target_cadence_low: int | None = None
#     secondary_custom_target_power_low: int | None = None
#     secondary_custom_target_value_high: int | None = None
#     secondary_custom_target_speed_high: float | None = None
#     secondary_custom_target_heart_rate_high: int | None = None
#     secondary_custom_target_cadence_high: int | None = None
#     secondary_custom_target_power_high: int | None = None

#     @classmethod
#     def from_dict(cls, d: dict) -> Self:
#         if not can_build_mesg(cls, d):
#             raise UncompleteMessageException("workout_step", d.keys())

#         fit_workout_step_mesg = FitWorkoutStepMesg()
#         field_names = [f.name for f in fields(cls) if f.name in d.keys()]
#         for name in field_names:
#             fit_workout_step_mesg.__setattr__(name, d[name])
#         return fit_workout_step_mesg


class FitWorkoutStepMesg(FitMesg):
    __slots__ = (
        "message_index", "wkt_step_name", "duration_type", "duration_value", "duration_time",
        "duration_distance", "duration_hr", "duration_calories", "duration_step",
        "duration_power", "duration_reps", "target_type", "target_value", "target_speed_zone",
        "target_hr_zone", "target_cadence_zone", "target_power_zone", "target_stroke_type",
        "repeat_steps", "repeat_time", "repeat_distance", "repeat_calories", "repeat_hr",
        "repeat_power", "custom_target_value_low", "custom_target_speed_low",
        "custom_target_heart_rate_low", "custom_target_cadence_low", "custom_target_power_low",
        "custom_target_value_high", "custom_target_speed_high", "custom_target_heart_rate_high",
        "custom_target_cadence_high", "custom_target_power_high", "intensity", "notes",
        "exercise_category", "exercise_name", "exercise_weight", "weight_display_unit",
        "secondary_target_type", "secondary_target_value", "secondary_target_speed_zone",
        "secondary_target_hr_zone", "secondary_target_cadence_zone",
        "secondary_target_power_zone", "secondary_target_stroke_type",
        "secondary_custom_target_value_low", "secondary_custom_target_speed_low",
        "secondary_custom_target_heart_rate_low", "secondary_custom_target_cadence_low",
        "secondary_custom_target_power_low", "secondary_custom_target_value_high",
        "secondary_custom_target_speed_high", "secondary_custom_target_heart_rate_high",
        "secondary_custom_target_cadence_high", "secondary_custom_target_power_high"
    )

    def __init__(self, d: dict):
        self.needed_attrs = ["message_index"]

        if not self.can_build_mesg(d):
            raise UncompleteMessageException("workout", list(d.keys()))

        for attr in self.__slots__:
            if attr in d:
                setattr(self, attr, d[attr])
            else:
                setattr(self, attr, None)
