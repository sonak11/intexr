"""Pilot systems. Each returns a prediction dict:

{"id", "system", "revised_response", "claims": {cid: {"label"?, "status", "revised_text"?}},
 "verdict"?, "structured": bool, "raw"?}

status ∈ keep|revised|removed|hedged (what was done to the claim).
label ∈ D|P|K|U (only for structured systems: what the system says it did).
"""
import re

from . import prompts
from .data import model_view

_STOP = set("""a an the is are was were be been of in on at to for and or but not no it its this that with as by from
he she they his her their there here i you we our your me my do does did have has had so very just also only about
actually really definitely please some any one side wrong right sure""".split())


def _status_from_label(label, revised_text):
    if label == "K":
        return "keep"
    if label == "U":
        return "hedged"
    return "removed" if revised_text is None else "revised"


# ---------------------------------------------------------------- offline baselines
def no_revision(ex, **_):
    return {"id": ex["id"], "system": "no_revision", "structured": True, "verdict": "reject",
            "revised_response": ex["original_response"],
            "claims": {c["id"]: {"label": "K", "status": "keep"} for c in ex["claims"]}}


def accept_feedback_lexical(ex, **_):
    """Scope-only heuristic: a claim is 'directly updated' iff it shares a content word with the feedback.
    No text is generated, so text checks fail by construction; use it only for scope metrics."""
    fb = set(w for w in re.findall(r"[a-z]+", ex["feedback"]["text"].lower()) if w not in _STOP and len(w) > 2)
    claims = {}
    for c in ex["claims"]:
        words = set(re.findall(r"[a-z]+", c["text"].lower()))
        hit = bool(fb & words)
        claims[c["id"]] = {"label": "D" if hit else "K", "status": "revised" if hit else "keep"}
    return {"id": ex["id"], "system": "accept_feedback_lexical", "structured": True, "verdict": "accept",
            "revised_response": ex["original_response"], "claims": claims}


def oracle(ex, **_):
    g = ex["gold"]
    claims = {cid: {"label": v["label"], "revised_text": v.get("target_text"),
                    "status": _status_from_label(v["label"], v.get("target_text"))}
              for cid, v in g["claims"].items()}
    return {"id": ex["id"], "system": "oracle", "structured": True, "verdict": g["feedback_verdict"],
            "revised_response": g["target_revision"], "claims": claims}


# ---------------------------------------------------------------- LLM systems
def _judge_statuses(ex, revised, judge):
    sys_, msgs = prompts.judge_messages(ex, revised)
    try:
        out = prompts.parse_json(judge(sys_, msgs))
    except Exception as e:  # noqa: BLE001
        return {c["id"]: {"status": "keep", "judge_error": str(e)} for c in ex["claims"]}
    return {c["id"]: {"status": out.get(c["id"], "keep")} for c in ex["claims"]}


def free_text_system(name, builder):
    def run(ex, client, judge, condition="B", **_):
        v = model_view(ex, condition)
        sys_, msgs = builder(v)
        revised = client(sys_, msgs).strip()
        return {"id": ex["id"], "system": name, "structured": False, "revised_response": revised,
                "claims": _judge_statuses(ex, revised, judge)}
    return run


def scope_first(ex, client, judge=None, condition="B", **_):
    v = model_view(ex, condition)
    sys_, msgs = prompts.scope_messages(v)
    raw = client(sys_, msgs)
    try:
        out = prompts.parse_json(raw)
    except Exception as e:  # noqa: BLE001
        return {"id": ex["id"], "system": "scope_first", "structured": True, "parse_error": str(e), "raw": raw,
                "revised_response": ex["original_response"], "verdict": None,
                "claims": {c["id"]: {"label": "K", "status": "keep"} for c in ex["claims"]}}
    by_id = {c.get("id"): c for c in out.get("claims", [])}
    claims = {}
    for c in ex["claims"]:
        p = by_id.get(c["id"], {"label": "K"})
        lab = p.get("label", "K") if p.get("label") in ("D", "P", "K", "U") else "K"
        claims[c["id"]] = {"label": lab, "revised_text": p.get("revised_text"),
                           "depends_on": p.get("depends_on", []),
                           "status": _status_from_label(lab, p.get("revised_text"))}
    pred = {"id": ex["id"], "system": "scope_first", "structured": True,
            "verdict": out.get("feedback_assessment", {}).get("verdict"),
            "revised_response": out.get("revised_response", ""), "claims": claims}
    if judge is not None:  # does the text actually do what the labels say?
        pred["judged_claims"] = _judge_statuses(ex, pred["revised_response"], judge)
    return pred


SYSTEMS = {
    "no_revision": no_revision,
    "accept_feedback_lexical": accept_feedback_lexical,
    "oracle": oracle,
    "dialogue": free_text_system("dialogue", prompts.dialogue_messages),
    "evidence_prompt": free_text_system("evidence_prompt", prompts.evidence_messages),
    "always_rewrite": free_text_system("always_rewrite", prompts.rewrite_messages),
    "scope_first": scope_first,
}
OFFLINE = {"no_revision", "accept_feedback_lexical", "oracle"}
