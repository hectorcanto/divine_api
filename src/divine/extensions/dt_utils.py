from datetime import (
    datetime,
    timedelta,
    UTC,
)


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


def future_dt(delta_minutes: int = 15) -> datetime:
    return datetime.now(tz=UTC) + timedelta(minutes=delta_minutes)
