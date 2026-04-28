from app.parsers.sc13 import parse_sc13_text


def test_sc13_signal_detection():
    parsed = parse_sc13_text("The purpose of transaction is strategic control")
    cats = {s["signal_category"] for s in parsed["signals"]}
    assert "purpose_of_transaction" in cats
    assert "activist_or_control_intent" in cats
