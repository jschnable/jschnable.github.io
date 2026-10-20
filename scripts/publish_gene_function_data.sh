#!/usr/bin/env bash
# Publish regenerated Gene Function Summaries data to jschnable/gene-function-data.
#
# The data repository keeps exactly one commit: each publish replaces its history, so old data
# versions never accumulate (GitHub Pages serves the new commit at
# https://schnablelab.org/gene-function-data/). Run scripts/generate_gene_function_summaries.py first.
#
# Usage: scripts/publish_gene_function_data.sh [data-checkout] (default: ../gene-function-data)
set -euo pipefail
DATA_DIR="${1:-$(cd "$(dirname "$0")/../.." && pwd)/gene-function-data}"
cd "$DATA_DIR"
test -f metadata.json || { echo "no metadata.json in $DATA_DIR; generate the data first" >&2; exit 1; }
generated=$(python3 -c 'import json; print(json.load(open("metadata.json"))["generated_at"])')
git checkout -q --orphan publish
git add -A
git commit -q -m "Gene function summary data generated $generated"
git branch -D main >/dev/null 2>&1 || true
git branch -m main
git push --force origin main
git reflog expire --expire=now --all
git gc -q --prune=now
echo "published data generated $generated"
