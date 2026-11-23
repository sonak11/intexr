#!/usr/bin/env python3
"""Non-medical replication table: does the MedScope pattern hold on EditPropBench and VitaminC?

  python3 scripts/external_summary.py [--tag _v1]

For each set, model and system: sycophancy (preservation error on evidence-supported claims attacked by false
feedback) under a verified edit (A) and unverified feedback (B), the paired B - A change on the same claims with a
95% source-item bootstrap interval, propagation recall (EditPropBench) or U-F1 (VitaminC), and exact accuracy.
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data, metrics  # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from export_results import NAMES, SYSTEMS  # noqa: E402
from summarize_results import load_preds, paired_gap  # noqa: E402

SETS = {"epb": ("EditPropBench-IX", "external/editpropbench_intexr{tag}.json", "change_recall_P", "Chg-P"),
        "vitc": ("VitaminC-IX", "external/vitaminc_intexr{tag}.json", "unresolved_F1", "U-F1")}
ORDER = ["evidence_prompt", "dialogue", "verify_revise", "scope_first", "scope_pipeline"]


def f(v):
    return "–" if v is None or v != v else f"{v:.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="_v1")
    a = ap.parse_args()
    out = ["# Non-medical replication", "",
           "Syc = share of evidence-supported claims changed when false feedback attacks them. A = verified edit, "
           "B = unverified feedback plus evidence; B − A is paired on the same claims (95% bootstrap over source "
           "items; * = interval excludes 0).", ""]
    for key, (title, path, extra, extra_h) in SETS.items():
        path = path.format(tag=a.tag)
        if not os.path.exists(path):
            out += [f"## {title}", "", f"(no data: {path})", ""]
            continue
        exs = data.load(path)
        by_id = {e["id"]: e for e in exs}
        preds = load_preds(sorted(glob.glob(f"results/{key}{a.tag}_*")))
        n_src = len({data.case_key(e) for e in exs})
        out += [f"## {title} ({len(exs)} examples, {n_src} source items)", "",
                f"| model | system | Syc A | Syc B | Syc B − A | {extra_h} B | Exact B |", "|---|---|---|---|---|---|---|"]
        rows = []
        for (spec, cond), pb in preds.items():
            if cond != "B" or "@" not in spec:
                continue
            sysname, model = spec.split("@", 1)
            if sysname not in ORDER:
                continue
            pa = preds.get((spec, "A"), {})

            def agg(pr):
                rs = [metrics.per_example(by_id[i], p) for i, p in pr.items() if i in by_id]
                return metrics.aggregate(rs) if rs else {}
            ma, mb = agg(pa), agg(pb)
            g, ci = paired_gap(exs, pa, pb, "preservation_error_Ksupported") if pa else (None, None)
            gs = "–" if g is None else f"{g:+.2f} [{ci[0]:+.2f}, {ci[1]:+.2f}]" + (" *" if ci and (ci[0] > 0 or ci[1] < 0) else "")
            rows.append((list(NAMES).index(model) if model in NAMES else 99, ORDER.index(sysname),
                         f"| {NAMES.get(model, model)} | {SYSTEMS.get(sysname, sysname)} | "
                         f"{f(ma.get('preservation_error_Ksupported'))} | {f(mb.get('preservation_error_Ksupported'))} | {gs} | "
                         f"{f(mb.get(extra))} | {f(mb.get('interaction_exact'))} |"))
        out += [r[2] for r in sorted(rows)] + [""]
    print("\n".join(out))


if __name__ == "__main__":
    main()
