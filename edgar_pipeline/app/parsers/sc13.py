from __future__ import annotations

SC13_SIGNAL_RULES = {
    "activist_or_control_intent": ["control", "solicit"],
    "passive_ownership": ["passive"],
    "ownership_increase": ["increased", "acquired"],
    "ownership_decrease": ["decreased", "disposed"],
    "large_holder_entry": ["beneficial owner"],
    "source_of_funds": ["source and amount of funds"],
    "purpose_of_transaction": ["purpose of transaction"],
    "governance_or_board_pressure": ["board", "governance"],
    "merger_or_strategic_transaction_interest": ["merger", "strategic"],
}


def parse_sc13_text(raw_text: str | None) -> dict:
    if not raw_text:
        return {"sections": [], "signals": []}
    signals = []
    low = raw_text.lower()
    for category, keywords in SC13_SIGNAL_RULES.items():
        for keyword in keywords:
            if keyword in low:
                signals.append(
                    {
                        "signal_category": category,
                        "signal_keyword": keyword,
                        "matched_text": keyword,
                        "confidence_method": "rule_based_keyword",
                    }
                )
    sections = [{"section_name": "full_text", "section_text": raw_text[:20000]}]
    return {"sections": sections, "signals": signals}
