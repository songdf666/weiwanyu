#!/usr/bin/env bash
set -euo pipefail

cd /Users/sdf/Desktop/论文复现/LSCDBenchmark

TOKENIZERS_PARALLELISM=false /Users/sdf/Desktop/论文复现/.conda/lscd/bin/python \
  main.py \
  dataset=nordiachange_1 \
  dataset/split=full \
  dataset/preprocessing=raw \
  'dataset.test_on=[kjemi,egg,damp,fil,plattform]' \
  task=lscd_graded \
  task/lscd_graded@task.model=apd_compare_all \
  task/wic@task.model.wic=contextual_embedder \
  task/wic/metric@task.model.wic.similarity_metric=cosine \
  task.model.wic.ckpt=prajjwal1/bert-tiny \
  evaluation=change_graded \
  evaluation/plotter=none
