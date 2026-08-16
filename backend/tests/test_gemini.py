import pytest

from app.vision.gemini import parse_gemini_match, parse_gemini_matches


def test_parses_strict_gemini_json():
    parsed = parse_gemini_match('{"hero":"Aoi","role":"jungle","result":"win","kills":9,"deaths":1,"assists":4,"confidence":0.91}')
    assert parsed.hero == "Aoi"
    assert parsed.confidence == 0.91


def test_rejects_invalid_gemini_result():
    with pytest.raises(ValueError):
        parse_gemini_match('{"hero":"Aoi","role":"jungle","result":"unknown","kills":9,"deaths":1,"assists":4,"confidence":0.91}')


def test_parses_multiple_history_rows():
    parsed = parse_gemini_matches('{"matches":[{"hero":"Baldum","role":"support","result":"win","kills":4,"deaths":1,"assists":14,"confidence":0.95},{"hero":"Alice","role":"support","result":"loss","kills":0,"deaths":2,"assists":6,"confidence":0.91}]}')
    assert len(parsed) == 2
    assert parsed[1].hero == "Alice"
