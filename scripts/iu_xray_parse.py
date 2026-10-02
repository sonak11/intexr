#!/usr/bin/env python3
"""Parse the IU X-ray (Open-i, Indiana University) reports and tag IntExR-Scope candidates.

No credentialing needed:
  curl -L -o data/iu_xray/NLMCXR_reports.tgz https://openi.nlm.nih.gov/imgs/collections/NLMCXR_reports.tgz
  tar xzf data/iu_xray/NLMCXR_reports.tgz -C data/iu_xray
  python3 scripts/iu_xray_parse.py

License: CC BY-NC-ND 4.0 (Demner-Fushman et al., JAMIA 2016). Fine for research. Because of the
no-derivatives term, do NOT redistribute modified reports: release report IDs + the perturbation
script instead. 'XXXX' marks de-identified spans.

Candidate tags:
  abnormal      MeSH major terms are not 'normal'
  hedged        impression contains uncertainty language -> natural U claims
  comparison    a prior study is referenced -> temporal / superseding cases
  chain         impression mentions a finding term also in FINDINGS -> natural finding->impression dependency
  device        lines/tubes/hardware -> position-change cases
"""
import glob
import json
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), "..", "data", "iu_xray")
HEDGE = re.compile(r"cannot be (excluded|ruled out)|versus|\bvs\b|possibl[ey]|may represent|could represent|"
                   r"likely|suspicious|concerning|questionable|differential|not excluded|probable", re.I)
DEVICE = re.compile(r"catheter|picc|tube|pacemaker|pacer|lead|clips|sternotomy|wires|port\b|stent|prosthe", re.I)
FINDING_TERMS = ["opacity", "opacities", "consolidation", "effusion", "atelectasis", "nodule", "cardiomegaly",
                 "edema", "pneumothorax", "granuloma", "scarring", "emphysema", "hyperinflat", "infiltrate",
                 "mass", "fracture", "hernia", "calcified", "enlarged", "tortuous"]


def parse(path):
    root = ET.parse(path).getroot()
    sec = {a.get("Label"): (a.text or "").strip() for a in root.iter("AbstractText")}
    mesh = [m.text for m in root.iter("major") if m.text]
    rid = root.find("uId").get("id")
    return {"id": rid, "indication": sec.get("INDICATION", ""), "comparison": sec.get("COMPARISON", ""),
            "findings": sec.get("FINDINGS", ""), "impression": sec.get("IMPRESSION", ""), "mesh": mesh,
            "images": [p.get("id") for p in root.iter("parentImage")]}


def tags(r):
    t = []
    if r["mesh"] and not all(m.lower().startswith("normal") for m in r["mesh"]):
        t.append("abnormal")
    if HEDGE.search(r["impression"]):
        t.append("hedged")
    if r["comparison"] and not re.match(r"^\s*(none|no prior|xxxx\.?)\s*\.?\s*$", r["comparison"], re.I):
        t.append("comparison")
    shared = [w for w in FINDING_TERMS if w in r["findings"].lower() and w in r["impression"].lower()]
    if shared:
        t.append("chain")
    if DEVICE.search(r["findings"] + " " + r["impression"]):
        t.append("device")
    return t, shared


def main():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "ecgen-radiology", "*.xml")), key=lambda s: int(re.sub(r"\D", "", os.path.basename(s)))):
        r = parse(p)
        if not r["findings"] or not r["impression"]:
            continue
        r["tags"], r["shared_terms"] = tags(r)
        r["n_sentences"] = len(re.findall(r"[.!?](\s|$)", r["findings"] + " " + r["impression"]))
        out.append(r)
    with open(os.path.join(ROOT, "iu_reports.jsonl"), "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    c = Counter(t for r in out for t in r["tags"])
    rich = [r for r in out if {"abnormal", "chain"} <= set(r["tags"]) and r["n_sentences"] >= 6]
    print(f"{len(out)} reports with findings+impression; tags: {dict(c)}")
    print(f"pilot-ready (abnormal + chain + >=6 sentences): {len(rich)}")
    with open(os.path.join(ROOT, "iu_candidates.jsonl"), "w") as f:
        for r in rich:
            f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
