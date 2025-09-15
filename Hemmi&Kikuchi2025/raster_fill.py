#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Last Update: 2025/06/25
# Developer: Ryodo Hemmi (https://orcid.org/0000-0002-9638-6926)
# Requirements (conda/pip): numpy, gdal, [optional] opencv (or scipy)

help_desc_msg ='''
Apply a 3x3 hole/mound fill on a raster using GDAL:
Reads a single-band raster (any GDAL-supported format), computes the 3×3 neighbor mean,
replaces pixels whose difference from that mean exceeds the tolerance,
and writes out via CreateCopy with the same driver/format as the input.
'''

try:
    import os, sys, argparse
    import numpy as np
except ImportError as e:
    missing_module = str(e).split("'")[1]
    sys.exit(f"Import error: \"{missing_module}\" is missing.")
try:
    from osgeo import gdal
except ImportError:
    try:
        import gdal
    except ImportError as e:
        missing_module = str(e).split("'")[1]
        sys.exit(f"Import error: \"{missing_module}\" is missing.")

gdal.UseExceptions()  # Raise exceptions instead of warnings

# Try OpenCV for convolution, otherwise fall back to SciPy
try:
    import cv2
    _USE_CV2 = True
    _USE_SCIPY = False
except ImportError as e:
    missing_module = str(e).split("'")[1]
    print(f"\"{missing_module}\" is missing.")
    try:
        from scipy.signal import convolve2d
        _USE_CV2 = False
        _USE_SCIPY = True
    except ImportError as e:
        missing_module = str(e).split("'")[1]
        print(f"\"{missing_module}\" is missing.")
        _USE_CV2 = False
        _USE_SCIPY = False

def raster_fill(input_path: str, output_path: str, tolerance: float):
    """
    Reads a single-band raster (any GDAL-supported format), computes the 3×3 neighbor mean,
    replaces pixels whose difference from that mean exceeds the tolerance,
    and writes out via CreateCopy with the same driver/format as the input.
    """
    # Open source dataset
    src_ds = gdal.Open(input_path, gdal.GA_ReadOnly)
    print(f"    Input: {input_path}")
    print(f"Tolerance: {tolerance}")

    if src_ds is None:
        raise FileNotFoundError(f"Could not open {input_path}")
    src_band = src_ds.GetRasterBand(1)
    arr = src_band.ReadAsArray().astype(np.float32)
    
    # Build the 3×3 neighbor-mean kernel
    kernel = np.ones((3, 3), dtype=np.float32)
    kernel[1, 1] = 0.0
    kernel /= 8.0
    
    # Compute neighbor mean
    if _USE_CV2:
        # https://docs.opencv.org/5.x/d4/d86/group__imgproc__filter.html#ga27c049795ce870216ddfb366086b5a04
        neigh = cv2.filter2D(arr, -1, kernel, borderType=cv2.BORDER_REFLECT)
    elif _USE_SCIPY:
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.convolve2d.html
        neigh = convolve2d(arr, kernel, mode="same", boundary="symm")
    else: # in case both cv2 and scipy are not available
        # Pad array to handle borders (reflect padding)
        padded = np.pad(arr, pad_width=1, mode='reflect')
        # Sum the 8 surrounding pixels for each location
        neigh_sum = (
            padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
            padded[1:-1, :-2]                + padded[1:-1, 2:] +
            padded[2:,  :-2] + padded[2:,  1:-1] + padded[2:,  2:]
        )
        neigh = neigh_sum / 8.0
    
    # Identify holes (tolerance < 0) or mounds (tolerance > 0)
    diff = arr - neigh
    if tolerance >= 0:
        mask = diff > tolerance
    else:
        mask = diff < tolerance

    # Fill selected pixels
    out_arr = arr.copy()
    out_arr[mask] = neigh[mask]

    # Preserve format by using the same driver
    driver = src_ds.GetDriver()
    out_ds = driver.CreateCopy(output_path, src_ds, 0)
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(out_arr)
    out_band.FlushCache()

    # Clean up
    out_ds = None
    src_ds = None
    print(f"   Output: {output_path}")

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    pass

def get_args():
    parser = argparse.ArgumentParser(description=help_desc_msg, formatter_class=CustomFormatter)
    
    parser.add_argument(
        "input",
        help="Path to the input raster file"
    )
    parser.add_argument(
        "-t", "--tolerance",
        type=float,
        default=-200,
        help=(
            f"Tolerance for hole/mound detection: \
            \nNegative values fill holes where pixel - neighbor_mean < tolerance; \
            \nPositive values flatten mounds where pixel - neighbor_mean > tolerance"
        )
    )
    parser.add_argument(
        "-o", "--output",
        nargs="?",
        help=(
            f"Optional path for the output raster file.\
            \nIf omitted, the script will insert \".fill\" before the input file's extension"
        ),
        default=None
    )
    args = parser.parse_args()
    return(args)

def main():
    terminal_width = os.get_terminal_size().columns
    print("=" * terminal_width)
    
    args = get_args()
    input_path = args.input
    tolerance = args.tolerance
    # Determine default output if not provided
    if args.output:
        output_path = args.output
    else:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}.fill{ext}"
    s = ""
    for arg in sys.argv:
        s = s + arg + " "
    
    print(f"{os.path.basename(sys.executable)} {s}")
    print("=" * terminal_width)

    raster_fill(input_path, output_path, tolerance)

if __name__ == "__main__":
    main()
