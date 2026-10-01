import pytest
from eligibility import evaluate, required_slots


def ev(**p):
    return evaluate(p)


@pytest.mark.parametrize("age,expected", [(17, "criteria_not_met"), (18, "potential_match"), (60, "potential_match")])
def test_widow_age_boundary(age, expected):
    assert ev(marital_status="widow", age=age, assets_over_limit=False)["status"] == expected


@pytest.mark.parametrize("age,expected", [(29, "criteria_not_met"), (30, "potential_match")])
def test_deserted_age_boundary(age, expected):
    assert ev(marital_status="deserted", age=age, deserted_years=6, assets_over_limit=False)["status"] == expected


@pytest.mark.parametrize("years,expected", [(4, "criteria_not_met"), (5, "potential_match")])
def test_deserted_years_boundary(years, expected):
    assert ev(marital_status="deserted", age=40, deserted_years=years, assets_over_limit=False)["status"] == expected


def test_divorced_does_not_need_years_and_is_not_asked():
    assert "deserted_years" not in required_slots({"marital_status": "divorced"})
    assert ev(marital_status="divorced", age=35, assets_over_limit=False)["status"] == "potential_match"


@pytest.mark.parametrize("age,expected", [(49, "criteria_not_met"), (50, "potential_match")])
def test_unmarried_age_boundary(age, expected):
    assert ev(marital_status="unmarried", age=age, assets_over_limit=False)["status"] == expected


def test_assets_over_limit_blocks():
    r = ev(marital_status="widow", age=40, assets_over_limit=True)
    assert r["status"] == "criteria_not_met" and r["reasons"][0]["code"] == "assets"


def test_never_matches_without_the_asset_answer():
    assert ev(marital_status="widow", age=40)["status"] == "needs_info"


def test_married_is_not_applicable():
    assert ev(marital_status="married")["status"] == "not_applicable"


def test_age_reason_reports_wait_time():
    r = ev(marital_status="unmarried", age=46)
    assert r["reasons"][0] == {"code": "age", "min": 50, "wait": 4}
