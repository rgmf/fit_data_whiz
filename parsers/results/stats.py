from datetime import datetime, timedelta, date, time
from dataclasses import dataclass, field
from collections import namedtuple
from typing import List
from .result import FitResult

from ...utils.date_utils import try_to_compute_local_datetime
from ...utils.garmin_sdk_utils import is_daily_log
from ...messages import (
    FitSessionMesg,
    FitRecordMesg,
    FitLapMesg,
    FitSplitMesg,
    FitSetMesg,
    FitWorkoutMesg,
    FitWorkoutStepMesg,
    FitMonitoringMesg,
    FitMonitoringHrDataMesg,
    FitMonitoringInfoMesg,
    FitStressLevelMesg,
    FitRespirationRateMesg
)
from ...definitions import (
    SplitType,
    ClimbResult,
    TRANSITION_SPORT,
    is_distance_sport,
    ACTIVITY_TYPES,
    ACTIVITY_TYPE_UNKNOWN
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
    session: FitSessionMesg,
    records: List[FitRecordMesg],
    laps: List[FitLapMesg]
) -> RecordsAndLaps:
    if not isinstance(session.start_time, datetime):
        return RecordsAndLaps([], [])
    if not isinstance(session.total_timer_time, int | float):
        return RecordsAndLaps([], [])

    datetime_from: datetime = session.start_time
    datetime_to: datetime = session.start_time + timedelta(seconds=session.total_timer_time)

    return RecordsAndLaps(
        [record for record in records if datetime_from <= record.timestamp <= datetime_to],
        [lap for lap in laps if datetime_from <= lap.timestamp <= datetime_to]
    )


@dataclass
class FitLap:
    message_index: int
    timestamp: int
    time: TimeStat
    total_distance: float
    speed: DoubleStat
    hr: DoubleStat
    altitude: AltitudeStat
    total_calories: int
    cadence: DoubleStat
    total_strides: int
    start_location: LocationStat
    end_location: LocationStat

    def __init__(self, lap: FitLapMesg):
        self.message_index = lap.message_index
        self.timestamp = lap.timestamp
        self.time = TimeStat(
            timestamp=lap.timestamp,
            start_time=lap.start_time,
            elapsed=lap.total_elapsed_time,
            timer=lap.total_timer_time
        )
        self.total_distance = lap.total_distance
        self.speed = DoubleStat(
            max=lap.enhanced_max_speed or lap.max_speed,
            avg=lap.enhanced_avg_speed or lap.avg_speed
        )
        self.hr = DoubleStat(max=lap.max_heart_rate, avg=lap.avg_heart_rate)
        self.altitude = AltitudeStat(
            max=lap.enhanced_max_altitude or lap.max_altitude,
            min=lap.enhanced_min_altitude or lap.min_altitude,
            gain=lap.total_ascent,
            loss=lap.total_descent
        )
        self.total_calories = lap.total_calories
        self.cadence = DoubleStat(
            max=lap.max_cadence or lap.max_running_cadence,
            avg=lap.avg_cadence or lap.avg_running_cadence
        )
        self.total_strides = lap.total_strides or lap.total_strokes
        self.start_location = LocationStat(lat=lap.start_position_lat, lon=lap.start_position_long)
        self.end_location = LocationStat(lat=lap.end_position_lat, lon=lap.end_position_long)


@dataclass
class FitSet:
    order: int
    excercise: str
    time: TimeStat
    repetitions: int
    weight: float
    weight_unit: str

    def __init__(self, set_mesg: FitSetMesg):
        self.order = set_mesg.message_index
        self.excercise = set_mesg.category[0] if set_mesg.category else set_mesg.set_type
        self.time = TimeStat(
            timestamp=set_mesg.timestamp,
            start_time=set_mesg.start_time,
            elapsed=set_mesg.duration,
            timer=set_mesg.duration
        )
        self.repetitions = set_mesg.repetitions
        self.weight = set_mesg.weight
        self.weight_unit = set_mesg.weight_display_unit


@dataclass
class FitClimb:
    time: TimeStat
    split_type: SplitType
    hr: DoubleStat
    total_calories: int
    difficulty: int
    result: ClimbResult

    def __init__(self, split: FitSplitMesg):
        self.time = TimeStat(
            timestamp=split.start_time,
            start_time=split.start_time,
            elapsed=split.total_elapsed_time,
            timer=split.total_timer_time
        )
        self.split_type = (
            split.split_type if split.split_type in list(SplitType) else SplitType.UNKNOWN
        )
        self.hr = DoubleStat(max=split.max_hr, avg=split.avg_hr)
        self.total_calories = split.total_calories
        self.difficulty = split.difficulty
        self.result = (
            ClimbResult.COMPLETED if split.result == 3 else (
                ClimbResult.ATTEMPTED if split.result == 2 else ClimbResult.DISCARDED
            )
        )


@dataclass
class FitWorkoutStep:
    message_index: int

    def __init__(self, step: FitWorkoutStepMesg):
        self.message_index = step.message_index


@dataclass
class FitWorkout:
    name: str
    sport: str
    steps: List[FitWorkoutStep]

    def __init__(self, workout: FitWorkoutMesg, steps: List[FitWorkoutStepMesg]):
        self.name = workout.wkt_name
        self.sport = workout.sport
        self.steps = [FitWorkoutStep(s) for s in steps]


@dataclass
class FitActivity(FitResult):
    name: str
    sport: str
    sub_sport: str
    time: TimeStat
    hr: DoubleStat
    temperature: TripleStat
    total_calories: int
    workout: FitWorkout | None

    def __init__(
            self,
            session: FitSessionMesg,
            workout: FitWorkoutMesg | None = None,
            workout_steps: List[FitWorkoutStepMesg] = []
    ):
        self.name = session.sport
        self.sport = session.sport
        self.sub_sport = session.sub_sport
        self.time = TimeStat(
            timestamp=session.timestamp,
            start_time=session.start_time,
            elapsed=session.total_elapsed_time,
            timer=session.total_timer_time
        )
        self.hr = DoubleStat(max=session.max_heart_rate, avg=session.avg_heart_rate)
        self.temperature = TripleStat(
            max=session.max_temperature,
            min=session.min_temperature,
            avg=session.avg_temperature
        )
        self.total_calories = session.total_calories
        self.workout = FitWorkout(workout, workout_steps) if workout else None


@dataclass
class FitDistanceActivity(FitActivity):
    total_distance: float
    speed: DoubleStat
    cadence: DoubleStat
    altitude: AltitudeStat
    laps: List[FitLap]
    total_strides: int
    start_location: LocationStat
    end_location: LocationStat

    def __init__(
            self,
            session: FitSessionMesg,
            records: List[FitRecordMesg],
            laps: List[FitLapMesg],
            workout: FitWorkoutMesg | None = None,
            workout_steps: List[FitWorkoutStepMesg] = []
    ):
        super().__init__(session, workout, workout_steps)

        altitudes: list[float] = [
            record.enhanced_altitude or record.altitude for record in records
            if record.enhanced_altitude or record.altitude
        ]

        self.total_distance = session.total_distance
        self.speed = DoubleStat(
            max=session.enhanced_max_speed or session.max_speed,
            avg=session.enhanced_avg_speed or session.avg_speed
        )
        self.cadence = DoubleStat(
            max=session.max_cadence or session.max_running_cadence,
            avg=session.avg_cadence or session.avg_running_cadence
        )
        self.altitude = AltitudeStat(
            max=max(altitudes) if altitudes else None,
            min=min(altitudes) if altitudes else None,
            gain=session.total_ascent,
            loss=session.total_descent
        )
        self.laps = [FitLap(lap) for lap in laps] if laps else []
        self.total_strides = session.total_strides
        self.start_location = LocationStat(
            lat=session.start_position_lat,
            lon=session.start_position_long
        )
        self.end_location = LocationStat(
            lat=session.end_position_lat,
            lon=session.end_position_long
        )


@dataclass
class FitClimbActivity(FitActivity):
    climbs: List[FitClimb]

    def __init__(
            self,
            session: FitSessionMesg,
            splits: List[FitSplitMesg],
            workout: FitWorkoutMesg | None = None,
            workout_steps: List[FitWorkoutStepMesg] = []
    ):
        super().__init__(session, workout, workout_steps)
        self.climbs = [FitClimb(s) for s in splits]


@dataclass
class FitSetActivity(FitActivity):
    sets: List[FitSet]

    def __init__(
            self,
            session: FitSessionMesg,
            sets: List[FitSetMesg],
            workout: FitWorkoutMesg | None = None,
            workout_steps: List[FitWorkoutStepMesg] = []
    ):
        super().__init__(session, workout, workout_steps)
        self.sets = [FitSet(s) for s in sets]


@dataclass
class FitTransitionActivity(FitActivity):
    def __init__(self, session: FitSessionMesg):
        super().__init__(session)
        self.name = "Transition"


@dataclass
class FitMultisportActivity:
    fit_activities: List[FitActivity]

    def __init__(
        self, sessions: List[FitSessionMesg], records: List[FitRecordMesg], laps: List[FitLapMesg]
    ):
        self.fit_activities = []

        for session in sessions:
            if session.sport == TRANSITION_SPORT:
                self.fit_activities.append(FitTransitionActivity(session))
            elif is_distance_sport(session.sport):
                session_records, session_laps = filter_by_session(session, records, laps)
                self.fit_activities.append(
                    FitDistanceActivity(
                        session=session,
                        records=session_records,
                        laps=session_laps
                    )
                )
            else:
                self.fit_activities.append(FitActivity(session=session))


@dataclass
class FitMonitoringInfo:
    datetime_utc: datetime
    monitoring_day: date
    activities: list[str]
    resting_metabolic_rate: int | None = None

    def __init__(self, mesg: FitMonitoringInfoMesg):
        self.datetime_utc = mesg.timestamp

        datetime_local: datetime = try_to_compute_local_datetime(self.datetime_utc)
        self.monitoring_day = date(
            year=datetime_local.year,
            month=datetime_local.month,
            day=datetime_local.day
        )

        self.activities = mesg.activity_type if mesg.activity_type else []
        self.resting_metabolic_rate = mesg.resting_metabolic_rate


@dataclass
class FitMonitoring:
    datetime_utc: datetime | None
    monitoring_day: date | None
    seconds_from_datetime_utc: int | None
    calories: int | None
    active_calories: int | None
    distance: float | None
    cycles: float | None
    steps: int | None
    strokes: int | None
    active_time: float | None     # in seconds
    activity_type: str | None
    activity_subtype: str | None
    activity_level: str | None    # (low, medium, high)
    heart_rate: int | None
    intensity: int | None
    duration_min: int | None      # in minutes
    duration: int | None          # in seconds
    ascent: int | None
    descent: int | None
    moderate_activity_minutes: int | None
    vigorous_activity_minutes: int | None

    def __init__(self, mesg: FitMonitoringMesg):
        self.datetime_utc = mesg.timestamp

        if self.datetime_utc is not None:
            datetime_local: datetime = try_to_compute_local_datetime(self.datetime_utc)
            self.monitoring_day = date(
                year=datetime_local.year,
                month=datetime_local.month,
                day=datetime_local.day
            )
            if is_daily_log(self.datetime_utc):
                self.monitoring_day -= timedelta(days=1)
        else:
            self.monitoring_day = None

        self.seconds_from_datetime_utc= mesg.timestamp_16

        self.calories = mesg.calories
        self.active_calories = mesg.active_calories
        self.distance = mesg.distance
        self.cycles = mesg.cycles
        self.steps = mesg.steps
        self.strokes = mesg.strokes
        self.active_time = mesg.active_time
        self.activity_type = str(mesg.activity_type) if mesg.activity_type else None
        self.activity_subtype = str(mesg.activity_subtype) if mesg.activity_subtype else None
        self.activity_level = str(mesg.activity_level) if mesg.activity_level else None
        self.heart_rate = mesg.heart_rate
        self.intensity = mesg.intensity
        self.duration_min = mesg.duration_min
        self.duration = mesg.duration
        self.ascent = mesg.ascent
        self.descent = mesg.descent
        self.moderate_activity_minutes = mesg.moderate_activity_minutes
        self.vigorous_activity_minutes = mesg.vigorous_activity_minutes

    def is_daily_log(self) -> bool:
        return (
            self.monitoring_day is not None and
            self.datetime_utc is not None and
            is_daily_log(self.datetime_utc)
        )

    def is_heart_rate(self) -> bool:
        return self.heart_rate is not None and self.seconds_from_datetime_utc is not None

    def has_steps(self) -> bool:
        return self.steps is not None and self.steps != 0


@dataclass
class FitHrData:
    datetime_utc: datetime
    resting_heart_rate: int
    current_day_resting_heart_rate: int

    def __init__(self, mesg: FitMonitoringHrDataMesg):
        self.datetime_utc = mesg.timestamp
        self.resting_heart_rate = mesg.resting_heart_rate
        self.current_day_resting_heart_rate = mesg.current_day_resting_heart_rate

    def is_daily_log(self) -> bool:
        return is_daily_log(self.datetime_utc)


@dataclass
class FitStressLevel:
    datetime_utc: datetime
    value: int

    def __init__(self, mesg: FitStressLevelMesg):
        self.datetime_utc = mesg.stress_level_time
        self.value = mesg.stress_level_value


@dataclass
class FitRespirationRate:
    datetime_utc: datetime
    respiration_rate: float

    def __init__(self, mesg: FitRespirationRateMesg):
        self.datetime_utc = mesg.timestamp
        self.respiration_rate = mesg.respiration_rate

    def is_valid(self) -> bool:
        return self.respiration_rate > 0.0


@dataclass
class FitSteps:
    monitorings: list[FitMonitoring]
    steps: int
    distance: float
    calories: int

    def __init__(self, fit_monitorings: list[FitMonitoring]) -> None:
        self.monitorings = fit_monitorings
        self.steps = sum([m.steps for m in fit_monitorings if m.steps])
        self.distance = sum([m.distance for m in fit_monitorings if m.distance])
        self.calories = sum([
            (value if value is not None else 0)
            for m in fit_monitorings
            for value in [m.active_calories, m.calories]
            if value is not None
        ])


@dataclass
class FitHeartRate:
    utc_datetime: datetime
    hr: int

    def __init__(self, day_date: date, seconds_from_datetime_utc: int, heart_rate: int) -> None:
        self.utc_datetime = (
            datetime.combine(day_date, time.min) + timedelta(seconds=seconds_from_datetime_utc)
        )
        self.hr = heart_rate


@dataclass
class FitMonitor(FitResult):
    monitoring_info: FitMonitoringInfo
    monitorings: list[FitMonitoring] = field(default_factory=list)
    fit_steps: FitSteps | None = None
    fit_heart_rates: list[FitHeartRate] = field(default_factory=list)
    resting_heart_rate: int | None = None
    respiration_rates: list[FitRespirationRate] = field(default_factory=list)
    stress_levels: list[FitStressLevel] = field(default_factory=list)

    def __init__(
            self,
            monitoring_info: FitMonitoringInfo,
            monitorings: list[FitMonitoring],
            hr_datas: list[FitHrData],
            stress_levels: list[FitStressLevel],
            respiration_rates: list[FitRespirationRate]
    ) -> None:
        self.monitoring_info = monitoring_info
        self.monitorings = monitorings
        self.respiration_rates = respiration_rates
        self.stress_levels = stress_levels

        filtered_steps_monitoring: list[FitMonitoring] = [
            m for m in self.monitorings if m.is_daily_log() and m.has_steps()
        ]
        if filtered_steps_monitoring:
            self.fit_steps = FitSteps(filtered_steps_monitoring)

        self.fit_heart_rates = [
            FitHeartRate(self.day_date, m.seconds_from_datetime_utc, m.heart_rate)
            for m in self.monitorings
            if m.is_heart_rate() and
            m.seconds_from_datetime_utc is not None and
            m.heart_rate is not None
        ]

        daily_log_hr_datas = [hd for hd in hr_datas if hd.is_daily_log()]
        self.resting_heart_rate = (
            daily_log_hr_datas[0].resting_heart_rate
            if daily_log_hr_datas else None
        )

    @property
    def day_date(self) -> date:
        return self.monitoring_info.monitoring_day

    @property
    def metabolic_calories(self) -> int:
        return (
            self.monitoring_info.resting_metabolic_rate
            if self.monitoring_info.resting_metabolic_rate else 0
        )

    @property
    def active_calories(self) -> int:
        return sum([
            (value if value is not None else 0)
            for m in self.monitorings if m.is_daily_log()
            for value in [m.active_calories, m.calories] if value is not None
        ])

    @property
    def total_calories(self) -> int:
        return self.metabolic_calories + self.active_calories
