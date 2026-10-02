# Datasets: what exists, what we build, and the dataset paper (v0.1, 2 Oct 2026)

## 1. Is there a ready-made dataset for this task?
**No.** No public dataset combines:
- multi-claim responses,
- claim-level D/P/K/U labels with dependencies,
- feedback whose validity varies, and
- evidence that decides it.

That gap is the contribution of Paper 1. Several public datasets each cover **one piece** with *real* data. We use them two ways:
- as **component checks** (does our harness and metric measure what we think?);
- as **raw material** for our own dataset.

| Source | License | Real part | Tests | Cannot test | In repo |
|---|---|---|---|---|---|
| **MEDEC** (Ben Abacha et al., Findings ACL 2025) | **CC BY 4.0** | clinical notes; expert-injected error + correction; ~49% error-free | D + K on clinical text; rejecting false feedback on correct notes | propagation; evidence (it relies on medical knowledge) | `external/medec_intexr.json` (40) |
| **VitaminC** (Schuster et al., NAACL 2021) | CC BY-SA 3.0 | real Wikipedia revisions; contrastive evidence | D / K / **U** per claim with real evidence | propagation | `external/vitaminc_intexr.json` (40) |
| **EditPropBench** (Kruthof, 2026) | CC BY 4.0 | dependency labels (synthetic manuscripts) | **P** + K preservation at scale. We add *false-feedback variants* | U; partial/ambiguous feedback | `external/editpropbench_intexr.json` (40) |
| IU X-ray (Open-i) | CC BY-NC-ND 4.0 | real radiology reports | real CXR text for our perturbation recipe | no redistribution of edits | local only (`scripts/build_iu_pilot.py`) |
| COCO Captions | CC BY 4.0 | 5 independent captions per image | U from caption conflict; evidence-only updates | deep propagation | in `pilot_v0.json` |
| ReXGradient-160K | HF license click-through (check terms) | 160k CXR reports with comparison sections | temporal / superseding cases at scale | depends on license | request access |
| CheXpert Plus | Stanford research-use agreement, **no redistribution** | 187k section-parsed CXR reports | scale-up source | release | request access |
| MIMIC-CXR | PhysioNet credentialed | reviewer-standard CXR reports | final CXR split, released via PhysioNet | — | apply in background |
| FRUIT | Apache-2.0 (`gs://gresearch/FRUIT`) | real Wikipedia article updates from new evidence | real D + K at document level | feedback | not fetched (needs gsutil + TFRecord) |
| ARIES | ODC-BY (`s3://ai2-s2-research-public/aries`) | real paper edits aligned to real reviewer comments | **real feedback** → revision | evidence-based verification | not fetched yet |

Commands:
```bash
python3 scripts/fetch_external.py                        # MEDEC, VitaminC, EditPropBench -> data/external/
python3 scripts/convert_external.py medec --n 200         # -> external/medec_intexr.json
python3 scripts/check_dataset.py external/*.json --show 2
python3 scripts/run_pilot.py --data external/editpropbench_intexr.json --systems ...   # same harness
```

**Why the false-feedback variants matter.** EditPropBench assumes every edit is correct. We pair each item with a copy whose evidence *contradicts* the requested edit, where the gold answer is "keep everything, reject the feedback". Running a model on both halves measures the cost of verification directly, on someone else's benchmark. That makes it a strong external version of the A-vs-B ablation.

## 2. Our own dataset: the IntExR-Scope benchmark

**Goal:** one release with these splits:

| Split | Source | Why |
|---|---|---|
| `clinical-notes` | MEDEC notes, extended with propagation | redistributable clinical core (CC BY 4.0) |
| `radiology` | MIMIC-CXR via PhysioNet, or ReXGradient if its license allows; IU as build script only | the headline clinical domain |
| `general` | VitaminC- and/or FRUIT-derived multi-claim responses (+ COCO if it proves deep enough) | non-medical generality |

**What we add to each source:**
1. **Propagation.** Make downstream sentences consistent with the error, so that fixing the error requires propagation. In MEDEC, management/treatment sentences that follow from a diagnosis are rewritten to match the wrong diagnosis. This is the same recipe as `build_iu_pilot.py`.
2. **Feedback of seven validity types,** from templates × speaker role × confidence cue. An LLM proposes; a human verifies.
3. **Evidence items** that decide each D/U claim, taken from real text wherever possible (VitaminC revisions, report comparison sections, addenda).
4. **Labels:** D/P/K/U + dependencies + feedback verdict. 30% double-labelled; κ reported; clinician review on clinical items.

**Target size** (to be fixed by the 18 Dec power analysis): about 300–500 source cases per split, × 2–3 feedback variants each, for about 2–4k interactions and 15–25k claims.

## 3. Yes, this is a dataset paper

Benchmark/dataset papers are a standard publication type.

**Venues** (check current deadlines; these are typical timings):
- **NeurIPS Datasets & Benchmarks track** (deadline usually around May–June). The best fit for the May 2027 target.
- **ACL / EMNLP / NAACL via ARR**, as a "resource" or long paper. Cycles run roughly every two months.
- **LREC-COLING**: language-resource focus.
- **CHIL / MLHC / ML4H**: clinical ML. A good venue for the radiology-specific findings.
- *Scientific Data* (Nature) or *JAMIA* for a clinical-data-descriptor version.

**What reviewers expect** (put these in the 18 Dec frozen protocol):
- [ ] Clear task + why existing datasets don't cover it. This is lit review §9 + the A-vs-B result.
- [ ] Documented construction pipeline, released as code (we have the start: `build_iu_pilot.py`, `convert_external.py`).
- [ ] Annotation guide, annotator details, agreement (κ), adjudication.
- [ ] **Datasheet for Datasets** (Gebru et al.) and, for NeurIPS D&B, **Croissant** metadata.
- [ ] Licenses respected per source:
  - IU → IDs + script only;
  - MIMIC → PhysioNet-hosted derivative;
  - MEDEC / VitaminC / EditPropBench → redistributable with attribution (VitaminC share-alike).
- [ ] Strong baselines (7 families), analysis of failure modes, and human validation of the LLM judge.
- [ ] Hosting (Hugging Face / PhysioNet), a fixed test split, and a maintenance plan.
- [ ] Ethics: clinical safety, de-identification, intended use.

**Contamination note:** VitaminC, MEDEC, and EditPropBench are public, so models may have seen them. Our added labels, feedback, and propagation edits are new. Still, report results on the newly authored parts separately, and add canary strings to the released files.
