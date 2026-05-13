from datetime import date
from decimal import Decimal
from lxml import etree
from edgar_ownership_etl.utils.hashing import row_hash


def _first(node, name):
    return node.xpath(f'.//*[local-name()="{name}"]')


def _text(node, name):
    f = _first(node, name)
    return f[0].text.strip() if f and f[0].text else None


def _date(v):
    return date.fromisoformat(v) if v else None


def parse_ownership_xml(xml_text: str) -> dict:
    root = etree.fromstring(xml_text.encode())
    submission = {"document_type": _text(root, "documentType") or "", "issuer_cik": _text(root, "issuerCik") or "", "issuer_name": _text(root, "issuerName"), "issuer_trading_symbol": _text(root, "issuerTradingSymbol"), "reporting_owners": [], "non_derivative_transactions": [], "derivative_transactions": [], "non_derivative_holdings": [], "derivative_holdings": [], "footnotes": [], "signatures": []}

    for owner in root.xpath('.//*[local-name()="reportingOwner"]'):
        submission["reporting_owners"].append({"rpt_owner_cik": _text(owner, "rptOwnerCik"), "owner_name": _text(owner, "rptOwnerName") or "Unknown", "is_director": (_text(owner, "isDirector") or "") in {"1", "true", "True"}})

    for idx, tx in enumerate(root.xpath('.//*[local-name()="nonDerivativeTransaction"]')):
        row = {"security_title": _text(tx, "value"), "transaction_date": _date(_text(tx, "transactionDate")), "transaction_code": _text(tx, "transactionCode"), "transaction_shares": Decimal(_text(tx, "transactionShares") or "0"), "transaction_price_per_share": Decimal(_text(tx, "transactionPricePerShare") or "0")}
        row["source_row_hash"] = row_hash({**row, "row_ordinal": idx})
        submission["non_derivative_transactions"].append(row)

    for ft in root.xpath('.//*[local-name()="footnote"]'):
        submission["footnotes"].append({"footnote_id": ft.get("id"), "footnote_text": (ft.text or "").strip()})
    for sig in root.xpath('.//*[local-name()="ownerSignature"]'):
        submission["signatures"].append({"signature_name": _text(sig, "signatureName") or "", "signature_date": _date(_text(sig, "signatureDate"))})
    return submission
