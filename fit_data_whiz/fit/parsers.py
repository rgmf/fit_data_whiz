from abc import ABC, abstractmethod

from pydantic import ValidationError, BaseModel

from fit_data_whiz.fit.results import (
    FitActivity, FitMonitor, FitHrv, FitSleep, FitResult, FitError
)
from fit_data_whiz.fit.definitions import (
    SPORTS, is_distance_sport, is_climb_sport, is_set_sport
)
from fit_data_whiz.fit.exceptions import (
    NotFitMessageFoundException,
    NotSupportedFitSportException,
    UnexpectedDataMessageException,
    FitMessageValidationException
)
from fit_data_whiz.fit.models import (
    FitMultisportActivity,
    FitDistanceActivity,
    FitClimbActivity,
    FitSetActivity,
    FitMonitorModel,
    FitHrvModel,
    FitSleepModel,
    FitWorkout,
    FitWorkoutStep,
    FitSession,
    FitRecord,
    FitLap,
    FitSplit,
    FitSet,
    FitMonitoringInfo,
    FitMonitoring,
    FitMonitoringHrData,
    FitStressLevel,
    FitRespirationRate,
    FitHrvStatusSummary,
    FitHrvValue,
    FitSleepAssessment,
    FitSleepLevel
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

        try:
            return FitActivity(self._fit_file_path, self._build_model())
        except ValidationError as error:
            return FitError(self._fit_file_path, [FitMessageValidationException(error)])
        except NotSupportedFitSportException as error:
            return FitError(self._fit_file_path, [error])

    def _supported_sport_in_session(self) -> bool:
        supported: list[str] = [n for k, v in SPORTS.items() for n in v.keys()]
        not_supported: list[str] = [
            s for s in self._messages["SESSION"] if s.sport not in supported
        ]

        if not_supported:
            return False
        return True

    def _build_model(self) -> BaseModel:
        """Try to build the model.

        :return: the BaseModel built upon messages.

        :raise: NotSupportedFitSportException if the sport in the message is
                not supported.
        """
        if len(self._messages["SESSION"]) > 1:
            return FitMultisportActivity(
                sessions=[FitSession(**s) for s in self._messages["SESSION"]],
                records=[FitRecord(**r) for r in self._messages["RECORD"]],
                laps=[FitLap(**lap) for lap in self._messages["LAP"]]
            )

        workout: FitWorkout | None = (
            FitWorkout(**self._messages["WORKOUT"][0])
            if self._messages["WORKOUT"] else None
        )
        workout_steps: list[FitWorkoutStep] = [
            FitWorkoutStep(**mesg) for mesg in self._messages["WORKOUT_STEP"]
        ]
        session: FitSession = FitSession(**self._messages["SESSION"][0])

        if is_distance_sport(session.sport):
            return FitDistanceActivity(
                session=session,
                records=[FitRecord(**r) for r in self._messages["RECORD"]],
                laps=[FitLap(**lap) for lap in self._messages["LAP"]],
                workout=workout,
                workout_steps=workout_steps
            )

        if is_climb_sport(session.sport):
            return FitClimbActivity(
                session=session,
                splits=[FitSplit(**s) for s in self._messages["SPLIT"]],
                workout=workout,
                workout_steps=workout_steps
            )

        if is_set_sport(session.sport):
            return FitSetActivity(
                session=session,
                sets=[FitSet(**s) for s in self._messages["SET"]],
                workout=workout,
                workout_steps=workout_steps
            )

        raise NotSupportedFitSportException(session.sport, session.sub_sport)


class FitMonitoringParser(FitAbstractParser):
    def __init__(self, fit_file_path: str, messages: dict[str, list]) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list] = messages

    def parse(self) -> FitMonitor | FitError:
        if "MONITORING_INFO" not in self._messages:
            return FitError(
                self._fit_file_path,
                [NotFitMessageFoundException("monitoring_info")]
            )

        if len(self._messages["MONITORING_INFO"]) != 1:
            return FitError(
                self._fit_file_path,
                [
                    UnexpectedDataMessageException(
                        "monitoring_info",
                        "expected one message per file but got "
                        f"{len(self._messages['MONITORING_INFO'])} messages"
                    )
                ]
            )

        try:
            monitoring_info: FitMonitoringInfo = FitMonitoringInfo(
                **self._messages["MONITORING_INFO"][0]
            )
            monitorings: list[FitMonitoring] = (
                [FitMonitoring(**message) for message in self._messages["MONITORING"]]
                if "MONITORING" in self._messages else []
            )
            hr_datas: list[FitMonitoringHrData] = (
                [
                    FitMonitoringHrData(**message)
                    for message in self._messages["MONITORING_HR_DATA"]
                ]
                if "MONITORING_HR_DATA" in self._messages else []
            )
            stress_levels: list[FitStressLevel] = (
                [FitStressLevel(**message) for message in self._messages["STRESS_LEVEL"]]
                if "STRESS_LEVEL" in self._messages else []
            )
            respiration_rates: list[FitRespirationRate] = (
                [
                    FitRespirationRate(**message)
                    for message in self._messages["RESPIRATION_RATE"]
                ]
                if "RESPIRATION_RATE" in self._messages else []
            )
        except ValidationError as error:
            return FitError(self._fit_file_path, [FitMessageValidationException(error)])

        return FitMonitor(
            self._fit_file_path,
            FitMonitorModel(
                monitoring_info=monitoring_info,
                monitorings=monitorings,
                hr_datas=hr_datas,
                stress_levels=stress_levels,
                respiration_rates=respiration_rates
            )
        )


class FitHrvParser(FitAbstractParser):
    def __init__(self, fit_file_path: str, messages: dict[str, list]) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list] = messages

    def parse(self) -> FitHrv | FitError:
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
                        "expected one message per file but got "
                        f"{len(self._messages['HRV_STATUS_SUMMARY'])} messages"
                    )
                ]
            )

        try:
            summary = FitHrvStatusSummary(**self._messages["HRV_STATUS_SUMMARY"][0])
            values = [FitHrvValue(**v) for v in self._messages["HRV_VALUE"]]
            model = FitHrvModel(summary=summary, values=values)
            return FitHrv(self._fit_file_path, model)
        except ValidationError as error:
            return FitError(self._fit_file_path, [FitMessageValidationException(error)])


class FitSleepParser(FitAbstractParser):
    def __init__(self, fit_file_path: str, messages: dict[str, list]) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list] = messages

    def parse(self) -> FitResult:
        if "SLEEP_ASSESSMENT" not in self._messages:
            return FitError(
                self._fit_file_path,
                [NotFitMessageFoundException("sleep_assessment")]
            )

        if "SLEEP_LEVEL" not in self._messages:
            return FitError(
                self._fit_file_path,
                [NotFitMessageFoundException("sleep_level")]
            )

        if len(self._messages["SLEEP_ASSESSMENT"]) != 1:
            return FitError(
                self._fit_file_path,
                [
                    UnexpectedDataMessageException(
                        "sleep_assessment",
                        "expected one message per file but got "
                        f"{len(self._messages['SLEEP_ASSESSMENT'])} messages"
                    )
                ]
            )

        try:
            assessment = FitSleepAssessment(**self._messages["SLEEP_ASSESSMENT"][0])
            levels = [FitSleepLevel(**level) for level in self._messages["SLEEP_LEVEL"]]
            model = FitSleepModel(assessment=assessment, levels=levels)
            return FitSleep(self._fit_file_path, model)
        except ValidationError as error:
            return FitError(self._fit_file_path, [FitMessageValidationException(error)])
