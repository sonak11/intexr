#!/usr/bin/env python3
"""Error audit for structured systems (paper: Analysis section).

  python3 scripts/error_audit.py --data paperB/data/medec_scope_v0.json \
      --preds results/medscope_*/preds_scope_pipeline@*_B.jsonl results/medscope_*/preds_scope_first@*_B.jsonl \
      --out results/ERROR_AUDIT.md

For every structured prediction file:
  - a gold x predicted label confusion matrix (claims), overall and per feedback condition;
  - for the scope-first pipeline (which records a trace), each wrong claim is attributed to the stage that caused it:
      align   missed contradiction (gold D, nothing direct found)    | spurious contradiction (gold K/P/U, pre-label D)
              missed conflict (gold U-evidence)                       | dispute treated as evidence (gold U-feedback, pre D)
              missed dispute (gold U-feedback, pre K)                 | missed dependency (gold P/U-dep, no changed parent)
      revise  missed propagation (P candidate answered UNCHANGED)     | over-propagation (P candidate changed, gold K)
      cascade a dependent claim inherits its parent's wrong label (e.g. gold U-dependency predicted P)
  - five example ids per category, so failures can be read in the predictions file.
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data  # noqa: E402

LABS = ("D", "P", "K", "U")


def stage_error(gold, pre, final):
    """Attribute one wrong claim of the pipeline. pre is the label before the propagation check ('P?' = candidate)."""
    gl, gt = gold["label"], gold.get("trigger")
    if gl == "D" and pre != "D":
        return "align: missed contradiction"
    if gl != "D" and pre == "D":
        return "align: dispute treated as evidence" if (gl == "U" and gt == "feedback") else "align: spurious contradiction"
    if gl == "U" and gt == "evidence" and pre != "U":
        return "align: missed conflict"
    if gl == "U" and gt == "feedback" and pre != "U":
        return "align: missed dispute"
    if gl == "P" and pre == "P?" and final == "K":
        return "revise: missed propagation (UNCHANGED)"
    if gl == "K" and pre == "P?" and final == "P":
        return "revise: over-propagation"
    if gl in ("P", "U") and pre not in ("P?", "U"):
        return "align: missed dependency"
    if gl in ("P", "U") and pre in ("P?", "U"):
        return "cascade: inherited a parent's error"
    if gl == "K" and pre == "U":
        return "align: spurious dispute or conflict"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--preds", nargs="+", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    by_id = {e["id"]: e for e in data.load(a.data)}
    md = ["# Error audit", "", f"Data: `{a.data}`", ""]
    for pat in a.preds:
        for f in sorted(glob.glob(pat)):
            preds = [json.loads(line) for line in open(f)]
            preds = [p for p in preds if p["id"] in by_id and p.get("structured") and any(
                "label" in c for c in p["claims"].values())]
            if not preds:
                continue
            name = re.sub(r"^preds_|\.jsonl$", "", os.path.basename(f))
            conf, stages, ex_ids = Counter(), Counter(), defaultdict(list)
            per_val = defaultdict(Counter)
            n_claims = n_wrong = 0
            for p in preds:
                ex = by_id[p["id"]]
                val = ex["gold"]["feedback_validity"]
                tr = p.get("trace", {})
                for cid, g in ex["gold"]["claims"].items():
                    pl = p["claims"][cid].get("label", "K")
                    conf[(g["label"], pl)] += 1
                    n_claims += 1
                    if pl != g["label"]:
                        n_wrong += 1
                        per_val[val]["wrong"] += 1
                        if tr:
                            s = stage_error(g, tr.get("labels_pre", {}).get(cid), pl)
                            stages[s] += 1
                            if len(ex_ids[s]) < 5:
                                ex_ids[s].append(f"{p['id']}:{cid}")
                    per_val[val]["n"] += 1
            md += [f"## {name}", "", f"{len(preds)} examples, {n_claims} claims, {n_wrong} wrong labels "
                   f"({n_wrong / max(n_claims, 1):.0%}).", "", "Confusion (rows gold, columns predicted):", "",
                   "| gold \\ pred | " + " | ".join(LABS) + " |", "|---|" + "---|" * len(LABS)]
            for g in LABS:
                md.append(f"| {g} | " + " | ".join(str(conf[(g, q)]) for q in LABS) + " |")
            md += ["", "Wrong-label rate by feedback condition: " + ", ".join(
                f"{v} {c['wrong'] / c['n']:.0%} (n={c['n']})" for v, c in sorted(per_val.items())), ""]
            if stages:
                md += ["| stage: error | claims | share of errors | examples |", "|---|---|---|---|"]
                for s, k in stages.most_common():
                    md.append(f"| {s} | {k} | {k / n_wrong:.0%} | {', '.join(ex_ids[s])} |")
                md.append("")
    text = "\n".join(md) + "\n"
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text)
    print(text)


if __name__ == "__main__":
    main()
