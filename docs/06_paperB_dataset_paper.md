# Paper B: Clinical Dataset Paper (Option B) (v0.1, 2 Oct 2026)

**Working title:** *MedScope: A Clinician-Reviewed Dataset for Evidence-Scoped Revision of Clinical Assessments Under Feedback of Varying Validity* (name is a placeholder; check it isn't taken).

## 1. What makes it a separate paper from Paper 1

| | **Paper B (MedScope)** | **Paper 1 (IntExR-Scope)** |
|---|---|---|
| Contribution | a **clinical resource**: data, construction, clinician review, clinical-harm annotation, dataset analysis | the **task across domains** + **scope-first method** + full baseline suite + verified-vs-unverified (A-vs-B) analysis |
| Domains | clinical only: assessment & plan (MEDEC-based), radiology reports | clinical (uses MedScope's test split, cited) + non-medical |
| Unique labels | **clinical harm severity** of each possible failure (accepting false feedback, missed propagation, deleting an unresolved finding…), rated by clinicians | none beyond the shared scope schema |
| Models | baseline numbers to characterise the data (3 models × 4 simple systems) | the method and all 7 baseline families, ablations, calibration, cost |
| Venue | clinical ML (CHIL / MLHC / ML4H) or NeurIPS D&B / ARR resource | ACL/EMNLP-style NLP venue (May 2027 plan) |

**Rule to avoid overlap:** submit Paper B **first**. Paper 1 then describes MedScope in a paragraph and cites it. Never have both under review making the same claims about the same data. **Get Prof. Metaxas's sign-off on this split.**

## 2. Data design

**Split 1: Assessment & Plan (MEDEC-based, redistributable, CC BY 4.0 + our additions).**
- **Prior evidence:** a MEDEC clinical note with its error sentence removed.
- **Original response:** an AI-drafted assessment & plan. It carries MEDEC's expert-designed error plus 1–3 claims that **follow from the error** (monitoring, follow-up, counselling, next tests).
- **New evidence:** a decisive result (pathology, imaging, labs) or a guideline statement.
- **Feedback variants per case:** valid, false (attacks a correct claim), partial (right fix + unsupported extra intervention), authority-only (no evidence). Still to add: ambiguous, outdated (an earlier lab superseded by a repeat), superseding (a new result after the note).
- **Status (2 Oct):** 31 cases → 188 examples, 873 claims, all seven feedback types (`paperB/proposals/*.json` → `scripts/build_medec_scope.py`). Error types: diagnosis, management, treatment, pharmacotherapy, causal organism. **Gaps:** only 2 superseding cases and 3 depth-2 chains, so the next batch should target those. Some MEDEC answers are disputable (e.g. ms-val-253, sinusitis antibiotic choice); those were skipped and the skip list is kept for the paper.

**Split 2: Radiology reports.** Built with the IU X-ray recipe (`scripts/build_iu_pilot.py`): real report = target, injected error + propagated impression. Released as a **build script + report IDs** (IU is no-derivatives). If PhysioNet access arrives, add a MIMIC-CXR version hosted on PhysioNet.

**Target size:** about 150–200 source cases → about 600–800 interactions, about 3–4k claims. Fix the exact number with the pilot variance (Dec).

## 3. Annotation and review protocol (the core of the dataset paper)
1. **Proposal.** An LLM (or the author) proposes cases with the fields in the proposals file. Every case is marked `proposed_unreviewed`.
2. **Clinician review.** Use `scripts/check_dataset.py --review` to produce a sheet. Per case, the clinician:
   - checks that the error is a real error;
   - checks that the dependent claims really follow from it;
   - checks that the corrected targets are right;
   - checks that the new evidence is realistic and decisive;
   - checks that the feedback variants are labelled correctly.
3. **Harm rating (new to this paper).** Per case, rate the clinical severity (none / minor / moderate / severe) of each failure mode:
   - (a) keeping the error;
   - (b) fixing the error but missing the dependent claims;
   - (c) accepting the false feedback;
   - (d) adopting the partial feedback's unsupported intervention;
   - (e) flipping on authority alone.

   This gives **harm-weighted metrics** for the paper.
4. **Double review** of at least 30% of cases. Report κ for labels and weighted κ for harm. Adjudicate disagreements.
5. Remove or fix any case a reviewer rejects, and **report rejection rates by error type**. That number is itself a finding about LLM-proposed clinical data.

## 4. Paper outline (8 pages + appendix)
1. **Introduction:** clinicians correct AI drafts; corrections can be wrong; a fix must spread to dependent conclusions; current clinical error datasets (MEDEC, CorBenchX, ReXErr) score one error, not scope.
2. **Related work:** clinical error correction, sycophancy in medicine (Med-Stress, SycEval, MedPRESS), edit propagation (EditPropBench, RevPropBench).
3. **Dataset construction:** sources, proposal, variants, review, harm rating.
4. **Statistics and quality:** label distribution, dependency depth, κ, rejection rates.
5. **Baseline evaluation:** 3 models × {no revision, dialogue, evidence-aware, structured}; the harm-weighted results.
6. **Analysis:** which error types propagate worst; how model behaviour changes with authority; abstention (U) behaviour.
7. **Limitations and ethics:** educational vignettes rather than real EHR notes; authored evidence; not for clinical use.
8. **Datasheet + Croissant** in the appendix.

## 5. Timeline, as fast as is realistic
| When | What |
|---|---|
| **Oct 3–10** | Expand proposals from 8 to 40 cases across all five error types. Add the ambiguous, outdated, and superseding variants. Build 10 radiology cases. **Ask Prof. Metaxas for clinician reviewers now**: reviewer time is the bottleneck. |
| Oct 10–24 | First clinician review round on 40 cases. Revise the guide. Try the harm-rating rubric. First model runs (needs an API key). |
| Oct 31 | Novelty review (shared with Paper 1): position MedScope against MEDEC, CorBenchX, Med-Stress, EditPropBench. |
| Nov | Scale to 150–200 cases; double review of 30%; full baseline runs. |
| Dec 1–18 | Analysis, figures, datasheet; frozen release. Same freeze date as Paper 1's protocol. |
| Jan 2027 | Write and polish. **Target CHIL 2027** (CHIL 2026's deadline was 4 Feb 2026; check the 2027 date). Fallbacks: an ARR cycle (resource paper), MLHC, or NeurIPS D&B (May–June). |

## 6. Risks
- **Clinical correctness of authored content.** All proposals so far are LLM-written; nothing ships without clinician review. Keep evidence statements traceable to named guidelines.
- **Vignette realism.** MEDEC-MS notes are exam-style (MedQA-derived). Be upfront about this, and use the radiology split for realism.
- **Contamination.** MEDEC is public. Our responses, dependencies, evidence, and feedback are new. Report results on the new parts and add canary strings.
- **Overlap with Paper 1.** Handled by §1. Keep a running list of which claims go in which paper.
