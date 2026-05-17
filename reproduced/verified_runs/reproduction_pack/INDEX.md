# Reproduction Pack

This directory organizes the locally verified reproduction state for two papers:

- ACL 2023: `Interpretable Word Sense Representations via Definition Generation: The Case of Semantic Change Analysis`
- EACL 2024 tutorial: `Computational modeling of semantic change`

## Directory Layout

- `acl2023_interpretable_definition_generation/`
- `eacl2024_semantic_change_benchmark/`

## Quick Status

| Paper | Local status | Actual local run | Main output |
| --- | --- | --- | --- |
| ACL 2023 | runnable | semantic-change case on 3 real target words, CoDWoE English trial benchmark, plus smoke test | `acl2023_interpretable_definition_generation/artifacts/semantic_change_case/sense_labels.tsv` and `acl2023_interpretable_definition_generation/artifacts/codwoe_en_trial/en_trial_metrics.tsv` |
| EACL 2024 | runnable | LSCD benchmark on `nordiachange_1` with 5 target words | `eacl2024_semantic_change_benchmark/artifacts/result.json` |

## Important Distinction

- The ACL 2023 folder now contains a smoke test, a real semantic-change case study on official benchmark-style data, and an extra CoDWoE English trial benchmark with gold-reference metrics. It still does **not** contain the paper's full WordNet/Oxford/full-CoDWoE suite.
- The EACL 2024 paper is a tutorial/benchmark paper. The local run uses the benchmark framework plus an official benchmark dataset configuration that was reachable from this machine.
- `testwug_en_111` was not used in the final verified EACL run because `zenodo.org` was unreachable from this machine during reproduction.

## Machine-Readable Summary

See `manifest.tsv`.
