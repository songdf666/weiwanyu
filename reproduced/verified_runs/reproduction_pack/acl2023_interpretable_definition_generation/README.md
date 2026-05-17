# ACL 2023 Reproduction

## Paper

- Title: `Interpretable Word Sense Representations via Definition Generation: The Case of Semantic Change Analysis`
- Official paper: `https://aclanthology.org/2023.acl-long.176/`
- Official code repo: `https://github.com/ltgoslo/definition_modeling`
- Local repo: `/Users/sdf/Desktop/论文复现/definition_modeling`
- Local commit: `f7daddecdd86ad07067e578978cf809bfc152cd9`

## What Was Actually Run Locally

This local reproduction now contains three layers:

1. a smoke test on a tiny custom input
2. a semantic-change case study on real benchmark-style usage data
3. a gold-reference benchmark layer on `CoDWoE` English trial

Together they cover:

- repository runnable verification
- the paper's semantic-change analysis workflow
- an additional definition-generation evaluation with gold definitions

## Data And Inputs

### 1. Smoke Test

File format used locally:

- column 1: `Targets`
- column 2: `Context`

Input files:

- `artifacts/sample_input.tsv`

Local input examples:

| Targets | Context |
| --- | --- |
| `bank` | `He sat on the bank of the river and watched the water.` |
| `mouse` | `The mouse clicked twice because the left button was stuck.` |

### 2. Semantic Change Case On Real Data

Source benchmark-style dataset:

- `/Users/sdf/Desktop/论文复现/LSCDBenchmark/wug/nor_dia_change/subset1`

Prepared input file:

- `artifacts/semantic_change_case/semantic_change_subset.tsv`

Columns:

- `id`
- `word`
- `pos`
- `date`
- `period`
- `cluster`
- `target_indices`
- `Targets`
- `Context`

Prepared subset size:

- `65` usages
- `3` target words

Words used in the semantic-change case:

- `kjemi`
- `damp`
- `plattform`

Cluster structure in the prepared subset:

- `kjemi`: 1 cluster
- `damp`: 4 clusters
- `plattform`: 4 clusters

### 3. CoDWoE English Trial Gold Benchmark

Source benchmark data:

- `/Users/sdf/Desktop/论文复现/acl2023_benchmarks/codwoe/trial_data/en.trial.complete.json`

Prepared benchmark input:

- `artifacts/codwoe_en_trial/en_trial_input.tsv`

Columns:

- `id`
- `Targets`
- `Context`
- `Definition`
- `POS`
- `Type`

Prepared benchmark size:

- `200` English trial examples

This layer is important because:

- it uses gold reference definitions
- it adds metric-based evaluation
- it is closer to the repository's original definition-generation benchmark setting than the semantic-change case alone

## Outputs

### 1. Smoke Test

Output files:

- `artifacts/sample_predicted.tsv.gz`
- `artifacts/sample_predicted_preview.tsv`

The script writes:

- original target
- original context
- prompt-augmented context in `Real_Contexts`
- generated definition in `Generated_Definition`

Local generated examples:

| Targets | Generated_Definition |
| --- | --- |
| `bank` | `the side of a body of water that is a source of water` |
| `mouse` | `A device that controls a computer, especially a computer's keyboard.` |

### 2. Semantic Change Case

Main outputs:

- `artifacts/semantic_change_case/generated_definitions.tsv`
- `artifacts/semantic_change_case/generated_definitions_for_labels.tsv`
- `artifacts/semantic_change_case/definition_embeddings.npz`
- `artifacts/semantic_change_case/sense_labels.tsv`

Recovered sense labels:

| Targets | Definitions | Clusters |
| --- | --- | --- |
| `damp` | `A mixture of a liquid and a gas, especially a liquid containing a volatile or odorless substance.` | `0` |
| `kjemi` | `A kjim.` | `0` |
| `plattform` | `A platform.` | `0` |
| `plattform` | `A platform.` | `1` |
| `plattform` | `A platform.` | `2` |

Some very small senses were labeled as:

- `Too few examples to generate a proper definition!`

This is consistent with the script logic, which requires at least 3 examples per sense to choose a stable prototype.

### 3. CoDWoE English Trial Benchmark

Main outputs:

- `artifacts/codwoe_en_trial/en_trial_input.tsv`
- `artifacts/codwoe_en_trial/en_trial_generated.tsv`
- `artifacts/codwoe_en_trial/en_trial_metrics.tsv`

Measured scores:

| Metric | Score |
| --- | --- |
| `sacrebleu` | `6.5549` |
| `rougeL` | `0.2190` |
| `exact_match` | `0.0000` |

Example generated rows:

| id | Targets | Gold Definition | Generated_Definition |
| --- | --- | --- | --- |
| `en.trial.1` | `beautiful` | `Pleasant ; clear .` | `Very good ; excellent ; excellent.` |
| `en.trial.2` | `cocktail` | `A mixture of other substances or things .` | `A mixture of different substances.` |
| `en.trial.3` | `institutionalized` | `Having been established as an institution .` | `Having been established in a particular institution.` |

Interpretation:

- the pipeline can run end to end on a gold-reference benchmark split
- the model outputs are often semantically related to the gold glosses
- the scores are still far from a "fully reproduced full benchmark suite" result because only the English trial split was used here

## Commands Used

Reusable scripts:

- `commands/run_smoke_test.sh`
- `commands/run_semantic_change_pipeline.sh`
- `commands/run_codwoe_trial_benchmark.sh`

Equivalent smoke-test command:

```bash
cd /Users/sdf/Desktop/论文复现/definition_modeling
TOKENIZERS_PARALLELISM=false /Users/sdf/Desktop/论文复现/.conda/defgen/bin/python \
  code/modeling/generate_t5.py \
  --model ltg/flan-t5-definition-en-base \
  --testdata sample_input.tsv \
  --bsize 1 \
  --save sample_predicted.tsv.gz
```

Equivalent CoDWoE benchmark command:

```bash
cd /Users/sdf/Desktop/论文复现/definition_modeling
TOKENIZERS_PARALLELISM=false /Users/sdf/Desktop/论文复现/.conda/defgen/bin/python \
  code/modeling/generate_t5.py \
  --model ltg/flan-t5-definition-en-base \
  --testdata /Users/sdf/Desktop/论文复现/reproduction_pack/acl2023_interpretable_definition_generation/artifacts/codwoe_en_trial/en_trial_input.tsv \
  --bsize 4 \
  --save /Users/sdf/Desktop/论文复现/reproduction_pack/acl2023_interpretable_definition_generation/artifacts/codwoe_en_trial/en_trial_generated.tsv

TOKENIZERS_PARALLELISM=false /Users/sdf/Desktop/论文复现/.conda/defgen/bin/python \
  code/evaluation/evaluate_simple.py \
  --data_path /Users/sdf/Desktop/论文复现/reproduction_pack/acl2023_interpretable_definition_generation/artifacts/codwoe_en_trial/en_trial_generated.tsv \
  --output /Users/sdf/Desktop/论文复现/reproduction_pack/acl2023_interpretable_definition_generation/artifacts/codwoe_en_trial/en_trial_metrics.tsv \
  --metrics sacrebleu rougeL exact_match
```

## Benchmark Data Mentioned By The Paper/Repo

The repository README points to these datasets for actual paper-style runs:

- WordNet
- Oxford
- CoDWoE

Local status:

- semantic-change application workflow: run on real benchmark-style usage data
- CoDWoE English trial: downloaded, converted, generated, and evaluated locally
- WordNet: not run in this workspace
- Oxford: not run in this workspace
- full CoDWoE benchmark suite: not fully run in this workspace

So the current local ACL result is:

- clearly stronger than a pure smoke test
- strong enough to claim basic reproduction of the paper's core semantic-change method
- stronger than the previous state because it now includes one gold-reference benchmark layer with automatic metrics
- still short of the paper's full large-scale benchmark coverage

## Local Compatibility Changes

Patched files:

- `/Users/sdf/Desktop/论文复现/definition_modeling/code/modeling/generate_t5.py`
- `/Users/sdf/Desktop/论文复现/definition_modeling/code/evaluation/evaluate_simple.py`
- `/Users/sdf/Desktop/论文复现/definition_modeling/code/proto_explanations/embed_definitions.py`
- `/Users/sdf/Desktop/论文复现/definition_modeling/code/proto_explanations/sense_label.py`
- `/Users/sdf/Desktop/论文复现/definition_modeling/code/extract_usage_embeddings.py`
- `/Users/sdf/Desktop/论文复现/definition_modeling/code/definition_pair_similarity.py`

Changes:

- convert `--sampling` and `--filter` from `0/1` integers into booleans before calling `transformers.generate()`
- replace old `.eval_metrics()` calls with `.eval()`
- lazily load only requested evaluation metrics so `evaluate_simple.py` does not fail on unused metric dependencies

Reason:

- on this machine, the unpatched generation path could return `None` and crash during decode
- the repository used older model/evaluation interfaces that are not fully compatible with the current local environment

Additional packages installed in the ACL environment for verified runs:

- `matplotlib==3.8.4`
- `rouge_score==0.1.2`
- `absl-py==2.1.0`
- `sacrebleu==2.4.2`
- `python-docx==1.1.2`

## Files In This Folder

- `artifacts/sample_input.tsv`
- `artifacts/sample_predicted.tsv.gz`
- `artifacts/sample_predicted_preview.tsv`
- `artifacts/semantic_change_case/semantic_change_subset.tsv`
- `artifacts/semantic_change_case/generated_definitions.tsv`
- `artifacts/semantic_change_case/generated_definitions_for_labels.tsv`
- `artifacts/semantic_change_case/definition_embeddings.npz`
- `artifacts/semantic_change_case/sense_labels.tsv`
- `artifacts/codwoe_en_trial/en_trial_input.tsv`
- `artifacts/codwoe_en_trial/en_trial_generated.tsv`
- `artifacts/codwoe_en_trial/en_trial_metrics.tsv`
- `commands/run_smoke_test.sh`
- `commands/prepare_semantic_change_subset.py`
- `commands/postprocess_generated_definitions.py`
- `commands/run_semantic_change_pipeline.sh`
- `commands/prepare_codwoe_trial.py`
- `commands/run_codwoe_trial_benchmark.sh`
