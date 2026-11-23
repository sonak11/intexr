#!/usr/bin/env bash
# Non-medical replication (thasos, one command). Converts ~100 source items each of EditPropBench and VitaminC
# (no human labelling: labels come from the source datasets), then runs the main comparison (conditions A and B)
# on the three models of the all-systems table, judged by the same local judge as MedScope.
#
#   source ~/intexr/scripts/thasos_env.sh && bash scripts/run_external.sh        # inside tmux; ~1 day of GPU time
#
# Resumable: every response is cached, so re-running continues where it stopped.
# Options: EPB_N / VITC_N (examples incl. valid+false variants, default 200), ONLY (models), SYSTEMS.
set -euo pipefail
cd "$(dirname "$0")/.."
for s in editpropbench vitaminc; do
  [ -n "$(ls data/external/$s 2>/dev/null)" ] || python3 scripts/fetch_external.py $s
done
[ -f external/editpropbench_intexr_v1.json ] || python3 scripts/convert_external.py editpropbench --n "${EPB_N:-200}" --suffix _v1
[ -f external/vitaminc_intexr_v1.json ] || python3 scripts/convert_external.py vitaminc --n "${VITC_N:-200}" --suffix _v1
export EPB_DATA=external/editpropbench_intexr_v1.json VITC_DATA=external/vitaminc_intexr_v1.json EXT_TAG=_v1
export STAGES="epb vitc"
export SYSTEMS="${SYSTEMS:-evidence_prompt verify_revise scope_first scope_pipeline dialogue}"
WHERE=thasos ONLY="${ONLY:-Qwen3-8B Qwen3-32B-AWQ llama-3.3-70b}" bash scripts/run_tiers.sh
python3 scripts/external_summary.py | tee results/EXTERNAL_SUMMARY.md
echo "Done. Push the results:  git add -f external/*_v1.json results/epb_v1_* results/vitc_v1_* results/EXTERNAL_SUMMARY.md"
