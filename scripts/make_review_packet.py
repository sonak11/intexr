#!/usr/bin/env python3
"""Build a clinical review packet (Markdown -> PDF via pandoc) for selected MedScope cases.

  python3 scripts/make_review_packet.py --cases ms-val-514 ms-val-30 ms-val-185 ms-val-333 ms-val-520 \
      --title "OB/GYN cases" --out annotation/review_packet_obgyn

Each case shows the source note (MEDEC, CC BY 4.0), the AI-drafted plan with the intended corrections, every piece
of authored evidence and feedback, and a short checklist for the reviewer. Everything except the MEDEC note was
written with LLM assistance; that is what the reviewer is checking.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
from scripts.build_medec_scope import load_medec  # noqa: E402

LABEL_NAMES = {"K": "keep", "D": "**correct** (the error)", "P": "**follows from the error**"}


def fix_mojibake(s):
    """Some MEDEC notes contain UTF-8 text decoded as cp1252 (e.g. 'Î¼L' for 'μL'); repair each garbled run."""
    def repair(m):
        try:
            return m.group(0).encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return m.group(0)
    s = re.sub("[\u00c2-\u00f4][\u0080-\u00bf\u0152-\u2122]{1,2}", repair, s)
    return s.replace("\u00e2\u20ac\u0153", "\u201c").replace("\u00e2\u20ac\u009d", "\u201d")


def pdf_safe(s):
    """Symbols the default pdflatex template cannot print, as inline math."""
    return s.replace("\u2265", "$\\geq$").replace("\u2264", "$\\leq$").replace("\u03bc", "$\\mu$")


def case_md(i, case, note):
    text = fix_mojibake(note["Text"].replace(note["Error Sentence"], "").replace("  ", " ").strip())
    fb = case["feedback"]
    out = [f"## Case {i}: {case['medec_id']} ({note['Error Type']})", "",
           "**Clinical note (MEDEC; the injected error sentence is removed):**", "", f"> {text}", "",
           "**AI-drafted assessment and plan, claim by claim** (D = contains the error; P = follows from the error):", ""]
    for c in case["claims"]:
        line = f"- **{c[0]}** [{c[2]}] {c[1]}"
        if c[2] in ("D", "P"):
            line += f"  \n  → intended revision: {c[3] if c[3] else '*(delete)*'}"
        out.append(line)
    deps = ", ".join(f"{a}→{b}" for a, b in case["dependencies"])
    out += ["", f"Dependencies (which claim was inferred from which): {deps}", "",
            f"**New evidence that settles the error:** {case['new_evidence']}", "",
            "**Feedback variants shown to the model:**", "",
            f"- *Correct feedback:* “{fb['valid']}”",
            f"- *Incorrect feedback* (attacks {fb['false'][0]}): “{fb['false'][1]}”  \n"
            f"  Evidence that the attacked claim is right: {case['false_support']}",
            f"- *Partly correct feedback:* “{fb['partial'][0]}” (the part “{', '.join(fb['partial'][1])}” is "
            "intended to be unsupported)"]
    if case.get("superseding"):
        sup = case["superseding"]
        ch = "; ".join(f"{k} → {v}" for k, v in sup["changes"].items())
        out.append(f"- *Later event:* {sup['evidence']} (intended change: {ch})")
    if case.get("conflicting"):
        out.append(f"- *Conflicting second read:* {case['conflicting']['evidence']}")
    out += ["", "**Please check (tick or comment):**", "",
            "- [ ] The original plan's error is a realistic mistake, and the intended revision is clinically correct.",
            "- [ ] The new evidence is plausible and actually settles the question.",
            "- [ ] The follow-on (P) revisions are correct, and the K claims are fine to keep unchanged.",
            "- [ ] The “incorrect feedback” really is incorrect, and its counter-evidence is accurate.",
            "- [ ] The “unsupported” part of the partly correct feedback is indeed not appropriate here.",
            "", "Comments:", "", "\\vspace{2.5cm}", "", "\\newpage", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", nargs="+", required=True)
    ap.add_argument("--title", default="MedScope cases")
    ap.add_argument("--out", default="annotation/review_packet")
    a = ap.parse_args()
    notes = load_medec()
    props = {}
    pdir = os.path.join(ROOT, "paperB", "proposals")
    for f in sorted(os.listdir(pdir)):
        if f.endswith(".json"):
            for c in json.load(open(os.path.join(pdir, f)))["cases"]:
                props[c["medec_id"]] = c
    md = [f"---\ntitle: \"IntExR / MedScope clinical review: {a.title}\"\ngeometry: margin=2cm\nfontsize: 10pt\n---", "",
          "Thank you for reviewing. Each case starts from a real clinical vignette (MEDEC dataset, CC BY 4.0), in which "
          "medical experts injected one error. An AI-drafted assessment and plan contains that error and the plan items "
          "that follow from it. **Everything except the MEDEC note was drafted with LLM assistance and has not been "
          "clinically reviewed; that is what we ask you to check.** About 5–10 minutes per case. Comments in any form "
          "are welcome; “this is wrong because …” is the most useful.", "", "\\newpage", ""]
    for i, cid in enumerate(a.cases, 1):
        md.append(case_md(i, props[cid], notes[cid]))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out + ".md", "w") as f:
        f.write(pdf_safe("\n".join(md)))
    if shutil.which("pandoc"):
        r = subprocess.run(["pandoc", a.out + ".md", "-o", a.out + ".pdf"], capture_output=True, text=True)
        print(r.stderr.strip() or f"wrote {a.out}.md and {a.out}.pdf")
    else:
        print(f"wrote {a.out}.md (install pandoc for a PDF)")


if __name__ == "__main__":
    main()
