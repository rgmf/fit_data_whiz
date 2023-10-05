from datetime import datetime

from fit_data_whiz.utils.date_utils import try_to_compute_local_datetime


def is_daily_log(utc_dt: datetime) -> bool:
    """Check if datetime is a daily log.

    In monitoring messages the timestamp must align to logging interval, for
    example, time must be 00:00:00 for daily log.

    It returns True if utc_dt has 00:00:00 time in the local datetime.
    """
    local_dt: datetime = try_to_compute_local_datetime(utc_dt)
    return local_dt.hour == 0 and local_dt.minute == 0 and local_dt.second == 0
