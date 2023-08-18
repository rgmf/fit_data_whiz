from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import namedtuple
from typing import List

from .messages import (
    FitSessionMesg,
    FitRecordMesg,
    FitLapMesg,
    FitSplitMesg,
    FitSetMesg,
    FitWorkoutMesg,
    FitWorkoutStepMesg
)
from .definitions import SplitType, ClimbResult, TRANSITION_SPORT, is_distance_sport


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
        return ([], [])
    if not isinstance(session.total_timer_time, int | float):
        return ([], [])

    datetime_from: datetime = session.start_time
    datetime_to: datetime = session.start_time + timedelta(seconds=session.total_timer_time)

    return (
        [r for r in records if datetime_from <= r.timestamp <= datetime_to],
        [l for l in laps if datetime_from <= l.timestamp <= datetime_to]
    )


@dataclass
class FitLap:
    message_index: int
    timestamp: int
    time: TimeStat
    total_distance: float
    speed: TripleStat
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

    def __init__(self, workout: FitWorkoutMesg, steps: FitWorkoutStepMesg):
        self.name = workout.wkt_name
        self.sport = workout.sport
        self.steps = [FitWorkoutStep(s) for s in steps]


@dataclass
class FitActivity:
    name: str
    sport: str
    sub_sport: str
    time: TimeStat
    hr: DoubleStat
    temperature: TripleStat
    total_calories: int
    workout: FitWorkout

    def __init__(
            self,
            session: FitSessionMesg,
            workout: FitWorkoutMesg = None,
            workout_steps: List[FitWorkoutStepMesg] = None
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
            workout: FitWorkoutMesg = None,
            workout_steps: List[FitWorkoutStepMesg] = None
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
            workout: FitWorkoutMesg = None,
            workout_steps: List[FitWorkoutStepMesg] = None
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
            workout: FitWorkoutMesg = None,
            workout_steps: List[FitWorkoutStepMesg] = None
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
