#!/usr/bin/env python3
"""Word version of the blind annotation page (same 24 items, same order, same neutral ids as the HTML).

  python3 scripts/make_annotation_docx.py make                       # -> annotation/intexr_annotation.docx
  python3 scripts/make_annotation_docx.py to-csv returned.docx       # -> returned.csv, for annotation_tools.py agree
  python3 scripts/annotation_tools.py agree returned.csv --gold paperB/data/medec_scope_v0.json \
      --key annotation/medscope_annotate_key.json

Needs python-docx (python3 -m pip install --user python-docx).
"""
import argparse
import csv
import json
import os
import re
import sys

from docx import Document
from docx.shared import Pt, RGBColor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from intexr import data  # noqa: E402
from make_annotation_html import blind, sample  # noqa: E402

INSTRUCTIONS = [
    "Each example shows an AI-drafted assessment and plan, split into claims c1, c2, …, plus evidence (e* = the clinical note; "
    "n* = new results or guidelines) and feedback from a clinician. Feedback is a claim by a person, not evidence. "
    "Read all evidence first, then the feedback. For each claim, apply these steps in order:",
    "1. Does a single evidence item contradict the claim, refine it in a way that changes what follows from it, or make a "
    "plan/recommendation moot? → D (direct update). Do evidence items conflict about it, or say it cannot be determined? → U. "
    "Does evidence support it? → go to step 4.",
    "2. No evidence speaks to it, but it was inferred from a claim you labelled D or P and no longer holds? → P (propagated). "
    "Still holds? → K.",
    "3. Inferred from a claim you labelled U? → U.",
    "4. The feedback disputes it and no evidence settles it either way? → U. Otherwise → K (keep).",
    "Also: a D label needs an evidence item, not just your own medical knowledge (you may use knowledge to decide whether a "
    "dependent claim still holds). If two evidence items disagree about a claim, label it U. If something happened after the "
    "response was written, forward-looking claims that no longer fit are D, and descriptions of the earlier state stay K. "
    "If the feedback adds a treatment no evidence supports, don't create a claim for it; just mention it in notes.",
    "Depends on: write the claims this claim was inferred from, e.g. c2;c3 (diagnosis → treatment → monitoring). "
    "Sharing a topic is not enough. Leave blank if none.",
    "Feedback verdict (once per example): accept = everything it asserts is supported by the evidence; partial = some supported, "
    "some not; reject = contradicted, or about something the response does not describe; insufficient = too vague to evaluate, "
    "or no evidence decides it. Generic vague feedback (\"something seems off\") is insufficient even if the evidence settles "
    "the claims.",
    "Type your answers into the grey columns. Please don't look up the source dataset or discuss items with the other annotator "
    "until you're done. Notes on anything hard or ambiguous are very useful.",
]


def make(args):
    exs = sample(data.load(args.data), args.seed)
    key = {f"item-{i + 1:02d}": ex["id"] for i, ex in enumerate(exs)}
    existing = os.path.splitext(args.html)[0] + "_key.json"
    if os.path.exists(existing) and json.load(open(existing)) != key:
        sys.exit(f"sample differs from {existing}; regenerate both with the same --seed")
    d = Document()
    d.styles["Normal"].font.name = "Calibri"
    d.styles["Normal"].font.size = Pt(10.5)
    d.add_heading("IntExR claim-labelling task", 0)
    d.add_paragraph(f"{len(exs)} examples, about 4 minutes each. Annotator initials: ________")
    d.add_heading("Instructions (read once)", 1)
    for p in INSTRUCTIONS:
        d.add_paragraph(p)
    for i, (iid, ex) in enumerate(zip(key, exs)):
        v = blind(data.model_view(ex, "B"))
        d.add_page_break()
        d.add_heading(f"Example {i + 1} of {len(exs)}  [{iid}]", 1)
        r = d.add_paragraph().add_run(v["context"])
        r.italic = True
        d.add_paragraph().add_run("Evidence").bold = True
        for e in v["prior_evidence"] + v["new_evidence"]:
            p = d.add_paragraph(style="List Bullet")
            p.add_run(f"[{e['id']}] ").bold = True
            p.add_run(f"({e.get('provenance', '')}) ").font.color.rgb = RGBColor(0x66, 0x66, 0x66)
            p.add_run(e["text"])
        p = d.add_paragraph()
        p.add_run("Feedback ").bold = True
        p.add_run(f"from {v['feedback']['speaker_role'].replace('_', ' ')}: “{v['feedback']['text']}”")
        t = d.add_table(rows=1, cols=4)
        t.style = "Table Grid"
        for c, h in zip(t.rows[0].cells, [iid, "claim", "label (D/P/K/U)", "depends on (e.g. c1;c2)"]):
            c.text = h
            c.paragraphs[0].runs[0].bold = True
        for c in v["claims"]:
            row = t.add_row().cells
            row[0].text, row[1].text = c["id"], c["text"]
        for row in t.rows:
            row.cells[0].width, row.cells[1].width = Pt(40), Pt(290)
        t2 = d.add_table(rows=2, cols=2)
        t2.style = "Table Grid"
        t2.cell(0, 0).text, t2.cell(1, 0).text = "Feedback verdict (accept / partial / reject / insufficient)", "Notes (optional)"
    d.save(args.out)
    print(f"wrote {args.out}: {len(exs)} examples, {sum(len(e['claims']) for e in exs)} claims (ids match {existing})")


def to_csv(args):
    d = Document(args.docx)
    rows = [["example_id", "domain", "claim_id", "claim_text", "label", "depends_on", "feedback_verdict", "notes"]]
    tables = d.tables
    for t, t2 in zip(tables[0::2], tables[1::2]):
        iid = t.cell(0, 0).text.strip()
        verdict = t2.cell(0, 1).text.strip().lower()
        notes = t2.cell(1, 1).text.strip()
        for j, row in enumerate(t.rows[1:]):
            cid, text, lab, deps = (c.text.strip() for c in row.cells)
            deps = ";".join(sorted(re.findall(r"c\d+", deps.lower())))
            rows.append([iid, "clinical", cid, text, lab.upper()[:1], deps, verdict if j == 0 else "-", notes if j == 0 else ""])
    out = os.path.splitext(args.docx)[0] + ".csv"
    with open(out, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"wrote {out}: {len(rows) - 1} claims")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("make")
    m.add_argument("--data", default="paperB/data/medec_scope_v0.json")
    m.add_argument("--html", default="annotation/medscope_annotate.html")
    m.add_argument("--out", default="annotation/intexr_annotation.docx")
    m.add_argument("--seed", type=int, default=7)
    c = sp.add_parser("to-csv")
    c.add_argument("docx")
    a = ap.parse_args()
    make(a) if a.cmd == "make" else to_csv(a)
