import logging
import sys
from enum import IntEnum

APP_ID = "fit_data_whiz"


class LogLevel(IntEnum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


def initialize(loglevel: LogLevel):
    """Initialize logger and return the logger.

    Arguments:
    loglevel -- a LogLevel indicating the level of the logging:
                5 -> logging.CRITICAL
                4 -> logging.ERROR
                3 -> logging.WARNING
                2 -> logging.INFO
                1 -> logging.DEBUG
    """
    # Create logger.
    logger = logging.getLogger(APP_ID)
    logger.setLevel(0 if loglevel not in (5, 4, 3, 2, 1) else loglevel * 10)

    # Create console handler.
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(loglevel)

    # Create formatter and add it to the handler.
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handlers to the logger.
    logger.addHandler(handler)

    return logger


def get_logger(name):
    """Return the logger object."""
    return logging.getLogger(APP_ID + "." + name)
