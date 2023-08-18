from typing import List

from garmin_fit_sdk import Decoder, Stream, Profile

from .custom_logging import get_logger, initialize
from .definitions import (
    MESSAGES, SPORTS, is_distance_sport, is_climb_sport, is_set_sport
)
from .exceptions import (
    FitException,
    NotSupportedFitFileException,
    NotFitMessageFoundException,
    NotSupportedFitSportException
)
from .messages import (
    FitWorkoutMesg, FitWorkoutStepMesg, FitSessionMesg
)
from .stats import (
    FitActivity,
    FitDistanceActivity,
    FitSetActivity,
    FitClimbActivity,
    FitMultisportActivity
)
from .custom_logging import LogLevel


# Initialize logger system.
initialize(LogLevel.DEBUG)


class FitParser:
    """Parser for fit files.

    It pre-parses all fit files and uses the right parser to parse the fit
    file.

    Not all fit files are supported, so the parse can result in errors.
    """
    pass


class FitActivityParser:
    """Parser for fit activity files.

    It parses a fit file using the Garmin SDK library and build a FitActivity
    object that contains all stats from the FIT file.

    Also, it handles the errors that save into an array of errors.
    """

    def __init__(self) -> None:
        self._messages: dict[str, list] = {name: [] for name in MESSAGES}
        self._errors: list[Exception] = []
        self._has_critical_error: bool = False
        self._activity: FitActivity | None = None

    def parse(self, file_path: str) -> None:
        self._load_all_messages(file_path)
        if self.has_errors():
            return

        self._check_supported_fit()
        if self.has_errors():
            return

        self._activity = self._build_activity()

    def _load_all_messages(self, file_path: str) -> None:
        stream = Stream.from_file(file_path)
        decoder = Decoder(stream)
        _, decoder_errors = decoder.read(mesg_listener=self._mesg_listener)
        self._errors.extend(decoder_errors)

    def _check_supported_fit(self) -> None:
        self._check_file_id_exists()
        self._check_exists_session_with_supported_sport()

    def _check_file_id_exists(self) -> None:
        if not self._messages["FILE_ID"]:
            self._errors.append(NotFitMessageFoundException("file_id"))

    def _check_exists_session_with_supported_sport(self) -> None:
        if not self._messages["SESSION"]:
            self._errors.append(NotFitMessageFoundException("session"))
            return

        supported: list[str] = [n for k, v in SPORTS.items() for n in v.keys()]
        not_supported: list[str] = [
            s for s in self._messages["SESSION"] if s.sport not in supported
        ]

        if not_supported:
            self._errors.append(
                NotSupportedFitSportException(not_supported[0].sport, not_supported[0].sub_sport)
            )

    def _build_activity(self) -> FitActivity | None:
        workout_mesg: FitWorkoutMesg = (
            self._messages["WORKOUT"][0] if self._messages["WORKOUT"] else None
        )
        workout_step_mesgs: List[FitWorkoutStepMesg] = self._messages["WORKOUT_STEP"]

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

        return None

    def has_errors(self) -> bool:
        return len(self._errors) != 0

    def get_errors(self) -> list[Exception]:
        return self._errors

    def get_messages(self) -> dict[str, list]:
        return self._messages

    def get_activity(self) -> FitActivity | None:
        return self._activity

    def _mesg_listener(self, mesg_num: int, mesg: dict) -> None:
        if self._has_critical_error:
            return
        for profile_name, profile_num in Profile["mesg_num"].items():
            self._add_message_if_supported(profile_name, profile_num, mesg_num, mesg)

    def _add_message_if_supported(
            self, profile_name: str, profile_num: int, mesg_num: int, mesg_data: dict
    ) -> None:
        if mesg_num != profile_num or profile_name not in MESSAGES:
            return

        try:
            message_object = MESSAGES[profile_name]["mesg_cls"](mesg_data)
            self._messages[profile_name].append(message_object)
        except NotSupportedFitFileException as error:
            self._errors.append(error)
            self._has_critical_error = True
            get_logger(__name__).exception(error)
        except FitException as error:
            self._errors.append(error)
            get_logger(__name__).exception(error)
        except Exception as error:
            self._errors.append(error)
            self._has_critical_error = True
            get_logger(__name__).exception(
                f"An exception was launched, maybe for a dev error (bug): {error}"
            )
