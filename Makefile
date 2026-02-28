SHELL := /bin/bash

-include .env
export

.PHONY: up down reset logs ps airflow-logs minio-logs postgres-logs db-psql ingest-backfill ingest-incremental test

up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up -d

logs:
	docker compose logs -f

ps:
	docker compose ps

airflow-logs:
	docker compose logs -f airflow-webserver airflow-scheduler

minio-logs:
	docker compose logs -f minio minio-init

postgres-logs:
	docker compose logs -f postgres

db-psql:
	docker compose exec postgres psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}


ingest-backfill:
	python -m src.ingestion.pipeline --mode backfill

ingest-incremental:
	python -m src.ingestion.pipeline --mode incremental

test:
	pytest -q
