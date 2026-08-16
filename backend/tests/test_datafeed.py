from bs4 import BeautifulSoup

from app.datafeed.collectors import _lq_role, _rov_role
from app.datafeed.normalizer import normalize_name, normalize_role


def test_normalizes_vietnamese_hero_aliases_for_matching():
    assert normalize_name("Tel’Annas") == "telannas"
    assert normalize_name("Điêu Thuyền") == "dieuthuyen"


def test_extracts_lien_quan_role_without_fixture_data():
    soup = BeautifulSoup("<p>Vị trí:</p><p>Pháp sư, Cấu rỉa</p>", "html.parser")
    assert normalize_role(_lq_role(soup)) == "mid"


def test_extracts_rov_lane_from_hero_page():
    soup = BeautifulSoup("<div>Aoi S TIER assassin Jungle Hard</div>", "html.parser")
    assert normalize_role(_rov_role(soup)) == "jungle"


def test_extracts_rov_class_when_the_page_has_no_explicit_lane():
    soup = BeautifulSoup("<div>Violet S TIER marksman Marksman / ADC Medium</div>", "html.parser")
    assert normalize_role(_rov_role(soup)) == "dragon"
