#!/usr/bin/env python3
"""Do the headline dev results survive removing doubtful data? (condition B, dev slice)

  python3 scripts/robustness.py [--out docs/14_robustness.md]

For every model x system with condition-B predictions, recomputes sycophancy (preservation error on
evidence-supported claims attacked by false feedback) and interaction-exact accuracy on:
  all             the 60-example dev slice
  -reviewed       without the 5 cases a clinician reviewed (their text changed after the runs)
  -flagged        without the authority-only items whose gold label the error analysis questioned
                  (ms-val-50, ms-val-303: the case text plus clinical knowledge already refutes the claim)
  -authority      without the whole authority-only cell
and the leave-one-case-out range of sycophancy (min-max over dropping each of the 20 source cases).
Also the verify-then-revise B-A sycophancy gap under the same subsets.
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data, metrics  # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from export_results import NAMES, SYSTEMS  # noqa: E402
from summarize_results import load_preds, paired_gap  # noqa: E402

REVIEWED = {"ms-val-514", "ms-val-30", "ms-val-185", "ms-val-333", "ms-val-520"}
FLAGGED = {"mscope-ms-val-50-authority", "mscope-ms-val-303-authority"}
SUBSETS = {
    "all": lambda e: True,
    "-reviewed": lambda e: e["id"].split("mscope-", 1)[1].rsplit("-", 1)[0] not in REVIEWED,
    "-flagged": lambda e: e["id"] not in FLAGGED,
    "-authority": lambda e: not e["id"].endswith("-authority"),
}
SHOW = ["evidence_prompt", "verify_revise", "scope_first", "scope_pipeline"]


def agg(exs, pr):
    rows = [metrics.per_example(e, pr[e["id"]]) for e in exs if e["id"] in pr]
    groups = [data.case_key(e) for e in exs if e["id"] in pr]
    return metrics.bootstrap(rows, groups, n=1000) if rows else (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="paperB/data/medec_scope_v0.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    by_id = {e["id"]: e for e in data.load(args.data)}
    preds = load_preds(sorted(glob.glob("results/medscope_*")))
    md = ["# Robustness of the dev results to doubtful data", "",
          "Condition B, dev slice. Syc = share of evidence-supported claims changed under false feedback (20 claims "
          "in the full slice); Exact = share of examples with every claim right. Brackets: 95% case-bootstrap "
          "intervals. LOO = range of Syc when any one of the 20 source cases is dropped.", "",
          "| model | system | Syc all | Syc -reviewed | Syc -flagged | LOO range | Exact all | Exact -reviewed | Exact -authority |",
          "|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for (spec, cond), pr in preds.items():
        if cond != "B" or "@" not in spec:
            continue
        sysname, model = spec.split("@", 1)
        if sysname not in SHOW or model not in NAMES:
            continue
        exs = [by_id[i] for i in pr if i in by_id]
        cell = {}
        for name, keep in SUBSETS.items():
            sub = [e for e in exs if keep(e)]
            cell[name] = agg(sub, pr)
        cases = sorted({data.case_key(e) for e in exs})
        loo = []
        for c in cases:
            sub = [e for e in exs if data.case_key(e) != c]
            rs = [metrics.per_example(e, pr[e["id"]]) for e in sub]
            v = metrics.aggregate(rs)["preservation_error_Ksupported"]
            if v == v:
                loo.append(v)

        def f(name, k):
            p, ci = cell[name]
            if p is None or p[k] != p[k]:
                return "–"
            return f"{p[k]:.2f} [{ci[k][0]:.2f}, {ci[k][1]:.2f}]" if k in ci else f"{p[k]:.2f}"
        rows.append((NAMES[model], SHOW.index(sysname), SYSTEMS[sysname], [
            f("all", "preservation_error_Ksupported"), f("-reviewed", "preservation_error_Ksupported"),
            f("-flagged", "preservation_error_Ksupported"), f"{min(loo):.2f}–{max(loo):.2f}" if loo else "–",
            f("all", "interaction_exact"), f("-reviewed", "interaction_exact"), f("-authority", "interaction_exact")]))
    order = list(NAMES.values())
    rows.sort(key=lambda r: (order.index(r[0]), r[1]))
    for m, _, s, cells in rows:
        md.append(f"| {m} | {s} | " + " | ".join(cells) + " |")
    md += ["", "## Verify-then-revise: sycophancy B - A on the same claims", "",
           "| model | all | -reviewed | -flagged |", "|---|---|---|---|"]
    for (spec, cond), pb in sorted(preds.items()):
        if cond != "B" or not spec.startswith("verify_revise@") or (spec, "A") not in preds:
            continue
        model = spec.split("@", 1)[1]
        cells = []
        for name in ("all", "-reviewed", "-flagged"):
            exs = [e for e in by_id.values() if SUBSETS[name](e)]
            g, ci = paired_gap(exs, preds[(spec, "A")], pb, "preservation_error_Ksupported", n=1000)
            cells.append(f"{g:+.2f} [{ci[0]:+.2f}, {ci[1]:+.2f}]" if g is not None else "–")
        md.append(f"| {NAMES.get(model, model)} | " + " | ".join(cells) + " |")
    text = "\n".join(md) + "\n"
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
    print(text)


if __name__ == "__main__":
    main()
