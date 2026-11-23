#!/usr/bin/env python3
"""Calls, tokens and seconds per example for every finished run, read from the response cache.

  python3 scripts/cost_per_example.py            # on the machine that holds results/.cache (thasos)

Every system is re-run over the examples of each preds file with a client that ONLY reads the cache: the
cache key is recomputed exactly as in intexr/clients.py, so no API or GPU call is made. A cache miss is counted,
not filled. System calls (the model under test) and judge calls (provider vllm2, the fixed scoring judge) are
reported separately; judge calls are evaluation cost, not part of the method. Seconds are wall time of the
request as cached (includes server retries, excludes our own rate-limit pacing). Writes results/COST.md.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import clients, data  # noqa: E402
from intexr.systems import SYSTEMS  # noqa: E402

LOG = []  # (role, usage dict, latency) for the current example


class Miss(Exception):
    pass


def cached_call(self, system, messages):
    extra = self.extra_body()
    key = hashlib.sha256(json.dumps([self.provider, self.model, self.temperature, system, messages]
                                    + ([extra] if extra else [])).encode()).hexdigest()
    path = os.path.join(clients.CACHE_DIR, key + ".json")
    role = "judge" if self.provider == "vllm2" else "system"
    if not os.path.exists(path):
        raise Miss(role)
    with open(path) as f:
        d = json.load(f)
    LOG.append((role, d.get("usage") or {}, d.get("latency_s") or 0.0))
    return d["text"]


clients.Client.__call__ = cached_call


def load_tiers(path):
    with open(path) as f:
        rows = [ln.rstrip("\n").split("\t") for ln in f if ln.strip() and not ln.startswith("#")]
    head = rows[0]
    return {r[0].replace(":", "_").replace("/", "_"): dict(zip(head, r)) for r in rows[1:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="paperB/data/medec_scope_v0.json")
    ap.add_argument("--runs", nargs="+", default=sorted(glob.glob("results/medscope_*")))
    ap.add_argument("--tiers", default="configs/model_tiers.tsv")
    ap.add_argument("--judge", default="vllm2:Qwen/Qwen3-32B-AWQ")
    ap.add_argument("--out", default="results/COST.md")
    args = ap.parse_args()
    os.environ["INTEXR_EXTRA_BODY_VLLM2"] = '{"chat_template_kwargs": {"enable_thinking": false}}'
    by_id = {e["id"]: e for e in data.load(args.data)}
    tiers = load_tiers(args.tiers)
    judge = clients.Client(args.judge)
    rows = []
    for d in args.runs:
        for f in sorted(glob.glob(os.path.join(d, "preds_*@*.jsonl"))):
            m = re.match(r"preds_(.+)@(.+)_([ABCDE])\.jsonl$", os.path.basename(f))
            if not m:
                continue
            name, model_tag, cond = m.groups()
            row = tiers.get(model_tag)
            if not row or name not in SYSTEMS:
                continue
            spec, prov = row["spec"], row["spec"].split(":", 1)[0]
            for k in [k for k in os.environ if k.startswith("INTEXR_EXTRA_BODY_") and k != "INTEXR_EXTRA_BODY_VLLM2"]:
                del os.environ[k]
            if row.get("extra") and row["extra"] != "{}":
                os.environ["INTEXR_EXTRA_BODY_" + prov.upper()] = row["extra"]
            if name == "evidence_gate":
                from intexr.gate import make_scorer
                client = make_scorer(spec)
            else:
                client = clients.Client(spec)
            ids = [json.loads(ln)["id"] for ln in open(f)]
            tot = defaultdict(float)
            for i in ids:
                LOG.clear()
                try:
                    SYSTEMS[name](by_id[i], client=client, judge=judge, condition=cond)
                except Miss as e:
                    tot["miss_" + str(e)] += 1
                    continue
                except Exception:  # noqa: BLE001  (a parse error inside a system is fine: the calls are logged)
                    pass
                tot["n"] += 1
                for role, u, lat in LOG:
                    tot[role + "_calls"] += 1
                    tot[role + "_in"] += u.get("prompt_tokens", u.get("input_tokens", 0)) or 0
                    tot[role + "_out"] += u.get("completion_tokens", u.get("output_tokens", 0)) or 0
                    tot[role + "_s"] += lat
            n = max(tot["n"], 1)
            rows.append((float(row["params_b"]) if row["params_b"] not in ("", "-") else 1e9, row["spec"], name, cond,
                         int(tot["n"]), {k: v / n for k, v in tot.items() if k != "n" and not k.startswith("miss")},
                         int(tot["miss_system"]), int(tot["miss_judge"])))
            print(f"{spec} {name} {cond}: {int(tot['n'])} examples, misses {int(tot['miss_system'])}/{int(tot['miss_judge'])}",
                  file=sys.stderr)
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    md = ["# Cost per example (from the response cache)", "",
          "Per example, averaged over the run. System = calls to the model under test; judge = scoring calls by the "
          "fixed judge (evaluation only). Tokens = prompt + output. Seconds = cached request wall time. All runs were "
          "free (public free tiers or the university GPU server), so the dollar cost is 0.", "",
          "| model | system | cond | n | sys calls | sys tokens in | sys tokens out | sys s | judge calls | judge tokens | misses (sys/judge) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, spec, name, cond, n, a, ms, mj in rows:
        md.append(f"| {spec} | {name} | {cond} | {n} | {a.get('system_calls', 0):.1f} | {a.get('system_in', 0):.0f} | "
                  f"{a.get('system_out', 0):.0f} | {a.get('system_s', 0):.1f} | {a.get('judge_calls', 0):.1f} | "
                  f"{a.get('judge_in', 0) + a.get('judge_out', 0):.0f} | {ms}/{mj} |")
    text = "\n".join(md) + "\n"
    with open(args.out, "w") as fh:
        fh.write(text)
    print(text)


if __name__ == "__main__":
    main()
