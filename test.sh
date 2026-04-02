#!/usr/bin/env bash
set -euo pipefail

INPUT_FILE="${1:-input.txt}"
OUTPUT_FILE="solver_output.txt"
PYTHON_BIN="${PYTHON:-python3}"

make
./build/art_gallery < "$INPUT_FILE" | tee "$OUTPUT_FILE"
"$PYTHON_BIN" visualize.py "$INPUT_FILE" --solver-output "$OUTPUT_FILE" --output-dir plots --format png
