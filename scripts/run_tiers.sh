#!/usr/bin/env bash
# Scale study: run every model in configs/model_tiers.tsv whose 'where' matches WHERE, one after another, through
# scripts/run_v0.sh (same systems, split and conditions for every model). Re-run to resume: responses are cached.
#
#   WHERE=groq   bash scripts/run_tiers.sh        # free API models (daily caps: re-run each day until done)
#   WHERE=gemini bash scripts/run_tiers.sh
#   WHERE=thasos bash scripts/run_tiers.sh        # on thasos: starts vLLM for each model, runs it, stops it
#   WHERE=credits bash scripts/run_tiers.sh       # Claude / closed GPT, once API credits exist (SPLIT=test only)
#
# Optional: ONLY="Qwen3-8B gpt-oss-20b" (substring filter on spec), SPLIT (default dev), SYSTEMS, CONDITIONS,
#           JUDGE (default gemini:gemini-3.5-flash-lite; on thasos you can set JUDGE_LOCAL=Qwen/Qwen3-32B-AWQ to serve a
#           fixed local judge on port 8001, GPUs 6-7, so the Gemini judge quota is not the bottleneck).
# Results land in results/medscope_<provider>_<model>/ and the scale table in results/RESULTS_medscope.md.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${WHERE:?set WHERE=groq|gemini|thasos|credits}"
export JUDGE="${JUDGE:-gemini:gemini-3.5-flash-lite}" SPLIT="${SPLIT:-dev}" FREE="${FREE:-1}"
PORT=8000
serve() {  # serve <hf model> <tp> <port> <gpus>
  CUDA_VISIBLE_DEVICES="$4" nohup vllm serve "$1" --dtype half --tensor-parallel-size "$2" --port "$3" \
    --max-model-len 8192 --gpu-memory-utilization 0.90 > "results/vllm_$(echo "$1" | tr '/' '_').log" 2>&1 &
  echo $!
}
wait_up() {  # wait_up <port>
  for _ in $(seq 1 180); do curl -sf "http://localhost:$1/v1/models" >/dev/null && return 0; sleep 10; done
  echo "vLLM on port $1 did not come up; see results/vllm_*.log" >&2; return 1
}
JPID=""
if [ "$WHERE" = thasos ] && [ -n "${JUDGE_LOCAL:-}" ]; then
  JPID=$(serve "$JUDGE_LOCAL" 2 8001 6,7); wait_up 8001
  export JUDGE="vllm2:$JUDGE_LOCAL" VLLM2_BASE_URL="http://localhost:8001/v1"
  export INTEXR_EXTRA_BODY_VLLM2='{"chat_template_kwargs": {"enable_thinking": false}}'
fi
trap '[ -n "$JPID" ] && kill $JPID 2>/dev/null || true' EXIT
grep -v '^#' configs/model_tiers.tsv | tail -n +2 | while IFS=$'\t' read -r spec family params tier where tp review extra maxtok notes; do
  [ "$where" = "$WHERE" ] || continue
  if [ -n "${ONLY:-}" ]; then hit=0; for o in $ONLY; do [[ "$spec" == *"$o"* ]] && hit=1; done; [ $hit = 1 ] || continue; fi
  if [[ "$spec" == *CHECK_* ]]; then echo "skip $spec: fill in the model id in configs/model_tiers.tsv"; continue; fi
  echo; echo "=== $spec  ($family, tier $tier) ==="
  prov="${spec%%:*}"; model="${spec#*:}"
  export "INTEXR_EXTRA_BODY_$(echo "$prov" | tr a-z A-Z)=$extra"
  if [ "$maxtok" != "-" ]; then export INTEXR_MAX_TOKENS="$maxtok"; else unset INTEXR_MAX_TOKENS; fi
  case $where in
    groq) export INTEXR_RPM="${INTEXR_RPM:-4}" ;;
    thasos) export INTEXR_RPM=0
            gpus=$(seq -s, 0 $((tp - 1))); pid=$(serve "$model" "$tp" $PORT "$gpus"); wait_up $PORT
            export VLLM_BASE_URL="http://localhost:$PORT/v1" ;;
  esac
  MODEL="$spec" bash scripts/run_v0.sh < /dev/null || echo "!! $spec stopped (daily cap or error); re-run later to resume"
  if [ "$where" = thasos ]; then kill "$pid" 2>/dev/null || true; sleep 15; fi
done
python3 scripts/summarize_results.py --data paperB/data/medec_scope_v0.json --runs results/medscope_* \
  --tiers configs/model_tiers.tsv --out results/RESULTS_medscope.md --tex paper1/tables >/dev/null
echo "Scale table: results/RESULTS_medscope.md (section 'By model scale')"
