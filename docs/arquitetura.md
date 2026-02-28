# Arquitetura de Dados (MVP)

## Stack
- Airflow (Docker)
- Postgres (Docker)
- MinIO (Docker)
- Parquet/Delta
- DuckDB (opcional)
- Streamlit

## Princípios
1. Postgres não guarda fatos analíticos; apenas controle/observabilidade.
2. MinIO guarda dados de negócio por camadas (raw/bronze/silver/gold).
3. Pipeline é reprocessável (partições e jobs idempotentes).
4. Regras e score ficam parametrizados em configuração externa.

## Camadas
- `raw`: payload original PNCP.
- `bronze`: normalização inicial.
- `silver`: modelo analítico limpo.
- `gold`: fatos de contrato, flags e score para consumo.
