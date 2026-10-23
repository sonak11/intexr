#!/usr/bin/env python3
"""How many source cases does the test set need? Uses the paired A/B design on dev results.

  python3 scripts/sample_size.py --data paperB/data/medec_scope_v0.json \
      --a results/medscope_X/preds_scope_pipeline@X_A.jsonl --b results/medscope_X/preds_scope_pipeline@X_B.jsonl \
      --metric change_recall_P --delta 0.10

For each source case it computes the B-minus-A difference of the metric (pooling the case's examples), takes the
standard deviation of those per-case differences, and applies the paired normal approximation
    n_cases = ((z_{1-alpha/2} + z_{power}) * sd / delta)^2
to report the number of source cases needed to detect a gap of size delta (two-sided alpha 0.05, power 0.8 by
default). It also reports the gap that the current number of cases can detect.
"""
import argparse
import json
import math
import os
import statistics
import sys
from collections import defaultdict
from statistics import NormalDist

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data, metrics  # noqa: E402


def load(path):
    with open(path) as f:
        return {p["id"]: p for p in (json.loads(line) for line in f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--a", required=True, help="predictions under condition A")
    ap.add_argument("--b", required=True, help="predictions under condition B")
    ap.add_argument("--metric", default="change_recall_P")
    ap.add_argument("--delta", type=float, default=0.10)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    a = ap.parse_args()
    exs = {e["id"]: e for e in data.load(a.data)}
    pa, pb = load(a.a), load(a.b)
    cases = defaultdict(lambda: ([], []))
    for i in set(pa) & set(pb) & set(exs):
        ex = exs[i]
        cases[data.case_key(ex)][0].append(metrics.per_example(ex, pa[i]))
        cases[data.case_key(ex)][1].append(metrics.per_example(ex, pb[i]))
    diffs = []
    for ra, rb in cases.values():
        x, y = metrics.aggregate(ra)[a.metric], metrics.aggregate(rb)[a.metric]
        if x == x and y == y:  # skip cases where the metric is undefined (e.g. no P claims)
            diffs.append(y - x)
    if len(diffs) < 3:
        sys.exit(f"only {len(diffs)} cases with a defined {a.metric}; need at least 3")
    mean, sd = statistics.mean(diffs), statistics.stdev(diffs)
    z = NormalDist().inv_cdf(1 - a.alpha / 2) + NormalDist().inv_cdf(a.power)
    need = math.ceil((z * sd / a.delta) ** 2) if sd > 0 else 1
    detectable = z * sd / math.sqrt(len(diffs))
    print(f"metric={a.metric}  cases={len(diffs)}  mean B-A={mean:+.3f}  sd of per-case differences={sd:.3f}")
    print(f"cases needed to detect |B-A| >= {a.delta:.2f} (alpha={a.alpha}, power={a.power}): {need}")
    print(f"smallest gap detectable with the current {len(diffs)} cases: {detectable:.3f}")


if __name__ == "__main__":
    main()
