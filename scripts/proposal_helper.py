"""Helper for authoring MedScope proposal batches (paperB/proposals/medec_scope_v0_batch*.json) from compact case
tuples, with a lint that reports every check-term clash at once. Usage: from proposal_helper import C, write"""
import json, os, re, sys


def _has(text, term):  # same matching rule as intexr.metrics._has
    return re.search(r"(?<![a-z])" + re.escape(term.lower()), text.lower()) is not None

def C(mid, dfp, claims, deps, ev, checks, valid, false, partial, fsup, **extra):
    d = {"medec_id": mid, "false_support": fsup, "decidable_from_prior": dfp,
         "claims": [list(c) for c in claims], "dependencies": [list(x) for x in deps],
         "new_evidence": ev, "checks": checks,
         "feedback": {"valid": valid, "false": list(false), "partial": [partial[0], list(partial[1])]}}
    d.update(extra)
    return d

def write(path, cases, note):
    lint(cases)
    json.dump({"version": "medec_scope_v0.3_proposals", "status":
               "PROPOSED by Claude (LLM) on 2026-10-27. NOT clinically reviewed. Every case needs clinician review "
               "before use as gold. " + note, "design": "scale-up toward ~150 source cases (Difei, 27 Oct)",
               "cases": cases}, open(path, "w"), indent=1, ensure_ascii=False)
    print("wrote", len(cases), "cases ->", path)

def lint(cases):
    """Report every check-term problem at once (the builder stops at the first)."""
    bad = []
    for c in cases:
        orig = " ".join(x[1] for x in c["claims"]).lower()
        tgt = {x[0]: (x[3] if len(x) > 3 else x[1]) for x in c["claims"]}
        tall = " ".join(tgt.values()).lower()
        for cid, ch in c["checks"].items():
            for t in ch.get("must_contain_any", []):
                if _has(orig, t):
                    bad.append((c["medec_id"], cid, "in original", t))
            if ch.get("must_contain_any") and not any(_has(tall, t) for t in ch["must_contain_any"]):
                bad.append((c["medec_id"], cid, "no must_contain in target", ch["must_contain_any"]))
            for t in ch.get("must_not_contain", []):
                if _has(tall, t):
                    bad.append((c["medec_id"], cid, "must_not in target", t))
        for t in c["feedback"]["partial"][1]:
            if t.lower() in orig:
                bad.append((c["medec_id"], "partial", "forbidden in original", t))
    for b in bad:
        print("LINT", *b)
    return bad
