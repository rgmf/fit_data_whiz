from abc import ABC, abstractmethod

from pydantic import ValidationError, BaseModel

from fit_data_whiz.fit.results import (
    FitActivity,
    FitDistanceActivity,
    FitClimbActivity,
    FitSetActivity,
    FitMultisportActivity,
    FitMonitor,
    FitHrv,
    FitSleep,
    FitResult,
    FitError
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
    MultisportActivityModel,
    DistanceActivityModel,
    ClimbActivityModel,
    SetActivityModel,
    MonitorModel,
    HrvModel,
    SleepModel,
    WorkoutModel,
    WorkoutStepModel,
    SessionModel,
    MonitoringInfoModel,
    MonitoringModel,
    MonitoringHrDataModel,
    StressLevelModel,
    RespirationRateModel,
    HrvStatusSummaryModel,
    HrvValueModel
)


class FitAbstractParser(ABC):
    @abstractmethod
    def __init__(self, fit_file_path: str, messages: dict[str, list[BaseModel]]) -> None:
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

    def __init__(self, fit_file_path: str, messages: dict[str, list[BaseModel]]) -> None:
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
            return self._build_activity(self._fit_file_path)
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

    def _build_activity(self, fit_file_path: str) -> FitActivity:
        """Try to build the activity model.

        :return: the BaseModel built upon messages.

        :raise: NotSupportedFitSportException if the sport in the message is
                not supported.
        """
        if len(self._messages["SESSION"]) > 1:
            model = MultisportActivityModel(
                sessions=[session_model for session_model in self._messages["SESSION"]],
                records=[record_model for record_model in self._messages["RECORD"]],
                laps=[lap_model for lap_model in self._messages["LAP"]]
            )
            return FitMultisportActivity(fit_file_path, model)

        workout: WorkoutModel | None = (
            self._messages["WORKOUT"][0] if self._messages["WORKOUT"] else None
        )
        workout_steps: list[WorkoutStepModel] = self._messages["WORKOUT_STEP"]
        session: SessionModel = self._messages["SESSION"][0]

        if is_distance_sport(session.sport):
            model = DistanceActivityModel(
                session=session,
                records=[r for r in self._messages["RECORD"]],
                laps=[lap for lap in self._messages["LAP"]],
                workout=workout,
                workout_steps=workout_steps
            )
            return FitDistanceActivity(fit_file_path, model)

        if is_climb_sport(session.sport):
            model = ClimbActivityModel(
                session=session,
                splits=[s for s in self._messages["SPLIT"]],
                workout=workout,
                workout_steps=workout_steps
            )
            return FitClimbActivity(fit_file_path, model)

        if is_set_sport(session.sport):
            model = SetActivityModel(
                session=session,
                sets=[s for s in self._messages["SET"]],
                workout=workout,
                workout_steps=workout_steps
            )
            return FitSetActivity(fit_file_path, model)

        raise NotSupportedFitSportException(session.sport, session.sub_sport)


class FitMonitoringParser(FitAbstractParser):
    def __init__(self, fit_file_path: str, messages: dict[str, list[BaseModel]]) -> None:
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
            monitoring_info: MonitoringInfoModel = self._messages["MONITORING_INFO"][0]
            monitorings: list[MonitoringModel] = (
                [message for message in self._messages["MONITORING"]]
                if "MONITORING" in self._messages else []
            )
            hr_datas: list[MonitoringHrDataModel] = (
                [message for message in self._messages["MONITORING_HR_DATA"]]
                if "MONITORING_HR_DATA" in self._messages else []
            )
            stress_levels: list[StressLevelModel] = (
                [message for message in self._messages["STRESS_LEVEL"]]
                if "STRESS_LEVEL" in self._messages else []
            )
            respiration_rates: list[RespirationRateModel] = (
                [message for message in self._messages["RESPIRATION_RATE"]]
                if "RESPIRATION_RATE" in self._messages else []
            )
        except ValidationError as error:
            return FitError(self._fit_file_path, [FitMessageValidationException(error)])

        return FitMonitor(
            self._fit_file_path,
            MonitorModel(
                monitoring_info=monitoring_info,
                monitorings=monitorings,
                hr_datas=hr_datas,
                stress_levels=stress_levels,
                respiration_rates=respiration_rates
            )
        )


class FitHrvParser(FitAbstractParser):
    def __init__(self, fit_file_path: str, messages: dict[str, list[BaseModel]]) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list[BaseModel]] = messages

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
            summary: HrvStatusSummaryModel = self._messages["HRV_STATUS_SUMMARY"][0]
            values: list[HrvValueModel] = self._messages["HRV_VALUE"]
            model = HrvModel(summary=summary, values=values)
            return FitHrv(self._fit_file_path, model)
        except ValidationError as error:
            return FitError(self._fit_file_path, [FitMessageValidationException(error)])


class FitSleepParser(FitAbstractParser):
    def __init__(self, fit_file_path: str, messages: dict[str, list[BaseModel]]) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list] = messages

    def parse(self) -> FitSleep | FitError:
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
            assessment = self._messages["SLEEP_ASSESSMENT"][0]
            levels = [level for level in self._messages["SLEEP_LEVEL"]]
            model = SleepModel(assessment=assessment, levels=levels)
            return FitSleep(self._fit_file_path, model)
        except ValidationError as error:
            return FitError(self._fit_file_path, [FitMessageValidationException(error)])
