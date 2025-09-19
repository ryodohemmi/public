#!/usr/bin/env python3
# Last update: 2025/02/15
# Developer: Ryodo Hemmi (ISAS/JAXA)

import sys
import os
import argparse
import numpy as np
from osgeo import gdal

gdal.UseExceptions()

def parseNoData(dtype_name):
    """
    Return a recommended default NoData value for the GDAL data type name.
    """
    if dtype_name == 'Byte':
        return 0
    elif dtype_name == 'Int16':
        return -32768
    elif dtype_name == 'UInt16':
        return 0
    elif dtype_name == 'Int32':
        return -2147483647
    elif dtype_name == 'UInt32':
        return 0
    elif dtype_name == 'Float32':
        return -3.402823466E+38
    elif dtype_name == 'Float64':
        return -1.7976931348623158E+308
    else:
        return 0

def print_progress(current, total):
    bar_len = 40
    filled_len = int(bar_len * current / total)
    bar = "#" * filled_len + "-" * (bar_len - filled_len)
    pct = 100.0 * current / total
    sys.stdout.write(f"\r[{bar}] {pct:6.2f}%  {current}/{total}")
    sys.stdout.flush()
    if current == total:
        print()

def compute_slope_raster(
    dem_array, valid_mask,
    baseline_pix, pixel_size,
    nodata_val, dtype_code,
    geotransform, projection,
    out_raster_path,
    direction="v"
):
    """
    Create a slope raster in degrees at the chosen baseline (in pixels).
    direction='v' => vertical differencing
    direction='h' => horizontal differencing
    Returns a numpy array of slope in degrees.
    """
    nrows, ncols = dem_array.shape
    slope_deg_arr = np.full((nrows, ncols), nodata_val, dtype=dem_array.dtype)

    if direction == "v":
        # vertical => differ in rows
        for r in range(nrows - baseline_pix):
            for c in range(ncols):
                if valid_mask[r,c] and valid_mask[r+baseline_pix,c]:
                    dz = dem_array[r+baseline_pix,c] - dem_array[r,c]
                    dimless = dz / (baseline_pix * pixel_size)
                    slope_deg = np.degrees(np.arctan(dimless))
                    slope_deg_arr[r,c] = slope_deg
    else:
        # horizontal => differ in columns
        for r in range(nrows):
            for c in range(ncols - baseline_pix):
                if valid_mask[r,c] and valid_mask[r,c+baseline_pix]:
                    dz = dem_array[r,c+baseline_pix] - dem_array[r,c]
                    dimless = dz / (baseline_pix * pixel_size)
                    slope_deg = np.degrees(np.arctan(dimless))
                    slope_deg_arr[r,c] = slope_deg

    driver = gdal.GetDriverByName("GTiff")
    ds_out = driver.Create(out_raster_path, ncols, nrows, 1, dtype_code)
    ds_out.SetProjection(projection)
    ds_out.SetGeoTransform(geotransform)
    out_band = ds_out.GetRasterBand(1)
    out_band.SetNoDataValue(float(nodata_val))
    out_band.WriteArray(slope_deg_arr)
    out_band = None
    ds_out = None

    return slope_deg_arr

def compute_rms_slope_from_slope_raster(slope_deg_arr, nodata_val):
    valid_mask = (slope_deg_arr != nodata_val)
    valid_slopes_deg = slope_deg_arr[valid_mask]
    if valid_slopes_deg.size < 1:
        return 0.0, 0.0

    slopes_rad = np.radians(valid_slopes_deg)
    dimless_vals = np.tan(slopes_rad)
    mean_sq = np.mean(dimless_vals**2)
    rms_dimless = np.sqrt(mean_sq)
    rms_slope_deg = np.degrees(np.arctan(rms_dimless))
    return rms_dimless, rms_slope_deg

def gen_powers_of_two(low, high):
    base = 1
    while base < low:
        base <<= 1
    while base <= high:
        yield base
        base <<= 1

def generate_baselines(min_baseline, max_baseline, interval_value):
    baselines = []
    if interval_value == "p2":
        for b in gen_powers_of_two(min_baseline, max_baseline):
            baselines.append(b)
    else:
        step_int = int(interval_value)
        val = min_baseline
        while val <= max_baseline:
            baselines.append(val)
            val += step_int
    return sorted(set(baselines))

def direction_label_for_print(d):
    if d=="v":
        return "vertical"
    elif d=="h":
        return "horizontal"
    else:
        return "both (vertical and horizontal)"

def process_direction(
    dem_path,
    dem_array,
    valid_mask,
    nodata_val,
    dtype_code,
    geotransform,
    projection,
    pixel_size,
    direction,
    min_baseline,
    max_baseline,
    interval_value,
    out_csv_base,
    out_raster_base
):
    baselines = generate_baselines(min_baseline, max_baseline, interval_value)
    out_csv_path = out_csv_base + ".csv"

    with open(out_csv_path, 'w') as f:
        f.write("Baseline_pix,Baseline_m,dimless_slope,RMS_slope_deg\n")

        total_count = len(baselines)
        for idx, b in enumerate(baselines):
            print_progress(idx+1, total_count)

            # zero-pad 4 digits => e.g. 0001, 9999
            out_raster_path = f"{out_raster_base}_{b:04d}.tif"

            slope_deg_arr = compute_slope_raster(
                dem_array=dem_array,
                valid_mask=valid_mask,
                baseline_pix=b,
                pixel_size=pixel_size,
                nodata_val=nodata_val,
                dtype_code=dtype_code,
                geotransform=geotransform,
                projection=projection,
                out_raster_path=out_raster_path,
                direction=direction
            )

            rms_dimless, rms_slope_deg = compute_rms_slope_from_slope_raster(
                slope_deg_arr=slope_deg_arr,
                nodata_val=nodata_val
            )

            baseline_m = b * pixel_size
            f.write(f"{b},{baseline_m},{rms_dimless},{rms_slope_deg}\n")

    print(f"Output          : {out_csv_path}")

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Compute baseline differencing in vertical/horizontal/both directions, produce slope rasters, and output RMS slope at each baseline."
    )
    parser.add_argument("dem", help="Path to input DEM raster")
    parser.add_argument(
        "--direction","-d",
        choices=["v","h","b"],
        default="v",
        help="Compute baseline differencing along vertical | horizontal | both."
    )
    parser.add_argument(
        "--min_baseline","-min",
        type=int,
        default=1,
        help="Minimum baseline in pixel units."
    )
    parser.add_argument(
        "--max_baseline","-max",
        type=int,
        default=100,
        help="Maximum baseline in pixel units."
    )
    parser.add_argument(
        "--interval","-i",
        default="1",
        help="Either an integer step in pixel units or 'p2' for powers of 2."
    )
    parser.add_argument(
        "--output","-o",
        default=None,
        help=("If not set and direction!='b', => <dem_no_ext>_{v|h}_slope_rms.csv. If direction='b', produce two separate CSVs. "
              "If set, e.g. '-o foo', direction='v' => 'foo_v_slope_rms.csv' & rasters => 'foo_v_slope_XXXX.tif'.")
    )

    args = parser.parse_args()

    print("============ Parameter Settings ============")
    import datetime
    now_utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")
    print(f"Start time (UTC): {now_utc}")
    print(f"Input DEM       : {args.dem}")
    dir_print = direction_label_for_print(args.direction)
    print(f"Direction       : {dir_print}")
    print(f"Min baseline pix: {args.min_baseline}")
    print(f"Max baseline pix: {args.max_baseline}")
    if args.interval == "p2":
        print(f"Interval        : powers of 2")
    else:
        print(f"Interval        : {args.interval}")
    print("===========================================")

    dem_path = args.dem
    direction = args.direction
    min_baseline = args.min_baseline
    max_baseline = args.max_baseline
    interval_value = args.interval
    user_out = args.output

    ds = gdal.Open(dem_path, gdal.GA_ReadOnly)
    if ds is None:
        raise IOError(f"Could not open {dem_path}")
    band = ds.GetRasterBand(1)

    nodata_val = band.GetNoDataValue()
    if nodata_val is None:
        dtype_code = band.DataType
        dtype_name = gdal.GetDataTypeName(dtype_code)
        nodata_val = parseNoData(dtype_name)
    else:
        dtype_code = band.DataType
        dtype_name = gdal.GetDataTypeName(dtype_code)

    dem_array = band.ReadAsArray().astype(np.float64)
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()
    ds = None

    pixel_size = abs(gt[1]) if (gt and gt[1] != 0) else 1.0
    valid_mask = (dem_array != nodata_val)

    base_no_ext = os.path.splitext(dem_path)[0]

    if direction in ("v","h"):
        if user_out is None:
            # old default => e.g. <dem_no_ext>_v_slope_rms for CSV, <dem_no_ext>_v_slope for rasters
            out_csv_base = f"{base_no_ext}_{direction}_slope_rms"
            out_raster_base = f"{base_no_ext}_{direction}_slope"
        else:
            # e.g. 'bidir/cr1' => 'bidir/cr1_v_slope_rms' for CSV base,
            # rasters => 'bidir/cr1_v_slope_XXXX.tif'
            out_csv_base = f"{user_out}_{direction}_slope_rms"
            out_raster_base = f"{user_out}_{direction}_slope"

        process_direction(
            dem_path=dem_path,
            dem_array=dem_array,
            valid_mask=valid_mask,
            nodata_val=nodata_val,
            dtype_code=dtype_code,
            geotransform=gt,
            projection=proj,
            pixel_size=pixel_size,
            direction=direction,
            min_baseline=min_baseline,
            max_baseline=max_baseline,
            interval_value=interval_value,
            out_csv_base=out_csv_base,
            out_raster_base=out_raster_base
        )

    else:
        # direction='b' => do vertical + horizontal
        if user_out is None:
            out_csv_base_v = f"{base_no_ext}_v_slope_rms"
            out_raster_base_v = f"{base_no_ext}_v_slope"
            out_csv_base_h = f"{base_no_ext}_h_slope_rms"
            out_raster_base_h = f"{base_no_ext}_h_slope"
        else:
            out_csv_base_v = f"{user_out}_v_slope_rms"
            out_raster_base_v = f"{user_out}_v_slope"
            out_csv_base_h = f"{user_out}_h_slope_rms"
            out_raster_base_h = f"{user_out}_h_slope"

        process_direction(
            dem_path=dem_path,
            dem_array=dem_array,
            valid_mask=valid_mask,
            nodata_val=nodata_val,
            dtype_code=dtype_code,
            geotransform=gt,
            projection=proj,
            pixel_size=pixel_size,
            direction="v",
            min_baseline=min_baseline,
            max_baseline=max_baseline,
            interval_value=interval_value,
            out_csv_base=out_csv_base_v,
            out_raster_base=out_raster_base_v
        )
        process_direction(
            dem_path=dem_path,
            dem_array=dem_array,
            valid_mask=valid_mask,
            nodata_val=nodata_val,
            dtype_code=dtype_code,
            geotransform=gt,
            projection=proj,
            pixel_size=pixel_size,
            direction="h",
            min_baseline=min_baseline,
            max_baseline=max_baseline,
            interval_value=interval_value,
            out_csv_base=out_csv_base_h,
            out_raster_base=out_raster_base_h
        )

if __name__ == "__main__":
    main()
