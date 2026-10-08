# Running everything for $0 (updated 7 Oct 2026)

There is no lab API key and no personal spending, so everything runs on free tiers and free GPUs. Free offers change often (GitHub Models was retired on 30 Jul 2026), so **check each provider's own limits page** before a big run.

## 1. The three models + judge (all free)

| Role | Where | Why | Limit to expect |
|---|---|---|---|
| Model 1: strong closed model | **Google AI Studio** free tier, a Gemini Flash model (`gemini:<id>`) | free frontier-class model | limits shown in AI Studio after sign-in |
| Model 2: strong open-weight | **Groq** free tier, `openai/gpt-oss-120b` or a 70B Llama (`groq:<id>`) | open weights, fast | ~1,000 requests/day per model; token/day caps usually bind first |
| Model 3: small open-weight you host | **Kaggle** (free GPUs, ~30 h/week) running vLLM with an 8B model, e.g. Qwen3-8B (`vllm:<id>`) | a model you control: no quotas, no data leaving your session, also usable later for tagger training | GPU hours only |
| Judge (free text → claim actions) | a *different* family from the model being judged, e.g. Groq Llama when judging Gemini | avoids self-judging | as above |
| Backups | Cerebras free tier; OpenRouter `:free` models (50 requests/day) | if a quota runs out | |

Get model ids with `python3 scripts/list_models.py groq` (or `gemini`, `cerebras`, `openrouter --free`). Don't copy ids from blog posts.

**Your Mac (M1, 8 GB, ~7 GB free disk):** only a ~3–4B model via Ollama, so it's useful for debugging prompts offline, not for headline results.

## 2. Data rule
Free tiers may log or train on prompts. **Only public data goes to them:** MEDEC, IU X-ray, COCO, VitaminC, EditPropBench. **MIMIC never goes to a free API.** For MIMIC (if access comes), use the self-hosted Kaggle/vLLM model, which keeps data inside your session. Check the PhysioNet DUA on whether Kaggle is acceptable.

## 3. Fitting the daily quotas
One scope-first pass over all 188 MedScope examples is ~160k input tokens + ~100k output tokens. That can exceed a free model's daily token cap, so:
- **Start small:** the three core variants of every case (`--match "valid$|false$|authority$"` → 93 examples), conditions A and B.
- Responses are cached. If a daily cap hits, the run stops with a message; **run the same command the next day and it resumes.**
- Throttle with `INTEXR_RPM` (default 20 requests/minute for free providers).

```bash
export GEMINI_API_KEY=...   # aistudio.google.com -> Get API key (no billing account needed)
export GROQ_API_KEY=...     # console.groq.com -> API keys
python3 scripts/list_models.py groq
python3 scripts/run_pilot.py --data paperB/data/medec_scope_v0.json \
  --match "valid$|false$|authority$" \
  --systems no_revision oracle evidence_prompt@gemini:<flash-id> scope_first@gemini:<flash-id> \
  --judge groq:<llama-id> --conditions A B --out results/medscope_gemini
```
Do **not** attach a billing account to Google Cloud or add credits anywhere, so the free tier can't silently turn into paid usage.

## 4. Kaggle GPU recipe (model 3)
1. kaggle.com → New Notebook → Settings: **Accelerator GPU T4 x2**, **Internet on** (requires phone verification once).
2. Add a GitHub token as a Kaggle Secret named `GH_TOKEN` (the repo is private), then run:
```bash
!pip install -q vllm
from kaggle_secrets import UserSecretsClient; import os
os.environ["GH_TOKEN"] = UserSecretsClient().get_secret("GH_TOKEN")
!git clone https://$GH_TOKEN@github.com/sonak11/intexr.git
!nohup python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen3-8B --tensor-parallel-size 2 --max-model-len 8192 --port 8000 > vllm.log 2>&1 &
# wait ~3-5 min until vllm.log shows the server is up
!cd intexr && python3 scripts/fetch_external.py medec && python3 scripts/build_medec_scope.py
!cd intexr && VLLM_BASE_URL=http://localhost:8000/v1 python3 scripts/run_pilot.py --data paperB/data/medec_scope_v0.json --systems scope_first@vllm:Qwen/Qwen3-8B evidence_prompt@vllm:Qwen/Qwen3-8B --judge vllm:Qwen/Qwen3-8B --conditions A B --out results/medscope_qwen8b
```
3. Download `results/` from the notebook's output panel. (Using the same model as judge here is a compromise: re-judge with a different free model later, since cached outputs make that cheap.)
4. The same notebook later trains the small tagger (DeBERTa-style) and runs the NLI evidence-gate baseline, both free on the T4.

## 5. Other free routes worth trying (no money involved)
- **University resources:** ask Defei/IT whether the school has a GPU cluster or free cloud credits for students.
- **Research credit programs:** some providers give free API credits to student researchers on application (check current Anthropic, OpenAI, Google programs). These are slow and not guaranteed, so don't block on them.
