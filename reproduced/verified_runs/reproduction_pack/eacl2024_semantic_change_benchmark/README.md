# EACL 2024 Reproduction

## Paper

- Title: `Computational modeling of semantic change`
- Official paper page: `https://aclanthology.org/2024.eacl-tutorials.1/`
- Official benchmark repo: `https://github.com/ChangeIsKey/LSCDBenchmark`
- Local repo: `/Users/sdf/Desktop/论文复现/LSCDBenchmark`
- Local commit: `dc9650aea062cbf3750bbba3da9b3a3737955e2e`

## What This Paper Is In Practice

This paper is a tutorial/benchmark paper, not a single-model paper.  
The local reproduction therefore targets the benchmark framework plus one verified benchmark run.

## What Was Actually Run Locally

Verified run:

- Framework: `LSCDBenchmark`
- Task: `lscd_graded`
- Model: `apd_compare_all`
- WiC model: `contextual_embedder`
- Similarity metric: `cosine`
- Transformer checkpoint: `prajjwal1/bert-tiny`
- Dataset config: `nordiachange_1`
- Actual data root: `/Users/sdf/Desktop/论文复现/LSCDBenchmark/wug/nor_dia_change/subset1`
- Tested target words: `kjemi`, `egg`, `damp`, `fil`, `plattform`

## Benchmark Data Used In The Verified Run

Raw data files:

- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/wug/nor_dia_change/subset1/data/kjemi/uses.tsv`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/wug/nor_dia_change/subset1/data/egg/uses.tsv`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/wug/nor_dia_change/subset1/data/damp/uses.tsv`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/wug/nor_dia_change/subset1/data/fil/uses.tsv`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/wug/nor_dia_change/subset1/data/plattform/uses.tsv`

Gold label source:

- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/wug/nor_dia_change/subset1/stats/opt/stats_groupings.tsv`

Copied subset files in this folder:

- `artifacts/input_words.txt`
- `artifacts/data_paths.txt`
- `artifacts/benchmark_labels_subset.tsv`
- `artifacts/dataset_nordiachange_1.yaml`

The local label subset is:

| lemma | change_graded |
| --- | --- |
| `damp` | `0.4636346501091604` |
| `egg` | `0.0` |
| `fil` | `0.8302961801327811` |
| `kjemi` | `0.0` |
| `plattform` | `0.8745367750924979` |

## Input And Output

Input to the benchmark command:

- dataset config: `nordiachange_1`
- selected words: `kjemi`, `egg`, `damp`, `fil`, `plattform`
- model config: `apd_compare_all + contextual_embedder + cosine`

Output files from the verified run:

- `artifacts/result.json`
- `artifacts/predictions.csv`

Verified result:

- metric: `spearmanr`
- score: `0.35909242322980395`

Verified predictions:

| instance | prediction | label |
| --- | --- | --- |
| `damp` | `-0.9232298441169676` | `0.4636346501091604` |
| `egg` | `-0.9112577177276296` | `0.0` |
| `fil` | `-0.8987084513853404` | `0.8302961801327811` |
| `kjemi` | `-0.9326321364434298` | `0.0` |
| `plattform` | `-0.9151633534549681` | `0.8745367750924979` |

## Command Used

Reusable script:

- `commands/run_verified_subset.sh`

Equivalent command:

```bash
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
```

## Blocked / Not Used In Final Verified Run

The repository's tiny test dataset `testwug_en_111` was the first intended benchmark target, but it was not usable here because:

- the code tries to download it from `zenodo.org`
- `zenodo.org` was unreachable from this machine during reproduction

So the final verified benchmark run uses `nordiachange_1`, which was reachable through GitHub.

## Local Compatibility Changes

Patched files:

- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/src/wic/__init__.py`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/src/wic/contextual_embedder.py`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/src/wsi/__init__.py`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/src/lscd/__init__.py`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/src/lemma.py`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/src/dataset.py`
- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/conf/dataset/nordiachange_1.yaml`

Why they were needed:

- make optional dependencies lazy so unrelated modules do not fail at import time
- support official datasets that ship `*.tsv` instead of `*.csv`
- align `nordiachange_1` grouping names with the current upstream dataset

## Files In This Folder

- `artifacts/result.json`
- `artifacts/predictions.csv`
- `artifacts/benchmark_labels_subset.tsv`
- `artifacts/input_words.txt`
- `artifacts/data_paths.txt`
- `artifacts/dataset_nordiachange_1.yaml`
- `commands/run_verified_subset.sh`
