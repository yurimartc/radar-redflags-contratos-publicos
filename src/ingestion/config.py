from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class IngestionConfig:
    pncp_base_url: str
    pncp_timeout_seconds: int
    pncp_page_size: int
    pncp_max_pages: int
    reprocess_days: int
    backfill_months: int
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str



def from_env() -> IngestionConfig:
    return IngestionConfig(
        pncp_base_url=os.getenv("PNCP_BASE_URL", "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"),
        pncp_timeout_seconds=int(os.getenv("PNCP_TIMEOUT_SECONDS", "30")),
        pncp_page_size=int(os.getenv("PNCP_PAGE_SIZE", "100")),
        pncp_max_pages=int(os.getenv("PNCP_MAX_PAGES", "500")),
        reprocess_days=int(os.getenv("PNCP_REPROCESS_DAYS", "7")),
        backfill_months=int(os.getenv("PNCP_BACKFILL_MONTHS", "12")),
        minio_endpoint=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
        minio_access_key=os.getenv("MINIO_ROOT_USER", "minio"),
        minio_secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minio123"),
        minio_bucket=os.getenv("MINIO_LAKE_BUCKET", "radar-lake"),
        postgres_host=os.getenv("POSTGRES_HOST", "postgres"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
        postgres_db=os.getenv("POSTGRES_DB", "radar_contratos"),
        postgres_user=os.getenv("POSTGRES_USER", "radar"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "radar123"),
    )
