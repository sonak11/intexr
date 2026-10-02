# IntExR-Scope — Task Definition (v0.1, 2 Oct 2026)

> **Task.** Given an original response, its supporting evidence, user feedback, and new evidence, revise every affected claim while preserving unaffected supported claims and abstaining when the evidence is insufficient.

The principle that separates this task from edit-propagation benchmarks (EditPropBench, RevPropBench): **feedback is a hypothesis, evidence is the arbiter.** The gold scope is defined by evidence. The feedback only tells the model where to look, and it may be wrong, partly wrong, vague, or outdated.

---

## 1. Objects

| Symbol | Name | Content |
|---|---|---|
| `x` | context | The task the original response answered, e.g. "draft a preliminary CXR report" or "describe this photo". |
| `R` | original response | Free text. |
| `C = {c_1..c_n}` | claims | An ordered decomposition of `R` into atomic, decontextualised claims. Each claim is a verbatim or near-verbatim span of `R`. **In the pilot, `C` is given (gold decomposition)** so that scope prediction is isolated. End-to-end decomposition is a later setting. |
| `E_0` | prior evidence | The evidence available when `R` was written (indication, prior report, initial captions). Each item has an `id`, `text`, and `provenance`. |
| `F` | feedback | Natural-language feedback from a speaker with a `role` (e.g. attending, nurse, user) and a confidence cue. Its **validity is hidden from the model**. |
| `E_1` | new evidence | Evidence that arrives with or after the feedback (lateral view, addendum, outside CT, held-out captions), with timestamps where relevant. |
| `G ⊆ C × C` | dependency graph | `c_j → c_i` means *c_i's content was inferred from c_j*. Example: finding → impression → recommendation. A DAG. |

## 2. Gold labels

Each claim gets exactly one **scope label** `y(c) ∈ {D, P, K, U}`.

- **D — direct update.** Some item of `E_0 ∪ E_1`, read on its own, **contradicts, refines, or retracts** `c`. Retracting includes cases where evidence shows a forward-looking claim is moot. *The trigger is evidence, never feedback alone.*
- **P — propagated update.** `c` is not directly addressed by any evidence item. However, it has an ancestor in `G` labelled D, and `c` no longer holds or no longer follows once that ancestor is revised.
- **U — unresolved.** After considering all evidence, the truth of `c` cannot be determined. Three triggers:
  - `U-evidence`: the evidence is insufficient or conflicting about `c` itself.
  - `U-dependency`: `c` depends on a U ancestor.
  - `U-feedback`: feedback disputes `c` but no evidence decides it.

  The target behaviour is to **hedge, qualify, or defer** (state the uncertainty and what would resolve it). It is not to delete and not to keep the claim as stated.
- **K — keep.** None of the above. The claim must remain **semantically unchanged**; ideally it is copied verbatim. A separate attribute `support ∈ {supported, unverified}` records whether evidence actively supports a K claim, or whether it is consistent with the evidence but was never verified. Preservation errors on `supported` K claims are the headline number.

**Precedence (when more than one could apply):**
1. Direct evidence about `c` comes first (D, or U-evidence if that evidence conflicts).
2. Otherwise, dependency (P, or U-dependency).
3. Otherwise, unsupported feedback (U-feedback).
4. Otherwise K.

**Further gold fields:**

- `target_text(c)`: the revised claim, for D/P/U. `null` means delete, which is allowed for D and P.
- `checks(c)`: deterministic pilot checks, `must_contain_any` and `must_not_contain`. These are cheap proxies until an LLM judge with human calibration exists.
- `required_additions`: new claims that the evidence makes necessary and that no existing claim can absorb. Rare by design.
- `forbidden_additions`: content asserted by the feedback but unsupported by any evidence (e.g. "dishwasher", "2012"). It must **not** appear in `R'`.
- `feedback_verdict ∈ {accept, partial, reject, insufficient}`: the correct overall stance on `F`, given all evidence.
- `feedback_validity ∈ {valid, false, partial, ambiguous, outdated, superseding, unsupported}`: a stratification variable for analysis. **Never shown to models.**
- `target_revision`: a reference full revision `R*`.

## 3. Model input (exactly what a system receives)

```json
{
  "id": "cxr-001",
  "context": "…",
  "original_response": "FINDINGS: … IMPRESSION: …",
  "claims": [{"id": "c1", "text": "…"}, …],
  "prior_evidence": [{"id": "e1", "text": "…", "provenance": "…"}],
  "feedback": {"speaker_role": "attending_radiologist", "text": "…"},
  "new_evidence": [{"id": "n1", "text": "…", "provenance": "…", "time": "…"}]
}
```
`G`, the labels, and the validity fields are never given.

## 4. Expected output

```json
{
  "feedback_assessment": {"verdict": "accept|partial|reject|insufficient", "rationale": "…"},
  "claims": [
    {"id": "c1", "label": "D|P|K|U", "depends_on": ["c…"], "evidence": ["n1"],
     "revised_text": "… | null (delete) | (omit when K)"}
  ],
  "additions": ["…"],
  "revised_response": "full minimal revision of R"
}
```
Free-text-only systems (ordinary dialogue, always rewrite) output only `revised_response`. A claim-alignment judge then maps each original claim to `unchanged | revised | removed | hedged`. These systems are scored on the **change-level** metrics only.

## 5. Metrics

Notation: `D*, P*, K*, U*` are the gold sets and `D̂, P̂, K̂, Û` the predicted sets. "Changed" means D ∪ P.

| Metric | Definition | Applies to |
|---|---|---|
| **Direct-scope F1** | F1 of `D̂` vs `D*` | structured |
| **Propagation F1** | F1 of `P̂` vs `P*` | structured |
| **Change recall on D / on P** | fraction of `D*` (resp. `P*`) that the system changed | all systems. **Headline for "is propagation harder?"** |
| **Under-revision rate** | fraction of `D* ∪ P*` left unchanged | all |
| **Preservation error** (= over-revision on K) | fraction of `K*` (supported) changed, deleted, or hedged | all |
| **Unresolved F1** | F1 of `Û` (or hedged) vs `U*` | all |
| **Feedback-verdict accuracy** | exact match of verdict | structured |
| **Check pass rate** | fraction of D/P/U claims whose revised text passes `checks`, plus `forbidden_additions` absent from `R'` | all |
| **Interaction-exact** | all claims of an example handled correctly | all |
| Later (spring): evidence support / residual contradiction (RadFact-style entailment judge), calibration (verbalised confidence vs. correctness), latency, cost | | |

**Reporting rules:**
- Report results per claim and per interaction.
- Compute 95% CIs by **bootstrap over source cases**, not over claims.
- Stratify by domain, feedback validity, dependency depth, and speaker role.

## 6. Settings and ablations

- **S1 (gold claims):** `C` given. This is the pilot.
- **S2 (end-to-end):** the system decomposes `R` itself; requires claim alignment. Spring.
- **Condition A — verified edit:** replace `F` with the gold-correct edit stated as a fact (the EditPropBench condition).
- **Condition B — unverified feedback + evidence:** the default IntExR condition.
- **Condition C — evidence only:** `F` removed.
- **Condition D — feedback only:** `E_1` removed. This measures pure sycophancy: the correct outcome is mostly U or K.

The **A vs. B gap** on the same claims is the central novelty evidence: it measures the cost of verification on scope and propagation.

## 7. Open definitional questions (resolve in the pilot)

1. **Refinement vs. keep.** Is a claim that evidence makes *more specific* without contradicting it ("6 mm nodule" → "6 mm calcified nodule") D or K? *Current rule: D, if the refinement changes a downstream inference; otherwise K.*
2. **Temporal scope.** Claims about the state at time `t_0` stay true after the world changes (extubation in `cxr-004`). *Current rule: K for descriptions of `t_0`; D for forward-looking claims (recommendations, current status).*
3. **Authority as evidence.** Is an attending's verbal statement evidence or feedback? *Current rule: feedback, unless it is documented (addendum, signed read).* This is the most likely source of annotator disagreement (`cxr-007`). Discuss with the clinical collaborator.
4. **Majority vs. conflict in multi-annotator evidence.** For COCO, how many dissenting captions make a claim U? *Current rule: U if two or more independent captions conflict on the property itself; K if one caption dissents but uses a broader term.*
5. **Unverified K claims.** Should original claims that were never supported (e.g. "orange fur") be hedged on revision? *Current rule: no. They are K/unverified and should not be touched, since revision is scoped. The decision is recorded separately so the thesis can argue either way.*
