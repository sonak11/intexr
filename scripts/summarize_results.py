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
  5. by model scale (--tiers configs/model_tiers.tsv): one row per model, ordered by family and size
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
            m = re.match(r"preds_(.+)_([ABCDE])\.jsonl$", os.path.basename(f))
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


def load_tiers(path):
    """model tag as it appears in prediction file names -> roster row"""
    if not path or not os.path.exists(path):
        return {}
    with open(path) as f:
        lines = [ln.rstrip("\n").split("\t") for ln in f if ln.strip() and not ln.startswith("#")]
    head = lines[0]
    return {r[0].replace(":", "_").replace("/", "_"): dict(zip(head, r)) for r in lines[1:]}


def scale_table(exs, by_id, preds, tiers_path):
    """One row per model: does propagation, sycophancy or hedging change with scale / family?"""
    tiers = load_tiers(tiers_path)
    models = sorted({s.split("@", 1)[1] for s, _ in preds if "@" in s})
    if not models:
        return []

    def agg(spec, cond):
        pr = preds.get((spec, cond))
        if not pr:
            return {}
        ex_s = [by_id[i] for i in pr if i in by_id]
        return metrics.aggregate([metrics.per_example(e, pr[e["id"]]) for e in ex_s])

    def size(m):
        try:
            return float(tiers.get(m, {}).get("params_b", "inf"))
        except ValueError:
            return float("inf")
    models.sort(key=lambda m: (tiers.get(m, {}).get("family", "~"), size(m), m))
    out = ["", "## By model scale (condition B unless marked; dev unless the run used --split test)", "",
           "Prompt = evidence_prompt, Pipe = scope_pipeline. Syc = PresErr-K+ (evidence-supported claims changed "
           "under false feedback). A-Chg-P = bare verified edit.", "",
           "| model | family | params (B) | tier | review | Prompt A-Chg-P | Prompt Chg-P | Prompt Syc | Prompt U-F1 "
           "| Prompt Exact | Pipe Chg-P | Pipe Syc | Pipe Verdict | Pipe Exact |", "|---|---|---|---|---|" + "---|" * 9]
    for m in models:
        t = tiers.get(m, {})
        pa, pb, sb = agg(f"evidence_prompt@{m}", "A"), agg(f"evidence_prompt@{m}", "B"), agg(f"scope_pipeline@{m}", "B")
        cells = [pa.get("change_recall_P"), pb.get("change_recall_P"), pb.get("preservation_error_Ksupported"),
                 pb.get("unresolved_F1"), pb.get("interaction_exact"), sb.get("change_recall_P"),
                 sb.get("preservation_error_Ksupported"), sb.get("verdict_acc"), sb.get("interaction_exact")]
        out.append(f"| {m} | {t.get('family', '?')} | {t.get('params_b', '?')} | {t.get('tier', '?')} | "
                   f"{'yes' if t.get('review') == '1' else ''} | " + " | ".join(fmt(c) for c in cells) + " |")
    return out + [""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--tex", default=None, help="directory for LaTeX table snippets")
    ap.add_argument("--tiers", default=os.path.join(os.path.dirname(__file__), "..", "configs", "model_tiers.tsv"),
                    help="model roster (family, size, tier) for the scale table")
    args = ap.parse_args()
    exs = data.load(args.data)
    by_id = {e["id"]: e for e in exs}
    preds = load_preds(args.runs)
    specs = sorted({s for s, _ in preds})
    md = [f"# Results — `{args.data}`", "",
          "Point estimate [95% CI, bootstrap over source cases]. PresErr: lower is better. "
          "K+ = K claims supported by evidence.", ""]
    tex_rows = []
    for cond in "ABCDE":
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
    pairs = [("A", "B", "Cost of verification: B − A (same claims)",
              "Negative change recall / exact = worse when feedback must be verified; positive PresErr = more collateral change."),
             ("A", "E", "Asking a verified editor to propagate: E − A (same claims)",
              "Positive change recall on P = the literal reading of verified edits is a wording effect.")]
    for c1, c2, head, expl in pairs:
        have = [s_ for s_ in specs if (s_, c1) in preds and (s_, c2) in preds]
        if not have:
            continue
        md += [f"## {head}", "", expl, "", "| system | " + " | ".join(gap_keys) + " |", "|---|" + "---|" * len(gap_keys)]
        for s_ in have:
            cells = [fmt(*paired_gap(exs, preds[(s_, c1)], preds[(s_, c2)], k)) for k in gap_keys]
            md.append(f"| {s_} | " + " | ".join(cells) + " |")
        md.append("")
    md += ["## Change recall on P by dependency depth (condition B)", "", "| system | depth 1 | depth 2+ |", "|---|---|---|"]
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
    md += scale_table(exs, by_id, preds, args.tiers)
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
