from abc import ABC


class FitResult(ABC):
    pass


class FitError(FitResult):
    __slots__ = ("fit_file_path", "errors")

    def __init__(self, fit_file_Path: str, errors: list[Exception]) -> None:
        self.fit_file_path = fit_file_Path
        self.errors = errors
