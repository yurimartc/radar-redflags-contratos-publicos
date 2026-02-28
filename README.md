# Projeto 1 — Radar de Contratos com Red Flags

## Objetivo
Construir um radar analítico para priorização de risco em contratos públicos, com foco em auditoria, compliance e governança.

## Arquitetura final (MVP)

- **Airflow (Docker):** orquestração de backfill + incremental.
- **Postgres (Docker):** metadata/controle/observabilidade (`control` e `observability`).
- **MinIO (Docker):** data lake S3 local para camadas `raw/bronze/silver/gold`.
- **Parquet/Delta:** formato analítico principal para dados reprocessáveis e baratos.
- **DuckDB (opcional):** consultas rápidas e agregações locais.
- **Streamlit:** dashboard para ranking e drill-down.

### Visão de responsabilidade por camada

- **MinIO** guarda os dados do pipeline (raw → gold).
- **Airflow** agenda e executa jobs (backfill, incremental e reprocessamento).
- **Postgres** guarda estado de execução, runs e eventos operacionais.
- **Streamlit** lê dados analíticos (Parquet/Delta) para visualização.

---

## Entregáveis do produto

1. Tabela analítica gold de contratos.
2. Tabela de red flags com severidade e evidências.
3. Tabela de score de risco 0–100 explicável.
4. Dashboard com visão geral, rankings e drill-down.
5. Documentação de dicionário, metodologia e limitações.

---

## Escopo de ingestão PNCP (MVP)

### Carga histórica (backfill)
- Execução mensal para últimos 12 meses.

### Carga incremental
- Execução diária (`D-1` até `D`) com reprocessamento de 7 dias.

### Requisitos operacionais
- Paginação.
- Retry + backoff.
- Idempotência.
- Logs e métricas de volume.

---

## Banco/infra local com Docker

## Serviços
- `postgres` → metadata/controle/observabilidade.
- `minio` + `minio-init` → storage S3 local e criação automática do bucket.
- `airflow-webserver` + `airflow-scheduler` + `airflow-init` → orquestração.
- `streamlit` → app inicial para dashboard.

## Subir stack local

```bash
cp .env.example .env
make up
```

Acessos padrão:
- Airflow: `http://localhost:8081`
- MinIO Console: `http://localhost:9001`
- MinIO API (S3): `http://localhost:9000`
- Streamlit: `http://localhost:8501`
- Postgres: `localhost:5432`

## Comandos úteis

```bash
make ps
make logs
make airflow-logs
make minio-logs
make postgres-logs
make db-psql
make down
make reset
```

---

## Inicialização SQL (Postgres)

Scripts em `sql/init/` são executados automaticamente na primeira subida.

Script atual:
- `sql/init/001_create_schemas_and_tables.sql`

Objetos principais:
- `control.etl_control`
- `control.etl_runs`
- `observability.pipeline_events`

> Observação: dados analíticos não ficam no Postgres; ficam em MinIO (Parquet/Delta).

---

## Estrutura atual do repositório

```text
.
├── airflow/
├── dags/
├── configs/
├── docs/
├── sql/init/
├── streamlit_app/
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Próximos passos

1. Implementar DAG `pncp_backfill_incremental` no Airflow.
2. Criar job Python de extração PNCP para `s3://<bucket>/raw/pncp/...`.
3. Implementar transformação para bronze/silver em Parquet/Delta.
4. Registrar métricas de execução no Postgres (`control` e `observability`).
5. Conectar Streamlit à camada gold e publicar ranking inicial.
