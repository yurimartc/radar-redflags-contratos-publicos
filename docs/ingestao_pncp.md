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
