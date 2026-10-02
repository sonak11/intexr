#!/usr/bin/env python3
"""Download public datasets that cover parts of IntExR-Scope into data/external/ (git-ignored).

  python3 scripts/fetch_external.py            # all
  python3 scripts/fetch_external.py medec      # one

| name          | license      | what it gives IntExR                                                    |
|---------------|--------------|--------------------------------------------------------------------------|
| medec         | CC BY 4.0    | real clinical notes, expert-injected error + correction; ~half error-free |
| vitaminc      | CC BY-SA 3.0 | real Wikipedia revisions: claim + evidence -> SUPPORTS / REFUTES / NEI     |
| editpropbench | CC BY 4.0    | synthetic manuscripts with direct / required-update / protected labels    |

Not fetched automatically (larger / special tooling), see docs/05_datasets_and_paper.md:
  FRUIT (gs://gresearch/FRUIT, Apache-2.0), ARIES (s3://ai2-s2-research-public/aries, ODC-BY),
  ReXGradient-160K (HF license click-through), CheXpert Plus (Stanford AIMI agreement).
"""
import os
import sys
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..", "data", "external")
MEDEC = "https://raw.githubusercontent.com/abachaa/MEDEC/main/MEDEC-MS/"
EPB = "https://huggingface.co/datasets/EditCoherenceBench/EditCoherenceBench/resolve/main/"
SOURCES = {
    "medec": [(MEDEC + "MEDEC-MS-TestSet-with-GroundTruth-and-ErrorType.csv", "test.csv"),
              (MEDEC + "MEDEC-MS-ValidationSet-with-GroundTruth-and-ErrorType.csv", "validation.csv")],
    "vitaminc": [("https://huggingface.co/datasets/tals/vitaminc/resolve/main/dev.jsonl", "dev.jsonl")],
    "editpropbench": [(EPB + "corpora/cascade-v1-creative/benchmark_items_cascade_only.jsonl", "items.jsonl"),
                      (EPB + "LICENSE", "LICENSE")],
}


def fetch(name):
    d = os.path.join(ROOT, name)
    os.makedirs(d, exist_ok=True)
    for url, fn in SOURCES[name]:
        path = os.path.join(d, fn)
        if os.path.exists(path):
            print(f"  have {path}")
            continue
        print(f"  get  {url}")
        urllib.request.urlretrieve(url, path)
        print(f"       {os.path.getsize(path) / 1e6:.1f} MB")


if __name__ == "__main__":
    for n in sys.argv[1:] or SOURCES:
        print(n)
        fetch(n)
