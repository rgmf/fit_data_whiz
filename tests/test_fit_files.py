from fit_data_whiz.whiz import FitDataWhiz
from fit_data_whiz.fit.exceptions import NotSupportedFitFileException
from fit_data_whiz.fit.results import FitError


def test_fit_file_not_supported() -> None:
    whiz = FitDataWhiz("tests/files/settings.fit")
    result = whiz.parse()
    assert isinstance(result, FitError)
    assert [e for e in result.errors if isinstance(e, NotSupportedFitFileException)]


def test_fit_file_not_fit_file() -> None:
    whiz = FitDataWhiz("tests/files/settings.csv")
    result = whiz.parse()
    assert isinstance(result, FitError)
    assert [e for e in result.errors if isinstance(e, RuntimeError)]
