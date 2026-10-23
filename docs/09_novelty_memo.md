# IntExR-Scope — Novelty Memo (31 Oct 2026 review)

*Sonakshi Sharma. Draft of 23 Oct 2026; section 4 is filled in when the free-tier runs finish.*

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
2. **An unresolved label that propagates** (U-dependency), with a precedence rule that makes every label decidable. The rule is executable: with gold alignments, our pipeline reproduces all 1,186 MedScope gold labels.
3. **Real clinical inference chains.** MEDEC notes with expert-injected errors, extended to error → treatment → monitoring chains (59 P claims at depth 2). Temporal *superseding* cases separate revision from update (Katsuno–Mendelzon).
4. **A paired design.** Eight feedback conditions over the *same* response and claims (valid, false, partial, authority-only, vague, outdated, superseding, conflicting evidence). Condition A reproduces the EditPropBench/RevPropBench setting on the same claims, so the difference is measured, not argued.

## 4. Evidence so far

**Offline (final; MedScope, 248 examples, CIs by bootstrap over 40 source cases):**
- A system that "accepts" feedback by keyword overlap changes **72% [57–85]** of the evidence-supported claims that false feedback attacks. The false condition does measure claim-level deference.
- Its change recall falls from **0.40 on D to 0.17 on P, and 0.10 at depth 2**. Following the feedback's surface finds direct targets but not their consequences.
- The gold oracle scores 1.0, and the deterministic label rules reproduce every gold label.

**Model runs (in progress, $0):**
- `gpt-oss-120b` and `qwen3.8-27b` on Groq's free tier; `gemini-3.5-flash-lite` as a fixed judge.
- 60 examples (20 cases × valid / false / authority) × conditions A and B × {evidence-aware prompt, single-prompt scope-first, scope-first pipeline}.
- The full design (248 examples, all conditions, 5 systems) runs on the department GPU server.

> **To fill in (from `results/RESULTS_medscope.md`):**
> - B − A gap on change recall D / P and interaction-exact, with paired case-level CIs;
> - preservation error on K⁺ in the false condition;
> - U-F1 on authority-only;
> - pipeline vs. evidence-aware prompt.
>
> Report a null A−B gap as a null.

## 5. Risks and how the design answers them

| Risk | Answer |
|---|---|
| "This is EditPropBench plus a sycophancy test." | The paired A/B design measures whether verification changes scope on identical claims. If the gap is null, the benchmark still contributes the U label, claim-level sycophancy (K⁺ in the false condition) and clinical chains. The paper is framed by whichever result holds. |
| LLM-authored clinical content | All authored text is flagged unreviewed. A clinically trained reviewer pass and a second annotator (Cohen's κ) come before release; cases that fail are dropped. |
| Small benchmark (40 cases) | CIs are computed over source cases, not claims. A radiology split (IU X-ray build script) and more MEDEC cases are planned; EditPropBench-IX gives a second domain. |
| Judge validity | 100 hand-labelled (claim, revision) pairs; target κ ≥ 0.75; switch judges if it falls short. |
| Plan-then-edit hurt propagation on EditPropBench | The `no-prop` ablation isolates our propagation check; we will report it either way. |

## 6. Decision requested

Keep the framing: **feedback is a hypothesis; evidence is the arbiter**. Lead with the cost of verification (A vs. B) if the runs show a gap. Otherwise lead with claim-level sycophancy and unresolved propagation.
