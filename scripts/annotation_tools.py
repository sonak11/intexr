#!/usr/bin/env python3
"""Blind annotation sheet export + inter-annotator agreement.

  python3 scripts/annotation_tools.py sheet --data pilot/data/pilot_v0.json --out annotation/sheet_blank.csv
  # annotators fill columns: label (D/P/K/U), depends_on (e.g. c1;c2), feedback_verdict (first row per example)
  python3 scripts/annotation_tools.py agree annotation/annotatorA.csv annotation/annotatorB.csv
  python3 scripts/annotation_tools.py agree annotation/annotatorA.csv --gold pilot/data/pilot_v0.json
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data  # noqa: E402

COLS = ["example_id", "domain", "claim_id", "claim_text", "label", "depends_on", "feedback_verdict", "notes"]


def sheet(args):
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for ex in data.load(args.data):
            for i, c in enumerate(ex["claims"]):
                w.writerow([ex["id"], ex["domain"], c["id"], c["text"], "", "", "" if i == 0 else "-", ""])
    # companion file with the inputs annotators need (no gold)
    with open(os.path.splitext(args.out)[0] + "_inputs.json", "w") as f:
        json.dump([data.model_view(ex) for ex in data.load(args.data)], f, indent=2)
    print("wrote", args.out)


def _read(path, key=None):
    """key: {neutral item id: example id} from make_annotation_html.py, so blind sheets map back to real ids."""
    with open(path, newline="") as f:
        return {((key or {}).get(r["example_id"], r["example_id"]), r["claim_id"]): r for r in csv.DictReader(f)}


def _gold_as_sheet(path):
    rows = {}
    for ex in data.load(path):
        parents = {}
        for a, b in ex["gold"]["dependencies"]:
            parents.setdefault(b, []).append(a)
        for i, c in enumerate(ex["claims"]):
            rows[(ex["id"], c["id"])] = {"label": ex["gold"]["claims"][c["id"]]["label"],
                                         "depends_on": ";".join(parents.get(c["id"], [])),
                                         "feedback_verdict": ex["gold"]["feedback_verdict"] if i == 0 else "-"}
    return rows


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0, po


def agree(args):
    key = json.load(open(args.key)) if args.key else None
    A = _read(args.a, key)
    B = _gold_as_sheet(args.gold) if args.gold else _read(args.b, key)
    keys = sorted(k for k in A if k in B and A[k]["label"].strip())
    la = [A[k]["label"].strip().upper() for k in keys]
    lb = [B[k]["label"].strip().upper() for k in keys]
    k, po = kappa(la, lb)
    print(f"claims={len(keys)}  label agreement={po:.2f}  Cohen's kappa={k:.2f}")
    conf = Counter(zip(la, lb))
    print("confusion (A,B):", dict(sorted(conf.items())))
    dep = [set(filter(None, A[x]["depends_on"].split(";"))) == set(filter(None, B[x]["depends_on"].split(";")))
           for x in keys]
    print(f"exact dependency-set agreement={sum(dep) / len(dep):.2f}")
    vk = [x for x in keys if A[x]["feedback_verdict"] not in ("", "-")]
    if vk:
        va = [A[x]["feedback_verdict"] for x in vk]
        vb = [B[x]["feedback_verdict"] for x in vk]
        print(f"feedback verdict kappa={kappa(va, vb)[0]:.2f} (n={len(vk)})")
    print("disagreements:")
    for x, p, q in zip(keys, la, lb):
        if p != q:
            print(f"  {x[0]} {x[1]}: {p} vs {q}")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("sheet")
    s.add_argument("--data", default="pilot/data/pilot_v0.json")
    s.add_argument("--out", default="annotation/sheet_blank.csv")
    g = sp.add_parser("agree")
    g.add_argument("a")
    g.add_argument("b", nargs="?")
    g.add_argument("--gold")
    g.add_argument("--key", help="item-id key from make_annotation_html.py")
    args = ap.parse_args()
    sheet(args) if args.cmd == "sheet" else agree(args)


if __name__ == "__main__":
    main()
