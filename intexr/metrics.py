"""Claim- and interaction-level metrics with source-case bootstrap CIs."""
import random
import re
from collections import defaultdict

CHANGED = ("revised", "removed")


def _has(text, term):
    return re.search(r"(?<![a-z])" + re.escape(term.lower()), text.lower()) is not None


def check_claim(revised_response, checks):
    """Deterministic pilot proxy for 'the revision says the right thing' (applied to the full response)."""
    if not checks:
        return None
    if any(_has(revised_response, t) for t in checks.get("must_not_contain", [])):
        return False
    need = checks.get("must_contain_any", [])
    return any(_has(revised_response, t) for t in need) if need else True


def _status_ok(gold_label, status):
    return {"D": status in CHANGED, "P": status in CHANGED, "K": status == "keep", "U": status == "hedged"}[gold_label]


def per_example(ex, pred, statuses_key="claims"):
    """Raw counts for one example; aggregated later so CIs resample whole source cases."""
    g = ex["gold"]["claims"]
    pc = pred[statuses_key]
    r = defaultdict(float)
    for cid, gv in g.items():
        lab, st = gv["label"], pc[cid]["status"]
        r[f"n_{lab}"] += 1
        if lab in ("D", "P"):
            r[f"chg_{lab}"] += st in CHANGED
            r[f"hedge_{lab}"] += st == "hedged"
            r["under"] += st == "keep"
        if lab == "K":
            r["k_changed"] += st != "keep"
            if gv.get("support") == "supported":
                r["n_Ksup"] += 1
                r["ksup_changed"] += st != "keep"
        # unresolved detection (hedged == predicted U)
        r["u_tp"] += lab == "U" and st == "hedged"
        r["u_fp"] += lab != "U" and st == "hedged"
        r["u_fn"] += lab == "U" and st != "hedged"
        r["claim_ok"] += _status_ok(lab, st)
        ok = check_claim(pred["revised_response"], gv.get("checks"))
        if ok is not None:
            r["chk_n"] += 1
            r["chk_ok"] += ok
        # exact labels (structured systems)
        pl = pc[cid].get("label")
        if pl is not None and statuses_key == "claims" and pred.get("structured"):
            for L in ("D", "P", "U"):
                r[f"{L}_tp"] += lab == L and pl == L
                r[f"{L}_fp"] += lab != L and pl == L
                r[f"{L}_fn"] += lab == L and pl != L
            r["label_ok"] += lab == pl
            r["has_labels"] = 1
    forb = ex["gold"].get("forbidden_additions", [])
    if forb:
        r["forb_n"] += 1
        r["forb_ok"] += not any(_has(pred["revised_response"], t) for t in forb)
    r["n_claims"] = len(g)
    r["exact"] = float(r["claim_ok"] == len(g))
    if pred.get("verdict") is not None:
        r["verdict_n"] = 1
        r["verdict_ok"] = float(pred["verdict"] == ex["gold"]["feedback_verdict"])
    return dict(r)


def _div(a, b):
    return a / b if b else float("nan")


def _f1(tp, fp, fn):
    p, rc = _div(tp, tp + fp), _div(tp, tp + fn)
    return _div(2 * p * rc, p + rc) if tp else (0.0 if (tp + fp + fn) else float("nan"))


def aggregate(rows):
    s = defaultdict(float)
    for r in rows:
        for k, v in r.items():
            s[k] += v
    m = {
        "change_recall_D": _div(s["chg_D"], s["n_D"]),
        "change_recall_P": _div(s["chg_P"], s["n_P"]),
        "under_revision": _div(s["under"], s["n_D"] + s["n_P"]),
        "preservation_error_K": _div(s["k_changed"], s["n_K"]),
        "preservation_error_Ksupported": _div(s["ksup_changed"], s["n_Ksup"]),
        "unresolved_F1": _f1(s["u_tp"], s["u_fp"], s["u_fn"]),
        "claim_action_acc": _div(s["claim_ok"], s["n_claims"]),
        "interaction_exact": _div(s["exact"], len(rows)),
        "check_pass": _div(s["chk_ok"], s["chk_n"]),
        "no_forbidden_additions": _div(s["forb_ok"], s["forb_n"]),
        "verdict_acc": _div(s["verdict_ok"], s["verdict_n"]),
    }
    if s["has_labels"]:
        m.update({"direct_F1": _f1(s["D_tp"], s["D_fp"], s["D_fn"]),
                  "propagation_F1": _f1(s["P_tp"], s["P_fp"], s["P_fn"]),
                  "label_acc": _div(s["label_ok"], s["n_claims"])})
    return m


def bootstrap(rows, n=2000, seed=0):
    rng = random.Random(seed)
    point = aggregate(rows)
    samples = defaultdict(list)
    for _ in range(n):
        agg = aggregate([rows[rng.randrange(len(rows))] for _ in rows])
        for k, v in agg.items():
            if v == v:  # not NaN
                samples[k].append(v)
    ci = {}
    for k, vs in samples.items():
        vs.sort()
        ci[k] = (vs[int(0.025 * len(vs))], vs[int(0.975 * len(vs)) - 1]) if vs else (float("nan"),) * 2
    return point, ci
