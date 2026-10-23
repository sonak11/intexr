"""Claim-level evidence gate baseline (thesis plan: "a simple claim-level evidence gate").

For every (claim, evidence item) pair an NLI scorer returns entailment / neutral / contradiction.
  contradiction by any item              -> D   (the claim is removed; the gate writes no new text)
  otherwise, feedback overlaps the claim -> U   if no item entails it (hedged with a fixed prefix), else K
  otherwise                              -> K
There is no propagation: dependent claims are never touched. That is the point of the baseline: it
shows how far claim-local verification gets, and how much of the gold change set is P.

Scorer specs (the part after '@' in --systems evidence_gate@SPEC):
  hf:<model id>        local transformers NLI model (thasos / Kaggle GPU or CPU), e.g.
                       hf:MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli  (verify the id on HF first)
  <provider>:<model>   any LLM client spec (intexr.clients); one call per example scores all pairs
Scores are cached in results/.cache like LLM responses.
"""
import hashlib
import json
import os

from . import prompts
from .clients import CACHE_DIR, Client
from .data import model_view
from .scope import assemble, content_words, evidence_for

LABELS3 = ("entailment", "neutral", "contradiction")
HEDGE = "Unconfirmed (disputed, not settled by the evidence): "


class HFScorer:
    """Premise = evidence text, hypothesis = claim text. Label names are read from the model config."""

    def __init__(self, model_id, batch_size=16):
        from transformers import AutoModelForSequenceClassification, AutoTokenizer  # noqa: PLC0415
        import torch  # noqa: PLC0415
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id).eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.id2label = {i: l.lower() for i, l in self.model.config.id2label.items()}
        self.name, self.batch_size = model_id, batch_size

    def score_pairs(self, pairs):
        out = []
        for k in range(0, len(pairs), self.batch_size):
            chunk = pairs[k:k + self.batch_size]
            enc = self.tok([p for p, _ in chunk], [h for _, h in chunk], truncation=True, max_length=512,
                           padding=True, return_tensors="pt").to(self.device)
            with self.torch.no_grad():
                probs = self.torch.softmax(self.model(**enc).logits, -1).cpu().tolist()
            for pr in probs:
                d = {lab: 0.0 for lab in LABELS3}
                for i, p in enumerate(pr):
                    lab = self.id2label[i]
                    lab = "contradiction" if lab.startswith("contra") else "entailment" if lab.startswith("entail") \
                        else "neutral"
                    d[lab] += p
                out.append(d)
        return out


NLI_SYS = """For each (claim, evidence) pair, decide the relation of the EVIDENCE to the CLAIM:
  entailment     the evidence states or directly confirms the claim
  contradiction  the evidence shows the claim is false or makes it moot
  neutral        the evidence does not settle the claim
Judge each pair on its own; do not use the other evidence items or background knowledge.
Return ONLY JSON: {"<claim id>|<evidence id>": "entailment|neutral|contradiction", ...}"""


class LLMScorer:
    def __init__(self, spec):
        self.client, self.name = Client(spec), spec

    def score_example(self, claims, evidence):
        user = ("CLAIMS:\n" + "\n".join(f"{c['id']}: {c['text']}" for c in claims) +
                "\n\nEVIDENCE:\n" + prompts._evidence_block(evidence) +
                "\n\nPAIRS:\n" + "\n".join(f"{c['id']}|{e['id']}" for c in claims for e in evidence))
        raw = self.client(NLI_SYS, [{"role": "user", "content": user}])  # API failures propagate
        try:
            out = prompts.parse_json(raw)
            out = out if isinstance(out, dict) else {}
        except ValueError:
            out = {}
        res = {}
        for c in claims:
            for e in evidence:
                lab = str(out.get(f"{c['id']}|{e['id']}", "neutral")).lower()
                lab = lab if lab in LABELS3 else "neutral"
                res[(c["id"], e["id"])] = {k: float(k == lab) for k in LABELS3}
        return res


class CachedHF:
    def __init__(self, model_id):
        self.model_id, self._m = model_id, None
        self.name = "hf:" + model_id

    def score_example(self, claims, evidence):
        pairs = [(e["text"], c["text"]) for c in claims for e in evidence]
        keys = [hashlib.sha256(json.dumps(["nli", self.model_id, p, h]).encode()).hexdigest() for p, h in pairs]
        res, todo = {}, []
        for i, k in enumerate(keys):
            path = os.path.join(CACHE_DIR, k + ".json")
            if os.path.exists(path):
                with open(path) as f:
                    res[i] = json.load(f)
            else:
                todo.append(i)
        if todo:
            if self._m is None:
                self._m = HFScorer(self.model_id)
            scores = self._m.score_pairs([pairs[i] for i in todo])
            os.makedirs(CACHE_DIR, exist_ok=True)
            for i, s in zip(todo, scores):
                res[i] = s
                with open(os.path.join(CACHE_DIR, keys[i] + ".json"), "w") as f:
                    json.dump(s, f)
        ids = [(c["id"], e["id"]) for c in claims for e in evidence]
        return {ids[i]: res[i] for i in range(len(ids))}


def make_scorer(spec):
    return CachedHF(spec[3:]) if spec.startswith("hf:") else LLMScorer(spec)


def _top(d):
    return max(LABELS3, key=lambda k: d.get(k, 0.0))


def run(ex, client, judge=None, condition="B", **_):
    """`client` is a scorer from make_scorer (run_pilot builds it for evidence_gate)."""
    v = model_view(ex, condition)
    ev = evidence_for(v)
    scores = client.score_example(v["claims"], ev) if ev else {}
    fb = v.get("feedback")
    fbw = content_words(fb["text"]) if fb and fb.get("speaker_role") != "verified_editor" else set()
    claims, new_text = {}, {}
    for c in v["claims"]:
        rel = [_top(scores[(c["id"], e["id"])]) for e in ev]
        if "contradiction" in rel:
            claims[c["id"]] = {"label": "D", "revised_text": None, "status": "removed"}
            new_text[c["id"]] = None
        elif fbw & content_words(c["text"]) and "entailment" not in rel:
            t = HEDGE + c["text"]
            claims[c["id"]] = {"label": "U", "revised_text": t, "status": "hedged"}
            new_text[c["id"]] = t
        else:
            claims[c["id"]] = {"label": "K", "status": "keep"}
    revised = assemble(v["original_response"], v["claims"], new_text)
    labs = {x["label"] for x in claims.values()}
    verdict = None if fb is None else ("accept" if "D" in labs else "insufficient" if "U" in labs else "reject")
    return {"id": ex["id"], "system": "evidence_gate", "structured": True, "verdict": verdict,
            "revised_response": revised, "claims": claims}
