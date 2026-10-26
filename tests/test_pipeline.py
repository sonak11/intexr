"""If the LLM stages of the scope pipeline were perfect, the deterministic stages must reproduce the gold labels,
verdicts, and checks exactly. Each failure is either a pipeline bug or a gold example that breaks the guide's rules.

    python3 -m unittest tests.test_pipeline -v
"""
import glob
import json
import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from intexr import data, gate, metrics, scope  # noqa: E402

FILES = ["paperB/data/medec_scope_v0.json", "pilot/data/pilot_v0.json"] + sorted(glob.glob(os.path.join(ROOT, "external", "*_intexr.json")))


def gold_alignment(ex):
    g = ex["gold"]
    ev_ids = [e["id"] for e in ex["prior_evidence"] + ex["new_evidence"]]
    parents = {}
    for a, b in g["dependencies"]:
        parents.setdefault(b, []).append(a)
    claims = []
    for c in ex["claims"]:
        gc = g["claims"][c["id"]]
        ev = gc.get("evidence") or []
        if gc["label"] == "D":
            rel = [{"id": e, "relation": "contradicts"} for e in (ev or ev_ids[-1:])]
        elif gc["label"] == "U" and gc.get("trigger") == "evidence":
            new = [e for e in ev if e in {x["id"] for x in ex["new_evidence"]}]
            if len(new) > 1:  # two new items disagree
                rel = [{"id": new[0], "relation": "contradicts"}] + [{"id": e, "relation": "supports"} for e in new[1:]]
            else:  # the newest item leaves it undetermined
                rel = [{"id": e, "relation": "uncertain"} for e in (new or ev or ev_ids[-1:])]
        elif gc["label"] == "K" and gc.get("support") == "supported":
            rel = [{"id": e, "relation": "supports"} for e in ev]
        else:
            rel = []
        claims.append({"id": c["id"], "evidence": rel, "depends_on": parents.get(c["id"], [])})
    disputes = [c for c, gc in g["claims"].items() if gc["label"] == "U" and gc.get("trigger") == "feedback"]
    return {"claims": claims, "feedback": {"disputes": disputes, "verdict": g["feedback_verdict"]}}


def fake_client(ex):
    g = ex["gold"]["claims"]

    def client(system, messages):
        if system == scope.ALIGN_SYS:
            return json.dumps(gold_alignment(ex))
        assert system == scope.REVISE_SYS
        want = [line.split(" ", 1)[0] for line in messages[0]["content"].split("CLAIMS TO HANDLE:\n", 1)[1].splitlines()
                if line[:1] == "c" or line[:1].isalnum() and "[" in line]
        return json.dumps({c: (g[c].get("target_text") if g[c]["label"] != "K" else "UNCHANGED") for c in want if c in g})
    return client


class GoldScorer:
    def __init__(self, ex):
        self.ex = ex

    def score_example(self, claims, evidence):
        g = self.ex["gold"]["claims"]
        out = {}
        for c in claims:
            for e in evidence:
                lab = "contradiction" if g[c["id"]]["label"] == "D" and e["id"] in (g[c["id"]].get("evidence") or [e["id"]]) \
                    else "neutral"
                out[(c["id"], e["id"])] = {k: float(k == lab) for k in gate.LABELS3}
        return out


class TestPipeline(unittest.TestCase):
    def test_gold_alignment_reproduces_oracle(self):
        for f in FILES:
            path = os.path.join(ROOT, f)
            if not os.path.exists(path):
                continue
            exs = data.load(path)
            rows, fails = [], []
            for ex in exs:
                if ex["gold"].get("no_target_text") or ex["source"].get("no_target_text"):
                    continue  # VitaminC has labels but no target texts
                if ex["source"].get("evidence_mode") == "knowledge":
                    continue  # MEDEC-knowledge: D comes from medical knowledge, outside an evidence-gated method
                p = scope.run(ex, fake_client(ex), condition="B")
                r = metrics.per_example(ex, p)
                rows.append(r)
                wrong = {c: (ex["gold"]["claims"][c]["label"], p["claims"][c]["label"])
                         for c in p["claims"] if p["claims"][c]["label"] != ex["gold"]["claims"][c]["label"]}
                if wrong or r.get("verdict_ok", 1) != 1 or r.get("chk_ok", 0) != r.get("chk_n", 0):
                    fails.append((ex["id"], wrong, p["verdict"], ex["gold"]["feedback_verdict"]))
            with self.subTest(file=f):
                self.assertEqual(fails, [], f"{f}: {len(fails)} examples differ, e.g. {fails[:5]}")

    def test_assemble(self):
        claims = [{"id": "c1", "text": "A is true."}, {"id": "c2", "text": "So B."}, {"id": "c3", "text": "C."}]
        orig = "PLAN: A is true. So B. C."
        self.assertEqual(scope.assemble(orig, claims, {"c1": "A is false.", "c2": None}), "PLAN: A is false. C.")
        self.assertEqual(scope.assemble(orig, claims, {}), orig)

    def test_direct_status_precedence(self):
        tier = {"e1": 0, "n1": 1, "n2": 1}
        self.assertEqual(scope.direct_status([{"id": "e1", "relation": "supports"}, {"id": "n1", "relation": "contradicts"}], tier), "D")
        self.assertEqual(scope.direct_status([{"id": "n1", "relation": "supports"}, {"id": "n2", "relation": "contradicts"}], tier), "U")
        self.assertEqual(scope.direct_status([{"id": "n1", "relation": "supports"}], tier), "S")
        self.assertIsNone(scope.direct_status([], tier))

    def test_rule_verdict(self):
        v = {"feedback": {"speaker_role": "attending", "text": "x"}}
        al = lambda d: {"feedback": {"disputes": d, "verdict": "partial"}}
        final = {"c1": {"label": "K"}, "c2": {"label": "D"}, "c3": {"label": "P"}, "c4": {"label": "U"}}
        self.assertEqual(scope.decide_verdict(v, al(["c2"]), final, set()), "accept")          # valid feedback
        self.assertEqual(scope.decide_verdict(v, al(["c2"]), final, {"phenytoin"}), "partial")  # adds unsupported content
        self.assertEqual(scope.decide_verdict(v, al(["c1"]), final, set()), "reject")           # attacks a kept claim
        self.assertEqual(scope.decide_verdict(v, al(["c4"]), final, set()), "insufficient")     # evidence cannot settle it
        self.assertEqual(scope.decide_verdict(v, al([]), final, set()), "partial")               # no dispute: model's verdict
        self.assertIsNone(scope.decide_verdict({"feedback": None}, al([]), final, set()))

    def test_gate_plumbing(self):
        ex = data.load(os.path.join(ROOT, FILES[0]))[0]
        p = gate.run(ex, GoldScorer(ex))
        d = [c for c, gc in ex["gold"]["claims"].items() if gc["label"] == "D"]
        self.assertTrue(all(p["claims"][c]["label"] == "D" for c in d))
        self.assertTrue(all(p["claims"][c]["label"] != "P" for c in p["claims"]))  # the gate never propagates


if __name__ == "__main__":
    unittest.main()
