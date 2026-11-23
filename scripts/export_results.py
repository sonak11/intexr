#!/usr/bin/env python3
"""Export every MedScope run as flat JSON tables (for the results dashboard and the Word tables).

  python3 scripts/export_results.py --out <dir>

Writes runs.json (one row per model x system x condition, every metric + 95% case-bootstrap CI),
gaps.json (paired B - A per model x system), strata.json (condition B by feedback validity),
checks.json and dataset.json (fixed reliability numbers and benchmark size).
"""
import argparse
import glob
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data, metrics  # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from summarize_results import load_preds, load_tiers, paired_gap  # noqa: E402

SYSTEMS = {"dialogue": "Dialogue", "always_rewrite": "Always rewrite", "evidence_prompt": "Evidence-aware prompt",
           "evidence_gate": "Evidence gate (NLI)", "verify_revise": "Verify-then-revise",
           "scope_first": "Scope-first (1 prompt)", "scope_pipeline": "Scope-first pipeline v1",
           "scope_pipeline_v0": "Scope-first pipeline v0"}
ORDER = list(SYSTEMS)
NAMES = {"vllm_Qwen_Qwen3-4B": "Qwen3-4B", "vllm_Qwen_Qwen3-8B": "Qwen3-8B", "vllm_Qwen_Qwen3-14B": "Qwen3-14B",
         "groq_openai_gpt-oss-20b": "gpt-oss-20b", "groq_qwen_qwen3.8-27b": "Qwen3.8-27B",
         "gemini_gemma-4-31b-it": "Gemma-4-31B", "vllm_Qwen_Qwen3-32B-AWQ": "Qwen3-32B (AWQ)",
         "vllm_casperhansen_llama-3.3-70b-instruct-awq": "Llama-3.3-70B (AWQ)", "groq_openai_gpt-oss-120b": "gpt-oss-120b"}
METRICS = ["change_recall_D", "change_recall_P", "preservation_error_Ksupported", "preservation_error_K",
           "under_revision", "unresolved_F1", "verdict_acc", "claim_action_acc", "interaction_exact"]
GAP_METRICS = ["preservation_error_Ksupported", "interaction_exact", "change_recall_P", "unresolved_F1"]
CHECKS = [
    {"check": "Second annotator vs gold: claim labels (Cohen kappa)", "value": 0.87, "n": "113 claims, 24 examples",
     "note": "raw agreement 0.91; target 0.70; 9 of 10 disagreements are gold P labelled D"},
    {"check": "Second annotator vs gold: feedback verdict (Cohen kappa)", "value": 0.94, "n": "24 examples",
     "note": "23 of 24 agree"},
    {"check": "Second annotator vs gold: exact dependency sets", "value": 0.6, "n": "113 claims",
     "note": "annotator also linked kept claims to findings"},
    {"check": "Local judge (Qwen3-32B) vs Gemini judge: claim-action agreement", "value": 0.96, "n": "2,646 claims",
     "note": "keep-vs-change disagreements under 0.3%"},
]
DATASET = [
    {"item": "Source cases (MEDEC notes)", "value": 154, "note": "20 dev / 134 test, split by case"},
    {"item": "Examples (case x feedback variant)", "value": 941,
     "note": "dev slice used for these runs: 60 (valid, false, authority-only)"},
    {"item": "Labelled claims", "value": 4525, "note": "D 873, P 1,292, K 2,167, U 193"},
    {"item": "Claims per run (dev slice)", "value": 294,
     "note": "K 156, D 44, P 57, U 37; 20 evidence-supported K claims attacked by false feedback"},
]


def r2(v):
    return None if v is None or v != v else round(v, 2)


def ci_str(ci):
    return "" if not ci or ci[0] != ci[0] else f"[{ci[0]:.2f}, {ci[1]:.2f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="paperB/data/medec_scope_v0.json")
    ap.add_argument("--runs", nargs="+", default=sorted(glob.glob("results/medscope_*")))
    ap.add_argument("--tiers", default="configs/model_tiers.tsv")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    exs = data.load(args.data)
    by_id = {e["id"]: e for e in exs}
    preds = load_preds([d for d in args.runs if os.path.isdir(d)])
    tiers = load_tiers(args.tiers)
    runs, gaps, strata = [], [], []
    for (spec, cond), pr in sorted(preds.items()):
        if "@" not in spec:
            continue
        sysname, model = spec.split("@", 1)
        if sysname not in SYSTEMS or model not in NAMES:
            print("skip", spec, cond, file=sys.stderr)
            continue
        ex_s = [by_id[i] for i in pr if i in by_id]
        rows = [metrics.per_example(e, pr[e["id"]]) for e in ex_s]
        point, ci = metrics.bootstrap(rows, [data.case_key(e) for e in ex_s])
        params = float(tiers.get(model, {}).get("params_b", "nan"))
        row = {"key": f"{model}|{sysname}|{cond}", "model": NAMES[model], "family": tiers.get(model, {}).get("family", ""),
               "params_b": params, "system": SYSTEMS[sysname], "system_order": ORDER.index(sysname), "condition": cond,
               "n": len(rows), "parse_failures": sum("parse_error" in pr[e["id"]] for e in ex_s)}
        for m in METRICS:
            row[m] = r2(point.get(m))
            row[m + "_ci"] = ci_str(ci.get(m)) if row[m] is not None else ""
        runs.append(row)
        if cond == "B":
            if (spec, "A") in preds:
                for m in GAP_METRICS:
                    g, gci = paired_gap(exs, preds[(spec, "A")], pr, m)
                    if g is None or g != g:
                        continue
                    gaps.append({"key": f"{model}|{sysname}|{m}", "model": NAMES[model], "system": SYSTEMS[sysname],
                                 "metric": m, "b_minus_a": r2(g), "ci": ci_str(gci),
                                 "excludes_zero": "yes" if gci and (gci[0] > 0 or gci[1] < 0) else "no"})
            by_v = defaultdict(list)
            for e in ex_s:
                by_v[e["gold"]["feedback_validity"]].append(metrics.per_example(e, pr[e["id"]]))
            for v, rs in sorted(by_v.items()):
                a = metrics.aggregate(rs)
                strata.append({"key": f"{model}|{sysname}|{v}", "model": NAMES[model], "system": SYSTEMS[sysname],
                               "validity": v, "n": len(rs), **{m: r2(a.get(m)) for m in
                               ["change_recall_D", "change_recall_P", "preservation_error_K",
                                "preservation_error_Ksupported", "unresolved_F1", "verdict_acc", "interaction_exact"]}})
    os.makedirs(args.out, exist_ok=True)
    for name, obj in [("runs", runs), ("gaps", gaps), ("strata", strata), ("checks", CHECKS), ("dataset", DATASET)]:
        with open(os.path.join(args.out, name + ".json"), "w") as f:
            json.dump(obj, f, indent=1)
        print(f"{name}: {len(obj)} rows")


if __name__ == "__main__":
    main()
