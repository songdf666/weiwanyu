#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/sdf/Desktop/论文复现"
ACL_REPO="$ROOT/definition_modeling"
DATA_ROOT="$ROOT/LSCDBenchmark/wug/nor_dia_change/subset1"
OUT_DIR="$ROOT/reproduction_pack/acl2023_interpretable_definition_generation/artifacts/semantic_change_case"
PY="$ROOT/.conda/defgen/bin/python"

mkdir -p "$OUT_DIR"

"$PY" "$ROOT/reproduction_pack/acl2023_interpretable_definition_generation/commands/prepare_semantic_change_subset.py" \
  --dataset-root "$DATA_ROOT" \
  --output "$OUT_DIR/semantic_change_subset.tsv" \
  --words kjemi damp plattform

cd "$ACL_REPO"

TOKENIZERS_PARALLELISM=false "$PY" code/modeling/generate_t5.py \
  --model ltg/flan-t5-definition-en-base \
  --testdata "$OUT_DIR/semantic_change_subset.tsv" \
  --bsize 2 \
  --save "$OUT_DIR/generated_definitions.tsv"

"$PY" "$ROOT/reproduction_pack/acl2023_interpretable_definition_generation/commands/postprocess_generated_definitions.py" \
  --input "$OUT_DIR/generated_definitions.tsv" \
  --output "$OUT_DIR/generated_definitions_for_labels.tsv"

TOKENIZERS_PARALLELISM=false "$PY" code/proto_explanations/embed_definitions.py \
  --input_path "$OUT_DIR/generated_definitions_for_labels.tsv" \
  --key_to_entry_id id \
  --output_path "$OUT_DIR/definition_embeddings"

TOKENIZERS_PARALLELISM=false "$PY" code/proto_explanations/sense_label.py \
  --data "$OUT_DIR/generated_definitions_for_labels.tsv" \
  --save text \
  --output "$OUT_DIR/sense_labels.tsv"
