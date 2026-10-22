#!/usr/bin/env python3
"""Judge calibration (HANDOFF Task 6): hand-label what a revision did to each claim, then measure agreement
with the LLM claim-alignment judge.

  # 1. sample ~100 (claim, revision) pairs from free-text system outputs; judge labels are hidden
  python3 scripts/label_actions.py sample --data paperB/data/medec_scope_v0.json \
      --preds results/medscope_*/preds_evidence_prompt@*_B.jsonl results/medscope_*/preds_dialogue@*_B.jsonl \
      --n 100 --out annotation/actions_sheet.csv
  # 2. label in the terminal (resumable; or fill the human_action column in a spreadsheet)
  python3 scripts/label_actions.py label annotation/actions_sheet.csv
  # 3. agreement with the judge (target Cohen's kappa >= 0.75)
  python3 scripts/label_actions.py score annotation/actions_sheet.csv

Actions: keep (meaning unchanged) | revised (content changed) | removed (gone) | hedged (kept but marked uncertain).
The sample is stratified by gold label so that rare actions (hedged, removed) are not swamped by keeps.
"""
import argparse
import csv
import glob
import json
import os
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import STATUSES, data  # noqa: E402
from annotation_tools import kappa  # noqa: E402

FIELDS = ["key", "example_id", "claim_id", "claim", "revised_response", "human_action", "note"]
HIDDEN = ["judge_action", "gold_label", "system"]


def sample(args):
    by_id = {e["id"]: e for e in data.load(args.data)}
    pool = defaultdict(list)
    for pat in args.preds:
        for f in glob.glob(pat):
            with open(f) as fh:
                for line in fh:
                    p = json.loads(line)
                    ex = by_id.get(p["id"])
                    if not ex or p.get("structured"):
                        continue
                    for c in ex["claims"]:
                        lab = ex["gold"]["claims"][c["id"]]["label"]
                        pool[lab].append({"key": f"{p['system']}|{p['id']}|{c['id']}", "example_id": p["id"],
                                          "claim_id": c["id"], "claim": c["text"], "revised_response": p["revised_response"],
                                          "human_action": "", "note": "", "judge_action": p["claims"][c["id"]]["status"],
                                          "gold_label": lab, "system": p["system"]})
    rng = random.Random(args.seed)
    labs = [lab for lab in "DPUK" if pool[lab]]
    if not labs:
        sys.exit("no free-text predictions found (structured systems are labelled by construction)")
    rows, per = [], max(1, args.n // len(labs))
    for lab in labs:
        rng.shuffle(pool[lab])
        rows += pool[lab][:per]
    rng.shuffle(rows)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in FIELDS})
    with open(args.out + ".hidden.json", "w") as f:
        json.dump({r["key"]: {k: r[k] for k in HIDDEN} for r in rows}, f, indent=1)
    print(f"wrote {len(rows)} pairs to {args.out} ({dict(Counter(r['gold_label'] for r in rows))}); "
          f"judge labels kept in {args.out}.hidden.json — don't open it before labelling")


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)


def label(args):
    rows = _read(args.sheet)
    keys = {"k": "keep", "r": "revised", "x": "removed", "h": "hedged"}
    todo = [r for r in rows if not r["human_action"]]
    print(f"{len(todo)} of {len(rows)} left. Keys: k=keep r=revised x=removed h=hedged s=skip q=save+quit\n")
    for i, r in enumerate(todo):
        print("=" * 80, f"\n[{i + 1}/{len(todo)}] {r['example_id']} {r['claim_id']}\nCLAIM:    {r['claim']}\n"
              f"REVISION: {r['revised_response']}\n")
        while True:
            a = input("action> ").strip().lower()
            if a in keys:
                r["human_action"] = keys[a]
                break
            if a in ("s", "q"):
                break
        if a == "q":
            break
        if a not in ("s",):
            r["note"] = input("note (enter to skip)> ").strip()
        _write(args.sheet, rows)
    _write(args.sheet, rows)


def score(args):
    rows = [r for r in _read(args.sheet) if r["human_action"] in STATUSES]
    hidden = json.load(open(args.sheet + ".hidden.json"))
    h = [r["human_action"] for r in rows]
    j = [hidden[r["key"]]["judge_action"] for r in rows]
    if not rows:
        sys.exit("no labelled rows yet")
    k, po = kappa(h, j)
    print(f"pairs={len(rows)}  agreement={po:.2f}  Cohen's kappa={k:.2f}  (target >= 0.75)\n")
    print("confusion (rows = human, cols = judge)")
    print(" " * 9 + "".join(f"{s:>9}" for s in STATUSES))
    cm = Counter(zip(h, j))
    for a in STATUSES:
        print(f"{a:>9}" + "".join(f"{cm[(a, b)]:>9}" for b in STATUSES))
    by_sys = defaultdict(list)
    for r, a, b in zip(rows, h, j):
        by_sys[hidden[r["key"]]["system"]].append(a == b)
    print("\nagreement by system: " + ", ".join(f"{s}={sum(v) / len(v):.2f} (n={len(v)})" for s, v in by_sys.items()))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--data", required=True)
    s.add_argument("--preds", nargs="+", required=True)
    s.add_argument("--n", type=int, default=100)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--out", default="annotation/actions_sheet.csv")
    for name in ("label", "score"):
        p = sub.add_parser(name)
        p.add_argument("sheet")
    a = ap.parse_args()
    {"sample": sample, "label": label, "score": score}[a.cmd](a)


if __name__ == "__main__":
    main()
