# IntExR — Session Handoff (written 22 Oct 2026; updated 23 Oct 2026)

## UPDATE 23 Oct, later (session 2, continued). Read this first.

**Git:** see `CLAUDE.md`. Work only on `main`, commit as sonak11 (GitHub noreply email), and add no Claude trailers.

**Model runs are live on the owner's Mac** (free tiers, public data only).
- Keys live in `~/.intexr_keys` (Mac home folder, never in the repo; `.gitignore` covers `.intexr_keys*`).
- Facts learned the hard way:
  - Python from python.org needs `Install Certificates.command`.
  - `gemini-2.5-flash` and `gemini-2.5-flash-lite` are retired (404) even though they are listed.
  - The Gemini free quota for `gemini-3.5-flash` is too small to use it as a model.
  - Groq free tier: ~200K tokens/day per model, so ~120 calls/day for gpt-oss-120b (~1.2–1.7K tokens/call).
  - Qwen on Groq needs `INTEXR_MAX_TOKENS=2000` and `reasoning_effort: none`.
- Commands, run daily until each one prints "Wrote results/RESULTS_medscope.md":
  ```
  # window 1
  export INTEXR_RPM=4 INTEXR_EXTRA_BODY_GROQ='{"reasoning_effort": "low"}'
  caffeinate -i env FREE=1 MODEL=groq:openai/gpt-oss-120b JUDGE=gemini:gemini-3.5-flash-lite bash scripts/run_v0.sh
  # window 2
  export INTEXR_RPM=2 INTEXR_MAX_TOKENS=2000 INTEXR_EXTRA_BODY_GROQ='{"reasoning_effort": "none"}'
  caffeinate -i env FREE=1 MODEL=groq:qwen/qwen3.8-27b JUDGE=gemini:gemini-3.5-flash-lite bash scripts/run_v0.sh
  ```
- `FREE=1` = 60 examples (first 20 cases × valid/false/authority) × conditions A, B × {evidence_prompt, scope_first, scope_pipeline}. The full design is for thasos (not yet logged in; the user needs Cisco Secure Client VPN `vpn.rutgers.edu` + Duo).
- When results are pushed: run `scripts/summarize_results.py` and `scripts/error_audit.py`, then fill paper §6 and novelty memo §4.

**Added in this part of the session:**
- Client robustness:
  - API errors stop the run (they are never scored as "keep");
  - waits are visible; daily caps stop the run immediately;
  - `INTEXR_EXTRA_BODY_<PROVIDER>`, `INTEXR_MAX_TOKENS`.
- New scripts:
  - `scripts/usage.py`: token use from the cache;
  - `scripts/check_preds.py`: post-run sanity check;
  - `scripts/error_audit.py`: confusion matrix + align / revise / cascade attribution.
- `docs/09_novelty_memo.md`: Oct 31 memo; §4 waits for the numbers.
- Literature matrix:
  - 14 more rows verified on the web, and MedLaSA and RaDialog venues fixed;
  - 4 new 2026 papers added (rows 56–59) after a fresh competitor search, which found no paper combining propagation with unreliable feedback;
  - 20 canonical rows remain `recall`.
- Second annotator package:
  - `annotation/medscope_annotate.html`: blind page, 24 stratified examples, neutral item ids, CSV export; tested in headless Chromium;
  - key file + `annotation/README_second_annotator.md`;
  - scoring: `annotation_tools.py agree … --key`.
- Paper:
  - appendix generated from code (`scripts/make_paper_appendix.py`: verbatim prompts + a worked example, ms-val-99, across 4 conditions);
  - Setup names the real models, the free-tier slice and the fixed judge.

---

## UPDATE 23 Oct (session 2, cloud container). Read this first; it overrides §0, §4, and §8 where they disagree.

**Environment of session 2.** It ran in a claude.ai cloud container, not on the Mac:
- no GPU, and no LLM API keys;
- the network blocks huggingface.co, api.groq.com, arxiv.org, aclanthology.org and openi.nlm.nih.gov;
- GitHub raw, generativelanguage.googleapis.com (Gemini), storage.googleapis.com and the AI2 S3 bucket (ARIES) are reachable.

So **no LLM has been run yet**. Nothing below is a model result.

**Done in session 2 (all on branch `claude/zen-pascal-0xzu4f`):**
1. **MedScope batch 3** (`paperB/proposals/medec_scope_v0_batch3.json`, 9 cases, LLM-written and UNREVIEWED). It adds depth-2 chains (diagnosis → treatment → monitoring), 3 superseding cases and 3 conflicting-evidence cases.
   - MedScope v0 is now 40 cases → 248 examples / 1,186 claims.
   - Labels D/P/K/U = 220/309/577/80.
   - P depth 1 / 2 = 250 / 59 (was 6 at depth 2).
   - U triggers evidence / dependency / feedback = 3 / 47 / 30.
   - 40 K-supported claims (was 0).
2. **Gold fix: the false variant.** Previously the claim attacked by false feedback was K/unverified. Under the guide's own step 5 it should have been U-feedback (feedback disputes it, no evidence either way). Every case now has `false_support`, an evidence item n2 that supports the attacked claim, so the claim is **K-supported** and the verdict stays `reject`. This variant now directly measures claim-level sycophancy on supported claims.
3. **New `conflicting` variant** (builder option): n2 contradicts n1 about the D claim, giving U-evidence on the D claim and U-dependency on its descendants; verdict `insufficient`.
4. **Builder asserts** that checks are satisfied by the gold revision and not by the original response.
5. **Bootstrap CIs now resample source cases** (`data.case_key`), as `docs/02` specifies. Before, they resampled examples, which made the CIs too narrow because there are ~6 variants per case.
6. **Method: `intexr/scope.py` (`scope_pipeline`)**, two LLM calls per example:
   - ALIGN (LLM): claim × evidence relations, dependencies, disputes, verdict;
   - LABEL (code): the guide's precedence; newest evidence tier wins; a split within the newest tier gives U;
   - REVISE (LLM): writes only D/U claims, and checks each P candidate (UNCHANGED → K);
   - ASSEMBLE (code): splices the revised claims in, so K claims stay verbatim by construction;
   - CHECK (code): feedback-only words must not leak into the revision; re-revise once if they do.
   - Ablations: `scope_pipeline_noprop`, `scope_pipeline_nocheck`.
7. **Baseline: `intexr/gate.py` (`evidence_gate`)**, the claim-level NLI gate (no propagation).
   - `evidence_gate@hf:<model>` runs on thasos/Kaggle; `evidence_gate@<provider:model>` uses an LLM as the NLI scorer.
   - NLI caching is built in.
8. **`tests/test_pipeline.py`**: with gold-perfect LLM stages, the pipeline reproduces the oracle on all of MedScope, pilot v0 and EditPropBench-IX. That makes the label rules executable. MEDEC-knowledge is skipped because it has no evidence by design.
9. **`scripts/summarize_results.py`**: paper tables covering the main results, the paired A−B gap with a case-level CI, P recall by depth, and validity strata; it also writes `paper1/tables/*.tex`.
10. **`scripts/run_v0.sh`**: Task 1 in one command (`SMOKE=1` for 3 examples).
11. **`scripts/label_actions.py`**: Task 6 judge calibration (sample → label in the terminal → kappa + confusion matrix).
12. **Paper 1 draft `paper1/main.tex`** (ACL style, 8 pages, compiles; PDF committed).
    - Drafted sections: abstract, intro, related work, task, benchmark, method, setup with **pre-registered hypotheses H1–H5**, results, limitations, ethics, appendix.
    - Offline baseline numbers are real. Every LLM cell is `\pending`; never fill those by hand.
    - Bib entries for EditPropBench, RevPropBench, LEDGER and Med-Stress were checked via web search; the 7 entries still marked `VERIFY` need checking.
13. Updated `docs/03` (status block) and `README.md`.

**Offline facts usable now (MedScope, condition B, case-level CIs):**
- The lexical always-accept baseline changes 72% [57–85] of the K-supported claims attacked by false feedback.
- Its change recall falls from D 0.40 to P 0.17, and to 0.10 at depth 2.

**Next session, in order:**
1. **Unblock models (only the user can do this).** Pick one path:
   - Create a free Gemini key and add `GEMINI_API_KEY` to the cloud environment; generativelanguage.googleapis.com is reachable from it. Or run on the Mac.
   - For Groq: add `GROQ_API_KEY` and allow `api.groq.com` in the environment's network settings.
   - Or: VPN → `ssh thasos` → vLLM (§6b), and run `MODEL=vllm:Qwen/Qwen3-8B bash scripts/run_v0.sh` there.
2. `SMOKE=1 MODEL=... JUDGE=... bash scripts/run_v0.sh`. Inspect `preds_scope_pipeline*` for `errors` and `preds_scope_first*` for `parse_error`, then do the full run.
3. Paste `results/RESULTS_medscope.md` into paper §6. Copy the generated `paper1/tables/main_medec_scope_v0.tex` rows into Table 2. Write H1–H5 honestly.
4. NLI gate on thasos: `evidence_gate@hf:<verified NLI id>`; needs `pip install torch transformers` there.
5. Judge calibration with `scripts/label_actions.py` on the first outputs (~100 pairs).
6. Clinician review and second annotator are still outstanding (Task 9). The batch 3 and `false_support` texts also need clinician review.
7. Optional: ARIES (s3, reachable) as the second real non-medical set.

---


Read this first in a new session. It is the single source of truth for where the project stands. Everything referenced is in this repo (`/Users/sonakshisharma/intexr`, GitHub `sonak11/intexr`, **private**).

---

## 0. TL;DR

- **Project:** Senior thesis with Prof. Metaxas (Rutgers CS). PhD mentor: **Defei**. The plan PDF is `~/Downloads/metaxas senior thesis plan.pdf`.
- **Papers:**
  - **Paper 1, IntExR-Scope:** claim-level revision benchmark + scope-first method. Target: May 2027.
  - **Paper 2, IntExR flagship:** contamination-resistant persistent learning. Target: Jan 2028.
  - **New: Paper B, MedScope:** a clinical dataset paper. Submit before Paper 1 (CHIL 2027, ~Feb; deadline unconfirmed).
- **Built so far:**
  - literature review (55 papers);
  - formal task definition;
  - annotation guide;
  - stdlib-only evaluation harness (7 systems, 4 conditions, 11 metrics, bootstrap CIs);
  - dataset checker;
  - free-tier LLM clients;
  - pilot data (24 examples);
  - MedScope v0 (31 cases → 188 examples, 873 claims);
  - external component sets (MEDEC, VitaminC, EditPropBench, 40 each).

  Everything validates, and the oracle scores 1.0.
- **NOT done:**
  - **zero real model results**: no LLM has been run yet;
  - no second annotator / κ;
  - no clinician review;
  - MIMIC-CXR access not started (user must do CITI + PhysioNet).
- **Hard constraints from the user:**
  1. **Spend no money.** Free tiers, Kaggle, and the Rutgers `thasos` GPU server only.
  2. **Be self-reliant:** don't block on Prof. Metaxas granting access or resources.
  3. Never send MIMIC to free APIs.
- **Next big win:** get real results on MedScope + pilot with free models (Gemini free tier, Groq free tier, self-hosted Qwen on thasos/Kaggle). Then add the NLI evidence-gate baseline. Then write MedScope batch 3. See §8 for the ordered task list.

---

## 1. People, constraints, preferences

- **User:** Sonakshi Sharma (they/them in notes unless told otherwise), NetID `ss4910`, Rutgers CS senior. Works aggressively in bursts; currently "a month behind" and wants to get ahead.
- **Advisor:** Prof. Metaxas. **The user does not want to depend on him for access or resources.** Still needed eventually (Defei confirmed): his input on the Paper 1 / MedScope split and on clinician reviewers. Defei said to have the cases ready before asking him.
- **PhD mentor Defei**, feedback from the meeting (~7 Oct):
  1. "Remind me what Paper 1 proposes." A reply draft exists in this chat history; summary in §2.
  2. Paper split + clinicians need the professor's input; **have cases ready before asking him**.
  3. **No lab API key.** The professor *may* reimburse later with receipts. The user then decided: **spend nothing at all**.
  4. **COCO:** keep as a baseline, switch to a harder dataset for the non-medical domain.
- **Defei's questions to answer** (draft answers were given in chat):
  - (1) which 3 models and how they're implemented;
  - (2) which dataset / how many cases;
  - (3) is there a tagger for the 4 labels.
- **User preferences:**
  - concise chat answers;
  - local-only files when asked (the meeting script docx lives in `meeting_notes/`, excluded from git via `.git/info/exclude`, **never push it**);
  - drafts, never send messages on their behalf;
  - pushes to GitHub are fine for project code/docs unless told otherwise.

## 2. The research in one paragraph
Given an original multi-claim response, prior evidence, user feedback (validity unknown), and new evidence, label every claim **D** (direct update: an evidence item itself contradicts, refines, or moots it), **P** (propagated: not addressed directly, but inferred from a D/P claim), **U** (unresolved: insufficient or conflicting evidence, a U parent, or feedback disputing it with no evidence; hedge, don't delete), or **K** (keep verbatim). Also give a feedback verdict (accept / partial / reject / insufficient) and a minimal revision.

Precedence: direct evidence > dependency > unsupported feedback > keep. **Principle: feedback is a hypothesis, evidence is the arbiter.**

**Novelty:** EditPropBench (Kruthof, arXiv 2605.02083, 2026) and RevPropBench / "What Else Needs Fixing?" (Kikuta, EMNLP 2026 Industry, arXiv 2609.03254) already have direct / cascade / protected labels but assume the edit is correct, and have no U. Our claim is the interaction of **unknown feedback validity × claim-level scope**, plus U and its propagation, plus clinical inferential dependencies and temporal scope.

**Key experiment:** condition A (verified edit) vs. B (unverified feedback + evidence) on the same claims. Conditions C (evidence only) and D (feedback only) are ablations.

## 3. Repo map (what each thing is, and its state)

```
HANDOFF.md                     this file
README.md                      layout + run commands (keep in sync)
docs/01_literature_review.md   55-paper review + coverage matrix (§10). ~35 rows marked `recall` still need verification
docs/literature_matrix.csv     matrix as CSV
docs/02_task_definition.md     formal task, I/O JSON, labels, metrics, conditions A–D, 5 open definitional questions
docs/03_semester1_plan.md      week-by-week to Oct 31 / Dec 18 (§0b data sources, §0c Paper B). Partly outdated: see §7
docs/04_annotation_guide.md    labeling procedure (incl. vague-feedback rule)
docs/05_datasets_and_paper.md  existing datasets table, our dataset plan, dataset-paper checklist (Croissant, datasheet…)
docs/06_paperB_dataset_paper.md MedScope: separation from Paper 1, design, review protocol, outline, timeline
docs/07_next_steps_and_drafts.md message drafts (Defei, Metaxas, clinician, annotator). Metaxas email ON HOLD (user wants self-reliance)
docs/08_free_compute.md        $0 plan: Gemini / Groq / Cerebras / OpenRouter free tiers, Kaggle vLLM recipe, data rules
docs/slides/                   build_update_deck.py + IntExR_update_Oct2026.pptx (Defei meeting deck; also a claude.ai Slides artifact)
intexr/  data.py               load / validate / model_view(condition A–D) / summarize / depth
         prompts.py            dialogue, evidence_prompt, always_rewrite, scope_first (JSON), claim-alignment judge
         clients.py            providers: groq gemini cerebras openrouter ollama vllm openai anthropic; cache; INTEXR_RPM throttle;
                               QuotaExhausted -> rerun resumes from cache; strips <think> blocks
         systems.py            no_revision, accept_feedback_lexical, oracle (offline); dialogue, evidence_prompt, always_rewrite, scope_first (LLM)
         metrics.py            change recall on D/P, under-revision, preservation error (K, K-supported), U F1, D/P F1,
                               verdict acc, deterministic text checks, forbidden additions, interaction-exact, bootstrap CIs
scripts/run_pilot.py           --data --systems SYSTEM@provider:model --judge --conditions A B C D --match REGEX --limit N --out
scripts/check_dataset.py       validate + balance tables + thin cells + --review markdown sheet (exit 1 on invalid)
scripts/list_models.py         list provider model ids (never copy ids from blogs)
scripts/fetch_external.py      MEDEC, VitaminC, EditPropBench -> data/external/ (git-ignored)
scripts/convert_external.py    -> external/*_intexr.json (+ valid/false feedback variants)
scripts/build_medec_scope.py   paperB/proposals/*.json + MEDEC -> paperB/data/medec_scope_v0.json (7 variant types)
scripts/iu_xray_parse.py       IU X-ray XML -> data/iu_xray/iu_reports.jsonl + candidates (540 rich)
scripts/build_iu_pilot.py      8 real-IU pilot items (contains ~40 verbatim IU sentences: OK in a private repo; must move out before going public)
scripts/merge_pilot_v1.py      IU + COCO + synthetic -> pilot/data/pilot_v1.json (git-ignored)
scripts/annotation_tools.py    blind sheet export + Cohen's kappa
scripts/mimic_candidates.py    skeleton miner for MIMIC-CXR (addenda / hedged / consecutive / RadGraph suggestive_of)
pilot/data/pilot_v0.json       16 items: 8 synthetic MIMIC-style CXR (cxr-001..008) + 8 real COCO (coco-001..008)
pilot/data/pilot_v1*.json      git-ignored (IU license): 24 items = iu-001..008 + coco + syn-001..008
paperB/proposals/              medec_scope_v0.json (8) + _batch2.json (23) + _batch3.json (9 cases). LLM-WRITTEN, NOT CLINICALLY REVIEWED
paperB/data/medec_scope_v0.json built output (248 examples)
external/                      medec / vitaminc / editpropbench _intexr.json (40 each) + README (attribution)
annotation/                    sheet_blank.csv (+inputs) for pilot_v0; sheet_v1_blank.csv git-ignored
meeting_notes/                 LOCAL ONLY (excluded via .git/info/exclude): Meeting_script_Defei_Oct2026.docx
results/                       git-ignored: offline runs, review sheets, .cache (LLM response cache)
data/                          git-ignored: iu_xray/, external/
```

Python on the Mac: `/usr/bin/python3` 3.9.6, stdlib only for the harness. `pypdf`, `python-pptx` and `python-docx` are installed with `--user`. The `rtk` hook rewrites shell commands; it's harmless.

## 4. Data inventory (current numbers, all validated)

| File | Examples | Claims | Labels D/P/K/U | Notes |
|---|---|---|---|---|
| `paperB/data/medec_scope_v0.json` | 248 (40 cases) | 1186 | 220/309/577/80 | 8 variant types; P depth: 250 at d1, 59 at d2; 5 superseding, 3 conflicting; 40 K-supported (false variant) |
| `pilot/data/pilot_v1.json` | 24 | 136 | 24/23/79/10 | iu (real IU), coco (real captions), syn (synthetic) |
| `pilot/data/pilot_v0.json` | 16 | 86 | 19/16/44/7 | the committed subset |
| `external/editpropbench_intexr.json` | 40 | 1600 | 205/103/1292/0 | valid + false variants; D = sentences stating the edited fact, P = qualifier-only |
| `external/medec_intexr.json` | 40 | 370 | 30/0/340/0 | knowledge-based (no evidence); 15 valid / 25 false |
| `external/vitaminc_intexr.json` | 40 | 160 | 45/0/86/29 | topic-diversity filter so evidence items never bear on other claims |

**Licenses:**
- MEDEC: CC BY 4.0 (redistributable; the MedScope core).
- VitaminC: CC BY-SA 3.0.
- EditPropBench: CC BY 4.0.
- COCO captions: CC BY 4.0.
- IU X-ray: CC BY-NC-ND 4.0, so **ship IDs + scripts only, never edited text**.
- MIMIC: PhysioNet credentialed DUA.

**Rebuild local data:**
```bash
cd ~/intexr
mkdir -p data/iu_xray && curl -L -o data/iu_xray/NLMCXR_reports.tgz https://openi.nlm.nih.gov/imgs/collections/NLMCXR_reports.tgz && tar xzf data/iu_xray/NLMCXR_reports.tgz -C data/iu_xray
python3 scripts/iu_xray_parse.py && python3 scripts/build_iu_pilot.py && python3 scripts/merge_pilot_v1.py
python3 scripts/fetch_external.py && for d in medec vitaminc editpropbench; do python3 scripts/convert_external.py $d --n 40; done
python3 scripts/build_medec_scope.py
python3 scripts/check_dataset.py paperB/data/medec_scope_v0.json pilot/data/pilot_v1.json external/*.json
```

## 5. Bugs found and fixed (don't reintroduce)
1. **VitaminC:** mixing before/after revisions of one page gave contradictory evidence and wrong D labels. Fix: one row per `case_id` **plus** a topic-diversity filter (content-word overlap thresholds).
2. **EditPropBench:** putting the qualifier value in the evidence turned every implied claim into D. Fix: evidence states only the explicit (non-QUALIFIER) facts. D = units whose `fact_ids` include an explicit target fact; P = the remaining required units.
3. **MEDEC:** its sentence splitter breaks mid-sentence. Fix: merge fragments that don't end in terminal punctuation; skip notes whose error sentence got merged.
4. **MEDEC checks:** checks run on the *whole* response, so check words must be absent from the original/target note. Fix: filter them.
5. **MedScope:** a forbidden addition already present in the original ("ribavirin"). The builder now asserts against this.
6. **Authority-only variants where the note itself decides** (`decidable_from_prior`): D evidence must cite `e1`, not `n1`.
7. **Vague-feedback rule** (annotation guide): generic vagueness → `insufficient`; a vague question about a specific claim that the evidence answers → `accept`.

Known quirks:
- The `accept_feedback_lexical` baseline scores well on the *outdated* variant because that feedback quotes the D sentence verbatim. That's an artefact; mention it as a shortcut example in the paper.
- The deterministic text checks are crude proxies. Replace them with a calibrated judge (§8 task 6).

## 6. Compute you can use without anyone's permission or money

### 6a. Free API tiers (public data ONLY)
- **Google AI Studio (Gemini Flash, free):** env `GEMINI_API_KEY`, spec `gemini:<id>`. No billing account.
- **Groq (free):** env `GROQ_API_KEY`, spec `groq:<id>` (gpt-oss-120b, Llama 70B, Qwen; ~1,000 req/day per model; token/day caps bind first).
- **Cerebras free** (`cerebras:`); **OpenRouter `:free` models** (`openrouter:`, 50 req/day).
- GitHub Models was **retired 30 Jul 2026**. Don't use it.
- **Status: the user has not yet created these keys.** First step of the next session: ask the user for the output of `python3 scripts/list_models.py groq` and `... gemini`.
- Data rule: free tiers may train on prompts. Only MEDEC / IU / COCO / VitaminC / EditPropBench. **Never MIMIC.**

### 6b. Rutgers `thasos` GPU server (the user has an account; this is their own resource)
- **Login:** `ssh thasos`. The `~/.ssh/config` block exists:
  ```
  Host thasos
    HostName thasos.cs.rutgers.edu
    User ss4910
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 8h
  ```
- **Authentication:** password / keyboard-interactive only (no SSH keys). **Claude must never type the password.** The user runs `ssh thasos` once in their own terminal; Claude then reuses the socket with `ssh -o BatchMode=yes thasos '<cmd>'` for 8 h.
- **Network:** on 22 Oct the hostname **did not resolve** from the Mac, so the user is probably off campus and needs the **Rutgers VPN** (Cisco AnyConnect / GlobalProtect per Rutgers OIT) before `ssh thasos`.
- **Machine:** Ubuntu 24.04, 64-core Xeon Gold 5218, 372 GB RAM, **8× Quadro RTX 6000 24 GB** (on 15 Oct GPU0 was in use by someone else, GPUs 1–7 idle), CUDA driver 12.5. No Slurm and no conda; system Python 3.12.
- **Storage:** home = `/research/cbim/vast/ss4910` (NFS, 6.1 TB free shared). `/data/local` is not readable.
- **Etiquette:** shared machine with no scheduler. Use 1–2 GPUs, pick idle ones via `nvidia-smi`, set `CUDA_VISIBLE_DEVICES`, run inside `tmux`, and don't hog GPUs for days. If Defei names lab rules, follow them.
- **MIMIC-CXR:** searched 15 Oct for mimic / physionet / cxr / chexpert / chest-xray at depth 4–5 in `/research/cbim/vast` (incl. `kd703/Datasets`, `zx149/data`), `/research/projects`, `/research/archive`, `/common`, `/filer`, `/koko`. **Not found.** The only hit was an unrelated `mimicmotion` conda env. Even if a lab copy exists, the user may only use it after their own PhysioNet credentialing + DUA.
- **Setup still to do there:**
  ```bash
  ssh thasos
  cd ~ && git clone https://github.com/sonak11/intexr.git   # private: needs a GitHub PAT or `gh auth login` on the server
  python3 -m venv ~/venv && source ~/venv/bin/activate && pip install vllm   # check torch/CUDA 12.x compatibility
  tmux new -s vllm
  CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen3-8B --max-model-len 8192 --port 8001
  # other shell, in ~/intexr:
  VLLM_BASE_URL=http://localhost:8001/v1 python3 scripts/run_pilot.py --data paperB/data/medec_scope_v0.json --systems scope_first@vllm:Qwen/Qwen3-8B evidence_prompt@vllm:Qwen/Qwen3-8B --judge vllm:Qwen/Qwen3-8B --conditions A B --out results/medscope_qwen8b
  ```
  - **Hugging Face cache:** set `HF_HOME=/research/cbim/vast/ss4910/hf` so models don't fill a small default disk.
  - **Bigger models:** a 32B model (e.g. Qwen3-32B in AWQ/GPTQ) fits on 1–2 GPUs; a 70B AWQ on 2–4 GPUs with `--tensor-parallel-size`.
  - **Note:** the Mac-side harness is stdlib, so it runs on the server's Python 3.12 as-is.
  - **MIMIC:** once access exists, run it only against self-hosted vLLM on thasos, never free APIs. Confirm the DUA allows university servers (it generally does for credentialed users).

### 6c. Kaggle (free 2×T4, ~30 h/week)
The recipe is in `docs/08_free_compute.md` §4. It needs phone verification and a `GH_TOKEN` secret. It's a backup to thasos.

### 6d. Mac (M1 8 GB, ~7 GB free disk)
Only Ollama with a ~3–4B model, for prompt debugging.

## 7. Timeline (fixed milestones) and what's slipping
- **Oct 31:** novelty review. Needs a verified literature matrix (the `recall` rows) + first A-vs-B numbers + a ≤3-page novelty memo (lit review §9 has the content). **At risk: no model results yet.**
- **Dec 18:** pilot report + frozen protocol (schema v1, guide v1, splits, metric code tag, judge calibration, sample size) for Paper 1 **and** MedScope.
- **Jan–Feb 2027:** write and submit MedScope (CHIL 2027; CHIL 2026's deadline was 4 Feb 2026, so confirm the 2027 date).
- **Apr 15 / Apr 30 / May 2027:** Paper 1 draft, then submission-ready, then submitted.
- `docs/03_semester1_plan.md` week items are partly stale:
  - PhysioNet is no longer on the critical path;
  - API access is now free tiers + thasos;
  - the Metaxas email is held until the cases are ready;
  - COCO is now a baseline only, with EditPropBench (and possibly FRUIT) as the hard non-medical set.

  Update the plan doc in the next session.

## 8. Ordered task list for the next session (do in this order)

**Task 1. First real results (highest priority; unblocks Oct 31).**
1. Ask the user to create a free Gemini key (aistudio.google.com) and a free Groq key (console.groq.com) and export them. Then run `scripts/list_models.py` for each.
2. Smoke-test on 3 examples: `--limit 3`, systems `no_revision oracle evidence_prompt@gemini:<id> scope_first@gemini:<id>`, `--judge groq:<llama-id>`, condition B. Inspect the raw outputs in `results/.../preds_*.jsonl`. Check that `scope_first` returns parseable JSON; if not, harden `prompts.parse_json` (e.g. strip trailing prose, retry once with "Return only JSON").
3. Full run on MedScope core variants: `--match "valid$|false$|authority$"` (93 examples), conditions A and B, three systems (`dialogue`, `evidence_prompt`, `scope_first`) × two models (Gemini Flash, Groq gpt-oss-120b or Llama-70B). Stay within the daily caps; reruns resume from the cache.
4. Same on `pilot/data/pilot_v1.json` (24 examples, conditions A–D) and `external/editpropbench_intexr.json` (A/B is the external novelty test).
5. Write `results/RESULTS_v0.md`: change recall D vs P, preservation error, U F1, verdict accuracy, A vs B gap, per feedback validity. **Report honestly**, including if there's no A–B gap.

**Task 2. Self-hosted open model on thasos** (once the user is on the VPN and logged in): §6b setup. Run Qwen3-8B (and if possible a 32B) on the same subsets. This is model 3 and needs no quotas.

**Task 3. NLI evidence-gate baseline** (in the thesis plan's baseline list).
- Script `scripts/nli_gate.py`: for each claim, run a public NLI model (e.g. `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` or similar; verify it on HF) against each evidence item.
- Contradiction → D, entailment → K, neutral on all items → K, or U if the feedback disputes the claim.
- Propagation: optional, via a predicted dependency (none in the simplest version, which is what shows P is hard).
- Run on thasos or Kaggle (free). Add it as system `nli_gate` in `intexr/systems.py` with precomputed predictions, or as a separate predictions file the metrics can read.

**Task 4. MedScope batch 3** (`paperB/proposals/medec_scope_v0_batch3.json`), 9–15 new cases. Target the thin cells:
- **depth-2 chains:** finding → diagnosis → plan;
- **more superseding cases:** a K claim changed by a later event;
- **genuinely ambiguous evidence → U-evidence:** currently only 4 in the pilot and 0 in MedScope's non-authority variants.

How to build:
- Pick from the MEDEC candidate list. The earlier listing is reproducible with the snippet in chat history; the command `python3 - <<EOF ... Error Flag=='1' ...` prints `Text ID | type | error => correction`.
- **Skip clinically disputable corrections** (e.g. `ms-val-253` sinusitis antibiotic, `ms-val-553` cephalexin with penicillin anaphylaxis).
- Keep `checks` words discriminative at the whole-note level, and keep `forbidden_additions` absent from the original. The builder asserts the latter.
- Rebuild, run `check_dataset.py`, and confirm the oracle scores 1.0.

**Task 5. Radiology split for MedScope.** Reuse the IU recipe (`scripts/build_iu_pilot.py`) to make about 10 more IU cases with depth-2 chains (finding → impression → recommendation), released as a build script. Keep verbatim-sentence assertions.

**Task 6. Judge calibration.** Hand-label claim actions (keep / revised / removed / hedged) on ~100 (claim, revision) pairs from Task 1 outputs, then measure agreement with the LLM judge (target κ ≥ 0.75). Build a tiny CLI to do the labelling: `scripts/label_actions.py`.

**Task 7. Non-medical hard split decision.** EditPropBench-IntExR is the current choice. Optionally evaluate FRUIT (Apache-2.0; `gs://gresearch/FRUIT/dataset`, TFRecord; public GCS is reachable over https at `storage.googleapis.com/gresearch/FRUIT/...`) or ARIES (ODC-BY; `s3://ai2-s2-research-public/aries`, public over https). Update `docs/03` §0b and the plan.

**Task 8. Docs upkeep.**
- Update `docs/03_semester1_plan.md` (stale items from §7).
- Update `README.md` (add `HANDOFF.md`, `list_models.py`, `--match/--limit`, `docs/08`).
- Verify the literature matrix's `recall` rows before Oct 31, using WebSearch/WebFetch on each paper.

**Task 9. Things only the user can do** (remind them):
- create the free API keys;
- connect to the VPN + `ssh thasos` (enter the password themselves);
- CITI "Data or Specimens Only Research" + PhysioNet credentialing (for MIMIC; optional now);
- Kaggle phone verification;
- recruit a second annotator (`annotation/sheet_blank.csv` + guide);
- eventually ask Prof. Metaxas about the paper split + clinicians, **after** cases and first results are ready (Defei's advice).

## 9. Rules / safety checklist for whoever continues
- Never type the user's passwords; never send messages or emails for them (draft only).
- **Spend no money:** no paid APIs, no billing accounts, no credit purchases.
- MIMIC text never goes to any external API, free or paid. Only self-hosted models on thasos/Kaggle, after the user's credentialing.
- IU X-ray: no redistribution of edited text. Before the repo ever goes public, move the verbatim IU sentences out of `scripts/build_iu_pilot.py`.
- All MedScope clinical content is **LLM-proposed and unreviewed**. Say so whenever it is presented.
- Don't commit `meeting_notes/`, `data/`, `results/`, or `pilot/data/pilot_v1*.json` (all ignored).
- After any data change: `python3 scripts/check_dataset.py <files>` must say OK, and the oracle must score 1.0 (`run_pilot.py --systems oracle`).

## 10. Key external links
- **Closest prior work:**
  - EditPropBench: https://arxiv.org/abs/2605.02083 · data https://huggingface.co/datasets/EditCoherenceBench/EditCoherenceBench
  - RevPropBench: https://arxiv.org/abs/2609.03254
  - LEDGER: https://aclanthology.org/2026.findings-acl.515/
- **Clinical datasets:**
  - MEDEC: https://github.com/abachaa/MEDEC
  - IU X-ray: https://openi.nlm.nih.gov/imgs/collections/NLMCXR_reports.tgz
  - ReXGradient-160K (HF click-through): https://huggingface.co/datasets/rajpurkarlab/ReXGradient-160K
  - CheXpert Plus: https://aimi.stanford.edu/datasets/chexpert-plus
- **Data rules:** PhysioNet LLM policy: https://physionet.org/news/post/llm-responsible-use/
- **Venues:** CHIL call for papers: https://chil.ahli.cc/submit/call-for-papers/
- **Meeting deck** (claude.ai Slides artifact, private): https://claude.ai/artifact/NiVjc5yyeEXAqMJiv4vcZp
