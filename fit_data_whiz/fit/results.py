from abc import ABC

from pydantic import BaseModel


class FitResult(ABC):
    __slots__ = ("fit_file_path",)

    def __init__(self, fit_file_path: str) -> None:
        self.fit_file_path = fit_file_path


class FitError(FitResult):
    __slots__ = ("errors",)

    def __init__(self, fit_file_Path: str, errors: list[Exception]) -> None:
        super().__init__(fit_file_Path)
        self.errors = errors


class FitActivity(FitResult):
    __slots__ = ("model",)

    def __init__(self, fit_file_path: str, model: BaseModel) -> None:
        super().__init__(fit_file_path)
        self.model = model


class FitMonitor(FitResult):
    __slots__ = ("model",)

    def __init__(self, fit_file_path: str, model: BaseModel) -> None:
        super().__init__(fit_file_path)
        self.model = model


class FitHrv(FitResult):
    __slots__ = ("model",)

    def __init__(self, fit_file_path: str, model: BaseModel) -> None:
        super().__init__(fit_file_path)
        self.model = model


class FitSleep(FitResult):
    __slots__ = ("model",)

    def __init__(self, fit_file_path: str, model: BaseModel) -> None:
        super().__init__(fit_file_path)
        self.model = model
