# Ingestão PNCP — arquitetura Airflow + MinIO + Postgres

## Objetivo
Implementar pipeline de ingestão PNCP com:
- armazenamento de dados em MinIO (S3 local),
- controle operacional no Postgres,
- orquestração via Airflow.

## Fluxo alvo
1. Airflow dispara DAG de backfill/incremental.
2. Task de extração chama API PNCP com paginação e retry.
3. Dados brutos são gravados em `s3://<bucket>/raw/pncp/extract_date=YYYY-MM-DD/`.
4. Task de metadata atualiza `control.etl_runs` e `control.etl_control`.
5. Eventos operacionais são registrados em `observability.pipeline_events`.

## Estratégia de execução
- **Backfill:** por mês (últimos 12 meses).
- **Incremental diário:** D-1 até D.
- **Reprocessamento:** janela móvel dos últimos 7 dias.

## Convenção de camadas no MinIO
- `raw/`
- `bronze/`
- `silver/`
- `gold/`

Formato recomendado:
- Parquet para consumo analítico.
- Delta para versionamento transacional (quando ativado no processamento).

## Checklist mínimo
- Paginação da API.
- Retry/backoff.
- Idempotência (dedupe por hash/chave de negócio).
- Logs por `batch_id`.
- Métricas: arquivos, linhas e duração por execução.

## Implementação atual no repositório

Arquivos principais:
- `src/ingestion/pipeline.py`: runner de ingestão (`--mode backfill|incremental`).
- `src/ingestion/pncp_client.py`: cliente HTTP PNCP com retry/backoff.
- `src/ingestion/storage.py`: escrita em MinIO S3 (`raw/pncp/...`).
- `src/ingestion/metadata.py`: registro em `control.etl_runs`, `control.etl_control` e `observability.pipeline_events`.
- `src/ingestion/windows.py`: janelas de backfill mensal e incremental.
- `dags/pncp_ingestion_dag.py`: DAG Airflow usando o runner real.

## Execução manual (fora do Airflow)

```bash
python -m src.ingestion.pipeline --mode backfill
python -m src.ingestion.pipeline --mode incremental
```
