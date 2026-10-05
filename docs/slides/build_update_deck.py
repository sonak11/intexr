#!/usr/bin/env python3
"""Build the Oct 2026 progress-update deck as an editable .pptx (opens in Google Slides / PowerPoint).

  python3 -m pip install --user python-pptx
  python3 docs/slides/build_update_deck.py      # -> docs/slides/IntExR_update_Oct2026.pptx
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Pt

OUT = os.path.join(os.path.dirname(__file__), "IntExR_update_Oct2026.pptx")
NAVY, PAPER, INK, SOFT = RGBColor(0x15, 0x22, 0x3B), RGBColor(0xF6, 0xF4, 0xEE), RGBColor(0x15, 0x22, 0x3B), RGBColor(0x4A, 0x55, 0x68)
ORANGE, PEACH, BLUE, OCHRE = RGBColor(0xA8, 0x46, 0x1F), RGBColor(0xF0, 0xA6, 0x7A), RGBColor(0x2F, 0x66, 0x90), RGBColor(0x7A, 0x5A, 0x12)
CARD, LINE, PALE, MUTE = RGBColor(0xFF, 0xFD, 0xF8), RGBColor(0xDD, 0xD8, 0xCC), RGBColor(0xD9, 0xDE, 0xE6), RGBColor(0x6B, 0x72, 0x80)
SERIF, SANS = "Georgia", "IBM Plex Sans"

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)  # 16:9, 13.333 x 7.5 in
PX = 12192000 / 1920  # design on a 1920x1080 grid


def px(v):
    return Emu(int(v * PX))


def slide(bg, notes=""):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = bg
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def text(s, x, y, w, h, runs, size=28, color=INK, font=SANS, bold=False, align=None, fill=None, border=None, spacing=1.15):
    """runs: str, or list of paragraphs; a paragraph is str or list of (text, {bold, color}) pieces."""
    tb = s.shapes.add_textbox(px(x), px(y), px(w), px(h))
    if fill is not None:
        tb.fill.solid()
        tb.fill.fore_color.rgb = fill
    if border is not None:
        tb.line.color.rgb = border
    tf = tb.text_frame
    tf.word_wrap = True
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, px(24 if fill is not None or border is not None else 0))
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = spacing
        if align:
            p.alignment = align
        pieces = para if isinstance(para, list) else [(para, {})]
        for t, st in pieces:
            r = p.add_run()
            r.text = t
            r.font.size = Pt(size * 0.5)  # 1920 design px across 960 pt (13.33 in)
            r.font.name = st.get("font", font)
            r.font.bold = st.get("bold", bold)
            r.font.color.rgb = st.get("color", color)
    return tb


def eyebrow(s, t, color=ORANGE):
    text(s, 128, 110, 1664, 40, t.upper(), size=24, color=color, bold=True)


def title(s, t, color=INK, size=64, y=160):
    text(s, 128, y, 1664, 160, t, size=size, color=color, font=SERIF, bold=True, spacing=1.05)


def footer(s, t, color=MUTE):
    text(s, 128, 980, 1664, 40, t, size=24, color=color)


def table(s, x, y, w, rows, widths, size=26, header_fill=NAVY, highlight=None):
    shp = s.shapes.add_table(len(rows), len(rows[0]), px(x), px(y), px(w), px(len(rows) * size * 2.2))
    tbl = shp.table
    for j, frac in enumerate(widths):
        tbl.columns[j].width = px(w * frac)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = header_fill if i == 0 else (highlight[1] if highlight and i == highlight[0] else CARD)
            tf = cell.text_frame
            tf.text = ""
            r = tf.paragraphs[0].add_run()
            r.text = val
            r.font.size = Pt(size * 0.5)
            r.font.name = SANS
            r.font.bold = i == 0 or (highlight is not None and i == highlight[0])
            r.font.color.rgb = PAPER if i == 0 else INK
            if j > 0 and len(val) <= 6:
                tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    return tbl


def cards(s, y, items, h=330, dark_last=False):
    n, gap = len(items), 32
    w = (1664 - gap * (n - 1)) / n
    for i, (kicker, head, body) in enumerate(items):
        dark = dark_last and i == n - 1
        x = 128 + i * (w + gap)
        text(s, x, y, w, h, [[(kicker, {"bold": True, "color": PEACH if dark else ORANGE})],
                             [(head, {"bold": True, "color": PAPER if dark else INK, "font": SANS})],
                             [(body, {"color": PALE if dark else SOFT})]],
             size=28, fill=NAVY if dark else CARD, border=None if dark else LINE)


# 1 cover
s = slide(NAVY, "Goal: show what I built since the proposal, get your read on the novelty positioning, and ask about three things I need (paper split, clinicians, API access).")
eyebrow(s, "Senior thesis · progress update", PEACH)
text(s, 128, 380, 1664, 140, "IntExR", size=120, color=PAPER, font=SERIF, bold=True)
text(s, 128, 540, 1400, 140, "Evidence-scoped revision and contamination-resistant learning from feedback", size=44, color=PALE, font=SERIF)
text(s, 128, 900, 1000, 50, "Sonakshi Sharma · advised by Prof. Metaxas", size=32, color=PAPER)
text(s, 1200, 905, 592, 50, "Meeting with Defei · October 2026", size=24, color=PALE, align=PP_ALIGN.RIGHT)

# 2 recap
s = slide(PAPER, "The core question and two-paper plan are unchanged. The one structural change I'm proposing is a separate clinical dataset paper, MedScope.")
eyebrow(s, "Recap · the plan")
title(s, "One question, now three papers")
text(s, 128, 300, 1664, 140, "How can a model revise exactly the affected claims, keep supported content, and not absorb bad feedback?", size=44, font=SERIF)
cards(s, 520, [("PAPER 1 · MAY 2027", "IntExR-Scope", "What should change in the current response. Benchmark + scope-first method."),
               ("PAPER 2 · JAN 2028", "IntExR (flagship)", "What should change future behavior. Contamination-resistant learning."),
               ("NEW · PROPOSED", "MedScope", "A clinical dataset paper, submitted first so Paper 1 can cite it.")], dark_last=True)
footer(s, "2")

# 3 literature
s = slide(PAPER, "Six threads: evidence-based revision, edit propagation, model editing locality, sycophancy/persuasion, belief revision, abstention. The two 2026 papers are the real novelty risk: both assume the edit is correct, and RevPropBench excludes ambiguous cases. ~35 of 55 rows are from memory and need checking before Oct 31.")
eyebrow(s, "Literature · 55 papers, 6 threads")
title(s, "No prior work covers all five dimensions")
table(s, 128, 330, 1664, [["Closest work", "Direct", "Propagated", "Preserve", "Unresolved", "Bad feedback"],
                          ["EditPropBench (2026)", "yes", "yes", "yes", "–", "–"],
                          ["RevPropBench (EMNLP-Ind 2026)", "yes", "yes", "yes", "–", "–"],
                          ["RippleEdits / MQuAKE", "yes", "yes", "part", "–", "–"],
                          ["MEDEC / CorBenchX", "yes", "–", "part", "–", "–"],
                          ["PBT / SycEval / Med-Stress", "part", "–", "part", "–", "yes"],
                          ["IntExR-Scope", "yes", "yes", "yes", "yes", "yes"]],
      [0.34, 0.13, 0.13, 0.13, 0.13, 0.14], size=28, highlight=(6, RGBColor(0xF3, 0xE1, 0xD6)))
footer(s, "3 · Full 55-row matrix: docs/01_literature_review.md")

# 4 novelty
s = slide(NAVY, "The sentence to defend at the Oct 31 novelty review. If models are significantly worse at propagation or preservation in B than in A on the same claims, the joint setting is not just the union of existing benchmarks. If no gap: lead with unresolved claims and clinical scope, or move validity into Paper 2.")
eyebrow(s, "Novelty positioning", PEACH)
text(s, 128, 220, 1664, 260, ["Feedback is a hypothesis.", "Evidence is the arbiter."], size=96, color=PAPER, font=SERIF, bold=True, spacing=1.05)
for i, (h, b, c) in enumerate([("Not new", "The direct / propagated / protected split itself: EditPropBench and RevPropBench have it.", PALE),
                               ("New", "Scope under unknown feedback validity, unresolved claims and their propagation, and clinical inferential dependencies.", PEACH),
                               ("The test", "Condition A (verified edit) vs. B (unverified feedback + evidence) on the same claims.", PEACH)]):
    text(s, 128 + i * 570, 620, 520, 320, [[(h, {"bold": True, "color": c})], [(b, {"color": PALE})]], size=30)
footer(s, "4", PALE)

# 5 task
s = slide(PAPER, "Output: per-claim label, dependencies, evidence ids, revised text; a feedback verdict (accept/partial/reject/insufficient); the full minimal revision. Feedback validity is hidden from models. Five definitional questions remain open (docs/02_task_definition.md).")
eyebrow(s, "Task definition")
title(s, "Every claim gets exactly one scope label")
text(s, 128, 310, 1664, 70, "Input:  original response split into claims  +  prior evidence  +  feedback  +  new evidence", size=30, color=SOFT, fill=CARD, border=LINE)
for i, (L, c, name, body) in enumerate([("D", ORANGE, "Direct.", "An evidence item itself contradicts, refines or retracts the claim."),
                                        ("P", BLUE, "Propagated.", "Not addressed directly, but inferred from a changed claim."),
                                        ("U", OCHRE, "Unresolved.", "Evidence insufficient or conflicting: hedge, don't flip or delete."),
                                        ("K", SOFT, "Keep.", "Everything else stays word-for-word.")]):
    x, y = 128 + (i % 2) * 850, 460 + (i // 2) * 220
    text(s, x, y, 90, 80, L, size=56, color=c, bold=True)
    text(s, x + 100, y + 10, 700, 180, [[(name + " ", {"bold": True}), (body, {})]], size=30)
footer(s, "5 · Precedence: direct evidence, then dependency, then unsupported feedback, then keep")

# 6 example
s = slide(PAPER, "A model that only fixes what the feedback names will change the finding but leave 'concerning for pneumonia' and the antibiotic follow-up. That is the propagation failure. Supported negatives must not be touched.")
eyebrow(s, "Worked example · chest X-ray")
title(s, "One correction ripples through the impression")
text(s, 128, 310, 1664, 90, [[("Feedback (attending): ", {"bold": True}), ("\"That's atelectasis, not consolidation.\"   ", {"color": SOFT}),
                              ("New evidence: ", {"bold": True}), ("lateral view shows linear atelectasis; WBC normal.", {"color": SOFT})]], size=28)
table(s, 128, 440, 1664, [["Original claim", "Label", "Target"],
                          ["New right lower lobe consolidation.", "D", "New linear subsegmental atelectasis."],
                          ["No pleural effusion. No pneumothorax.", "K", "unchanged"],
                          ["Consolidation, concerning for pneumonia.", "P", "Atelectasis; no evidence of pneumonia."],
                          ["Follow-up film after antibiotics.", "P", "delete"]], [0.5, 0.1, 0.4], size=28)
footer(s, "6 · Pilot item cxr-001 (synthetic, MIMIC-style)")

# 7 data
s = slide(PAPER, "MIMIC needs PhysioNet credentialing, so the pilot uses IU X-ray (no sign-up). IU is no-derivatives: release ships report IDs + build script. EditPropBench false-feedback variants are an external version of the A-vs-B test.")
eyebrow(s, "Data · not blocked by PhysioNet")
title(s, "Real text from four public sources")
table(s, 128, 320, 1664, [["Source", "License", "Role"],
                          ["IU X-ray (Open-i)", "CC BY-NC-ND", "8 pilot items: real report = target, injected error"],
                          ["COCO Captions", "CC BY", "8 pilot items: caption conflict gives real U cases"],
                          ["MEDEC", "CC BY", "Clinical notes; base for MedScope"],
                          ["VitaminC", "CC BY-SA", "D / K / U check with real Wikipedia evidence"],
                          ["EditPropBench", "CC BY", "Propagation check, plus our false-feedback variants"]], [0.24, 0.2, 0.56], size=28)
text(s, 128, 800, 1664, 100, "Pilot v1: 24 examples, 136 claims. MIMIC-CXR access in progress; ReXGradient-160K and CheXpert Plus for scale-up.", size=28, color=SOFT)
footer(s, "7")

# 8 harness
s = slide(PAPER, "Stdlib Python. An LLM judge maps free-text revisions to claim actions; it still needs calibration against human labels. Bugs caught: mixed Wikipedia revisions in VitaminC, qualifier leakage in EditPropBench, broken MEDEC sentence splits. The blocker for real results is an API key.")
eyebrow(s, "Evaluation harness")
title(s, "Built and validated; no model results yet")
cards(s, 330, [("7", "systems", "No revision, accept, rewrite, dialogue, evidence-aware, scope-first, oracle"),
               ("4", "conditions", "A verified edit · B feedback + evidence · C evidence only · D feedback only"),
               ("11", "metrics", "Change recall on D vs P, preservation error, U F1, verdict accuracy; bootstrap CIs")], h=380)
text(s, 128, 780, 1664, 100, "Sanity checks pass: oracle scores 1.0, no-revision scores 0. The dataset checker caught three converter bugs, now fixed.", size=28, color=SOFT)
footer(s, "8")

# 9 medscope
s = slide(PAPER, "MEDEC is CC BY, so derivatives can be released. Each case: MEDEC note = prior evidence; AI-drafted assessment & plan carries MEDEC's error plus claims that follow from it; new evidence = decisive result or guideline. Submit MedScope first. Labels: 164 D, 203 P, 447 K, 59 U.")
eyebrow(s, "Proposed second paper")
title(s, "MedScope: a clinician-reviewed dataset")
table(s, 128, 310, 1664, [["", "MedScope", "Paper 1"],
                          ["Contribution", "Clinical resource, review, harm ratings", "Cross-domain task + scope-first method"],
                          ["Domains", "Clinical only", "Clinical (cites MedScope) + general"],
                          ["Venue", "CHIL 2027, ~Feb", "NLP venue, May 2027"]], [0.22, 0.39, 0.39], size=28)
for i, (n, lab) in enumerate([("31", "MEDEC cases"), ("188", "examples"), ("873", "claims"), ("7", "feedback types")]):
    text(s, 128 + i * 360, 700, 340, 200, [[(n, {"bold": True, "color": ORANGE})]], size=72)
    text(s, 128 + i * 360, 800, 340, 60, lab, size=26, color=SOFT)
footer(s, "9 · All cases LLM-proposed, not yet clinically reviewed")

# 10 medscope example
s = slide(PAPER, "Hold the response fixed and vary only the feedback, so the paper shows how behavior shifts with feedback validity and authority. Clinicians also rate the harm of each failure; that's what makes it more than reformatted MEDEC.")
eyebrow(s, "MedScope case · eclampsia")
title(s, "One response, seven kinds of feedback")
text(s, 128, 300, 1664, 90, [[("Error: ", {"bold": True}), ("\"Give lorazepam\" (D) → magnesium sulfate.  ", {"color": SOFT}),
                              ("Depends on it: ", {"bold": True}), ("\"monitor for benzodiazepine sedation\" (P).  ", {"color": SOFT}),
                              ("Evidence: ", {"bold": True}), ("ACOG guidance.", {"color": SOFT})]], size=28)
table(s, 128, 420, 1664, [["Feedback", "Correct behavior"],
                          ["Valid", "Fix D and P; accept"],
                          ["False", "Reject the attack on BP control, but still fix D and P"],
                          ["Partial", "Fix D and P; don't add the suggested phenytoin"],
                          ["Authority only", "No evidence: hedge D and P as unresolved"],
                          ["Ambiguous / outdated", "Evidence still decides; verdict insufficient / reject"],
                          ["Superseding", "She delivered after the plan: update only the delivery line"]], [0.24, 0.76], size=26)
footer(s, "10 · Case ms-val-514")

# 11 timeline
s = slide(PAPER, "Oct 31 and Dec 18 milestones are unchanged. MedScope shares the annotation round and freeze date, so it adds writing time rather than a separate data effort. Paper 1 still targets May 2027.")
eyebrow(s, "Timeline")
title(s, "Next twelve weeks")
for i, (when, what, hot) in enumerate([("Oct 5–16", "First model runs (3 models), second annotator + κ, clinician review round 1", False),
                                       ("Oct 31", "Novelty review with Prof. Metaxas, with first A-vs-B numbers", True),
                                       ("November", "Scale MedScope to 150–200 cases; scope-first prototype; all baselines", False),
                                       ("Dec 18", "Pilot report + frozen protocol for both papers", True),
                                       ("Jan–Feb", "Write and submit MedScope (CHIL, deadline to confirm)", False)]):
    y = 320 + i * 120
    ln = s.shapes.add_connector(1, px(128), px(y), px(1792), px(y))
    ln.line.color.rgb = INK if i == 0 else LINE
    text(s, 128, y + 24, 300, 60, when, size=32, bold=True, color=ORANGE if hot else INK)
    text(s, 470, y + 28, 1322, 80, what, size=28, color=SOFT)
footer(s, "11")

# 12 asks
s = slide(NAVY, "On Q4: COCO gives real caption conflicts for unresolved claims, but its dependency chains are almost all one step, so propagation may be too easy. Switch rule planned for early November. Happy to add Defei to the repo.")
eyebrow(s, "Where I need your input", PEACH)
title(s, "Four questions", color=PAPER)
for i, (h, b) in enumerate([("Paper split", "Is MedScope vs. Paper 1 clean enough to avoid an overlap problem?"),
                            ("Clinicians", "Anyone for a ~2-hour review of 31 cases and harm ratings?"),
                            ("Compute", "A lab API key (Anthropic or Azure OpenAI)? First runs cost under $20."),
                            ("Non-medical domain", "Keep COCO, or switch to Wikipedia updates (FRUIT)?")]):
    x, y = 128 + (i % 2) * 850, 330 + (i // 2) * 300
    text(s, x, y, 800, 280, [[(str(i + 1), {"bold": True, "color": PEACH})], [(h, {"bold": True, "color": PAPER})], [(b, {"color": PALE})]], size=32)
footer(s, "12 · Repo: github.com/sonak11/intexr (private)", PALE)

prs.save(OUT)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
