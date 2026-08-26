#!/usr/bin/env bash
set -euo pipefail

# Reproduce *_NoSpin_result_TA000.csv products from GFandSlope output tables.

INPUT_DIR="../input"
OUTPUT_DIR="./output_NoSpin_result_TA000"

LSK="../spice/lsk/naif0012.tls"
PCK="../spice/pck/pck00011.tpc"
GM="../spice/pck/gm_de440.tpc"
SPK="../spice/spk/mar099s.bsp"

START_TIME="2029-01-01T00:00:00"

# Add or remove files here depending on the resolutions used in the study.
INPUT_FILES=(
  "v004_80_surface.txt"
  # "v004_100_surface.txt"
  # "v004_125_surface.txt"
  # "v004_150_surface.txt"
  # "v004_175_surface.txt"
  # "v004_200_surface.txt"
  # "v004_250_surface.txt"
  # "v004_500_surface.txt"
  # "v004_1000_surface.txt"
  # "v004_2000_surface.txt"
)

mkdir -p "${OUTPUT_DIR}"

python make_NoSpin_result_TA000.py \
  --input-dir "${INPUT_DIR}" \
  --input-files "${INPUT_FILES[@]}" \
  --output-dir "${OUTPUT_DIR}" \
  --lsk "${LSK}" \
  --pck "${PCK}" \
  --gm "${GM}" \
  --spk "${SPK}" \
  --start-time "${START_TIME}" \
  --ta 0

echo
echo "Outputs written to: ${OUTPUT_DIR}"
ls -lh "${OUTPUT_DIR}"/*_NoSpin_result_TA000.csv
