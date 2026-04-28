CREATE SCHEMA IF NOT EXISTS parsed;

CREATE TABLE IF NOT EXISTS parsed.eightk_items (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  item_number TEXT,
  item_description TEXT,
  section_text TEXT,
  parsed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS parsed.eightk_exhibits (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  exhibit_number TEXT,
  exhibit_description TEXT,
  exhibit_filename TEXT,
  exhibit_url TEXT,
  exhibit_text TEXT
);

CREATE TABLE IF NOT EXISTS parsed.eightk_event_tags (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  event_category TEXT,
  event_keyword TEXT,
  confidence_method TEXT,
  matched_text TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS parsed.form4_reporting_owners (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  owner_cik TEXT,
  owner_name TEXT,
  is_director BOOLEAN,
  is_officer BOOLEAN,
  officer_title TEXT,
  is_ten_percent_owner BOOLEAN,
  is_other BOOLEAN,
  other_text TEXT
);

CREATE TABLE IF NOT EXISTS parsed.form4_non_derivative_transactions (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  owner_cik TEXT,
  security_title TEXT,
  transaction_date DATE,
  deemed_execution_date DATE,
  transaction_code TEXT,
  transaction_acquired_disposed_code TEXT,
  shares_amount NUMERIC,
  price_per_share NUMERIC,
  shares_owned_following_transaction NUMERIC,
  direct_or_indirect_ownership TEXT,
  ownership_nature TEXT,
  footnote_ids TEXT
);

CREATE TABLE IF NOT EXISTS parsed.form4_derivative_transactions (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  owner_cik TEXT,
  security_title TEXT,
  conversion_or_exercise_price NUMERIC,
  transaction_date DATE,
  transaction_code TEXT,
  transaction_acquired_disposed_code TEXT,
  derivative_shares_amount NUMERIC,
  price_per_derivative_security NUMERIC,
  underlying_security_title TEXT,
  underlying_security_shares NUMERIC,
  exercise_date DATE,
  expiration_date DATE,
  shares_owned_following_transaction NUMERIC,
  direct_or_indirect_ownership TEXT,
  ownership_nature TEXT,
  footnote_ids TEXT
);

CREATE TABLE IF NOT EXISTS parsed.form4_footnotes (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  footnote_id TEXT,
  footnote_text TEXT
);

CREATE TABLE IF NOT EXISTS parsed.sc13_filers (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  reporting_person_name TEXT,
  reporting_person_cik TEXT,
  reporting_person_type TEXT,
  address_text TEXT
);

CREATE TABLE IF NOT EXISTS parsed.sc13_holdings (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  issuer_name TEXT,
  issuer_cik TEXT,
  title_of_class TEXT,
  cusip TEXT,
  shares_beneficially_owned NUMERIC,
  percent_of_class NUMERIC,
  sole_voting_power NUMERIC,
  shared_voting_power NUMERIC,
  sole_dispositive_power NUMERIC,
  shared_dispositive_power NUMERIC
);

CREATE TABLE IF NOT EXISTS parsed.sc13_sections (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  section_name TEXT,
  section_text TEXT
);

CREATE TABLE IF NOT EXISTS parsed.sc13_signals (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES raw.sec_filings(filing_id) ON DELETE CASCADE,
  signal_category TEXT,
  signal_keyword TEXT,
  matched_text TEXT,
  confidence_method TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
