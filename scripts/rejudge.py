#!/usr/bin/env python3
"""Re-score existing predictions with a different judge, so every model in a study is scored by the same judge.

  python3 scripts/rejudge.py --data paperB/data/medec_scope_v0.json --judge vllm2:Qwen/Qwen3-32B-AWQ \
      results/medscope_groq_openai_gpt-oss-120b results/medscope_groq_qwen_qwen3.8-27b

Only the judge is re-run; the revisions come from the prediction files, so no model is called again. For free-text
systems the claim statuses are replaced; for structured systems the judged-from-text statuses are. The previous
judgments are kept under "prev_judge" in each prediction, and claim-level agreement between the two judges is
printed per file (a robustness number for the paper). Files already scored by --judge are skipped.
"""
import argparse
import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data  # noqa: E402
from intexr.clients import Client  # noqa: E402
from intexr.systems import _judge_statuses  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--judge", required=True)
    ap.add_argument("runs", nargs="+", help="run directories (results/medscope_*)")
    args = ap.parse_args()
    by_id = {e["id"]: e for e in data.load(args.data)}
    judge = Client(args.judge)
    total = Counter()
    for d in args.runs:
        for f in sorted(glob.glob(os.path.join(d, "preds_*@*.jsonl"))):
            with open(f) as fh:
                preds = [json.loads(line) for line in fh]
            if preds and all(p.get("judge") == args.judge for p in preds):
                print(f"skip (already judged by {args.judge}): {f}")
                continue
            agree = Counter()
            for k, p in enumerate(preds):
                ex = by_id.get(p["id"])
                key = "judged_claims" if p.get("structured") else "claims"
                if ex is None or (p.get("structured") and key not in p) or p.get("judge") == args.judge:
                    continue
                print(f"  {os.path.basename(f)} {k + 1}/{len(preds)}", file=sys.stderr, flush=True)
                new = _judge_statuses(ex, p["revised_response"], judge)
                old = p.get(key, {})
                for cid in new:
                    agree["n"] += 1
                    agree["same"] += old.get(cid, {}).get("status") == new[cid]["status"]
                if key == "claims":  # free-text: keep any non-status fields the system wrote
                    new = {cid: dict(old.get(cid, {}), **v) for cid, v in new.items()}
                p["prev_judge"] = {"judge": p.get("judge", "gemini:gemini-3.5-flash-lite"), key: old}
                p[key], p["judge"] = new, args.judge
            with open(f, "w") as fh:
                for p in preds:
                    fh.write(json.dumps(p) + "\n")
            if agree["n"]:
                total.update(agree)
                print(f"{f}: claim-status agreement with the previous judge {agree['same'] / agree['n']:.2f} (n={agree['n']})")
    if total["n"]:
        print(f"\nOverall agreement with the previous judge: {total['same'] / total['n']:.2f} (n={total['n']})")


if __name__ == "__main__":
    main()
