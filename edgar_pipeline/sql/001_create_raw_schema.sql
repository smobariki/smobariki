CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.ingestion_runs (
  run_id BIGSERIAL PRIMARY KEY,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status TEXT NOT NULL,
  filings_found_count INTEGER NOT NULL DEFAULT 0,
  filings_inserted_count INTEGER NOT NULL DEFAULT 0,
  filings_failed_count INTEGER NOT NULL DEFAULT 0,
  error_message TEXT
);

CREATE TABLE IF NOT EXISTS raw.company_universe (
  cik TEXT PRIMARY KEY,
  ticker TEXT,
  company_name TEXT NOT NULL,
  exchange TEXT,
  source TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  last_seen_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.sec_filings (
  filing_id BIGSERIAL PRIMARY KEY,
  accession_number TEXT NOT NULL UNIQUE,
  cik TEXT NOT NULL,
  ticker TEXT,
  company_name TEXT,
  form_type TEXT NOT NULL,
  filing_date DATE,
  report_date DATE,
  acceptance_datetime TIMESTAMPTZ,
  primary_document TEXT,
  primary_document_url TEXT,
  filing_detail_url TEXT,
  filing_index_url TEXT,
  is_amendment BOOLEAN NOT NULL DEFAULT FALSE,
  amendment_parent_accession_number TEXT,
  latest_known_accession_number TEXT,
  raw_metadata_json JSONB,
  raw_html TEXT,
  raw_xml TEXT,
  raw_text TEXT,
  content_sha256 TEXT,
  fetched_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.filing_documents (
  document_id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  document_sequence TEXT,
  document_type TEXT,
  document_description TEXT,
  document_filename TEXT,
  document_url TEXT,
  content_type TEXT,
  raw_content TEXT,
  fetched_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS raw.qlik_reload_log (
  qlik_reload_log_id BIGSERIAL PRIMARY KEY,
  run_id BIGINT REFERENCES raw.ingestion_runs(run_id),
  reload_id TEXT,
  status TEXT,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ
);
