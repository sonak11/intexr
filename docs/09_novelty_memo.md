# IntExR-Scope — Novelty Memo (31 Oct 2026 review)

*Sonakshi Sharma. 25 Oct 2026. Results are a pilot on the dev split; see `docs/11_results_v0.md`.*

## 1. Claim

When a user corrects a multi-claim response, three judgments are needed:
- **whether** the correction is right (feedback is a hypothesis to check against evidence);
- **which** claims the evidence changes directly (D);
- **which** claims change only because something they were inferred from changed (P).

All of this must happen while every other claim is kept (K), and claims the evidence cannot settle are hedged rather than flipped (U).

**IntExR-Scope is the first benchmark that scores this partition when the validity of the feedback is unknown.** Its central measurement is the *cost of verification*: the drop in scope and propagation accuracy between a verified edit (condition A) and the same correction given as unverified feedback plus evidence (condition B), on identical claims.

## 2. Closest work and the gap (literature matrix: 59 papers, 39 verified on the web)

| Thread | Closest papers | What they have | What they lack |
|---|---|---|---|
| Edit propagation | EditPropBench (Kruthof 2026), RevPropBench (Kikuta, EMNLP-Ind 2026), LEDGER (Findings ACL 2026) | direct / cascade / protected labels; the best editors miss ~30% of cascade updates | **the edit is always correct**; no unresolved label; ambiguous cases excluded (RevPropBench) |
| Sycophancy / persuasion | Sharma et al. 2024, SycEval 2025, PBT (NAACL 2025), Med-Stress (ACL 2026), *Sycophancy Suppression Can Impair Rational Updating* (2026) | feedback can be wrong; resisting bad and accepting good feedback trade off | **one decision per answer**; cannot see feedback that is right about one claim and wrong about another |
| Evidence-based revision | FRUIT, RARR, FAVA, MEDEC, CorBenchX | evidence-driven correction, sometimes preservation | evidence treated as the oracle; one error per text; dependents not labelled |
| Belief revision | AGM, Katsuno–Mendelzon, TMS, Belief-R | the theory: minimal change, revision vs. update, dependency retraction | synthetic logic, not natural-language responses with evidence |

**No paper has both propagation and unreliable feedback** (matrix §10). A fresh search on 23 Oct for 2026 work found no paper combining them. The newest neighbour (row 56) argues that anti-sycophancy is a *selectivity* problem at the answer level. IntExR-Scope measures selectivity per claim.

## 3. What is new, concretely

1. **The partition under unknown validity.** Labels are defined by evidence, not by the request. This produces cases neither propagation benchmark can express:
   - correct feedback with no evidence → **U**, not D;
   - wrong feedback about a claim the evidence overturns anyway → **D**;
   - partial feedback → D on some claims and a forbidden addition on others;
   - false feedback attacking a claim the evidence supports → **K⁺**, and changing it is measurable sycophancy.
2. **An unresolved label that propagates** (U-dependency), with a precedence rule that makes every label decidable. The rule is executable: with gold alignments, our pipeline reproduces every MedScope gold label.
3. **Real clinical inference chains.** MEDEC notes with expert-injected errors, extended to error → treatment → monitoring chains (59 P claims at depth 2). Temporal *superseding* cases separate revision from update (Katsuno–Mendelzon).
4. **A paired design.** Eight feedback conditions over the *same* response and claims (valid, false, partial, authority-only, vague, outdated, superseding, conflicting evidence). Condition A reproduces the EditPropBench/RevPropBench setting on the same claims, so the difference is measured, not argued.

## 4. Evidence so far

**Offline (MedScope v0.1, 248 examples, CIs by bootstrap over 40 source cases):**
- A system that "accepts" feedback by keyword overlap changes **72% [57–85]** of the evidence-supported claims that false feedback attacks. The false condition does measure claim-level deference.
- Its change recall falls from **0.40 on D to 0.17 on P, and 0.10 at depth 2**. Following the feedback's surface finds direct targets but not their consequences.
- The gold oracle scores 1.0, and the deterministic label rules reproduce every gold label.

**First model runs** ($0; MedScope dev split, 20 cases × valid / false / authority-only feedback, 60 examples):
- Models: gpt-oss-120b and Qwen3.8-27B (Groq free tier); judge gemini-3.5-flash-lite.

Findings:
- **Given a bare verified edit, models apply it literally and leave the dependent claims stale.** P recall is higher under unverified feedback + evidence than under the bare verified edit: +0.18 (gpt-oss), +0.67 (Qwen).
  - A wording control (condition E: the verified edit + "also update what depends on it") shows this is the instruction's wording: E − A = +0.72; B ≈ E.
  - So propagation benchmarks built on bare verified edits measure literal application as much as propagation.
  - With wording controlled, **the cost of unverified feedback is sycophancy**: +0.15 [0.00, 0.30] more evidence-supported claims changed.
- **Claim-level sycophancy is measurable.** Under false feedback, the evidence-aware prompt changes **15–20%** of the evidence-supported claims the feedback attacks. Our scope-first pipeline changes **0%** (Qwen).
- **Free-text revision under-hedges:** unresolved-F1 is 0.05–0.15, vs. 0.72 for the pipeline.
- **The pipeline is best with Qwen** (exact 0.80 vs. 0.45), but not yet with gpt-oss (0.57 vs. 0.63), where the model omits dependency links. Pipeline v1 fixes that by rule; re-runs are pending.

What the pilot also showed:
- In about a third of propagated claims, the authored evidence states the corrected content outright, which blurs D vs. P. Fixed in MedScope v0.2: 11 evidence items rewritten.
- Detecting 0.10 effects on the test split needs about 110–170 cases. MedScope should grow to ~100+ cases.

## 5. Risks and how the design answers them

| Risk | Answer |
|---|---|
| "This is EditPropBench plus a sycophancy test." | Partly answered. Propagation under verified edits depends on the instruction's wording (bare edits are applied literally). Once that is controlled, unverified feedback adds a measurable claim-level sycophancy cost on the same claims, plus the U label and its propagation. Neither benchmark alone shows either. |
| LLM-authored clinical content | All authored text is flagged unreviewed. A clinically trained reviewer pass and a second annotator (Cohen's κ) come before release; cases that fail are dropped. |
| Small benchmark (47 cases; 20 dev / 27 test) | CIs are computed over source cases, not claims. A radiology split (IU X-ray build script) and more MEDEC cases are planned; EditPropBench-IX gives a second domain. |
| Judge validity | 100 hand-labelled (claim, revision) pairs; target κ ≥ 0.75; switch judges if it falls short. |
| Plan-then-edit hurt propagation on EditPropBench | The `no-prop` ablation isolates our propagation check; we will report it either way. |

## 6. Decision requested

Keep the framing: **feedback is a hypothesis; evidence is the arbiter**. Lead with claim-level sycophancy and unresolved handling under unverified feedback, measured against a wording-controlled verified-edit baseline (condition E). Report the bare-edit literalness as a methodological finding for propagation benchmarks. Grow MedScope to ~100+ cases before the final test.
