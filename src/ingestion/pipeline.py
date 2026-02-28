from __future__ import annotations

import argparse
import json
from datetime import datetime

from src.ingestion.config import from_env
from src.ingestion.metadata import MetadataStore
from src.ingestion.pncp_client import PNCPClient
from src.ingestion.storage import MinioRawStorage
from src.ingestion.windows import incremental_window, monthly_windows


def _batch_id(mode: str) -> str:
    return f"{mode}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"


def _run_window(mode: str, start_date, end_date) -> None:
    cfg = from_env()
    batch_id = _batch_id(mode)
    client = PNCPClient(base_url=cfg.pncp_base_url, timeout_seconds=cfg.pncp_timeout_seconds)
    storage = MinioRawStorage(
        endpoint=cfg.minio_endpoint,
        access_key=cfg.minio_access_key,
        secret_key=cfg.minio_secret_key,
        bucket=cfg.minio_bucket,
    )
    metadata = MetadataStore(
        host=cfg.postgres_host,
        port=cfg.postgres_port,
        dbname=cfg.postgres_db,
        user=cfg.postgres_user,
        password=cfg.postgres_password,
    )

    storage.ensure_bucket()
    run_id = metadata.start_run("pncp_ingestion", "pncp", batch_id, mode, start_date, end_date)
    files_count = 0
    rows_count = 0

    try:
        for page, items, _payload in client.iterate_contracts(
            start_date=start_date,
            end_date=end_date,
            page_size=cfg.pncp_page_size,
            max_pages=cfg.pncp_max_pages,
        ):
            key, count = storage.write_page(
                batch_id=batch_id,
                window_start=start_date.isoformat(),
                window_end=end_date.isoformat(),
                page=page,
                items=items,
            )
            files_count += 1
            rows_count += count
            metadata.add_event(
                run_id,
                "INFO",
                "PAGE_WRITTEN",
                f"Page {page} saved",
                json.dumps({"s3_key": key, "rows": count}),
            )

        metadata.finish_run(run_id, files_count, rows_count, "success")
        metadata.upsert_control("pncp_ingestion", "pncp", batch_id, "success", start_date, end_date)
    except Exception as exc:  # noqa: BLE001
        metadata.finish_run(run_id, files_count, rows_count, "failed", str(exc))
        metadata.add_event(run_id, "ERROR", "RUN_FAILED", str(exc), None)
        raise


def run(mode: str) -> None:
    cfg = from_env()
    if mode == "backfill":
        windows = list(monthly_windows(cfg.backfill_months))
        for window in reversed(windows):
            _run_window("backfill", window.start, window.end)
        return

    if mode == "incremental":
        window = incremental_window(cfg.reprocess_days)
        _run_window("incremental", window.start, window.end)
        return

    raise ValueError(f"Unsupported mode: {mode}")


def main() -> None:
    parser = argparse.ArgumentParser(description="PNCP ingestion runner")
    parser.add_argument("--mode", choices=["backfill", "incremental"], required=True)
    args = parser.parse_args()
    run(args.mode)


if __name__ == "__main__":
    main()
