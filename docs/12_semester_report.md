---
title: "IntExR-Scope: Fall 2026 pilot report"
subtitle: "Revising clinical answers under feedback of unknown validity"
author: "Sonakshi Sharma · advisor Prof. Metaxas · mentor Difei Gu"
date: "23 November 2026"
---

# Summary

- **Task.** A model has written a clinical answer made of claims. It then receives feedback that may be right, wrong or unsupported, plus some evidence. It must change the claims the evidence overturns (D), change the claims that depended on them (P), keep the rest (K), and hedge the claims that no evidence settles (U).
- **Benchmark.** MedScope v0.3, built from MEDEC: 154 source cases, 941 examples, 4,525 labelled claims. It is split by case into 20 dev cases and 134 held-out test cases. A second annotator agrees with the gold labels at Cohen's κ = 0.87.
- **Main finding (dev, 9 open models from 4B to 117B).** Existing correction methods become sycophantic when a correction is not verified. Verify-then-revise is near-perfect on a verified edit, but it changes 55–70% of the evidence-supported claims that false feedback attacks (paired rise +0.50 to +0.70, every interval excludes 0).
- **Method.** Our scope-first pipeline (align → label by rule → revise → splice → check) brings this to 0–10% for every model of 27B and up, across four model families. It helps less at 14–21B and fails at 4–8B.
- **Weak spots.** The pipeline still mishandles a third to half of the claims it should hedge. The analysis below shows this is three separate problems: some gold labels for authority-only feedback are debatable, dependency links are missed, and one model's output is often not valid JSON. Each has a fix planned before the test run.
- **Cost.** All work so far cost $0: free API tiers and the department's GPU server (thasos).

# 1. What was built this semester

| Item | Status |
|---|---|
| Task definition, labels D / P / K / U, annotation guide v0.9 | done (`docs/02`, `docs/04`) |
| MedScope v0.3: 154 cases, 941 examples, 4,525 claims; dev/test split by case, frozen 23 Oct | done |
| Systems: 4 prompting baselines, verify-then-revise, an evidence gate, scope-first (1 prompt) and the pipeline (v1, plus v0 as ablation) | done |
| Scale study: 9 open models, 4B–117B, families Qwen, Llama, Gemma, gpt-oss | done on dev (two small Llama models need a Hugging Face token; optional) |
| One fixed judge for all runs: Qwen3-32B-AWQ, run locally | done; agrees with the earlier Gemini judge on 96% of 2,646 claims |
| Second annotator (Difei Gu), 24 examples, 113 claims | done: label κ 0.87, verdict κ 0.94 |
| Paper 1 draft (ACL format), protocol draft, results dashboard and tables | in progress, about 60% |

# 2. Main results (dev split, condition B unless marked)

Syc = share of the 20 evidence-supported claims that false feedback attacks which the system changed anyway; lower is better. Exact = share of the 60 examples in which every claim is handled correctly. Brackets are 95% intervals from resampling source cases.

**Table 1. Scale study: evidence-aware prompt vs. scope-first pipeline.**

| Model | Params | A: propagation (prompt) | Syc, prompt | Syc, pipeline | Exact, prompt | Exact, pipeline | U-F1, pipeline |
|---|---|---|---|---|---|---|---|
| Qwen3-4B | 4B | 0.12 | 0.10 [0.00, 0.25] | 0.65 [0.45, 0.85] | 0.25 | 0.18 | 0.50 |
| Qwen3-8B | 8B | 0.32 | 0.30 [0.10, 0.50] | 0.30 [0.10, 0.50] | 0.25 | 0.32 | 0.68 |
| Qwen3-14B | 14B | 0.28 | 0.35 [0.15, 0.55] | 0.15 [0.00, 0.30] | 0.40 | 0.38 | 0.69 |
| gpt-oss-20b | 21B | 0.68 | 0.50 [0.30, 0.70] | 0.10 [0.00, 0.25] | 0.18 | 0.37 | 0.49 |
| Qwen3.8-27B | 27B | 0.04 | 0.45 [0.25, 0.65] | 0.00 [0.00, 0.00] | 0.32 | 0.80 | 0.72 |
| Gemma-4-31B | 31B | 1.00 | 0.15 [0.00, 0.30] | 0.00 [0.00, 0.00] | 0.68 | 0.65 | 0.47 |
| Qwen3-32B (AWQ) | 32B | 0.05 | 0.35 [0.15, 0.55] | 0.10 [0.00, 0.25] | 0.22 | 0.52 | 0.62 |
| Llama-3.3-70B (AWQ) | 70B | 0.95 | 0.75 [0.55, 0.95] | 0.05 [0.00, 0.15] | 0.32 | 0.55 | 0.85 |
| gpt-oss-120b | 117B | 0.63 | 0.15 [0.00, 0.30] | 0.05 [0.00, 0.15] | 0.50 | 0.63 | 0.73 |

**Table 2. All systems on three models.** Syc under a verified edit (A) and under unverified feedback (B), and exact accuracy under B.

| System | Qwen3-8B: Syc A → B | Qwen3-32B: Syc A → B | Llama-70B: Syc A → B | Qwen3-8B: Exact | Qwen3-32B: Exact | Llama-70B: Exact |
|---|---|---|---|---|---|---|
| Dialogue | 0.40 → 0.60 | 0.25 → 0.50 | 0.40 → 0.50 | 0.25 | 0.33 | 0.22 |
| Always rewrite | 0.20 → 0.50 | 0.25 → 0.60 | 0.20 → 0.60 | 0.30 | 0.20 | 0.23 |
| Evidence-aware prompt | 0.05 → 0.30 | 0.00 → 0.35 | 0.25 → 0.75 | 0.25 | 0.22 | 0.32 |
| Evidence gate | 0.30 → 0.05 | 0.00 → 0.00 | 0.00 → 0.00 | 0.12 | 0.17 | 0.18 |
| Verify-then-revise | 0.00 → 0.70 | 0.05 → 0.55 | 0.10 → 0.65 | 0.37 | 0.40 | 0.25 |
| Scope-first (1 prompt) | 0.00 → 0.80 | 0.10 → 0.65 | 0.05 → 0.55 | 0.22 | 0.43 | 0.43 |
| **Scope-first pipeline** | 0.00 → 0.30 | 0.00 → 0.10 | 0.00 → 0.05 | 0.32 | 0.52 | 0.55 |

What the tables show:

1. **Sycophancy appears at every size and does not shrink with scale.** With the plain evidence-aware prompt, models change 10–75% of attacked, evidence-supported claims. The largest model, Llama-70B, changes the most.
2. **The strongest existing method collapses when the correction is not verified.** Verify-then-revise goes from 0.00–0.10 to 0.55–0.70; the paired rise is +0.70 [0.50, 0.90], +0.50 [0.30, 0.70] and +0.55 [0.30, 0.80].
3. **The pipeline fixes this for models of 27B and up** (Syc 0.00–0.10), and has the best exact accuracy among the systems in Table 2 for the two larger models. The evidence gate is the only other system with low Syc, but it cannot propagate, so it has the lowest exact accuracy.
4. **Applying a bare verified edit literally is a family trait, not a size effect.** Under condition A, Qwen models propagate a verified edit to only 4–32% of dependent claims, gpt-oss to 63–68%, and Llama and Gemma to 95–100%. A wording control (condition E: "also update what depends on it") shows this gap is about wording.

# 3. Where the pipeline still fails

Per-claim analysis of every model's pipeline output under condition B (`scripts/pipeline_failures.py`, `scripts/error_audit.py`).

**Most "label errors" do not matter.** Most wrong labels are dependent claims (P) labelled as directly addressed (D). Both labels mean "change it", so the claim is still handled correctly. For example, gpt-oss-120b has 35 such swaps but only 30 claims with a wrong action out of 294. The same D/P boundary accounts for 9 of the 10 disagreements between the second annotator and the gold labels, so the guide will add one sentence and an example on it.

**Hedging (gold-U claims, 37 per model).** Cells are hedged / kept / changed.

| Model | All U | U from feedback (n=16) | U from dependency (n=21) | Non-U claims hedged |
|---|---|---|---|---|
| Qwen3-4B | 22 / 12 / 3 | 12 / 1 / 3 | 10 / 11 / 0 | 29 |
| Qwen3-8B | 22 / 7 / 8 | 11 / 0 / 5 | 11 / 7 / 3 | 6 |
| Qwen3-14B | 26 / 8 / 3 | 12 / 2 / 2 | 14 / 6 / 1 | 12 |
| gpt-oss-20b | 16 / 8 / 13 | 9 / 1 / 6 | 7 / 7 / 7 | 12 |
| Qwen3.8-27B | 22 / 1 / 14 | 10 / 0 / 6 | 12 / 1 / 8 | 2 |
| Gemma-4-31B | 12 / 16 / 9 | 5 / 7 / 4 | 7 / 9 / 5 | 2 |
| Qwen3-32B | 17 / 3 / 17 | 8 / 0 / 8 | 9 / 3 / 9 | 1 |
| Llama-3.3-70B | 37 / 0 / 0 | 16 / 0 / 0 | 21 / 0 / 0 | 13 |
| gpt-oss-120b | 24 / 11 / 2 | 15 / 0 / 1 | 9 / 11 / 1 | 5 |

Four separate causes:

1. **Authority-only feedback on an error the case text already exposes (a data issue).** In this cell, a senior clinician disputes a claim and no new evidence is given, so the gold label is U. But the disputed claim is the original MEDEC error, and sometimes the case text plus medical knowledge already refutes it. In ms-val-50, ring-enhancing lesions with CD4 under 100 point to toxoplasmosis, not HIV encephalopathy; 7 of 9 models change the claim. In ms-val-303, a beta-blocker overdose calls for glucagon, not pralidoxime; 6 of 9 change it. Those models are arguably right. Across all 16 such claims, most models hedge 13. **Action:** the clinical review decides, case by case, whether the case text settles the claim. If it does, the claim becomes D or the case is replaced.
2. **Missed dependencies (a model problem, partly a data one).** Dependent claims are kept instead of hedged because the model does not link them to the disputed claim. Examples: "Recheck INR after each FFP unit" depends on "reverse with FFP" (ms-val-197); "Reassess in one week" depends on "warm sitz baths" (ms-val-185). This is also the weakest part of the gold: exact dependency-set agreement with the second annotator is 0.60. **Action:** the guide states when a monitoring or follow-up item depends on a treatment; the clinical review checks dependency links.
3. **Disputes treated as evidence (Qwen3.8-27B and Qwen3-32B).** These models label the disputed claim D and rewrite it; their dependents are then changed too. That is a third to half of their U claims (14 of 37 and 17 of 37). Together with cause 1, this is the main reason their U-F1 is 0.62–0.72 and not higher.
4. **Malformed output (Gemma).** 20 of Gemma's 60 pipeline examples had a step (align, revise or check) whose JSON output could not be parsed: mostly text after the JSON object, or single-quoted keys. When that happens nothing is revised. 13 of the 16 U claims Gemma kept unchanged come from those examples. **Action:** parse the first JSON object and tolerate trailing text, then re-run on dev only. This is a format fix, not a change to the method.

**Over-hedging.** Llama-70B hedges every U claim (U-F1 0.85), but it also hedges 13 claims that should be kept or changed, and leaves 18 dependent claims unchanged. Qwen3-4B hedges 29 claims that are not U. High U recall alone is therefore not the goal; the paper reports U-F1 and the D/P/K errors together.

**Remaining sycophancy (pipeline).** From 27B up, at most 2 of 20 attacked claims are changed. Below 27B, the Qwen models mostly mislabel the attacked claim as D: the align step reads the false feedback as a contradiction (4B: 12 of 13 changed claims).

# 4. Reliability

| Check | Value | Based on |
|---|---|---|
| Second annotator vs. gold, claim labels | κ 0.87 (agreement 0.91) | 113 claims, 24 examples |
| Second annotator vs. gold, feedback verdict | κ 0.94 | 24 examples |
| Exact dependency sets | 0.60 | 113 claims |
| Local judge vs. Gemini judge, claim actions | 0.96 | 2,646 claims |
| Judge vs. first author (calibration, target κ ≥ 0.75) | pending | 120 pairs, sheet ready |

# 5. Before the test run (protocol freeze planned for 18 December)

1. **Clinical review** of the authored items, including the authority-only cases and dependency links flagged in Section 3. Cases judged wrong are fixed or dropped without looking at any test result.
2. **Judge calibration:** the first author labels the 120-pair sheet (target κ ≥ 0.75; otherwise switch judge and re-score from the cache).
3. **Guide v1:** add the D/P rule and the dependency rule for monitoring items.
4. **Tolerant JSON parsing** in the pipeline; re-run dev only.
5. **Freeze** `docs/10_frozen_protocol.md` and tag `protocol-v1`.
6. **Test run:** 402 examples per condition (134 cases × valid / false / authority-only), conditions A, B and E.
    - Primary models run on thasos: Qwen3-4B, 8B, 14B, 32B and Llama-70B.
    - The API models (gpt-oss-20b/120b, Qwen3.8-27B, Gemma) are secondary, because the free tiers allow only about one model every 3–4 weeks.
7. **Cost (measured, condition B, models on thasos).**

    | System | Model calls | Tokens per example | Seconds per example |
    |---|---|---|---|
    | Evidence-aware prompt | 1 | about 600 | 3–7 |
    | Single-prompt scope-first | 1 | about 1,300 | 14–18 |
    | Verify-then-revise | 2 | about 1,800 | 19–23 |
    | Scope-first pipeline | 2.0–2.1 | about 1,900 | 13–19 |

    The pipeline costs about three times the plain prompt and about the same as verify-then-revise, and is faster than verify-then-revise on the same GPU because it rewrites only the claims that change. Scoring a free-text output adds one judge call of about 450 tokens.

# 6. Questions for Prof. Metaxas

1. Is building on MEDEC (CC BY 4.0) acceptable for the benchmark release, or is a second data source needed?
2. Target venue and timeline for Paper 1, and for the separate dataset paper.
3. Author list: Difei Gu and Prof. Metaxas, and the clinical reviewer if they agree?
4. Can the lab support a small research-credit request for Claude and closed GPT models? These would run on the test split only.

*Note: example ids such as `ms-test-97` come from MEDEC's own file names. All of them are in our dev split.*
