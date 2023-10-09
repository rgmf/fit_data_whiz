from fit_data_whiz.whiz import FitDataWhiz
from fit_data_whiz.fit.exceptions import NotSupportedFitFileException
from fit_data_whiz.fit.results import FitError


# def test_show_monitor_information() -> None:
#     import os
#     from ..parsers.results.result import FitError
#     from ..parsers.results.stats import FitHrv, FitSleep
#     for dirpath, dirnames, filenames in os.walk("/home/roman/garmin_monitor"):
#         for filename in [name for name in filenames if name.lower().endswith(".fit")]:
#             print(os.path.join(dirpath, filename))
#             fit_file_path: str = os.path.join(dirpath, filename)

#             fit_parse = FitParser(fit_file_path)
#             monitor = fit_parse.parse()
#             if isinstance(monitor, FitError):
#                 print(monitor.errors)
#             elif isinstance(monitor, FitHrv):
#                 print(f"last_night_average: {monitor.last_night_average}")
#             elif isinstance(monitor, FitSleep):
#                 print(f"overall_sleep_score: {monitor.overall_sleep_score}")
#             elif isinstance(monitor, FitMonitor):
#                 print(f"steps: {monitor.fit_steps.steps if monitor.fit_steps is not None else None}")
#                 print(f"calories: {monitor.total_calories}")
#                 if monitor.activity_intensities:
#                     moderate = sum([i.moderate for i in monitor.activity_intensities])
#                     vigorous = sum([i.vigorous for i in monitor.activity_intensities])
#                     print(f"Moderate: {moderate}")
#                     print(f"Vigorous: {vigorous}")

#             print()
#             print()


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
