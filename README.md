# Euphemism and Semantic Change Reproduction Repository

本仓库用于整理当前文件夹中已经下载或复现过的代码，统一保存源码索引、实验日志模板和预处理脚本框架。

## 目录说明

- `reproduced/`: 从当前工作区同步过来的轻量源码副本。数据、模型权重、运行输出、虚拟环境不会进入该目录。
- `docs/CODE_INDEX.md`: 已复现代码索引和标注，记录原始路径、用途、入口脚本和当前状态。
- `docs/PAPER_INDEX.md`: 每个源码目录对应的论文索引、官方链接和本地候选文件。
- `papers/`: 论文题录说明。默认不提交 PDF 全文。
- `templates/EXPERIMENT_LOG_TEMPLATE.md`: 单次实验记录模板。
- `scripts/preprocess_corpus.py`: 语料预处理命令行入口。
- `src/euphemism_repro/preprocess/`: 可扩展的预处理 Python 包骨架。
- `configs/preprocess.default.json`: 预处理默认配置。
- `configs/source_manifest.json`: 源码同步清单。

## 快速开始

同步当前工作区中的复现源码：

```bash
python scripts/sync_reproduced_code.py --workspace-root .. --manifest configs/source_manifest.json
```

运行预处理框架：

```bash
python scripts/preprocess_corpus.py \
  --input data/raw \
  --output data/processed/corpus.jsonl \
  --config configs/preprocess.default.json
```

## 管理原则

1. 代码与数据分离：仓库内只保存源码、配置和小型示例，不保存语料全集、模型权重、向量文件和虚拟环境。
2. 每个复现项目保留 `SOURCE_NOTE.md`，说明来源、用途、入口和排除内容。
3. 每次实验复制 `templates/EXPERIMENT_LOG_TEMPLATE.md` 到 `logs/`，用日期和实验编号命名。
4. 新增预处理步骤时优先扩展 `src/euphemism_repro/preprocess/`，让 CLI 只负责参数解析。
