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

Review one representative model per size tier (Difei, 27 Oct), not every model:
  python3 scripts/label_actions.py sample --data paperB/data/medec_scope_v0.json \
      --preds 'results/medscope_*/preds_evidence_prompt@*_B.jsonl' --reps-only --n 120 --out annotation/actions_sheet.csv
  (--reps-only keeps the models marked review=1 in configs/model_tiers.tsv; the sample is balanced across models,
  then across gold labels, so `score` reports judge agreement per model, i.e. per tier.)

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
    reps = None
    if args.reps_only:
        sys.path.insert(0, os.path.dirname(__file__))
        from summarize_results import load_tiers
        reps = {m for m, t in load_tiers(args.tiers).items() if t.get("review") == "1"}
    pool = defaultdict(list)
    for pat in args.preds:
        for f in glob.glob(pat):
            # preds_<system>@<model tag>_<condition>.jsonl
            stem, cond = os.path.basename(f)[len("preds_"):-len(".jsonl")].rsplit("_", 1)
            model = stem.split("@", 1)[1] if "@" in stem else ""
            with open(f) as fh:
                for line in fh:
                    p = json.loads(line)
                    ex = by_id.get(p["id"])
                    if not ex or p.get("structured"):
                        continue
                    if reps is not None and model not in reps:
                        continue
                    sysname = f"{p['system']}@{model}" if model else p["system"]
                    for c in ex["claims"]:
                        lab = ex["gold"]["claims"][c["id"]]["label"]
                        pool[(sysname, lab)].append({"key": f"{sysname}|{cond}|{p['id']}|{c['id']}", "example_id": p["id"],
                                          "claim_id": c["id"], "claim": c["text"], "revised_response": p["revised_response"],
                                          "human_action": "", "note": "", "judge_action": p["claims"][c["id"]]["status"],
                                          "gold_label": lab, "system": sysname})
    rng = random.Random(args.seed)
    cells = sorted(k for k in pool if pool[k])
    if not cells:
        sys.exit("no free-text predictions found (structured systems are labelled by construction)")
    rows, per = [], max(1, args.n // len(cells))
    for k in cells:
        rng.shuffle(pool[k])
        rows += pool[k][:per]
    rng.shuffle(rows)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in FIELDS})
    with open(args.out + ".hidden.json", "w") as f:
        json.dump({r["key"]: {k: r[k] for k in HIDDEN} for r in rows}, f, indent=1)
    print(f"wrote {len(rows)} pairs to {args.out} ({dict(Counter(r['gold_label'] for r in rows))}; {dict(Counter(r['system'] for r in rows))}); "
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


def rehide(args):
    """After re-judging (scripts/rejudge.py), refresh the hidden judge labels for the same sampled pairs."""
    hidden = json.load(open(args.sheet + ".hidden.json"))
    current = {}
    for pat in args.preds:
        for f in glob.glob(pat):
            stem, cond = os.path.basename(f)[len("preds_"):-len(".jsonl")].rsplit("_", 1)
            with open(f) as fh:
                for line in fh:
                    p = json.loads(line)
                    for cid, v in p.get("claims", {}).items():
                        current[f"{stem}|{cond}|{p['id']}|{cid}"] = v["status"]
    missing = [k for k in hidden if k not in current]
    if missing:
        sys.exit(f"{len(missing)} sampled pairs not found in --preds, e.g. {missing[:3]}")
    changed = sum(hidden[k]["judge_action"] != current[k] for k in hidden)
    for k in hidden:
        hidden[k]["judge_action"] = current[k]
    with open(args.sheet + ".hidden.json", "w") as f:
        json.dump(hidden, f, indent=1)
    print(f"refreshed {len(hidden)} hidden judge labels ({changed} changed); your human labels are untouched")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--data", required=True)
    s.add_argument("--preds", nargs="+", required=True)
    s.add_argument("--n", type=int, default=100)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--out", default="annotation/actions_sheet.csv")
    s.add_argument("--reps-only", action="store_true", help="only the review=1 model of each tier (see --tiers)")
    s.add_argument("--tiers", default=os.path.join(os.path.dirname(__file__), "..", "configs", "model_tiers.tsv"))
    for name in ("label", "score"):
        p = sub.add_parser(name)
        p.add_argument("sheet")
    r = sub.add_parser("rehide", help="refresh hidden judge labels after re-judging")
    r.add_argument("sheet")
    r.add_argument("--preds", nargs="+", required=True)
    a = ap.parse_args()
    {"sample": sample, "label": label, "score": score, "rehide": rehide}[a.cmd](a)


if __name__ == "__main__":
    main()
