#!/usr/bin/env python3
"""Sanity-check model outputs after a run: parse failures, pipeline errors, empty revisions.

  python3 scripts/check_preds.py results/smoke_*        # OK / PROBLEM per predictions file
"""
import glob
import json
import os
import sys

bad = 0
for d in sys.argv[1:]:
    for f in sorted(glob.glob(os.path.join(d, "preds_*.jsonl"))):
        ps = [json.loads(line) for line in open(f)]
        parse = sum("parse_error" in p for p in ps)
        errs = sum(bool(p.get("errors")) for p in ps)
        empty = sum(not (p.get("revised_response") or "").strip() for p in ps)
        judge = sum(any("judge_error" in c for c in p.get("claims", {}).values()) for p in ps)
        problem = parse or errs or empty or judge
        bad += bool(problem)
        print(f"{'PROBLEM' if problem else 'OK':8} {os.path.basename(f)}: n={len(ps)} parse_errors={parse} "
              f"pipeline_errors={errs} empty_revisions={empty} judge_errors={judge}")
        if problem:
            p = next(p for p in ps if "parse_error" in p or p.get("errors") or not (p.get("revised_response") or "").strip()
                     or any("judge_error" in c for c in p.get("claims", {}).values()))
            print("         first bad example:", p["id"], (p.get("parse_error") or p.get("errors") or "")[:300])
sys.exit(1 if bad else 0)
