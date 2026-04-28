from __future__ import annotations

import xml.etree.ElementTree as ET


def _find_text(node: ET.Element | None, path: str) -> str | None:
    if node is None:
        return None
    found = node.find(path)
    return found.text.strip() if found is not None and found.text else None


def parse_form4(xml_text: str | None) -> dict:
    if not xml_text:
        return {"owners": [], "non_derivative": [], "derivative": [], "footnotes": []}

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return {"owners": [], "non_derivative": [], "derivative": [], "footnotes": []}

    owners = []
    for owner in root.findall(".//reportingOwner"):
        rel = owner.find("reportingOwnerRelationship")
        owner_id = owner.find("reportingOwnerId")
        owners.append(
            {
                "owner_cik": _find_text(owner_id, "rptOwnerCik"),
                "owner_name": _find_text(owner_id, "rptOwnerName"),
                "is_director": _find_text(rel, "isDirector") == "1",
                "is_officer": _find_text(rel, "isOfficer") == "1",
                "officer_title": _find_text(rel, "officerTitle"),
                "is_ten_percent_owner": _find_text(rel, "isTenPercentOwner") == "1",
                "is_other": _find_text(rel, "isOther") == "1",
                "other_text": _find_text(rel, "otherText"),
            }
        )

    footnotes = []
    for footnote in root.findall(".//footnote"):
        footnotes.append(
            {
                "footnote_id": footnote.attrib.get("id"),
                "footnote_text": (footnote.text or "").strip(),
            }
        )

    def _parse_tx(node: ET.Element):
        return {
            "security_title": _find_text(node.find("securityTitle"), "value") or _find_text(node, "securityTitle"),
            "transaction_date": _find_text(node.find("transactionDate"), "value") or _find_text(node, "transactionDate"),
            "transaction_code": _find_text(node.find("transactionCoding"), "transactionCode") or _find_text(node, "transactionCode"),
        }

    non_derivative = [_parse_tx(t) for t in root.findall(".//nonDerivativeTransaction")]
    derivative = [_parse_tx(t) for t in root.findall(".//derivativeTransaction")]

    return {
        "owners": owners,
        "non_derivative": non_derivative,
        "derivative": derivative,
        "footnotes": footnotes,
    }
