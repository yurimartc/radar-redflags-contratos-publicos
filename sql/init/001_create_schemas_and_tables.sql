CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS control;
CREATE SCHEMA IF NOT EXISTS observability;

CREATE TABLE IF NOT EXISTS control.etl_control (
  pipeline_name TEXT PRIMARY KEY,
  source_name TEXT NOT NULL,
  last_successful_reference_start_date DATE,
  last_successful_reference_end_date DATE,
  last_batch_id TEXT,
  last_status TEXT CHECK (last_status IN ('success', 'failed')),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS control.etl_runs (
  run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pipeline_name TEXT NOT NULL,
  source_name TEXT NOT NULL,
  batch_id TEXT NOT NULL,
  run_type TEXT NOT NULL CHECK (run_type IN ('backfill', 'incremental', 'reprocess')),
  reference_start_date DATE NOT NULL,
  reference_end_date DATE NOT NULL,
  processed_files INTEGER NOT NULL DEFAULT 0,
  processed_rows BIGINT NOT NULL DEFAULT 0,
  status TEXT NOT NULL CHECK (status IN ('started', 'success', 'failed')),
  error_message TEXT,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_etl_runs_pipeline_started_at
  ON control.etl_runs (pipeline_name, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_etl_runs_status
  ON control.etl_runs (status, started_at DESC);

CREATE TABLE IF NOT EXISTS observability.pipeline_events (
  event_id BIGSERIAL PRIMARY KEY,
  run_id UUID REFERENCES control.etl_runs(run_id),
  event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  level TEXT NOT NULL,
  event_type TEXT NOT NULL,
  message TEXT NOT NULL,
  details JSONB
);

CREATE INDEX IF NOT EXISTS idx_pipeline_events_run_id
  ON observability.pipeline_events (run_id, event_time DESC);
