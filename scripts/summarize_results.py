#!/usr/bin/env python3
"""Combine run_pilot.py outputs into the paper's result tables.

  python3 scripts/summarize_results.py --data paperB/data/medec_scope_v0.json \
      --runs results/medscope_gemini results/medscope_groq --out results/RESULTS_v0.md --tex paper1/tables/

Reads every preds_<system>@<model>_<cond>.jsonl in the run directories and reports:
  1. main table (condition B): change recall D / P, preservation error (K, K-supported), U F1, verdict acc,
     forbidden-addition rate, interaction exact; 95% CIs by bootstrap over source cases
  2. A vs B gap per system, with a PAIRED case-level bootstrap CI (same claims, both conditions)
  3. change recall on P by dependency depth (1 vs 2+)
  4. per feedback-validity stratum (condition B): preservation error and change recall
Only examples present in both the data file and the predictions are used.
"""
import argparse
import glob
import json
import os
import random
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data, metrics  # noqa: E402

MAIN = [("change_recall_D", "Chg-D"), ("change_recall_P", "Chg-P"), ("preservation_error_K", "PresErr-K"),
        ("preservation_error_Ksupported", "PresErr-K+"), ("unresolved_F1", "U-F1"), ("verdict_acc", "Verdict"),
        ("no_forbidden_additions", "NoForbid"), ("interaction_exact", "Exact")]
LOWER_BETTER = {"preservation_error_K", "preservation_error_Ksupported"}


def load_preds(runs):
    out = defaultdict(dict)  # (spec, cond) -> id -> pred
    for d in runs:
        for f in glob.glob(os.path.join(d, "preds_*.jsonl")):
            m = re.match(r"preds_(.+)_([ABCD])\.jsonl$", os.path.basename(f))
            if not m:
                continue
            spec, cond = m.group(1), m.group(2)
            with open(f) as fh:
                for line in fh:
                    p = json.loads(line)
                    out[(spec, cond)][p["id"]] = p
    return out


def fmt(v, ci=None):
    if v is None or v != v:
        return "–"
    return f"{v:.2f}" + (f" [{ci[0]:.2f}, {ci[1]:.2f}]" if ci else "")


def paired_gap(exs, pa, pb, key, n=2000, seed=0):
    """B minus A on the same examples; CI resamples source cases."""
    groups = defaultdict(list)
    for ex in exs:
        if ex["id"] in pa and ex["id"] in pb:
            groups[data.case_key(ex)].append((metrics.per_example(ex, pa[ex["id"]]), metrics.per_example(ex, pb[ex["id"]])))
    cl = list(groups.values())
    if not cl:
        return None, None

    def gap(sample):
        a = metrics.aggregate([x for c in sample for x, _ in c])[key]
        b = metrics.aggregate([y for c in sample for _, y in c])[key]
        return b - a
    point = gap(cl)
    rng = random.Random(seed)
    vs = sorted(v for v in (gap([cl[rng.randrange(len(cl))] for _ in cl]) for _ in range(n)) if v == v)
    return point, (vs[int(0.025 * len(vs))], vs[int(0.975 * len(vs)) - 1]) if vs else None


def depth_recall(exs, preds):
    hit, tot = defaultdict(float), defaultdict(float)
    for ex in exs:
        p = preds.get(ex["id"])
        if not p:
            continue
        for cid, g in ex["gold"]["claims"].items():
            if g["label"] != "P":
                continue
            d = data.depth(ex, cid) or 1
            k = "1" if d == 1 else "2+"
            tot[k] += 1
            hit[k] += p["claims"][cid]["status"] in metrics.CHANGED
    return {k: (hit[k] / tot[k], int(tot[k])) for k in tot}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--tex", default=None, help="directory for LaTeX table snippets")
    args = ap.parse_args()
    exs = data.load(args.data)
    by_id = {e["id"]: e for e in exs}
    preds = load_preds(args.runs)
    specs = sorted({s for s, _ in preds})
    md = [f"# Results — `{args.data}`", "",
          "Point estimate [95% CI, bootstrap over source cases]. PresErr: lower is better. "
          "K+ = K claims supported by evidence.", ""]
    tex_rows = []
    for cond in "ABCD":
        rows_c = [(s, preds[(s, cond)]) for s in specs if (s, cond) in preds]
        if not rows_c:
            continue
        md += [f"## Condition {cond}", "", "| system | n | " + " | ".join(h for _, h in MAIN) + " |",
               "|---|---|" + "---|" * len(MAIN)]
        for s, pr in rows_c:
            ex_s = [by_id[i] for i in pr if i in by_id]
            rows = [metrics.per_example(e, pr[e["id"]]) for e in ex_s]
            point, ci = metrics.bootstrap(rows, [data.case_key(e) for e in ex_s])
            md.append(f"| {s} | {len(rows)} | " + " | ".join(fmt(point.get(k), ci.get(k)) for k, _ in MAIN) + " |")
            if cond == "B":
                tex_rows.append(s.replace("_", r"\_") + " & " + " & ".join(fmt(point.get(k)) for k, _ in MAIN) + r" \\")
        md.append("")
    # A vs B
    gap_keys = ["change_recall_D", "change_recall_P", "preservation_error_K", "unresolved_F1", "interaction_exact"]
    md += ["## Cost of verification: B − A (same claims)", "",
           "Negative change recall / exact = worse when feedback must be verified; positive PresErr = more collateral change.", "",
           "| system | " + " | ".join(gap_keys) + " |", "|---|" + "---|" * len(gap_keys)]
    for s in specs:
        if (s, "A") in preds and (s, "B") in preds:
            cells = []
            for k in gap_keys:
                v, ci = paired_gap(exs, preds[(s, "A")], preds[(s, "B")], k)
                cells.append(fmt(v, ci))
            md.append(f"| {s} | " + " | ".join(cells) + " |")
    md += ["", "## Change recall on P by dependency depth (condition B)", "", "| system | depth 1 | depth 2+ |", "|---|---|---|"]
    for s in specs:
        if (s, "B") in preds:
            dr = depth_recall(exs, preds[(s, "B")])
            md.append(f"| {s} | " + " | ".join(f"{dr[k][0]:.2f} (n={dr[k][1]})" if k in dr else "–" for k in ("1", "2+")) + " |")
    md += ["", "## By feedback validity (condition B)", "",
           "| system | validity | n | Chg-D | Chg-P | PresErr-K | PresErr-K+ | U-F1 | Verdict |", "|---|---|---|---|---|---|---|---|---|"]
    for s in specs:
        pr = preds.get((s, "B"))
        if not pr:
            continue
        strata = defaultdict(list)
        for i, p in pr.items():
            if i in by_id:
                strata[by_id[i]["gold"]["feedback_validity"]].append(metrics.per_example(by_id[i], p))
        for v, rows in sorted(strata.items()):
            a = metrics.aggregate(rows)
            md.append(f"| {s} | {v} | {len(rows)} | " + " | ".join(fmt(a[k]) for k in (
                "change_recall_D", "change_recall_P", "preservation_error_K", "preservation_error_Ksupported",
                "unresolved_F1", "verdict_acc")) + " |")
    text = "\n".join(md) + "\n"
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w") as f:
            f.write(text)
    if args.tex and tex_rows:
        os.makedirs(args.tex, exist_ok=True)
        name = os.path.splitext(os.path.basename(args.data))[0]
        with open(os.path.join(args.tex, f"main_{name}.tex"), "w") as f:
            f.write("% generated by scripts/summarize_results.py — do not edit by hand\n" + "\n".join(tex_rows) + "\n")
    print(text)


if __name__ == "__main__":
    main()
