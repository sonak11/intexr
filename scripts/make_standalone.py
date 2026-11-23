#!/usr/bin/env python3
"""Write paper1/main_standalone.tex: main.tex with refs.bib and the generated appendix inlined and the ACL style
replaced by standard packages, so it compiles as a single file (e.g. uploaded alone to Overleaf).

  python3 scripts/make_standalone.py
"""
import os

P = os.path.join(os.path.dirname(__file__), "..", "paper1")


def read(name):
    with open(os.path.join(P, name)) as f:
        return f.read()


s = read("main.tex")
s = s.replace("\\usepackage[review]{acl}", "\\usepackage[a4paper,margin=2.2cm,columnsep=0.6cm]{geometry}\n"
              "\\usepackage[round]{natbib}\n\\bibliographystyle{plainnat}\n\\usepackage{url}\n\\usepackage[hidelinks]{hyperref}")
s = s.replace("\\documentclass[11pt]{article}", "\\documentclass[11pt,twocolumn]{article}")
s = s.replace("\\input{generated/example}", read("generated/example.tex").strip())
s = s.replace("\\input{generated/prompts}", read("generated/prompts.tex").strip())
head = ("% Standalone single-file version of paper1/main.tex: no acl.sty, acl_natbib.bst, refs.bib or generated/ needed.\n"
        "% Compile with pdfLaTeX + BibTeX (Overleaf: just upload this one file). Regenerated from main.tex by "
        "scripts/make_standalone.py.\n\\begin{filecontents*}[overwrite]{refs.bib}\n" + read("refs.bib").strip() +
        "\n\\end{filecontents*}\n")
with open(os.path.join(P, "main_standalone.tex"), "w") as f:
    f.write(head + s)
print("wrote paper1/main_standalone.tex")
