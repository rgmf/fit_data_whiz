from datetime import datetime, tzinfo, timedelta


def try_to_compute_local_datetime(dt_utc: datetime) -> datetime:
    """
    Try to compute the local datetime from dt_utc and return the local datetime
    or dt_utc itself.
    """
    info: tzinfo | None = datetime.now().astimezone().tzinfo
    local_timedelta: timedelta | None = info.utcoffset(dt_utc) if info else timedelta(seconds=0)
    datetime_local: datetime = dt_utc + (local_timedelta if local_timedelta else timedelta(seconds=0))
    return datetime_local
