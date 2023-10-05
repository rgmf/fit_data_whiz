from pydantic import ValidationError


class FitException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NotSupportedFitFileException(FitException):
    def __init__(self, file_type: str) -> None:
        super().__init__(f"The FIT file '{file_type}' is not supported")


class NotSupportedFitSportException(FitException):
    def __init__(self, sport: str, sub_sport: str) -> None:
        super().__init__(f"The FIT file describes a not supported sport: {sport} ({sub_sport})")


class NotFitMessageFoundException(FitException):
    def __init__(self, message: str) -> None:
        super().__init__(f"Not found '{message}' into FIT file")


class UncompleteMessageException(FitException):
    def __init__(self, message_name: str, values: list[str]) -> None:
        super().__init__(
            f"Uncomplete data to build '{message_name}' "
            f"message: {', '.join([str(n) for n in values])}"
        )


class UnexpectedDataMessageException(FitException):
    def __init__(self, message_name: str, description: str) -> None:
        super().__init__(f"Unexpected data for '{message_name}' message: {description}")


class FitMessageValidationException(FitException):
    def __init__(self, error: ValidationError) -> None:
        super().__init__(f"Validation error: {str(error)}")
