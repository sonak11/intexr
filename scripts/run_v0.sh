#!/usr/bin/env bash
# First real results (HANDOFF Task 1). One model per invocation; re-run the same command to resume after a
# free-tier daily cap (every response is cached in results/.cache).
#
#   MODEL=gemini:<id>  JUDGE=groq:<id>   bash scripts/run_v0.sh        # free tiers (public data only)
#   MODEL=vllm:Qwen/Qwen3-8B JUDGE=vllm:Qwen/Qwen3-8B VLLM_BASE_URL=http://localhost:8001/v1 bash scripts/run_v0.sh
#
# Optional: SMOKE=1 (2 examples, condition B only), TAG=<name for the results dir>, STAGES="medscope pilot epb",
#           SYSTEMS="evidence_prompt scope_pipeline" (subset), LIMIT=<n> (first n MedScope core examples).
# FREE=1    preset for free API tiers (Groq: ~200K tokens/day per model): the three systems the main claims need
#           (evidence_prompt, scope_first, scope_pipeline), MedScope only, first 20 cases x valid/false/authority
#           (LIMIT=60), conditions A and B. The full design runs on thasos (no caps).
# Fewer tokens on Groq's gpt-oss:  INTEXR_EXTRA_BODY_GROQ='{"reasoning_effort": "low"}'
# Check spending afterwards:        python3 scripts/usage.py --since 1d
set -euo pipefail
cd "$(dirname "$0")/.."
: "${MODEL:?set MODEL=provider:model (see python3 scripts/list_models.py <provider>)}"
JUDGE="${JUDGE:-$MODEL}"
TAG="${TAG:-$(echo "$MODEL" | tr ':/' '__')}"
if [ "${FREE:-0}" = 1 ]; then
  SYSTEMS="${SYSTEMS:-evidence_prompt scope_first scope_pipeline}"; STAGES="${STAGES:-medscope}"; LIMIT="${LIMIT:-60}"
fi
STAGES="${STAGES:-medscope pilot epb}"
SYSTEMS="${SYSTEMS:-dialogue evidence_prompt scope_first scope_pipeline evidence_gate}"
SYS=""; for x in $SYSTEMS; do SYS="$SYS $x@$MODEL"; done
LIM=""; [ -n "${LIMIT:-}" ] && LIM="--limit $LIMIT"
OFF="no_revision oracle"
CORE='valid$|false$|authority$|conflicting$'   # 123 MedScope examples: the four cells the A/B claim rests on

if [ "${SMOKE:-0}" = 1 ]; then
  python3 scripts/run_pilot.py --data paperB/data/medec_scope_v0.json --limit 2 --systems $OFF $SYS \
    --judge "$JUDGE" --conditions B --out "results/smoke_$TAG"
  echo; python3 scripts/check_preds.py "results/smoke_$TAG" || true; python3 scripts/usage.py --since 1h
  exit 0
fi
for s in $STAGES; do
  case $s in
    medscope) python3 scripts/run_pilot.py --data paperB/data/medec_scope_v0.json --match "$CORE" $LIM \
                --systems $OFF $SYS --judge "$JUDGE" --conditions A B --out "results/medscope_$TAG" ;;
    pilot)    f=pilot/data/pilot_v1.json; [ -f $f ] || f=pilot/data/pilot_v0.json
              python3 scripts/run_pilot.py --data $f --systems $OFF $SYS --judge "$JUDGE" \
                --conditions A B C D --out "results/pilot_$TAG" ;;
    epb)      python3 scripts/run_pilot.py --data external/editpropbench_intexr.json \
                --systems $OFF $SYS --judge "$JUDGE" --conditions A B --out "results/epb_$TAG" ;;
  esac
done
python3 scripts/summarize_results.py --data paperB/data/medec_scope_v0.json --runs results/medscope_* \
  --out results/RESULTS_medscope.md --tex paper1/tables >/dev/null
python3 scripts/summarize_results.py --data external/editpropbench_intexr.json --runs results/epb_* \
  --out results/RESULTS_epb.md --tex paper1/tables >/dev/null || true
echo "Wrote results/RESULTS_medscope.md, results/RESULTS_epb.md and paper1/tables/main_*.tex"
