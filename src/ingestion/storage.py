from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

import boto3
from botocore.client import Config


@dataclass
class MinioRawStorage:
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str

    def __post_init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    def ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception:  # noqa: BLE001
            self.client.create_bucket(Bucket=self.bucket)

    @staticmethod
    def payload_hash(payload: dict) -> str:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def write_page(
        self,
        batch_id: str,
        window_start: str,
        window_end: str,
        page: int,
        items: list[dict],
    ) -> tuple[str, int]:
        extraction_date = datetime.utcnow().date().isoformat()
        key = (
            f"raw/pncp/extraction_date={extraction_date}/"
            f"window_start={window_start}/window_end={window_end}/"
            f"batch_id={batch_id}/page={page}.ndjson"
        )
        body = "\n".join(json.dumps(item, ensure_ascii=False) for item in items).encode("utf-8")
        self.client.put_object(Bucket=self.bucket, Key=key, Body=body, ContentType="application/x-ndjson")
        return key, len(items)
