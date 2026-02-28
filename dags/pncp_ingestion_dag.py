from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.ingestion.pipeline import run


def run_backfill() -> None:
    run("backfill")


def run_incremental() -> None:
    run("incremental")


with DAG(
    dag_id="pncp_backfill_incremental",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["pncp", "ingestion", "radar"],
) as dag:
    task_backfill = PythonOperator(task_id="run_backfill_if_needed", python_callable=run_backfill)
    task_incremental = PythonOperator(task_id="run_incremental", python_callable=run_incremental)

    task_backfill >> task_incremental
