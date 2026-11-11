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
#           GPUS="2,3" (on thasos: which GPUs to use; default = the ones with the most free memory).
# Results land in results/medscope_<provider>_<model>/ and the scale table in results/RESULTS_medscope.md.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${WHERE:?set WHERE=groq|gemini|thasos|credits}"
export JUDGE="${JUDGE:-gemini:gemini-3.5-flash-lite}" SPLIT="${SPLIT:-dev}" FREE="${FREE:-1}"
PORT=8000
LOG=""
serve() {  # serve <hf model> <tp> <port> <gpus>; sets SPID and LOG
  mkdir -p results; LOG="results/vllm_$(echo "$1" | tr '/' '_').log"
  echo "starting vLLM for $1 on GPU(s) $4 (log: $LOG)"
  CUDA_VISIBLE_DEVICES="$4" nohup vllm serve "$1" --dtype half --tensor-parallel-size "$2" --port "$3" \
    --max-model-len 8192 --gpu-memory-utilization 0.85 > "$LOG" 2>&1 &
  SPID=$!
}
wait_up() {  # wait_up <port> <pid>: stop at once if the server dies; print progress while it loads
  for i in $(seq 1 180); do
    curl -sf "http://localhost:$1/v1/models" >/dev/null && { echo "vLLM is up on port $1"; return 0; }
    if ! kill -0 "$2" 2>/dev/null; then
      echo "!! vLLM exited before it came up. Last lines of $LOG:" >&2; tail -25 "$LOG" >&2; return 1
    fi
    [ $((i % 6)) = 0 ] && echo "  still loading ($((i / 6)) min): $(tail -1 "$LOG" | cut -c1-150)"
    sleep 10
  done
  echo "!! vLLM on port $1 did not come up in 30 min; see $LOG" >&2; return 1
}
pick_gpus() {  # pick_gpus <n>: the n GPUs with the most free memory (or $GPUS if set)
  if [ -n "${GPUS:-}" ]; then echo "$GPUS"; return; fi
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits | sort -t, -k2 -nr | head -n "$1" \
    | cut -d, -f1 | tr -d ' ' | paste -sd, -
}
if [ "$WHERE" = thasos ]; then
  command -v vllm >/dev/null || { echo "vllm is not installed here. Install it first:
  python3 -m venv ~/vllm-env && source ~/vllm-env/bin/activate && pip install vllm
then re-run this command (with the venv activated)."; exit 1; }
  nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv
fi
JPID=""
if [ "$WHERE" = thasos ] && [ -n "${JUDGE_LOCAL:-}" ]; then
  serve "$JUDGE_LOCAL" 2 8001 "${JUDGE_GPUS:-6,7}"; JPID=$SPID; wait_up 8001 "$JPID" || exit 1
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
            serve "$model" "$tp" $PORT "$(pick_gpus "$tp")"; pid=$SPID
            if ! wait_up $PORT "$pid"; then kill "$pid" 2>/dev/null || true; echo "!! skipping $spec"; continue; fi
            export VLLM_BASE_URL="http://localhost:$PORT/v1" ;;
  esac
  MODEL="$spec" bash scripts/run_v0.sh < /dev/null || echo "!! $spec stopped (daily cap or error); re-run later to resume"
  if [ "$where" = thasos ]; then kill "$pid" 2>/dev/null || true; sleep 15; fi
done
python3 scripts/summarize_results.py --data paperB/data/medec_scope_v0.json --runs results/medscope_* \
  --tiers configs/model_tiers.tsv --out results/RESULTS_medscope.md --tex paper1/tables >/dev/null
echo "Scale table: results/RESULTS_medscope.md (section 'By model scale')"
