#!/usr/bin/env python3
"""Token use per model, read from the response cache (results/.cache). Use it to plan runs against free-tier caps.

  python3 scripts/usage.py                 # all cached calls
  python3 scripts/usage.py --since 2h      # only calls cached in the last 2 hours (e.g. today's run)
"""
import argparse
import glob
import json
import os
import time
from collections import defaultdict

CACHE = os.path.join(os.path.dirname(__file__), "..", "results", ".cache")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None, help="e.g. 30m, 2h, 1d")
    a = ap.parse_args()
    cutoff = 0
    if a.since:
        n, unit = float(a.since[:-1]), a.since[-1]
        cutoff = time.time() - n * {"m": 60, "h": 3600, "d": 86400}[unit]
    s = defaultdict(lambda: defaultdict(float))
    for f in glob.glob(os.path.join(CACHE, "*.json")):
        if os.path.getmtime(f) < cutoff:
            continue
        try:
            d = json.load(open(f))
        except Exception:  # noqa: BLE001
            continue
        if "provider" not in d:
            continue  # NLI score cache entries
        u = d.get("usage") or {}
        k = f"{d['provider']}:{d['model']}"
        s[k]["calls"] += 1
        s[k]["prompt"] += u.get("prompt_tokens", u.get("input_tokens", 0)) or 0
        s[k]["completion"] += u.get("completion_tokens", u.get("output_tokens", 0)) or 0
        s[k]["latency"] += d.get("latency_s", 0) or 0
    if not s:
        print("no cached calls" + (f" in the last {a.since}" if a.since else ""))
        return
    print(f"{'model':45} {'calls':>6} {'prompt tok':>11} {'output tok':>11} {'tok/call':>9} {'s/call':>7}")
    for k, v in sorted(s.items()):
        tot = v["prompt"] + v["completion"]
        print(f"{k:45} {int(v['calls']):>6} {int(v['prompt']):>11} {int(v['completion']):>11} "
              f"{tot / v['calls']:>9.0f} {v['latency'] / v['calls']:>7.1f}")


if __name__ == "__main__":
    main()
