# IntExR — Semester 1 (Fall 2026) Detailed Plan

**Fixed milestones (from the thesis plan):**
- **Sat 31 Oct 2026:** first novelty review.
- **Fri 18 Dec 2026:** pilot report + frozen protocol.

**Data:** MIMIC-CXR (medical) and COCO Captions (non-medical, provisional).

The plan works backwards from three decisions the pilot must make:

1. **Are the D/P/K/U labels workable?** Two annotators reach Cohen's κ ≥ 0.6 on the pilot, with a target of ≥ 0.7 on the frozen set.
2. **Is propagation genuinely hard?** For ≥ 2 of 3 models, change-recall on P is ≥ 10 points below recall on D, *or* preservation error on supported K claims is ≥ 10%.
3. **Does verifying feedback matter beyond existing propagation benchmarks?** On the same claims, condition B (unverified feedback) is ≥ 10 points worse than condition A (verified edit, the EditPropBench setting) on P recall or K preservation. **This is the novelty argument against EditPropBench and RevPropBench.**

If (2) or (3) fails, see the fallback options in §4.

---

## Update 25 Oct 2026
- First model results (dev pilot): `docs/11_results_v0.md`.
- MedScope v0.2: 47 cases (20 dev / 27 test).
- Novelty memo ready for 31 Oct.
- Remaining for Dec 18: second annotator + κ, clinical review, judge calibration, thasos full design, condition E, test-split growth.

## Update 23 Oct 2026 (overrides the stale items below)

- **Compute / API:** $0 only: Gemini and Groq free tiers (public data), vLLM on thasos, and Kaggle as a backup. See `docs/08_free_compute.md`. The Anthropic/Azure items in week 1 are dropped.
- **MIMIC / PhysioNet:** off the critical path. MedScope (MEDEC-based) is the clinical core. MIMIC is only added if credentialing arrives, and then only on self-hosted models.
- **Prof. Metaxas email:** on hold until the cases and first model results are ready (Defei's advice).
- **Non-medical domain:** COCO is now a baseline only. EditPropBench-IntExR is the hard non-medical set. FRUIT or ARIES are optional (ARIES's S3 bucket is reachable from the cloud sessions).
- **Done since 2 Oct:**
  - MedScope v0: 40 cases, 248 examples, 1,186 claims; 59 depth-2 P claims; superseding and conflicting-evidence variants; evidence-backed false variant.
  - Scope-first pipeline and evidence-gate baseline (`intexr/scope.py`, `intexr/gate.py`) plus tests.
  - Results summarizer, `scripts/run_v0.sh`, and the judge-labelling CLI.
  - Paper 1 draft (`paper1/main.tex`, 8 pp.).
- **Still blocking Oct 31:** first model numbers (needs API keys or thasos), and verifying the `recall` rows of the literature matrix.

## 0. Status as of 2 Oct

| Item | File | State |
|---|---|---|
| Literature review + 55-row coverage matrix | `docs/01_literature_review.md`, `docs/literature_matrix.csv` | v0.1. About 35 rows are from memory and must be checked |
| Formal task definition, I/O spec, metrics | `docs/02_task_definition.md` | v0.1 |
| Annotation guide | `docs/04_annotation_guide.md` | v0 |
| Pilot set: 16 examples / 86 claims (8 CXR synthetic MIMIC-style, 8 COCO real captions) | `pilot/data/pilot_v0.json` | v0, single-annotator (me) |
| Harness: 7 systems, 4 conditions, metrics, bootstrap CIs, LLM claim-alignment judge | `intexr/`, `scripts/run_pilot.py` | runs offline; LLM runs need an API key |
| Blind annotation sheet + κ / agreement tool | `annotation/`, `scripts/annotation_tools.py` | ready |
| MIMIC candidate miner (addenda, hedged impressions, consecutive studies, RadGraph `suggestive_of`) | `scripts/mimic_candidates.py` | skeleton; needs access |

Pilot label distribution: D 19, P 16 (12 at depth 1, 4 at depth 2), K 44 (23 supported, 21 unverified), U 7. Feedback validity: valid 5, false 3, partial 3, ambiguous 2, superseding 1, outdated 1, unsupported 1.

---

## 0b. Data sources (updated 2 Oct): start without PhysioNet

| Source | Access | Status | Role |
|---|---|---|---|
| **IU X-ray / Open-i** (3,955 reports; 3,419 with findings + impression) | none, direct download | **downloaded and parsed**; 540 rich candidates; 8 pilot items built (`scripts/build_iu_pilot.py`) | primary CXR source for the pilot |
| **ReXGradient-160K** (160k studies, 3 US health systems, indication/comparison/findings/impression) | Hugging Face license click-through | request today | scale-up source; has comparison sections for temporal cases |
| **CheXpert Plus** (187k reports, section-parsed) | Stanford AIMI research-use agreement (click-through) | request today | second scale-up option |
| MIMIC-CXR | PhysioNet credentialing + CITI | apply in parallel; *not* on the critical path anymore | reviewer-familiar benchmark; add if access arrives by January |

IU is CC BY-NC-ND 4.0. Because of the no-derivatives term, the released benchmark ships IU report IDs plus the build script, not the edited text.

## 0c. Second paper (Option B, decided 2 Oct)
A separate clinical dataset paper, **MedScope**: plan, timeline, and how it is kept separate from Paper 1 are in `docs/06_paperB_dataset_paper.md`. It shares the annotation round and the Dec 18 freeze with Paper 1. Target: CHIL 2027 (check the deadline; early Feb in 2026). **Submit Paper B before Paper 1.**

## 1. Week-by-week

### Week 1 · Fri 2 – Fri 9 Oct · *Access + reading*
- [x] IU X-ray downloaded; 8 real-report pilot items built (`pilot/data/pilot_v1.json`: 24 examples / 136 claims).
- [ ] Click through the ReXGradient-160K (HF) and CheXpert Plus (Stanford AIMI) agreements. Start the PhysioNet/CITI application in the background; it is no longer blocking.
- [ ] Email Prof. Metaxas:
  - the 1-page summary (§5 below);
  - ask for help finding a radiologist or clinician collaborator (needed for the `cxr-007` authority question and for double-labelling);
  - confirm that COCO is acceptable as the provisional second domain.
- [ ] Read in full: EditPropBench, RevPropBench, PBT. Fill in their rows in the matrix from the papers.
- [ ] Get API access for **three models**:
  - (a) a frontier closed model via the Anthropic API (allowed for MIMIC under PhysioNet guidance);
  - (b) a second vendor via **Azure OpenAI with human review opted out** (direct OpenAI API is *not* allowed for MIMIC);
  - (c) an open-weight model (e.g. Qwen3 / Llama-3.x 70B) via vLLM or university GPUs.
- [ ] Run the pilot on all three models under conditions A–D (commands in the README). Cost is under $10.

### Week 2 · 10 – 16 Oct · *First model results + second annotator*
- [ ] Read every model output for 4 examples by hand. Check that the LLM judge's keep/revised/removed/hedged calls match yours, and record the judge-vs-you agreement.
- [ ] Recruit a second annotator (labmate or Metaxas group). Give them `annotation/sheet_blank.csv` + the guide. They label blind (~1 hour).
- [ ] Compute κ with `scripts/annotation_tools.py agree`. List every disagreement and classify its cause:
  - granularity;
  - authority-as-evidence;
  - majority vs. conflict;
  - temporal scope;
  - refinement vs. keep.
- [ ] Read RARR, FRUIT, Belief-R, Hase et al. 2024, MEDEC, CorBenchX, RaDialog.

### Week 3 · 17 – 23 Oct · *Revise schema + grow the pilot*
- [ ] Revise the guide and task definition (v0.2) from the disagreements. Close open questions 1–5 in the task definition, or keep them as explicit parameters.
- [ ] Add 4–6 examples aimed at **depth-2/3 propagation** and **U-dependency**, the thinnest cells (U-feedback n=1). Use the same format.
- [ ] Draft the **novelty memo** (≤ 3 pages):
  - closest-work table (lit review §9);
  - what is not new (the D/P/K partition);
  - what is new (validity × scope; U and its propagation; clinical inferential dependencies; temporal scope);
  - first A-vs-B numbers.

### Week 4 · 24 – 31 Oct · ***Novelty review (due Sat 31 Oct)***
- [ ] Final search sweep from 1 Oct onward: arXiv cs.CL/cs.AI for "propagation", "revision", "sycophancy", "radiology report correction". Check the EMNLP 2026 accepted list and any NeurIPS 2026 D&B acceptance of EditPropBench.
- [ ] Check every `recall` row of the matrix and change it to `verified`.
- [ ] Meet Prof. Metaxas with the memo. **Decision:** keep the framing, narrow it (e.g. lead with the validity × scope interaction), or pivot.

### Week 5 · 1 – 7 Nov · *CXR scale-up pipeline (IU + ReXGradient; MIMIC if access arrives)*
- [ ] Run `scripts/mimic_candidates.py` over a 2–5k-patient sample.
  - **Order studies by `StudyDate`/`StudyTime` from the metadata CSV**: study IDs are not chronological.
  - Count candidates by type: addendum, hedged, consecutive.
- [ ] Design how the original response is produced for real cases. Recommended:
  - (i) draft reports from a public CXR report generator, or LLM-perturbed reference reports using ReXErr-style error types (laterality, severity, negation, device position);
  - (ii) the true report, addendum, or next study serves as new evidence;
  - (iii) RadGraph `suggestive_of` edges propose the finding → impression dependencies.
- [ ] Write the feedback generator: templates × speaker role × confidence cue × validity type. An LLM *proposes* feedback; a human checks every item.
- [ ] Decide the non-medical source. Keep COCO if pilot P recall < 0.9 and depth ≥ 2 is feasible. Otherwise switch to FRUIT (Wikipedia updates) or ARIES (reviewer-feedback revisions). See lit review §9.

### Week 6 · 8 – 14 Nov · *Pilot v1 at ~60–80 examples*
- [ ] Build ~40 MIMIC + ~30 non-medical examples, balanced over label × validity × depth. **MIMIC text stays in `data/mimic/` (git-ignored)** and goes only to PhysioNet-approved endpoints.
- [ ] Double-label at least 30% of examples; adjudicate.
- [ ] Complete the baselines required by the thesis plan:

  | Thesis plan baseline | Harness name / status |
  |---|---|
  | no revision | `no_revision` |
  | always accept | `accept_feedback_lexical` (scope only); add an LLM "apply the feedback" variant |
  | always rewrite | `always_rewrite` |
  | ordinary dialogue | `dialogue` |
  | evidence-aware prompting / RAG | `evidence_prompt`; add a RAG variant if the evidence pool grows beyond what fits in context |
  | simple claim-level evidence gate | **to build**: NLI or LLM per claim; revise iff contradicted |
  | strong current correction baseline | **to choose**: LEDGER-style dependency-graph editing, or a RARR-style pipeline |

### Week 7 · 15 – 21 Nov · *Scope-first prototype v1*
- [ ] Split `scope_first` into explicit stages: decompose → align (with provenance) → scope → constrained revise → consistency check.
  - The **deterministic constraint**: K claims are copied byte-for-byte from the original. This is enforced in code, not by prompting.
  - The **consistency check**: re-run alignment on R′ and flag residual contradictions.
- [ ] Ablations:
  - (a) single-call vs. staged (EditPropBench found plan-then-edit *hurt* propagation, so test this);
  - (b) with vs. without the dependency step;
  - (c) gold vs. predicted claims (setting S1 vs. S2).

### Week 8 · 22 – 28 Nov · *Error analysis (Thanksgiving week, light)*
- [ ] Build a taxonomy of failures from 30+ errors per system:
  - missed propagation;
  - over-revision of K;
  - deleting U instead of hedging;
  - adopting unsupported feedback additions;
  - temporal-scope errors.
- [ ] Compute **per-cell n** and the bootstrap CI width. Estimate how many source cases the spring benchmark needs for a ±0.05 CI on P recall.

### Week 9 · 29 Nov – 5 Dec · *Judge calibration + metrics freeze*
- [ ] Hand-label claim actions on 100+ (claim, revision) pairs and measure LLM-judge agreement. Freeze the judge only if κ ≥ 0.75. Otherwise move to a stricter rubric or two judges.
- [ ] Replace or augment the deterministic text checks with an entailment judge for evidence support and residual contradiction (RadFact-style).
- [ ] Add calibration: the scope-first output includes a confidence per label; report ECE.

### Week 10 · 6 – 12 Dec · *Write pilot report*
- [ ] Pilot report (~8 pp):
  - task;
  - data and statistics;
  - agreement;
  - results for 3 models × 7 systems × 4 conditions;
  - A-vs-B gap;
  - error taxonomy;
  - go/no-go on the three pilot questions.

### Week 11 · 13 – 18 Dec · ***Frozen protocol (due Fri 18 Dec)***
- [ ] Freeze:
  - schema v1;
  - annotation guide v1;
  - generation recipe per domain;
  - split policy (by source case / patient; test set frozen before headline experiments);
  - metric code (tagged git release);
  - judge prompt + calibration numbers;
  - target sample size;
  - release plan (MIMIC derivatives via PhysioNet; COCO under CC-BY).
- [ ] Spring timeline: scale → baselines → ablations → human error audit → draft by 15 Apr.

---

## 2. Deliverables checklist for 18 Dec
1. Literature matrix (verified) and the novelty memo.
2. Task definition v1 and annotation guide v1.
3. Pilot set v1 (~70–90 examples) with double-labelled subset and κ.
4. Baseline harness with all 7 baseline families, plus scope-first v1.
5. Pilot report with go/no-go decisions.
6. Frozen protocol document plus a tagged code release.

## 3. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| PhysioNet access delayed past wk 5 | Med | Keep building on synthetic MIMIC-style + IU X-ray (OpenI, public) reports, then swap in MIMIC. Code is source-agnostic. |
| No clinical collaborator for labels | Med | Use RadGraph structure and addenda (radiologist-authored ground truth) to reduce clinical judgment. Restrict clinical judgment calls to a small, clearly reported subset. |
| Scooped / framing too close to EditPropBench–RevPropBench | Med-High | Lead with the validity × scope interaction, U propagation, and temporal scope, supported by the A-vs-B ablation. Cite both prominently and reuse their metric names (ERA ≈ change_recall_P, CDR ≈ preservation error). |
| COCO dependencies too shallow | High | Pre-registered switch rule (wk 5) to FRUIT or ARIES. |
| Frontier models hit ceiling on the pilot | Med | Push difficulty: depth ≥ 2, implicit dependencies, multiple feedback items, longer reports. EditPropBench's hard stratum shows implicit dependencies stay hard. |
| LLM judge unreliable | Med | Use structured outputs where possible. Calibrate the judge against human labels (wk 9). Report human-checked subset numbers. |
| Label disagreement on U | High | U is defined by triggers (evidence / dependency / feedback). Disagreements are reported as findings, not hidden. |

## 4. Fallbacks if pilot questions fail
- **(2) fails (propagation not hard):** increase dependency depth and implicitness. Report preservation/over-revision as the main failure. Shift the emphasis to feedback validity.
- **(3) fails (no A–B gap):** the joint setting adds little difficulty. Re-frame Paper 1 around clinical revision with unresolved claims (U), or move the validity axis wholly into Paper 2 (persistence), where contamination is the main concern.

## 5. One-paragraph summary to send Prof. Metaxas
> I've finished a first literature pass (55 papers across evidence-based revision, edit propagation, model editing, sycophancy, belief revision, abstention, and radiology correction). Two 2026 benchmarks (EditPropBench, RevPropBench) already label direct, cascaded, and protected edits, but both assume the requested edit is correct and exclude unresolved cases. IntExR-Scope's distinct contribution is the interaction between *unknown feedback validity* and *claim-level scope*, including unresolved claims and their propagation, in clinical reports where impressions depend on findings. I've written a formal task definition, a 16-example pilot (8 synthetic MIMIC-style CXR, 8 COCO) covering all four labels and seven feedback-validity types, and an evaluation harness. Next: PhysioNet access, a second annotator for agreement, and runs on three models, including a verified-edit vs. unverified-feedback ablation that directly tests novelty against those benchmarks. Could you help me find a radiology collaborator for double-labelling?
