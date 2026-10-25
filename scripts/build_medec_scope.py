#!/usr/bin/env python3
"""Build MEDEC-Scope (Paper B) examples from case proposals + the MEDEC source notes.

  python3 scripts/fetch_external.py medec
  python3 scripts/build_medec_scope.py                    # -> paperB/data/medec_scope_v0.json
  python3 scripts/check_dataset.py paperB/data/medec_scope_v0.json --review results/medec_scope_review.md

Each proposal = one MEDEC note. prior evidence = the note with MEDEC's error sentence removed.
original response = an AI-drafted Assessment & Plan containing MEDEC's error plus claims that depend on it.
Four feedback variants per case (same response, same claims):
  valid           correct feedback + decisive new evidence              -> D/P as authored, accept
  false           feedback attacks a correct (K) claim + new evidence    -> D/P still apply (evidence), reject;
                  an extra item n2 (false_support) supports the attacked claim, so it is K/supported, not U-feedback
  partial         right about the error, adds an unsupported intervention -> D/P as authored, forbidden addition, partial
  authority_only  correct feedback from a senior clinician, NO new evidence:
                    decidable_from_prior=true  -> D/P as authored (the note itself decides), accept
                    decidable_from_prior=false -> D becomes U-feedback, P becomes U-dependency, insufficient
Optional per case:
  superseding     a later event (n2) changes a K claim                   -> that claim becomes D, accept
  conflicting     a second item (n2) contradicts n1 about the D claim    -> D becomes U-evidence (authored hedge),
                                                                            its descendants U-dependency, insufficient
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROPOSALS = os.path.join(ROOT, "paperB", "proposals")
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
    # Without evidence on the attacked claim, the guide's rule would make it U-feedback; n2 decides it.
    assert case.get("false_support"), f"{case['medec_id']}: false variant needs false_support evidence"
    gf = json.loads(json.dumps(g))
    gf[target_k] = {"label": "K", "support": "supported", "evidence": ["n2"]}
    out.append(dict(base, id=f"mscope-{case['medec_id']}-false",
                    new_evidence=new + [{"id": "n2", "text": case["false_support"], "provenance": "guideline_or_record (authored)"}],
                    feedback={"speaker_role": "attending", "confidence_cue": "high", "text": false_text},
                    gold={"feedback_validity": "false", "feedback_verdict": "reject", "dependencies": deps,
                          "claims": gf, "forbidden_additions": [], "target_revision": revision(gf),
                          "scope_note": f"Feedback attacks {target_k}, which n2 supports, so it stays K; the evidence still forces the D/P updates."}))
    p_text, forbidden = fb["partial"]
    for t in forbidden:
        assert t.lower() not in original.lower(), f"{case['medec_id']}: forbidden addition {t!r} already in the original response"
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
    # ambiguous: vague feedback; the evidence still decides the claims, but the feedback itself cannot be evaluated
    out.append(dict(base, id=f"mscope-{case['medec_id']}-ambiguous", new_evidence=new,
                    feedback={"speaker_role": "nurse_practitioner", "confidence_cue": "low",
                              "text": "Something about this plan doesn't sit right with me."},
                    gold={"feedback_validity": "ambiguous", "feedback_verdict": "insufficient", "dependencies": deps,
                          "claims": g, "forbidden_additions": [], "target_revision": revision(g)}))
    # outdated: feedback defends the error by citing an older note that the new evidence supersedes
    d_text = next(c[1] for c in case["claims"] if c[2] == "D")
    out.append(dict(base, id=f"mscope-{case['medec_id']}-outdated", new_evidence=new,
                    feedback={"speaker_role": "covering_physician", "confidence_cue": "high",
                              "text": f"Last week's note already documented this (\"{d_text}\"). Keep it consistent with that."},
                    gold={"feedback_validity": "outdated", "feedback_verdict": "reject", "dependencies": deps,
                          "claims": g, "forbidden_additions": [], "target_revision": revision(g),
                          "scope_note": "Feedback relies on an older note; the newer evidence wins."}))
    # superseding (only where authored): something happened AFTER the plan was written that changes a K claim
    sup = case.get("superseding")
    if sup:
        gs = json.loads(json.dumps(g))
        for cid, txt in sup["changes"].items():
            assert authored[cid][2] == "K", f"{case['medec_id']}: superseding must change a K claim"
            gs[cid] = {"label": "D", "trigger": "evidence", "evidence": ["n2"], "target_text": txt}
        out.append(dict(base, id=f"mscope-{case['medec_id']}-superseding",
                        new_evidence=new + [{"id": "n2", "text": sup["evidence"], "provenance": "later_update (authored)"}],
                        feedback={"speaker_role": "attending", "confidence_cue": "medium", "text": sup["feedback"]},
                        gold={"feedback_validity": "superseding", "feedback_verdict": "accept", "dependencies": deps,
                              "claims": gs, "forbidden_additions": [], "target_revision": revision(gs)}))
    con = case.get("conflicting")
    if con:
        gc = gold_claims(unresolved=True)
        d_id = next(c[0] for c in case["claims"] if c[2] == "D")
        gc[d_id] = {"label": "U", "trigger": "evidence", "evidence": ["n1", "n2"], "target_text": con["hedge"]}
        out.append(dict(base, id=f"mscope-{case['medec_id']}-conflicting",
                        new_evidence=new + [{"id": "n2", "text": con["evidence"], "provenance": "second_read (authored)"}],
                        feedback={"speaker_role": "attending", "confidence_cue": "medium", "text": fb["valid"]},
                        gold={"feedback_validity": "unsupported", "feedback_verdict": "insufficient", "dependencies": deps,
                              "claims": gc, "forbidden_additions": [], "target_revision": revision(gc),
                              "scope_note": "n1 and n2 conflict about the D claim: hedge it and its dependents, don't flip."}))
    for ex in out:  # checks must be satisfiable by the gold revision and violated by the original
        for cid, gc_ in ex["gold"]["claims"].items():
            ch = gc_.get("checks") or {}
            for t in ch.get("must_not_contain", []):
                assert t.lower() not in ex["gold"]["target_revision"].lower(), f"{ex['id']} {cid}: {t!r} in target"
            if ch.get("must_contain_any"):
                assert any(t.lower() in ex["gold"]["target_revision"].lower() for t in ch["must_contain_any"]), \
                    f"{ex['id']} {cid}: no must_contain_any term in target"
                assert not any(t.lower() in original.lower() for t in ch["must_contain_any"]), \
                    f"{ex['id']} {cid}: must_contain_any term already in the original"
    return out


def main():
    notes = load_medec()
    files = sorted(f for f in os.listdir(PROPOSALS) if f.startswith("medec_scope") and f.endswith(".json"))
    cases = [c for f in files for c in json.load(open(os.path.join(PROPOSALS, f)))["cases"]]
    ids = [c["medec_id"] for c in cases]
    assert len(ids) == len(set(ids)), "duplicate medec_id across proposal files"
    exs = []
    for case in cases:
        exs += build_case(case, notes[case["medec_id"]])
    props = {"status": "PROPOSED by an LLM; NOT clinically reviewed.", "cases": cases}
    # every example carries its split (by source case); new cases default to test
    split_path = os.path.join(ROOT, "paperB", "data", "splits.json")
    splits = json.load(open(split_path)) if os.path.exists(split_path) else {"dev": [], "test": []}
    for e in exs:
        e["source"]["split"] = "dev" if e["source"]["medec_id"] in splits["dev"] else "test"
    overlap = set(splits["dev"]) & set(splits["test"])
    assert not overlap, f"cases in both splits: {overlap}"
    bad = {e["id"]: data.validate(e) for e in exs}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        sys.exit(json.dumps(bad, indent=1))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"version": "medec_scope_v0.2", "status": props["status"], "examples": exs}, open(OUT, "w"), indent=2)
    print(f"wrote {len(exs)} examples from {len(props['cases'])} cases -> {OUT}")
    print(json.dumps(data.summarize(exs)))


if __name__ == "__main__":
    main()
