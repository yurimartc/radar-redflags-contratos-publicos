from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import psycopg2


@dataclass
class MetadataStore:
    host: str
    port: int
    dbname: str
    user: str
    password: str

    def _conn(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )

    def start_run(self, pipeline_name: str, source_name: str, batch_id: str, run_type: str, start: date, end: date) -> str:
        query = """
        INSERT INTO control.etl_runs
        (pipeline_name, source_name, batch_id, run_type, reference_start_date, reference_end_date, status)
        VALUES (%s,%s,%s,%s,%s,%s,'started')
        RETURNING run_id::text;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(query, (pipeline_name, source_name, batch_id, run_type, start, end))
            run_id = cur.fetchone()[0]
            conn.commit()
        return run_id

    def finish_run(self, run_id: str, processed_files: int, processed_rows: int, status: str, error_message: str | None = None) -> None:
        query = """
        UPDATE control.etl_runs
           SET processed_files=%s,
               processed_rows=%s,
               status=%s,
               error_message=%s,
               finished_at=NOW()
         WHERE run_id=%s::uuid;
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(query, (processed_files, processed_rows, status, error_message, run_id))
            conn.commit()

    def upsert_control(self, pipeline_name: str, source_name: str, batch_id: str, status: str, start: date, end: date) -> None:
        query = """
        INSERT INTO control.etl_control
            (pipeline_name, source_name, last_successful_reference_start_date, last_successful_reference_end_date, last_batch_id, last_status)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (pipeline_name)
        DO UPDATE SET
            source_name=EXCLUDED.source_name,
            last_successful_reference_start_date=EXCLUDED.last_successful_reference_start_date,
            last_successful_reference_end_date=EXCLUDED.last_successful_reference_end_date,
            last_batch_id=EXCLUDED.last_batch_id,
            last_status=EXCLUDED.last_status,
            updated_at=NOW();
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(query, (pipeline_name, source_name, start, end, batch_id, status))
            conn.commit()

    def add_event(self, run_id: str, level: str, event_type: str, message: str, details: str | None = None) -> None:
        query = """
        INSERT INTO observability.pipeline_events (run_id, level, event_type, message, details)
        VALUES (%s::uuid, %s, %s, %s, CASE WHEN %s IS NULL THEN NULL ELSE %s::jsonb END);
        """
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(query, (run_id, level, event_type, message, details, details))
            conn.commit()
