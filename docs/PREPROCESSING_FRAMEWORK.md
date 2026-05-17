# 预处理脚本框架

预处理框架用于把分散的 `.txt`、`.jsonl`、`.csv`、`.tsv` 语料统一转换为 JSONL。默认输出字段如下：

- `doc_id`: 文档编号。优先使用输入文件中的 id 字段，否则自动生成。
- `source_path`: 原始文件路径。
- `period`: 时间片。优先使用配置中的时间字段，否则从文件名按正则提取年份。
- `text`: 清洗后的文本。
- `tokens`: 简单 token 列表，可通过配置关闭。
- `meta`: 输入格式、行号等辅助信息。

## 命令

```bash
python scripts/preprocess_corpus.py \
  --input data/raw \
  --output data/processed/corpus.jsonl \
  --config configs/preprocess.default.json
```

## 当前能力

- 递归读取 `.txt`、`.jsonl`、`.csv`、`.tsv`
- Unicode 规范化
- URL 去除
- 空白折叠
- 最小长度过滤
- 从列或文件名提取时间片
- 输出 JSONL，便于后续接 LSCD、TempoBERT、BERT embedding、定义生成等管线

## 扩展点

- 在 `src/euphemism_repro/preprocess/text.py` 中替换 tokenizer。
- 在 `src/euphemism_repro/preprocess/loaders.py` 中增加 docx/pdf/xlsx 等读取器。
- 在 `src/euphemism_repro/preprocess/pipeline.py` 中增加委婉语词表匹配、语种识别、去重或句子切分。
