from datetime import date
from decimal import Decimal, InvalidOperation

from lxml import etree

from edgar_ownership_etl.utils.hashing import row_hash


def _find(node, path: str):
    expr = "/".join([f"*[local-name()='{part}']" for part in path.split('/')])
    matches = node.xpath(expr)
    return matches[0] if matches else None


def _text_path(node, path: str):
    found = _find(node, path)
    if found is None or found.text is None:
        return None
    value = found.text.strip()
    return value or None


def _decimal_path(node, path: str):
    value = _text_path(node, path)
    if value is None:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _date_path(node, path: str):
    value = _text_path(node, path)
    return date.fromisoformat(value) if value else None


def _bool_path(node, path: str):
    value = _text_path(node, path)
    if value is None:
        return None
    return value.strip().lower() in {'1','true','y','yes'}


def parse_ownership_xml(xml_text: str) -> dict:
    root = etree.fromstring(xml_text.encode())
    submission = {
        "document_type": _text_path(root, "documentType") or "",
        "issuer_cik": _text_path(root, "issuer/issuerCik") or "",
        "issuer_name": _text_path(root, "issuer/issuerName"),
        "issuer_trading_symbol": _text_path(root, "issuer/issuerTradingSymbol"),
        "reporting_owners": [],
        "non_derivative_transactions": [],
        "derivative_transactions": [],
        "non_derivative_holdings": [],
        "derivative_holdings": [],
        "footnotes": [],
        "signatures": [],
    }

    for owner in root.xpath("*[local-name()='reportingOwner']"):
        submission["reporting_owners"].append({
            "rpt_owner_cik": _text_path(owner, "reportingOwnerId/rptOwnerCik"),
            "owner_name": _text_path(owner, "reportingOwnerId/rptOwnerName") or "Unknown",
            "is_director": _bool_path(owner, "reportingOwnerRelationship/isDirector"),
            "is_officer": _bool_path(owner, "reportingOwnerRelationship/isOfficer"),
            "officer_title": _text_path(owner, "reportingOwnerRelationship/officerTitle"),
            "is_ten_percent_owner": _bool_path(owner, "reportingOwnerRelationship/isTenPercentOwner"),
            "is_other": _bool_path(owner, "reportingOwnerRelationship/isOther"),
            "other_text": _text_path(owner, "reportingOwnerRelationship/otherText"),
        })

    for idx, tx in enumerate(root.xpath("*[local-name()='nonDerivativeTable']/*[local-name()='nonDerivativeTransaction']")):
        row = {
            "security_title": _text_path(tx, "securityTitle/value"),
            "transaction_date": _date_path(tx, "transactionDate/value"),
            "transaction_code": _text_path(tx, "transactionCoding/transactionCode"),
            "equity_swap_involved": _text_path(tx, "transactionCoding/equitySwapInvolved"),
            "transaction_shares": _decimal_path(tx, "transactionAmounts/transactionShares/value"),
            "transaction_price_per_share": _decimal_path(tx, "transactionAmounts/transactionPricePerShare/value"),
            "transaction_acquired_disposed_code": _text_path(tx, "transactionAmounts/transactionAcquiredDisposedCode/value"),
            "shares_owned_following_transaction": _decimal_path(tx, "postTransactionAmounts/sharesOwnedFollowingTransaction/value"),
            "direct_or_indirect_ownership": _text_path(tx, "ownershipNature/directOrIndirectOwnership/value"),
            "nature_of_ownership": _text_path(tx, "ownershipNature/natureOfOwnership/value"),
        }
        row["source_row_hash"] = row_hash({**row, "row_ordinal": idx})
        submission["non_derivative_transactions"].append(row)

    for idx, tx in enumerate(root.xpath("*[local-name()='derivativeTable']/*[local-name()='derivativeTransaction']")):
        row = {
            "security_title": _text_path(tx, "securityTitle/value"),
            "transaction_date": _date_path(tx, "transactionDate/value"),
            "transaction_code": _text_path(tx, "transactionCoding/transactionCode"),
            "transaction_shares": _decimal_path(tx, "transactionAmounts/transactionShares/value"),
            "transaction_price_per_share": _decimal_path(tx, "transactionAmounts/transactionPricePerShare/value"),
            "direct_or_indirect_ownership": _text_path(tx, "ownershipNature/directOrIndirectOwnership/value"),
        }
        row["source_row_hash"] = row_hash({**row, "row_ordinal": idx})
        submission["derivative_transactions"].append(row)

    for ft in root.xpath("*[local-name()='footnotes']/*[local-name()='footnote']"):
        submission["footnotes"].append({"footnote_id": ft.get("id"), "footnote_text": (ft.text or "").strip()})
    for sig in root.xpath("*[local-name()='ownerSignature']"):
        submission["signatures"].append({"signature_name": _text_path(sig, "signatureName") or "", "signature_date": _date_path(sig, "signatureDate")})
    return submission
