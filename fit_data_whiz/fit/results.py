from abc import ABC
from datetime import date, datetime, timedelta
from collections import namedtuple

from fit_data_whiz.fit.definitions import (
    HRV_STATUS,
    ACTIVITY_TYPES,
    ACTIVITY_TYPE_UNKNOWN,
    SplitType,
    ClimbResult,
    TRANSITION_SPORT,
    is_distance_sport,
    SLEEP_LEVEL
)
from fit_data_whiz.fit.models import (
    HrvModel,
    HrvValueModel,
    MonitorModel,
    RespirationRateModel,
    StressLevelModel,
    SleepModel,
    SleepLevelModel,
    WorkoutModel,
    WorkoutStepModel,
    SplitModel,
    MonitoringModel,
    ActivityModel,
    ClimbActivityModel,
    DistanceActivityModel,
    SetActivityModel,
    LapModel,
    SetModel,
    MultisportActivityModel,
    SessionModel,
    RecordModel
)
from fit_data_whiz.utils.date_utils import (
    try_to_compute_local_datetime,
    combine_date_and_seconds
)

DoubleStat = namedtuple("DoubleStat", ["max", "avg"])
TripleStat = namedtuple("TripleStat", ["max", "min", "avg"])
AltitudeStat = namedtuple("AltitudeStat", ["max", "min", "gain", "loss"])
LocationStat = namedtuple("LocationStat", ["lat", "lon"])
TimeStat = namedtuple(
    "TimeStat", [
        "timestamp",   # when event was registered
        "start_time",  # start time, when user pressed play/start button.
        "elapsed",     # time from start to end NOT including pauses.
        "timer"        # time from start to end including pauses.
    ]
)
RecordsAndLaps = namedtuple("RecordsAndLaps", ["records", "laps"])


def filter_by_session(
    session: SessionModel,
    records: list[RecordModel],
    laps: list[LapModel]
) -> RecordsAndLaps:
    if not isinstance(session.start_time, datetime):
        return RecordsAndLaps([], [])
    if not isinstance(session.total_timer_time, int | float):
        return RecordsAndLaps([], [])

    datetime_from: datetime = session.start_time
    datetime_to: datetime = (
        session.start_time + timedelta(seconds=session.total_timer_time)
    )

    return RecordsAndLaps(
        [
            record for record in records
            if datetime_from <= record.timestamp <= datetime_to
        ],
        [
            lap for lap in laps
            if datetime_from <= lap.timestamp <= datetime_to
        ]
    )


class FitResult(ABC):
    __slots__ = ("fit_file_path",)

    def __init__(self, fit_file_path: str) -> None:
        self.fit_file_path = fit_file_path


class FitError(FitResult):
    __slots__ = ("errors",)

    def __init__(self, fit_file_Path: str, errors: list[Exception]) -> None:
        super().__init__(fit_file_Path)
        self.errors = errors


class FitWorkoutStep:
    __slots__ = ("message_index",)

    def __init__(self, step: WorkoutStepModel) -> None:
        self.message_index = step.message_index


class FitWorkout:
    __slots__ = ("name", "sport", "steps")

    def __init__(self, workout: WorkoutModel, steps: list[WorkoutStepModel]) -> None:
        self.name: str = workout.wkt_name
        self.sport: str = workout.sport
        self.steps: list[WorkoutStepModel] = [WorkoutStepModel(s) for s in steps]


class FitActivity(FitResult):
    __slots__ = (
        "model", "name", "sport", "sub_sport", "time", "hr", "temperature",
        "total_calories", "workout"
    )

    def __init__(self, fit_file_path: str, model: ActivityModel) -> None:
        super().__init__(fit_file_path)
        self.model: ActivityModel = model
        self.name = model.session.sport
        self.sport = model.session.sport
        self.sub_sport = model.session.sub_sport
        self.time = TimeStat(
            timestamp=model.session.timestamp,
            start_time=model.session.start_time,
            elapsed=model.session.total_elapsed_time,
            timer=model.session.total_timer_time
        )
        self.hr = DoubleStat(
            max=model.session.max_heart_rate,
            avg=model.session.avg_heart_rate
        )
        self.temperature = TripleStat(
            max=model.session.max_temperature,
            min=model.session.min_temperature,
            avg=model.session.avg_temperature
        )
        self.total_calories = model.session.total_calories
        self.workout = (
            FitWorkout(model.workout, model.workout_steps) if model.workout else None
        )


class FitLap:
    __slots__ = (
        "message_index", "timestamp", "time", "total_distance", "speed", "hr",
        "altitude", "total_calories", "cadence", "total_strides",
        "start_location", "end_location",
    )

    def __init__(self, lap: LapModel) -> None:
        self.message_index: int = lap.message_index
        self.timestamp: datetime = lap.timestamp
        self.time: TimeStat = TimeStat(
            timestamp=lap.timestamp,
            start_time=lap.start_time,
            elapsed=lap.total_elapsed_time,
            timer=lap.total_timer_time
        )
        self.total_distance: float | None = lap.total_distance
        self.speed: DoubleStat = DoubleStat(
            max=lap.enhanced_max_speed or lap.max_speed,
            avg=lap.enhanced_avg_speed or lap.avg_speed
        )
        self.hr: DoubleStat = DoubleStat(max=lap.max_heart_rate, avg=lap.avg_heart_rate)
        self.altitude: AltitudeStat = AltitudeStat(
            max=lap.enhanced_max_altitude or lap.max_altitude,
            min=lap.enhanced_min_altitude or lap.min_altitude,
            gain=lap.total_ascent,
            loss=lap.total_descent
        )
        self.total_calories: int | None = lap.total_calories
        self.cadence = DoubleStat(
            max=lap.max_cadence or lap.max_running_cadence,
            avg=lap.avg_cadence or lap.avg_running_cadence
        )
        self.total_strides: int | None = lap.total_strides or lap.total_strokes
        self.start_location: LocationStat = LocationStat(
            lat=lap.start_position_lat, lon=lap.start_position_long
        )
        self.end_location: LocationStat = LocationStat(
            lat=lap.end_position_lat, lon=lap.end_position_long
        )


class FitDistanceActivity(FitActivity):
    __slots__ = (
        "start_location", "end_location", "total_distance", "speed", "cadence",
        "altitude", "total_strides", "laps"
    )

    def __init__(self, fit_file_path: str, model: DistanceActivityModel) -> None:
        super().__init__(fit_file_path, model)

        altitudes: list[float] = [
            record.enhanced_altitude or record.altitude for record in model.records
            if record.enhanced_altitude or record.altitude
        ]

        self.total_distance: float | None = model.session.total_distance
        self.speed: DoubleStat = DoubleStat(
            max=model.session.enhanced_max_speed or model.session.max_speed,
            avg=model.session.enhanced_avg_speed or model.session.avg_speed
        )
        self.cadence: DoubleStat = DoubleStat(
            max=model.session.max_cadence or model.session.max_running_cadence,
            avg=model.session.avg_cadence or model.session.avg_running_cadence
        )
        self.altitude: AltitudeStat = AltitudeStat(
            max=max(altitudes) if altitudes else None,
            min=min(altitudes) if altitudes else None,
            gain=model.session.total_ascent,
            loss=model.session.total_descent
        )
        self.laps: list[FitLap] = (
            [FitLap(lap) for lap in model.laps] if model.laps else []
        )
        self.total_strides: int | None = model.session.total_strides
        self.start_location: LocationStat = LocationStat(
            lat=model.session.start_position_lat,
            lon=model.session.start_position_long
        )
        self.end_location: LocationStat = LocationStat(
            lat=model.session.end_position_lat,
            lon=model.session.end_position_long
        )


class FitClimb:
    __slots__ = ("time", "split_type", "hr", "total_calories", "difficulty", "result")

    def __init__(self, split: SplitModel) -> None:
        self.time: TimeStat = TimeStat(
            timestamp=split.start_time,
            start_time=split.start_time,
            elapsed=split.total_elapsed_time,
            timer=split.total_timer_time
        )
        self.split_type: SplitType = (
            split.split_type if split.split_type in list(SplitType)
            else SplitType.UNKNOWN
        )
        self.hr: DoubleStat = DoubleStat(max=split.max_hr, avg=split.avg_hr)
        self.total_calories: int = split.total_calories
        self.difficulty: int = split.difficulty
        self.result: ClimbResult = (
            ClimbResult.COMPLETED if split.result == 3 else (
                ClimbResult.ATTEMPTED if split.result == 2 else ClimbResult.DISCARDED
            )
        )


class FitClimbActivity(FitActivity):
    __slots__ = ("climbs",)

    def __init__(self, fit_file_path: str, model: ClimbActivityModel) -> None:
        super().__init__(fit_file_path, model)
        self.climbs: list[FitClimb] = [FitClimb(s) for s in model.splits]


class FitSet:
    __slots__ = ("order", "exercise", "time", "repetitions", "weight", "weight_unit")

    def __init__(self, set_: SetModel) -> None:
        self.order: int = set_.message_index or 0
        self.exercise: str | None = set_.category[0] if set_.category else set_.set_type
        self.time: TimeStat = TimeStat(
            timestamp=set_.timestamp,
            start_time=set_.start_time,
            elapsed=set_.duration,
            timer=set_.duration
        )
        self.repetitions: int | None = set_.repetitions
        self.weight: float | None = set_.weight
        self.weight_unit: str | None = set_.weight_display_unit


class FitSetActivity(FitActivity):
    __slots__ = ("sets",)

    def __init__(self, fit_file_path: str, model: SetActivityModel) -> None:
        super().__init__(fit_file_path, model)
        self.sets: list[FitSet] = [FitSet(s) for s in model.sets]


class FitTransitionActivity:
    __slots__ = (
        "name", "sport", "sub_sport", "time", "hr", "temperature", "total_calories"
    )

    def __init__(self, session: SessionModel) -> None:
        self.name: str = session.sport
        self.sport: str = session.sport
        self.sub_sport: str = session.sub_sport
        self.time: TimeStat = TimeStat(
            timestamp=session.timestamp,
            start_time=session.start_time,
            elapsed=session.total_elapsed_time,
            timer=session.total_timer_time
        )
        self.hr: DoubleStat = DoubleStat(
            max=session.max_heart_rate,
            avg=session.avg_heart_rate
        )
        self.temperature: TripleStat = TripleStat(
            max=session.max_temperature,
            min=session.min_temperature,
            avg=session.avg_temperature
        )
        self.total_calories: float | None = session.total_calories


class FitMultisportActivity(FitResult):
    __slots__ = ("model", "fit_activities",)

    def __init__(self, fit_file_path: str, model: MultisportActivityModel) -> None:
        super().__init__(fit_file_path)
        self.model: MultisportActivityModel = model
        self.fit_activities: list[FitActivity] = []

        for session in model.sessions:
            if session.sport == TRANSITION_SPORT:
                activity = FitTransitionActivity(session)
            elif is_distance_sport(session.sport):
                session_records, session_laps = filter_by_session(
                    session, model.records, model.laps
                )
                activity = FitDistanceActivity(
                    fit_file_path,
                    DistanceActivityModel(
                        session=session,
                        workout=None,
                        workout_steps=[],
                        records=session_records,
                        laps=session_laps
                    )
                )
            else:
                activity = FitActivity(fit_file_path, ActivityModel(session=session))
            self.fit_activities.append(activity)


class FitSteps:
    __slots__ = ("steps", "distance", "calories")

    def __init__(self, monitoring: MonitoringModel) -> None:
        self.steps = monitoring.steps or 0
        self.distance = monitoring.distance or 0
        self.calories = monitoring.active_calories or monitoring.calories or 0


class FitHeartRate:
    __slots__ = ("heart_rate", "datetime_utc", "datetime_local")

    def __init__(self, monitoring_date: date, monitoring: MonitoringModel) -> None:
        self.heart_rate: int | None = monitoring.heart_rate
        self.datetime_utc: datetime | None = combine_date_and_seconds(
            monitoring_date, monitoring.timestamp_16
        ) if monitoring.timestamp_16 is not None else None
        self.datetime_local: datetime | None = (
            try_to_compute_local_datetime(self.datetime_utc)
            if self.datetime_utc is not None else None
        )


class FitActivityIntensity:
    __slots__ = (
        "moderate_minutes", "vigorous_minutes", "datetime_utc", "datetime_local"
    )

    def __init__(self, monitoring_date: date, monitoring: MonitoringModel) -> None:
        self.moderate_minutes: int = monitoring.moderate_activity_minutes or 0
        self.vigorous_minutes: int = monitoring.vigorous_activity_minutes or 0
        self.datetime_utc: datetime | None = combine_date_and_seconds(
            monitoring_date, monitoring.timestamp_16
        ) if monitoring.timestamp_16 is not None else None
        self.datetime_local: datetime | None = (
            try_to_compute_local_datetime(self.datetime_utc)
            if self.datetime_utc is not None else None
        )


class FitMonitor(FitResult):
    __slots__ = (
        "model", "datetime_utc", "datetime_local", "monitoring_date",
        "metabolic_calories", "activities", "active_calories", "steps",
        "heart_rates", "activity_intensities", "respiration_rates",
        "stress_levels"
    )

    def __init__(self, fit_file_path: str, model: MonitorModel) -> None:
        super().__init__(fit_file_path)
        self.model: MonitorModel = model
        self.datetime_utc: datetime = self.model.monitoring_info.timestamp
        self.datetime_local: datetime = try_to_compute_local_datetime(self.datetime_utc)
        self.monitoring_date: date = date(
            year=self.datetime_local.year,
            month=self.datetime_local.month,
            day=self.datetime_local.day
        )
        self.metabolic_calories: int = (
            self.model.monitoring_info.resting_metabolic_rate or 0
        )
        self.activities: list[str] = self._activity_types_as_str()
        self.active_calories: int = sum([
            (value if value is not None else 0)
            for m in self.model.monitorings if m.is_daily_log()
            for value in [m.active_calories, m.calories] if value is not None
        ])
        self.steps: list[FitSteps] = [
            FitSteps(m) for m in self.model.monitorings
            if m.is_daily_log() and m.steps is not None
        ]
        self.heart_rates: list[FitHeartRate] = [
            FitHeartRate(self.monitoring_date, m) for m in self.model.monitorings
            if m.heart_rate is not None and m.timestamp_16 is not None
        ]
        self.activity_intensities: list[FitActivityIntensity] = [
            FitActivityIntensity(self.monitoring_date, m) for m in self.model.monitorings
            if m.timestamp_16 is not None and (
                    m.moderate_activity_minutes is not None or
                    m.vigorous_activity_minutes is not None
            )
        ]
        self.respiration_rates: list[RespirationRateModel] = self.model.respiration_rates
        self.stress_levels: list[StressLevelModel] = self.model.stress_levels

    @property
    def total_steps(self) -> int:
        return sum([steps.steps for steps in self.steps])

    @property
    def total_calories(self) -> int:
        return self.metabolic_calories + self.active_calories

    def _activity_types_as_str(self) -> list[str]:
        if self.model.monitoring_info.activity_type is None:
            return []

        activity_types: list[str] = []
        for at in self.model.monitoring_info.activity_type:
            if at in ACTIVITY_TYPES:
                activity_types.append(ACTIVITY_TYPES[at])
            elif type(at) is str:
                activity_types.append(at)
            else:
                activity_types.append(ACTIVITY_TYPE_UNKNOWN)

        return activity_types


class FitHrv(FitResult):
    __slots__ = (
        "model", "datetime_utc", "weekly_average", "last_night_average",
        "last_night_5_min_high", "baseline_low_upper", "baseline_balanced_lower",
        "baseline_balanced_upper", "values"
    )

    def __init__(self, fit_file_path: str, model: HrvModel) -> None:
        super().__init__(fit_file_path)
        self.model: HrvModel = model
        self.datetime_utc: datetime = model.summary.timestamp
        self.weekly_average: float = model.summary.weekly_average
        self.last_night_average: float = model.summary.last_night_average
        self.last_night_5_min_high: float = model.summary.last_night_5_min_high
        self.baseline_low_upper: float = model.summary.baseline_low_upper
        self.baseline_balanced_lower: float = model.summary.baseline_balanced_lower
        self.baseline_balanced_upper: float = model.summary.baseline_balanced_upper
        self.values: list[HrvValueModel] = model.values

    @property
    def status(self) -> str:
        if isinstance(self.model.summary.status, int):
            return (
                HRV_STATUS[self.model.summary.status]
                if self.model.summary.status in HRV_STATUS
                else HRV_STATUS[0]
            )
        return self.model.summary.status


class FitSleepLevel:
    __slots__ = ("datetime_utc", "datetime_local", "level")

    def __init__(self, level_model: SleepLevelModel) -> None:
        self.datetime_utc: datetime = level_model.timestamp
        self.datetime_local: datetime = try_to_compute_local_datetime(self.datetime_utc)
        self.level: str = (
            level_model.sleep_level if isinstance(level_model.sleep_level, str) else (
                SLEEP_LEVEL[level_model.sleep_level]
                if level_model.sleep_level in SLEEP_LEVEL else SLEEP_LEVEL[0]
            )
        )


class FitSleep(FitResult):
    __slots__ = (
        "model", "dates", "levels", "combined_awake_score", "awake_time_score",
        "awakenings_count_score", "deep_sleep_score", "sleep_duration_score",
        "light_sleep_score", "overall_sleep_score", "sleep_quality_score",
        "sleep_recovery_score", "rem_sleep_score", "sleep_restlessness_score",
        "awakenings_count", "interruptions_score", "average_stress_during_sleep"
    )

    def __init__(self, fit_file_path: str, model: SleepModel) -> None:
        super().__init__(fit_file_path)
        self.model: SleepModel = model
        self.levels: list[FitSleepLevel] = [
            FitSleepLevel(level) for level in self.model.levels
            if level.sleep_level is not None
        ]
        self.dates = sorted(set([level.datetime_utc.date() for level in self.levels]))
        self.combined_awake_score: int = model.assessment.combined_awake_score
        self.awake_time_score: int = model.assessment.awake_time_score
        self.awakenings_count_score: int = model.assessment.awakenings_count_score
        self.deep_sleep_score: int = model.assessment.deep_sleep_score
        self.sleep_duration_score: int = model.assessment.sleep_duration_score
        self.light_sleep_score: int = model.assessment.light_sleep_score
        self.overall_sleep_score: int = model.assessment.overall_sleep_score
        self.sleep_quality_score: int = model.assessment.sleep_quality_score
        self.sleep_recovery_score: int = model.assessment.sleep_recovery_score
        self.rem_sleep_score: int = model.assessment.rem_sleep_score
        self.sleep_restlessness_score: int = model.assessment.sleep_restlessness_score
        self.awakenings_count: int = model.assessment.awakenings_count
        self.interruptions_score: int = model.assessment.interruptions_score
        self.average_stress_during_sleep: float = (
            model.assessment.average_stress_during_sleep
        )
