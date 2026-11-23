# IntExR-Scope — Protocol (DRAFT, to freeze on 18 Dec 2026)

Everything here is decided *before* test-set results are seen. Items marked **TBD** are filled from dev results or the agreement study, then the document is frozen and the code is tagged (`git tag protocol-v1`). After the freeze, any change must be listed in a "deviations" section with its reason.

## 1. Task and schema (v1)
- Task, labels (D / P / K / U with triggers), precedence, verdicts and conditions A–D are as in `docs/02_task_definition.md`.
- Example schema: as validated by `intexr/data.py::validate`. Gold claims are given (setting S1). End-to-end decomposition (S2) is out of scope for Paper 1.

## 2. Annotation
- Guide: `docs/04_annotation_guide.md` (v0.9 now; v1 after the agreement study).
- Agreement study:
  - 24 stratified MedScope examples (`annotation/medscope_annotate.html`), labelled by the first author and an independent annotator;
  - report Cohen's κ on D/P/K/U, dependency-set agreement, and verdict κ.
  - **Target κ ≥ 0.70.** If it falls below, revise the guide and re-label a fresh sample.
  - **Result (18 Nov):** second annotator (Difei Gu, PhD mentor) vs. the gold labels on all 24 items: label agreement 0.91, **Cohen's κ = 0.87** (113 claims; target ≥ 0.70 met); feedback-verdict κ = 0.94 (n = 24); exact dependency-set agreement 0.60. 9 of the 10 label disagreements are gold-P claims labelled D (a plan item that changes because its diagnosis changed, read as directly addressed), the same D/P boundary the dev error audit found; 1 is a superseding-case K labelled D. Guide change for v1: one sentence and an example on why a plan item that follows from a corrected diagnosis is P even when the evidence names the new diagnosis. Files: `annotation/returned/annotator_DG.*`.
- Clinical review:
  - a clinically trained reviewer checks every authored item (new evidence, false_support, target texts, forbidden additions);
  - cases judged wrong are **fixed or dropped before the freeze**; no test result may be looked at when deciding.
  - **Round 1 (23 Nov):** Dr. Pradhan (MD, OB/GYN) reviewed the 5 OB/GYN dev cases: 5 of 5 corrections confirmed; wording fixes in all 5, one plan reordered, one later-event change extended; 2 cases (ms-val-30 evidence, ms-val-333 flow) await her clarification. Log: `docs/13_clinical_review.md`.
  - **TBD:** reviewers for the other 149 cases; final number of cases changed or dropped.

## 3. Data and splits
- MedScope v1 = the cases that pass review, built by `scripts/build_medec_scope.py`. Current: v0.3 (154 cases, 941 examples, 4,525 claims; 20 dev / 134 test; the 47 v0.2 cases are unchanged); evidence items decide the erroneous claim only, so propagated claims must be inferred (rule added after the dev pilot). The source is MEDEC (CC BY 4.0); authored text is released under the same licence.
- Split by source case (`paperB/data/splits.json`, frozen 23 Oct 2026):
  - **dev** (20 cases) is used for prompts, pilot runs and error analysis;
  - **test** (134 cases as of v0.3; every case added after 23 Oct goes to test) is held out.
  - No prompt, rule or method change may follow from test outputs.
- Secondary sets:
  - EditPropBench-IX (verified edit vs. unverified feedback);
  - VitaminC-IX (U-evidence);
  - MEDEC-knowledge (evidence-free control).
  - Built by `scripts/convert_external.py` with fixed seeds.

## 4. Systems and settings
- Systems: no revision, always accept (lexical), always rewrite, dialogue, evidence-aware prompt, verify-then-revise (strong baseline), evidence gate (the same LLM used as a three-way NLI scorer, one call per example; a DeBERTa NLI classifier is supported by the code but not used), single-prompt scope-first, scope-first pipeline (+ no-prop, no-check ablations). Prompts are reproduced verbatim in the paper appendix (`scripts/make_paper_appendix.py`).
- Models: one or two per size tier, from `configs/model_tiers.tsv` (Difei, 27 Oct: "one for each model tier"; "large and small GPT, Claude, Qwen"). Temperature 0. All responses are cached and released.
  - 3–4B: Qwen3-4B, Llama-3.2-3B · 7–8B: Qwen3-8B, Llama-3.1-8B · 14B: Qwen3-14B (GPU server, vLLM).
  - 20–32B: gpt-oss-20b, Qwen3.8-27B (Groq free tier), Gemma-4-31B (Gemini free tier), Qwen3-32B-AWQ (GPU server).
  - 70B+: Llama-3.3-70B-AWQ (GPU server), gpt-oss-120b (Groq free tier).
  - Closed: Claude (small + large) and closed GPT (small + large), **only if** research credits are granted; test split only.
  - Run with `scripts/run_tiers.sh`; the scale table is the "By model scale" section of `results/RESULTS_medscope.md`.
  - **Dev status (23 Nov):** done for all nine open models above except Llama-3.2-3B and Llama-3.1-8B (gated on Hugging Face; optional, since 4B–117B is covered). The all-systems comparison (dialogue, always rewrite, evidence gate, verify-then-revise) was run on Qwen3-8B, Qwen3-32B-AWQ and Llama-3.3-70B-AWQ.
- **Test run plan (decided before the freeze).** The test slice is the 134 test cases × valid / false / authority-only = 402 examples (1,926 claims) per condition, about 7× dev.
  - **Primary models** (results the hypotheses are tested on): the GPU-server models, which have no rate limit: Qwen3-4B, Qwen3-8B, Qwen3-14B, Qwen3-32B-AWQ, Llama-3.3-70B-AWQ. Conditions A, B and E; all systems on Qwen3-8B, Qwen3-32B-AWQ and Llama-3.3-70B-AWQ, the three core systems (evidence-aware prompt, single-prompt scope-first, pipeline) on the others.
  - **Secondary models** (reported if they finish, never used to choose anything): gpt-oss-20b, gpt-oss-120b, Qwen3.8-27B (Groq) and Gemma-4-31B (Gemini). At the free-tier caps seen on dev (about 120 calls a day for gpt-oss-120b; repeated 503 errors on Gemini), one model needs roughly 3–4 weeks for the core systems on test, so they run in parallel and are reported as they complete.
  - Each primary model × system × condition is run once; no reruns except to complete examples that failed with an API error (identical prompts, served from the cache).
- Human review is done per tier, not per model: the model marked `review=1` in each tier (5 open tiers + closed) supplies the judge-calibration and error-audit samples (`label_actions.py sample --reps-only`).
- Judge: **Qwen3-32B-AWQ, served locally with vLLM (GPUs 6–7 on thasos, thinking off), fixed for every model and both splits**, with the prompt in the appendix. It replaced gemini-3.5-flash-lite (used for the first two pilot runs) because the Gemini free tier allows only 500 judge calls a day. The two earlier runs were re-scored with it (`scripts/rejudge.py`); on the 2,646 claims scored by both, the judges agree on 0.96 of claim actions and differ on keep vs. change for under 0.3%.
  - Calibration: 120 (claim, revision) pairs, stratified over the review=1 models, systems and gold labels, labelled by the first author blind to the judge (`annotation/actions_sheet.csv`, `scripts/label_actions.py`).
  - **Target κ ≥ 0.75.** If it falls below, switch the judge and re-judge from the cache.
  - **TBD:** κ, confusion matrix.

## 5. Hypotheses and primary analyses
Pre-registered in the paper (§5): H1 cost of verification, H2 propagation harder and depth, H3 claim-level sycophancy, H4 under-hedging, H5 method.

| Hypothesis | Primary metric | Comparison | Test |
|---|---|---|---|
| H1 | change recall on P; interaction-exact | B − A, same claims, per system | paired case-level bootstrap 95% CI excludes 0 |
| H2 | change recall P vs. D; P at depth 1 vs. 2+ | within system, condition B | case-level bootstrap CI of the difference |
| H3 | preservation error on K⁺ | false vs. valid condition | case-level bootstrap CI of the difference |
| H4 | U-F1; share of U-feedback claims flipped | authority-only condition | descriptive, with CI |
| H5 | preservation error K, forbidden additions, change recall D | pipeline vs. evidence-aware prompt and vs. verify-then-revise | paired case-level bootstrap |

- Condition E (verified edit + "also update what depends on it") is the wording control for H1. On dev, the A/B gap in P recall came from the wording of bare verified edits (E − A = +0.72; B ≈ E), so H1 is reported as both B − A and B − E; with wording controlled, the effect of unverified feedback is tested on preservation error K⁺ (B − E).
- Intervals: 95% percentile bootstrap, 2,000 resamples of source cases (`intexr/metrics.py`).
- Five hypotheses → we report all of them and correct with Holm's method across the five primary comparisons.
- Null results are reported as null.

## 6. Sample size
- From the dev pilot (`docs/11_results_v0.md`), the per-case B − A differences have SD 0.37–0.47.
- With 20 test cases, the smallest detectable difference is about 0.23–0.29. Detecting 0.10 needs about **110–170 source cases** (α = 0.05, power 0.8; `scripts/sample_size.py`).
- **Decision (27 Oct):** grow to 154 cases (MedScope v0.3: 20 dev / 134 test), which meets the 110–170 target and matches the scale of RevPropBench (150 items).
  - Cases that fail clinical review are dropped; we report the minimum detectable difference for the final test size.
  - The headline effects seen on dev (+0.37 to +0.60) are detectable at any of these sizes.

## 7. Release
- Code (harness, systems, metrics, builders), MedScope v1 (MEDEC-derived, CC BY 4.0), splits, annotation guide, agreement data, judge calibration labels, all model outputs.
- Converted sets are released where their licences allow (EditPropBench CC BY 4.0, VitaminC CC BY-SA 3.0).
- IU X-ray: identifiers and scripts only (CC BY-NC-ND). No MIMIC data.

## 8. Deviations after freeze
(none yet)
