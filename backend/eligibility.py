"""Deterministic eligibility. Rules mirror the official Tamil Nadu criteria in scheme_data.py.

Statuses: potential_match | criteria_not_met | needs_info.  It never says "eligible" - only the
government officer can confirm that.
"""
from typing import Any, Dict, List, Optional

from scheme_data import SCHEMES, SCHEME_FOR_STATUS


def scheme_for(profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    sid = SCHEME_FOR_STATUS.get(profile.get("marital_status"))
    return SCHEMES[sid] if sid else None


def required_slots(profile: Dict[str, Any]) -> List[str]:
    """Slots we still need, in the order Sakhi asks them."""
    status = profile.get("marital_status")
    if status is None:
        return ["marital_status"]
    if status == "married":
        return []
    slots = ["age"]
    if status == "deserted":
        slots.append("deserted_years")  # a divorced / court-separated woman does not need this
    slots.append("assets_over_limit")
    return slots


def evaluate(profile: Dict[str, Any]) -> Dict[str, Any]:
    scheme = scheme_for(profile)
    if scheme is None:
        return {"status": "not_applicable" if profile.get("marital_status") == "married" else "needs_info",
                "scheme": None, "reasons": [], "missing": required_slots(profile)}

    reasons: List[Dict[str, Any]] = []
    age = profile.get("age")
    if age is not None and age < scheme["age_min"]:
        reasons.append({"code": "age", "min": scheme["age_min"], "wait": scheme["age_min"] - age})

    years_min = scheme["deserted_years_min"]
    years = profile.get("deserted_years")
    if profile.get("marital_status") == "deserted" and years_min and years is not None and years < years_min:
        reasons.append({"code": "years", "min": years_min, "have": years})

    if profile.get("assets_over_limit") is True:
        reasons.append({"code": "assets"})

    missing = [s for s in required_slots(profile) if profile.get(s) is None]
    if reasons:
        status = "criteria_not_met"
    elif missing:
        status = "needs_info"
    else:
        status = "potential_match"
    return {"status": status, "scheme": scheme, "reasons": reasons, "missing": missing}
