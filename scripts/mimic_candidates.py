#!/usr/bin/env python3
"""Mine MIMIC-CXR report pairs that are natural IntExR-Scope candidates (run ONLY after PhysioNet access).

Inputs (from PhysioNet, credentialed):
  --reports   mimic-cxr-reports/files/   (p1x/pXXXXXXXX/sXXXXXXXX.txt)
  --radgraph  (optional) RadGraph-XL / RadGraph inference JSON, used to propose finding->impression edges
Outputs: candidates.jsonl with the sections and a candidate type; human selection and labeling follow.

Candidate types (each yields a natural source of 'new evidence'):
  consecutive   same patient, next study within --max-hours: the later report is new evidence for the earlier one
                (interval change, lines/tubes placed or removed -> superseding / temporal-scope cases)
  addendum      report containing an ADDENDUM / correction -> direct updates with real provenance
  hedged        impressions with 'cannot be excluded', 'versus', 'possibly' -> real unresolved claims

Data handling: never commit MIMIC text to git or send it to an LLM endpoint not permitted by the PhysioNet DUA.
Keep outputs under data/mimic/ (git-ignored).
"""
import argparse
import glob
import json
import os
import re
from collections import defaultdict

SECTION_RE = re.compile(r"^\s*(FINDINGS|IMPRESSION|COMPARISON|INDICATION|HISTORY|TECHNIQUE|ADDENDUM)\s*:", re.M | re.I)
HEDGE_RE = re.compile(r"cannot be (excluded|ruled out)|versus|\bvs\.?\b|possibl[ey]|may represent|differential", re.I)
ADDENDUM_RE = re.compile(r"addendum|correction|corrected|amended", re.I)


def sections(text):
    out, marks = {}, list(SECTION_RE.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out[m.group(1).upper()] = " ".join(text[m.end():end].split())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", required=True)
    ap.add_argument("--out", default="data/mimic/candidates.jsonl")
    ap.add_argument("--limit-patients", type=int, default=2000)
    ap.add_argument("--radgraph", default=None)
    args = ap.parse_args()

    by_patient = defaultdict(list)
    for path in glob.glob(os.path.join(args.reports, "p1*", "p*", "s*.txt")):
        pid = os.path.basename(os.path.dirname(path))
        by_patient[pid].append(path)
        if len(by_patient) > args.limit_patients:
            break

    rg = {}
    if args.radgraph:
        with open(args.radgraph) as f:
            rg = json.load(f)  # {report_key: {"entities": {...}}}; suggestive_of edges -> candidate dependencies

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    n = 0
    with open(args.out, "w") as out:
        for pid, paths in by_patient.items():
            # NOTE: study order needs StudyDate/StudyTime from mimic-cxr-2.0.0-metadata.csv; ID order is NOT time order.
            reps = [(os.path.basename(p)[:-4], sections(open(p).read()), open(p).read()) for p in sorted(paths)]
            for sid, sec, raw in reps:
                if "IMPRESSION" not in sec or "FINDINGS" not in sec:
                    continue
                kinds = []
                if ADDENDUM_RE.search(raw):
                    kinds.append("addendum")
                if HEDGE_RE.search(sec["IMPRESSION"]):
                    kinds.append("hedged")
                deps = []
                for ent in rg.get(sid, {}).get("entities", {}).values():
                    for rel, tgt in ent.get("relations", []):
                        if rel == "suggestive_of":
                            deps.append([ent.get("tokens"), rg[sid]["entities"][tgt].get("tokens")])
                if kinds or deps:
                    out.write(json.dumps({"patient": pid, "study": sid, "types": kinds, "sections": sec,
                                          "suggestive_of": deps}) + "\n")
                    n += 1
            if len(reps) > 1:
                out.write(json.dumps({"patient": pid, "types": ["consecutive"], "studies": [r[0] for r in reps],
                                      "todo": "order by metadata StudyDate; pair (t, t+1) within max-hours"}) + "\n")
    print(f"wrote {n} single-study candidates to {args.out}")


if __name__ == "__main__":
    main()
