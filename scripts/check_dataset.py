#!/usr/bin/env python3
"""Check any IntExR-Scope dataset file: validity, balance, thin cells, and a readable review sheet.

  python3 scripts/check_dataset.py pilot/data/pilot_v0.json
  python3 scripts/check_dataset.py external/medec_intexr.json --show 2          # print 2 random examples
  python3 scripts/check_dataset.py pilot/data/pilot_v1.json --review review.md  # markdown to read/mark up
  python3 scripts/check_dataset.py pilot/data/*.json external/*.json            # several files at once

Exit code 1 if any example fails validation (usable in CI).
"""
import argparse
import json
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import LABELS, VALIDITY, data  # noqa: E402
from intexr.metrics import check_claim  # noqa: E402

MIN_CELL = 5  # flag label x validity cells with fewer claims than this


def render(ex):
    g = ex["gold"]
    lines = [f"### {ex['id']}  ({ex['domain']}; feedback={g['feedback_validity']} -> {g['feedback_verdict']})", "",
             f"**Context:** {ex['context']}", ""]
    for e in ex["prior_evidence"]:
        lines.append(f"- prior `{e['id']}`: {e['text']}")
    fb = ex.get("feedback")
    if fb:
        lines.append(f"- **feedback** ({fb['speaker_role']}): {fb['text']}")
    for e in ex["new_evidence"]:
        lines.append(f"- new `{e['id']}`: {e['text']}")
    parents = {}
    for a, b in g["dependencies"]:
        parents.setdefault(b, []).append(a)
    lines += ["", "| id | claim | gold | depends on | target |", "|---|---|---|---|---|"]
    for c in ex["claims"]:
        gc = g["claims"][c["id"]]
        tgt = gc.get("target_text", "")
        tgt = "(delete)" if tgt is None and gc["label"] in ("D", "P") else (tgt or "")
        lab = gc["label"] + (f"/{gc.get('trigger') or gc.get('support')}" if gc.get("trigger") or gc.get("support") else "")
        lines.append(f"| {c['id']} | {c['text']} | **{lab}** | {','.join(parents.get(c['id'], []))} | {tgt} |")
    if g.get("scope_note"):
        lines += ["", f"_Note:_ {g['scope_note']}"]
    lines += ["", "Reviewer: agree? ☐  issue: ____________", ""]
    return "\n".join(lines)


def check(path, args):
    exs = data.load(path)
    print(f"\n=== {path}: {len(exs)} examples")
    n_bad = 0
    for ex in exs:
        errs = data.validate(ex)
        # gold target must pass its own text checks (otherwise the check or the target is wrong)
        tr = ex["gold"].get("target_revision")
        if tr:
            for cid, gc in ex["gold"]["claims"].items():
                if check_claim(tr, gc.get("checks")) is False:
                    errs.append(f"{cid}: gold target_revision fails its own checks")
        if errs:
            n_bad += 1
            print(f"  INVALID {ex['id']}: {errs}")
    s = data.summarize(exs)
    print(f"  claims={s['n_claims']}  labels={s['labels']}  P-depth={s['P_depth']}")
    print(f"  domains={s['domains']}  feedback validity={s['feedback_validity']}")
    cell = Counter((g["label"], ex["gold"]["feedback_validity"]) for ex in exs for g in ex["gold"]["claims"].values())
    present = sorted({v for _, v in cell})
    print("  claims per label x feedback validity:")
    print("        " + "".join(f"{v[:10]:>12}" for v in present))
    for L in LABELS:
        print(f"    {L}   " + "".join(f"{cell.get((L, v), 0):>12}" for v in present))
    thin = [f"{L}x{v}" for L in LABELS for v in present if 0 < cell.get((L, v), 0) < MIN_CELL]
    missing_v = [v for v in VALIDITY if v not in present]
    if thin:
        print(f"  thin cells (<{MIN_CELL} claims): {', '.join(thin)}")
    if missing_v:
        print(f"  feedback types absent: {', '.join(missing_v)}")
    if not s["P_depth"]:
        print("  no propagated (P) claims: this file cannot test propagation")
    if args.show:
        for ex in random.Random(args.seed).sample(exs, min(args.show, len(exs))):
            print("\n" + render(ex))
    return exs, n_bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--show", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--review", help="write all examples as a markdown review sheet")
    args = ap.parse_args()
    all_exs, bad = [], 0
    for p in args.paths:
        exs, b = check(p, args)
        all_exs += exs
        bad += b
    if args.review:
        with open(args.review, "w") as f:
            f.write("# IntExR-Scope review sheet\n\n" + "\n".join(render(ex) for ex in all_exs))
        print(f"\nwrote review sheet -> {args.review}")
    print(f"\n{'OK' if not bad else f'{bad} INVALID'}: {len(all_exs)} examples checked")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
