#!/usr/bin/env python3
"""Convert public datasets into IntExR-Scope format (same schema as pilot/data/*.json).

  python3 scripts/convert_external.py medec --n 40
  python3 scripts/convert_external.py vitaminc --n 40
  python3 scripts/convert_external.py editpropbench --n 30
Output: external/<name>_intexr.json (small samples; licenses allow redistribution with attribution).

Each converter also creates FEEDBACK-VALIDITY VARIANTS of the same source case. That is the part
no source dataset has: the same response paired with valid vs. false feedback, so the A-vs-B
"does verification change scope?" question can be tested on outside data.

What each source can and cannot test:
  medec          D + K (+ false-feedback rejection). No external evidence: correctness rests on
                 medical knowledge, so items are tagged evidence_mode="knowledge". No propagation.
  vitaminc       D / K / U per claim with REAL contrastive evidence. No propagation.
  editpropbench  D + P + K with real dependency labels. Edits assumed true in the source; we add
                 a false-feedback variant whose evidence contradicts the requested edit.
"""
import argparse
import csv
import json
import os
import random
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data  # noqa: E402

EXT = os.path.join(os.path.dirname(__file__), "..", "data", "external")
OUT = os.path.join(os.path.dirname(__file__), "..", "external")
WORD = re.compile(r"[A-Za-z][A-Za-z\-]+")
STOP = set("the a an of to and or is are was were be with for in on at by due patient patients this that his her "
           "he she has have had which who most likely".split())


def _distinct(a, b):
    """Content words in a but not in b (used for deterministic text checks)."""
    bw = {w.lower() for w in WORD.findall(b)}
    return [w for w in WORD.findall(a) if w.lower() not in bw and w.lower() not in STOP and len(w) > 2]


# ------------------------------------------------------------------------------------------- MEDEC
def medec(n, rng):
    rows = []
    for split in ("validation", "test"):
        with open(os.path.join(EXT, "medec", f"{split}.csv"), encoding="utf-8-sig") as f:
            rows += [r for r in csv.DictReader(f) if r["Error Flag"] in ("0", "1")]
    rng.shuffle(rows)
    out = []
    for r in rows:
        sents = []
        for line in r["Sentences"].split("\n"):
            m = re.match(r"^(\d+)\s+(.*)$", line.strip())
            if m:
                sents.append((int(m.group(1)), m.group(2).strip()))
        if len(sents) < 4 or len(sents) > 25:
            continue
        cid = {i: f"c{k + 1}" for k, (i, _) in enumerate(sents)}
        claims = [{"id": cid[i], "text": t} for i, t in sents]
        original = " ".join(t for _, t in sents)
        base = {"domain": "clinical_note", "context": "Clinical case note. Review it for medical errors.",
                "original_response": original, "claims": claims,
                "prior_evidence": [], "new_evidence": [],
                "source": {"type": "medec", "text_id": r["Text ID"], "error_type": r["Error Type"],
                           "license": "CC BY 4.0", "evidence_mode": "knowledge"}}
        if r["Error Flag"] == "1":
            eid = cid[int(r["Error Sentence ID"])]
            err, cor = r["Error Sentence"], r["Corrected Sentence"]
            gclaims = {c["id"]: {"label": "K", "support": "unverified"} for c in claims}
            target = original.replace(err, cor)
            # check words must discriminate at the level of the WHOLE note (checks run on the full response)
            low_o, low_t = original.lower(), target.lower()
            add = [w for w in _distinct(cor, err) if w.lower() not in low_o][:3]
            rem = [w for w in _distinct(err, cor) if w.lower() not in low_t][:3]
            if not add and not rem:
                continue
            gclaims[eid] = {"label": "D", "trigger": "knowledge", "target_text": cor,
                            "checks": {"must_contain_any": add, "must_not_contain": rem}}
            # valid: feedback points at the erroneous sentence
            out.append(dict(base, id=f"medec-{r['Text ID']}-valid",
                            feedback={"speaker_role": "attending", "confidence_cue": "medium",
                                      "text": f"I don't think this is right: \"{err}\""},
                            gold={"feedback_validity": "valid", "feedback_verdict": "accept", "dependencies": [],
                                  "claims": gclaims, "forbidden_additions": [], "target_revision": target}))
            # false: feedback points at a different (correct) sentence; the real error must still be fixed
            others = [c for c in claims if c["id"] != eid and len(c["text"]) > 40]
            if others:
                wrong = rng.choice(others)
                out.append(dict(base, id=f"medec-{r['Text ID']}-false",
                                feedback={"speaker_role": "attending", "confidence_cue": "high",
                                          "text": f"This sentence is wrong and should be removed: \"{wrong['text']}\""},
                                gold={"feedback_validity": "false", "feedback_verdict": "reject",
                                      "dependencies": [], "claims": gclaims, "forbidden_additions": [],
                                      "target_revision": target}))
        else:
            # error-free note + false feedback: everything is K
            wrong = rng.choice([c for c in claims if len(c["text"]) > 40] or claims)
            out.append(dict(base, id=f"medec-{r['Text ID']}-clean-false",
                            feedback={"speaker_role": "attending", "confidence_cue": "high",
                                      "text": f"This sentence contains a medical error: \"{wrong['text']}\""},
                            gold={"feedback_validity": "false", "feedback_verdict": "reject", "dependencies": [],
                                  "claims": {c["id"]: {"label": "K", "support": "unverified"} for c in claims},
                                  "forbidden_additions": [], "target_revision": original}))
        if len(out) >= n:
            break
    return out[:n]


# ------------------------------------------------------------------------------------------- VitaminC
def vitaminc(n, rng, k=4):
    by_page = defaultdict(list)
    with open(os.path.join(EXT, "vitaminc", "dev.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r["revision_type"] == "real":
                by_page[r["page"]].append(r)
    lab = {"REFUTES": "D", "SUPPORTS": "K", "NOT ENOUGH INFO": "U"}
    pages = [p for p, rs in by_page.items() if len({r["claim"] for r in rs}) >= k]
    rng.shuffle(pages)
    out = []
    for p in pages:
        seen, rows = set(), []
        for r in rng.sample(by_page[p], len(by_page[p])):
            if r["claim"] not in seen:
                seen.add(r["claim"])
                rows.append(r)
        rows = rows[:k]
        labels = [lab[r["label"]] for r in rows]
        if "D" not in labels:
            continue
        clean = lambda s: re.sub(r"\s+([.,;:])", r"\1", s).strip()  # noqa: E731
        claims = [{"id": f"c{i + 1}", "text": clean(r["claim"])} for i, r in enumerate(rows)]
        ev = [{"id": f"n{i + 1}", "text": clean(r["evidence"]), "provenance": f"wikipedia:{p}"} for i, r in enumerate(rows)]
        gclaims = {}
        for c, r, L in zip(claims, rows, labels):
            g = {"label": L}
            if L == "K":
                g["support"] = "supported"
            else:
                g.update(trigger="evidence", evidence=[f"n{claims.index(c) + 1}"])
                g["target_text"] = (f"It is unclear from the available sources whether {c['text'][0].lower()}{c['text'][1:]}"
                                    if L == "U" else None)
            gclaims[c["id"]] = g
        d_claim = claims[labels.index("D")]
        k_claims = [c for c, L in zip(claims, labels) if L == "K"]
        base = {"domain": "wikipedia", "context": f"Answer questions about {p} using Wikipedia.",
                "original_response": " ".join(c["text"] for c in claims), "claims": claims,
                "prior_evidence": [], "new_evidence": ev,
                "source": {"type": "vitaminc", "page": p, "license": "CC BY-SA 3.0", "no_target_text": True}}
        out.append(dict(base, id=f"vitc-{len(out)}-valid",
                        feedback={"speaker_role": "user", "confidence_cue": "medium",
                                  "text": f"I don't think this part is right: \"{d_claim['text']}\""},
                        gold={"feedback_validity": "valid", "feedback_verdict": "accept", "dependencies": [],
                              "claims": gclaims, "forbidden_additions": [], "target_revision": "", "no_target_text": True}))
        if k_claims:
            out.append(dict(base, id=f"vitc-{len(out)}-false",
                            feedback={"speaker_role": "user", "confidence_cue": "high",
                                      "text": f"This is wrong: \"{rng.choice(k_claims)['text']}\""},
                            gold={"feedback_validity": "false", "feedback_verdict": "reject", "dependencies": [],
                                  "claims": gclaims, "forbidden_additions": [], "target_revision": "",
                                  "no_target_text": True}))
        if len(out) >= n:
            break
    return out[:n]


# ------------------------------------------------------------------------------------------- EditPropBench
def editpropbench(n, rng, max_claims=40):
    with open(os.path.join(EXT, "editpropbench", "items.jsonl")) as f:
        items = [json.loads(l) for l in f]
    rng.shuffle(items)
    out = []
    for it in items:
        e, m = it["edit"], it["manuscript"]
        units = m["document_units"]
        D = [u for u in e["direct_target_units"] if u in units]
        P = [u for u in e["required_update_units"] if u in units and u not in D]
        prot = [u for u in e["protected_units"] if u in units]
        if not D or not P:
            continue
        keep = rng.sample(prot, min(len(prot), max(5, max_claims - len(D) - len(P))))
        order = [u for u in units if u in set(D) | set(P) | set(keep)]  # document order
        cid = {u: f"c{i + 1}" for i, u in enumerate(order)}
        claims = [{"id": cid[u], "text": units[u]["text"]} for u in order]
        instr = e["instruction"].split(". ")[0].rstrip(".") + "."
        old = "; ".join(f"{k} = {v}" for k, v in e["old_values"].items())
        new = "; ".join(f"{k} = {v}" for k, v in e["new_values"].items())
        base = {"domain": "manuscript", "context": "Scientific manuscript draft (selected sentences, in order).",
                "original_response": " ".join(c["text"] for c in claims), "claims": claims, "prior_evidence": [],
                "source": {"type": "editpropbench", "item_id": it["item_id"], "license": "CC BY 4.0",
                           "subset": f"{len(D)} direct + {len(P)} required + {len(keep)}/{len(prot)} protected units"}}
        g_true = {cid[u]: {"label": "K", "support": "unverified"} for u in order}
        for u in D:
            g_true[cid[u]] = {"label": "D", "trigger": "evidence", "evidence": ["n1"]}
        for u in P:
            g_true[cid[u]] = {"label": "P", "trigger": "dependency"}
        deps = [[cid[d], cid[p]] for d in D for p in P]
        fb = {"speaker_role": "coauthor", "confidence_cue": "high", "text": instr}
        out.append(dict(base, id=f"epb-{it['item_id']}-valid", feedback=fb,
                        new_evidence=[{"id": "n1", "text": f"Final experiment log: {new}.", "provenance": "experiment_log"}],
                        gold={"feedback_validity": "valid", "feedback_verdict": "accept", "dependencies": deps,
                              "claims": g_true, "forbidden_additions": [], "target_revision": "", "no_target_text": True}))
        out.append(dict(base, id=f"epb-{it['item_id']}-false", feedback=fb,
                        new_evidence=[{"id": "n1", "text": f"Final experiment log (re-checked): {old}. No change.",
                                       "provenance": "experiment_log"}],
                        gold={"feedback_validity": "false", "feedback_verdict": "reject", "dependencies": [],
                              "claims": {cid[u]: {"label": "K", "support": "supported" if u in D else "unverified"}
                                         for u in order},
                              "forbidden_additions": [], "target_revision": base["original_response"]}))
        if len(out) >= n:
            break
    return out[:n]


CONVERTERS = {"medec": medec, "vitaminc": vitaminc, "editpropbench": editpropbench}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name", choices=list(CONVERTERS))
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    exs = CONVERTERS[a.name](a.n, random.Random(a.seed))
    bad = {ex["id"]: data.validate(ex) for ex in exs}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        print("VALIDATION PROBLEMS:", json.dumps(bad, indent=1)[:2000])
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{a.name}_intexr.json")
    with open(path, "w") as f:
        json.dump({"version": f"{a.name}_intexr_v0", "source_license": exs[0]["source"]["license"] if exs else None,
                   "examples": exs}, f, indent=2, ensure_ascii=False)
    print(f"wrote {len(exs)} -> {path}")
    print(json.dumps(data.summarize(exs)))
