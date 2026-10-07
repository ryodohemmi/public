# Scripts for generating `*_NoSpin_result_TA000.csv`

This directory contains the wrapper/post-processing scripts used to generate
the `*_NoSpin_result_TA000.csv` dynamic-slope products from GFandSlope output
tables.

GFandSlope itself is not included here because it is already released by the
University of Aizu. These scripts document the settings and execution procedure
used after obtaining facet-wise GFandSlope output tables.

## Files

- `make_NoSpin_result_TA000.py`  
  Main Python script. It reads one or more GFandSlope output tables and writes
  dynamic-slope products at true anomaly TA = 000 deg.

- `run_make_NoSpin_result_TA000.sh`  
  Example shell wrapper containing the input file list, SPICE kernel paths,
  output directory, epoch-search start time, and execution command.

- `requirements_NoSpin_result_TA000.txt`  
  Minimal Python package requirements.

## Input

The script expects a whitespace-delimited GFandSlope output table with the
following header:

```text
ID Point.x Point.y Point.z Lon Lat CRefAcc.x CRefAcc.y CRefAcc.z GravAcc.x GravAcc.y GravAcc.z TotalAcc.x TotalAcc.y TotalAcc.z Gpotential Rpotential Tpotential GeopotentialSlope Normal.x Normal.y Normal.z Area
```

Coordinates are in km. Other quantities are in SI units.

For the GFandSlope outputs used in this study, `GravAcc.x/y/z` are outward
vectors. The script therefore uses:

```text
self-gravity acceleration = -GravAcc
```

`CRefAcc` and the GFandSlope `TotalAcc` columns are read for compatibility with
the input table format, but the dynamic-slope calculation uses `GravAcc` as the
self-gravity term and then adds the SPICE-derived terms described below.

## Dynamic acceleration terms

For each facet center, the script computes

```text
g_total = g_self + a_tidal,Mars + a_centrifugal + a_Euler
```

where:

- `g_self = -GravAcc`
- `a_tidal,Mars` is the differential Mars acceleration at the facet relative to
  the Phobos center
- `a_centrifugal = -omega x (omega x r)`
- `a_Euler = -alpha x r`

The angular velocity `omega` and angular acceleration `alpha` are computed from
SPICE using the `J2000 -> IAU_PHOBOS` state transformation. The vector components
are rotated into `IAU_PHOBOS` before the cross products.

## Example execution

Edit `run_make_NoSpin_result_TA000.sh` if needed, especially the input file list
and SPICE kernel paths, then run:

```bash
bash run_make_NoSpin_result_TA000.sh
```

For the example input

```text
v004_80_surface.txt
```

the output file is

```text
output_NoSpin_result_TA000/v004_80_surface_NoSpin_result_TA000.csv
```

## Output columns

```text
facet_id
lon_deg
lat_deg
dynamic_slope_deg
dynamic_slope_azimuth_deg
facet_area
g_total_x_m_s2
g_total_y_m_s2
g_total_z_m_s2
g_total_mag_m_s2
```

The output CSV also contains metadata header lines beginning with `#`, including
the SPICE-derived epoch, Mars distance, angular velocity, angular acceleration,
and vector-sign diagnostics.
