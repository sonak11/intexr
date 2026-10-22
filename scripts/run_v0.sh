#!/usr/bin/env bash
# First real results (HANDOFF Task 1). One model per invocation; re-run the same command to resume after a
# free-tier daily cap (every response is cached in results/.cache).
#
#   MODEL=gemini:<id>  JUDGE=groq:<id>   bash scripts/run_v0.sh        # free tiers (public data only)
#   MODEL=vllm:Qwen/Qwen3-8B JUDGE=vllm:Qwen/Qwen3-8B VLLM_BASE_URL=http://localhost:8001/v1 bash scripts/run_v0.sh
#
# Optional: SMOKE=1 (3 examples, condition B only), TAG=<name for the results dir>, STAGES="medscope pilot epb"
set -euo pipefail
cd "$(dirname "$0")/.."
: "${MODEL:?set MODEL=provider:model (see python3 scripts/list_models.py <provider>)}"
JUDGE="${JUDGE:-$MODEL}"
TAG="${TAG:-$(echo "$MODEL" | tr ':/' '__')}"
STAGES="${STAGES:-medscope pilot epb}"
SYS="dialogue@$MODEL evidence_prompt@$MODEL scope_first@$MODEL scope_pipeline@$MODEL evidence_gate@$MODEL"
OFF="no_revision oracle"
CORE='valid$|false$|authority$|conflicting$'   # 123 MedScope examples: the four cells the A/B claim rests on

if [ "${SMOKE:-0}" = 1 ]; then
  python3 scripts/run_pilot.py --data paperB/data/medec_scope_v0.json --limit 3 --systems $OFF $SYS \
    --judge "$JUDGE" --conditions B --out "results/smoke_$TAG"
  echo; echo "Inspect results/smoke_$TAG/preds_*.jsonl: scope_first / scope_pipeline must have no parse_error / errors."
  exit 0
fi
for s in $STAGES; do
  case $s in
    medscope) python3 scripts/run_pilot.py --data paperB/data/medec_scope_v0.json --match "$CORE" \
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
