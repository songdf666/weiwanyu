# 论文与可复现代码索引

本文件明确区分两类对象：

- **论文**：研究论文、学位论文或本地复现包对应的论文组，只记录题录、官方链接和本地候选 PDF 路径。
- **论文对应的可复现代码**：放在 `reproduced/` 下的轻量源码快照，每个目录有 `SOURCE_NOTE.md` 和 `PAPER.md`。

为避免公开仓库中的版权风险，这里默认保存论文题录、官方链接和本地候选 PDF 路径，不直接提交 PDF 全文。

## 论文清单

| 编号 | 类型 | 论文/论文组 | 年份/venue | 官方链接 | 本地候选文件 |
| --- | --- | --- | --- | --- | --- |
| `histwords_acl2016` | paper | Diachronic Word Embeddings Reveal Statistical Laws of Semantic Change | 2016, ACL | https://aclanthology.org/P16-1141/ | `委婉语/ACL与高分期刊/期刊文件/《历时词向量揭示语义变化的统计规律》.pdf` |
| `scalable_semantic_shift_naacl2021` | paper | Scalable and Interpretable Semantic Change Detection | 2021, NAACL | https://aclanthology.org/2021.naacl-main.369/ | `委婉语/语义计算/2021.naacl-main.369.pdf` |
| `tempobert_wsdm2022` | paper | Time Masking for Temporal Language Models | 2022, WSDM | https://arxiv.org/abs/2110.06366 | 待确认 |
| `lscd_benchmark` | paper | Human and Computational Measurement of Lexical Semantic Change | 2023, PhD thesis / benchmark reference | http://dx.doi.org/10.18419/opus-12833 | 待确认 |
| `scdisc_hplt_2026` | paper | DHPLT: large-scale multilingual diachronic corpora and word representations for semantic change modelling | 2026, LChange | https://arxiv.org/abs/2602.11968 | 待确认 |
| `semantic_change_discovery_emnlp2025` | paper | Semantic Change Quantification Methods Struggle with Discovery in the Wild | 2025, EMNLP | https://aclanthology.org/2025.emnlp-main.1791/ | `论文复现/papers/2025-semantic-change-discovery/misc/slides.pdf` |
| `dhplt_scdisc_2026_minimal` | paper | DHPLT: large-scale multilingual diachronic corpora and word representations for semantic change modelling | 2026, LChange | https://arxiv.org/abs/2602.11968 | 待确认 |
| `definition_modeling_acl2023` | paper | Interpretable Word Sense Representations via Definition Generation: The Case of Semantic Change Analysis | 2023, ACL | https://aclanthology.org/2023.acl-long.176/ | `语义计算/.tmp_papers/interpretable.pdf` |
| `verified_reproduction_pack` | paper_group | ACL 2023 definition generation and EACL 2024 semantic-change reproduction records | 2023/2024 | https://aclanthology.org/2023.acl-long.176/ | `语义计算/.tmp_papers/tutorial_semchange.pdf` |
| `copl_emnlp2025` | paper | CoPL: Collaborative Preference Learning for Personalizing LLMs | 2025, EMNLP | https://arxiv.org/abs/2503.01658 | 待确认 |
| `talon_time_series_llm` | paper | Adapting LLMs to Time Series Forecasting via Temporal Heterogeneity Modeling and Semantic Alignment | 待确认 | 待确认 | 待确认 |
| `mambafcs_2026` | paper | Joint Spatio-Frequency Feature Fusion with Change-Guided Attention and SeK Loss | 2026, IEEE JSTARS | https://doi.org/10.1109/JSTARS.2026.3663066 | 待确认 |
| `mambafcs_2026_v2` | paper | Joint Spatio-Frequency Feature Fusion with Change-Guided Attention and SeK Loss | 2026, IEEE JSTARS | https://doi.org/10.1109/JSTARS.2026.3663066 | 待确认 |

## 论文对应的可复现代码

| 编号 | 类型 | 可复现代码目录 | 本地原始源码 | 检查范围 |
| --- | --- | --- | --- | --- |
| `histwords_acl2016` | reproducible_code | `reproduced/lexical_semantic_change/histwords_acl2016` | `语义计算/histwords` | 源码快照一致性、入口存在、文件卫生 |
| `scalable_semantic_shift_naacl2021` | reproducible_code | `reproduced/lexical_semantic_change/scalable_semantic_shift_naacl2021` | `委婉语/语义计算/scalable_semantic_shift-master` | 源码快照一致性、入口存在、文件卫生 |
| `tempobert_wsdm2022` | reproducible_code | `reproduced/temporal_models/tempobert_wsdm2022` | `委婉语/动态演化建模/tempobert` | 源码快照一致性、入口存在、文件卫生 |
| `lscd_benchmark` | reproducible_code | `reproduced/benchmarks/lscd_benchmark` | `论文复现/LSCDBenchmark` | 源码快照一致性、入口存在、文件卫生 |
| `scdisc_hplt_2026` | reproducible_code | `reproduced/lexical_semantic_change/scdisc_hplt_2026` | `论文复现/papers/2026-scdisc-hplt` | 源码快照一致性、入口存在、文件卫生 |
| `semantic_change_discovery_emnlp2025` | reproducible_code | `reproduced/lexical_semantic_change/semantic_change_discovery_emnlp2025` | `论文复现/papers/2025-semantic-change-discovery` | 源码快照一致性、入口存在、文件卫生 |
| `dhplt_scdisc_2026_minimal` | reproducible_code | `reproduced/lexical_semantic_change/dhplt_scdisc_2026_minimal` | `论文复现/papers/2026-dhplt-scdisc` | 源码快照一致性、入口存在、文件卫生 |
| `definition_modeling_acl2023` | reproducible_code | `reproduced/definition_generation/definition_modeling_acl2023` | `论文复现/definition_modeling` | 源码快照一致性、入口存在、文件卫生 |
| `verified_reproduction_pack` | reproducible_code | `reproduced/verified_runs/reproduction_pack` | `论文复现/reproduction_pack` | 源码快照一致性、入口存在、文件卫生 |
| `copl_emnlp2025` | reproducible_code | `reproduced/peripheral_llm/copl_emnlp2025` | `委婉语/论文复现/CoPL-main` | 源码快照一致性、入口存在、文件卫生 |
| `talon_time_series_llm` | reproducible_code | `reproduced/peripheral_llm/talon_time_series_llm` | `委婉语/论文复现/TALON-main` | 源码快照一致性、入口存在、文件卫生 |
| `mambafcs_2026` | reproducible_code | `reproduced/peripheral_remote_sensing/mambafcs_2026` | `论文复现/papers/2026-mambafcs` | 源码快照一致性、入口存在、文件卫生 |
| `mambafcs_2026_v2` | reproducible_code | `reproduced/peripheral_remote_sensing/mambafcs_2026_v2` | `论文复现/papers/2026-mambafcs-v2` | 源码快照一致性、入口存在、文件卫生 |

## 说明

- `待确认` 表示当前文件夹扫描中没有可靠匹配的论文 PDF，或 README 中未给出完整出版信息。
- 如果后续确认 PDF 允许公开二次分发，可放入 `papers/pdfs/` 并在本表补充相对路径。
- 源码目录内的 `PAPER.md` 是每个项目的就近论文说明。
- 自动检查结果见 `docs/REPRODUCIBILITY_AUDIT.md`。
