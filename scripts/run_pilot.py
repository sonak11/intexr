#!/usr/bin/env python3
"""Run IntExR-Scope pilot systems and write predictions + a markdown report.

Examples
  # offline sanity check (no API key needed)
  python3 scripts/run_pilot.py --systems no_revision accept_feedback_lexical oracle

  # LLM systems: SYSTEM@PROVIDER:MODEL ; judge maps free-text revisions to claim actions
  export ANTHROPIC_API_KEY=...
  python3 scripts/run_pilot.py \
      --systems no_revision oracle \
                dialogue@anthropic:claude-sonnet-5-5 evidence_prompt@anthropic:claude-sonnet-5-5 \
                always_rewrite@anthropic:claude-sonnet-5-5 scope_first@anthropic:claude-sonnet-5-5 \
      --judge anthropic:claude-haiku-4-5-20251001 --conditions A B C D
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from intexr import data, metrics  # noqa: E402
from intexr.clients import Client, QuotaExhausted  # noqa: E402
from intexr.systems import OFFLINE, SYSTEMS  # noqa: E402

KEYS = ["change_recall_D", "change_recall_P", "under_revision", "preservation_error_Ksupported",
        "preservation_error_K", "unresolved_F1", "direct_F1", "propagation_F1", "verdict_acc",
        "check_pass", "no_forbidden_additions", "claim_action_acc", "interaction_exact"]


def fmt(point, ci, k):
    v = point.get(k)
    if v is None or v != v:
        return "–"
    lo, hi = ci.get(k, (v, v))
    return f"{v:.2f} [{lo:.2f},{hi:.2f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="pilot/data/pilot_v0.json")
    ap.add_argument("--systems", nargs="+", required=True)
    ap.add_argument("--judge", default=None, help="PROVIDER:MODEL for claim alignment of free-text outputs")
    ap.add_argument("--conditions", nargs="+", default=["B"], choices=list("ABCDE"))
    ap.add_argument("--out", default="results")
    ap.add_argument("--match", default=None, help="regex on example ids, e.g. 'valid|false|authority' to fit a daily free quota")
    ap.add_argument("--limit", type=int, default=None, help="use only the first N matching examples")
    ap.add_argument("--split", choices=["dev", "test"], default=None,
                    help="MedScope split by source case (paperB/data/splits.json); test is held out until the protocol freeze")
    args = ap.parse_args()

    exs = data.load(args.data)
    if args.match:
        import re
        exs = [e for e in exs if re.search(args.match, e["id"])]
    if args.split:
        exs = [e for e in exs if e.get("source", {}).get("split") == args.split]
    if args.limit:
        exs = exs[:args.limit]
    bad = {ex["id"]: data.validate(ex) for ex in exs}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        sys.exit(f"invalid examples: {json.dumps(bad, indent=1)}")
    judge = Client(args.judge) if args.judge else None
    os.makedirs(args.out, exist_ok=True)

    report = ["# IntExR-Scope pilot results", "", f"Data: `{args.data}` — {json.dumps(data.summarize(exs))}", "",
              "Values: point estimate [95% bootstrap CI over source cases]. Text checks are applied to the full revised "
              "response (deterministic pilot proxy).", ""]
    for cond in args.conditions:
        rows_all = []
        report += [f"## Condition {cond}", "", "| system | " + " | ".join(KEYS) + " |",
                   "|" + "---|" * (len(KEYS) + 1)]
        breakdown = []
        for spec in args.systems:
            name, _, model = spec.partition("@")
            if name in OFFLINE and cond != "B":
                continue
            fn = SYSTEMS[name]
            if name == "evidence_gate":
                from intexr.gate import make_scorer
                client = make_scorer(model) if model else None
            else:
                client = Client(model) if model else None
            if name not in OFFLINE and client is None:
                sys.exit(f"{name} needs @PROVIDER:MODEL")
            if name in ("dialogue", "evidence_prompt", "always_rewrite", "verify_revise") and judge is None:
                sys.exit(f"{name} needs --judge")
            preds, rows = [], []
            t0 = time.time()
            for k, ex in enumerate(exs):
                if name not in OFFLINE:  # progress, so slow free-tier runs don't look frozen
                    print(f"  [{spec} | condition {cond}] {k + 1}/{len(exs)} {ex['id']}  ({time.time() - t0:.0f}s elapsed)",
                          file=sys.stderr, flush=True)
                try:
                    p = fn(ex, client=client, judge=judge, condition=cond)
                except QuotaExhausted as e:
                    sys.exit(f"\nStopped at {spec}, condition {cond}, example {k + 1}/{len(exs)}.\n{e}")
                except RuntimeError as e:  # an API error (judge or model): stop instead of writing bad scores
                    sys.exit(f"\nAPI error at {spec}, condition {cond}, example {k + 1}/{len(exs)} "
                             f"(model {model}, judge {args.judge}):\n{e}")
                p["condition"], p["model"], p["judge"] = cond, model, args.judge
                preds.append(p)
                rows.append(metrics.per_example(ex, p))
            tag = f"{name}{'@' + model.replace(':', '_').replace('/', '_') if model else ''}_{cond}"
            with open(os.path.join(args.out, f"preds_{tag}.jsonl"), "w") as f:
                for p in preds:
                    f.write(json.dumps(p) + "\n")
            point, ci = metrics.bootstrap(rows, [data.case_key(e) for e in exs])
            report.append(f"| {spec} | " + " | ".join(fmt(point, ci, k) for k in KEYS) + " |")
            # breakdown by domain and by feedback validity
            for key in ("domain", "feedback_validity"):
                groups = {}
                for ex, r in zip(exs, rows):
                    gk = ex[key] if key == "domain" else ex["gold"][key]
                    groups.setdefault(gk, []).append(r)
                for gk, rs in sorted(groups.items()):
                    a = metrics.aggregate(rs)
                    breakdown.append(f"| {spec} | {key}={gk} (n={len(rs)}) | {a['change_recall_D']:.2f} | "
                                     f"{a['change_recall_P']:.2f} | {a['preservation_error_K']:.2f} | "
                                     f"{a['unresolved_F1']:.2f} | {a['claim_action_acc']:.2f} |")
            # label/action consistency for structured LLM output
            if any("judged_claims" in p for p in preds):
                rows_j = [metrics.per_example(ex, p, "judged_claims") for ex, p in zip(exs, preds)]
                aj = metrics.aggregate(rows_j)
                breakdown.append(f"| {spec} | judged-from-text | {aj['change_recall_D']:.2f} | "
                                 f"{aj['change_recall_P']:.2f} | {aj['preservation_error_K']:.2f} | "
                                 f"{aj['unresolved_F1']:.2f} | {aj['claim_action_acc']:.2f} |")
            rows_all.append((spec, rows))
        report += ["", "### Breakdown", "",
                   "| system | stratum | chg_rec_D | chg_rec_P | pres_err_K | U_F1 | claim_acc |",
                   "|---|---|---|---|---|---|---|"] + breakdown + [""]
    with open(os.path.join(args.out, "report.md"), "w") as f:
        f.write("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
