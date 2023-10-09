from enum import Enum, StrEnum

from fit_data_whiz.fit.models import (
    FileIdModel,
    LapModel,
    RecordModel,
    SessionModel,
    SetModel,
    SplitModel,
    WorkoutModel,
    WorkoutStepModel,
    MonitoringHrDataModel,
    StressLevelModel,
    RespirationRateModel,
    MonitoringInfoModel,
    MonitoringModel,
    HrvStatusSummaryModel,
    HrvValueModel,
    SleepLevelModel,
    SleepAssessmentModel
)


# All messages supported.
# Each message (whose key is in the FIT SDK Profile) has:
# - The name you can find in the FIT SDK Profile.
# - The number you can find in the FIT SDK Profile.
# - The class message to build the message from garmin_fit_sdk library.
MESSAGES = {
    "FILE_ID": {
        "name": "FILE_ID",
        "num": 0,
        "model_cls": FileIdModel
    },

    # ACTIVITY DEFINITIONS
    # "SPORT": {
    #     "name": "SPORT",
    #     "num": 12,
    #     "model_cls": FitSportMesg
    # },
    # "TRAINING_FILE": {
    #     "name": "TRAINING_FILE",
    #     "num": 72,
    #     "model_cls": None
    # },
    "WORKOUT": {
        "name": "WORKOUT",
        "num": 26,
        "model_cls": WorkoutModel
    },
    "WORKOUT_STEP": {
        "name": "WORKOUT_STEP",
        "num": 27,
        "model_cls": WorkoutStepModel
    },
    "RECORD": {
        "name": "RECORD",
        "num": 20,
        "model_cls": RecordModel
    },
    "LAP": {
        "name": "LAP",
        "num": 19,
        "model_cls": LapModel
    },
    "SET": {
        "name": "SET",
        "num": 225,
        "model_cls": SetModel
    },
    "SPLIT": {
        "name": "SPLIT",
        "num": 312,
        "model_cls": SplitModel
    },
    # "TIME_IN_ZONE": {
    #     "name": "TIME_IN_ZONE",
    #     "num": 216,
    #     "model_cls": None
    # },
    "SESSION": {
        "name": "SESSION",
        "num": 18,
        "model_cls": SessionModel
    },
    # "ACTIVITY": {
    #     "name": "ACTIVITY",
    #     "num": 34,
    #     "model_cls": None
    # }

    # MONITOR DEFINITIONS
    "MONITORING_INFO": {
        "name": "MONITORING_INFO",
        "num": 103,
        "model_cls": MonitoringInfoModel
    },
    "MONITORING": {
        "name": "MONITORING",
        "num": 55,
        "model_cls": MonitoringModel
    },
    "MONITORING_HR_DATA": {
        "name": "MONITORING_HR_DATA",
        "num": 211,
        "model_cls": MonitoringHrDataModel
    },
    "STRESS_LEVEL": {
        "name": "STRESS_LEVEL",
        "num": 227,
        "model_cls": StressLevelModel
    },
    "RESPIRATION_RATE": {
        "name": "RESPIRATION_RATE",
        "num": 297,
        "model_cls": RespirationRateModel
    },

    # SLEEP AND HRV DEFINITIONS
    "SLEEP_LEVEL": {
        "name": "SLEEP_LEVEL",
        "num": 275,
        "model_cls": SleepLevelModel
    },
    "SLEEP_ASSESSMENT": {
        "name": "SLEEP_ASSESSMENT",
        "num": 346,
        "model_cls": SleepAssessmentModel
    },
    "HRV_STATUS_SUMMARY": {
        "name": "HRV_STATUS_SUMMARY",
        "num": 370,
        "model_cls": HrvStatusSummaryModel
    },
    "HRV_VALUE": {
        "name": "HRV_VALUE",
        "num": 371,
        "model_cls": HrvValueModel
    }
}


# Split's type.
class SplitType(StrEnum):
    ASCENT_SPLIT = "ascent_split"
    DESCENT_SPLIT = "descent_split"
    INTERVAL_ACTIVE = "interval_active"
    INTERVAL_REST = "interval_rest"
    INTERVAL_WARMUP = "interval_warmup"
    INTERVAL_COOLDOWN = "interval_cooldown"
    INTERVAL_RECOVERY = "interval_recovery"
    INTERVAL_OTHER = "interval_other"
    CLIMB_ACTIVE = "climb_active"
    CLIMB_REST = "climb_rest"
    SURF_ACTIVE = "surf_active"
    RUN_ACTIVE = "run_active"
    RUN_REST = "run_rest"
    WORKOUT_ROUND = "workout_round"
    RWD_RUN = "rwd_run"
    RWD_WALK = "rwd_walk"
    WINDSURF_ACTIVE = "windsurf_active"
    RWD_STAND = "rwd_stand"
    TRANSITION = "transition"
    SKI_LIFT_SPLIT = "ski_lift_split"
    SKI_RUN_SPLIT = "ski_run_split"
    UNKNOWN = "unknown"


# Split's result.
class ClimbResult(Enum):
    COMPLETED = 1
    ATTEMPTED = 2
    DISCARDED = 3


# Training's excercise categories.
class ExerciseCategories(StrEnum):
    BENCH_PRESS = "bench_press"
    CALF_RAISE = "calf_raise"
    CARDIO = "cardio"
    CARRY = "carry"
    CHOP = "chop"
    CORE = "core"
    CRUNCH = "crunch"
    CURL = "curl"
    DEADLIFT = "deadlift"
    FLYE = "flye"
    HIP_RAISE = "hip_raise"
    HIP_STABILITY = "hip_stability"
    HIP_SWING = "hip_swing"
    HYPEREXTENSION = "hyperextension"
    LATERAL_RAISE = "lateral_raise"
    LEG_CURL = "leg_curl"
    LEG_RAISE = "leg_raise"
    LUNGE = "lunge"
    OLYMPIC_LIFT = "olympic_lift"
    PLANK = "plank"
    PLYO = "plyo"
    PULL_UP = "pull_up"
    PUSH_UP = "push_up"
    ROW = "row"
    SHOULDER_PRESS = "shoulder_press"
    SHOULDER_STABILITY = "shoulder_stability"
    SHRUG = "shrug"
    SIT_UP = "sit_up"
    SQUAT = "squat"
    TOTAL_BODY = "total_body"
    TRICEPS_EXTENSION = "triceps_extension"
    WARM_UP = "warm_up"
    RUN = "run"
    UNKNOWN = "unknown"
    REST = "rest"


# Supported sports organized by categories.
# Each category contains a list of sports, each with a list of sub-sport.
# The values used for 'sport' and 'sub-sport' are from the FIT standard (Profile).
DISTANCE_CATEGORY = "distance"
SET_CATEGORY = "set"
CLIMB_CATEGORY = "climbing"
MULTISPORT_CATEGORY = "multisport"

RUNNING_SPORT = "running"
WALKING_SPORT = "walking"
HIKING_SPORT = "hiking"
CYCLING_SPORT = "cycling"

ROCK_CLIMBING_SPORT = "rock_climbing"
TRAINING_SPORT = "training"

TRANSITION_SPORT = "transition"

GENERIC_SUB_SPORT = "generic"
TRAIL_SUB_SPORT = "trail"
ROAD_SUB_SPORT = "road"
MOUNTAIN_SUB_SPORT = "mountain"
BOULDERING_SUB_SPORT = "bouldering"
STRENGTH_TRAINING_SUB_SPORT = "strength_training"

SPORTS = {
    DISTANCE_CATEGORY: {
        RUNNING_SPORT: [GENERIC_SUB_SPORT, TRAIL_SUB_SPORT],
        WALKING_SPORT: [GENERIC_SUB_SPORT],
        HIKING_SPORT: [GENERIC_SUB_SPORT],
        CYCLING_SPORT: [GENERIC_SUB_SPORT, ROAD_SUB_SPORT, MOUNTAIN_SUB_SPORT]
    },
    SET_CATEGORY: {
        TRAINING_SPORT: [GENERIC_SUB_SPORT, STRENGTH_TRAINING_SUB_SPORT]
    },
    CLIMB_CATEGORY: {
        ROCK_CLIMBING_SPORT: [GENERIC_SUB_SPORT, BOULDERING_SUB_SPORT]
    },
    MULTISPORT_CATEGORY: {
        TRANSITION_SPORT: [GENERIC_SUB_SPORT]
    }
}

ACTIVITY_TYPES = {
    0: "generic",
    1: "running",
    2: "cycling",
    3: "transition",
    4: "fitness_equipment",
    5: "swimming",
    6: "walking",
    8: "sedentary",
    254: "all"
}
ACTIVITY_TYPE_UNKNOWN = "unknown"

HRV_STATUS = {
    0: "none",
    1: "poor",
    2: "low",
    3: "unbalanced",
    4: "balanced"
}

SLEEP_LEVEL = {
    0: "unmeasurable",
    1: "awake",
    2: "light",
    3: "deep",
    4: "rem"
}


def is_distance_sport(sport: str) -> bool:
    return sport in SPORTS[DISTANCE_CATEGORY]


def is_climb_sport(sport: str) -> bool:
    return sport in SPORTS[CLIMB_CATEGORY]


def is_set_sport(sport: str) -> bool:
    return sport in SPORTS[SET_CATEGORY]
