"""Loading, validation, and model-facing views of IntExR-Scope examples."""
import json
from collections import Counter

from . import LABELS, VERDICTS, VALIDITY


def load(path):
    with open(path) as f:
        obj = json.load(f)
    return obj["examples"] if isinstance(obj, dict) else obj


def validate(ex):
    """Return a list of problems (empty if the example is well-formed)."""
    errs = []
    cid = [c["id"] for c in ex["claims"]]
    gold = ex["gold"]
    if len(set(cid)) != len(cid):
        errs.append("duplicate claim ids")
    if set(gold["claims"]) != set(cid):
        errs.append(f"gold claims {sorted(gold['claims'])} != claims {cid}")
    for c in ex["claims"]:
        if c["text"] not in ex["original_response"]:
            errs.append(f"{c['id']} text not a span of original_response")
    ev_ids = {e["id"] for e in ex["prior_evidence"] + ex["new_evidence"]}
    for k, g in gold["claims"].items():
        if g["label"] not in LABELS:
            errs.append(f"{k}: bad label {g['label']}")
        if g["label"] in ("D", "P", "U") and "target_text" not in g and not gold.get("no_target_text"):
            errs.append(f"{k}: {g['label']} needs target_text (null = delete)")
        if g["label"] == "U" and g.get("target_text") is None:
            errs.append(f"{k}: U claims must be hedged, not deleted")
        if g["label"] == "K" and g.get("support") not in ("supported", "unverified"):
            errs.append(f"{k}: K needs support=supported|unverified")
        for e in g.get("evidence", []):
            if e not in ev_ids:
                errs.append(f"{k}: unknown evidence id {e}")
    for a, b in gold["dependencies"]:
        if a not in cid or b not in cid:
            errs.append(f"bad dependency {a}->{b}")
    # P claims must have a D (or P) ancestor; U-dependency must have a U ancestor.
    parents = {}
    for a, b in gold["dependencies"]:
        parents.setdefault(b, []).append(a)
    for k, g in gold["claims"].items():
        if g["label"] == "P" and not any(gold["claims"][p]["label"] in ("D", "P") for p in parents.get(k, [])):
            errs.append(f"{k}: P without a D/P parent")
        if g.get("trigger") == "dependency" and g["label"] == "U" and not any(
            gold["claims"][p]["label"] == "U" for p in parents.get(k, [])
        ):
            errs.append(f"{k}: U-dependency without a U parent")
    if gold["feedback_verdict"] not in VERDICTS:
        errs.append("bad feedback_verdict")
    if gold["feedback_validity"] not in VALIDITY:
        errs.append("bad feedback_validity")
    return errs


def depth(ex, cid):
    """Longest dependency path from a D claim to cid (0 for D, None if unrelated)."""
    gold = ex["gold"]
    parents = {}
    for a, b in gold["dependencies"]:
        parents.setdefault(b, []).append(a)
    lab = gold["claims"][cid]["label"]
    if lab == "D":
        return 0
    ds = [depth(ex, p) for p in parents.get(cid, []) if gold["claims"][p]["label"] in ("D", "P")]
    ds = [d for d in ds if d is not None]
    return 1 + max(ds) if ds else None


def model_view(ex, condition="B"):
    """The input a system sees. Gold, dependencies, and validity are never included.

    A: verified direct edits replace feedback (EditPropBench-style).
    B: unverified feedback + new evidence (IntExR default).
    C: new evidence only (no feedback).
    D: feedback only (no new evidence).
    """
    view = {
        "id": ex["id"],
        "context": ex["context"],
        "original_response": ex["original_response"],
        "claims": ex["claims"],
        "prior_evidence": [{k: e[k] for k in ("id", "text", "provenance")} for e in ex["prior_evidence"]],
        "feedback": {"speaker_role": ex["feedback"]["speaker_role"], "text": ex["feedback"]["text"]},
        "new_evidence": [{k: e[k] for k in e if k in ("id", "text", "provenance", "time")} for e in ex["new_evidence"]],
    }
    if condition == "A":
        edits = [
            f'"{c["text"]}" -> ' + (f'"{g["target_text"]}"' if g["target_text"] else "(delete)")
            for c in ex["claims"]
            for g in [ex["gold"]["claims"][c["id"]]]
            if g["label"] == "D"
        ]
        view["feedback"] = {
            "speaker_role": "verified_editor",
            "text": "VERIFIED CORRECTIONS (apply these; they are correct): " + ("; ".join(edits) or "none"),
        }
    elif condition == "C":
        view["feedback"] = None
    elif condition == "D":
        view["new_evidence"] = []
    return view


def summarize(examples):
    lab = Counter(g["label"] for ex in examples for g in ex["gold"]["claims"].values())
    val = Counter(ex["gold"]["feedback_validity"] for ex in examples)
    dom = Counter(ex["domain"] for ex in examples)
    trig = Counter(
        f"{g['label']}-{g.get('trigger', g.get('support'))}" for ex in examples for g in ex["gold"]["claims"].values()
    )
    deps = Counter(depth(ex, c) for ex in examples for c, g in ex["gold"]["claims"].items() if g["label"] == "P")
    return {"n_examples": len(examples), "n_claims": sum(lab.values()), "domains": dict(dom),
            "labels": dict(lab), "label_triggers": dict(trig), "feedback_validity": dict(val),
            "P_depth": {str(k): v for k, v in deps.items()}}
