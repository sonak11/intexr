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
  - **TBD:** κ values, guide changes.
- Clinical review:
  - a clinically trained reviewer checks every authored item (new evidence, false_support, target texts, forbidden additions);
  - cases judged wrong are **fixed or dropped before the freeze**; no test result may be looked at when deciding.
  - **TBD:** reviewer, number of cases changed or dropped.

## 3. Data and splits
- MedScope v1 = the cases that pass review, built by `scripts/build_medec_scope.py`. Current: v0.2 (47 cases, 293 examples); evidence items decide the erroneous claim only, so propagated claims must be inferred (rule added after the dev pilot). The source is MEDEC (CC BY 4.0); authored text is released under the same licence.
- Split by source case (`paperB/data/splits.json`, frozen 23 Oct 2026):
  - **dev** (20 cases) is used for prompts, pilot runs and error analysis;
  - **test** (20 cases + any new cases) is held out.
  - No prompt, rule or method change may follow from test outputs.
- Secondary sets:
  - EditPropBench-IX (verified edit vs. unverified feedback);
  - VitaminC-IX (U-evidence);
  - MEDEC-knowledge (evidence-free control).
  - Built by `scripts/convert_external.py` with fixed seeds.

## 4. Systems and settings
- Systems: no revision, always accept (lexical), always rewrite, dialogue, evidence-aware prompt, verify-then-revise (strong baseline), evidence gate (NLI), single-prompt scope-first, scope-first pipeline (+ no-prop, no-check ablations). Prompts are reproduced verbatim in the paper appendix (`scripts/make_paper_appendix.py`).
- Models: gpt-oss-120b and Qwen3.8-27B (free API tier); self-hosted open-weight models on the GPU server (**TBD:** final list). Temperature 0. All responses are cached and released.
- Judge: gemini-3.5-flash-lite, fixed, with the prompt in the appendix.
  - Calibration: 100 stratified (claim, revision) pairs labelled by the first author (`scripts/label_actions.py`).
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

- Intervals: 95% percentile bootstrap, 2,000 resamples of source cases (`intexr/metrics.py`).
- Five hypotheses → we report all of them and correct with Holm's method across the five primary comparisons.
- Null results are reported as null.

## 6. Sample size
- From the dev pilot (`docs/11_results_v0.md`), the per-case B − A differences have SD 0.37–0.47.
- With 20 test cases, the smallest detectable difference is about 0.23–0.29. Detecting 0.10 needs about **110–170 source cases** (α = 0.05, power 0.8; `scripts/sample_size.py`).
- **Decision:**
  - grow the test split to at least 60 cases before the freeze if review capacity allows, reporting the minimum detectable difference that results;
  - the headline effects seen on dev (+0.37 to +0.60) are detectable at the current size;
  - the test split has 27 cases as of 25 Oct (v0.2 + batch 4).

## 7. Release
- Code (harness, systems, metrics, builders), MedScope v1 (MEDEC-derived, CC BY 4.0), splits, annotation guide, agreement data, judge calibration labels, all model outputs.
- Converted sets are released where their licences allow (EditPropBench CC BY 4.0, VitaminC CC BY-SA 3.0).
- IU X-ray: identifiers and scripts only (CC BY-NC-ND). No MIMIC data.

## 8. Deviations after freeze
(none yet)
