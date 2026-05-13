from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('issuers', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('cik', sa.String(), nullable=False), sa.Column('ticker', sa.String()), sa.Column('name', sa.String(), nullable=False), sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint('cik'))
    op.create_index('ix_issuers_ticker', 'issuers', ['ticker'])
    op.create_table('source_filings', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('accession_number', sa.String(), nullable=False), sa.Column('cik', sa.String(), nullable=False), sa.Column('form_type', sa.String(), nullable=False), sa.Column('filing_date', sa.Date()), sa.Column('report_date', sa.Date()), sa.Column('acceptance_datetime', sa.DateTime(timezone=True)), sa.Column('filing_detail_url', sa.Text(), nullable=False), sa.Column('archive_base_url', sa.Text(), nullable=False), sa.Column('is_amendment', sa.Boolean(), nullable=False, server_default='false'), sa.Column('parse_status', sa.String(), nullable=False, server_default='pending'), sa.Column('parse_error', sa.Text()), sa.UniqueConstraint('accession_number'))
    op.create_table('raw_documents', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('source_filing_id', sa.UUID(), sa.ForeignKey('source_filings.id')), sa.Column('document_name', sa.String(), nullable=False), sa.Column('document_url', sa.Text(), nullable=False), sa.Column('content_type', sa.String()), sa.Column('content_sha256', sa.String(), nullable=False), sa.Column('raw_text', sa.Text()), sa.Column('retrieved_at', sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint('source_filing_id', 'document_name'))
    op.create_table('ownership_submissions', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('source_filing_id', sa.UUID(), sa.ForeignKey('source_filings.id'), unique=True), sa.Column('accession_number', sa.String(), unique=True), sa.Column('document_type', sa.String(), nullable=False), sa.Column('issuer_cik', sa.String(), nullable=False))
    op.create_table('reporting_owners', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('rpt_owner_cik', sa.String()), sa.Column('owner_name', sa.String(), nullable=False), sa.Column('is_director', sa.Boolean()), sa.UniqueConstraint('rpt_owner_cik', 'owner_name'))
    op.create_table('ownership_submission_reporting_owners', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('ownership_submission_id', sa.UUID(), sa.ForeignKey('ownership_submissions.id')), sa.Column('reporting_owner_id', sa.UUID(), sa.ForeignKey('reporting_owners.id')), sa.UniqueConstraint('ownership_submission_id', 'reporting_owner_id'))
    for t in ['non_derivative_transactions','derivative_transactions','non_derivative_holdings','derivative_holdings']:
        op.create_table(t, sa.Column('id', sa.UUID(), primary_key=True), sa.Column('ownership_submission_id', sa.UUID(), sa.ForeignKey('ownership_submissions.id')), sa.Column('transaction_date', sa.Date()), sa.Column('transaction_code', sa.String()), sa.Column('transaction_shares', sa.Numeric()), sa.Column('transaction_price_per_share', sa.Numeric()), sa.Column('security_title', sa.String()), sa.Column('source_row_hash', sa.String(), nullable=False), sa.UniqueConstraint('ownership_submission_id', 'source_row_hash'))
    op.create_table('ownership_footnotes', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('ownership_submission_id', sa.UUID(), sa.ForeignKey('ownership_submissions.id')), sa.Column('footnote_id', sa.String(), nullable=False), sa.Column('footnote_text', sa.Text(), nullable=False), sa.UniqueConstraint('ownership_submission_id', 'footnote_id'))
    op.create_table('owner_signatures', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('ownership_submission_id', sa.UUID(), sa.ForeignKey('ownership_submissions.id')), sa.Column('signature_name', sa.String(), nullable=False), sa.Column('signature_date', sa.Date()), sa.UniqueConstraint('ownership_submission_id', 'signature_name', 'signature_date'))
    op.create_table('etl_watermarks', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('scope', sa.String(), nullable=False), sa.Column('scope_value', sa.String(), nullable=False), sa.Column('last_accession_number', sa.String()), sa.Column('last_filing_date', sa.Date()), sa.Column('last_acceptance_datetime', sa.DateTime(timezone=True)), sa.UniqueConstraint('scope','scope_value'))
    op.execute("""CREATE VIEW vw_company_filing_history AS SELECT i.ticker, i.name issuer_name, sf.cik issuer_cik, sf.accession_number, sf.form_type, sf.is_amendment, sf.filing_date, sf.acceptance_datetime, sf.parse_status FROM source_filings sf LEFT JOIN issuers i ON sf.cik=i.cik;""")
    op.execute("""CREATE VIEW vw_form4_transactions AS SELECT sf.accession_number, sf.cik issuer_cik, sf.filing_date, ndt.transaction_date, ndt.transaction_code, ndt.transaction_shares, ndt.transaction_price_per_share FROM non_derivative_transactions ndt JOIN ownership_submissions os ON ndt.ownership_submission_id=os.id JOIN source_filings sf ON os.source_filing_id=sf.id WHERE sf.form_type in ('4','4/A');""")
    op.execute("""CREATE VIEW vw_latest_insider_transactions AS SELECT * FROM vw_form4_transactions;""")
    op.execute("""CREATE VIEW vw_reporting_owner_activity AS SELECT ro.owner_name, ro.rpt_owner_cik, count(*) filing_count FROM reporting_owners ro JOIN ownership_submission_reporting_owners osro ON ro.id=osro.reporting_owner_id GROUP BY ro.owner_name, ro.rpt_owner_cik;""")


def downgrade():
    for v in ['vw_reporting_owner_activity','vw_latest_insider_transactions','vw_form4_transactions','vw_company_filing_history']:
        op.execute(f'DROP VIEW IF EXISTS {v}')
