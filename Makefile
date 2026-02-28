SHELL := /bin/bash

-include .env
export

.PHONY: up down reset logs ps airflow-logs minio-logs postgres-logs db-psql

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
