from __future__ import annotations

from app.sec_client import SECClient


def fetch_filing_content(sec_client: SECClient, filing: dict) -> dict:
    html = None
    xml = None
    text = None
    if filing.get("primary_document_url"):
        body = sec_client.get_text(filing["primary_document_url"])
        text = body
        if "<html" in body.lower():
            html = body
        if "<?xml" in body.lower() or "<ownershipDocument" in body:
            xml = body
    return {"raw_html": html, "raw_xml": xml, "raw_text": text}
