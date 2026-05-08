from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Issuer(Base):
    __tablename__ = "issuers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cik: Mapped[str] = mapped_column(String, unique=True, index=True)
    ticker: Mapped[str | None] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class SourceFiling(Base):
    __tablename__ = "source_filings"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accession_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    cik: Mapped[str] = mapped_column(String, index=True)
    form_type: Mapped[str] = mapped_column(String, index=True)
    filing_date: Mapped[Date | None] = mapped_column(Date, index=True)
    acceptance_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    filing_detail_url: Mapped[str] = mapped_column(Text)
    archive_base_url: Mapped[str] = mapped_column(Text)
    is_amendment: Mapped[bool] = mapped_column(Boolean, default=False)
    parse_status: Mapped[str] = mapped_column(String, default="pending")
    parse_error: Mapped[str | None] = mapped_column(Text)


class OwnershipSubmission(Base):
    __tablename__ = "ownership_submissions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_filing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_filings.id"), unique=True)
    accession_number: Mapped[str] = mapped_column(String, unique=True)
    document_type: Mapped[str] = mapped_column(String)
    issuer_cik: Mapped[str] = mapped_column(String)


class ReportingOwner(Base):
    __tablename__ = "reporting_owners"
    __table_args__ = (UniqueConstraint("rpt_owner_cik", "owner_name"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rpt_owner_cik: Mapped[str | None] = mapped_column(String, index=True)
    owner_name: Mapped[str] = mapped_column(String, index=True)
    is_director: Mapped[bool | None] = mapped_column(Boolean)


class NonDerivativeTransaction(Base):
    __tablename__ = "non_derivative_transactions"
    __table_args__ = (UniqueConstraint("ownership_submission_id", "source_row_hash"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ownership_submission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ownership_submissions.id"))
    transaction_date: Mapped[Date | None] = mapped_column(Date, index=True)
    transaction_code: Mapped[str | None] = mapped_column(String, index=True)
    transaction_shares: Mapped[float | None] = mapped_column(Numeric)
    transaction_price_per_share: Mapped[float | None] = mapped_column(Numeric)
    transaction_acquired_disposed_code: Mapped[str | None] = mapped_column(String)
    shares_owned_following_transaction: Mapped[float | None] = mapped_column(Numeric)
    direct_or_indirect_ownership: Mapped[str | None] = mapped_column(String)
    security_title: Mapped[str | None] = mapped_column(String)
    nature_of_ownership: Mapped[str | None] = mapped_column(String)
    footnote_ids: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    source_row_hash: Mapped[str] = mapped_column(String)


class EtlWatermark(Base):
    __tablename__ = "etl_watermarks"
    __table_args__ = (UniqueConstraint("scope", "scope_value"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope: Mapped[str] = mapped_column(String)
    scope_value: Mapped[str] = mapped_column(String)
    last_accession_number: Mapped[str | None] = mapped_column(String)
