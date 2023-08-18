from ..parse import FitActivityParser
from ..exceptions import NotSupportedFitFileException


def test_fit_file_not_supported():
    fit_parse = FitActivityParser()
    fit_parse.parse("tests/files/settings.fit")

    errors = fit_parse.get_errors()

    assert fit_parse.has_errors()
    assert len(errors) > 0
    assert [e for e in errors if isinstance(e, NotSupportedFitFileException)]


def test_fit_file_not_fit_file():
    fit_parse = FitActivityParser()
    fit_parse.parse("tests/files/settings.csv")

    errors = fit_parse.get_errors()

    assert fit_parse.has_errors()
    assert len(errors) > 0
    assert [e for e in errors if isinstance(e, RuntimeError)]
