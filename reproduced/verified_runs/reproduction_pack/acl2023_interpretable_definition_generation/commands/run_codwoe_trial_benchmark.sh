#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/sdf/Desktop/论文复现"
OUT_DIR="$ROOT/reproduction_pack/acl2023_interpretable_definition_generation/artifacts/codwoe_en_trial"
ACL_REPO="$ROOT/definition_modeling"
PY="$ROOT/.conda/defgen/bin/python"

mkdir -p "$OUT_DIR"

"$PY" "$ROOT/reproduction_pack/acl2023_interpretable_definition_generation/commands/prepare_codwoe_trial.py" \
  --input-json "$ROOT/acl2023_benchmarks/codwoe/trial_data/en.trial.complete.json" \
  --output-tsv "$OUT_DIR/en_trial_input.tsv"

cd "$ACL_REPO"

TOKENIZERS_PARALLELISM=false "$PY" code/modeling/generate_t5.py \
  --model ltg/flan-t5-definition-en-base \
  --testdata "$OUT_DIR/en_trial_input.tsv" \
  --bsize 4 \
  --save "$OUT_DIR/en_trial_generated.tsv"

TOKENIZERS_PARALLELISM=false "$PY" code/evaluation/evaluate_simple.py \
  --data_path "$OUT_DIR/en_trial_generated.tsv" \
  --output "$OUT_DIR/en_trial_metrics.tsv" \
  --metrics sacrebleu rougeL exact_match
