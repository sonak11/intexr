"""Prompt templates for the pilot systems and the claim-alignment judge."""
import json


def _evidence_block(items):
    if not items:
        return "(none)"
    return "\n".join(f"[{e['id']}] ({e.get('provenance', '')}{', ' + e['time'] if e.get('time') else ''}) {e['text']}"
                     for e in items)


def _feedback_block(fb):
    if not fb:
        return "(no feedback)"
    return f"From {fb['speaker_role']}: \"{fb['text']}\""


# ---------------------------------------------------------------- dialogue
def dialogue_messages(v):
    """Ordinary chat: the user pastes feedback and new information; no revision guidance."""
    turn = _feedback_block(v["feedback"]) if v["feedback"] else ""
    if v["new_evidence"]:
        turn += "\n\nAdditional information:\n" + "\n".join(e["text"] for e in v["new_evidence"])
    turn += "\n\nPlease update your response."
    return None, [
        {"role": "user", "content": v["context"] + "\n\nAvailable information:\n" +
         "\n".join(e["text"] for e in v["prior_evidence"])},
        {"role": "assistant", "content": v["original_response"]},
        {"role": "user", "content": turn.strip()},
    ]


# ---------------------------------------------------------------- evidence-aware prompt
EVIDENCE_SYS = """You revise a previous response in light of feedback and new evidence.
Rules:
- Feedback may be wrong, partly wrong, vague, or outdated. Check it against the evidence; do not accept it on authority alone.
- Change only what the evidence requires, including statements that were inferred from something you change.
- Keep every other sentence exactly as written.
- If the evidence is insufficient or conflicting about a statement, say so explicitly instead of asserting or deleting it.
- Do not add facts that are not supported by the evidence.
Return only the revised response text."""


def evidence_messages(v):
    user = (f"TASK: {v['context']}\n\nPRIOR EVIDENCE:\n{_evidence_block(v['prior_evidence'])}\n\n"
            f"PREVIOUS RESPONSE:\n{v['original_response']}\n\nFEEDBACK:\n{_feedback_block(v['feedback'])}\n\n"
            f"NEW EVIDENCE:\n{_evidence_block(v['new_evidence'])}")
    return EVIDENCE_SYS, [{"role": "user", "content": user}]


# ---------------------------------------------------------------- always rewrite
REWRITE_SYS = """Write a new, complete response to the task using all of the evidence and the feedback.
You may restructure freely. Return only the new response text."""


def rewrite_messages(v):
    _, msgs = evidence_messages(v)
    return REWRITE_SYS, msgs


# ---------------------------------------------------------------- scope-first (structured)
SCOPE_SYS = """You perform evidence-scoped revision of a multi-claim response.

Principle: feedback is a hypothesis; evidence is the arbiter. Never change a claim because of feedback alone.

Steps:
1. For each numbered claim, find evidence items that support, contradict, refine, or are silent about it.
2. Identify which claims were inferred from which other claims (dependencies).
3. Assign exactly one label per claim:
   D  direct update: an evidence item itself contradicts, refines, or makes the claim moot.
   P  propagated update: no evidence addresses it directly, but it depends on a D (or P) claim and no longer holds.
   U  unresolved: evidence is insufficient or conflicting about it, it depends on a U claim, or feedback disputes it with no evidence either way. Hedge it; do not delete it.
   K  keep: none of the above. It must stay word-for-word unchanged.
   Precedence: direct evidence > dependency > unsupported feedback > keep.
4. Judge the feedback overall: accept (supported), partial (some supported, some not), reject (contradicted or irrelevant to what the response describes), insufficient (cannot be decided from the evidence).
5. Write revised_text for D/P/U claims (null deletes a D/P claim). Then write the full revised response: K claims verbatim, minimal changes elsewhere, nothing unsupported added.

Return ONLY a JSON object:
{"feedback_assessment": {"verdict": "accept|partial|reject|insufficient", "rationale": "..."},
 "claims": [{"id": "c1", "label": "D|P|U|K", "depends_on": [], "evidence": [], "revised_text": "... or null"}],
 "additions": [],
 "revised_response": "..."}"""


def scope_messages(v):
    claims = "\n".join(f"{c['id']}: {c['text']}" for c in v["claims"])
    user = (f"TASK: {v['context']}\n\nPRIOR EVIDENCE:\n{_evidence_block(v['prior_evidence'])}\n\n"
            f"ORIGINAL RESPONSE:\n{v['original_response']}\n\nCLAIMS:\n{claims}\n\n"
            f"FEEDBACK:\n{_feedback_block(v['feedback'])}\n\nNEW EVIDENCE:\n{_evidence_block(v['new_evidence'])}")
    return SCOPE_SYS, [{"role": "user", "content": user}]


# ---------------------------------------------------------------- verify-then-revise (CoVe / RARR-style baseline)
VERIFY_SYS = """You check each numbered claim of a previous response against the evidence, one claim at a time.
For every claim:
1. Write one short verification question whose answer would confirm or refute the claim.
2. Answer it using ONLY the evidence items (cite their ids). Do not use the feedback as evidence.
3. Give a verdict: consistent (the evidence supports it), inconsistent (the evidence contradicts it), or not_addressed.
Return ONLY JSON: {"c1": {"question": "...", "answer": "...", "evidence": ["n1"], "verdict": "consistent|inconsistent|not_addressed"}, ...}"""

VERIFIED_REVISE_SYS = """You revise a previous response using the results of a claim-by-claim verification against evidence.
Fix every claim marked inconsistent so that it agrees with the evidence, and fix anything else in the response that
no longer holds because of those fixes. Leave the rest of the response as it is. Feedback may be wrong; follow the
evidence. Return only the revised response text."""


def verify_messages(v):
    claims = "\n".join(f"{c['id']}: {c['text']}" for c in v["claims"])
    user = (f"TASK: {v['context']}\n\nPRIOR EVIDENCE:\n{_evidence_block(v['prior_evidence'])}\n\n"
            f"NEW EVIDENCE:\n{_evidence_block(v['new_evidence'])}\n\nFEEDBACK:\n{_feedback_block(v['feedback'])}\n\n"
            f"CLAIMS:\n{claims}")
    return VERIFY_SYS, [{"role": "user", "content": user}]


def verified_revise_messages(v, checks):
    lines = "\n".join(f"{cid}: {c.get('verdict', '?')} | Q: {c.get('question', '')} | A: {c.get('answer', '')}"
                      for cid, c in checks.items() if isinstance(c, dict))
    user = (f"TASK: {v['context']}\n\nPRIOR EVIDENCE:\n{_evidence_block(v['prior_evidence'])}\n\n"
            f"NEW EVIDENCE:\n{_evidence_block(v['new_evidence'])}\n\nFEEDBACK:\n{_feedback_block(v['feedback'])}\n\n"
            f"PREVIOUS RESPONSE:\n{v['original_response']}\n\nVERIFICATION RESULTS:\n{lines or '(verification failed)'}")
    return VERIFIED_REVISE_SYS, [{"role": "user", "content": user}]


# ---------------------------------------------------------------- claim-alignment judge
JUDGE_SYS = """You compare an ORIGINAL response with a REVISED response, claim by claim.
For each original claim, decide what the revision did to it:
  keep     the claim's meaning is unchanged (rewording that preserves meaning counts as keep)
  revised  the claim's content was changed (corrected, replaced, refined)
  removed  the claim no longer appears in any form
  hedged   the claim is still present but now explicitly marked as uncertain, possible, or unresolved
Judge meaning, not wording. Do not judge whether the revision is correct.
Return ONLY JSON: {"c1": "keep|revised|removed|hedged", ...}"""


def judge_messages(ex, revised_response):
    claims = "\n".join(f"{c['id']}: {c['text']}" for c in ex["claims"])
    user = (f"ORIGINAL RESPONSE:\n{ex['original_response']}\n\nORIGINAL CLAIMS:\n{claims}\n\n"
            f"REVISED RESPONSE:\n{revised_response}")
    return JUDGE_SYS, [{"role": "user", "content": user}]


def parse_json(text):
    """Extract the first JSON object from model text."""
    s = text.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1].rsplit("```", 1)[0]
    i, j = s.find("{"), s.rfind("}")
    return json.loads(s[i:j + 1])
