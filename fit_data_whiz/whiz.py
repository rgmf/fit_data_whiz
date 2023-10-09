import os

from pydantic import BaseModel
from garmin_fit_sdk import Decoder, Stream, Profile

from fit_data_whiz.logging.logging import get_logger, initialize, LogLevel
from fit_data_whiz.fit.definitions import MESSAGES
from fit_data_whiz.fit.exceptions import (
    FitException, NotFitMessageFoundException, NotSupportedFitFileException
)
from fit_data_whiz.fit.results import FitResult, FitError
from fit_data_whiz.fit.parsers import (
    FitActivityParser, FitMonitoringParser, FitHrvParser, FitSleepParser
)

# Initialize logger system.
initialize(LogLevel.DEBUG)


# All FIT files supported.
FIT_FILE_SUPPORTED = {
    "activity": {
        "name": "activity",
        "num": 4,
        "parser_cls": FitActivityParser,
        "description": "Activity FIT file: running, cycling..."
    },
    "monitoring_a": {
        "name": "monitoring_a",
        "num": 15,
        "parser_cls": FitMonitoringParser,
        "description": ""
    },
    "monitoring_b": {
        "name": "monitoring_b",
        "num": 32,
        "parser_cls": FitMonitoringParser,
        "description": "Monitoring FIT file with steps, stress level... data"
    },
    68: {
        "name": 68,
        "num": 68,
        "parser_cls": FitHrvParser,
        "description": "FIT file with HRV data"
    },
    49: {
        "name": 49,
        "num": 49,
        "parser_cls": FitSleepParser,
        "description": "FIT file with sleep data"
    }
}


class FitReader:
    def __init__(self, root_folder: str) -> None:
        self.fit_results: dict[str, FitResult] = {}

        for dirpath, dirnames, filenames in os.walk(root_folder):
            for filename in [name for name in filenames if name.lower().endswith(".fit")]:
                print(os.path.join(dirpath, filename))
                fit_file_path: str = os.path.join(dirpath, filename)
                fit_parser = FitDataWhiz(fit_file_path)
                fit_result: FitResult = fit_parser.parse()
                self.fit_results[fit_file_path] = fit_result


class FitDataWhiz:
    """Main class for parsing fit files.

    It pre-parses all fit files and uses the right parser to parse the fit
    file.

    It makes generic checking because not all fit files are supported, so the
    parse can result in errors.

    To use this class, build an object using the constructor that only needs the
    path of the file to be parsed.

    Once you have the object of this class then call parse method and it returns
    a FitResult that can be a FitError, FitActivity or whatever fit result
    depending on the type of the fit file.
    """
    def __init__(self, fit_file_path: str) -> None:
        self._fit_file_path: str = fit_file_path
        self._messages: dict[str, list[BaseModel]] = {name: [] for name in MESSAGES}
        self._errors: list[Exception] = []
        self._has_critical_error: bool = False

    def parse(self) -> FitResult:
        stream = Stream.from_file(self._fit_file_path)
        decoder = Decoder(stream)
        _, decoder_errors = decoder.read(mesg_listener=self._mesg_listener)
        self._errors.extend(decoder_errors)

        if len(self._errors) > 0:
            return FitError(self._fit_file_path, self._errors)

        if not self._messages["FILE_ID"]:
            self._errors.append(NotFitMessageFoundException("file_id"))
            return FitError(self._fit_file_path, self._errors)

        file_type: str = self._messages["FILE_ID"][0].file_type

        if file_type not in FIT_FILE_SUPPORTED.keys():
            self._errors.append(NotSupportedFitFileException(file_type))
            return FitError(self._fit_file_path, self._errors)

        parser = FIT_FILE_SUPPORTED[file_type]["parser_cls"](
            fit_file_path=self._fit_file_path,
            messages=self._messages
        )
        return parser.parse()

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
            data_dict = {str(k): v for k, v in mesg_data.items()}
            model = MESSAGES[profile_name]["model_cls"](**data_dict)
            self._messages[profile_name].append(model)
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
