# First model results (v0, free-tier dev slice), 25 Oct 2026

**Scope.**
- Data: MedScope **dev** split, the 20 source cases under valid / false / authority-only feedback (60 examples, 294 claims). The test split is untouched.
- Conditions A (verified edit) and B (unverified feedback + evidence).
- Systems: evidence-aware prompt, single-prompt scope-first, scope-first pipeline.
- Models: gpt-oss-120b (low reasoning) and Qwen3.8-27B (reasoning off), via Groq's free tier. Judge: gemini-3.5-flash-lite.
- 95% CIs by bootstrap over the 20 source cases.
- Tables: `results/RESULTS_medscope.md`. Error audit: `results/ERROR_AUDIT.md`.

**Missing:** gpt-oss-120b × scope-first pipeline × condition B (the run stopped at the daily cap; one more daily run).

**Caveats:**
- This is a pilot on dev. The authored clinical content is unreviewed, and labels have one annotator.
- Only 3 depth-2 P claims fall in dev, so depth effects can only be tested on the test split.

## Headline findings

1. **Verified edits make free-text revision *more literal*, not less.** For the evidence-aware prompt, change recall on propagated claims is **higher** under unverified feedback + evidence than under a verified edit:
   - gpt-oss: B − A = **+0.18** [0.08, 0.29];
   - Qwen: **+0.60** [0.40, 0.77].
   
   Given an explicit list of correct edits, models apply the list and leave dependent claims stale. For example, after the diagnosis is corrected to frontotemporal dementia, "death within a year" and the CJD work-up stay. With evidence and unverified feedback they reason about the case and fix dependents: 34 P claims changed under B but not A, versus 1 the other way (Qwen).
   - This is the EditPropBench failure mode, reproduced, and it is the **opposite of H1** as pre-registered.
   - It could be a wording effect ("apply these"). **Condition E** (the verified edit plus "also update what depends on it") is implemented to test that.
   - For the structured systems, A and B do not differ on P recall (scope-first gpt-oss −0.04 [−0.09, 0.00]; Qwen 0.00; pipeline Qwen 0.00).
2. **Claim-level sycophancy is measurable and method-dependent.** In the false condition, the evidence-aware prompt (Qwen) changes **25%** of the evidence-supported claims the feedback attacks [10, 45]. Its preservation error on K rises from 0.02 (valid) to 0.10 [0.04, 0.17] (false). The pipeline changes **0%** of those supported claims, and its preservation error is 0.02 under both valid and false feedback.
3. **Free-text revision under-hedges.** Unresolved-F1 for the evidence-aware prompt is 0.15 (gpt-oss) and 0.05 (Qwen). Structured systems hedge far more (scope-first 0.62 / 0.44; pipeline Qwen 0.72 [0.50, 0.88]).
4. **The pipeline is the best Qwen system** (condition B):
   - interaction-exact 0.80 [0.68, 0.90], vs. 0.73 for single-prompt scope-first and 0.43 for the evidence-aware prompt;
   - P recall 1.00, verdict accuracy 0.80;
   - the one cost is D recall: 0.93 vs. 0.98–1.00.
   
   Judged from its text instead of its labels, exact is 0.68. The judge and the labels agree on 93% of claims; we report both.
5. **Propagation is harder only for free-text systems.** Evidence-aware prompt: D recall 0.98–1.00 vs. P 0.74–0.88. Structured systems: P ≈ D.

## Pre-registered hypotheses (dev pilot; final tests on the test split)

| | Prediction | Status on dev |
|---|---|---|
| H1 | B lowers P recall vs. A | **Not supported, reversed** for free-text (A is *worse*); null for structured. Condition E decides whether this is wording. |
| H2 | P harder than D; worse at depth 2 | Supported for free-text; not for structured. Depth untestable on dev (n = 3). |
| H3 | False feedback raises collateral change on supported claims | Supported for the evidence-aware prompt (Qwen); weak for gpt-oss; absent for the pipeline. |
| H4 | Under-hedging; authority-only flips instead of hedging | Supported for free-text (U-F1 ≤ 0.15). The audit shows the pipeline treats some authority-only disputes as evidence (6 claims). |
| H5 | Pipeline lowers preservation error and forbidden additions without hurting D recall | Mostly supported for Qwen (sycophancy 0.25 → 0.00, exact +0.37); D recall slightly lower (0.93). gpt-oss pending. |

## What the error audit found (pipeline, Qwen, B)

- **77% of label errors are gold-P claims labelled D.** The action is still correct; the D-vs-P label is what's wrong. This is mainly a **dataset issue**: in about a third of gold-P claims (9/26 dev, 10/31 test), the authored new evidence states the corrected content outright (e.g. "12 weeks"). That makes those claims directly addressed, which is D by our own guide.
- **Fixed (MedScope v0.2, 25 Oct):** 11 evidence items rewritten so they correct only the error; dependents must now be inferred. The 9 remaining overlaps only name the corrected treatment itself. These results are from v0.1; the affected dev examples are re-run before the freeze.
- The other errors are 6 disputes treated as evidence, 3 errors inherited from a parent, and 3 missed contradictions.

## Sample size

- From the dev A/B and system pairs, the per-case differences have SD 0.37–0.47.
- With 20 test cases, the smallest detectable difference is about 0.23–0.29. The effects seen here (+0.37 to +0.60) are above that.
- To detect a 0.10 difference, the test split needs **about 110–170 cases**. That argues for growing MedScope to ~100+ cases before the final experiments.

## Next

1. One more daily gpt-oss run (pipeline × B).
2. Run condition E (Qwen, evidence-aware prompt; ~120 calls):
   `CONDITIONS="E" SYSTEMS="evidence_prompt" FREE=1 MODEL=groq:qwen/qwen3.8-27b JUDGE=gemini:gemini-3.5-flash-lite bash scripts/run_v0.sh`
3. ~~Fix the evidence items that state P content~~: done (v0.2). Re-run the dev slice on v0.2 when convenient; unchanged examples come from the cache.
4. Judge calibration (`scripts/label_actions.py`); second annotator; full design on thasos.
