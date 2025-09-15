#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Last Update: 2025/09/12
# Developer: Ryodo Hemmi (https://orcid.org/0000-0002-9638-6926)
# Requirements (conda/pip): spiceypy, ale (or isis), opencv, scipy, numpy, gdal

try:
    import os, sys, argparse, math, csv
    import spiceypy as spice
    import ale
    import numpy as np
    import cv2 as cv
    from scipy.stats import norm
except ImportError as e:
    missing_module = str(e).split("'")[1]
    sys.exit(f"Import error: \"{missing_module}\" is missing.")
try:
    from osgeo import gdal, gdal_array
except ImportError:
    try:
        import gdal
    except ImportError as e:
        missing_module = str(e).split("'")[1]
        sys.exit(f"Import error: \"{missing_module}\" is missing.")

gdal.UseExceptions()  # Raise exceptions instead of warnings

help_desc_msg ='''

First, calculate the shift of an input image in pixels during exposure duration between observation start and stop timings using SPICE kernels.
Second, apply Wiener deconvolution to an input imagen with a simple PSF based on the shift.

The original sample code [1] demonstrates using DFT for Wiener deconvolution [2] of an image with a user-defined point spread function (PSF).

[1] https://github.com/opencv/opencv/blob/master/samples/python/deconvolution.py
[2] http://en.wikipedia.org/wiki/Wiener_deconvolution
'''

# ------------------
# GDAL helper functions
# ------------------
def import_isis_cube(filename, out_log):
    ds = gdal.Open(filename, gdal.GA_ReadOnly)
    if ds is None:
        sys.exit(f"Failed to open file: {filename}")
    
    band = ds.GetRasterBand(1)
    dtype = gdal.GetDataTypeName(band.DataType)
    print(f"Input: {filename} ({dtype})", file=out_log)
    arr = band.ReadAsArray().astype(np.float32)
    scale = band.GetScale() or 1.0
    offset = band.GetOffset() or 0.0
    arr_scaled = (arr * scale) + offset
    
    return arr_scaled

def export_isis_cube(filename, array, template_filename, out_log):
    # Determine the GDAL data type from the numpy array's data type.
    gdal_dtype = gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype)

    if template_filename is not None:
        # Use the template cube file
        gdal.Translate(
            destName=filename,
            srcDS=template_filename,
            format="ISIS3",
            outputType=gdal_dtype
        )

        dataset = gdal.Open(filename, gdal.GA_Update)
        if dataset is None:
            print(f"Failed to open cube for updating: {filename}", file=out_log)
            return
        band = dataset.GetRasterBand(1)
        if band is None:
            print(f"Failed to get raster band from cube: {filename}", file=out_log)
            return
        rows, cols = array.shape
        if dataset.RasterXSize != cols or dataset.RasterYSize != rows:
            print(f"Size mismatch: Cube({dataset.RasterYSize},{dataset.RasterXSize}), Array({rows},{cols})", file=out_log)
            dataset = None
            return
        band.WriteArray(array)
        band.FlushCache()
        dataset = None
        print(f"Output: {filename}", file=out_log)
    else:
        # If there is no template, create a new cube using the numpy array's data type.
        rows, cols = array.shape
        
        # Get the ISISCube driver.
        driver = gdal.GetDriverByName('ISIS3')
        if driver is None:
            raise RuntimeError("ISIS3 driver not available.")
        
        # Create a new cube dataset. The parameters are: filename, width (cols), height (rows), number of bands, data type.
        dataset = driver.Create(filename, cols, rows, 1, gdal_dtype)
        if dataset is None:
            print(f"Failed to create new cube: {filename}", file=out_log)
            return
        
        band = dataset.GetRasterBand(1)
        if band is None:
            print(f"Failed to get raster band from new cube: {filename}", file=out_log)
            return
        
        band.WriteArray(array)
        band.FlushCache()
        dataset = None
        print(f"Output: {filename}", file=out_log)

def estimate_snr(gray_image):
    """
    Estimate SNR by taking the residual after low-pass
    smoothing, then computing noise‐MAD from that residual.
    Returns SNR in dB.
    """
    image = gray_image.astype(np.float32)

    # 1) Smooth with a small Gaussian kernel (3×3, sigma=1)
    smooth = cv.GaussianBlur(image, ksize=(3,3), sigmaX=1.0)
    
    # 2) Residual (hopefully (mostly) noise)
    residual = image - smooth

    # 3) MAD‐based sigma_N estimate from the residual
    mad   = np.median(np.abs(residual))
    sigma = mad / norm.ppf(0.75)   # ≈ mad/0.6745
    # norm.ppf(0.75) implies the 75th percentile (or third quartile, Q3) of the standard normal distribution, 
    # showing that 75% of the noise data will fall below this value
    #
    #  Sigma  |      Coverage      |   Percentile   | norm.ppf (upper percentile)
    # --------|--------------------|----------------|-----------------------------
    # 0.6745σ |~50%–75% (median–Q3)|   75% (here)   | norm.ppf(0.75)=0.6745
    #    1σ   |      ~68.27%       |   84.135%      | norm.ppf(0.84135)=1.0
    #    2σ   |      ~95.45%       |   97.725%      | norm.ppf(0.97725)=2.0
    #    3σ   |      ~99.73%       |   99.865%      | norm.ppf(0.99865)=3.0
    """
    Median Absolute Deviation (MAD) is defined as:
    MAD=median(∣X−median(X)∣) 
    
    MAD is widely used because it is robust to extreme values (outliers).
    Edges and textures can produce high values that are not representative of the typical noise level. 
    Using the median helps to mitigate the influence of these outliers.
    
    For Gaussian (normal) distributions, the relationship between MAD and standard deviation (σ) is given by:
    𝜎≈MAD/0.6745
    This relationship holds because the MAD of a standard normal distribution is about 0.6745.
    Thus, using norm.ppf(0.75) here is not arbitrary.
    Instead, it arises naturally due to statistical properties:
    The median absolute deviation of a standard normal distribution equals the absolute deviation value at exactly the 75th percentile 
    (since 50% of values fall below the median, MAD naturally aligns with the 75th percentile absolute deviation).
    """
    # 4) Compute total image variance (signal + noise)
    var_I = np.mean((image - image.mean())**2)
    #    Alternatively, var_I = np.var(image) if you prefer.
    
    # 5) Estimate signal variance = var_I - sigma^2
    var_signal = var_I - sigma**2
    var_signal = max(var_signal, 1e-12)  # avoid negatives
    
    # 6) SNR in dB
    snr_db = 10.0 * np.log10(var_signal / (sigma**2))
    return snr_db

# ------------------------
# Deconvolution functions
# ------------------------
def make_half_odd(value):
    value = int(abs(value) // 2)
    if value % 2 == 0:  # Ensure even number
        if value > 0:
            value += 1  # Make it odd for the kernel size
        elif value == 0:  # If value is zero, keep it zero
            pass
    else:
        pass
    return value

def blur_edge(img, dx, dy):
    """
    Edge-taper with independent horizontal (dx) and vertical (dy) radii,
    allowing dx==0 or dy==0 to disable blurring in that direction.

    img : H×W or H×W×C array
    dx  : horizontal taper half-width (pixels; if zero, no horizontal blur/taper)
    dy  : vertical   taper half-width (pixels; if zero, no vertical blur/taper)
    """
    h, w = img.shape[:2]
    # 1) Pad & blur
    #    BORDER_WRAP with 0 on that side is effectively a no-op pad
    img_pad  = cv.copyMakeBorder(img,
                                 top=dy, bottom=dy,
                                 left=dx, right=dx,
                                 borderType=cv.BORDER_WRAP)
    # ksize = 2*radius+1: if radius==0 => ksize==1 => no blur in that axis
    ksize    = (2*dx + 1, 2*dy + 1)
    img_blur = cv.GaussianBlur(img_pad, ksize, sigmaX=-1, sigmaY=-1)
    img_blur = img_blur[dy:dy+h, dx:dx+w]
    # 2) Build 2D taper mask, splitting x and y so we never divide by zero
    y, x = np.indices((h, w))
    if dx > 0:
        dist_x = np.minimum(x, w - x - 1).astype(np.float32) / dx
    else:
        # no horizontal taper ⇒ weight = 1 everywhere in x
        dist_x = np.ones((h, w), dtype=np.float32)
    if dy > 0:
        dist_y = np.minimum(y, h - y - 1).astype(np.float32) / dy
    else:
        # no vertical taper ⇒ weight = 1 everywhere in y
        dist_y = np.ones((h, w), dtype=np.float32)
    # combined depth from edges, clamped to [0,1]
    w_mask = np.minimum(np.minimum(dist_x, dist_y), 1.0)
    # if color image, broadcast mask across channels
    if img.ndim == 3:
        w_mask = w_mask[:, :, None]

    # 3) Blend original & blurred
    # if both dx and dy are zero, img_blur == img and mask == 1 ⇒ just original
    return img * w_mask + img_blur * (1.0 - w_mask)

def gaussian(img, px, sigma):
    if px <=0:
        return img
    else:
        if sigma == 0:
            n = px - 1
            coeffs = np.array([math.comb(n, k) for k in range(n + 1)], dtype=float)
            kernel = np.outer(coeffs, coeffs)
            kernel /= kernel.sum()
        else:
            half_px = (px - 1) / 2
            x, y = np.mgrid[-half_px:half_px+1, -half_px:half_px+1]
            squared_distance = x**2 + y**2
            kernel = np.exp(-squared_distance / (2 * sigma**2))
            kernel /= kernel.sum()
        
        pad_h = kernel.shape[0] // 2
        pad_w = kernel.shape[1] // 2
        padded_img = np.pad(img, ((pad_h, pad_h), (pad_w, pad_w)), mode='constant')
        
        output = np.zeros_like(img)
        
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                region = padded_img[i : i + kernel.shape[0],
                                    j : j + kernel.shape[1]]
                output[i, j] = np.sum(region * kernel)
        
        return output

def gaussian_print(px, sigma, out_log):
    if sigma == 0:
        n = px - 1
        coeffs = np.array([math.comb(n, k) for k in range(n + 1)], dtype=float)
        kernel = np.outer(coeffs, coeffs)
        kernel /= kernel.sum()
    else:
        half_px = (px - 1) / 2
        x, y = np.mgrid[-half_px:half_px+1, -half_px:half_px+1]
        squared_distance = x**2 + y**2
        kernel = np.exp(-squared_distance / (2 * sigma**2))
        kernel /= kernel.sum()
    
    print(f"Gaussian filter (initial condtion, normalized to be sum = {kernel.sum()}):\
            \n{kernel}", file=out_log)

def motion_kernel(angle, d, sz, gauss, gpx, gsigma):
    if d<=0:
        d=1
    d = int(np.round(d))
    kern = np.ones((1, d), np.float32)
    c, s = np.cos(angle), np.sin(angle)
    A = np.float32([[c, -s, 0], [s, c, 0]])
    sz2 = sz // 2
    A[:,2] = (sz2, sz2) - np.dot(A[:,:2], ((d-1)*0.5, 0))
    kern = cv.warpAffine(kern, A, (sz, sz), flags=cv.INTER_LINEAR)
    
    if gauss is True:
        kern = gaussian(kern, gpx, gsigma)
    else:
        pass
    # normalize before returning
    kern /= kern.sum()
    return kern

def defocus_kernel(d, sz, gauss, gpx, gsigma):
    d = float(d)
    kern = np.zeros((sz, sz), np.uint8)
    radius = max(1, int(round(d/2.0)))
    center = (sz // 2, sz // 2)
    cv.circle(kern, center, radius, 255, -1, cv.LINE_AA, shift=1)
    kern = np.float32(kern) / 255.0
    
    if gauss is True:
        kern = gaussian(kern, gpx, gsigma)
    else:
        pass
    # normalize before returning
    kern /= kern.sum()
    return kern

def positive_int(value):
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not an integer")
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue

def to_u8_minmax(a):
    a = a.astype(np.float32)
    mn, mx = float(a.min()), float(a.max())
    if mx <= mn: 
        return np.zeros_like(a, np.uint8)
    return np.uint8(255 * (a - mn) / (mx - mn))

# ------------------------
# Quantitative evaluation
# ------------------------
# G: denoised input (float32/float64)
# Fhat: deblurred output, same size
# h: PSF array (energy normalized to sum==1), e.g., your geometry-derived PSF

def compute_ssim_cv(G, Fhat, mask=None, win_size=11, sigma=1.5, data_range=None, eps=1e-12):
    """
    Compute SSIM using NumPy and OpenCV only.
    Returns:
        ssim_all (float): global average of SSIM map
        ssim_masked (float or None): average over mask (if provided)
        ssim_map (H,W): per-pixel SSIM values
    """
    G = np.asarray(G)
    Fhat = np.asarray(Fhat)
    assert G.shape == Fhat.shape, "G and Fhat must have the same shape"

    Gf = G.astype(np.float32, copy=False)
    Ff = Fhat.astype(np.float32, copy=False)

    # If grayscale, expand to (H,W,1)
    if Gf.ndim == 2:
        Gf = Gf[..., None]
        Ff = Ff[..., None]
    H, W, C = Gf.shape

    # Determine data range for C1, C2
    if data_range is None:
        gmin, gmax = float(np.min(Gf)), float(np.max(Gf))
        fmin, fmax = float(np.min(Ff)), float(np.max(Ff))
        dr = max(gmax, fmax) - min(gmin, fmin)
        if dr <= 0:
            dr = 1.0
    else:
        dr = float(data_range)

    # SSIM constants
    K1, K2 = 0.01, 0.03
    C1 = (K1 * dr) ** 2
    C2 = (K2 * dr) ** 2

    ksize = max(3, int(win_size)) | 1  # ensure odd and >=3
    ssim_maps = []
    for ch in range(C):
        X = Gf[..., ch]
        Y = Ff[..., ch]

        muX = cv.GaussianBlur(X, (ksize, ksize), sigma, borderType=cv.BORDER_REFLECT)
        muY = cv.GaussianBlur(Y, (ksize, ksize), sigma, borderType=cv.BORDER_REFLECT)

        muX2 = muX * muX
        muY2 = muY * muY
        muXY = muX * muY

        sigmaX2 = cv.GaussianBlur(X * X, (ksize, ksize), sigma, borderType=cv.BORDER_REFLECT) - muX2
        sigmaY2 = cv.GaussianBlur(Y * Y, (ksize, ksize), sigma, borderType=cv.BORDER_REFLECT) - muY2
        sigmaXY = cv.GaussianBlur(X * Y, (ksize, ksize), sigma, borderType=cv.BORDER_REFLECT) - muXY

        # Clamp negative variances to zero (can happen due to numerical issues)
        sigmaX2 = np.maximum(sigmaX2, 0.0)
        sigmaY2 = np.maximum(sigmaY2, 0.0)
        
        num = (2 * muXY + C1) * (2 * sigmaXY + C2)
        den = (muX2 + muY2 + C1) * (sigmaX2 + sigmaY2 + C2) + eps
        ssim_maps.append(num / den)

    # Average across channels -> (H,W)
    ssim_map = np.mean(np.stack(ssim_maps, axis=-1), axis=-1)
    valid = np.isfinite(ssim_map)
    ssim_all = float(np.mean(ssim_map[valid])) if np.any(valid) else float("nan")

    # Average within mask
    ssim_masked = None
    if mask is not None:
        m = np.asarray(mask).astype(bool)
        assert m.shape == (H, W), "mask shape must match (H,W)"
        mv = m & valid
        ssim_masked = float(np.mean(ssim_map[mv])) if np.any(mv) else float("nan")

    return ssim_all, ssim_masked, ssim_map

def compute_psnr(A, B, mask=None, data_range=None, eps=1e-12):
    A = np.asarray(A, np.float32)
    B = np.asarray(B, np.float32)
    assert A.shape == B.shape, "PSNR: shapes must match"

    if mask is not None:
        m = np.asarray(mask).astype(bool)
        mse = float(np.mean((A[m] - B[m])**2)) if np.any(m) else np.nan
    else:
        mse = float(np.mean((A - B)**2))

    if data_range is None:
        # Pick a fixed peak across your dataset for comparability (see note below)
        peak = float(max(A.max(), B.max()) - min(A.min(), B.min()))
    else:
        peak = float(data_range)

    if mse <= eps:
        return float('inf')
    return 20.0 * np.log10((peak + eps) / np.sqrt(mse + eps))

def mask_edges(img, dx, dy):
    H, W = np.asarray(img).shape[:2]      # <-- 2D shape
    m = np.ones((H, W), dtype=bool)       # <-- always 2D
    
    # Left and right edges
    if dx > 0:
        m[:, :dx] = False
        m[:, -dx:] = False
    else:
        pass
    
    # Top and bottom edges
    if dy > 0:
        m[:dy, :] = False
        m[-dy:, :] = False
    else:
        pass
    
    return m

def difference_and_residual_with_metrics(
    G, Fhat, h, dx, dy, win_size=11, sigma=1.5,
    data_range=None, match_for_display=True,
    snr_db=None, debug_pred=False, out_log=sys.stdout):

    # 0) mask & types
    mask = mask_edges(G, dx, dy)
    G = np.asarray(G, np.float32)
    Fhat = np.asarray(Fhat, np.float32)

    # 1) reblur (circular) with a normalized PSF
    h = np.asarray(h, np.float32)
    h /= (h.sum() + 1e-12)
    reblur = cv.filter2D(Fhat, -1, cv.flip(h, -1), borderType=cv.BORDER_WRAP)

    # --- (A) quick sanity prints (optional) ---
    if debug_pred:
        print(f"G:      min={G.min():.4f} max={G.max():.4f} max-min={np.ptp(G):.4f}", file=out_log)
        print(f"Fhat:   min={Fhat.min():.4f} max={Fhat.max():.4f} max-min={np.ptp(Fhat):.4f}", file=out_log)
        print(f"reblur: min={reblur.min():.4f} max={reblur.max():.4f} max-min={np.ptp(reblur):.4f}", file=out_log)

    # --- (B) spectral prediction on the *same* masked, demeaned region ---
    if debug_pred and (snr_db is not None):
        H, W = G.shape[:2]
        kh, kw = h.shape[:2]
        psf_pad = np.zeros((H, W), np.float32)
        cy, cx = H//2, W//2
        psf_pad[cy-kh//2:cy-kh//2+kh, cx-kw//2:cx-kw//2+kw] = h
        psf_pad = np.fft.ifftshift(psf_pad)
        PSF = cv.dft(psf_pad, flags=cv.DFT_COMPLEX_OUTPUT)
        Hpow = PSF[...,0]**2 + PSF[...,1]**2

        K = 10**(-0.1 * float(snr_db))
        A = Hpow / (Hpow + K)

        g_mean_mask = float(G[mask].mean())
        Gz = (G - g_mean_mask).astype(np.float32)
        Wm = np.zeros_like(G, np.float32); Wm[mask] = 1.0
        Gf = cv.dft(Gz * Wm, flags=cv.DFT_COMPLEX_OUTPUT)
        Gpow = Gf[...,0]**2 + Gf[...,1]**2

        a_pred = float((A * Gpow).sum() / (Gpow.sum() + 1e-12))
        gamma0 = float(Hpow[0,0] / (Hpow[0,0] + K))
        b_pred = (gamma0 - a_pred) * g_mean_mask
        print(f"[pred(masked)] a_pred={a_pred:.4f}  b_pred={b_pred:.4f}  gamma0={gamma0:.4f}", file=out_log)

    # --- measured spatial fit on the masked interior (reblur ≈ a*G + b) ---
    g = G[mask].astype(np.float64)
    r = reblur[mask].astype(np.float64)
    g_mean = g.mean()
    r_mean = r.mean()
    den = np.sum((g - g_mean)**2) + 1e-12
    a_meas = float(np.sum((g - g_mean) * (r - r_mean)) / den)
    b_meas = float(r_mean - a_meas * g_mean)
    corr_meas = float(np.corrcoef(g, r)[0, 1])

    print(f" [fit(masked)] a_meas={a_meas:.4f}  b_meas={b_meas:.4f}    corr={corr_meas:.4f}", file=out_log)

    # 2) residuals & metrics (unchanged)
    R = G - reblur
    rms_R = float(np.sqrt(np.mean((R[mask])**2)))
    vol_gain = cv.Laplacian(Fhat, cv.CV_32F)[mask].var() / (cv.Laplacian(G, cv.CV_32F)[mask].var() + 1e-8)

    dr = (np.percentile(G[mask], 99.9) - np.percentile(G[mask], 0.1)) if data_range is None else float(data_range)
    _, ssim_re_masked, ssim_re_map = compute_ssim_cv(G, reblur, mask=mask, win_size=win_size, sigma=sigma, data_range=dr)
    psnr_re_masked = compute_psnr(G, reblur, mask=mask, data_range=dr)

    Fhat_disp = Fhat
    if match_for_display:
        mu, sG = G[mask].mean(), G[mask].std()
        Fhat_disp = (Fhat - Fhat[mask].mean()) * (sG / (Fhat[mask].std() + 1e-8)) + mu
    Delta = Fhat_disp - G
    
    psnr_fg_masked = compute_psnr(Fhat, G, mask=mask, data_range=dr)
    
    ssim_all, ssim_masked, ssim_map = compute_ssim_cv(G, Fhat, mask=mask, win_size=win_size, sigma=sigma, data_range=dr)

    return (Delta, R, rms_R, vol_gain,
            ssim_all, ssim_masked, ssim_map,
            float(ssim_re_masked), ssim_re_map, float(psnr_fg_masked), float(psnr_re_masked))


class Tee():
    def __init__(self, filename):
        self.filename = filename
    def write(self, text):
        with open(self.filename, 'a') as handle:
            handle.write(text)
        print(text, end='')

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    pass

def get_args():
    
    parser = argparse.ArgumentParser(description=help_desc_msg, formatter_class=CustomFormatter)
    
    # Calculate the shift of an input image in pixels between observation start and stop timings using SPICE kernels.
    parser.add_argument('cube', type=str, 
                        help='Input ISIS cube file path')
    parser.add_argument("-up", "--uprec", type=positive_int, default=6, 
                        help=f"Set UTC decimal precision (default: 6, microsecond precision).")
    parser.add_argument("-log", "--log", action="store_true", 
                        help=f"Record a log file, <input>.log.txt")
    parser.add_argument("-k", "--kern", type=str, nargs='+', default=None, 
                        help=f"Add extra SPICE kernels to be loaded explicitly")
    parser.add_argument("-u", "--unload", type=str, nargs='+', default=None, 
                        help=f"Unload SPICE kernels specified by this option.\
                               \nYou can avoid the use of these kernels auto-loaded by this program")
    parser.add_argument("-abc", "--abcorr", type=str.lower, default="cn+s", 
                        choices=["none", "lt", "lt+s", "cn", "cn+s"], 
                        help=f"Set aberration correction for calculating the state of a target body relative to an observer.\
                             \nSee https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/sincpt_c.html and \
                             \nhttps://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkezr_c.html")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, 
                        help=f"Set verbose mode")
    parser.add_argument("-stop", "--stop-at-shift", action="store_true", default=False, 
                        help=f"Stop after calculating the shift")
    parser.add_argument("-times", "--stop-at-times", action="store_true", default=False, 
                        help=f"Stop after calculating the ephemeris times and image time")
    
    # Apply Wiener deconvolution to an input image with a simple PSF based on the shift.
    parser.add_argument("-skip", "--skip-shift", action="store_true", default=False, 
                        help=f"Skip pixel shift calculation and directly apply Wiener deconvolution")
    parser.add_argument('-a', '--ang', type=int, default=0, 
                        help='(optional for -skip) the angle (degrees) of a linear PSF')
    parser.add_argument('-d', '--diam', type=int, default=50, 
                        help='(optional for -skip) the diameter/length (pixels) of a circular/linear PSF')
    parser.add_argument("-sn", "--snr", type=int, default=None, 
                        help=f"Set the signal-to-noise ratio (dB) for the Wiener filter")
    parser.add_argument("-c", "--circle", action="store_true", 
                        help=f"Use a circular PSF instead of a linear PSF")
    parser.add_argument("-s", "--save", action="store_true", 
                        help=f"Export output images every time track bars are moved")
    parser.add_argument("-se", "--save_exit", action="store_true", 
                        help=f"Run this script, export output, and terminate it immediatly")
    parser.add_argument("-pw", "--psf_width", type=positive_int, default=151, 
                        help=f"Set a window size of psf (in pixels).\
                             \nFor example, a linear PSF would have a length of ~30 pixels, -kw 50 will be fine.")
    parser.add_argument("-e", "--edgetaper", type=str.lower, default="manual", choices=["manual", "auto"],
                        help=f"Select edge‐tapering diameters to reduce ringing artifacts. Not interacive in deconvolution window.\
                             \n\"auto\" values are from half of pixel-shift diameters;\
                             \n\"manual\" uses eparams values that are set by -ep/--eparams option.")
    parser.add_argument("-ep", "--eparams", type=int, nargs=2, default=[162, 0], metavar=("dx", "dy"),
                        help=f"(only used if --edgetaper manual) the dx,dy taper values.\
                             \nDefault values are dx:162, dy:0 (left & right: 81 pixels; top & bottom: 0 pixels), which works well for most MEx SRC images.")
    parser.add_argument("-g", "--gauss", action="store_true", default=False, 
                        help=f"Apply a gaussian filter")
    parser.add_argument("-gp", "--gparams", metavar=("width", "sigma"), type=float, default=[3, 1.0], nargs=2, 
                        help=f"Set a width (pix; formatted to positive int) and a sigma value (float) of a gaussian filter")
    parser.add_argument("-ev", "--evaluate", action="store_true", default=False, 
                        help=f"Evaluate results by quantitative metrics (RMS residual, volumentric gain, SSIM)")
    parser.add_argument("-p", "--prec", type=positive_int, default=2, 
                        help=f"Set decimal precisions for track bars scaling factors, standard output, and csv output.")
    parser.add_argument("-t", "--transpose", action="store_true", default=False, 
                        help=f"Transpose the output csv file instead of the default format (1 column per parameter).")
    parser.add_argument("-o", "--outfile", type=str, default=None, 
                        help=f"Set output file path without file extension explicitly")

    args = parser.parse_args()
    return(args)

def main():
    terminal_width = os.get_terminal_size().columns
    print("=" * terminal_width)
    
    args = get_args()
    
    # Calculate the shift of an input image in pixels between observation start and stop timings using SPICE kernels.
    cub = args.cube
    
    if args.outfile is not None:
        out_name = args.outfile
    else:
        out_name = os.path.splitext(cub)[0]
    
    if args.log is True:
        log_name = f"{out_name}.dbl.log"
        out_log = Tee(log_name)
        if os.path.exists(log_name):
            os.remove(log_name)
        else:
            pass
        print(f"Logging: ON", file=out_log)
    else:
        out_log = sys.stdout
        print(f"Logging: OFF", file=out_log)
    
    s = ""
    for arg in sys.argv:
        s = s + arg + " "
    
    print(f"{os.path.basename(sys.executable)} {s}", file=out_log)
    print("=" * terminal_width, file=out_log)
    
    if args.skip_shift is True:
        print("Skipping pixel shift calculation and directly applying Wiener deconvolution.", file=out_log)
    else:
        
        kernels = []
        
        # Loading SPICE kernels other than the ones auto-loaded by ALE
        if args.kern is not None:
            kernels += args.kern
        else:
            pass
        
        # Loading SPICE kernels auto-loaded by ALE
        if ale.util.generate_kernels_from_cube(cub) is not None:
            kernels += ale.util.generate_kernels_from_cube(cub, expand=True)
        else:
            sys.exit("ERROR: No kernels found.")
        
        spice.furnsh(kernels)
        
        try:
            lbl = ale.load(cub, formatter="ale", props={"kernels": kernels}, verbose=False)
        except:
            print("WARNING: No label found by ale.load. Trying ale.drivers.parse_label(cub) instead.", file=out_log)
        
        try:
            lbl = ale.drivers.parse_label(cub)
        except:
            print("WARNING: No label found by ale.drivers.parse_label. Trying ale.drivers.parse_label(cub, pvl.grammar.ISISGrammar()) instead.", file=out_log)
        
        try:
            import pvl
            lbl = ale.drivers.parse_label(cub, pvl.grammar.ISISGrammar())
        except:
            sys.exit("ERROR: No label found by ale.drivers.parse_label(cub, pvl.grammar.ISISGrammar()).")
        
        # Loading DSK kernels
        if lbl["IsisCube"]["Kernels"]["ShapeModel"] is not None:
            dsk = lbl["IsisCube"]["Kernels"]["ShapeModel"]
            spice.furnsh(dsk)
        else:
            pass
        
        if spice.ktotal("DSK") == 0:
            method = "ellipsoid"
            print(f"WARNING: No DSK kernels loaded. Using {method} for sincpt instead.", file=out_log)
        elif spice.ktotal("DSK") == 1:
            method = "dsk/unprioritized"
            print(f"Using {method} for sincpt.\
                  \nhttps://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/sincpt_c.html", file=out_log)
        elif spice.ktotal("DSK") > 1:
            print(f"ERROR: More than one DSK kernels loaded ({spice.ktotal('DSK')}).", file=out_log)
            for i in range(spice.ktotal("DSK")):
                spice.kdata(i, "DSK")[0]
            sys.exit(f"Run this program again with \"-u|--unload\" option to unload the unwanted DSK kernel(s).")
        
        # Unloading kernels if specified
        if args.unload is not None:
            for kernel in args.unload:
                try:
                    spice.unload(kernel)
                    print(f"Unloaded kernel: {kernel}", file=out_log)
                except Exception as e:
                    print(f"WARNING: Failed to unload kernel {kernel}: {e}", file=out_log)
        else:
            pass
        
        # Listing loaded kernels
        if args.verbose:
            print("=" * terminal_width, file=out_log)
            print(f"Loaded kernels", file=out_log)
            for i in range(spice.ktotal("all")):
                print(spice.kdata(i, "all")[0], file=out_log)
            print("=" * terminal_width, file=out_log)
        else:
            pass
        
        # Set UTC decimal precisions; 6 (= microsecond precisios) in most cases
        uprec = args.uprec
        print(f"UTC decimal precision: {uprec}", file=out_log)
        
        try:
            utc1 = lbl["IsisCube"]["Instrument"]["StartTime"].strftime(f"%Y-%m-%dT%H:%M:%S.%f")
            utc2 = lbl["IsisCube"]["Instrument"][ "StopTime"].strftime(f"%Y-%m-%dT%H:%M:%S.%f")
            
            if utc1 == utc2:
                raise ValueError("StartTime and StopTime are the same.")
            et1 = spice.utc2et(utc1)
            et2 = spice.utc2et(utc2)
            et0 = (et1+et2)/2
            utc0 = spice.et2utc(et0, "ISOC", uprec)
            exposure_sec = et2 - et1

            print(f"StartTime: {utc1} (EphemerisTime: {et1:.{uprec}f}) <= StartTime (original label info)", file=out_log)
            print(f"StopTime:  {utc2} (EphemerisTime: {et2:.{uprec}f}) <=  StopTime (original label info)", file=out_log)
            print(f"ImageTime: {utc0} (EphemerisTime: {et0:.{uprec}f}) <= (StartTime + StopTime)/2", file=out_log)
            print(f"Exposure duration (approx.): {exposure_sec:.{uprec}f} sec <= StopTime - StartTime", file=out_log)
            
            stoptime = True
        except Exception as e:
            print(f"WARNING: {e}", file=out_log)
            stoptime = False
        
        try:
            exposure_quantity = lbl["IsisCube"]["Instrument"]["ExposureDuration"] # e.g., Quantity(value=20.16, units='ms')
            value = exposure_quantity.value
            unit = exposure_quantity.units.lower()  # make it lowercase for consistency
            conversion_factors = {
                "s": 1,
                "sec": 1,
                "seconds": 1,
                "ms": 1e-3,
                "msec": 1e-3,
                "milliseconds": 1e-3,
                "us": 1e-6,
                "µs": 1e-6,
                "microseconds": 1e-6,
                "ns": 1e-9,
                "nanoseconds": 1e-9,
            }
            exposure_sec = value * conversion_factors.get(unit, 1)
            print(f"Exposure duration (precise): {exposure_sec:.{uprec}f} sec <= {value} {unit} (original label info)", file=out_log)
            exposure_approx = False
        except:
            print(f"WARNING: No \"ExposureDuration\" label specified. Using the approximate value (StopTime - StartTime) instead.", file=out_log)
            value = exposure_sec
            unit = "sec"
            exposure_approx = True
        
        print("=" * terminal_width, file=out_log)

        if stoptime is True:
            try:
                if exposure_approx is True:
                    pass
                elif exposure_approx is False:
                    et1 = et0 - exposure_sec/2
                    et2 = et0 + exposure_sec/2
                    utc1 = spice.et2utc(et1, "ISOC", uprec)
                    utc2 = spice.et2utc(et2, "ISOC", uprec)
                    print(f"ImageTime: {utc0} (EphemerisTime: {et0:.{uprec}f}) <= (StartTime + StopTime)/2", file=out_log)
                    print(f"StartTime: {utc1} (EphemerisTime: {et1:.{uprec}f}) <= ImageTime - (exposure/2)", file=out_log)
                    print(f" StopTime: {utc2} (EphemerisTime: {et2:.{uprec}f}) <= ImageTime + (exposure/2)", file=out_log)
                    print("=" * terminal_width)
            except:
                print(f"WARNING: No StopTime specified. Using the StartTime and ExposureDuration instead.", file=out_log)
        elif stoptime is False:
            try:
                utc1 = lbl["IsisCube"]["Instrument"]["StartTime"].strftime("%Y-%m-%dT%H:%M:%S.%f")
                et1 = spice.utc2et(utc1)
                et0 = et1 + (exposure_sec/2)
                et2 = et1 + exposure_sec
                utc0 = spice.et2utc(et0, "ISOC", uprec)
                utc2 = spice.et2utc(et2, "ISOC", uprec)
                print(f"StartTime: {utc1} (EphemerisTime: {et1:.{uprec}f}) <= StartTime", file=out_log)
                print(f" StopTime: {utc2} (EphemerisTime: {et2:.{uprec}f}) <= StartTime + exposure", file=out_log)
                print(f"ImageTime: {utc0} (EphemerisTime: {et0:.{uprec}f}) <= StartTime+ (exposure/2)", file=out_log)
                print("=" * terminal_width, file=out_log)
            except:
                sys.exit(f"ERROR: Neither StopTime nor ExposureDuration specified.")
        
        if args.stop_at_times is True:
            sys.exit("Stopped after calculating the ephemeris times and image time.")
        
        # For MEx SRC, instfrm, instc = 'MEX_HRSC_SRC', -41220 (See FK/MEX_V16.TF)
        attempts = [
            lambda: (lbl["NaifKeywords"][f"INS{spice.bodn2c(lbl['IsisCube']['Archive']['DetectorId'])}_FOV_FRAME"], spice.bodn2c(lbl['IsisCube']['Archive']['DetectorId'])),
            lambda: (lbl["IsisCube"]["Archive"]["DetectorId"], spice.bodn2c(lbl["IsisCube"]["Archive"]["DetectorId"])),
            lambda: (spice.bodc2n(lbl["IsisCube"]["Kernels"]["NaifIkCode"]), lbl["IsisCube"]["Kernels"]["NaifIkCode"]),
            lambda: (spice.bodc2n(lbl["IsisCube"]["Kernels"]["NaifFrameCode"]), lbl["IsisCube"]["Kernels"]["NaifFrameCode"]),
            ]
        
        for attempt in attempts:
            try:
                instfrm, instc = attempt()
                break  # Successfully got the values; exit the loop.
            except Exception:
                continue  # If this attempt fails, try the next one.
        else:
            sys.exit("ERROR: No detector frame specified.")
        
        # For MEx SRC, focal_length_mm = 984.76 (mm)
        if lbl["NaifKeywords"][f"INS{instc}_FOCAL_LENGTH"] is not None:
            focal_length_mm = lbl["NaifKeywords"][f"INS{instc}_FOCAL_LENGTH"]
        elif spice.gdpool(f'INS{instc}_FOCAL_LENGTH', 0, 1)[0] is not None:
            focal_length_mm = spice.gdpool(f'INS{instc}_FOCAL_LENGTH', 0, 1)[0]
        else:
            sys.exit("ERROR: No focal length specified.")
        
        focal_length_km = focal_length_mm * 1e-6 # convert mm to km
        
        # For MEx SRC, pixel_size_x, pixel_size_y = 9.0, 9.0 (micrometers)
        if lbl["NaifKeywords"][f"INS{instc}_PIXEL_SIZE"] is not None:
            try:
                pixel_size_x, pixel_size_y = lbl["NaifKeywords"][f"INS{instc}_PIXEL_SIZE"]
            except:
                pixel_size_x = lbl["NaifKeywords"][f"INS{instc}_PIXEL_SIZE"]
                pixel_size_y = lbl["NaifKeywords"][f"INS{instc}_PIXEL_SIZE"]
        elif spice.gdpool(f'INS{instc}_PIXEL_SIZE', 0, 2) is not None:
            pixel_size_x, pixel_size_y = spice.gdpool(f'INS{instc}_PIXEL_SIZE', 0, 2)
        else:
            sys.exit("ERROR: No pixel size specified.")
        
        pixel_size_x_km = pixel_size_x * 1e-9 # convert μm to km
        pixel_size_y_km = pixel_size_y * 1e-9 # convert μm to km
        
        # For MEx SRC, tgt, bodyfrm = 'PHOBOS', 'IAU_PHOBOS'
        if lbl["IsisCube"]["Instrument"]["TargetName"] is not None:
            tgt = lbl["IsisCube"]["Instrument"]["TargetName"]
            bodyfrm = spice.cnmfrm(tgt)[1]
        elif lbl["NaifKeywords"]["BODY_CODE"] is not None:
            tgt = spice.bodc2n(lbl["NaifKeywords"]["BODY_CODE"])
            bodyfrm = spice.cidfrm(lbl["NaifKeywords"]["BODY_CODE"])[1]
        else:
            sys.exit("ERROR: No target frame specified.")
        
        try:
            # For MEx SRC, obs = 'MEX_HRSC' (if SPK/MEX_STRUCT_V01.BSP is loaded additionally)
            obs = spice.bodc2n(spice.frinfo(instc)[0])
        except Exception:
            # For MEx SRC, obs = 'MARS EXPRESS'
            if lbl["IsisCube"]["Instrument"]["SpacecraftName"] is not None:
                obs = lbl["IsisCube"]["Instrument"]["SpacecraftName"]
                if "_" in obs: # e.g., 'VIKING_ORBITER_2'
                    obs = obs.replace("_", " ")
            else:
                sys.exit("ERROR: No spacecraft name specified.")
        
        if args.verbose:
            print(f"Camera specs:", file=out_log)
            print(f"Name (frame): {instfrm} (ID: {instc})", file=out_log)
            print(f"Focal length: {focal_length_mm} (mm)", file=out_log)
            print(f"Pixel size:   {pixel_size_x} x {pixel_size_y} (\u03BCm)", file=out_log)
            print("=" * terminal_width, file=out_log)
        else:
            pass
        
        abcorr = args.abcorr
        
        try:
            obs = spice.bodc2n(spice.frinfo(instc)[0]) # For MEx SRC, obs = 'MEX_HRSC' (if SPK/MEX_STRUCT_V01.BSP is loaded additionally)
            bsight = spice.getfov(instc, 256)[2] # For MEx SRC, bsight = array([  0.  ,   0.  , 984.76])
            bod2spt_bodyfrm_et1, _, obs2spt_bodyfrm_et1 = spice.sincpt(method, tgt, et1, bodyfrm, abcorr, obs, instfrm, bsight)
            obs2bod_bodyfrm_et1 = spice.vsub(obs2spt_bodyfrm_et1, bod2spt_bodyfrm_et1)
            obs2bod_bodyfrm_et2, _ = spice.spkpos(tgt, et2, bodyfrm, abcorr, obs)
            obs2obs_bodyfrm_et2 = spice.vsub(obs2bod_bodyfrm_et2, obs2bod_bodyfrm_et1)
            obs2spt_bodyfrm_et2 = spice.vadd(obs2obs_bodyfrm_et2, obs2spt_bodyfrm_et1)
            obs2spt_instfrm_et1 = spice.mxv(spice.pxform(bodyfrm, instfrm, et1), obs2spt_bodyfrm_et1)
            obs2spt_instfrm_et2 = spice.mxv(spice.pxform(bodyfrm, instfrm, et2), obs2spt_bodyfrm_et2)
        
        except Exception:
            sys.exit(f"ERROR: Failed to get {tgt}\'s positions relative to {obs} in the frame \"{instfrm}\".") 
        
        if args.verbose:
            dist_et1 = spice.vnorm(obs2spt_instfrm_et1)
            dist_et2 = spice.vnorm(obs2spt_instfrm_et2)
            print(f"Surface intercept point relative to {obs} (frame: \"{instfrm}\") at ET1: {obs2spt_instfrm_et1} (Dist. {dist_et1:.2f} km)", file=out_log)
            print(f"Surface intercept point relative to {obs} (frame: \"{instfrm}\") at ET2: {obs2spt_instfrm_et2} (Dist. {dist_et2:.2f} km)", file=out_log)
        
        x_fp_et1_km = obs2spt_instfrm_et1[0] * (focal_length_km / obs2spt_instfrm_et1[2])
        y_fp_et1_km = obs2spt_instfrm_et1[1] * (focal_length_km / obs2spt_instfrm_et1[2])
        x_fp_et2_km = obs2spt_instfrm_et2[0] * (focal_length_km / obs2spt_instfrm_et2[2])
        y_fp_et2_km = obs2spt_instfrm_et2[1] * (focal_length_km / obs2spt_instfrm_et2[2])
        
        x_pixel_et1 = x_fp_et1_km / pixel_size_x_km
        y_pixel_et1 = y_fp_et1_km / pixel_size_y_km
        x_pixel_et2 = x_fp_et2_km / pixel_size_x_km
        y_pixel_et2 = y_fp_et2_km / pixel_size_y_km
        
        shift_x = x_pixel_et2 - x_pixel_et1
        shift_y = y_pixel_et2 - y_pixel_et1
        diam = np.sqrt(shift_x**2 + shift_y**2)
        ang = np.degrees(np.arctan2(shift_y, shift_x))
        
        print(f"Observer:              {obs} (SPICE body ID: {spice.bodn2c(obs)})", file=out_log)
        print(f"Target:                {tgt} (SPICE body ID: {spice.bodn2c(tgt)})", file=out_log)
        print(f"Body frame:            {bodyfrm} (SPICE FK ID: {spice.namfrm(bodyfrm)})", file=out_log)
        print(f"Instrument frame:      {instfrm} (SPICE FK ID: {instc})", file=out_log)
        print(f"Aberration correction: {abcorr}", file=out_log)
        print(f"Pixel shift:           \u0394x = {shift_x:.4f} (pix),  \u0394y = {shift_y:.4f} (pix), \u0394t = {value:.4f} {unit}", file=out_log)
        print(f"Linear PSF geometry:   d = {diam:.4f} (pix), ang = {ang:.4f} (deg) <= d = sqrt(\u0394x^2+\u0394y^2) and ang = arctan(\u0394y/\u0394x)", file=out_log)
        print("=" * terminal_width, file=out_log)

        if args.stop_at_shift:
            sys.exit("Stopped after calculating the shift.")
        else:
            pass
        

########################################################################################################################################################
    # Apply Wiener deconvolution to an input image with a simple PSF based on the shift.
    # Open input cube for metadata.

    print(f"Applying interactive Wiener deconvolution", file=out_log)
    print(f"Press SPACE to switch between linear and circular PSF", file=out_log)
    print(f"Press ESC or close one of windows to exit", file=out_log)
    
    if args.skip_shift is True:
        ang = args.ang # default: 0 degrees
        diam = args.diam # default: 50 pixels
        shift_x = diam * np.cos(np.deg2rad(ang))
        shift_y = diam * np.sin(np.deg2rad(ang))
    else:
        pass
        
    # High-precision scaling (4-decimal precision by default).
    scale = float(f"1e+{args.prec}")
    threshold = 1/scale
    prec = f"0=+{5+args.prec}.{args.prec}f"
    csvp = f".{args.prec+2}f"
    print(f"Precision: {args.prec}", file=out_log)
    
    # Import image data.
    img = import_isis_cube(cub, out_log)
    print(f"Samples (columns): {img.shape[1]}", file=out_log)
    print(f"     Lines (rows): {img.shape[0]}", file=out_log)

    if args.snr is not None:
        snr = args.snr
        print(f"Signal/Noise ratio: {snr:.2f} (dB) (apriori)", file=out_log)
    else:
        snr = estimate_snr(img)
        print(f"Signal/Noise ratio: {snr:.2f} (dB) (estimated)", file=out_log)
    
    # Determine normalization bounds to export 8-bit png:
    if img.dtype is not np.uint8:
        uniq_vals = np.unique(img)
        if uniq_vals.shape[0] > 1:
            norm_low = uniq_vals[1]
        else:
            norm_low = uniq_vals[0]
        norm_high = uniq_vals[-1]
        disp_input = ((img - norm_low) / (norm_high - norm_low) * 255).astype(np.float32)
        disp_input = np.clip(disp_input, 0, 255).astype(np.uint8)
    else:
        disp_input = img
    
    png_inp = disp_input.copy()
    h1, w1 = disp_input.shape
    h2 = 500
    resize_rate = h2 / h1
    w2 = int(w1 * resize_rate)
    disp_img = cv.resize(disp_input, (w2, h2))
    cv.imshow('input', disp_img)
    
    if args.edgetaper == "manual":
        dx, dy = make_half_odd(args.eparams[0]), make_half_odd(args.eparams[1])
    else: #  args.edgetaper == "auto"
        dx, dy = make_half_odd(shift_x), make_half_odd(shift_y)
    
    img = blur_edge(img, dx, dy)
    
    png_tap= to_u8_minmax(img)
    
    # Create windows.
    deconv_win = 'deconvolution'
    cv.namedWindow(deconv_win)
    cv.namedWindow('psf', 0)
    
    def nothing(x):
        pass
    
    cv.createTrackbar('angle', deconv_win, int((ang + 180) * scale), int(360 * scale), nothing)
    cv.setTrackbarMin('angle', deconv_win, 0)
    cv.createTrackbar('d', deconv_win, int(diam * scale), int(500 * scale), nothing)
    cv.setTrackbarMin('d', deconv_win, 0)
    cv.createTrackbar('SNR (dB)', deconv_win, int(snr * scale), int(60 * scale), nothing)
    cv.setTrackbarMin('SNR (dB)', deconv_win, 0)
    
    defocus_flag = args.circle
    if args.gauss is True:
        prev_params = {'angle': None, 'd': None, 'snr': None, 'gwidth': None, 'gsigma': None}
    else:
        prev_params = {'angle': None, 'd': None, 'snr': None}
    
    first_shift = True
    
    # Gaussian filter setting (initial condition).
    gwidth = positive_int(args.gparams[0])
    gsigma = args.gparams[1]
    if args.gauss is True:
        cv.createTrackbar('gwidth', deconv_win, gwidth, 100, nothing)
        cv.setTrackbarMin('gwidth', deconv_win, 0)
        cv.createTrackbar('gsigma', deconv_win, int(gsigma * scale), int(10* scale), nothing)
        cv.setTrackbarMin('gsigma', deconv_win, 0)
        print(f"Gaussian filter: {args.gauss}", file=out_log)
        print(f"Gaussian kernel width: {gwidth} (pix)", file=out_log)
        print(f"Gaussian sigma: {gsigma}", file=out_log)
        gaussian_print(gwidth, gsigma, out_log)
    else:
        print(f"Gaussian filter: {args.gauss}", file=out_log)
    
    def update(_):
        nonlocal prev_params, first_shift, shift_x, shift_y, defocus_flag, scale, threshold, prec, csvp
        
        if first_shift and (shift_x != 0.0 or shift_y != 0.0):
            computed_d = np.sqrt(shift_x**2 + shift_y**2)
            computed_angle_deg = np.degrees(np.arctan2(shift_y, shift_x))
            # If negative, convert to positive within [0,360)
            if computed_angle_deg < 0:
                computed_angle_deg += 360
            cv.setTrackbarPos('angle', deconv_win, int(computed_angle_deg * scale))
            cv.setTrackbarPos('d', deconv_win, int(computed_d * scale))
            current_angle_deg = computed_angle_deg
            current_d = computed_d
            first_shift = False
        else:
            current_angle_deg = (cv.getTrackbarPos('angle', deconv_win) / scale)
            current_d = cv.getTrackbarPos('d', deconv_win) / scale

        current_snr = (cv.getTrackbarPos('SNR (dB)', deconv_win) / scale)
        noise = 10**(-0.1 * current_snr)
        
        if args.gauss is True:
            current_gwidth = cv.getTrackbarPos('gwidth', deconv_win)
            current_gsigma = cv.getTrackbarPos('gsigma', deconv_win) / scale
            
            if (prev_params['angle'] is None or 
                abs(prev_params['angle'] - current_angle_deg) > threshold or
                abs(prev_params['d'] - current_d) > threshold or
                prev_params['snr'] != current_snr
                or prev_params['gwidth'] != current_gwidth
                or prev_params['gsigma'] != current_gsigma):
                prev_params['angle'] = current_angle_deg
                prev_params['d'] = current_d
                prev_params['snr'] = current_snr
                prev_params['gwidth'] = current_gwidth
                prev_params['gsigma'] = current_gsigma
                shift_x = current_d * np.cos(np.deg2rad(current_angle_deg))
                shift_y = current_d * np.sin(np.deg2rad(current_angle_deg))
                print(f"\u0394x: {shift_x:{prec}} (pix), \u0394y: {shift_y:{prec}} (pix), d: {current_d:{prec}} (pix), d_psf: {int(np.round(current_d)):03d} (pix), angle: {current_angle_deg:{prec}} (\N{DEGREE SIGN}), snr: {current_snr:{prec}} (dB), gwidth: {current_gwidth:03d} (pix), gsigma: {current_gsigma:{prec}}, edge_dx: {dx:03d} (pix), edge_dy: {dy:03d} (pix)", file=out_log)

        else:
            current_gwidth = gwidth
            current_gsigma = gsigma
            
            if (prev_params['angle'] is None or 
                abs(prev_params['angle'] - current_angle_deg) > threshold or
                abs(prev_params['d'] - current_d) > threshold or
                prev_params['snr'] != current_snr):
                prev_params['angle'] = current_angle_deg
                prev_params['d'] = current_d
                prev_params['snr'] = current_snr
                # Compute x, y values using the slider values:
                # x = -d * cos(angle) ; y = d * sin(angle)
                shift_x = current_d * np.cos(np.deg2rad(current_angle_deg))
                shift_y = current_d * np.sin(np.deg2rad(current_angle_deg))
                print(f"\u0394x: {shift_x:{prec}} (pix), \u0394y: {shift_y:{prec}} (pix), d: {current_d:{prec}} (pix), d_psf: {int(np.round(current_d)):03d} (pix), angle: {current_angle_deg:{prec}} (\N{DEGREE SIGN}), snr: {current_snr:{prec}} (dB), edge_dx: {dx:03d} (pix), edge_dy: {dy:03d} (pix)", file=out_log)
        
        # Use the slider angle (in [0,360)) for PSF generation.
        ang = - np.deg2rad(current_angle_deg)
        
        if defocus_flag:
            psf = defocus_kernel(d=current_d, sz=args.psf_width, \
                                gauss=args.gauss, gpx=current_gwidth, gsigma=current_gsigma)
        else:
            psf = motion_kernel(angle=ang, d=current_d, sz=args.psf_width, \
                                gauss=args.gauss, gpx=current_gwidth, gsigma=current_gsigma)
        
        cv.imshow('psf', psf)
        
        png_psf = np.uint8(255 * (psf / psf.max()))

        H, W    = img.shape
        kh, kw  = psf.shape
        
        # 1) Zero-pad & *center* your PSF in the array
        psf_pad = np.zeros((H, W), dtype=np.float32)
        cy, cx  = H//2, W//2
        psf_pad[cy - kh//2 : cy - kh//2 + kh,
                cx - kw//2 : cx - kw//2 + kw] = psf
        
        # 2) Move PSF center to the origin (0,0) before DFT
        psf_pad = np.fft.ifftshift(psf_pad)
        
        # 3) DFT of image & kernel
        IMG = cv.dft(img,     flags=cv.DFT_COMPLEX_OUTPUT)
        PSF = cv.dft(psf_pad, flags=cv.DFT_COMPLEX_OUTPUT)
        

        ## Debugging info
        # Check H(0)
        print(f"[psf] sum={psf.sum():.6f}, shape={psf.shape}")
        # DC (zero-frequency) is at [0,0] after ifftshift
        H0_re, H0_im = PSF[0,0,0], PSF[0,0,1] # DC component
        H0 = (H0_re**2 + H0_im**2)**0.5
        print(f"[wiener] H(0) magnitude = {H0:.6f} (should be ~1.0 if psf.sum()==1)")
        K = 10**(-0.1 * current_snr)
        gamma0 = (H0*H0) / (H0*H0 + K)
        print(f"[wiener] predicted DC gain (gamma0) = {gamma0:.4f}")
        # Compute A(f) with the SAME H(f) you use in Wiener
        Hpow = PSF[...,0]**2 + PSF[...,1]**2        # |H|^2
        A = Hpow / (Hpow + K)
        # Energy weights from G
        Gf = cv.dft(img, flags=cv.DFT_COMPLEX_OUTPUT)
        Gpow = Gf[...,0]**2 + Gf[...,1]**2
        a_pred = float((A * Gpow).sum() / (Gpow.sum() + 1e-12))
        g_mean = float(img.mean())
        gamma0 = float(Hpow[0,0] / (Hpow[0,0] + K))
        b_pred = (gamma0 - a_pred) * g_mean
        print(f"[pred] a_pred={a_pred:.4f}  b_pred={b_pred:.4f}  gamma0={gamma0:.4f}")
        

        # 4) Build the true Wiener filter with H*
        PSF_conj = PSF.copy()
        PSF_conj[...,1] *= -1                    # flip imaginary part
        mag2     = PSF[...,0]**2 + PSF[...,1]**2  # |H|^2
        iPSF     = PSF_conj / (mag2[...,None] + noise)
        
        # 5) Filter & inverse DFT
        RES = cv.mulSpectrums(IMG, iPSF, flags=0) 
        res = cv.idft(RES, flags=cv.DFT_SCALE|cv.DFT_REAL_OUTPUT)
        
        # Original code for PSF-based deconvolution
        # psf_pad = np.zeros_like(img)
        # kh, kw = psf.shape
        # psf_pad[:kh, :kw] = psf
        # PSF = cv.dft(psf_pad, flags=cv.DFT_COMPLEX_OUTPUT, nonzeroRows=kh)
        # PSF2 = (PSF**2).sum(-1) # = |H|^2
        # iPSF = PSF / (PSF2 + noise)[..., np.newaxis]
        # RES = cv.mulSpectrums(IMG, iPSF, 0)
        # res = cv.idft(RES, flags=cv.DFT_SCALE | cv.DFT_REAL_OUTPUT)
        # off_y = -((kh - 1) // 2)
        # off_x = -((kw - 1) // 2)
        # res = np.roll(res, off_y, axis=0)
        # res = np.roll(res, off_x, axis=1)
        
        disp_res = cv.normalize(res, None, 0, 255, cv.NORM_MINMAX)
        png_dbl = disp_res.copy()
        disp_res = cv.convertScaleAbs(disp_res)
        disp_res = cv.resize(disp_res, (w2, h2))
        
        overlay = disp_res.copy()
        font = cv.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        text = f"dx: {shift_x:.2f} (pix), dy: {shift_y:.2f} (pix)"
        cv.putText(overlay, text, (10, 30), font, font_scale, (0, 255, 0), thickness, cv.LINE_AA)
        disp_res = overlay
        
        cv.imshow(deconv_win, disp_res)
        
        def save():
            
            in_name = os.path.splitext(os.path.basename(cub))[0]
            ext = os.path.splitext(cub)[1]

            png_inp_name = f"{out_name}.inp.png"
            out_tap_name = f"{out_name}.tap{ext}"
            png_tap_name = f"{out_name}.tap.png"
            out_dbl_name = f"{out_name}.dbl{ext}"
            png_dbl_name = f"{out_name}.dbl.png"
            out_psf_name = f"{out_name}.psf{ext}"
            png_psf_name = f"{out_name}.psf.png"
            out_csv_name = f"{out_name}.psf.csv"

            if args.evaluate is True:
                out_Delta_name = f"{out_name}.delta{ext}"
                png_Delta_name = f"{out_name}.delta.png"
                out_R_name = f"{out_name}.R{ext}"
                png_R_name = f"{out_name}.R.png"
                out_ssim_name = f"{out_name}.ssim{ext}"
                png_ssim_name = f"{out_name}.ssim.png"
                out_ssimre_name = f"{out_name}.ssim_re{ext}"
                png_ssimre_name = f"{out_name}.ssim_re.png"
                
                (Delta, R, rms_R, vol_gain,
                ssim_all, ssim_masked, ssim_map,
                ssim_re_masked, ssim_re_map, psnr_fg_masked,
                psnr_re_masked) = difference_and_residual_with_metrics( img, res, psf, dx, dy, 
                                                                        data_range=None, match_for_display=True,
                                                                        snr_db=current_snr, debug_pred=True, 
                                                                        out_log=out_log )
                
                print(f"rms_R: {rms_R:{csvp}}", file=out_log)
                print(f"vol_gain: {vol_gain:{csvp}}", file=out_log)
                print(f"SSIM(Fhat, G)  : masked={ssim_masked:{csvp}} all={ssim_all:{csvp}}", file=out_log)
                print(f"SSIM(G, reblur): masked={ssim_re_masked:{csvp}}", file=out_log)
                print(f"PSNR(Fhat, G)  : {psnr_fg_masked:{csvp}}", file=out_log)
                print(f"PSNR(G, reblur): {psnr_re_masked:{csvp}}", file=out_log)

            else:
                pass
            
            if args.transpose is True:
                with open(out_csv_name, 'w', newline="") as csvfile:
                    writer = csv.writer(csvfile, lineterminator="\n")
                    # Common part of header and row
                    header = ["id","image","start","stop",f"t ({unit})",
                              "x (pix)","y (pix)","d (pix)","d_psf (pix)",
                              f"ang (\N{DEGREE SIGN})","snr (dB)",
                              "edge_dx (pix)","edge_dy (pix)"]
                    
                    row = [in_name, utc0, utc1, utc2, format(value, csvp), 
                           format(shift_x, csvp), format(shift_y, csvp), format(current_d, csvp), int(np.round(current_d)), 
                           format(current_angle_deg, csvp), format(current_snr, csvp),
                           format(dx, csvp), format(dy, csvp)]

                    if args.gauss is True:
                        header += ["gwidth (pix)", "gsigma"]
                        row += [current_gwidth, format(current_gsigma, csvp)]
                    else:
                        pass
                    
                    if args.evaluate is True:
                        header += ["rms_R","vol_gain",
                                   "SSIM(Fhat, G)_all","SSIM(Fhat, G)_masked",
                                   "SSIM(G, reblur)_masked","PSNR(Fhat, G)","PSNR(G, reblur)"]
                        row += [format(rms_R, csvp), format(vol_gain, csvp),
                                format(ssim_all, csvp), format(ssim_masked, csvp),
                                format(ssim_re_masked, csvp), format(psnr_fg_masked, csvp), format(psnr_re_masked, csvp)]
                    else:
                        pass
                    
                    # Write everything
                    writer.writerow(header)
                    writer.writerow(row)
            else:
                with open(out_csv_name, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile, lineterminator="\n")
                    writer.writerow(["id",in_name])
                    writer.writerow(["start",utc1])
                    writer.writerow([" stop",utc2])
                    writer.writerow(["image",utc0])
                    writer.writerow([f"t ({unit})",format(value, csvp)])
                    writer.writerow(["x (pix)",format(shift_x, csvp)])
                    writer.writerow(["y (pix)",format(shift_y, csvp)])
                    writer.writerow(["d (pix)",format(current_d, csvp)])
                    writer.writerow(["d_psf (pix)",int(np.round(current_d))])
                    writer.writerow([f"ang (\N{DEGREE SIGN})",format(current_angle_deg, csvp)])
                    writer.writerow(["snr (dB)",format(current_snr, csvp)])
                    writer.writerow(["edge_dx (pix)",format(dx, csvp)])
                    writer.writerow(["edge_dy (pix)",format(dy, csvp)])

                    if args.gauss is True:
                        writer.writerow(["gwidth (pix)",current_gwidth])
                        writer.writerow(["gsigma",format(current_gsigma, csvp)])
                    else:
                        pass
                    
                    if args.evaluate is True:
                        writer.writerow(["rms_R",format(rms_R, csvp)])
                        writer.writerow(["vol_gain",format(vol_gain, csvp)])
                        writer.writerow(["SSIM(Fhat, G)_all",format(ssim_all, csvp)])
                        writer.writerow(["SSIM(Fhat, G)_masked",format(ssim_masked, csvp)])
                        writer.writerow(["SSIM(G, reblur)_masked",format(ssim_re_masked, csvp)])
                        writer.writerow(["PSNR(Fhat, G)",format(psnr_fg_masked, csvp)])
                        writer.writerow(["PSNR(G, reblur)",format(psnr_re_masked, csvp)])
                    else:
                        pass
            
            print("=" * terminal_width, file=out_log)
            cv.imwrite(png_inp_name, png_inp)
            print(f"Output: {png_inp_name}", file=out_log)
            export_isis_cube(out_tap_name, img, cub, out_log)
            cv.imwrite(png_tap_name, png_tap)
            print(f"Output: {png_tap_name}", file=out_log)
            print(f"Output: {out_csv_name}", file=out_log)
            export_isis_cube(out_psf_name, psf, None, out_log)
            cv.imwrite(png_psf_name, png_psf)
            print(f"Output: {png_psf_name}", file=out_log)
            export_isis_cube(out_dbl_name, res, cub, out_log)
            cv.imwrite(png_dbl_name, png_dbl)
            print(f"Output: {png_dbl_name}", file=out_log)
            
            if args.evaluate is True:
                export_isis_cube(out_Delta_name, Delta, cub, out_log)
                export_isis_cube(out_R_name, R, cub, out_log)
                export_isis_cube(out_ssim_name, ssim_map, cub, out_log)
                export_isis_cube(out_ssimre_name, ssim_re_map, cub, out_log)
                png_Delta  = to_u8_minmax(Delta)
                png_R      = to_u8_minmax(R)
                png_ssim   = to_u8_minmax(ssim_map)
                png_ssimre = to_u8_minmax(ssim_re_map)
                cv.imwrite(png_Delta_name, png_Delta)
                print(f"Output: {png_Delta_name}", file=out_log)
                cv.imwrite(png_R_name, png_R)
                print(f"Output: {png_R_name}", file=out_log)
                cv.imwrite(png_ssim_name, png_ssim)
                print(f"Output: {png_ssim_name}", file=out_log)
                cv.imwrite(png_ssimre_name, png_ssimre)
                print(f"Output: {png_ssimre_name}", file=out_log)
            else:
                pass
            
            if args.log is True:
                print(f"Output: {log_name}", file=out_log)
            else:
                pass
        
        if args.save:
            save()
        elif args.save_exit:
            save()
            os._exit(0)

    while True:
        update(None)
        ch = cv.waitKey(50)
        try:
            if (cv.getWindowProperty('input', cv.WND_PROP_VISIBLE) < 1 or
                cv.getWindowProperty(deconv_win, cv.WND_PROP_VISIBLE) < 1 or
                cv.getWindowProperty('psf', cv.WND_PROP_VISIBLE) < 1):
                break
        except cv.error:
            break
        if ch == 27:
            break
        if ch == ord(' '):
            defocus_flag = not defocus_flag
            update(None)

    print("Done", file=out_log)
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
    cv.destroyAllWindows()
