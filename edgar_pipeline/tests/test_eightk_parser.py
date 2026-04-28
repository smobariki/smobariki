from app.parsers.eightk import classify_eightk_events, parse_eightk_sections


def test_parse_eightk_sections_extracts_items():
    text = "Item 1.01 Entry into a Material Definitive Agreement. body. Item 2.02 Results of Operations and Financial Condition."
    items = parse_eightk_sections(text)
    assert len(items) == 2
    assert items[0]["item_number"] == "1.01"


def test_classify_eightk_events_matches_keywords():
    tags = classify_eightk_events("This earnings release announces results of operations")
    categories = {t["event_category"] for t in tags}
    assert "earnings_release" in categories
