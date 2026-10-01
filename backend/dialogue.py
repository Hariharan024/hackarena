"""The conversation engine: one question at a time, state lives in the client's profile (stateless server)."""
from typing import Any, Callable, Dict, List, Optional

import nlu
from eligibility import evaluate, required_slots
from messages import CHIP, STATUS_OPTIONS, t
from scheme_data import ASSET_LIMIT_RUPEES, DOCUMENTS, LAST_VERIFIED, SOURCES

Extractor = Callable[[str, Optional[str]], Dict[str, Any]]
SLOTS = ("marital_status", "age", "deserted_years", "assets_over_limit")
VALID_STATUS = {o["value"] for o in STATUS_OPTIONS}


# ---------------------------------------------------------------- profile hygiene
def clean_profile(raw: Dict[str, Any]) -> Dict[str, Any]:
    p: Dict[str, Any] = {}
    if raw.get("marital_status") in VALID_STATUS:
        p["marital_status"] = raw["marital_status"]
    for key, lo, hi in (("age", 10, 110), ("deserted_years", 0, 60)):
        v = raw.get(key)
        if isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi:
            p[key] = v
    if isinstance(raw.get("assets_over_limit"), bool):
        p["assets_over_limit"] = raw["assets_over_limit"]
    docs = [d for d in (raw.get("docs_ready") or []) if d in DOCUMENTS]
    if docs:
        p["docs_ready"] = sorted(set(docs))
    if p.get("marital_status") != "deserted":
        p.pop("deserted_years", None)  # irrelevant for everyone but "husband left"
    return p


def merge(profile: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(profile)
    for key, value in facts.items():
        if key == "docs_ready":
            merged["docs_ready"] = sorted(set(merged.get("docs_ready", [])) | set(value))
        elif value is not None:
            merged[key] = value
    return clean_profile(merged)


def clear_slot(profile: Dict[str, Any], slot: str) -> Dict[str, Any]:
    p = dict(profile)
    p.pop(slot, None)
    if slot == "marital_status":
        p.pop("deserted_years", None)
    return p


# ---------------------------------------------------------------- presentation
def understood(profile: Dict[str, Any], lang: str) -> List[Dict[str, Any]]:
    chips = []
    if "marital_status" in profile:
        opt = next(o for o in STATUS_OPTIONS if o["value"] == profile["marital_status"])
        chips.append({"slot": "marital_status", "icon": opt["icon"], "text": opt["label"][lang]})
    if "age" in profile:
        chips.append({"slot": "age", "icon": "🎂", "text": CHIP["age"][lang].format(v=profile["age"])})
    if "deserted_years" in profile:
        chips.append({"slot": "deserted_years", "icon": "📅", "text": CHIP["years"][lang].format(v=profile["deserted_years"])})
    if "assets_over_limit" in profile:
        key = "assets_yes" if profile["assets_over_limit"] else "assets_no"
        chips.append({"slot": "assets_over_limit", "icon": "🏡", "text": CHIP[key][lang]})
    return chips


def step_for(slot: str, lang: str) -> Dict[str, Any]:
    if slot == "marital_status":
        return {"id": "situation", "slot": slot, "input": "choice",
                "options": [{"value": o["value"], "icon": o["icon"], "label": o["label"][lang]} for o in STATUS_OPTIONS]}
    if slot == "age":
        return {"id": "age", "slot": slot, "input": "number", "min": 18, "max": 100, "default": 40}
    if slot == "deserted_years":
        return {"id": "years", "slot": slot, "input": "number", "min": 0, "max": 40, "default": 5}
    yes_no = ({"ta": ("இல்லை", "இருக்கு"), "en": ("No", "Yes")})[lang]
    return {"id": "assets", "slot": slot, "input": "yesno",
            "options": [{"value": False, "icon": "👍", "label": yes_no[0]}, {"value": True, "icon": "🏡", "label": yes_no[1]}]}


PROMPT_KEY = {"marital_status": "ask_situation", "age": "ask_age", "deserted_years": "ask_years", "assets_over_limit": "ask_assets"}


def _money(n: int) -> str:
    return f"{n:,}"


def build_result(profile: Dict[str, Any], ev: Dict[str, Any], lang: str) -> Dict[str, Any]:
    scheme, status = ev["scheme"], ev["status"]
    docs_ready = set(profile.get("docs_ready", []))
    result: Dict[str, Any] = {"status": status, "reasons": [r["code"] for r in ev["reasons"]], "verified_on": LAST_VERIFIED}
    sources = [SOURCES["eligibility"], SOURCES["amount"], SOURCES["esevai"]]
    result["sources"] = [{"title": s["title"][lang], "url": s["url"]} for s in sources]

    if status == "not_applicable":
        result.update(headline=t("headline_na", lang), message=t("married", lang), scheme=None, documents=[], steps=[])
        return result
    if status == "criteria_not_met":
        r = ev["reasons"][0]
        if r["code"] == "age":
            msg = t("not_age", lang, min=r["min"], n=r["wait"])
        elif r["code"] == "years":
            msg = t("not_years", lang, min=r["min"])
        else:
            msg = t("not_assets", lang)
        result.update(headline=t("headline_no", lang), message=msg, documents=[], steps=[])
        result["scheme"] = {"id": scheme["id"], "name": scheme["name"][lang], "short": scheme["short"][lang]}
        return result

    amount = _money(scheme["amount"])
    docs = [{"key": k, "label": DOCUMENTS[k][lang], "icon": DOCUMENTS[k]["icon"], "ready": k in docs_ready} for k in scheme["documents"]]
    steps = [{"icon": "📋", "text": t("step1", lang)}, {"icon": "🏛️", "text": t("step2", lang)}, {"icon": "🙋", "text": t("step3", lang)}]
    message = t("match", lang, scheme=scheme["short"][lang], amount=amount)
    share = "\n".join([f"*{t('share_title', lang)}*", scheme["name"][lang], t("amount_per_month", lang, amount=amount), "",
                       t("share_docs", lang), *[f"- {d['label']}" for d in docs], "", t("share_go", lang), SOURCES["eligibility"]["url"]])
    result.update(headline=t("headline_match", lang), message=message, steps=steps, documents=docs,
                  scheme={"id": scheme["id"], "name": scheme["name"][lang], "short": scheme["short"][lang],
                          "amount": t("amount_per_month", lang, amount=amount)},
                  share_text=share, asset_limit=ASSET_LIMIT_RUPEES)
    return result


# ---------------------------------------------------------------- one conversation turn
def handle_turn(lang: str, profile: Dict[str, Any], *, message: Optional[str] = None, answer: Optional[Dict[str, Any]] = None,
                ask: Optional[str] = None, start: bool = False, pending: Optional[str] = None,
                extractor: Optional[Extractor] = None) -> Dict[str, Any]:
    profile = clean_profile(profile)
    prefix = ""
    not_understood = False

    if start:
        prefix = "WELCOME" if not profile else ""
    elif ask:
        profile = clear_slot(profile, ask)
    elif answer is not None:
        profile = merge(profile, {answer["slot"]: answer["value"]})
        prefix = t("ack", lang)
    elif message:
        facts = nlu.extract(message, pending, profile)
        wanted = pending or "marital_status"
        if wanted not in facts and extractor:
            for key, value in (extractor(message, pending) or {}).items():
                facts.setdefault(key, value)
        if any(k in facts for k in SLOTS):
            profile = merge(profile, facts)
            prefix = t("ack", lang)
        else:
            not_understood = True
            prefix = t("not_understood", lang)

    ev = evaluate(profile)
    missing_now = None if ev["status"] in ("criteria_not_met", "not_applicable", "potential_match") else ev["missing"][0]

    if missing_now:
        step = step_for(missing_now, lang)
        question = t(PROMPT_KEY[missing_now], lang)
        reply = t("welcome", lang) if prefix == "WELCOME" else f"{prefix} {question}".strip()
        result = None
    else:
        result = build_result(profile, ev, lang)
        step = {"id": "result", "slot": None, "input": "none"}
        reply = result["message"]

    return {"reply": reply, "lang": lang, "profile": profile, "understood": understood(profile, lang),
            "step": step, "result": result, "not_understood": not_understood}
