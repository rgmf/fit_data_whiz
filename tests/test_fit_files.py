from ..parse import FitParser
from ..exceptions import NotSupportedFitFileException
from ..parsers.results.result import FitResult, FitError


def test_fit_file_not_supported() -> None:
    fit_parse = FitParser("tests/files/settings.fit")
    result: FitResult = fit_parse.parse()
    assert isinstance(result, FitError)
    assert [e for e in result.errors if isinstance(e, NotSupportedFitFileException)]


def test_fit_file_not_fit_file() -> None:
    fit_parse = FitParser("tests/files/settings.csv")
    result: FitResult = fit_parse.parse()
    assert isinstance(result, FitError)
    assert [e for e in result.errors if isinstance(e, NotSupportedFitFileException)]
