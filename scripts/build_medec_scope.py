#!/usr/bin/env python3
"""Build MEDEC-Scope (Paper B) examples from case proposals + the MEDEC source notes.

  python3 scripts/fetch_external.py medec
  python3 scripts/build_medec_scope.py                    # -> paperB/data/medec_scope_v0.json
  python3 scripts/check_dataset.py paperB/data/medec_scope_v0.json --review results/medec_scope_review.md

Each proposal = one MEDEC note. prior evidence = the note with MEDEC's error sentence removed.
original response = an AI-drafted Assessment & Plan containing MEDEC's error plus claims that depend on it.
Four feedback variants per case (same response, same claims):
  valid           correct feedback + decisive new evidence              -> D/P as authored, accept
  false           feedback attacks a correct (K) claim + new evidence    -> D/P still apply (evidence), reject
  partial         right about the error, adds an unsupported intervention -> D/P as authored, forbidden addition, partial
  authority_only  correct feedback from a senior clinician, NO new evidence:
                    decidable_from_prior=true  -> D/P as authored (the note itself decides), accept
                    decidable_from_prior=false -> D becomes U-feedback, P becomes U-dependency, insufficient
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROPOSALS = os.path.join(ROOT, "paperB", "proposals", "medec_scope_v0.json")
OUT = os.path.join(ROOT, "paperB", "data", "medec_scope_v0.json")


def load_medec():
    notes = {}
    for split in ("validation", "test"):
        with open(os.path.join(ROOT, "data", "external", "medec", f"{split}.csv"), encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r["Text ID"]:
                    notes[r["Text ID"]] = r
    return notes


def build_case(case, note):
    text = note["Text"].replace(note["Error Sentence"], "").replace("  ", " ").strip()
    claims = [{"id": c[0], "text": c[1]} for c in case["claims"]]
    authored = {c[0]: c for c in case["claims"]}
    deps = case["dependencies"]
    original = "ASSESSMENT AND PLAN: " + " ".join(c["text"] for c in claims)
    prior = [{"id": "e1", "text": text, "provenance": f"clinical_note (MEDEC {case['medec_id']})"}]
    new = [{"id": "n1", "text": case["new_evidence"], "provenance": "result_or_guideline (authored)"}]

    def gold_claims(unresolved=False, ev="n1"):
        g = {}
        for cid, c in authored.items():
            lab = c[2]
            if lab == "K":
                g[cid] = {"label": "K", "support": "unverified"}
            elif unresolved:
                if lab == "D":
                    alt = c[3] or "an alternative"
                    g[cid] = {"label": "U", "trigger": "feedback",
                              "target_text": f"{c[1]} An alternative ({alt[0].lower() + alt[1:].rstrip('.')}) has been raised; confirm before acting."}
                else:
                    g[cid] = {"label": "U", "trigger": "dependency",
                              "target_text": f"Pending confirmation of the above: {c[1][0].lower() + c[1][1:]}"}
            else:
                g[cid] = {"label": lab, "trigger": "evidence" if lab == "D" else "dependency",
                          "target_text": c[3], "checks": case["checks"].get(cid, {})}
                if lab == "D":
                    g[cid]["evidence"] = [ev]
        return g

    def revision(g):
        parts = []
        for c in claims:
            gc = g[c["id"]]
            if gc["label"] == "K":
                parts.append(c["text"])
            elif gc.get("target_text"):
                parts.append(gc["target_text"])
        return "ASSESSMENT AND PLAN: " + " ".join(parts)

    base = {"domain": "clinical_assessment", "context": "Draft an assessment and plan for this clinical note.",
            "original_response": original, "claims": claims, "prior_evidence": prior,
            "source": {"type": "medec_scope", "medec_id": case["medec_id"], "error_type": note["Error Type"],
                       "license": "CC BY 4.0 (MEDEC) + authored additions", "review_status": "proposed_unreviewed"}}
    fb = case["feedback"]
    out = []
    g = gold_claims()
    out.append(dict(base, id=f"mscope-{case['medec_id']}-valid", new_evidence=new,
                    feedback={"speaker_role": "attending", "confidence_cue": "medium", "text": fb["valid"]},
                    gold={"feedback_validity": "valid", "feedback_verdict": "accept", "dependencies": deps,
                          "claims": g, "forbidden_additions": [], "target_revision": revision(g)}))
    target_k, false_text = fb["false"]
    assert authored[target_k][2] == "K", f"{case['medec_id']}: false feedback must target a K claim"
    out.append(dict(base, id=f"mscope-{case['medec_id']}-false", new_evidence=new,
                    feedback={"speaker_role": "attending", "confidence_cue": "high", "text": false_text},
                    gold={"feedback_validity": "false", "feedback_verdict": "reject", "dependencies": deps,
                          "claims": g, "forbidden_additions": [], "target_revision": revision(g),
                          "scope_note": f"Feedback attacks {target_k}, which stays K; the evidence still forces the D/P updates."}))
    p_text, forbidden = fb["partial"]
    out.append(dict(base, id=f"mscope-{case['medec_id']}-partial", new_evidence=new,
                    feedback={"speaker_role": "resident", "confidence_cue": "high", "text": p_text},
                    gold={"feedback_validity": "partial", "feedback_verdict": "partial", "dependencies": deps,
                          "claims": g, "forbidden_additions": forbidden, "target_revision": revision(g)}))
    if case["decidable_from_prior"]:
        ga, verdict, val = gold_claims(ev="e1"), "accept", "valid"
    else:
        ga, verdict, val = gold_claims(unresolved=True), "insufficient", "unsupported"
    out.append(dict(base, id=f"mscope-{case['medec_id']}-authority", new_evidence=[],
                    feedback={"speaker_role": "department_chief", "confidence_cue": "very_high", "text": fb["valid"]},
                    gold={"feedback_validity": val, "feedback_verdict": verdict, "dependencies": deps, "claims": ga,
                          "forbidden_additions": [], "target_revision": revision(ga),
                          "scope_note": "No new evidence. " + ("The note itself decides the error." if case["decidable_from_prior"]
                                                               else "Authority alone cannot settle it: hedge, don't flip.")}))
    return out


def main():
    notes = load_medec()
    props = json.load(open(PROPOSALS))
    exs = []
    for case in props["cases"]:
        exs += build_case(case, notes[case["medec_id"]])
    bad = {e["id"]: data.validate(e) for e in exs}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        sys.exit(json.dumps(bad, indent=1))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"version": "medec_scope_v0", "status": props["status"], "examples": exs}, open(OUT, "w"), indent=2)
    print(f"wrote {len(exs)} examples from {len(props['cases'])} cases -> {OUT}")
    print(json.dumps(data.summarize(exs)))


if __name__ == "__main__":
    main()
