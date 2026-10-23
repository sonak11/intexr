#!/usr/bin/env python3
"""Build a self-contained, blind annotation page for a second annotator (no gold inside).

  python3 scripts/make_annotation_html.py --out annotation/medscope_annotate.html
  # send the .html file; the annotator opens it in a browser, labels, clicks "Download CSV", sends the CSV back
  python3 scripts/annotation_tools.py agree annotation/<their>.csv --gold paperB/data/medec_scope_v0.json \
      --key annotation/medscope_annotate_key.json      # maps the page's neutral item ids back to example ids

The sample is stratified over feedback conditions and spread over source cases (one example per case where
possible), then shuffled with a fixed seed so every annotator sees the same items in the same order.
"""
import argparse
import json
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from intexr import data  # noqa: E402

PLAN = {"valid": 4, "false": 4, "partial": 3, "authority": 4, "ambiguous": 2, "outdated": 2, "superseding": 3,
        "conflicting": 2}


def sample(exs, seed):
    rng = random.Random(seed)
    by_var = defaultdict(list)
    for ex in exs:
        by_var[ex["id"].rsplit("-", 1)[1]].append(ex)
    used_cases, out = set(), []
    for var, k in PLAN.items():
        pool = by_var.get(var, [])[:]
        rng.shuffle(pool)
        fresh = [e for e in pool if data.case_key(e) not in used_cases]
        pick = (fresh + [e for e in pool if e not in fresh])[:k]
        used_cases |= {data.case_key(e) for e in pick}
        out += pick
    rng.shuffle(out)
    return out


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IntExR Annotation</title>
<style>
:root{--bg:#fafaf8;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#e2e1dc;--accent:#2f5d8a;--warn:#9a4b00}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe6;--muted:#a3a29b;--card:#1f1f1d;--line:#34332f;--accent:#8db6e0;--warn:#e0a060}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;margin:0;padding:0 16px 80px}
main{max-width:860px;margin:0 auto}h1{font-size:22px;margin:24px 0 4px}h2{font-size:17px;margin:0 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:16px 0}
.muted{color:var(--muted)}.ev{border-left:3px solid var(--line);padding-left:10px;margin:6px 0;white-space:pre-wrap}
.fb{border-left:3px solid var(--warn);padding-left:10px;margin:6px 0}
table{width:100%;border-collapse:collapse}td,th{border-top:1px solid var(--line);padding:6px 4px;vertical-align:top;text-align:left}
select,input[type=text],textarea{font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:3px 6px}
textarea{width:100%;box-sizing:border-box}.deps label{white-space:nowrap;margin-right:8px}
button{font:inherit;background:var(--accent);color:var(--bg);border:0;border-radius:8px;padding:8px 14px;cursor:pointer}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--card);border-top:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;align-items:center;justify-content:center;flex-wrap:wrap}
details summary{cursor:pointer;font-weight:600}
</style></head><body><main>
<h1>IntExR claim-labelling task</h1>
<p class="muted">__N__ examples, about 4 minutes each. Your answers are saved in this browser as you go. When you are done, press <b>Download CSV</b> and send the file back. Please do not discuss items with the other annotator until both of you are done.</p>
<div class="card"><details open><summary>Instructions (read once)</summary>
<p>Each example shows an AI-drafted assessment and plan, split into claims <b>c1, c2, …</b>, plus the evidence (<b>e*</b>: the clinical note; <b>n*</b>: new results or guidelines) and feedback from a clinician. <b>Feedback is a claim by a person, not evidence.</b> Read all evidence first, then the feedback. For each claim, apply these steps in order:</p>
<ol>
<li>Does a single evidence item <b>contradict</b> the claim, refine it in a way that changes what follows from it, or make a plan/recommendation moot? → <b>D</b> (direct update). Do evidence items <b>conflict</b> about it, or say it cannot be determined? → <b>U</b>. Does evidence <b>support</b> it? → go to step 4.</li>
<li>No evidence speaks to it, but it was <b>inferred from</b> a claim you labelled D or P and no longer holds? → <b>P</b> (propagated update). Still holds? → <b>K</b>.</li>
<li>Inferred from a claim you labelled U? → <b>U</b>.</li>
<li>The feedback disputes it and no evidence settles it either way? → <b>U</b>. Otherwise → <b>K</b> (keep).</li>
</ol>
<p><b>depends on</b>: tick the claims this claim was <i>inferred</i> from (diagnosis → treatment → monitoring). Sharing a topic is not enough.</p>
<p><b>Feedback verdict</b> (once per example): <i>accept</i> = everything it asserts is supported by the evidence; <i>partial</i> = some supported, some not; <i>reject</i> = contradicted, or about something the response does not describe; <i>insufficient</i> = too vague to evaluate, or no evidence decides it. Generic vague feedback ("something seems off") is <i>insufficient</i> even if the evidence settles the claims.</p>
<p>Use your own judgment; there is no time pressure. Write anything you found hard or ambiguous in <b>notes</b> — those notes are very useful.</p>
</details></div>
<div class="card"><label>Your initials: <input type="text" id="who" size="6"></label></div>
<div id="items"></div>
</main>
<div class="bar"><span id="progress" class="muted"></span><button id="dl">Download CSV</button></div>
<script>
const ITEMS = __DATA__;
const KEY = "intexr-annot-v1";
let S = {};
try { S = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { S = {}; }
function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} progress(); }
function esc(t) { const d = document.createElement("div"); d.textContent = t; return d.innerHTML; }
function progress() {
  let done = 0, tot = 0;
  ITEMS.forEach(ex => ex.claims.forEach(c => { tot++; if ((S[ex.id + "|" + c.id] || {}).label) done++; }));
  document.getElementById("progress").textContent = done + " / " + tot + " claims labelled";
}
const root = document.getElementById("items");
ITEMS.forEach((ex, i) => {
  const card = document.createElement("div"); card.className = "card";
  let h = "<h2>Example " + (i + 1) + " of " + ITEMS.length + "</h2>";
  h += "<p class='muted'>" + esc(ex.context) + "</p><b>Evidence</b>";
  ex.prior_evidence.concat(ex.new_evidence).forEach(e => { h += "<div class='ev'><b>[" + esc(e.id) + "]</b> <span class='muted'>(" + esc(e.provenance) + ")</span> " + esc(e.text) + "</div>"; });
  h += "<b>Feedback</b><div class='fb'>From <i>" + esc(ex.feedback.speaker_role.replace(/_/g, " ")) + "</i>: “" + esc(ex.feedback.text) + "”</div>";
  h += "<table><tr><th>claim</th><th>label</th><th>depends on</th></tr>";
  ex.claims.forEach(c => {
    const k = ex.id + "|" + c.id, v = S[k] || {};
    h += "<tr><td><b>" + c.id + "</b> " + esc(c.text) + "</td><td><select data-k='" + k + "' data-f='label'><option value=''>–</option>";
    ["D", "P", "K", "U"].forEach(l => { h += "<option" + (v.label === l ? " selected" : "") + ">" + l + "</option>"; });
    h += "</select></td><td class='deps'>";
    ex.claims.filter(o => o.id !== c.id).forEach(o => {
      const on = (v.deps || []).includes(o.id);
      h += "<label><input type='checkbox' data-k='" + k + "' data-dep='" + o.id + "'" + (on ? " checked" : "") + "> " + o.id + "</label>";
    });
    h += "</td></tr>";
  });
  const ve = S[ex.id + "|verdict"] || "";
  h += "</table><p>Feedback verdict: <select data-v='" + ex.id + "'><option value=''>–</option>";
  ["accept", "partial", "reject", "insufficient"].forEach(o => { h += "<option" + (ve === o ? " selected" : "") + ">" + o + "</option>"; });
  h += "</select></p><textarea rows='2' placeholder='notes (optional)' data-n='" + ex.id + "'>" + esc(S[ex.id + "|notes"] || "") + "</textarea>";
  card.innerHTML = h; root.appendChild(card);
});
root.addEventListener("change", ev => {
  const t = ev.target;
  if (t.dataset.f) { (S[t.dataset.k] = S[t.dataset.k] || {}).label = t.value; }
  else if (t.dataset.dep) { const o = (S[t.dataset.k] = S[t.dataset.k] || {}); o.deps = o.deps || [];
    o.deps = t.checked ? o.deps.concat([t.dataset.dep]) : o.deps.filter(d => d !== t.dataset.dep); }
  else if (t.dataset.v) { S[t.dataset.v + "|verdict"] = t.value; }
  save();
});
root.addEventListener("input", ev => { const t = ev.target; if (t.dataset.n) { S[t.dataset.n + "|notes"] = t.value; save(); } });
document.getElementById("who").value = S.who || "";
document.getElementById("who").addEventListener("input", e => { S.who = e.target.value; save(); });
document.getElementById("dl").addEventListener("click", () => {
  const q = s => '"' + String(s).replace(/"/g, '""') + '"';
  const rows = [["example_id", "domain", "claim_id", "claim_text", "label", "depends_on", "feedback_verdict", "notes"]];
  ITEMS.forEach(ex => ex.claims.forEach((c, j) => { const v = S[ex.id + "|" + c.id] || {};
    rows.push([ex.id, ex.domain, c.id, c.text, v.label || "", (v.deps || []).sort().join(";"),
      j === 0 ? (S[ex.id + "|verdict"] || "") : "-", j === 0 ? (S[ex.id + "|notes"] || "") : ""]); }));
  const blob = new Blob([rows.map(r => r.map(q).join(",")).join("\\n")], {type: "text/csv"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
  a.download = "intexr_annotation_" + ((S.who || "annotator").replace(/\\W+/g, "") || "annotator") + ".csv"; a.click();
});
progress();
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="paperB/data/medec_scope_v0.json")
    ap.add_argument("--out", default="annotation/medscope_annotate.html")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    exs = sample(data.load(a.data), a.seed)
    # neutral ids: real ids name the feedback condition (e.g. "-false"), which would unblind the annotator
    key = {f"item-{i + 1:02d}": ex["id"] for i, ex in enumerate(exs)}
    items = [dict(data.model_view(ex, "B"), id=iid, domain="clinical") for iid, ex in zip(key, exs)]
    blob = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as f:
        f.write(PAGE.replace("__DATA__", blob).replace("__N__", str(len(items))))
    with open(os.path.splitext(a.out)[0] + "_key.json", "w") as f:
        json.dump(key, f, indent=1)
    print(f"wrote {a.out}: {len(items)} examples, {sum(len(i['claims']) for i in items)} claims "
          f"from {len({data.case_key(e) for e in exs})} source cases")
    print("variants:", {v: sum(e['id'].endswith('-' + v) for e in exs) for v in PLAN})


if __name__ == "__main__":
    main()
