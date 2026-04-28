CREATE SCHEMA IF NOT EXISTS normalized;

CREATE TABLE IF NOT EXISTS normalized.companies (
  company_id BIGSERIAL PRIMARY KEY,
  cik TEXT UNIQUE NOT NULL,
  ticker TEXT,
  company_name TEXT,
  exchange TEXT
);

CREATE TABLE IF NOT EXISTS normalized.filings (
  normalized_filing_id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT UNIQUE REFERENCES raw.sec_filings(filing_id),
  company_id BIGINT REFERENCES normalized.companies(company_id),
  accession_number TEXT UNIQUE,
  form_type TEXT,
  filing_date DATE,
  is_amendment BOOLEAN,
  amendment_parent_accession_number TEXT,
  latest_known_accession_number TEXT
);

CREATE TABLE IF NOT EXISTS normalized.people_and_entities (
  entity_id BIGSERIAL PRIMARY KEY,
  entity_name TEXT,
  entity_cik TEXT,
  entity_type TEXT
);

CREATE TABLE IF NOT EXISTS normalized.securities (
  security_id BIGSERIAL PRIMARY KEY,
  issuer_cik TEXT,
  issuer_name TEXT,
  security_title TEXT,
  cusip TEXT
);

CREATE TABLE IF NOT EXISTS normalized.ownership_events (
  ownership_event_id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT REFERENCES raw.sec_filings(filing_id),
  entity_id BIGINT REFERENCES normalized.people_and_entities(entity_id),
  security_id BIGINT REFERENCES normalized.securities(security_id),
  event_type TEXT,
  event_date DATE,
  shares NUMERIC,
  percent_of_class NUMERIC
);

CREATE TABLE IF NOT EXISTS normalized.material_events (
  material_event_id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT REFERENCES raw.sec_filings(filing_id),
  category TEXT,
  keyword TEXT,
  event_date DATE,
  details TEXT
);
