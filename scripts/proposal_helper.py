"""Helper for authoring MedScope proposal batches from compact case tuples (paperB/proposals/medec_scope_v0_batch*.json)."""
import json, os, sys

def C(mid, dfp, claims, deps, ev, checks, valid, false, partial, fsup, **extra):
    d = {"medec_id": mid, "false_support": fsup, "decidable_from_prior": dfp,
         "claims": [list(c) for c in claims], "dependencies": [list(x) for x in deps],
         "new_evidence": ev, "checks": checks,
         "feedback": {"valid": valid, "false": list(false), "partial": [partial[0], list(partial[1])]}}
    d.update(extra)
    return d

def write(path, cases, note):
    json.dump({"version": "medec_scope_v0.3_proposals", "status":
               "PROPOSED by Claude (LLM) on 2026-10-27. NOT clinically reviewed. Every case needs clinician review "
               "before use as gold. " + note, "design": "scale-up toward ~150 source cases (Difei, 27 Oct)",
               "cases": cases}, open(path, "w"), indent=1, ensure_ascii=False)
    print("wrote", len(cases), "cases ->", path)
