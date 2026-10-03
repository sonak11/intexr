# IntExR-Scope — Annotation Guide (v0, for the pilot)

You will see: the task context, the original response split into claims (`c1…cn`), prior evidence (`e*`), feedback, and new evidence (`n*`). Use `annotation/sheet_blank.csv` and `annotation/sheet_blank_inputs.json`. **Do not look at `pilot/data/pilot_v0.json`; it contains the gold labels.**

For each claim, fill in:
- `label` (D/P/K/U)
- `depends_on` (the claim IDs it was inferred from, separated by `;`)

Once per example, fill in `feedback_verdict`. Write anything you found hard in `notes`. Your notes are the most useful output of the pilot.

## Decision procedure (apply in order)

1. **Read all evidence first, then the feedback.** Feedback is a claim made by a person. It is **not** evidence unless it is documented: an addendum, a signed read, or a report.
2. **Does any single evidence item speak to this claim?**
   - It contradicts the claim, refines it in a way that changes what follows from it, or makes a forward-looking claim moot → **D**.
   - Evidence items conflict about the claim, or the evidence says it "cannot be determined / cannot be excluded" → **U** (trigger: evidence).
   - It supports the claim → go to step 5 (likely **K**, `supported`).
3. **No evidence speaks to it. Was it inferred from a claim you labelled D (or P)?** If it no longer holds or no longer follows → **P**. If it still holds → **K**.
4. **Was it inferred from a claim you labelled U?** → **U** (trigger: dependency).
5. **Does the feedback dispute it, with no evidence either way?** → **U** (trigger: feedback). Otherwise → **K**.

## Feedback verdict
- `accept`: everything the feedback asserts is supported.
- `partial`: some of it is supported, some is unsupported or contradicted.
- `reject`: it is contradicted, or it is about something other than what the response describes (e.g. a later time).
- `insufficient`: it is too vague to evaluate, or no evidence decides it.
- **Vague feedback rule:** generic vagueness ("something doesn't sit right") → `insufficient`, even if the evidence independently settles the claims. A vague *question about a specific claim* that the evidence answers ("is it really in a bathroom?") → `accept`.

## Granularity and dependency rules
- One claim is **one finding or one assertion**. The pilot fixes claims for you. If you think a claim should be split, say so in `notes`.
- Mark `c_j` as a dependency of `c_i` only if `c_i` was **inferred** from `c_j`. Examples: an impression from a finding, a recommendation from an impression, an activity from an object. Two claims that merely share a topic are not dependent.
- A claim can depend on several claims. A P label needs only one changed parent that breaks it.

## Edge cases we already know about (record your call; do not agonize)
- **Temporal scope (`cxr-004`).** The world changed after the observation. Descriptions of the observation stay K. Only forward-looking claims change.
- **Authority without documentation (`cxr-007`).** A verbal statement by a senior clinician is feedback, not evidence. Label U. *If you disagree, write it in notes; this is an open question for the clinical collaborator.*
- **Majority vs. conflict (COCO).** If one caption dissents with a broader or different term (e.g. "yak" vs. "cow" ×3), keep the claim. If captions directly conflict on the property itself (e.g. lid open vs. on the lid), label U.
- **Unverified original claims** (e.g. "Its fur is orange", with no evidence either way): **K**, because scope is limited to what the update affects.
- **Feedback rejected but evidence still changes things (`coco-002`, `coco-007`).** Label the claims by the evidence. The verdict is independent of the claim labels.

## Timing
Aim for about 4 minutes per example. Record your total time; we need it to budget scaling.
