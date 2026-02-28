from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterator, Literal

RunMode = Literal["backfill", "incremental"]


@dataclass(frozen=True)
class DateWindow:
    start: date
    end: date



def _month_bounds(year: int, month: int) -> DateWindow:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return DateWindow(start=start, end=end)



def monthly_windows(months_back: int, run_date: date | None = None) -> Iterator[DateWindow]:
    if months_back <= 0:
        return
    base = run_date or datetime.utcnow().date()
    year, month = base.year, base.month
    for _ in range(months_back):
        yield _month_bounds(year, month)
        month -= 1
        if month == 0:
            month = 12
            year -= 1



def incremental_window(reprocess_days: int, run_date: date | None = None) -> DateWindow:
    base = run_date or datetime.utcnow().date()
    start = base - timedelta(days=max(reprocess_days, 1))
    end = base
    return DateWindow(start=start, end=end)
