#!/usr/bin/env python3
"""
phobos_slope_analysis.py

Complete analysis pipeline for the Phobos gravity-referenced slope study.

The script is designed for the current v004 dataset:

  GPKG sequence
    v004gpkg/v004_18_surface_TA00.gpkg       native, unsmoothed reference
    v004gpkg/v004_<L>_surface_TA00.gpkg      smoothed models

  OBJ sequence
    phobos_g_018m_spc_obj_0000n00000_v004.obj
    phobos_g_018m_spc_obj_0000n00000_v004_diffuse_efold_<L>_preserve.obj

where L = 80, 100, 125, 150, 175, 200, 250, 500, 1000, 2000 m.

Analyses produced
-----------------
1. Global area-weighted slope-frequency distributions:
       mean, standard deviation, p50, p75, p90, p95
       differential histogram and CDF for every L

2. Direct effective-gravity response relative to the native model:
       Delta g_i(L) = angular change of g direction
       |delta g_i(L)| = absolute relative change of |g| in percent
       area-weighted median and p95 (plus mean/std/max diagnostics)

3. Direct surface-normal response from corresponding OBJ facets:
       Delta n_i(L) = angular change of facet-normal direction
       area-weighted median and p95 (plus mean/std/max diagnostics)

4. Four representative 2 deg x 2 deg equatorial regions:
       Leading   : 1 S-1 N, 91-89 W
       Sub-Mars  : 1 S-1 N, 1 W-1 E
       Trailing  : 1 S-1 N, 89-91 E
       Anti-Mars : 1 S-1 N, 179 E-179 W
   For every L:
       theta_mean, theta_std, theta_p95
       psi_mean, R, sigma_psi
       area-weighted slope histograms

5. Fixed global latitude-longitude sampling grids at one or more window
   sizes W supplied with --grid-sizes-deg. For every (L, W):
       theta_mean, theta_std, theta_p95
       psi_mean, R, sigma_psi
   Grid membership is defined from native-model facet centroids and held
   fixed while L is varied.

6. Window-size sensitivity summary across grid cells:
       area-weighted cell-level quantiles of R, sigma_psi, theta_std,
       and theta_p95 for every (L, W).

Critical methodological choices
--------------------------------
* The L=18 GPKG/OBJ is the unsmoothed native reference. It is not a smoothed
  L=18 product.

* Cross-scale feature matching is by facet_id / preserved face order, never by
  point spacing, nearest-neighbor matching, or smoothed centroid coordinates.

* Fixed regional/grid membership is assigned from native-model facet
  centroids and reused for every smoothing level. For each requested grid
  size W, W is therefore held fixed while L is varied. Supplying multiple W
  values performs an explicit window-size sensitivity analysis.

* Slope, ROI, and gridded statistics use the facet area of the corresponding
  scale model by default (--regional-weight current). This preserves the
  manuscript's area-weighted surface statistics. The option
  --regional-weight native is provided as a sensitivity check.

* Paired Delta n / Delta g / |delta g| statistics use native-model facet areas
  by default (--vector-weight native), so the weights themselves do not change
  when evaluating vector response.

* Global/ROI percentiles use a fine weighted histogram (default 0.001 deg).
  Gridded theta_p95 uses a coarser histogram (default 0.1 deg) to keep memory
  practical when multiple W values are accumulated in the same GPKG pass.
  The gridded bin width is recorded in the output manifest.

Outputs
-------
global_slope_summary.csv
global_slope_histograms.csv
vector_response_summary.csv
roi_scale_response.csv
roi_slope_histograms.csv
grid_scale_response.csv
grid_window_summary.csv
analysis_manifest.json

Optional preview plots:
global_slope_distributions.png
vector_direction_response.png
gravity_magnitude_response.png
roi_theta95_response.png
roi_directional_coherence.png
grid_window_R_sensitivity.png
grid_window_sigma_psi_sensitivity.png

Dependencies
------------
Required:
    Python 3
    NumPy

Optional:
    Matplotlib  (only for --plots)

The GeoPackages are read directly with Python sqlite3. GDAL/OGR, GeoPandas,
pandas, scipy, and trimesh are not required.

Example
-------
python -u phobos_slope_analysis.py \
    --gpkg-dir v004gpkg \
    --native-scale 18 \
    --native-obj phobos_g_018m_spc_obj_0000n00000_v004.obj \
    --obj-pattern 'phobos_g_018m_spc_obj_0000n00000_v004_diffuse_efold_{L}_preserve.obj' \
    --output-dir slope_analysis \
    --grid-sizes-deg 1 2 4 8 \
    --plots
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

import numpy as np


REQUIRED_FIELDS = (
    "facet_id",
    "lat_deg",
    "lon_deg",
    "dynamic_slope_deg",
    "dynamic_slope_azimuth_deg",
    "facet_area",
    "g_total_x_m_s2",
    "g_total_y_m_s2",
    "g_total_z_m_s2",
    "g_total_mag_m_s2",
)

ROI_NAMES = ("Leading", "Sub-Mars", "Trailing", "Anti-Mars")
N_ROI = 4



@dataclass
class GpkgInfo:
    path: Path
    layer: str
    feature_count: int
    columns: Tuple[str, ...]


@dataclass
class WeightedMoments:
    sum_w: float = 0.0
    sum_wx: float = 0.0
    sum_wx2: float = 0.0
    min_x: float = math.inf
    max_x: float = -math.inf
    n_valid: int = 0

    def update(self, x: np.ndarray, w: np.ndarray) -> None:
        good = np.isfinite(x) & np.isfinite(w) & (w > 0.0)
        if not np.any(good):
            return
        xv = x[good].astype(np.float64, copy=False)
        wv = w[good].astype(np.float64, copy=False)
        self.sum_w += float(np.sum(wv))
        self.sum_wx += float(np.dot(wv, xv))
        self.sum_wx2 += float(np.dot(wv, xv * xv))
        self.min_x = min(self.min_x, float(np.min(xv)))
        self.max_x = max(self.max_x, float(np.max(xv)))
        self.n_valid += int(xv.size)

    @property
    def mean(self) -> float:
        return self.sum_wx / self.sum_w if self.sum_w > 0.0 else float("nan")

    @property
    def std(self) -> float:
        if self.sum_w <= 0.0:
            return float("nan")
        var = self.sum_wx2 / self.sum_w - self.mean * self.mean
        return math.sqrt(max(0.0, var))


class UniformWeightedHistogram:
    """Weighted histogram with uniform bin spacing."""

    def __init__(self, lo: float, hi: float, width: float) -> None:
        if not (math.isfinite(lo) and math.isfinite(hi) and math.isfinite(width)):
            raise ValueError("Histogram parameters must be finite.")
        if hi <= lo or width <= 0.0:
            raise ValueError("Invalid histogram limits or width.")
        self.lo = float(lo)
        self.width = float(width)
        self.n = int(math.ceil((hi - lo) / width))
        self.hi = self.lo + self.n * self.width
        self.counts = np.zeros(self.n, dtype=np.float64)
        self.underflow_weight = 0.0
        self.overflow_weight = 0.0

    def update(self, x: np.ndarray, w: np.ndarray) -> None:
        good = np.isfinite(x) & np.isfinite(w) & (w > 0.0)
        if not np.any(good):
            return
        xv = x[good].astype(np.float64, copy=False)
        wv = w[good].astype(np.float64, copy=False)

        under = xv < self.lo
        over = xv > self.hi
        if np.any(under):
            self.underflow_weight += float(np.sum(wv[under]))
        if np.any(over):
            self.overflow_weight += float(np.sum(wv[over]))

        inside = (~under) & (~over)
        if not np.any(inside):
            return

        xv = xv[inside]
        wv = wv[inside]
        idx = np.floor((xv - self.lo) / self.width).astype(np.int64)
        idx = np.clip(idx, 0, self.n - 1)
        self.counts += np.bincount(
            idx, weights=wv, minlength=self.n
        )[: self.n]

    def quantile(self, q: float) -> float:
        if not 0.0 <= q <= 1.0:
            raise ValueError("q must be within [0, 1].")
        total = float(np.sum(self.counts))
        if total <= 0.0:
            return float("nan")

        target = q * total
        cum = np.cumsum(self.counts)
        i = int(np.searchsorted(cum, target, side="left"))
        i = min(max(i, 0), self.n - 1)

        prev = 0.0 if i == 0 else float(cum[i - 1])
        bw = float(self.counts[i])
        left = self.lo + i * self.width
        if bw <= 0.0:
            return left + 0.5 * self.width

        frac = (target - prev) / bw
        frac = min(max(frac, 0.0), 1.0)
        return left + frac * self.width

    def edges(self) -> np.ndarray:
        return self.lo + np.arange(self.n + 1, dtype=np.float64) * self.width

    def centers(self) -> np.ndarray:
        return self.lo + (np.arange(self.n, dtype=np.float64) + 0.5) * self.width


@dataclass
class CircularAccumulator:
    sum_w: float = 0.0
    sum_w_cos: float = 0.0
    sum_w_sin: float = 0.0
    n_valid: int = 0

    def update(self, az_deg: np.ndarray, w: np.ndarray) -> None:
        good = np.isfinite(az_deg) & np.isfinite(w) & (w > 0.0)
        if not np.any(good):
            return
        a = np.deg2rad(az_deg[good].astype(np.float64, copy=False))
        wv = w[good].astype(np.float64, copy=False)
        self.sum_w += float(np.sum(wv))
        self.sum_w_cos += float(np.dot(wv, np.cos(a)))
        self.sum_w_sin += float(np.dot(wv, np.sin(a)))
        self.n_valid += int(a.size)

    def summary(self) -> Tuple[float, float, float]:
        if self.sum_w <= 0.0:
            return float("nan"), float("nan"), float("nan")

        r = math.hypot(self.sum_w_cos, self.sum_w_sin) / self.sum_w
        r = min(max(r, 0.0), 1.0)

        psi = math.degrees(math.atan2(self.sum_w_sin, self.sum_w_cos))
        if psi < 0.0:
            psi += 360.0

        if r <= 0.0:
            sigma = float("inf")
        else:
            sigma = math.degrees(math.sqrt(max(0.0, -2.0 * math.log(r))))

        return psi, r, sigma


class GridAccumulator:
    """
    Exact weighted mean/std/circular statistics plus histogram-based theta_p95
    for one fixed latitude-longitude grid window size W.

    Grid edges are anchored at -90 deg latitude and -180 deg longitude.
    Arbitrary positive W values are accepted. If W does not divide 180 or 360
    exactly, the final latitude/longitude band is narrower than W; the actual
    cell bounds are written to the output CSV.
    """

    def __init__(self, window_deg: float, p95_bin_width_deg: float) -> None:
        if not math.isfinite(window_deg) or window_deg <= 0.0 or window_deg > 180.0:
            raise ValueError("Grid window size W must be within (0, 180] deg.")
        self.W = float(window_deg)
        self.n_lat = int(math.ceil(180.0 / self.W))
        self.n_lon = int(math.ceil(360.0 / self.W))
        self.n_grid = self.n_lat * self.n_lon

        self.n = np.zeros(self.n_grid, dtype=np.int64)
        self.sum_w = np.zeros(self.n_grid, dtype=np.float64)
        self.sum_wx = np.zeros(self.n_grid, dtype=np.float64)
        self.sum_wx2 = np.zeros(self.n_grid, dtype=np.float64)
        self.sum_w_az = np.zeros(self.n_grid, dtype=np.float64)
        self.sum_w_cos = np.zeros(self.n_grid, dtype=np.float64)
        self.sum_w_sin = np.zeros(self.n_grid, dtype=np.float64)

        self.p95_width = float(p95_bin_width_deg)
        self.p95_nbin = int(math.ceil(90.0 / self.p95_width))
        # float32 is adequate because this histogram only locates a percentile
        # within p95_width; exact weighted means/std/circular sums remain float64.
        self.p95_hist = np.zeros(
            (self.n_grid, self.p95_nbin), dtype=np.float32
        )

    def cell_ids(self, lat_deg: np.ndarray, lon_deg: np.ndarray) -> np.ndarray:
        lon = ((lon_deg + 180.0) % 360.0) - 180.0
        ilat = np.floor((lat_deg + 90.0) / self.W).astype(np.int64)
        ilon = np.floor((lon + 180.0) / self.W).astype(np.int64)
        ilat = np.clip(ilat, 0, self.n_lat - 1)
        ilon = np.clip(ilon, 0, self.n_lon - 1)
        return ilat * self.n_lon + ilon

    def update_from_latlon(
        self,
        lat_deg: np.ndarray,
        lon_deg: np.ndarray,
        slope_deg: np.ndarray,
        az_deg: np.ndarray,
        w: np.ndarray,
    ) -> None:
        self.update(self.cell_ids(lat_deg, lon_deg), slope_deg, az_deg, w)

    def update(
        self,
        cell: np.ndarray,
        slope_deg: np.ndarray,
        az_deg: np.ndarray,
        w: np.ndarray,
    ) -> None:
        good = (
            (cell >= 0)
            & (cell < self.n_grid)
            & np.isfinite(slope_deg)
            & np.isfinite(w)
            & (w > 0.0)
        )
        if not np.any(good):
            return

        c = cell[good].astype(np.int64, copy=False)
        s = slope_deg[good].astype(np.float64, copy=False)
        ww = w[good].astype(np.float64, copy=False)

        self.n += np.bincount(c, minlength=self.n_grid)
        self.sum_w += np.bincount(c, weights=ww, minlength=self.n_grid)
        self.sum_wx += np.bincount(c, weights=ww * s, minlength=self.n_grid)
        self.sum_wx2 += np.bincount(c, weights=ww * s * s, minlength=self.n_grid)

        sb = np.floor(s / self.p95_width).astype(np.int64)
        sb = np.clip(sb, 0, self.p95_nbin - 1)
        flat = c * self.p95_nbin + sb
        add = np.bincount(
            flat,
            weights=ww,
            minlength=self.n_grid * self.p95_nbin,
        ).reshape(self.n_grid, self.p95_nbin)
        self.p95_hist += add.astype(np.float32, copy=False)

        good_az = np.isfinite(az_deg[good])
        if np.any(good_az):
            ca = c[good_az]
            wa = ww[good_az]
            ar = np.deg2rad(az_deg[good][good_az].astype(np.float64, copy=False))
            self.sum_w_az += np.bincount(ca, weights=wa, minlength=self.n_grid)
            self.sum_w_cos += np.bincount(
                ca, weights=wa * np.cos(ar), minlength=self.n_grid
            )
            self.sum_w_sin += np.bincount(
                ca, weights=wa * np.sin(ar), minlength=self.n_grid
            )

    def rows(self, L: float) -> List[Dict[str, object]]:
        out: List[Dict[str, object]] = []

        for cell in range(self.n_grid):
            sw = float(self.sum_w[cell])
            if sw <= 0.0:
                continue

            ilat = cell // self.n_lon
            ilon = cell % self.n_lon
            lat_min = -90.0 + self.W * ilat
            lat_max = min(90.0, lat_min + self.W)
            lon_min = -180.0 + self.W * ilon
            lon_max = min(180.0, lon_min + self.W)

            mean = self.sum_wx[cell] / sw
            var = self.sum_wx2[cell] / sw - mean * mean
            std = math.sqrt(max(0.0, var))

            rowhist = self.p95_hist[cell].astype(np.float64, copy=False)
            total_hist = float(np.sum(rowhist))
            if total_hist > 0.0:
                target = 0.95 * total_hist
                cum = np.cumsum(rowhist)
                bi = int(np.searchsorted(cum, target, side="left"))
                bi = min(max(bi, 0), self.p95_nbin - 1)
                prev = 0.0 if bi == 0 else float(cum[bi - 1])
                bw = float(rowhist[bi])
                left = bi * self.p95_width
                if bw > 0.0:
                    frac = min(max((target - prev) / bw, 0.0), 1.0)
                    p95 = left + frac * self.p95_width
                else:
                    p95 = left + 0.5 * self.p95_width
            else:
                p95 = float("nan")

            az_sw = float(self.sum_w_az[cell])
            csum = float(self.sum_w_cos[cell])
            ssum = float(self.sum_w_sin[cell])
            if az_sw > 0.0:
                R = min(max(math.hypot(csum, ssum) / az_sw, 0.0), 1.0)
                psi = math.degrees(math.atan2(ssum, csum))
                if psi < 0.0:
                    psi += 360.0
                sigma_psi = (
                    float("inf")
                    if R <= 0.0
                    else math.degrees(math.sqrt(max(0.0, -2.0 * math.log(R))))
                )
            else:
                R = float("nan")
                psi = float("nan")
                sigma_psi = float("nan")

            out.append(
                {
                    "L_m": L,
                    "W_deg": self.W,
                    "cell_id": cell,
                    "lat_min_deg": lat_min,
                    "lat_max_deg": lat_max,
                    "lat_center_deg": 0.5 * (lat_min + lat_max),
                    "lon_min_deg": lon_min,
                    "lon_max_deg": lon_max,
                    "lon_center_deg": 0.5 * (lon_min + lon_max),
                    "facet_count": int(self.n[cell]),
                    "area_weight_sum": sw,
                    "theta_mean_deg": mean,
                    "theta_std_deg": std,
                    "theta_p95_deg": p95,
                    "psi_mean_deg": psi,
                    "R": R,
                    "sigma_psi_deg": sigma_psi,
                }
            )

        return out


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "Complete scale-response analysis for the Phobos v004 "
            "gravity-referenced slope study."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    ap.add_argument(
        "--gpkg-dir",
        type=Path,
        default=Path("v004gpkg"),
        help="Directory containing v004_<L>_surface_TA00.gpkg files.",
    )
    ap.add_argument(
        "--gpkg-regex",
        default=r"^v004_(\d+(?:\.\d+)?)_surface_TA00\.gpkg$",
        help="Regex extracting L from GPKG basename; capture group 1 is L.",
    )
    ap.add_argument(
        "--native-scale",
        type=float,
        default=18.0,
        help="Scale label of the native unsmoothed GPKG.",
    )
    ap.add_argument(
        "--scales",
        type=float,
        nargs="*",
        default=None,
        help="Optional scale subset. Native scale is always included.",
    )

    ap.add_argument(
        "--native-obj",
        type=Path,
        default=Path("phobos_g_018m_spc_obj_0000n00000_v004.obj"),
        help="Native unsmoothed OBJ.",
    )
    ap.add_argument(
        "--obj-pattern",
        default=(
            "phobos_g_018m_spc_obj_0000n00000_v004_"
            "diffuse_efold_{L}_preserve.obj"
        ),
        help="Smoothed OBJ pattern containing {L}.",
    )
    ap.add_argument(
        "--skip-normal",
        action="store_true",
        help="Skip OBJ surface-normal comparison.",
    )

    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("slope_analysis"),
        help="Output directory.",
    )
    ap.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Native fixed-support cache. Default: <output-dir>/_native_cache.",
    )
    ap.add_argument(
        "--rebuild-cache",
        action="store_true",
        help="Force recreation of native cache.",
    )

    ap.add_argument(
        "--chunk-size",
        type=int,
        default=200_000,
        help="Number of GPKG rows processed per chunk.",
    )
    ap.add_argument(
        "--obj-normal-chunk-size",
        type=int,
        default=500_000,
        help="Number of OBJ facets processed per normal-comparison chunk.",
    )

    ap.add_argument(
        "--regional-weight",
        choices=("current", "native"),
        default="current",
        help="Area weighting for global slope, ROI, and fixed-grid statistics.",
    )
    ap.add_argument(
        "--vector-weight",
        choices=("native", "current"),
        default="native",
        help="Area weighting for Delta n / Delta g / |delta g|.",
    )

    ap.add_argument(
        "--global-hist-bin-width-deg",
        type=float,
        default=0.5,
        help="Output bin width for global slope distributions.",
    )
    ap.add_argument(
        "--roi-hist-bin-width-deg",
        type=float,
        default=0.5,
        help="Output bin width for ROI slope distributions.",
    )
    ap.add_argument(
        "--fine-quantile-bin-width-deg",
        type=float,
        default=0.001,
        help="Fine histogram width for global/ROI/vector percentiles.",
    )
    ap.add_argument(
        "--grid-sizes-deg",
        type=float,
        nargs="+",
        default=[2.0],
        help=(
            "One or more fixed latitude-longitude window sizes W in degrees. "
            "Example: --grid-sizes-deg 1 2 4 8. Each W is assigned from "
            "native-model facet centroids and held fixed while L is varied."
        ),
    )
    ap.add_argument(
        "--grid-quantile-bin-width-deg",
        type=float,
        default=0.1,
        help="Histogram width used for fixed-grid theta_p95.",
    )
    ap.add_argument(
        "--gravity-mag-bin-width-pct",
        type=float,
        default=0.001,
        help="Fine histogram width for |delta g| percentiles.",
    )
    ap.add_argument(
        "--gravity-mag-max-pct",
        type=float,
        default=100.0,
        help="Upper |delta g| histogram bound in percent.",
    )

    ap.add_argument(
        "--skip-grid",
        action="store_true",
        help="Skip global fixed-grid aggregation and W-sensitivity outputs.",
    )
    ap.add_argument(
        "--plots",
        action="store_true",
        help="Write preview plots if matplotlib is installed.",
    )
    ap.add_argument(
        "--plots-only",
        action="store_true",
        help=(
            "Read the existing CSV outputs in --output-dir and regenerate only "
            "the PNG plots. No GPKG or OBJ files are read and no analysis is rerun."
        ),
    )

    return ap.parse_args()


def fmt_scale(L: float) -> str:
    if abs(L - round(L)) < 1.0e-10:
        return str(int(round(L)))
    return f"{L:g}"


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def sqlite_ro(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    con.execute("PRAGMA temp_store=MEMORY")
    try:
        con.execute("PRAGMA mmap_size=1073741824")
    except sqlite3.DatabaseError:
        pass
    return con


def discover_gpkgs(directory: Path, regex: str) -> Dict[float, Path]:
    if not directory.is_dir():
        raise FileNotFoundError(f"GPKG directory not found: {directory}")
    rx = re.compile(regex)
    out: Dict[float, Path] = {}
    for p in sorted(directory.glob("*.gpkg")):
        m = rx.match(p.name)
        if not m:
            continue
        L = float(m.group(1))
        if L in out:
            raise ValueError(f"Duplicate GPKG scale L={L:g}")
        out[L] = p
    if not out:
        raise FileNotFoundError(
            f"No GPKGs matching {regex!r} in {directory}"
        )
    return out


def fast_feature_count(con: sqlite3.Connection, layer: str) -> int:
    # GDAL-created GPKGs often maintain this table.
    try:
        row = con.execute(
            "SELECT feature_count FROM gpkg_ogr_contents "
            "WHERE table_name=?",
            (layer,),
        ).fetchone()
        if row is not None and row[0] is not None:
            return int(row[0])
    except sqlite3.DatabaseError:
        pass

    # Fallback.
    return int(
        con.execute(
            f"SELECT COUNT(*) FROM {quote_ident(layer)}"
        ).fetchone()[0]
    )


def inspect_gpkg(path: Path) -> GpkgInfo:
    con = sqlite_ro(path)
    try:
        layers = con.execute(
            "SELECT table_name FROM gpkg_contents WHERE data_type='features'"
        ).fetchall()
        if len(layers) != 1:
            raise ValueError(
                f"{path}: expected one feature layer, found {layers}"
            )
        layer = str(layers[0][0])
        cols = tuple(
            str(r[1])
            for r in con.execute(
                f"PRAGMA table_info({quote_ident(layer)})"
            )
        )
        missing = [x for x in REQUIRED_FIELDS if x not in cols]
        if missing:
            raise ValueError(f"{path}: missing fields: {missing}")
        n = fast_feature_count(con, layer)
        return GpkgInfo(path=path, layer=layer, feature_count=n, columns=cols)
    finally:
        con.close()


def iter_gpkg_chunks(
    info: GpkgInfo,
    fields: Sequence[str],
    chunk_size: int,
) -> Iterator[np.ndarray]:
    select = ", ".join(quote_ident(x) for x in fields)
    sql = (
        f"SELECT {select} FROM {quote_ident(info.layer)} ORDER BY fid"
    )

    con = sqlite_ro(info.path)
    try:
        cur = con.execute(sql)
        while True:
            rows = cur.fetchmany(chunk_size)
            if not rows:
                break
            yield np.asarray(rows, dtype=np.float64)
    finally:
        con.close()


def facet_ids_to_int(values: np.ndarray) -> np.ndarray:
    ids = np.rint(values).astype(np.int64)
    if not np.allclose(values, ids, rtol=0.0, atol=1.0e-8):
        raise ValueError("facet_id contains non-integer values.")
    return ids


def native_roi_code(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """
    Return -1 for no ROI or 0..3 corresponding to ROI_NAMES.
    ROI membership is defined from native facet centroids and remains 2 deg
    x 2 deg; --grid-sizes-deg applies to the global fixed-grid analysis.
    """
    lon2 = ((lon + 180.0) % 360.0) - 180.0
    out = np.full(lat.shape, -1, dtype=np.int8)
    eq = (lat >= -1.0) & (lat <= 1.0)
    out[eq & (lon2 >= -91.0) & (lon2 <= -89.0)] = 0
    out[eq & (lon2 >= -1.0) & (lon2 <= 1.0)] = 1
    out[eq & (lon2 >= 89.0) & (lon2 <= 91.0)] = 2
    out[eq & ((lon2 >= 179.0) | (lon2 <= -179.0))] = 3
    return out


def normalize_grid_sizes(values: Sequence[float]) -> List[float]:
    out: List[float] = []
    for value in values:
        W = float(value)
        if not math.isfinite(W) or W <= 0.0 or W > 180.0:
            raise ValueError(f"Invalid grid size W={value!r}; require 0 < W <= 180 deg.")
        if not any(abs(W - x) < 1.0e-12 for x in out):
            out.append(W)
    return sorted(out)


def new_grid_accumulators(args: argparse.Namespace) -> Dict[float, GridAccumulator]:
    if args.skip_grid:
        return {}
    return {
        W: GridAccumulator(W, args.grid_quantile_bin_width_deg)
        for W in args.grid_sizes_deg
    }


def cache_paths(cache_dir: Path) -> Dict[str, Path]:
    return {
        "meta": cache_dir / "meta.json",
        "area": cache_dir / "native_area.float64.dat",
        "gravity": cache_dir / "native_gravity.float64.dat",
        "lat": cache_dir / "native_lat.float32.dat",
        "lon": cache_dir / "native_lon.float32.dat",
    }


def cache_valid(
    paths: Dict[str, Path],
    native_info: GpkgInfo,
) -> bool:
    if not all(p.exists() for p in paths.values()):
        return False
    try:
        meta = json.loads(paths["meta"].read_text(encoding="utf-8"))
    except Exception:
        return False

    st = native_info.path.stat()
    return (
        meta.get("cache_schema") == "native-area-gravity-latlon-v2"
        and meta.get("source") == str(native_info.path.resolve())
        and int(meta.get("feature_count", -1)) == native_info.feature_count
        and int(meta.get("source_size", -1)) == st.st_size
        and int(meta.get("source_mtime_ns", -1)) == st.st_mtime_ns
    )


def open_native_cache(
    paths: Dict[str, Path],
    n: int,
    mode: str,
) -> Tuple[np.memmap, np.memmap, np.memmap, np.memmap]:
    area = np.memmap(paths["area"], mode=mode, dtype=np.float64, shape=(n,))
    gravity = np.memmap(paths["gravity"], mode=mode, dtype=np.float64, shape=(n, 3))
    lat = np.memmap(paths["lat"], mode=mode, dtype=np.float32, shape=(n,))
    lon = np.memmap(paths["lon"], mode=mode, dtype=np.float32, shape=(n,))
    return area, gravity, lat, lon


def new_global_slope_accumulators(
    args: argparse.Namespace,
) -> Tuple[WeightedMoments, UniformWeightedHistogram, UniformWeightedHistogram]:
    return (
        WeightedMoments(),
        UniformWeightedHistogram(
            0.0, 90.0, args.global_hist_bin_width_deg
        ),
        UniformWeightedHistogram(
            0.0, 90.0, args.fine_quantile_bin_width_deg
        ),
    )


def new_roi_accumulators(
    args: argparse.Namespace,
):
    moments = [WeightedMoments() for _ in range(N_ROI)]
    circular = [CircularAccumulator() for _ in range(N_ROI)]
    fine = [
        UniformWeightedHistogram(
            0.0, 90.0, args.fine_quantile_bin_width_deg
        )
        for _ in range(N_ROI)
    ]
    output_hist = [
        UniformWeightedHistogram(
            0.0, 90.0, args.roi_hist_bin_width_deg
        )
        for _ in range(N_ROI)
    ]
    return moments, circular, fine, output_hist


def update_roi_accumulators(
    roi_code: np.ndarray,
    slope: np.ndarray,
    azimuth: np.ndarray,
    weights: np.ndarray,
    moments,
    circular,
    fine,
    output_hist,
) -> None:
    for rid in range(N_ROI):
        mask = roi_code == rid
        if not np.any(mask):
            continue
        moments[rid].update(slope[mask], weights[mask])
        circular[rid].update(azimuth[mask], weights[mask])
        fine[rid].update(slope[mask], weights[mask])
        output_hist[rid].update(slope[mask], weights[mask])


def summarize_global_slope(
    L: float,
    weighting: str,
    moments: WeightedMoments,
    fine: UniformWeightedHistogram,
) -> Dict[str, object]:
    return {
        "L_m": L,
        "weighting": weighting,
        "facet_count_valid": moments.n_valid,
        "area_weight_sum": moments.sum_w,
        "theta_mean_deg": moments.mean,
        "theta_std_deg": moments.std,
        "theta_p50_deg": fine.quantile(0.50),
        "theta_p75_deg": fine.quantile(0.75),
        "theta_p90_deg": fine.quantile(0.90),
        "theta_p95_deg": fine.quantile(0.95),
        "theta_min_deg": moments.min_x,
        "theta_max_deg": moments.max_x,
    }


def summarize_rois(
    L: float,
    weighting: str,
    moments,
    circular,
    fine,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []

    for rid, name in enumerate(ROI_NAMES):
        psi, R, sigma = circular[rid].summary()
        m = moments[rid]
        rows.append(
            {
                "L_m": L,
                "region": name,
                "weighting": weighting,
                "facet_count_valid": m.n_valid,
                "area_weight_sum": m.sum_w,
                "theta_mean_deg": m.mean,
                "theta_std_deg": m.std,
                "theta_p50_deg": fine[rid].quantile(0.50),
                "theta_p95_deg": fine[rid].quantile(0.95),
                "psi_mean_deg": psi,
                "R": R,
                "sigma_psi_deg": sigma,
            }
        )

    return rows


def build_native_cache_and_native_stats(
    args: argparse.Namespace,
    native_info: GpkgInfo,
):
    cache_dir = args.cache_dir or (args.output_dir / "_native_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    paths = cache_paths(cache_dir)
    n = native_info.feature_count

    global_m, global_out_hist, global_fine = new_global_slope_accumulators(args)
    roi_m, roi_c, roi_fine, roi_out_hist = new_roi_accumulators(args)
    grid_accs = new_grid_accumulators(args)

    if not args.rebuild_cache and cache_valid(paths, native_info):
        print(f"[INFO] Reusing native cache: {cache_dir}", flush=True)
        area, gravity, native_lat, native_lon = open_native_cache(paths, n, "r")
        meta = json.loads(paths["meta"].read_text(encoding="utf-8"))
        facet_id_base = int(meta["facet_id_base"])

        fields = (
            "facet_id",
            "dynamic_slope_deg",
            "dynamic_slope_azimuth_deg",
            "facet_area",
        )
        start = 0
        for arr in iter_gpkg_chunks(native_info, fields, args.chunk_size):
            k = arr.shape[0]
            ids = facet_ids_to_int(arr[:, 0])
            expected = np.arange(start, start + k, dtype=np.int64) + facet_id_base
            if not np.array_equal(ids, expected):
                raise ValueError(f"Native facet_id mismatch at row {start:,}.")

            slope = arr[:, 1]
            az = arr[:, 2]
            current_area = arr[:, 3]
            w = current_area if args.regional_weight == "current" else np.asarray(area[start:start+k])
            lat = np.asarray(native_lat[start:start+k], dtype=np.float64)
            lon = np.asarray(native_lon[start:start+k], dtype=np.float64)

            global_m.update(slope, w)
            global_out_hist.update(slope, w)
            global_fine.update(slope, w)
            update_roi_accumulators(
                native_roi_code(lat, lon), slope, az, w,
                roi_m, roi_c, roi_fine, roi_out_hist,
            )
            for acc in grid_accs.values():
                acc.update_from_latlon(lat, lon, slope, az, w)

            start += k
            if start == n or start % (args.chunk_size * 10) == 0:
                print(f"[INFO] Native stats: {start:,}/{n:,}", flush=True)

        return (
            area, gravity, native_lat, native_lon, facet_id_base,
            summarize_global_slope(args.native_scale, args.regional_weight, global_m, global_fine),
            global_out_hist,
            summarize_rois(args.native_scale, args.regional_weight, roi_m, roi_c, roi_fine),
            roi_out_hist,
            grid_accs,
        )

    print(f"[INFO] Building native cache from {native_info.path}", flush=True)
    for key, p in paths.items():
        if key != "meta" and p.exists():
            p.unlink()
    if paths["meta"].exists():
        paths["meta"].unlink()

    area, gravity, native_lat, native_lon = open_native_cache(paths, n, "w+")
    fields = (
        "facet_id", "lat_deg", "lon_deg", "dynamic_slope_deg",
        "dynamic_slope_azimuth_deg", "facet_area",
        "g_total_x_m_s2", "g_total_y_m_s2", "g_total_z_m_s2",
    )

    start = 0
    facet_id_base: Optional[int] = None
    t0 = time.time()

    for arr in iter_gpkg_chunks(native_info, fields, args.chunk_size):
        k = arr.shape[0]
        ids = facet_ids_to_int(arr[:, 0])
        if facet_id_base is None:
            facet_id_base = int(ids[0])
        expected = np.arange(start, start + k, dtype=np.int64) + facet_id_base
        if not np.array_equal(ids, expected):
            bad = np.flatnonzero(ids != expected)
            j = int(bad[0]) if bad.size else 0
            raise ValueError(
                "Native facet_id must be contiguous and in face order. "
                f"Row {start+j:,}: got {ids[j]}, expected {expected[j]}."
            )

        lat = arr[:, 1]
        lon = arr[:, 2]
        slope = arr[:, 3]
        az = arr[:, 4]
        current_area = arr[:, 5]

        area[start:start+k] = current_area
        gravity[start:start+k, :] = arr[:, 6:9]
        native_lat[start:start+k] = lat.astype(np.float32, copy=False)
        native_lon[start:start+k] = lon.astype(np.float32, copy=False)

        w = current_area
        global_m.update(slope, w)
        global_out_hist.update(slope, w)
        global_fine.update(slope, w)
        update_roi_accumulators(
            native_roi_code(lat, lon), slope, az, w,
            roi_m, roi_c, roi_fine, roi_out_hist,
        )
        for acc in grid_accs.values():
            acc.update_from_latlon(lat, lon, slope, az, w)

        start += k
        if start == n or start % (args.chunk_size * 10) == 0:
            print(
                f"[INFO] Native cache/stats: {start:,}/{n:,} "
                f"({100.0*start/n:.1f}%)", flush=True,
            )

    if start != n:
        raise RuntimeError(f"Native row count mismatch: read {start:,}, expected {n:,}")

    area.flush(); gravity.flush(); native_lat.flush(); native_lon.flush()
    assert facet_id_base is not None
    st = native_info.path.stat()
    meta = {
        "cache_schema": "native-area-gravity-latlon-v2",
        "source": str(native_info.path.resolve()),
        "source_size": st.st_size,
        "source_mtime_ns": st.st_mtime_ns,
        "feature_count": n,
        "facet_id_base": facet_id_base,
        "support_definition": "native-model facet centroid latitude/longitude",
        "created_unix": time.time(),
    }
    tmp = paths["meta"].with_suffix(".tmp")
    tmp.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    os.replace(tmp, paths["meta"])
    print(f"[TIME] Native cache/stats: {time.time()-t0:.1f} s", flush=True)

    del area, gravity, native_lat, native_lon
    area, gravity, native_lat, native_lon = open_native_cache(paths, n, "r")

    return (
        area, gravity, native_lat, native_lon, facet_id_base,
        summarize_global_slope(args.native_scale, args.regional_weight, global_m, global_fine),
        global_out_hist,
        summarize_rois(args.native_scale, args.regional_weight, roi_m, roi_c, roi_fine),
        roi_out_hist,
        grid_accs,
    )


def analyze_smoothed_gpkg(
    args: argparse.Namespace,
    L: float,
    info: GpkgInfo,
    native_area: np.memmap,
    native_gravity: np.memmap,
    native_lat: np.memmap,
    native_lon: np.memmap,
    facet_id_base: int,
):
    n = native_area.shape[0]
    global_m, global_out_hist, global_fine = new_global_slope_accumulators(args)
    roi_m, roi_c, roi_fine, roi_out_hist = new_roi_accumulators(args)
    grid_accs = new_grid_accumulators(args)

    gdir_m = WeightedMoments()
    gdir_fine = UniformWeightedHistogram(0.0, 180.0, args.fine_quantile_bin_width_deg)
    gmag_m = WeightedMoments()
    gmag_fine = UniformWeightedHistogram(
        0.0, args.gravity_mag_max_pct, args.gravity_mag_bin_width_pct
    )

    fields = (
        "facet_id", "dynamic_slope_deg", "dynamic_slope_azimuth_deg",
        "facet_area", "g_total_x_m_s2", "g_total_y_m_s2", "g_total_z_m_s2",
    )
    start = 0
    t0 = time.time()

    for arr in iter_gpkg_chunks(info, fields, args.chunk_size):
        k = arr.shape[0]
        ids = facet_ids_to_int(arr[:, 0])
        expected = np.arange(start, start + k, dtype=np.int64) + facet_id_base
        if not np.array_equal(ids, expected):
            bad = np.flatnonzero(ids != expected)
            j = int(bad[0]) if bad.size else 0
            raise ValueError(
                f"L={L:g}: facet_id mismatch at row {start+j:,}: "
                f"got {ids[j]}, expected {expected[j]}."
            )

        slope = arr[:, 1]
        az = arr[:, 2]
        current_area = arr[:, 3]
        na = np.asarray(native_area[start:start+k])
        lat = np.asarray(native_lat[start:start+k], dtype=np.float64)
        lon = np.asarray(native_lon[start:start+k], dtype=np.float64)
        regional_w = current_area if args.regional_weight == "current" else na

        global_m.update(slope, regional_w)
        global_out_hist.update(slope, regional_w)
        global_fine.update(slope, regional_w)
        update_roi_accumulators(
            native_roi_code(lat, lon), slope, az, regional_w,
            roi_m, roi_c, roi_fine, roi_out_hist,
        )
        for acc in grid_accs.values():
            acc.update_from_latlon(lat, lon, slope, az, regional_w)

        vector_w = na if args.vector_weight == "native" else current_area
        g0 = np.asarray(native_gravity[start:start+k, :], dtype=np.float64)
        g1 = arr[:, 4:7].astype(np.float64, copy=False)
        n0 = np.linalg.norm(g0, axis=1)
        n1 = np.linalg.norm(g1, axis=1)
        good = (
            np.isfinite(n0) & np.isfinite(n1) & (n0 > 0.0) & (n1 > 0.0)
            & np.isfinite(vector_w) & (vector_w > 0.0)
        )
        if np.any(good):
            dot = np.einsum("ij,ij->i", g0[good], g1[good])
            cosang = np.clip(dot / (n0[good] * n1[good]), -1.0, 1.0)
            dg = np.degrees(np.arccos(cosang))
            dmag = 100.0 * np.abs(n1[good] - n0[good]) / n0[good]
            vw = vector_w[good].astype(np.float64, copy=False)
            gdir_m.update(dg, vw); gdir_fine.update(dg, vw)
            gmag_m.update(dmag, vw); gmag_fine.update(dmag, vw)

        start += k
        if start == n or start % (args.chunk_size * 10) == 0:
            print(
                f"[INFO] L={L:g} GPKG: {start:,}/{n:,} "
                f"({100.0*start/n:.1f}%)", flush=True,
            )

    if start != n:
        raise RuntimeError(f"L={L:g}: read {start:,} rows, expected {n:,}")

    global_row = summarize_global_slope(L, args.regional_weight, global_m, global_fine)
    roi_rows = summarize_rois(L, args.regional_weight, roi_m, roi_c, roi_fine)
    vector_row = {
        "L_m": L,
        "vector_weighting": args.vector_weight,
        "gravity_dir_mean_change_deg": gdir_m.mean,
        "gravity_dir_std_change_deg": gdir_m.std,
        "gravity_dir_p50_change_deg": gdir_fine.quantile(0.50),
        "gravity_dir_p95_change_deg": gdir_fine.quantile(0.95),
        "gravity_dir_max_change_deg": gdir_m.max_x,
        "gravity_mag_abs_mean_change_pct": gmag_m.mean,
        "gravity_mag_abs_p50_change_pct": gmag_fine.quantile(0.50),
        "gravity_mag_abs_p95_change_pct": gmag_fine.quantile(0.95),
        "gravity_mag_abs_max_change_pct": gmag_m.max_x,
        "gravity_mag_hist_overflow_weight": gmag_fine.overflow_weight,
    }

    print(
        f"[RESULT] L={L:g}: theta95={global_row['theta_p95_deg']:.4f} deg; "
        f"median Delta-g={vector_row['gravity_dir_p50_change_deg']:.6f} deg; "
        f"p95 Delta-g={vector_row['gravity_dir_p95_change_deg']:.6f} deg; "
        f"median |delta-g|={vector_row['gravity_mag_abs_p50_change_pct']:.6f}%",
        flush=True,
    )
    print(f"[TIME] L={L:g} GPKG analysis: {time.time()-t0:.1f} s", flush=True)
    return global_row, global_out_hist, roi_rows, roi_out_hist, grid_accs, vector_row


def native_vector_zero_row(
    L: float, vector_weight: str
) -> Dict[str, object]:
    return {
        "L_m": L,
        "vector_weighting": vector_weight,
        "gravity_dir_mean_change_deg": 0.0,
        "gravity_dir_std_change_deg": 0.0,
        "gravity_dir_p50_change_deg": 0.0,
        "gravity_dir_p95_change_deg": 0.0,
        "gravity_dir_max_change_deg": 0.0,
        "gravity_mag_abs_mean_change_pct": 0.0,
        "gravity_mag_abs_p50_change_pct": 0.0,
        "gravity_mag_abs_p95_change_pct": 0.0,
        "gravity_mag_abs_max_change_pct": 0.0,
        "gravity_mag_hist_overflow_weight": 0.0,
    }


def count_obj(path: Path) -> Tuple[int, int]:
    nv = 0
    nf = 0
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                nv += 1
            elif line.startswith("f "):
                nf += 1
    return nv, nf


def parse_face_index(token: str, vertices_seen: int) -> int:
    raw = token.split("/", 1)[0]
    idx = int(raw)
    return idx - 1 if idx > 0 else vertices_seen + idx


def read_native_obj(
    path: Path,
    n_vertices: int,
    n_faces: int,
) -> Tuple[np.ndarray, np.ndarray]:
    vertices = np.empty((n_vertices, 3), dtype=np.float64)
    faces = np.empty((n_faces, 3), dtype=np.int32)

    vi = 0
    fi = 0
    t0 = time.time()
    print(f"[INFO] Reading native OBJ: {path}", flush=True)

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                p = line.split()
                vertices[vi] = (
                    float(p[1]),
                    float(p[2]),
                    float(p[3]),
                )
                vi += 1
            elif line.startswith("f "):
                p = line.split()
                if len(p) != 4:
                    raise ValueError(
                        f"Non-triangular OBJ face: {line[:100]!r}"
                    )
                faces[fi] = (
                    parse_face_index(p[1], vi),
                    parse_face_index(p[2], vi),
                    parse_face_index(p[3], vi),
                )
                fi += 1

    if vi != n_vertices or fi != n_faces:
        raise RuntimeError(
            f"Native OBJ count mismatch: v={vi}/{n_vertices}, "
            f"f={fi}/{n_faces}"
        )

    print(
        f"[TIME] Native OBJ read: {time.time() - t0:.1f} s",
        flush=True,
    )
    return vertices, faces


def read_smoothed_vertices(
    path: Path, expected_vertices: int
) -> np.ndarray:
    vertices = np.empty((expected_vertices, 3), dtype=np.float64)
    vi = 0
    t0 = time.time()
    print(f"[INFO] Reading smoothed OBJ vertices: {path}", flush=True)

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                if vi >= expected_vertices:
                    raise RuntimeError(
                        f"{path}: too many vertices."
                    )
                p = line.split()
                vertices[vi] = (
                    float(p[1]),
                    float(p[2]),
                    float(p[3]),
                )
                vi += 1
            elif line.startswith("f "):
                # Connectivity/order is known to be preserved by the smoothing
                # workflow, so face lines need not be reread for each scale.
                break

    if vi != expected_vertices:
        raise RuntimeError(
            f"{path}: vertices {vi:,} != native {expected_vertices:,}"
        )

    print(
        f"[TIME] Smoothed OBJ vertex read: {time.time() - t0:.1f} s",
        flush=True,
    )
    return vertices


def face_cross(
    vertices: np.ndarray, faces: np.ndarray
) -> np.ndarray:
    p0 = vertices[faces[:, 0]]
    p1 = vertices[faces[:, 1]]
    p2 = vertices[faces[:, 2]]
    return np.cross(p1 - p0, p2 - p0)


def analyze_normal_scale(
    args: argparse.Namespace,
    L: float,
    native_vertices: np.ndarray,
    smoothed_vertices: np.ndarray,
    faces: np.ndarray,
    native_area: np.memmap,
    current_area_for_vector: Optional[np.ndarray] = None,
) -> Dict[str, object]:
    m = WeightedMoments()
    fine = UniformWeightedHistogram(
        0.0, 180.0, args.fine_quantile_bin_width_deg
    )

    nfaces = faces.shape[0]
    t0 = time.time()

    for start in range(0, nfaces, args.obj_normal_chunk_size):
        end = min(start + args.obj_normal_chunk_size, nfaces)
        f = faces[start:end]

        c0 = face_cross(native_vertices, f)
        c1 = face_cross(smoothed_vertices, f)
        n0 = np.linalg.norm(c0, axis=1)
        n1 = np.linalg.norm(c1, axis=1)

        good = (
            np.isfinite(n0)
            & np.isfinite(n1)
            & (n0 > 0.0)
            & (n1 > 0.0)
        )
        if np.any(good):
            dot = np.einsum("ij,ij->i", c0[good], c1[good])
            cosang = dot / (n0[good] * n1[good])
            cosang = np.clip(cosang, -1.0, 1.0)
            dn = np.degrees(np.arccos(cosang))

            if args.vector_weight == "native":
                w = np.asarray(
                    native_area[start:end][good],
                    dtype=np.float64,
                )
            else:
                if current_area_for_vector is None:
                    raise ValueError(
                        "current vector weighting requested without "
                        "current-area array"
                    )
                w = np.asarray(
                    current_area_for_vector[start:end][good],
                    dtype=np.float64,
                )

            m.update(dn, w)
            fine.update(dn, w)

        if end == nfaces or end % (
            args.obj_normal_chunk_size * 10
        ) == 0:
            print(
                f"[INFO] L={L:g} normals: {end:,}/{nfaces:,} "
                f"({100.0 * end / nfaces:.1f}%)",
                flush=True,
            )

    row = {
        "L_m": L,
        "normal_dir_mean_change_deg": m.mean,
        "normal_dir_std_change_deg": m.std,
        "normal_dir_p50_change_deg": fine.quantile(0.50),
        "normal_dir_p95_change_deg": fine.quantile(0.95),
        "normal_dir_max_change_deg": m.max_x,
    }

    print(
        f"[RESULT] L={L:g}: median Delta-n="
        f"{row['normal_dir_p50_change_deg']:.6f} deg; "
        f"p95 Delta-n={row['normal_dir_p95_change_deg']:.6f} deg",
        flush=True,
    )
    print(
        f"[TIME] L={L:g} normal analysis: {time.time() - t0:.1f} s",
        flush=True,
    )
    return row


def load_current_areas(
    info: GpkgInfo,
    chunk_size: int,
    facet_id_base: int,
) -> np.ndarray:
    """
    Used only for the optional --vector-weight current normal analysis.
    Default native weighting does not need this extra memory/read.
    """
    arr_out = np.empty(info.feature_count, dtype=np.float64)
    start = 0
    for arr in iter_gpkg_chunks(
        info, ("facet_id", "facet_area"), chunk_size
    ):
        k = arr.shape[0]
        ids = facet_ids_to_int(arr[:, 0])
        expected = (
            np.arange(start, start + k, dtype=np.int64) + facet_id_base
        )
        if not np.array_equal(ids, expected):
            raise ValueError("facet_id mismatch while loading current areas")
        arr_out[start : start + k] = arr[:, 1]
        start += k
    return arr_out


def write_dict_rows(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=fieldnames)
        wr.writeheader()
        wr.writerows(rows)


def write_global_histograms(
    path: Path,
    hist_by_scale: Dict[float, UniformWeightedHistogram],
) -> None:
    fields = (
        "L_m",
        "bin_left_deg",
        "bin_right_deg",
        "bin_center_deg",
        "area_weight",
        "area_fraction",
        "cumulative_fraction",
    )
    with path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        for L in sorted(hist_by_scale):
            h = hist_by_scale[L]
            total = float(np.sum(h.counts))
            if total <= 0.0:
                continue
            edges = h.edges()
            centers = h.centers()
            frac = h.counts / total
            cum = np.cumsum(frac)
            for i in range(h.n):
                wr.writerow(
                    {
                        "L_m": L,
                        "bin_left_deg": edges[i],
                        "bin_right_deg": edges[i + 1],
                        "bin_center_deg": centers[i],
                        "area_weight": h.counts[i],
                        "area_fraction": frac[i],
                        "cumulative_fraction": cum[i],
                    }
                )


def write_roi_histograms(
    path: Path,
    hist_by_scale: Dict[float, List[UniformWeightedHistogram]],
) -> None:
    fields = (
        "L_m",
        "region",
        "bin_left_deg",
        "bin_right_deg",
        "bin_center_deg",
        "area_weight",
        "area_fraction",
        "cumulative_fraction",
    )
    with path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()

        for L in sorted(hist_by_scale):
            for rid, name in enumerate(ROI_NAMES):
                h = hist_by_scale[L][rid]
                total = float(np.sum(h.counts))
                if total <= 0.0:
                    continue
                edges = h.edges()
                centers = h.centers()
                frac = h.counts / total
                cum = np.cumsum(frac)
                for i in range(h.n):
                    wr.writerow(
                        {
                            "L_m": L,
                            "region": name,
                            "bin_left_deg": edges[i],
                            "bin_right_deg": edges[i + 1],
                            "bin_center_deg": centers[i],
                            "area_weight": h.counts[i],
                            "area_fraction": frac[i],
                            "cumulative_fraction": cum[i],
                        }
                    )


def merge_normal_into_vector_rows(
    vector_rows: List[Dict[str, object]],
    normal_rows: Dict[float, Dict[str, object]],
) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in sorted(vector_rows, key=lambda r: float(r["L_m"])):
        L = float(row["L_m"])
        merged = dict(row)
        if L in normal_rows:
            for k, v in normal_rows[L].items():
                if k != "L_m":
                    merged[k] = v
        out.append(merged)
    return out



def weighted_quantile_exact(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    good = np.isfinite(values) & np.isfinite(weights) & (weights > 0.0)
    if not np.any(good):
        return float("nan")
    x = values[good].astype(np.float64, copy=False)
    w = weights[good].astype(np.float64, copy=False)
    order = np.argsort(x)
    x = x[order]
    w = w[order]
    cw = np.cumsum(w)
    target = q * cw[-1]
    i = int(np.searchsorted(cw, target, side="left"))
    return float(x[min(i, x.size - 1)])


def summarize_grid_window_rows(rows: List[Dict[str, object]]) -> Dict[str, object]:
    if not rows:
        raise ValueError("Cannot summarize an empty grid.")
    W = float(rows[0]["W_deg"])
    L = float(rows[0]["L_m"])
    area = np.asarray([float(r["area_weight_sum"]) for r in rows], dtype=np.float64)

    def qs(key: str):
        x = np.asarray([float(r[key]) for r in rows], dtype=np.float64)
        return (
            weighted_quantile_exact(x, area, 0.25),
            weighted_quantile_exact(x, area, 0.50),
            weighted_quantile_exact(x, area, 0.75),
        )

    r25, r50, r75 = qs("R")
    s25, s50, s75 = qs("sigma_psi_deg")
    t25, t50, t75 = qs("theta_std_deg")
    p25, p50, p75 = qs("theta_p95_deg")
    return {
        "L_m": L,
        "W_deg": W,
        "nonempty_cell_count": len(rows),
        "area_weight_sum": float(np.sum(area)),
        "cell_R_areaweighted_p25": r25,
        "cell_R_areaweighted_p50": r50,
        "cell_R_areaweighted_p75": r75,
        "cell_sigma_psi_deg_areaweighted_p25": s25,
        "cell_sigma_psi_deg_areaweighted_p50": s50,
        "cell_sigma_psi_deg_areaweighted_p75": s75,
        "cell_theta_std_deg_areaweighted_p25": t25,
        "cell_theta_std_deg_areaweighted_p50": t50,
        "cell_theta_std_deg_areaweighted_p75": t75,
        "cell_theta_p95_deg_areaweighted_p25": p25,
        "cell_theta_p95_deg_areaweighted_p50": p50,
        "cell_theta_p95_deg_areaweighted_p75": p75,
    }


GRID_FIELDS = (
    "L_m", "W_deg", "cell_id",
    "lat_min_deg", "lat_max_deg", "lat_center_deg",
    "lon_min_deg", "lon_max_deg", "lon_center_deg",
    "facet_count", "area_weight_sum",
    "theta_mean_deg", "theta_std_deg", "theta_p95_deg",
    "psi_mean_deg", "R", "sigma_psi_deg",
)


def initialize_grid_csv(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=GRID_FIELDS)
        wr.writeheader()


def append_grid_accumulators(
    path: Path,
    L: float,
    grid_accs: Dict[float, GridAccumulator],
) -> List[Dict[str, object]]:
    summaries: List[Dict[str, object]] = []
    if not grid_accs:
        return summaries
    with path.open("a", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=GRID_FIELDS)
        for W in sorted(grid_accs):
            rows = grid_accs[W].rows(L)
            wr.writerows(rows)
            summaries.append(summarize_grid_window_rows(rows))
            print(
                f"[INFO] W={W:g} deg, L={L:g}: wrote {len(rows):,} nonempty grid cells",
                flush=True,
            )
    return summaries


def make_plots(
    args: argparse.Namespace,
    global_hists: Dict[float, UniformWeightedHistogram],
    vector_rows: List[Dict[str, object]],
    roi_rows: List[Dict[str, object]],
    grid_window_rows: List[Dict[str, object]],
) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(
            f"[WARN] matplotlib unavailable; skipping plots: {exc}",
            flush=True,
        )
        return

    # Global SFD.
    fig, ax = plt.subplots()
    for L in sorted(global_hists):
        h = global_hists[L]
        total = float(np.sum(h.counts))
        if total > 0.0:
            ax.plot(
                h.centers(),
                h.counts / total,
                label=f"{fmt_scale(L)} m",
            )
    ax.set_xlabel("Gravity-referenced slope (deg)")
    ax.set_ylabel("Fractional surface area per bin")
    ax.legend(ncol=2, fontsize="small")
    fig.tight_layout()
    fig.savefig(
        args.output_dir / "global_slope_distributions.png",
        dpi=200,
    )
    plt.close(fig)

    # Vector direction response.
    vr = sorted(vector_rows, key=lambda r: float(r["L_m"]))
    L = np.asarray([float(r["L_m"]) for r in vr])
    g50 = np.asarray(
        [float(r["gravity_dir_p50_change_deg"]) for r in vr]
    )
    g95 = np.asarray(
        [float(r["gravity_dir_p95_change_deg"]) for r in vr]
    )

    fig, ax = plt.subplots()
    ax.plot(L, g50, marker="o", label="Gravity direction median")
    ax.plot(L, g95, marker="o", label="Gravity direction p95")

    if all("normal_dir_p50_change_deg" in r for r in vr):
        n50 = np.asarray(
            [float(r["normal_dir_p50_change_deg"]) for r in vr]
        )
        n95 = np.asarray(
            [float(r["normal_dir_p95_change_deg"]) for r in vr]
        )
        ax.plot(L, n50, marker="o", label="Normal direction median")
        ax.plot(L, n95, marker="o", label="Normal direction p95")

    ax.set_xscale("log")
    ax.set_xlabel("Smoothing wavelength L (m)")
    ax.set_ylabel("Angular change from native model (deg)")
    ax.legend(fontsize="small")
    fig.tight_layout()
    fig.savefig(
        args.output_dir / "vector_direction_response.png",
        dpi=200,
    )
    plt.close(fig)

    # Gravity magnitude.
    gm50 = np.asarray(
        [float(r["gravity_mag_abs_p50_change_pct"]) for r in vr]
    )
    gm95 = np.asarray(
        [float(r["gravity_mag_abs_p95_change_pct"]) for r in vr]
    )
    fig, ax = plt.subplots()
    ax.plot(L, gm50, marker="o", label="Median")
    ax.plot(L, gm95, marker="o", label="p95")
    ax.set_xscale("log")
    ax.set_xlabel("Smoothing wavelength L (m)")
    ax.set_ylabel("Absolute effective-gravity magnitude change (%)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        args.output_dir / "gravity_magnitude_response.png",
        dpi=200,
    )
    plt.close(fig)

    # ROI theta95.
    fig, ax = plt.subplots()
    for name in ROI_NAMES:
        rr = sorted(
            [r for r in roi_rows if r["region"] == name],
            key=lambda r: float(r["L_m"]),
        )
        ax.plot(
            [float(r["L_m"]) for r in rr],
            [float(r["theta_p95_deg"]) for r in rr],
            marker="o",
            label=name,
        )
    ax.set_xscale("log")
    ax.set_xlabel("Smoothing wavelength L (m)")
    ax.set_ylabel("Regional 95th-percentile slope (deg)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        args.output_dir / "roi_theta95_response.png",
        dpi=200,
    )
    plt.close(fig)

    # ROI R.
    fig, ax = plt.subplots()
    for name in ROI_NAMES:
        rr = sorted(
            [r for r in roi_rows if r["region"] == name],
            key=lambda r: float(r["L_m"]),
        )
        ax.plot(
            [float(r["L_m"]) for r in rr],
            [float(r["R"]) for r in rr],
            marker="o",
            label=name,
        )
    ax.set_xscale("log")
    ax.set_xlabel("Smoothing wavelength L (m)")
    ax.set_ylabel("Mean resultant length R")
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        args.output_dir / "roi_directional_coherence.png",
        dpi=200,
    )
    plt.close(fig)


    if grid_window_rows:
        fig, ax = plt.subplots()
        for W in sorted({float(r["W_deg"]) for r in grid_window_rows}):
            rr = sorted(
                [r for r in grid_window_rows if float(r["W_deg"]) == W],
                key=lambda r: float(r["L_m"]),
            )
            ax.plot(
                [float(r["L_m"]) for r in rr],
                [float(r["cell_R_areaweighted_p50"]) for r in rr],
                marker="o",
                label=f"W={fmt_scale(W)} deg",
            )
        ax.set_xscale("log")
        ax.set_xlabel("Smoothing wavelength L (m)")
        ax.set_ylabel("Area-weighted median cell R")
        ax.legend()
        fig.tight_layout()
        fig.savefig(args.output_dir / "grid_window_R_sensitivity.png", dpi=200)
        plt.close(fig)

        fig, ax = plt.subplots()
        for W in sorted({float(r["W_deg"]) for r in grid_window_rows}):
            rr = sorted(
                [r for r in grid_window_rows if float(r["W_deg"]) == W],
                key=lambda r: float(r["L_m"]),
            )
            ax.plot(
                [float(r["L_m"]) for r in rr],
                [float(r["cell_sigma_psi_deg_areaweighted_p50"]) for r in rr],
                marker="o",
                label=f"W={fmt_scale(W)} deg",
            )
        ax.set_xscale("log")
        ax.set_xlabel("Smoothing wavelength L (m)")
        ax.set_ylabel("Area-weighted median cell sigma_psi (deg)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(args.output_dir / "grid_window_sigma_psi_sensitivity.png", dpi=200)
        plt.close(fig)



def read_saved_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required saved analysis output not found: {path}"
        )
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def make_plots_from_saved_outputs(args: argparse.Namespace) -> None:
    """
    Regenerate the same preview plots from previously written CSV products.

    This is intentionally independent of GPKG/OBJ inputs so that installing
    matplotlib after a completed analysis does not require repeating the
    expensive numerical analysis.
    """
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise RuntimeError(
            "matplotlib is required for --plots-only. "
            "Install it in the active environment and rerun."
        ) from exc

    outdir = args.output_dir

    global_hist_rows = read_saved_csv_rows(
        outdir / "global_slope_histograms.csv"
    )
    vector_rows = read_saved_csv_rows(
        outdir / "vector_response_summary.csv"
    )
    roi_rows = read_saved_csv_rows(
        outdir / "roi_scale_response.csv"
    )

    grid_summary_path = outdir / "grid_window_summary.csv"
    grid_window_rows = (
        read_saved_csv_rows(grid_summary_path)
        if grid_summary_path.exists()
        else []
    )

    # Global slope-frequency distributions.
    grouped_hist: Dict[float, List[Dict[str, str]]] = {}
    for row in global_hist_rows:
        L = float(row["L_m"])
        grouped_hist.setdefault(L, []).append(row)

    fig, ax = plt.subplots()
    for L in sorted(grouped_hist):
        rr = sorted(
            grouped_hist[L],
            key=lambda r: float(r["bin_center_deg"]),
        )
        ax.plot(
            [float(r["bin_center_deg"]) for r in rr],
            [float(r["area_fraction"]) for r in rr],
            label=f"{fmt_scale(L)} m",
        )
    ax.set_xlabel("Gravity-referenced slope (deg)")
    ax.set_ylabel("Fractional surface area per bin")
    ax.legend(ncol=2, fontsize="small")
    fig.tight_layout()
    path = outdir / "global_slope_distributions.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"[PLOT] {path}", flush=True)

    # Surface-normal and effective-gravity directional response.
    vr = sorted(vector_rows, key=lambda r: float(r["L_m"]))
    L = np.asarray([float(r["L_m"]) for r in vr], dtype=float)
    g50 = np.asarray(
        [float(r["gravity_dir_p50_change_deg"]) for r in vr],
        dtype=float,
    )
    g95 = np.asarray(
        [float(r["gravity_dir_p95_change_deg"]) for r in vr],
        dtype=float,
    )

    fig, ax = plt.subplots()
    ax.plot(L, g50, marker="o", label="Gravity direction median")
    ax.plot(L, g95, marker="o", label="Gravity direction p95")

    if all(
        r.get("normal_dir_p50_change_deg", "") != ""
        and r.get("normal_dir_p95_change_deg", "") != ""
        for r in vr
    ):
        n50 = np.asarray(
            [float(r["normal_dir_p50_change_deg"]) for r in vr],
            dtype=float,
        )
        n95 = np.asarray(
            [float(r["normal_dir_p95_change_deg"]) for r in vr],
            dtype=float,
        )
        ax.plot(L, n50, marker="o", label="Normal direction median")
        ax.plot(L, n95, marker="o", label="Normal direction p95")

    ax.set_xscale("log")
    ax.set_xlabel("Smoothing wavelength L (m)")
    ax.set_ylabel("Angular change from native model (deg)")
    ax.legend(fontsize="small")
    fig.tight_layout()
    path = outdir / "vector_direction_response.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"[PLOT] {path}", flush=True)

    # Effective-gravity magnitude response.
    gm50 = np.asarray(
        [float(r["gravity_mag_abs_p50_change_pct"]) for r in vr],
        dtype=float,
    )
    gm95 = np.asarray(
        [float(r["gravity_mag_abs_p95_change_pct"]) for r in vr],
        dtype=float,
    )
    fig, ax = plt.subplots()
    ax.plot(L, gm50, marker="o", label="Median")
    ax.plot(L, gm95, marker="o", label="p95")
    ax.set_xscale("log")
    ax.set_xlabel("Smoothing wavelength L (m)")
    ax.set_ylabel("Absolute effective-gravity magnitude change (%)")
    ax.legend()
    fig.tight_layout()
    path = outdir / "gravity_magnitude_response.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"[PLOT] {path}", flush=True)

    # Representative-region theta95 response.
    fig, ax = plt.subplots()
    for name in ROI_NAMES:
        rr = sorted(
            [r for r in roi_rows if r["region"] == name],
            key=lambda r: float(r["L_m"]),
        )
        ax.plot(
            [float(r["L_m"]) for r in rr],
            [float(r["theta_p95_deg"]) for r in rr],
            marker="o",
            label=name,
        )
    ax.set_xscale("log")
    ax.set_xlabel("Smoothing wavelength L (m)")
    ax.set_ylabel("Regional 95th-percentile slope (deg)")
    ax.legend()
    fig.tight_layout()
    path = outdir / "roi_theta95_response.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"[PLOT] {path}", flush=True)

    # Representative-region directional coherence.
    fig, ax = plt.subplots()
    for name in ROI_NAMES:
        rr = sorted(
            [r for r in roi_rows if r["region"] == name],
            key=lambda r: float(r["L_m"]),
        )
        ax.plot(
            [float(r["L_m"]) for r in rr],
            [float(r["R"]) for r in rr],
            marker="o",
            label=name,
        )
    ax.set_xscale("log")
    ax.set_xlabel("Smoothing wavelength L (m)")
    ax.set_ylabel("Mean resultant length R")
    ax.legend()
    fig.tight_layout()
    path = outdir / "roi_directional_coherence.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"[PLOT] {path}", flush=True)

    # W-sensitivity plots, if the saved grid summary exists.
    if grid_window_rows:
        Ws = sorted({float(r["W_deg"]) for r in grid_window_rows})

        fig, ax = plt.subplots()
        for W in Ws:
            rr = sorted(
                [
                    r for r in grid_window_rows
                    if float(r["W_deg"]) == W
                ],
                key=lambda r: float(r["L_m"]),
            )
            ax.plot(
                [float(r["L_m"]) for r in rr],
                [float(r["cell_R_areaweighted_p50"]) for r in rr],
                marker="o",
                label=f"W={fmt_scale(W)} deg",
            )
        ax.set_xscale("log")
        ax.set_xlabel("Smoothing wavelength L (m)")
        ax.set_ylabel("Area-weighted median cell R")
        ax.legend()
        fig.tight_layout()
        path = outdir / "grid_window_R_sensitivity.png"
        fig.savefig(path, dpi=200)
        plt.close(fig)
        print(f"[PLOT] {path}", flush=True)

        fig, ax = plt.subplots()
        for W in Ws:
            rr = sorted(
                [
                    r for r in grid_window_rows
                    if float(r["W_deg"]) == W
                ],
                key=lambda r: float(r["L_m"]),
            )
            ax.plot(
                [float(r["L_m"]) for r in rr],
                [
                    float(r["cell_sigma_psi_deg_areaweighted_p50"])
                    for r in rr
                ],
                marker="o",
                label=f"W={fmt_scale(W)} deg",
            )
        ax.set_xscale("log")
        ax.set_xlabel("Smoothing wavelength L (m)")
        ax.set_ylabel("Area-weighted median cell sigma_psi (deg)")
        ax.legend()
        fig.tight_layout()
        path = outdir / "grid_window_sigma_psi_sensitivity.png"
        fig.savefig(path, dpi=200)
        plt.close(fig)
        print(f"[PLOT] {path}", flush=True)

    print(
        "[DONE] Plot-only regeneration completed; numerical analysis was not rerun.",
        flush=True,
    )


def main() -> None:
    args = parse_args()

    if args.plots_only:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        make_plots_from_saved_outputs(args)
        return

    args.grid_sizes_deg = normalize_grid_sizes(args.grid_sizes_deg)

    for value, name in (
        (args.chunk_size, "--chunk-size"),
        (args.obj_normal_chunk_size, "--obj-normal-chunk-size"),
    ):
        if value <= 0:
            raise ValueError(f"{name} must be positive.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    gpkg_map = discover_gpkgs(args.gpkg_dir, args.gpkg_regex)
    if args.native_scale not in gpkg_map:
        raise FileNotFoundError(
            f"Native scale {args.native_scale:g} not found. Available: {sorted(gpkg_map)}"
        )

    if args.scales:
        requested = {float(x) for x in args.scales}
        requested.add(float(args.native_scale))
        missing = sorted(requested.difference(gpkg_map))
        if missing:
            raise FileNotFoundError(f"Requested GPKG scales missing: {missing}")
        scales = sorted(requested)
    else:
        scales = sorted(gpkg_map)

    print("[INFO] Analysis scales: " + ", ".join(fmt_scale(x) for x in scales), flush=True)
    print(
        "[INFO] Grid window sizes W: " + ", ".join(f"{fmt_scale(x)} deg" for x in args.grid_sizes_deg),
        flush=True,
    )
    print(
        "[INFO] L=18 is native/unsmoothed. Grid support is assigned from native "
        "facet centroids separately for each W and held fixed while L varies.",
        flush=True,
    )

    info_by_scale: Dict[float, GpkgInfo] = {}
    for L in scales:
        print(f"[INFO] Inspecting GPKG L={L:g}: {gpkg_map[L]}", flush=True)
        info = inspect_gpkg(gpkg_map[L])
        info_by_scale[L] = info
        print(f"[INFO]   layer={info.layer}, features={info.feature_count:,}", flush=True)

    native_info = info_by_scale[args.native_scale]
    for L, info in info_by_scale.items():
        if info.feature_count != native_info.feature_count:
            raise ValueError(
                f"L={L:g} feature count {info.feature_count:,} != native {native_info.feature_count:,}"
            )

    (
        native_area, native_gravity, native_lat, native_lon, facet_id_base,
        native_global_row, native_global_hist, native_roi_rows,
        native_roi_hists, native_grid_accs,
    ) = build_native_cache_and_native_stats(args, native_info)

    global_rows: List[Dict[str, object]] = [native_global_row]
    global_hists: Dict[float, UniformWeightedHistogram] = {args.native_scale: native_global_hist}
    roi_rows: List[Dict[str, object]] = list(native_roi_rows)
    roi_hists: Dict[float, List[UniformWeightedHistogram]] = {args.native_scale: native_roi_hists}
    vector_rows: List[Dict[str, object]] = [native_vector_zero_row(args.native_scale, args.vector_weight)]
    grid_window_rows: List[Dict[str, object]] = []

    grid_path = args.output_dir / "grid_scale_response.csv"
    if not args.skip_grid:
        initialize_grid_csv(grid_path)
        grid_window_rows.extend(
            append_grid_accumulators(grid_path, args.native_scale, native_grid_accs)
        )
        del native_grid_accs

    # Each smoothed GPKG is streamed exactly once; all requested W values are
    # accumulated simultaneously from the same fixed native centroid support.
    for L in scales:
        if L == args.native_scale:
            continue
        grow, ghist, rrows, rhists, grid_accs, vrow = analyze_smoothed_gpkg(
            args, L, info_by_scale[L], native_area, native_gravity,
            native_lat, native_lon, facet_id_base,
        )
        global_rows.append(grow)
        global_hists[L] = ghist
        roi_rows.extend(rrows)
        roi_hists[L] = rhists
        vector_rows.append(vrow)
        if not args.skip_grid:
            grid_window_rows.extend(append_grid_accumulators(grid_path, L, grid_accs))
        del grid_accs

    # OBJ normal analysis.
    normal_rows: Dict[float, Dict[str, object]] = {
        args.native_scale: {
            "L_m": args.native_scale,
            "normal_dir_mean_change_deg": 0.0,
            "normal_dir_std_change_deg": 0.0,
            "normal_dir_p50_change_deg": 0.0,
            "normal_dir_p95_change_deg": 0.0,
            "normal_dir_max_change_deg": 0.0,
        }
    }
    if not args.skip_normal:
        if not args.native_obj.exists():
            raise FileNotFoundError(f"Native OBJ not found: {args.native_obj}")
        nv, nf = count_obj(args.native_obj)
        print(f"[INFO] Native OBJ: vertices={nv:,}, faces={nf:,}", flush=True)
        if nf != native_info.feature_count:
            raise ValueError(
                f"Native OBJ faces {nf:,} != GPKG facets {native_info.feature_count:,}. "
                "facet_id/face-order comparison cannot proceed."
            )
        native_vertices, faces = read_native_obj(args.native_obj, nv, nf)
        for L in scales:
            if L == args.native_scale:
                continue
            obj_path = Path(args.obj_pattern.format(L=fmt_scale(L)))
            if not obj_path.exists():
                raise FileNotFoundError(f"L={L:g} smoothed OBJ not found: {obj_path}")
            smoothed_vertices = read_smoothed_vertices(obj_path, nv)
            current_areas = None
            if args.vector_weight == "current":
                print(f"[INFO] Loading current facet areas for L={L:g} normal weighting.", flush=True)
                current_areas = load_current_areas(info_by_scale[L], args.chunk_size, facet_id_base)
            normal_rows[L] = analyze_normal_scale(
                args, L, native_vertices, smoothed_vertices, faces, native_area, current_areas
            )
            del smoothed_vertices
            if current_areas is not None:
                del current_areas

    vector_rows = merge_normal_into_vector_rows(vector_rows, normal_rows)
    global_rows.sort(key=lambda r: float(r["L_m"]))
    roi_rows.sort(key=lambda r: (float(r["L_m"]), str(r["region"])))
    vector_rows.sort(key=lambda r: float(r["L_m"]))
    grid_window_rows.sort(key=lambda r: (float(r["W_deg"]), float(r["L_m"])))

    write_dict_rows(args.output_dir / "global_slope_summary.csv", global_rows)
    write_global_histograms(args.output_dir / "global_slope_histograms.csv", global_hists)
    write_dict_rows(args.output_dir / "vector_response_summary.csv", vector_rows)
    write_dict_rows(args.output_dir / "roi_scale_response.csv", roi_rows)
    write_roi_histograms(args.output_dir / "roi_slope_histograms.csv", roi_hists)
    if not args.skip_grid:
        write_dict_rows(args.output_dir / "grid_window_summary.csv", grid_window_rows)

    overflow = [
        r for r in vector_rows
        if float(r.get("gravity_mag_hist_overflow_weight", 0.0)) > 0.0
    ]
    if overflow:
        print(
            "[WARN] |delta g| histogram overflow occurred. Increase "
            "--gravity-mag-max-pct and rerun before using magnitude percentiles.",
            flush=True,
        )

    manifest = {
        "analysis": "Phobos v004 gravity-referenced slope scale analysis",
        "native_scale_m": args.native_scale,
        "native_is_unsmoothed": True,
        "scales_m": scales,
        "grid_sizes_W_deg": args.grid_sizes_deg,
        "feature_count": native_info.feature_count,
        "facet_id_base": facet_id_base,
        "regional_weighting": args.regional_weight,
        "vector_weighting": args.vector_weight,
        "fixed_support": {
            "grid": (
                "For each W, latitude-longitude cell membership is assigned from native-model "
                "facet centroids and reused for every L. Grid edges are anchored at -90 deg "
                "latitude and -180 deg longitude. If W does not divide 180/360 exactly, the "
                "final edge band is narrower and its actual bounds are written to the CSV."
            ),
            "regions": {
                "Leading": "lat [-1,1], lon [-91,-89] deg",
                "Sub-Mars": "lat [-1,1], lon [-1,1] deg",
                "Trailing": "lat [-1,1], lon [89,91] deg",
                "Anti-Mars": "lat [-1,1], lon [179,180) union [-180,-179] deg",
            },
        },
        "histogram_settings": {
            "global_output_bin_width_deg": args.global_hist_bin_width_deg,
            "roi_output_bin_width_deg": args.roi_hist_bin_width_deg,
            "fine_quantile_bin_width_deg": args.fine_quantile_bin_width_deg,
            "grid_p95_bin_width_deg": args.grid_quantile_bin_width_deg,
            "gravity_mag_bin_width_pct": args.gravity_mag_bin_width_pct,
        },
        "grid_window_summary": (
            "Area-weighted quantiles across nonempty grid cells; intended as a descriptive "
            "W-sensitivity diagnostic, not an intrinsic transition-wavelength estimator."
        ),
        "gpkg_files": {fmt_scale(L): str(gpkg_map[L]) for L in scales},
        "native_obj": None if args.skip_normal else str(args.native_obj),
        "smoothed_obj_pattern": None if args.skip_normal else args.obj_pattern,
        "notes": [
            "GPKG geometry/point spacing is not used for cross-scale matching.",
            "Facet matching uses contiguous facet_id and preserved OBJ face order.",
            "Each requested W is an explicit fixed spatial-support scale.",
            "No threshold-defined transition wavelength is inferred by this script.",
        ],
    }
    (args.output_dir / "analysis_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    if args.plots:
        make_plots(args, global_hists, vector_rows, roi_rows, grid_window_rows)

    print("[DONE] Slope analysis completed.", flush=True)
    for name in (
        "global_slope_summary.csv",
        "global_slope_histograms.csv",
        "vector_response_summary.csv",
        "roi_scale_response.csv",
        "roi_slope_histograms.csv",
        "grid_scale_response.csv",
        "grid_window_summary.csv",
        "analysis_manifest.json",
    ):
        p = args.output_dir / name
        if p.exists():
            print(f"  {p}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CANCELLED]", file=sys.stderr, flush=True)
        raise SystemExit(130)
