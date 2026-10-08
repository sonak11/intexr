#!/usr/bin/env python3
"""List the model ids a provider offers (use them in SYSTEM@provider:model specs).

  export GROQ_API_KEY=...;  python3 scripts/list_models.py groq
  python3 scripts/list_models.py openrouter --free     # only ':free' models
  python3 scripts/list_models.py ollama
"""
import argparse
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr.clients import Client  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("provider")
ap.add_argument("--free", action="store_true", help="openrouter: only models ending in ':free'")
a = ap.parse_args()
base, key = Client(f"{a.provider}:x").endpoint()
req = urllib.request.Request(base.rstrip("/") + "/models", headers={"Authorization": f"Bearer {key}",
                                                                    "User-Agent": "intexr-research/0.1"})
with urllib.request.urlopen(req, timeout=60) as r:
    data = json.loads(r.read())
ids = sorted(m.get("id", "") for m in data.get("data", data.get("models", [])))
for i in ids:
    if not a.free or i.endswith(":free"):
        print(i)
