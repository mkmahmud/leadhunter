from datetime import UTC, date, datetime, time, timedelta

from app.schemas.leads import DateRange


def resolve_date_range(date_range: DateRange) -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    today_start = datetime.combine(now.date(), time.min, tzinfo=UTC)
    if date_range.preset == "today":
        return today_start, now
    if date_range.preset == "last_24_hours":
        return now - timedelta(hours=24), now
    if date_range.preset == "last_3_days":
        return now - timedelta(days=3), now
    if date_range.preset == "last_7_days":
        return now - timedelta(days=7), now
    if date_range.preset == "last_30_days":
        return now - timedelta(days=30), now
    start = _date_to_start(date_range.start_date) if date_range.start_date else now - timedelta(days=7)
    end = _date_to_end(date_range.end_date) if date_range.end_date else now
    return start, end


def _date_to_start(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=UTC)


def _date_to_end(value: date) -> datetime:
    return datetime.combine(value, time.max, tzinfo=UTC)
