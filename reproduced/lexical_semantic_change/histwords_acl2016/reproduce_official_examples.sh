#!/usr/bin/env bash
set -euo pipefail

source /Users/sdf/Desktop/语义计算/histwords/.venv/bin/activate
cd /Users/sdf/Desktop/语义计算/histwords

echo "[1/2] Running official example.py"
python example.py

echo
echo "[2/2] Running official ws_eval example"
python -m vecanalysis.ws_eval embeddings/eng-fiction-all_sgns/1990 \
  vecanalysis/simtestsets/ws/bruni_men.txt --type SGNS
