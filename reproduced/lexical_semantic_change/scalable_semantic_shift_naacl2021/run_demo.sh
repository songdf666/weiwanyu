#!/bin/bash
# ============================================================
#  一键运行脚本 - Scalable and Interpretable Semantic Change Detection
#  论文复现: NAACL 2021
# ============================================================

set -e

# 自动检测 conda 环境
PYTHON="/opt/miniconda3/envs/semantic_shift/bin/python"
if [ ! -f "$PYTHON" ]; then
    echo "错误: 未找到 conda 环境 semantic_shift，请先运行 setup_env.sh"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "============================================================"
echo " 实验 1：语义差异计算 (Semantic Shift Detection)"
echo " 论文: Scalable and Interpretable Semantic Change Detection"
echo "============================================================"
echo ""

# ---- Step 1: 生成演示数据 ----
echo "[Step 1/5] 生成演示数据..."
$PYTHON prepare_demo_data.py
echo ""

# ---- Step 2: 提取 BERT 嵌入 ----
echo "[Step 2/5] 提取 BERT 上下文嵌入 (使用预训练 bert-base-uncased)..."
echo "  这一步可能需要几分钟，取决于硬件性能..."
$PYTHON get_embeddings_scalable.py \
  --corpus_paths "data/demo/period1.txt;data/demo/period2.txt" \
  --corpus_slices "1960;1990" \
  --target_path "data/demo/target_words.csv" \
  --task coha \
  --batch_size 8 \
  --max_sequence_length 128 \
  --path_to_fine_tuned_model "" \
  --embeddings_path "embeddings/demo_scalable.pickle"
echo ""

# ---- Step 3: 聚类与语义偏移测量 (JSD) ----
echo "[Step 3/5] 聚类 & 计算语义偏移 (Jensen-Shannon Divergence)..."
$PYTHON measure_semantic_shift.py \
  --corpus_slices "1960;1990" \
  --embeddings_path "embeddings/demo_scalable.pickle" \
  --results_dir_path "results_demo" \
  --method JSD \
  --get_additional_info
echo ""

# ---- Step 4: 聚类与语义偏移测量 (WD) ----
echo "[Step 4/5] 聚类 & 计算语义偏移 (Wasserstein Distance)..."
$PYTHON measure_semantic_shift.py \
  --corpus_slices "1960;1990" \
  --embeddings_path "embeddings/demo_scalable.pickle" \
  --results_dir_path "results_demo" \
  --method WD \
  --get_additional_info
echo ""

# ---- Step 5: 评估 ----
echo "[Step 5/5] 评估结果 (与 gold standard 的 Spearman 相关性)..."
echo ""
echo "--- JSD 方法 ---"
$PYTHON evaluate.py \
  --task coha \
  --gold_standard_path "data/demo/target_words.csv" \
  --results_path "results_demo/word_ranking_results_JSD.csv" \
  --corpus_slices "1960;1990"
echo ""
echo "--- WD 方法 ---"
$PYTHON evaluate.py \
  --task coha \
  --gold_standard_path "data/demo/target_words.csv" \
  --results_path "results_demo/word_ranking_results_WD.csv" \
  --corpus_slices "1960;1990"

echo ""
echo "============================================================"
echo " 实验完成!"
echo " 结果文件位于: results_demo/"
echo "   - word_ranking_results_JSD.csv  (JSD 语义偏移分数)"
echo "   - word_ranking_results_WD.csv   (WD 语义偏移分数)"
echo "   - kmeans_5_labels.pkl           (K-means 5 聚类标签)"
echo "   - aff_prop_labels.pkl           (Affinity Propagation 聚类标签)"
echo "   - sents.pkl                     (句子-嵌入映射)"
echo "============================================================"
