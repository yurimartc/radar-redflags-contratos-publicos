from datetime import date

from src.ingestion.windows import incremental_window, monthly_windows


def test_incremental_window_uses_reprocess_days() -> None:
    window = incremental_window(reprocess_days=7, run_date=date(2026, 2, 28))
    assert window.start.isoformat() == "2026-02-21"
    assert window.end.isoformat() == "2026-02-28"


def test_monthly_windows_returns_expected_month_boundaries() -> None:
    windows = list(monthly_windows(months_back=2, run_date=date(2026, 2, 28)))
    assert windows[0].start.isoformat() == "2026-02-01"
    assert windows[0].end.isoformat() == "2026-02-28"
    assert windows[1].start.isoformat() == "2026-01-01"
    assert windows[1].end.isoformat() == "2026-01-31"
