from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('issuers', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('cik', sa.String(), nullable=False), sa.Column('ticker', sa.String()), sa.Column('name', sa.String(), nullable=False), sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint('cik'))
    op.create_index('ix_issuers_ticker', 'issuers', ['ticker'])
    op.create_table('source_filings', sa.Column('id', sa.UUID(), primary_key=True), sa.Column('accession_number', sa.String(), nullable=False), sa.Column('cik', sa.String(), nullable=False), sa.Column('form_type', sa.String(), nullable=False), sa.Column('filing_date', sa.Date()), sa.Column('acceptance_datetime', sa.DateTime(timezone=True)), sa.Column('filing_detail_url', sa.Text(), nullable=False), sa.Column('archive_base_url', sa.Text(), nullable=False), sa.Column('is_amendment', sa.Boolean(), nullable=False, server_default='false'), sa.Column('parse_status', sa.String(), nullable=False, server_default='pending'), sa.Column('parse_error', sa.Text()), sa.UniqueConstraint('accession_number'))
    op.create_view = lambda *args, **kwargs: None
    op.execute("""
    CREATE VIEW vw_company_filing_history AS
    SELECT i.ticker, i.name AS issuer_name, sf.cik AS issuer_cik, sf.accession_number, sf.form_type, sf.is_amendment, sf.filing_date, sf.acceptance_datetime, sf.parse_status, sf.parse_error, sf.filing_detail_url, sf.archive_base_url
    FROM source_filings sf LEFT JOIN issuers i ON sf.cik=i.cik;
    """)


def downgrade():
    op.execute('DROP VIEW IF EXISTS vw_company_filing_history')
    op.drop_table('source_filings')
    op.drop_table('issuers')
