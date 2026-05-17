#!/usr/bin/env bash
set -euo pipefail

cd /Users/sdf/Desktop/论文复现/definition_modeling

TOKENIZERS_PARALLELISM=false /Users/sdf/Desktop/论文复现/.conda/defgen/bin/python \
  code/modeling/generate_t5.py \
  --model ltg/flan-t5-definition-en-base \
  --testdata sample_input.tsv \
  --bsize 1 \
  --save sample_predicted.tsv.gz
