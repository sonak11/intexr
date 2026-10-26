// IntExR progress since the 7 Oct meeting with Defei. Builds an editable .pptx (opens in Google Slides / PowerPoint).
//   npm i pptxgenjs@3.12.0  (once, anywhere on NODE_PATH)
//   node docs/slides/build_update_deck_late_oct.js  -> docs/slides/IntExR_update_late_Oct2026.pptx
// Same visual language as IntExR_update_Oct2026.pptx (navy, warm paper, orange labels), with Office-safe fonts.
const path = require("path");
const pptxgen = require("pptxgenjs");

const OUT = path.join(__dirname, "IntExR_update_late_Oct2026.pptx");
const APPLY_THEME = process.env.APPLY_THEME; // path to the pptx skill's apply_theme.js (optional)

const THEME = {
  name: "IntExR Paper",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "15223B", lt1: "FFFFFF", dk2: "4A5568", lt2: "F6F4EE",
    accent1: "A8461F", accent2: "2F6690", accent3: "7A5A12", accent4: "F0A67A", accent5: "DDD8CC", accent6: "6B7280",
    hlink: "2F6690", folHlink: "7A5A12",
  },
};
const HEX = { navy: "15223B", paper: "F6F4EE", orange: "A8461F", blue: "2F6690", line: "DDD8CC", mute: "6B7280", card: "FFFDF8", peach: "F0A67A", soft: "4A5568" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.author = "Sonakshi Sharma";
pres.title = "IntExR progress since 7 Oct";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

// ---------------------------------------------------------------- layouts
const M = 0.6; // side margin
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: HEX.navy },
  objects: [
    { placeholder: { options: { name: "eyebrow", type: "body", x: M, y: 2.0, w: 12.1, h: 0.4, fontSize: 14, bold: true, color: C.accent4, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.45, w: 12.1, h: 1.8, fontSize: 44, bold: true, color: C.background1, fontFace: "Cambria", valign: "top", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 4.4, w: 11.5, h: 1.2, fontSize: 18, color: C.accent5, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.paper },
  objects: [
    { placeholder: { options: { name: "eyebrow", type: "body", x: M, y: 0.45, w: 12.1, h: 0.35, fontSize: 13, bold: true, color: C.accent1, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.8, w: 12.1, h: 0.85, fontSize: 32, bold: true, color: C.text1, fontFace: "Cambria", valign: "top", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "footer", type: "body", x: 1.1, y: 6.95, w: 11.6, h: 0.3, fontSize: 11, color: C.accent6, margin: 0 }, text: "" } },
  ],
  slideNumber: { x: M, y: 6.95, w: 0.4, h: 0.3, fontSize: 11, color: HEX.mute },
});
pres.defineSlideMaster({
  title: "CONTENT_DARK",
  background: { color: HEX.navy },
  objects: [
    { placeholder: { options: { name: "eyebrow", type: "body", x: M, y: 0.45, w: 12.1, h: 0.35, fontSize: 13, bold: true, color: C.accent4, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.8, w: 12.1, h: 0.85, fontSize: 32, bold: true, color: C.background1, fontFace: "Cambria", valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: M, y: 6.95, w: 0.4, h: 0.3, fontSize: 11, color: HEX.line },
});

function content(section, eyebrow, title, footer, notes, dark = false) {
  const s = pres.addSlide({ masterName: dark ? "CONTENT_DARK" : "CONTENT", sectionTitle: section });
  s.addText(eyebrow.toUpperCase(), { placeholder: "eyebrow" });
  s.addText(title, { placeholder: "title" });
  if (footer && !dark) s.addText(footer, { placeholder: "footer" });
  if (notes) s.addNotes(notes);
  return s;
}

function card(s, name, x, y, w, h, opts = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    objectName: name, x, y, w, h, rectRadius: 0.08,
    fill: { color: opts.fill || HEX.card }, line: { color: opts.line || HEX.line, width: 0.75 },
  });
}

function stat(s, name, x, y, w, value, label, color = C.accent1) {
  s.addText(value, { objectName: name + "-value", x, y, w, h: 0.8, fontSize: 44, bold: true, color, fontFace: "Cambria", margin: 0, isTextBox: true });
  s.addText(label, { objectName: name + "-label", x, y: y + 0.8, w, h: 0.6, fontSize: 14, color: C.text2, margin: 0, valign: "top", isTextBox: true });
}

const tableHead = (cells) => cells.map((t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: HEX.navy } } }));

// ---------------------------------------------------------------- 1 title
pres.addSection({ title: "Overview" });
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Overview" });
s.addText("INTEXR · PROGRESS UPDATE · LATE OCTOBER 2026", { placeholder: "eyebrow" });
s.addText("From a built harness to real model runs", { placeholder: "title" });
s.addText("Everything since our 7 Oct meeting: answers to the four open questions, a bigger MedScope, the scope-first method, and first runs at $0.\nSonakshi Sharma · Rutgers CS · thesis with Prof. Metaxas", { placeholder: "body" });
s.addNotes("Last time the harness was built but no model had been run, and I had four open questions. This deck covers what changed since 7 Oct. Short version: the questions are answered, the method is built, and real runs are going at zero cost.");

// ---------------------------------------------------------------- 2 at a glance
s = content("Overview", "At a glance", "Three weeks of progress in four numbers", "All work is in github.com/sonak11/intexr (private)",
  "MedScope grew from 31 to 47 cases. The scope-first method is now a real pipeline. First model results are in, on the dev split: two open models, three systems. Our pipeline gets 0.80 interaction-exact accuracy with Qwen, against 0.45 for an evidence-aware prompt. The Paper 1 draft exists in ACL format.");
const glance = [
  ["47", "MedScope source cases\n(was 31 on 7 Oct)"],
  ["1,418", "gold-labelled claims\n(was 873)"],
  ["0.80", "best exact accuracy:\nour pipeline (Qwen)"],
  ["$0", "spent: free tiers + Rutgers GPUs\nno lab API key needed"],
];
glance.forEach(([v, l], i) => {
  const x = M + i * 3.07;
  card(s, `glance-card-${i}`, x, 2.1, 2.85, 2.1);
  stat(s, `glance-${i}`, x + 0.3, 2.45, 2.3, v, l, i === 3 ? C.accent2 : C.accent1);
});
s.addText("Also new: an 8-page Paper 1 draft, a frozen dev/test split, a protocol draft, and review packets for clinicians.", {
  objectName: "glance-also", x: M, y: 4.75, w: 12.1, h: 0.5, fontSize: 16, color: C.text1, margin: 0, isTextBox: true });

// ---------------------------------------------------------------- 3 four questions answered
pres.addSection({ title: "Open questions" });
s = content("Open questions", "Follow-up", "The four open questions from last time", "Q1 still needs Prof. Metaxas; the rest are resolved or in motion",
  "Compute: instead of asking for a lab key, I moved everything to free tiers and the department GPU server. Clinicians: two Rutgers faculty identified, with review packets ready. Non-medical: COCO is now only a baseline; EditPropBench converted to our format is the hard set.");
s.addTable([
  tableHead(["Question (7 Oct)", "Status now"]),
  ["1 · Paper split (MedScope vs. Paper 1)", "Plan unchanged; still to confirm with Prof. Metaxas at the novelty review"],
  ["2 · Clinicians for review", "Two RWJMS faculty identified: Dr. Archana Pradhan (MD, OB/GYN) and Dr. Naveena Yanamala (clinical AI); review packets ready"],
  ["3 · Compute (lab API key?)", "Not needed: Groq + Gemini free tiers for public data; thasos GPUs for the full design. $0 so far"],
  ["4 · Non-medical domain", "COCO kept only as a baseline; EditPropBench-IntExR is the hard set; ARIES as an option"],
], { objectName: "questions-table", x: M, y: 1.95, w: 12.1, colW: [3.9, 8.2], fontSize: 15, color: HEX.navy, fill: { color: HEX.card },
  border: { type: "solid", pt: 0.75, color: HEX.line }, margin: [0.08, 0.12, 0.08, 0.12], rowH: 0.75, valign: "middle" });

// ---------------------------------------------------------------- 4 MedScope growth (chart)
pres.addSection({ title: "Data" });
s = content("Data", "MedScope · batches 3 and 4", "New cases filled the thin cells", "47 cases → 293 examples, 1,418 claims · 20 dev / 27 test · all authored content still clinically unreviewed",
  "Sixteen new cases target what was thin: two-step chains (diagnosis, then treatment, then monitoring), events after the plan was written, and conflicting evidence. Depth-2 propagated claims went from 6 to 98. All new content is LLM-drafted and flagged unreviewed.");
s.addChart(pres.charts.BAR, [
  { name: "7 Oct", labels: ["Source cases", "Depth-2 P claims", "Supported K claims", "Superseding examples", "Conflicting-evidence ex."], values: [31, 6, 0, 2, 0] },
  { name: "Now", labels: ["Source cases", "Depth-2 P claims", "Supported K claims", "Superseding examples", "Conflicting-evidence ex."], values: [47, 98, 47, 6, 5] },
], { objectName: "growth-chart", x: M, y: 1.85, w: 7.6, h: 4.8, barDir: "bar", barGrouping: "clustered",
  chartColors: [HEX.line, HEX.orange], showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt",
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelFontFace: "+mn-lt", dataLabelColor: HEX.navy,
  catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", catAxisLabelColor: HEX.soft, valAxisHidden: true,
  valGridLine: { style: "none" }, catGridLine: { style: "none" }, catAxisOrientation: "maxMin" });
card(s, "growth-card", 8.6, 2.0, 4.1, 2.75);
s.addText([
  { text: "What the new cases add", options: { bold: true, breakLine: true, fontSize: 16 } },
  { text: "Two-step chains: a wrong diagnosis → its treatment → its monitoring", options: { bullet: true, breakLine: true } },
  { text: "Later events that change a claim that was right when written", options: { bullet: true, breakLine: true } },
  { text: "Two evidence items that disagree → the claim must be hedged", options: { bullet: true } },
], { objectName: "growth-text", x: 8.85, y: 2.2, w: 3.65, h: 2.4, fontSize: 14, color: C.text1, valign: "top", paraSpaceAfter: 8, margin: 0, isTextBox: true });

// ---------------------------------------------------------------- 5 rigor fixes
s = content("Data", "Rigor", "Two problems found and fixed", "Both fixes are in the builder and the metrics code; the oracle still scores 1.0",
  "Fix 1: the false-feedback condition broke our own rule. A claim attacked by feedback with no evidence either way should be Unresolved, but it was labelled Keep. Each case now has an evidence item supporting the attacked claim, which also creates the evidence-supported Keep category we report as the headline preservation number. Fix 2: confidence intervals resampled examples, but each case has 6 to 8 variants, so the intervals were too narrow.");
[["1", "False-feedback variant contradicted our own guide",
  "The attacked claim was labelled K, but with no evidence either way the guide says U. Each case now carries an evidence item supporting the attacked claim, so it is K-supported: changing it is measurable sycophancy."],
 ["2", "Confidence intervals were too narrow",
  "Bootstrap resampled examples, but each case has 6–8 feedback variants. It now resamples whole source cases, as the task definition specifies."]].forEach(([n, h, b], i) => {
  const x = M + i * 6.15;
  card(s, `fix-card-${i}`, x, 2.0, 5.95, 2.9);
  s.addShape(pres.shapes.OVAL, { objectName: `fix-badge-${i}`, x: x + 0.35, y: 2.35, w: 0.6, h: 0.6, fill: { color: HEX.orange }, line: { color: HEX.orange } });
  s.addText(n, { objectName: `fix-num-${i}`, x: x + 0.35, y: 2.35, w: 0.6, h: 0.6, fontSize: 18, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText(h, { objectName: `fix-head-${i}`, x: x + 1.15, y: 2.3, w: 4.5, h: 0.8, fontSize: 18, bold: true, color: C.text1, valign: "middle", margin: 0, isTextBox: true });
  s.addText(b, { objectName: `fix-body-${i}`, x: x + 0.35, y: 3.3, w: 5.3, h: 1.45, fontSize: 15, color: C.text2, valign: "top", margin: 0, isTextBox: true });
});

// ---------------------------------------------------------------- 6 method
pres.addSection({ title: "Method" });
s = content("Method", "Scope-first pipeline", "The LLM reads; code decides the labels", "With perfect alignment, the code reproduces every gold label: the label rules are executable and tested",
  "The single-prompt version asks one call to do everything. The pipeline gives the model only what needs language understanding: which evidence supports or contradicts each claim, and how to word the changes. The precedence rule is code. Kept claims are copied verbatim, so they cannot be reworded. A final check catches content that only the feedback asserts. Two to three calls per example.");
const steps = [
  ["1 · Align", "LLM", "Which evidence supports or contradicts each claim; dependencies; disputes"],
  ["2 · Label", "code", "Precedence: direct evidence > dependency > feedback > keep"],
  ["3 · Revise", "LLM", "Rewrite only changed or hedged claims; check each dependent"],
  ["4 · Assemble", "code", "Splice into the original; kept claims copied verbatim"],
  ["5 · Check", "code", "Feedback-only content may not leak; re-revise once"],
];
steps.forEach(([h, kind, b], i) => {
  const x = M + i * 2.48, llm = kind === "LLM";
  card(s, `step-card-${i}`, x, 2.2, 2.2, 2.7, { fill: llm ? "E3ECF4" : HEX.card, line: llm ? HEX.blue : HEX.line });
  s.addText(kind.toUpperCase(), { objectName: `step-kind-${i}`, x: x + 0.2, y: 2.35, w: 1.8, h: 0.3, fontSize: 11, bold: true, color: llm ? C.accent2 : C.accent6, margin: 0, isTextBox: true });
  s.addText(h, { objectName: `step-head-${i}`, x: x + 0.2, y: 2.7, w: 1.85, h: 0.5, fontSize: 17, bold: true, color: C.text1, margin: 0, isTextBox: true });
  s.addText(b, { objectName: `step-body-${i}`, x: x + 0.2, y: 3.3, w: 1.85, h: 1.45, fontSize: 14, color: C.text2, valign: "top", margin: 0, isTextBox: true });
  if (i < steps.length - 1) {
    s.addShape(pres.shapes.LINE, { objectName: `step-arrow-${i}`, x: x + 2.22, y: 3.85, w: 0.24, h: 0, line: { color: HEX.orange, width: 2, endArrowType: "triangle" } });
  }
});
s.addText("Blue = model call · white = deterministic code", { objectName: "step-legend", x: M, y: 5.2, w: 12.1, h: 0.4, fontSize: 14, color: C.text2, margin: 0, isTextBox: true });

// ---------------------------------------------------------------- 7 systems
s = content("Method", "Baselines", "Every baseline the thesis plan lists now exists", "Free-text systems are mapped to claim actions by a fixed LLM judge; structured systems are also checked against it",
  "New since last time: the claim-level evidence gate, which needs a natural-language-inference model and so runs on thasos, and the strong correction baseline, verify-then-revise, modelled on Chain-of-Verification and RARR. It shares our per-claim checking but not our label rules, propagation check or verbatim assembly, so it isolates what those add.");
s.addTable([
  tableHead(["System", "What it is", "Status"]),
  ["No revision · always accept · always rewrite", "Floor and naive baselines", "built"],
  ["Dialogue · evidence-aware prompt", "Ordinary chat; prompt that says feedback may be wrong", "built, running"],
  ["Evidence gate (NLI)", "Per-claim entailment check, no propagation", "new · needs GPU"],
  ["Verify-then-revise", "Strong baseline: Chain-of-Verification / RARR style", "new"],
  ["Scope-first (one prompt)", "Structured JSON in a single call", "built, running"],
  ["Scope-first pipeline + 2 ablations", "Our method; no-propagation-check and no-leak-check variants", "new, running"],
], { objectName: "systems-table", x: M, y: 1.9, w: 12.1, colW: [4.2, 5.6, 2.3], fontSize: 15, color: HEX.navy, fill: { color: HEX.card },
  border: { type: "solid", pt: 0.75, color: HEX.line }, margin: [0.07, 0.12, 0.07, 0.12], rowH: 0.62, valign: "middle" });

// ---------------------------------------------------------------- 8 runs at $0
pres.addSection({ title: "Experiments" });
s = content("Experiments", "Model runs", "Real runs started, at zero cost", "Free tiers only for public data; MIMIC would only ever run on self-hosted models",
  "Groq's free tier allows about 200 thousand tokens per model per day, roughly 120 calls. So the free tier runs a pre-specified slice: the 20 dev cases under valid, false and authority-only feedback, conditions A and B, and the three systems the main claims need. That takes about four days per model, running in parallel. The full design (all 293 examples, all systems) needs the thasos GPUs, which I can use with my own account.");
const runs = [
  ["Models", "gpt-oss-120b (low reasoning)\nQwen3.8-27B (reasoning off)\nboth via Groq free tier"],
  ["Judge", "gemini-3.5-flash-lite,\nfixed for every run;\ncalibration against my labels next"],
  ["Free-tier slice", "60 dev examples × conditions A, B\n× 3 systems ≈ 4 days per model\n(200K tokens/day cap)"],
  ["Full design", "293 examples, all systems,\nNLI gate: thasos GPUs\n(own account, no scheduler)"],
];
runs.forEach(([h, b], i) => {
  const x = M + (i % 2) * 6.15, y = 2.0 + Math.floor(i / 2) * 2.3;
  card(s, `run-card-${i}`, x, y, 5.95, 2.05);
  s.addText(h, { objectName: `run-head-${i}`, x: x + 0.3, y: y + 0.2, w: 5.3, h: 0.45, fontSize: 18, bold: true, color: i < 3 ? C.accent1 : C.accent2, margin: 0, isTextBox: true });
  s.addText(b, { objectName: `run-body-${i}`, x: x + 0.3, y: y + 0.7, w: 5.3, h: 1.2, fontSize: 15, color: C.text1, valign: "top", margin: 0, isTextBox: true });
});

// ---------------------------------------------------------------- 9 first model results
s = content("Experiments", "First model results · dev split, 60 examples", "Unverified feedback costs preservation, not propagation",
  "Qwen3.8-27B, evidence-aware prompt. E − A = +0.72 [0.57, 0.86]; B − E = −0.05 [−0.21, 0.09] on P recall; B − E = +0.15 [0.00, 0.30] on supported-claim changes",
  "Three conditions on the same claims. A: a bare verified edit. The model applies exactly that edit and leaves dependents stale: only 7 percent of dependent claims get fixed. E: the same verified edit plus 'also update what depends on it': 79 percent. B: unverified feedback plus evidence: 74 percent. So the gap I first saw between A and B was the wording of the edit, not verification. That matters for benchmarks built on bare verified edits. With wording controlled, propagation is the same, and the real cost of unverified feedback is sycophancy: the model changes more of the claims the evidence supports. Our pipeline changes none of them, and gets 0.80 exact accuracy with Qwen versus 0.45. With gpt-oss the pipeline was weaker, because the model skips dependency links; I fixed that by rule in version 1.");
s.addChart(pres.charts.BAR, [
  { name: "Change recall on propagated claims", labels: ["A · bare verified edit", "E · verified edit + 'update dependents'", "B · feedback + evidence"], values: [0.07, 0.79, 0.74] },
], { objectName: "abe-chart", x: M, y: 1.95, w: 7.0, h: 4.6, barDir: "col", chartColors: [HEX.line, HEX.blue, HEX.orange], showLegend: false,
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelFontSize: 14, dataLabelFontFace: "+mn-lt", dataLabelColor: HEX.navy,
  catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", catAxisLabelColor: HEX.soft, valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 1,
  valGridLine: { style: "none" }, catGridLine: { style: "none" }, showTitle: true, title: "Change recall on propagated claims (Qwen, evidence-aware prompt)", titleFontSize: 13, titleFontFace: "+mn-lt", titleColor: HEX.soft });
card(s, "syco-card", 8.1, 2.0, 4.6, 4.4);
stat(s, "syco", 8.45, 2.3, 4.0, "20% → 0%", "of evidence-supported claims changed under false feedback: evidence-aware prompt vs. our pipeline (Qwen)");
s.addText("Pipeline exact accuracy 0.80 vs. 0.45 (Qwen). With gpt-oss it was weaker (0.57), because the model skips dependency links; v1 fixes this by rule.", {
  objectName: "syco-text", x: 8.45, y: 4.3, w: 4.0, h: 1.9, fontSize: 15, color: C.text1, valign: "top", margin: 0, isTextBox: true });

// ---------------------------------------------------------------- 10 novelty
pres.addSection({ title: "Novelty and protocol" });
s = content("Novelty and protocol", "Novelty review · Oct 31", "The gap is still open",
  "Literature matrix: 59 papers, 39 verified on the web (was 20 of 55) · memo: docs/09_novelty_memo.md",
  "I verified 14 more papers online, fixed two venues, and ran a fresh search for 2026 work. Nothing combines dependent-claim propagation with feedback that may be wrong. The closest new paper shows that suppressing sycophancy also suppresses justified updating, at the answer level; they call it a selectivity problem, which is what we measure per claim. The two-page memo for the 31 October review is drafted; its results section waits for the runs.");
s.addTable([
  tableHead(["Closest work", "Propagation", "Feedback may be wrong", "Claim-level"]),
  ["EditPropBench (2026) · RevPropBench (EMNLP-Ind 2026)", "yes", "no: edit assumed correct", "yes"],
  ["Sycophancy Suppression … Rational Updating (2026, new)", "no", "yes", "no: whole answer"],
  ["PBT · SycEval · Med-Stress (2025–26)", "no", "yes", "no: whole answer"],
  ["IntExR-Scope", "yes", "yes", "yes"],
], { objectName: "novelty-table", x: M, y: 1.95, w: 12.1, colW: [5.6, 1.9, 2.7, 1.9], fontSize: 15, color: HEX.navy, fill: { color: HEX.card },
  border: { type: "solid", pt: 0.75, color: HEX.line }, margin: [0.08, 0.12, 0.08, 0.12], rowH: 0.7, valign: "middle" });
s.addText("Same claims, three conditions: bare verified edit (A), verified edit + 'update dependents' (E), unverified feedback + evidence (B).", {
  objectName: "novelty-test", x: M, y: 5.75, w: 12.1, h: 0.5, fontSize: 16, bold: true, color: C.text1, margin: 0, isTextBox: true });

// ---------------------------------------------------------------- 11 protocol
s = content("Novelty and protocol", "Toward the Dec 18 freeze", "Rigor is in place before the headline numbers", "Protocol draft: docs/10_frozen_protocol.md · guide: docs/04_annotation_guide.md",
  "The dev/test split is frozen by source case: the 20 cases in the runs are dev, the other 20 are held out until the freeze. Hypotheses H1 to H5 are written down with their tests before any model result. The second annotator gets a blind web page; clinicians get separate review packets that contain the answers.");
[["Dev / test split", "Frozen by source case: 20 dev (runs, prompts) · 20 test held out until 18 Dec"],
 ["Pre-registered", "H1–H5 with their statistical tests and Holm correction, written before results"],
 ["Second annotator", "Blind 24-item web page: autosave, CSV export, neutral item ids"],
 ["Clinical review", "PDF packets: 5 OB/GYN cases and all 40, with a checklist per case"],
 ["Sample size", "Script computes test-set size from dev A/B variance (≈34 cases in simulation)"],
 ["Paper 1 draft", "8 pages, ACL format; appendix generated from the code (prompts, example)"]].forEach(([h, b], i) => {
  const x = M + (i % 3) * 4.1, y = 1.95 + Math.floor(i / 3) * 2.0;
  card(s, `proto-card-${i}`, x, y, 3.9, 1.75);
  s.addText(h, { objectName: `proto-head-${i}`, x: x + 0.25, y: y + 0.2, w: 3.4, h: 0.45, fontSize: 17, bold: true, color: C.accent1, margin: 0, isTextBox: true });
  s.addText(b, { objectName: `proto-body-${i}`, x: x + 0.25, y: y + 0.7, w: 3.4, h: 0.95, fontSize: 14, color: C.text1, valign: "top", margin: 0, isTextBox: true });
});

// ---------------------------------------------------------------- 12 timeline + asks
pres.addSection({ title: "Next" });
s = content("Next", "Next steps and where I need input", "Next eight weeks", "",
  "Oct 31: novelty review with the first A-versus-B numbers. November: agreement study, clinical review, full runs on thasos, judge calibration. Dec 18: pilot report and frozen protocol. Questions for Defei are on the right.", true);
const tl = [["Oct 31", "Novelty review with first A-vs-B numbers (free-tier slice)"],
  ["November", "Second annotator + κ · clinical review · full runs on thasos · judge calibration"],
  ["Dec 18", "Pilot report with go/no-go · frozen protocol · tagged release"],
  ["Jan–Feb", "Write and submit MedScope (CHIL, deadline to confirm)"]];
tl.forEach(([d, t], i) => {
  const y = 2.0 + i * 1.12;
  s.addText(d, { objectName: `tl-date-${i}`, x: M, y, w: 1.6, h: 0.9, fontSize: 18, bold: true, color: C.accent4, valign: "top", margin: 0, isTextBox: true });
  s.addText(t, { objectName: `tl-text-${i}`, x: M + 1.7, y, w: 4.9, h: 0.9, fontSize: 15, color: C.background1, valign: "top", margin: 0, isTextBox: true });
});
card(s, "ask-card", 7.4, 1.95, 5.3, 3.9, { fill: "1F2F4D", line: "2F4066" });
s.addText([
  { text: "Questions for you", options: { bold: true, fontSize: 18, color: HEX.peach, breakLine: true } },
  { text: "Is the free-tier dev slice enough evidence for the Oct 31 review?", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Approaching Dr. Pradhan and Dr. Yanamala: any advice, and how to involve Prof. Metaxas?", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Target size for MedScope: grow from 40 to 80–100 cases before spring?", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Are open-weight models enough for reviewers, or do we need one frontier model?", options: { bullet: { type: "number" } } },
], { objectName: "ask-list", x: 7.7, y: 2.2, w: 4.75, h: 3.5, fontSize: 15, color: "FFFFFF", valign: "top", paraSpaceAfter: 10, margin: 0, isTextBox: true });

(async () => {
  await pres.writeFile({ fileName: OUT });
  if (APPLY_THEME) {
    const { applyTheme } = require(APPLY_THEME);
    await applyTheme(OUT, THEME);
  }
  console.log("wrote", OUT);
})();
