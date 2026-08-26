#!/usr/bin/env bash
set -euo pipefail

# Reproduce the GFandSlope self-gravity stage used for the Phobos slope analysis.
#
# Default assumptions:
#   GFandSlope repository: ~/GFandSlope
#   Phobos shape-model directory: ~/phobos_slope
#   GPU ID: 0
#   Density: 1862.297786 kg/m^3
#   GFandSlope period: 0.0 h
#
# The final effective-gravity products used in the paper are NOT produced by
# GFandSlope alone. Centrifugal and Martian tidal accelerations are added later
# by the separate gravity wrapper distributed with the reproduction package.
#
# Usage:
#   ./run_gfandslope.sh
#   ./run_gfandslope.sh 18 80 200 2000
#
# Optional environment overrides:
#   GFANDSLOPE_DIR=/path/to/GFandSlope
#   PHOBOS_SLOPE_DIR=/path/to/phobos_slope
#   CFG_TEMPLATE=/path/to/gfandslope.cfg.template
#   GPU_ID=0
#   DENSITY=1862.297786

GFANDSLOPE_DIR="${GFANDSLOPE_DIR:-$HOME/GFandSlope}"
PHOBOS_SLOPE_DIR="${PHOBOS_SLOPE_DIR:-$HOME/phobos_slope}"
CFG_TEMPLATE="${CFG_TEMPLATE:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/gfandslope.cfg.template}"
GPU_ID="${GPU_ID:-0}"
DENSITY="${DENSITY:-1862.297786}"
PERIOD="${PERIOD:-0.0}"

DEFAULT_SCALES=(18 80 100 125 150 175 200 250 500 1000 2000)

if (($# > 0)); then
    SCALES=("$@")
else
    SCALES=("${DEFAULT_SCALES[@]}")
fi

if [[ ! -d "$GFANDSLOPE_DIR" ]]; then
    echo "ERROR: GFandSlope directory not found: $GFANDSLOPE_DIR" >&2
    exit 1
fi

if [[ ! -d "$PHOBOS_SLOPE_DIR" ]]; then
    echo "ERROR: Phobos slope directory not found: $PHOBOS_SLOPE_DIR" >&2
    exit 1
fi

if [[ ! -f "$CFG_TEMPLATE" ]]; then
    echo "ERROR: configuration template not found: $CFG_TEMPLATE" >&2
    exit 1
fi

if [[ ! -x "$GFANDSLOPE_DIR/src/GFandSlope" ]]; then
    echo "ERROR: GFandSlope executable not found or not executable:" >&2
    echo "       $GFANDSLOPE_DIR/src/GFandSlope" >&2
    exit 1
fi

if [[ ! -f "$GFANDSLOPE_DIR/util/Mesh2GFandSlopeInput.py" ]]; then
    echo "ERROR: Mesh2GFandSlopeInput.py not found:" >&2
    echo "       $GFANDSLOPE_DIR/util/Mesh2GFandSlopeInput.py" >&2
    exit 1
fi

mkdir -p "$GFANDSLOPE_DIR/work"
cd "$GFANDSLOPE_DIR"

cleanup_link() {
    local link_path="$1"
    if [[ -L "$link_path" ]]; then
        unlink "$link_path"
    fi
}

for scale in "${SCALES[@]}"; do
    if [[ "$scale" == "18" ]]; then
        src_obj="$PHOBOS_SLOPE_DIR/phobos_g_018m_spc_obj_0000n00000_v004.obj"
    else
        src_obj="$PHOBOS_SLOPE_DIR/phobos_g_018m_spc_obj_0000n00000_v004_diffuse_efold_${scale}_preserve.obj"
    fi

    work_obj="work/v004_${scale}.obj"
    polygon_txt="${work_obj}.txt"
    cfg="work/v004_${scale}.cfg"
    output="work/v004_${scale}_surface.txt"

    if [[ ! -f "$src_obj" ]]; then
        echo "ERROR: input OBJ not found for L=${scale} m:" >&2
        echo "       $src_obj" >&2
        exit 1
    fi

    echo
    echo "============================================================"
    echo "GFandSlope self-gravity stage: L=${scale} m"
    echo "Input OBJ:  $src_obj"
    echo "Output:     $output"
    echo "============================================================"

    cleanup_link "$work_obj"
    ln -s "$src_obj" "$work_obj"

    python util/Mesh2GFandSlopeInput.py "$work_obj"

    sed         -e "s|@PERIOD@|$PERIOD|g"         -e "s|@DENSITY@|$DENSITY|g"         -e "s|@INPUT_POLYGON@|$polygon_txt|g"         -e "s|@OUTPUT@|$output|g"         -e "s|@GPU_ID@|$GPU_ID|g"         "$CFG_TEMPLATE" > "$cfg"

    echo "--- Configuration: $cfg ---"
    cat "$cfg"
    echo "--------------------------------"

    time ./src/GFandSlope "$cfg"

    if [[ ! -s "$output" ]]; then
        echo "ERROR: expected GFandSlope output was not created or is empty:" >&2
        echo "       $output" >&2
        exit 1
    fi

    ls -lh "$output"
    head -n 5 "$output"

    cleanup_link "$work_obj"
done

echo
echo "GFandSlope self-gravity calculations completed successfully."
echo "Next step: run the separate gravity wrapper to add centrifugal"
echo "and Martian tidal accelerations and to calculate final"
echo "effective-gravity slope and downslope azimuth products."
