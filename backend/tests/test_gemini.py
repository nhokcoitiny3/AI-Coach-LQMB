import pytest

from app.vision.gemini import parse_gemini_match


def test_parses_strict_gemini_json():
    parsed = parse_gemini_match('{"hero":"Aoi","role":"jungle","result":"win","kills":9,"deaths":1,"assists":4,"confidence":0.91}')
    assert parsed.hero == "Aoi"
    assert parsed.confidence == 0.91


def test_rejects_invalid_gemini_result():
    with pytest.raises(ValueError):
        parse_gemini_match('{"hero":"Aoi","role":"jungle","result":"unknown","kills":9,"deaths":1,"assists":4,"confidence":0.91}')
