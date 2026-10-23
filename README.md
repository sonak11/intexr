# IntExR — Interactive Explanation and Refinement (senior thesis, Prof. Metaxas)

**Start with [`HANDOFF.md`](HANDOFF.md)**: it records the current state and the ordered task list.

Paper 1, **IntExR-Scope**: given an original response, its supporting evidence, user feedback, and new evidence, revise every affected claim, preserve unaffected supported claims, and abstain when the evidence is insufficient.

## Layout
```
docs/01_literature_review.md   literature review + 55-paper coverage matrix (direct / propagated / preservation / unresolved / unreliable feedback)
docs/literature_matrix.csv     same matrix, machine-readable
docs/02_task_definition.md     formal task, input/output spec, labels D/P/K/U, metrics, conditions A–D
docs/03_semester1_plan.md      week-by-week plan to 31 Oct novelty review and 18 Dec frozen protocol
docs/04_annotation_guide.md    labeling procedure for annotators
docs/05_datasets_and_paper.md  existing datasets, our dataset plan, dataset-paper venues and checklist
docs/06_paperB_dataset_paper.md  Paper B (MedScope clinical dataset): separation from Paper 1, design, review protocol, timeline
paperB/proposals/              case proposals (LLM-written, NOT clinically reviewed)
paperB/data/                   built MedScope examples (scripts/build_medec_scope.py)
external/                      40-example IntExR-format samples from MEDEC, VitaminC, EditPropBench (see external/README.md)
pilot/data/pilot_v0.json       16 pilot examples (8 synthetic MIMIC-style CXR, 8 real COCO captions), 86 claims
intexr/                        harness: data validation, prompts, stdlib LLM clients, systems, metrics
intexr/scope.py                scope-first PIPELINE (the method): align (LLM) → label (code) → revise (LLM) → assemble → leak check
intexr/gate.py                 claim-level evidence-gate baseline (HF NLI model or LLM scorer)
tests/test_pipeline.py         gold-perfect LLM stages must reproduce the oracle  (python3 -m unittest tests.test_pipeline)
paper1/                        Paper 1 draft (ACL format): cd paper1 && latexmk -pdf main.tex
scripts/run_pilot.py           run systems × conditions → results/report.md (--match REGEX, --limit N for free quotas)
scripts/run_v0.sh              first real results in one command: MODEL=gemini:<id> JUDGE=groq:<id> bash scripts/run_v0.sh
scripts/summarize_results.py   paper tables: main, paired A−B gap, P recall by depth, validity strata (+ LaTeX)
scripts/label_actions.py       judge calibration: sample / label / score (Cohen's kappa vs the LLM judge)
scripts/list_models.py         list a provider's model ids
docs/08_free_compute.md        $0 compute plan (free API tiers, thasos vLLM, Kaggle)
scripts/check_dataset.py       validate any dataset file, balance tables, thin cells, markdown review sheet
scripts/fetch_external.py      download MEDEC / VitaminC / EditPropBench
scripts/convert_external.py    convert them to IntExR format (+ feedback-validity variants)
scripts/annotation_tools.py    blind annotation sheet + Cohen's kappa
scripts/mimic_candidates.py    mine MIMIC-CXR candidates (after PhysioNet access)
```

## Run
```bash
python3 scripts/run_pilot.py --systems no_revision accept_feedback_lexical oracle --out results/offline
```
Free models (public data only; see docs/08):
```bash
export GEMINI_API_KEY=... GROQ_API_KEY=...
python3 scripts/list_models.py gemini && python3 scripts/list_models.py groq
SMOKE=1 MODEL=gemini:<id> JUDGE=groq:<id> bash scripts/run_v0.sh     # 3 examples first
MODEL=gemini:<id> JUDGE=groq:<id> bash scripts/run_v0.sh             # resumable after daily caps
```
Systems include `scope_pipeline`, `scope_pipeline_noprop`, `scope_pipeline_nocheck`, and `evidence_gate@hf:<NLI model>` (on a GPU box) or `evidence_gate@<provider:model>`.

With a paid model (Python 3.9+, no packages needed):
```bash
export ANTHROPIC_API_KEY=...
python3 scripts/run_pilot.py --systems no_revision oracle dialogue@anthropic:claude-sonnet-5-5 evidence_prompt@anthropic:claude-sonnet-5-5 always_rewrite@anthropic:claude-sonnet-5-5 scope_first@anthropic:claude-sonnet-5-5 --judge anthropic:claude-haiku-4-5-20251001 --conditions A B C D --out results/sonnet
```
For an OpenAI-compatible endpoint (Azure OpenAI, vLLM, Together, Ollama), set `OPENAI_BASE_URL` and `OPENAI_API_KEY`, then use `SYSTEM@openai:MODEL`. Responses are cached in `results/.cache/`.

## Data rules
- Pilot CXR cases are **synthetic** and contain no MIMIC text.
- Real MIMIC-CXR data needs PhysioNet credentialing and the DUA. Keep it in `data/mimic/` (git-ignored), and send it only to [PhysioNet-approved LLM services](https://physionet.org/news/post/llm-responsible-use/) (e.g. Anthropic API, Azure OpenAI with human review opted out, Bedrock, Vertex). **Not** the direct OpenAI API or ChatGPT.
- COCO captions are CC-BY 4.0.

## Check a dataset
```bash
python3 scripts/check_dataset.py pilot/data/pilot_v0.json external/*.json --show 1 --review results/review.md
```

## Rebuild local data (not in git)
```bash
mkdir -p data/iu_xray && curl -L -o data/iu_xray/NLMCXR_reports.tgz https://openi.nlm.nih.gov/imgs/collections/NLMCXR_reports.tgz
tar xzf data/iu_xray/NLMCXR_reports.tgz -C data/iu_xray
python3 scripts/iu_xray_parse.py
python3 scripts/build_iu_pilot.py
python3 scripts/merge_pilot_v1.py
```
`pilot/data/pilot_v1.json` (24 examples) merges `pilot_v1_iu.json` (real IU), the COCO items, and the synthetic items from `pilot_v0.json`. It is git-ignored because IU is CC BY-NC-ND 4.0.
