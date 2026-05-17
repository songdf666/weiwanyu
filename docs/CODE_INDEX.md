# 已复现代码索引

本索引按当前工作区扫描结果整理。`reproduced/` 中保存的是轻量源码副本；原始数据、模型权重、向量文件、虚拟环境和运行输出只在此处标注，不进入仓库。每个源码对应论文见 `docs/PAPER_INDEX.md`，每个源码目录内也有 `PAPER.md`。

| 编号 | 项目 | 原始路径 | 仓库路径 | 标注 |
| --- | --- | --- | --- | --- |
| 1 | HistWords ACL 2016 | `语义计算/histwords` | `reproduced/lexical_semantic_change/histwords_acl2016` | 词义历时变化经典静态词向量复现。已本地验证官方示例和词相似度评测；排除 `embeddings/`、`.venv/`、`.git/`。 |
| 2 | Scalable Semantic Shift NAACL 2021 | `委婉语/语义计算/scalable_semantic_shift-master` | `reproduced/lexical_semantic_change/scalable_semantic_shift_naacl2021` | BERT 上下文化表示、聚类、JSD/WD 语义变化检测。数据需外部下载。 |
| 3 | TempoBERT WSDM 2022 | `委婉语/动态演化建模/tempobert` | `reproduced/temporal_models/tempobert_wsdm2022` | 时间掩码语言模型和语义变化检测。排除 `datasets/`、`output/`、`logs/`、`venv/`。 |
| 4 | LSCDBenchmark | `论文复现/LSCDBenchmark` | `reproduced/benchmarks/lscd_benchmark` | Hydra 配置化 LSCD benchmark。保留 `src/`、`conf/`、`tests/`、`docs/`。 |
| 5 | DHPLT/HPLT semantic change scripts | `论文复现/papers/2026-scdisc-hplt` | `reproduced/lexical_semantic_change/scdisc_hplt_2026` | 大规模多语历时语料、静态/上下文化表示、APD 和 substitutes 管线。大数据外置。 |
| 6 | Semantic Change Discovery EMNLP 2025 | `论文复现/papers/2025-semantic-change-discovery` | `reproduced/lexical_semantic_change/semantic_change_discovery_emnlp2025` | 语义变化发现、上下文化嵌入、MLM substitutes、聚类/APD/JSD 评测。 |
| 7 | DHPLT minimal subset | `论文复现/papers/2026-dhplt-scdisc` | `reproduced/lexical_semantic_change/dhplt_scdisc_2026_minimal` | 最小本地副本，主要含 tokenization 和时间分布统计脚本。 |
| 8 | Definition Modeling ACL 2023 | `论文复现/definition_modeling` | `reproduced/definition_generation/definition_modeling_acl2023` | 定义生成、词义标签、可解释词义表示。复现实验记录见 `verified_runs`。 |
| 9 | Verified Reproduction Pack | `论文复现/reproduction_pack` | `reproduced/verified_runs/reproduction_pack` | 已验证本地复现记录、命令包装器和小型输出工件。 |
| 10 | CoPL EMNLP 2025 | `委婉语/论文复现/CoPL-main` | `reproduced/peripheral_llm/copl_emnlp2025` | 个性化偏好学习 LLM 项目。与委婉语/词义变化主线关系较弱，作为外围复现代码保留；排除 PEFT vendor、模型、日志、数据集和虚拟环境。 |
| 11 | TALON | `委婉语/论文复现/TALON-main` | `reproduced/peripheral_llm/talon_time_series_llm` | LLM 时间序列预测项目。作为外围项目保留源码入口；排除数据、checkpoint 和结果。 |
| 12 | Mamba-FCS | `论文复现/papers/2026-mambafcs` | `reproduced/peripheral_remote_sensing/mambafcs_2026` | 遥感语义变化检测项目，不属于词汇语义变化；保留核心源码，排除 vendor 配置和权重。 |
| 13 | Mamba-FCS v2 | `论文复现/papers/2026-mambafcs-v2` | `reproduced/peripheral_remote_sensing/mambafcs_2026_v2` | 第二份本地源码快照，按同样规则保留。 |

## 标注约定

- `SOURCE_NOTE.md`: 每个同步后的项目目录都会自动生成，记录来源、同步状态、入口脚本和排除规则。
- `domain`: 区分词汇语义变化、定义生成、时间语言模型、外围 LLM 项目和遥感 SCD 项目。
- `status`: 描述本地复现状态，不等同于论文完整复现。
- `entrypoints`: 优先检查这些脚本或配置文件来恢复实验。

## 后续整理建议

1. 将与委婉语研究直接相关的代码提升到 `src/euphemism_repro/`，保留统一接口。
2. 把外部项目的原始 README 和本地复现日志分开管理，避免误把官方说明当成本地已完成实验。
3. 对每个新实验都从 `templates/EXPERIMENT_LOG_TEMPLATE.md` 复制一份到 `logs/YYYYMMDD_experiment-name.md`。
