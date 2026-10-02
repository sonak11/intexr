#!/usr/bin/env python3
"""Merge IU, COCO, and synthetic pilot items into pilot/data/pilot_v1.json (git-ignored)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data
iu = data.load("pilot/data/pilot_v1_iu.json")
v0 = data.load("pilot/data/pilot_v0.json")
coco = [e for e in v0 if e["domain"] == "coco"]
syn = [dict(e, id=e["id"].replace("cxr", "syn"), domain="cxr_synthetic") for e in v0 if e["domain"] == "cxr"]
json.dump({"version": "pilot_v1", "notes": "iu-* real IU X-ray (do not redistribute); coco-* real COCO captions; "
           "syn-* synthetic MIMIC-style probes.", "examples": iu + coco + syn},
          open("pilot/data/pilot_v1.json", "w"), indent=2)
print(json.dumps(data.summarize(iu + coco + syn)))
