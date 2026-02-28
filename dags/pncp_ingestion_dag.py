from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def start_log(**context):
    print("[PNCP] Iniciando pipeline de ingestão (backfill + incremental).")
    print(f"run_id={context.get('run_id')}")


def extract_to_raw():
    """Placeholder da extração PNCP para MinIO em raw/.

    Próxima etapa: integrar cliente PNCP real + escrita parquet/delta em S3.
    """
    print("[PNCP] Extraindo dados e gravando em s3://<bucket>/raw/pncp/...")


def update_metadata():
    """Placeholder para atualizar Postgres (control.etl_runs / etl_control)."""
    print("[PNCP] Atualizando metadata no Postgres.")


with DAG(
    dag_id="pncp_backfill_incremental",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["pncp", "ingestion", "radar"],
) as dag:
    task_start = PythonOperator(task_id="start_log", python_callable=start_log)
    task_extract = PythonOperator(task_id="extract_to_raw_minio", python_callable=extract_to_raw)
    task_metadata = PythonOperator(task_id="update_postgres_metadata", python_callable=update_metadata)

    task_start >> task_extract >> task_metadata
