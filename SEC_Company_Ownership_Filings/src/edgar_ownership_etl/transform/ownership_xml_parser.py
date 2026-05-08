from decimal import Decimal
from lxml import etree
from edgar_ownership_etl.utils.hashing import row_hash


def _text(node, path):
    found = node.find(path)
    return found.text.strip() if found is not None and found.text else None


def parse_ownership_xml(xml_text: str) -> dict:
    root = etree.fromstring(xml_text.encode())
    submission = {
        "document_type": _text(root, "documentType") or "",
        "issuer_cik": _text(root, "issuer/issuerCik") or "",
        "issuer_name": _text(root, "issuer/issuerName"),
        "issuer_trading_symbol": _text(root, "issuer/issuerTradingSymbol"),
        "non_derivative_transactions": [],
    }
    for tx in root.findall("nonDerivativeTable/nonDerivativeTransaction"):
        row = {
            "security_title": _text(tx, "securityTitle/value"),
            "transaction_date": _text(tx, "transactionDate/value"),
            "transaction_code": _text(tx, "transactionCoding/transactionCode"),
            "transaction_shares": Decimal(_text(tx, "transactionAmounts/transactionShares/value") or "0"),
            "transaction_price_per_share": Decimal(_text(tx, "transactionAmounts/transactionPricePerShare/value") or "0"),
            "transaction_acquired_disposed_code": _text(tx, "transactionAmounts/transactionAcquiredDisposedCode/value"),
            "shares_owned_following_transaction": Decimal(_text(tx, "postTransactionAmounts/sharesOwnedFollowingTransaction/value") or "0"),
            "direct_or_indirect_ownership": _text(tx, "ownershipNature/directOrIndirectOwnership/value"),
            "nature_of_ownership": _text(tx, "ownershipNature/natureOfOwnership/value"),
        }
        row["source_row_hash"] = row_hash(row)
        submission["non_derivative_transactions"].append(row)
    return submission
