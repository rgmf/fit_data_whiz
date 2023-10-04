from abc import ABC, abstractmethod

from .results.result import FitResult, FitError
from .results.stats import (
    FitActivity,
    FitMultisportActivity,
    FitDistanceActivity,
    FitClimbActivity,
    FitSetActivity,
    FitMonitoring,
    FitMonitoringInfo,
    FitStressLevel,
    FitHrData,
    FitRespirationRate,
    FitMonitor,
    FitHrv
)
from ..definitions import SPORTS, is_distance_sport, is_climb_sport, is_set_sport
from ..exceptions import (
    NotFitMessageFoundException,
    NotSupportedFitSportException,
    UnexpectedDataMessageException
)
from ..messages import (
    FitWorkoutMesg,
    FitWorkoutStepMesg,
    FitSessionMesg
)


class FitAbstractParser(ABC):
    @abstractmethod
    def __init__(self, fit_file_path: str, messages: dict[str, list]) -> None:
        pass

    @abstractmethod
    def parse(self) -> FitResult:
        pass


class FitActivityParser(FitAbstractParser):
    """Parser for fit activity files.

    It parses a fit file using the Garmin SDK library and build a FitActivity
    object that contains all stats from the FIT file.

    Also, it handles the errors that save into an array of errors.
    """

    def __init__(self, fit_file_path: str, messages: dict[str, list]) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list] = messages

    def parse(self) -> FitActivity | FitError:
        if not self._messages["SESSION"]:
            return FitError(self._fit_file_path, [NotFitMessageFoundException("session")])

        if not self._supported_sport_in_session():
            return FitError(
                self._fit_file_path,
                [
                    NotSupportedFitSportException(
                        self._messages["SESSION"][0].sport,
                        self._messages["SESSION"][0].sub_sport
                    )
                ]
            )

        return self._build_activity()

    def _supported_sport_in_session(self) -> bool:
        supported: list[str] = [n for k, v in SPORTS.items() for n in v.keys()]
        not_supported: list[str] = [
            s for s in self._messages["SESSION"] if s.sport not in supported
        ]

        if not_supported:
            return False
        return True

    def _build_activity(self) -> FitActivity | FitError:
        workout_mesg: FitWorkoutMesg = (
            self._messages["WORKOUT"][0] if self._messages["WORKOUT"] else None
        )
        workout_step_mesgs: list[FitWorkoutStepMesg] = self._messages["WORKOUT_STEP"]

        if len(self._messages["SESSION"]) > 1:
            return FitMultisportActivity(
                sessions=self._messages["SESSION"],
                records=self._messages["RECORD"],
                laps=self._messages["LAP"]
            )

        session_mesg: FitSessionMesg = self._messages["SESSION"][0]

        if is_distance_sport(session_mesg.sport):
            return FitDistanceActivity(
                session=session_mesg,
                records=self._messages["RECORD"],
                laps=self._messages["LAP"],
                workout=workout_mesg,
                workout_steps=workout_step_mesgs
            )

        if is_climb_sport(session_mesg.sport):
            return FitClimbActivity(
                session=session_mesg,
                splits=self._messages["SPLIT"],
                workout=workout_mesg,
                workout_steps=workout_step_mesgs
            )

        if is_set_sport(session_mesg.sport):
            return FitSetActivity(
                session=session_mesg,
                sets=self._messages["SET"],
                workout=workout_mesg,
                workout_steps=workout_step_mesgs
            )

        return FitError(
            self._fit_file_path,
            [
                NotSupportedFitSportException(session_mesg.sport, session_mesg.sub_sport)
            ]
        )


class FitMonitoringParser(FitAbstractParser):
    def __init__(self, fit_file_path: str, messages: dict[str, list]) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list] = messages

    def parse(self) -> FitResult:
        if "MONITORING_INFO" not in self._messages:
            return FitError(self._fit_file_path, [NotFitMessageFoundException("monitoring_info")])

        if len(self._messages["MONITORING_INFO"]) != 1:
            return FitError(
                self._fit_file_path,
                [
                    UnexpectedDataMessageException(
                        "monitoring_info",
                        f"expected one message per file but got {len(self._messages['MONITORING_INFO'])} messages"
                    )
                ]
            )

        monitoring_info: FitMonitoringInfo = FitMonitoringInfo(self._messages["MONITORING_INFO"][0])
        monitorings: list[FitMonitoring] = (
            [FitMonitoring(message) for message in self._messages["MONITORING"]]
            if "MONITORING" in self._messages else []
        )
        hr_datas: list[FitHrData] = (
            [FitHrData(message) for message in self._messages["MONITORING_HR_DATA"]]
            if "MONITORING_HR_DATA" in self._messages else []
        )
        stress_levels: list[FitStressLevel] = (
            [FitStressLevel(message) for message in self._messages["STRESS_LEVEL"]]
            if "STRESS_LEVEL" in self._messages else []
        )
        respiration_rates: list[FitRespirationRate] = (
            [FitRespirationRate(message) for message in self._messages["RESPIRATION_RATE"]]
            if "RESPIRATION_RATE" in self._messages else []
        )

        return FitMonitor(monitoring_info, monitorings, hr_datas, stress_levels, respiration_rates)


class FitHrvParser(FitAbstractParser):
    def __init__(self, fit_file_path: str, messages: dict[str, list]) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list] = messages

    def parse(self) -> FitResult:
        if "HRV_STATUS_SUMMARY" not in self._messages:
            return FitError(self._fit_file_path, [NotFitMessageFoundException("hrv_status_summary")])

        if "HRV_VALUE" not in self._messages:
            return FitError(self._fit_file_path, [NotFitMessageFoundException("hrv_value")])

        if len(self._messages["HRV_STATUS_SUMMARY"]) != 1:
            return FitError(
                self._fit_file_path,
                [
                    UnexpectedDataMessageException(
                        "hrv_status_summary",
                        f"expected one message per file but got {len(self._messages['HRV_STATUS_SUMMARY'])} messages"
                    )
                ]
            )

        return FitHrv(self._messages["HRV_STATUS_SUMMARY"][0], self._messages["HRV_VALUE"])


class FitSleepParser(FitAbstractParser):
    def __init__(self, fit_file_path: str, messages: dict[str, list]) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list] = messages

    def parse(self) -> FitResult:
       pass
