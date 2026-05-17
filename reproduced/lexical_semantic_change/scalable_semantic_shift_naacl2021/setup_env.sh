#!/bin/bash
# ============================================================
#  环境安装脚本 - Scalable Semantic Shift Detection
# ============================================================

set -e

echo "正在创建 conda 环境 (Python 3.9)..."
/opt/miniconda3/bin/conda create -n semantic_shift python=3.9 -y

PYTHON="/opt/miniconda3/envs/semantic_shift/bin/python"
PIP="/opt/miniconda3/envs/semantic_shift/bin/pip"

echo "正在安装依赖..."
$PIP install setuptools
$PIP install numpy pandas scipy scikit-learn tqdm transformers tokenizers \
    tensorboardX nltk matplotlib POT torch torchvision

echo "下载 NLTK 数据..."
$PYTHON -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

echo ""
echo "环境安装完成!"
echo "Python: $($PYTHON --version)"
echo "使用方法: bash run_demo.sh"
