# First model results (v0, free-tier dev slice), 25–26 Oct 2026

**26 Oct update:**
- Numbers re-run on MedScope v0.2 (dev).
- The gpt-oss pipeline × B result and the condition E wording control are in.
- The H1 finding is revised below: the 'literal' effect is wording; the real cost of unverified feedback is sycophancy.
- **Pipeline v1** (rule-based verdict, broader propagation check), dev results 26 Oct:
  - gpt-oss: P recall 0.72 → **0.95**, verdict 0.25 → **0.93**, exact 0.57 → **0.63** (level with the single prompt); collateral change on K 0.03 → 0.07.
  - Qwen: unchanged except verdict 0.80 → **0.88**.
  - The verdict numbers are recomputed from stored traces with the final rule. A first rule that used feedback-only words gave 0.57 / 0.62 and was dropped as too noisy.

**Scope.**
- Data: MedScope **dev** split, the 20 source cases under valid / false / authority-only feedback (60 examples, 294 claims). The test split is untouched.
- Conditions A (verified edit) and B (unverified feedback + evidence).
- Systems: evidence-aware prompt, single-prompt scope-first, scope-first pipeline.
- Models: gpt-oss-120b (low reasoning) and Qwen3.8-27B (reasoning off), via Groq's free tier. Judge: gemini-3.5-flash-lite.
- 95% CIs by bootstrap over the 20 source cases.
- Tables: `results/RESULTS_medscope.md`. Error audit: `results/ERROR_AUDIT.md`.

**Complete** for v0 of the pipeline. Pipeline v1 (26 Oct) needs one more daily run per model (align calls are cached).

**Caveats:**
- This is a pilot on dev. The authored clinical content is unreviewed, and labels have one annotator.
- Only 3 depth-2 P claims fall in dev, so depth effects can only be tested on the test split.

## Headline findings

1. **With a bare verified edit, models apply the edit literally, and that's wording, not verification.**
   - For the evidence-aware prompt, P change recall is higher under B (unverified feedback + evidence) than under A (bare verified edit): gpt-oss **+0.18** [0.08, 0.29]; Qwen **+0.67** [0.48, 0.83].
   - Condition E (the verified edit plus "also update every statement inferred from a corrected one") closes the gap: **E − A = +0.72** [0.57, 0.86], and **B − E = −0.05** [−0.21, 0.09] on P recall (Qwen).
   - So the A-vs-B gap in the first write-up was the instruction's wording. Benchmarks that hand models bare verified edits measure literal application as much as propagation.
   - **With wording controlled, the cost of *unverified* feedback shows up as sycophancy:** B − E on preservation of evidence-supported claims is **+0.15** [0.00, 0.30] (4/20 vs. 1/20 supported claims changed). This is the defensible H1 result.
   - Structured systems: A and B do not differ on P recall.
2. **Claim-level sycophancy is measurable and method-dependent.** In the false condition, the evidence-aware prompt changes **15%** (gpt-oss) and **20%** [5, 40] (Qwen) of the evidence-supported claims the feedback attacks (v0.2 numbers). Its preservation error on K rises from 0.02 (valid) to 0.10 [0.04, 0.17] (false). The pipeline changes **0%** of those supported claims, and its preservation error is 0.02 under both valid and false feedback.
3. **Free-text revision under-hedges.** Unresolved-F1 for the evidence-aware prompt is 0.15 (gpt-oss) and 0.05 (Qwen). Structured systems hedge far more (scope-first 0.62 / 0.44; pipeline Qwen 0.72 [0.50, 0.88]).
4. **The pipeline (v0) is the best Qwen system, but not the best gpt-oss system** (condition B). gpt-oss pipeline: exact 0.57 vs. 0.63 for single-prompt scope-first. gpt-oss often omits dependency links (38% of its errors, P recall 0.72), and its verdicts are skewed to "partial" (45/60, accuracy 0.25). **Pipeline v1** fixes both by rule: it checks every later claim without direct evidence, and decides the verdict from the labels of the disputed claims. The Qwen numbers:
   - interaction-exact 0.80 [0.68, 0.90], vs. 0.73 for single-prompt scope-first and 0.43 for the evidence-aware prompt;
   - P recall 1.00, verdict accuracy 0.80;
   - the one cost is D recall: 0.93 vs. 0.98–1.00.
   
   Judged from its text instead of its labels, exact is 0.68. The judge and the labels agree on 93% of claims; we report both.
5. **Propagation is harder only for free-text systems.** Evidence-aware prompt: D recall 0.98–1.00 vs. P 0.74–0.88. Structured systems: P ≈ D.

## Pre-registered hypotheses (dev pilot; final tests on the test split)

| | Prediction | Status on dev |
|---|---|---|
| H1 | B lowers P recall vs. A | **Not supported.** The A < B gap is a wording effect (condition E). With wording controlled, propagation is equal; the cost of unverified feedback is +0.15 sycophancy on supported claims. |
| H2 | P harder than D; worse at depth 2 | Supported for free-text; not for structured. Depth untestable on dev (n = 3). |
| H3 | False feedback raises collateral change on supported claims | Supported for the evidence-aware prompt (Qwen); weak for gpt-oss; absent for the pipeline. |
| H4 | Under-hedging; authority-only flips instead of hedging | Supported for free-text (U-F1 ≤ 0.15). The audit shows the pipeline treats some authority-only disputes as evidence (6 claims). |
| H5 | Pipeline lowers preservation error and forbidden additions without hurting D recall | Supported for Qwen (sycophancy 0.20 → 0.00, exact +0.35). For gpt-oss, v1 ties the single prompt (0.63) and is best on verdict (0.93) and P recall (0.95). D recall 0.93 for both. |

## What the error audit found (pipeline, Qwen, B)

- **77% of label errors are gold-P claims labelled D.** The action is still correct; the D-vs-P label is what's wrong. This is mainly a **dataset issue**: in about a third of gold-P claims (9/26 dev, 10/31 test), the authored new evidence states the corrected content outright (e.g. "12 weeks"). That makes those claims directly addressed, which is D by our own guide.
- **Fixed (MedScope v0.2, 25 Oct):** 11 evidence items rewritten so they correct only the error; dependents must now be inferred. The 9 remaining overlaps only name the corrected treatment itself. These results are from v0.1; the affected dev examples are re-run before the freeze.
- The other errors are 6 disputes treated as evidence, 3 errors inherited from a parent, and 3 missed contradictions.

## Sample size

- From the dev A/B and system pairs, the per-case differences have SD 0.37–0.47.
- With 20 test cases, the smallest detectable difference is about 0.23–0.29. The effects seen here (+0.37 to +0.60) are above that.
- To detect a 0.10 difference, the test split needs **about 110–170 cases**. **Done (27 Oct):** MedScope v0.3 has 134 test cases (154 total).

## Next (26 Oct)

- Re-run both models once (the pipeline is now v1; `scope_pipeline_v0` is the ablation).

## Earlier next steps

1. One more daily gpt-oss run (pipeline × B).
2. Run condition E (Qwen, evidence-aware prompt; ~120 calls):
   `CONDITIONS="E" SYSTEMS="evidence_prompt" FREE=1 MODEL=groq:qwen/qwen3.8-27b JUDGE=gemini:gemini-3.5-flash-lite bash scripts/run_v0.sh`
3. ~~Fix the evidence items that state P content~~: done (v0.2). Re-run the dev slice on v0.2 when convenient; unchanged examples come from the cache.
4. Judge calibration (`scripts/label_actions.py`); second annotator; full design on thasos.
