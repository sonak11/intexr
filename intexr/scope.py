"""Scope-first revision pipeline (the Paper 1 method).

The single-prompt `scope_first` system asks one LLM call to do everything. This pipeline splits the
task so that the parts with a right answer by rule are done by code, and the LLM only does what needs
language understanding:

  1. ALIGN    (LLM)   per claim: which evidence items support / contradict it, or leave it uncertain;
                      which claims it was inferred from; which claims the feedback disputes; verdict.
  2. LABEL    (code)  the annotation guide's precedence, applied deterministically:
                      direct evidence > dependency > unsupported feedback > keep.
  3. REVISE   (LLM)   write text only for D / U claims, and decide for each descendant of a changed
                      claim whether it still holds (-> K) or must change (-> P).
  4. ASSEMBLE (code)  splice revised claims into the original response. K claims are copied verbatim,
                      so preservation of kept claims holds by construction.
  5. CHECK    (code)  terms that appear only in the feedback (in no evidence, not in the original) must
                      not enter the revision; offending claims are re-revised once.

Ablation flags (system names in SYSTEMS): `scope_pipeline_noprop` skips the propagation check in step 3
(every descendant of a changed claim is kept), `scope_pipeline_nocheck` skips step 5.
Under condition A the verified edits are treated as an evidence item (they are verified by definition).
"""
import re

from . import prompts
from .data import model_view

RELATIONS = ("supports", "contradicts", "uncertain")

_STOP = set("""a an the is are was were be been being of in on at to for and or but not no nor it its this that these those
with as by from he she they his her their them there here i you we our your me my do does did done have has had so very
just also only about actually really definitely please some any one side wrong right sure if then than when what which
who why how should would could can will may might must don't doesn't isn't it's that's i'm you're he's she's let's
think look looks like really yes okay ok make sure use give start stop keep add plus too well thing things""".split())


def content_words(text):
    return {w for w in re.findall(r"[a-z][a-z\-]+", text.lower()) if w not in _STOP and len(w) > 3}


# ---------------------------------------------------------------- prompts
ALIGN_SYS = """You audit a previous response against evidence before anything is revised. Do not revise anything.

Feedback is a hypothesis from a person; it is NOT evidence unless it is a verified correction. Evidence items have ids.

For EVERY numbered claim report:
- "evidence": the evidence items that speak to the claim itself, each with a relation:
    "supports"     the item states or directly confirms what the claim says
    "contradicts"  the item shows the claim is false, must be made more specific in a way that changes what
                   follows from it, or makes a forward-looking claim (plan, recommendation, status) moot
    "uncertain"    the item says the matter cannot be determined, is equivocal, or is pending
  Leave the list empty when no item addresses the claim directly. A claim is not contradicted just because a
  claim it was inferred from is wrong; that is a dependency, not evidence.
- "depends_on": the ids of earlier claims this claim was inferred from (finding -> diagnosis -> plan). Two claims
  that merely share a topic are not dependent.

Then for the feedback:
- "disputes": the claim ids the feedback says are wrong or questions.
- "verdict": accept (everything it asserts is supported by the evidence), partial (some supported, some unsupported
  or contradicted), reject (contradicted by evidence, or about something other than what the response describes),
  insufficient (too vague to evaluate, or no evidence decides it).

Return ONLY JSON:
{"claims": [{"id": "c1", "evidence": [{"id": "n1", "relation": "supports|contradicts|uncertain"}], "depends_on": []}],
 "feedback": {"disputes": [], "verdict": "accept|partial|reject|insufficient", "rationale": "..."}}"""

REVISE_SYS = """You make a minimal, evidence-scoped revision of specific claims. Other claims are fixed and are shown only
for context. Use only the evidence; never add a fact that appears only in the feedback.

Tasks, by claim:
- UPDATE: the evidence contradicts this claim. Rewrite it so it agrees with the evidence, changing as little as
  possible, or return null to delete it if nothing of it survives.
- HEDGE: the evidence does not settle this claim. Keep the claim but state the uncertainty and what would resolve it.
  Do not delete it and do not assert the opposite.
- CHECK: this claim was inferred from a claim that is changing. If it still holds after that change, return
  "UNCHANGED". If it no longer holds or no longer follows, rewrite it to follow from the changed claim, or return
  null to delete it.

Return ONLY JSON mapping claim id to the new text, null, or "UNCHANGED", e.g. {"c2": "...", "c4": null, "c5": "UNCHANGED"}"""


def _claims_block(claims):
    return "\n".join(f"{c['id']}: {c['text']}" for c in claims)


def align_messages(v, evidence):
    user = (f"TASK: {v['context']}\n\nEVIDENCE:\n{prompts._evidence_block(evidence)}\n\n"
            f"ORIGINAL RESPONSE:\n{v['original_response']}\n\nCLAIMS:\n{_claims_block(v['claims'])}\n\n"
            f"FEEDBACK:\n{prompts._feedback_block(v['feedback'])}")
    return ALIGN_SYS, [{"role": "user", "content": user}]


def revise_messages(v, evidence, jobs, texts, extra=""):
    """jobs: list of (cid, kind, note) with kind in UPDATE / HEDGE / CHECK, in dependency order."""
    by_id = {c["id"]: c["text"] for c in v["claims"]}
    lines = []
    for cid, kind, note in jobs:
        lines.append(f"{cid} [{kind}] {by_id[cid]}" + (f"\n    ({note})" if note else ""))
    fixed = [c for c in v["claims"] if c["id"] not in {j[0] for j in jobs}]
    user = (f"TASK: {v['context']}\n\nEVIDENCE:\n{prompts._evidence_block(evidence)}\n\n"
            f"FEEDBACK (unverified):\n{prompts._feedback_block(v['feedback'])}\n\n"
            f"FIXED CLAIMS (context only):\n{_claims_block(fixed) or '(none)'}\n\n"
            f"CLAIMS TO HANDLE:\n" + "\n".join(lines) + (f"\n\n{extra}" if extra else ""))
    return REVISE_SYS, [{"role": "user", "content": user}]


# ---------------------------------------------------------------- deterministic steps
def evidence_for(v):
    """Evidence the pipeline may rely on. Verified edits (condition A) count as evidence; feedback never does."""
    ev = list(v["prior_evidence"]) + list(v["new_evidence"])
    fb = v.get("feedback")
    if fb and fb.get("speaker_role") == "verified_editor":
        ev.append({"id": "v1", "text": fb["text"], "provenance": "verified_edit"})
    return ev


def direct_status(rels, tier):
    """Collapse one claim's evidence relations to D / U / K-supported / None.

    Newer evidence overrides older (prior < new). Within the newest tier that speaks to the claim,
    disagreement or an explicit 'uncertain' makes the claim unresolved.
    """
    rels = [(r["id"], r["relation"]) for r in rels if r.get("relation") in RELATIONS and r.get("id") in tier]
    if not rels:
        return None
    top = max(tier[i] for i, _ in rels)
    kinds = {rel for i, rel in rels if tier[i] == top}
    if "uncertain" in kinds or kinds == {"supports", "contradicts"}:
        return "U"
    return "D" if "contradicts" in kinds else "S"


def topo_order(cids, parents):
    seen, order = set(), []

    def visit(c, stack=()):
        if c in seen or c in stack:
            return
        for p in parents.get(c, []):
            visit(p, stack + (c,))
        seen.add(c)
        order.append(c)
    for c in cids:
        visit(c)
    return order


def assign_labels(v, align):
    """Apply the guide's precedence to the alignment. Returns (labels, triggers, parents, candidates) where
    candidates are claims that may be P: they await the propagation check in REVISE."""
    cids = [c["id"] for c in v["claims"]]
    by = {c.get("id"): c for c in align.get("claims", []) if isinstance(c, dict)}
    ev = evidence_for(v)
    tier = {e["id"]: (0 if e in v["prior_evidence"] else 1) for e in ev}
    parents = {c: [p for p in (by.get(c, {}).get("depends_on") or []) if p in cids and p != c] for c in cids}
    fb = v.get("feedback") or {}
    # a verified edit (condition A) is evidence, not a dispute
    disputes = set((align.get("feedback") or {}).get("disputes") or []) \
        if fb and fb.get("speaker_role") != "verified_editor" else set()
    labels, triggers = {}, {}
    for c in topo_order(cids, parents):
        d = direct_status(by.get(c, {}).get("evidence") or [], tier)
        if d in ("D", "U"):
            labels[c], triggers[c] = d, "evidence"
        elif d == "S":
            labels[c], triggers[c] = "K", "supported"
        elif any(labels.get(p) in ("D", "P?") for p in parents[c]):
            labels[c], triggers[c] = "P?", "dependency"
        elif any(labels.get(p) == "U" for p in parents[c]):
            labels[c], triggers[c] = "U", "dependency"
        elif c in disputes:
            labels[c], triggers[c] = "U", "feedback"
        else:
            labels[c], triggers[c] = "K", "unverified"
    return labels, triggers, parents


def assemble(original, claims, new_text):
    """Splice revised claim texts into the original response. new_text[cid]: str, None (delete), or absent (keep)."""
    spans = []
    pos = 0
    for c in claims:
        i = original.find(c["text"], pos)
        if i < 0:
            i = original.find(c["text"])
        spans.append((i, i + len(c["text"]), c["id"]))
        pos = max(pos, i + len(c["text"]))
    out = original
    for i, j, cid in sorted(spans, reverse=True):
        if i < 0 or cid not in new_text:
            continue
        t = new_text[cid]
        if t is None:  # delete the span and the whitespace that follows it
            k = j
            while k < len(out) and out[k] in " \t":
                k += 1
            out = out[:i] + out[k:]
        else:
            out = out[:i] + t + out[j:]
    return re.sub(r"[ \t]{2,}", " ", out).strip()


def feedback_only_terms(v):
    """Content words the feedback introduces that no evidence item, the context, or the original contains."""
    fb = v.get("feedback")
    if not fb or fb.get("speaker_role") == "verified_editor":
        return set()
    known = content_words(v["context"] + " " + v["original_response"] + " " +
                          " ".join(e["text"] for e in v["prior_evidence"] + v["new_evidence"]))
    return {w for w in content_words(fb["text"]) if w not in known and w.rstrip("s") not in known}


# ---------------------------------------------------------------- the system
def _status(label, text):
    if label == "K":
        return "keep"
    if label == "U":
        return "hedged"
    return "removed" if text is None else "revised"


def _texts(raw):
    out = prompts.parse_json(raw)
    return {k: v for k, v in out.items() if isinstance(k, str)}


def decide_verdict(v, align, final, leaks):
    """Feedback verdict by rule, from what the feedback disputes and how the evidence labelled those claims.
    Falls back to the model's verdict when the feedback disputes no claim (vague or defending a claim).
    Known limit: feedback that is right about the error but adds an unsupported intervention gets 'accept'."""
    fb = v.get("feedback")
    if not fb:
        return None
    llm = (align.get("feedback") or {}).get("verdict")
    if fb.get("speaker_role") == "verified_editor":
        return llm
    disputes = [c for c in ((align.get("feedback") or {}).get("disputes") or []) if c in final]
    if not disputes:
        return llm if llm in ("accept", "partial", "reject", "insufficient") else "insufficient"
    labs = {final[c]["label"] for c in disputes}
    # `leaks` (feedback-only words) is too noisy to signal unsupported additions: ordinary words in valid feedback
    # trip it (dev pilot, 26 Oct). Unsupported additions are scored by the forbidden-addition metric instead, so
    # 'partial' here comes only from feedback whose disputed claims are partly overturned and partly kept.
    if labs <= {"D", "P"}:
        return "accept"
    if labs == {"K"}:
        return "reject"
    if "U" in labs and not labs & {"D", "P"}:
        return "insufficient"
    return "partial"


def run(ex, client, judge=None, condition="B", propagate=True, check=True, check_scope="after", rule_verdict=True,
        name="scope_pipeline", **_):
    """check_scope: 'deps' checks only claims the model linked to a changed claim; 'after' also checks every later
    claim that has no direct evidence (models often omit dependency links). rule_verdict: decide the verdict by
    decide_verdict instead of taking the model's."""
    v = model_view(ex, condition)
    ev = evidence_for(v)
    cids = [c["id"] for c in v["claims"]]
    by_text = {c["id"]: c["text"] for c in v["claims"]}
    errors = []
    sys_, msgs = align_messages(v, ev)
    raw_align = client(sys_, msgs)
    try:
        align = prompts.parse_json(raw_align)
        if not isinstance(align, dict):
            raise ValueError("align output is not a JSON object")
    except ValueError as e:
        errors.append(f"align: {e}")
        align = {"claims": [], "feedback": {}}
    labels, triggers, parents = assign_labels(v, align)
    if not propagate:
        labels = {c: ("K" if l == "P?" else l) for c, l in labels.items()}
    elif check_scope == "after":
        changed_at = [i for i, c in enumerate(cids) if labels[c] in ("D", "P?")]
        if changed_at:
            for c in cids[changed_at[0] + 1:]:
                if labels[c] == "K" and triggers[c] == "unverified":
                    labels[c], triggers[c] = "P?", "dependency"
                    parents[c] = parents[c] or [cids[changed_at[0]]]

    order = topo_order(cids, parents)
    jobs = []
    for c in order:
        if labels[c] == "D":
            jobs.append((c, "UPDATE", None))
        elif labels[c] == "U":
            note = {"evidence": "the evidence items conflict or are inconclusive about it",
                    "dependency": "it was inferred from an unresolved claim: " + ", ".join(
                        p for p in parents[c] if labels.get(p) == "U"),
                    "feedback": "the feedback disputes it, but no evidence decides it"}[triggers[c]]
            jobs.append((c, "HEDGE", note))
        elif labels[c] == "P?":
            jobs.append((c, "CHECK", "inferred from " + ", ".join(p for p in parents[c] if labels.get(p) in ("D", "P?"))))
    new_text = {}
    if jobs:
        sys_, msgs = revise_messages(v, ev, jobs, new_text)
        raw_rev = client(sys_, msgs)
        try:
            new_text = _texts(raw_rev)
        except (ValueError, AttributeError) as e:
            errors.append(f"revise: {e}")
    final = {}
    for c in cids:
        lab = labels[c]
        t = new_text.get(c, "UNCHANGED") if lab != "K" else "UNCHANGED"
        if lab == "P?":
            lab = "K" if (t == "UNCHANGED" or t == by_text[c]) else "P"
        elif lab in ("D", "U") and (t == "UNCHANGED" or (lab == "U" and t is None)):
            t = by_text[c]  # the model refused to change it; keep the text, keep the label (scored as such)
        if lab == "K":
            final[c] = {"label": "K", "status": "keep"}
        else:
            final[c] = {"label": lab, "revised_text": t, "status": _status(lab, t)}
    # CHECK: feedback-only content must not leak into revised claims
    leaks = feedback_only_terms(v) if check else set()
    bad = [c for c in cids if final[c]["label"] != "K" and final[c].get("revised_text")
           and content_words(final[c]["revised_text"]) & leaks]
    if bad:
        redo = [j for j in jobs if j[0] in bad]
        extra = ("Your previous answer added content that only the feedback asserts (" + ", ".join(sorted(leaks)) +
                 "). No evidence supports it. Do not include it.")
        sys_, msgs = revise_messages(v, ev, redo, new_text, extra)
        raw_again = client(sys_, msgs)
        try:
            again = _texts(raw_again)
            for c in bad:
                if c in again and again[c] != "UNCHANGED":
                    final[c]["revised_text"] = again[c]
                    final[c]["status"] = _status(final[c]["label"], again[c])
        except (ValueError, AttributeError) as e:
            errors.append(f"check: {e}")
    revised = assemble(v["original_response"], v["claims"],
                       {c: f["revised_text"] for c, f in final.items() if f["label"] != "K"})
    pred = {"id": ex["id"], "system": name, "structured": True,
            "verdict": decide_verdict(v, align, final, leaks) if rule_verdict else
                       ((align.get("feedback") or {}).get("verdict") if v.get("feedback") else "insufficient"),
            "revised_response": revised, "claims": final,
            "trace": {"labels_pre": labels, "triggers": triggers, "parents": parents, "leaks": sorted(leaks),
                      "rechecked": bad, "disputes": (align.get("feedback") or {}).get("disputes"),
                      "llm_verdict": (align.get("feedback") or {}).get("verdict")}}
    if v.get("feedback") is None:
        pred["verdict"] = None  # condition C has no feedback to judge
    if errors:
        pred["errors"] = errors
    if judge is not None:
        from .systems import _judge_statuses
        pred["judged_claims"] = _judge_statuses(ex, revised, judge)
    return pred
