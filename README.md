# IntExR — Interactive Explanation and Refinement (senior thesis, Prof. Metaxas)

Paper 1, **IntExR-Scope**: given an original response, its supporting evidence, user feedback, and new evidence, revise every affected claim, preserve unaffected supported claims, and abstain when the evidence is insufficient.

## Layout
```
docs/01_literature_review.md   literature review + 55-paper coverage matrix (direct / propagated / preservation / unresolved / unreliable feedback)
docs/literature_matrix.csv     same matrix, machine-readable
docs/02_task_definition.md     formal task, input/output spec, labels D/P/K/U, metrics, conditions A–D
docs/03_semester1_plan.md      week-by-week plan to 31 Oct novelty review and 18 Dec frozen protocol
docs/04_annotation_guide.md    labeling procedure for annotators
pilot/data/pilot_v0.json       16 pilot examples (8 synthetic MIMIC-style CXR, 8 real COCO captions), 86 claims
intexr/                        harness: data validation, prompts, stdlib LLM clients, systems, metrics
scripts/run_pilot.py           run systems × conditions → results/report.md
scripts/annotation_tools.py    blind annotation sheet + Cohen's kappa
scripts/mimic_candidates.py    mine MIMIC-CXR candidates (after PhysioNet access)
```

## Run
```bash
python3 scripts/run_pilot.py --systems no_revision accept_feedback_lexical oracle --out results/offline
```
With a model (Python 3.9+, no packages needed):
```bash
export ANTHROPIC_API_KEY=...
python3 scripts/run_pilot.py --systems no_revision oracle dialogue@anthropic:claude-sonnet-5-5 evidence_prompt@anthropic:claude-sonnet-5-5 always_rewrite@anthropic:claude-sonnet-5-5 scope_first@anthropic:claude-sonnet-5-5 --judge anthropic:claude-haiku-4-5-20251001 --conditions A B C D --out results/sonnet
```
For an OpenAI-compatible endpoint (Azure OpenAI, vLLM, Together, Ollama), set `OPENAI_BASE_URL` and `OPENAI_API_KEY`, then use `SYSTEM@openai:MODEL`. Responses are cached in `results/.cache/`.

## Data rules
- Pilot CXR cases are **synthetic** and contain no MIMIC text.
- Real MIMIC-CXR data needs PhysioNet credentialing and the DUA. Keep it in `data/mimic/` (git-ignored), and send it only to [PhysioNet-approved LLM services](https://physionet.org/news/post/llm-responsible-use/) (e.g. Anthropic API, Azure OpenAI with human review opted out, Bedrock, Vertex). **Not** the direct OpenAI API or ChatGPT.
- COCO captions are CC-BY 4.0.

## Rebuild local data (not in git)
```bash
mkdir -p data/iu_xray && curl -L -o data/iu_xray/NLMCXR_reports.tgz https://openi.nlm.nih.gov/imgs/collections/NLMCXR_reports.tgz
tar xzf data/iu_xray/NLMCXR_reports.tgz -C data/iu_xray
python3 scripts/iu_xray_parse.py
python3 scripts/build_iu_pilot.py
python3 scripts/merge_pilot_v1.py
```
`pilot/data/pilot_v1.json` (24 examples) merges `pilot_v1_iu.json` (real IU), the COCO items, and the synthetic items from `pilot_v0.json`. It is git-ignored because IU is CC BY-NC-ND 4.0.
