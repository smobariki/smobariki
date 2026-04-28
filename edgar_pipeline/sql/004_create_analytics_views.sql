CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.v_recent_filings AS
SELECT
  f.filing_id,
  f.accession_number,
  f.cik,
  f.ticker,
  f.company_name,
  f.form_type,
  f.filing_date,
  f.report_date,
  f.acceptance_datetime,
  f.is_amendment,
  f.amendment_parent_accession_number,
  f.primary_document_url,
  f.filing_index_url
FROM raw.sec_filings f
WHERE f.filing_date >= (CURRENT_DATE - INTERVAL '30 days');

CREATE OR REPLACE VIEW analytics.v_8k_events AS
SELECT
  f.filing_id,
  f.accession_number,
  f.cik,
  f.ticker,
  f.company_name,
  f.filing_date,
  e.event_category,
  e.event_keyword,
  e.matched_text
FROM raw.sec_filings f
JOIN parsed.eightk_event_tags e ON e.filing_id = f.filing_id
WHERE f.form_type IN ('8-K', '8-K/A');

CREATE OR REPLACE VIEW analytics.v_form4_transactions AS
SELECT
  f.filing_id,
  f.accession_number,
  f.cik,
  f.ticker,
  f.company_name,
  f.filing_date,
  'non_derivative'::TEXT AS transaction_kind,
  n.security_title,
  n.transaction_date,
  n.transaction_code,
  n.shares_amount,
  n.price_per_share
FROM raw.sec_filings f
JOIN parsed.form4_non_derivative_transactions n ON n.filing_id = f.filing_id
UNION ALL
SELECT
  f.filing_id,
  f.accession_number,
  f.cik,
  f.ticker,
  f.company_name,
  f.filing_date,
  'derivative'::TEXT AS transaction_kind,
  d.security_title,
  d.transaction_date,
  d.transaction_code,
  d.derivative_shares_amount AS shares_amount,
  d.price_per_derivative_security AS price_per_share
FROM raw.sec_filings f
JOIN parsed.form4_derivative_transactions d ON d.filing_id = f.filing_id;

CREATE OR REPLACE VIEW analytics.v_insider_activity_summary AS
SELECT
  ticker,
  company_name,
  DATE_TRUNC('day', filing_date)::DATE AS activity_day,
  COUNT(*) AS transaction_count,
  SUM(COALESCE(shares_amount, 0)) AS total_shares
FROM analytics.v_form4_transactions
GROUP BY 1,2,3;

CREATE OR REPLACE VIEW analytics.v_sc13_ownership_changes AS
SELECT
  f.filing_id,
  f.accession_number,
  f.cik,
  f.ticker,
  f.company_name,
  f.filing_date,
  s.signal_category,
  s.signal_keyword,
  s.matched_text
FROM raw.sec_filings f
JOIN parsed.sc13_signals s ON s.filing_id = f.filing_id
WHERE f.form_type IN ('SC 13D', 'SC 13D/A', 'SC 13G', 'SC 13G/A');

CREATE OR REPLACE VIEW analytics.v_company_filing_activity AS
SELECT
  f.cik,
  COALESCE(f.ticker, cu.ticker) AS ticker,
  COALESCE(f.company_name, cu.company_name) AS company_name,
  COUNT(*) AS filing_count,
  COUNT(*) FILTER (WHERE f.form_type IN ('8-K', '8-K/A')) AS filing_8k_count,
  COUNT(*) FILTER (WHERE f.form_type IN ('4', '4/A')) AS filing_form4_count,
  COUNT(*) FILTER (WHERE f.form_type LIKE 'SC 13%') AS filing_sc13_count,
  MAX(f.filing_date) AS most_recent_filing_date
FROM raw.sec_filings f
LEFT JOIN raw.company_universe cu USING (cik)
GROUP BY 1,2,3;

CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_daily_filing_kpis AS
SELECT
  DATE_TRUNC('day', filing_date)::DATE AS filing_day,
  COUNT(*) AS filings_total,
  COUNT(*) FILTER (WHERE is_amendment) AS amendments_total,
  COUNT(*) FILTER (WHERE form_type IN ('8-K', '8-K/A')) AS filings_8k,
  COUNT(*) FILTER (WHERE form_type IN ('4', '4/A')) AS filings_form4,
  COUNT(*) FILTER (WHERE form_type LIKE 'SC 13%') AS filings_sc13
FROM raw.sec_filings
GROUP BY 1;

CREATE OR REPLACE VIEW analytics.v_daily_filing_kpis AS
SELECT * FROM analytics.mv_daily_filing_kpis;

CREATE OR REPLACE VIEW analytics.v_alert_candidates AS
SELECT
  e.filing_id,
  e.accession_number,
  e.ticker,
  e.company_name,
  e.filing_date,
  '8k_event'::TEXT AS alert_type,
  e.event_category AS alert_category,
  e.matched_text AS alert_message
FROM analytics.v_8k_events e
UNION ALL
SELECT
  s.filing_id,
  s.accession_number,
  s.ticker,
  s.company_name,
  s.filing_date,
  'sc13_signal'::TEXT,
  s.signal_category,
  s.matched_text
FROM analytics.v_sc13_ownership_changes s;
