#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate *_NoSpin_result_TA000.csv dynamic-slope products for Phobos.

GFandSlope itself is not included here.  This script is a compact wrapper/
post-processing script for GFandSlope facet-wise output tables.  It reads the
precomputed GFandSlope table, uses GravAcc.x/y/z as the self-gravity term, adds
the SPICE-derived Mars tidal, centrifugal, and Euler accelerations in
IAU_PHOBOS, and writes the dynamic slope and downslope azimuth at TA=000 deg.

The output filename follows the product naming requested for this study:

    <input-stem>_NoSpin_result_TA000.csv

Input table
-----------
A whitespace-delimited GFandSlope output table with one row per facet and the
following header:

    ID Point.x Point.y Point.z Lon Lat
    CRefAcc.x CRefAcc.y CRefAcc.z
    GravAcc.x GravAcc.y GravAcc.z
    TotalAcc.x TotalAcc.y TotalAcc.z
    Gpotential Rpotential Tpotential GeopotentialSlope
    Normal.x Normal.y Normal.z Area

The coordinates Point.x/y/z are in km in IAU_PHOBOS.  All other physical
quantities are in SI units.  For the GFandSlope outputs used here, GravAcc.x/y/z
are outward vectors, so the script uses

    self-gravity acceleration = -GravAcc

Output columns
--------------
    facet_id
    lon_deg, lat_deg
    dynamic_slope_deg
    dynamic_slope_azimuth_deg
    facet_area
    g_total_x_m_s2, g_total_y_m_s2, g_total_z_m_s2, g_total_mag_m_s2

The azimuth is the downslope direction, measured clockwise from local north
toward east in degrees.

Example
-------
python make_NoSpin_result_TA000.py \
  --input-dir ../input \
  --input-files v004_80_surface.txt \
  --output-dir ./output_NoSpin_result_TA000 \
  --lsk ../spice/lsk/naif0012.tls \
  --pck ../spice/pck/pck00011.tpc \
  --gm ../spice/pck/gm_de440.tpc \
  --spk ../spice/spk/mar099s.bsp \
  --start-time 2029-01-01T00:00:00
"""

from __future__ import annotations

import argparse
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import spiceypy as spice
from scipy.optimize import brentq

KM_TO_M = 1000.0

TARGET = "PHOBOS"
OBSERVER = "MARS"
FRAME_INERTIAL = "J2000"
FRAME_FIXED = "IAU_PHOBOS"
ABERRATION_CORRECTION = "NONE"

RAW_INPUT_COLUMNS = [
    "ID",
    "Point.x", "Point.y", "Point.z",
    "Lon", "Lat",
    "CRefAcc.x", "CRefAcc.y", "CRefAcc.z",
    "GravAcc.x", "GravAcc.y", "GravAcc.z",
    "TotalAcc.x", "TotalAcc.y", "TotalAcc.z",
    "Gpotential", "Rpotential", "Tpotential",
    "GeopotentialSlope",
    "Normal.x", "Normal.y", "Normal.z",
    "Area",
]

COLUMN_ALIASES = {
    "Point.x": "Cx",
    "Point.y": "Cy",
    "Point.z": "Cz",
    "CRefAcc.x": "CRefAccX",
    "CRefAcc.y": "CRefAccY",
    "CRefAcc.z": "CRefAccZ",
    "GravAcc.x": "Gx",
    "GravAcc.y": "Gy",
    "GravAcc.z": "Gz",
    "TotalAcc.x": "Tx",
    "TotalAcc.y": "Ty",
    "TotalAcc.z": "Tz",
    "Gpotential": "Gpot",
    "Rpotential": "Rpot",
    "Tpotential": "Tpot",
    "GeopotentialSlope": "GeoSlope",
    "Normal.x": "Nx",
    "Normal.y": "Ny",
    "Normal.z": "Nz",
}

INTERNAL_COLUMNS = [
    "ID", "Cx", "Cy", "Cz", "Lon", "Lat",
    "CRefAccX", "CRefAccY", "CRefAccZ",
    "Gx", "Gy", "Gz",
    "Tx", "Ty", "Tz",
    "Gpot", "Rpot", "Tpot",
    "GeoSlope",
    "Nx", "Ny", "Nz",
    "Area",
]

GM_MARS: float | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate *_NoSpin_result_TA000.csv dynamic-slope products "
            "from GFandSlope facet-wise output tables."
        )
    )
    parser.add_argument("--input-dir", default="../input")
    parser.add_argument(
        "--input-files",
        nargs="+",
        required=True,
        help="One or more GFandSlope facet-wise output tables.",
    )
    parser.add_argument("--output-dir", default="./output_NoSpin_result_TA000")

    parser.add_argument("--lsk", required=True, help="NAIF leap-seconds kernel")
    parser.add_argument("--pck", required=True, help="NAIF text PCK containing IAU_PHOBOS orientation")
    parser.add_argument("--gm", required=True, help="NAIF GM kernel")
    parser.add_argument("--spk", required=True, help="Mars-system SPK kernel")

    parser.add_argument("--start-time", default="2029-01-01T00:00:00")
    parser.add_argument(
        "--ta",
        nargs="+",
        type=float,
        default=[0.0],
        help="Target true anomaly values in degrees. Default: 0",
    )
    parser.add_argument(
        "--alpha-dt",
        type=float,
        default=1.0,
        help="Time step [s] for centered finite difference of angular velocity.",
    )
    return parser.parse_args()


def load_kernels(args: argparse.Namespace) -> None:
    """Load SPICE kernels and Mars GM."""
    global GM_MARS
    for kernel in [args.lsk, args.pck, args.gm, args.spk]:
        spice.furnsh(kernel)
        print(f"Loaded kernel: {kernel}")
    GM_MARS = float(spice.bodvrd("MARS", "GM", 1)[1][0])
    print(f"Mars GM: {GM_MARS:.15e} km^3/s^2")


def state_phobos_about_mars(et: float) -> np.ndarray:
    state, _ = spice.spkezr(TARGET, et, FRAME_INERTIAL, ABERRATION_CORRECTION, OBSERVER)
    return np.asarray(state, dtype=float)


def position_mars_from_phobos(et: float) -> np.ndarray:
    state, _ = spice.spkezr(OBSERVER, et, FRAME_INERTIAL, ABERRATION_CORRECTION, TARGET)
    return np.asarray(state[:3], dtype=float)


def radial_velocity(et: float) -> float:
    state = state_phobos_about_mars(et)
    return float(np.dot(state[:3], state[3:6]))


def true_anomaly_deg(et: float) -> float:
    """Osculating true anomaly of Phobos about Mars in degrees [0, 360)."""
    if GM_MARS is None:
        raise RuntimeError("Mars GM has not been loaded")
    state = state_phobos_about_mars(et)
    r_vec = state[:3]
    v_vec = state[3:6]
    r = np.linalg.norm(r_vec)
    v2 = float(np.dot(v_vec, v_vec))
    rv = float(np.dot(r_vec, v_vec))
    e_vec = ((v2 - GM_MARS / r) * r_vec - rv * v_vec) / GM_MARS
    e = np.linalg.norm(e_vec)
    if e <= 0.0:
        raise RuntimeError("Invalid osculating eccentricity")
    cos_nu = float(np.dot(e_vec, r_vec) / (e * r))
    cos_nu = float(np.clip(cos_nu, -1.0, 1.0))
    nu = float(np.arccos(cos_nu))
    if rv < 0.0:
        nu = 2.0 * np.pi - nu
    return float(np.degrees(nu) % 360.0)


def find_next_periapsis(start_time: str) -> float:
    """Find the first periapsis after start_time from r dot v = 0."""
    start_et = spice.str2et(start_time)
    times = np.linspace(start_et, start_et + 40000.0, 1500)
    rv = np.array([radial_velocity(t) for t in times])
    for i in range(len(times) - 1):
        if rv[i] < 0.0 and rv[i + 1] >= 0.0:
            return float(brentq(radial_velocity, times[i], times[i + 1]))
    raise RuntimeError("Could not find periapsis crossing after start time")


def find_next_periapsis_after(et_after: float) -> float:
    times = np.linspace(et_after, et_after + 40000.0, 1500)
    rv = np.array([radial_velocity(t) for t in times])
    for i in range(len(times) - 1):
        if rv[i] < 0.0 and rv[i + 1] >= 0.0:
            return float(brentq(radial_velocity, times[i], times[i + 1]))
    raise RuntimeError("Could not find next periapsis crossing")


def wrapped_difference_deg(a: float, b: float) -> float:
    return float((a - b + 180.0) % 360.0 - 180.0)


def target_epochs(start_time: str, targets_deg: list[float]) -> list[tuple[float, float]]:
    """Find epochs for target true anomalies in the first full orbit."""
    peri_et = find_next_periapsis(start_time)
    next_peri_et = find_next_periapsis_after(peri_et + 600.0)
    out: list[tuple[float, float]] = []

    for target in targets_deg:
        target_mod = target % 360.0
        if abs(target_mod) < 1.0e-12 or abs(target_mod - 360.0) < 1.0e-12:
            out.append((target, peri_et))
            continue

        def f(et: float) -> float:
            return wrapped_difference_deg(true_anomaly_deg(et), target_mod)

        samples = np.linspace(peri_et + 30.0, next_peri_et - 30.0, 1200)
        values = np.array([f(t) for t in samples])
        found = None
        for i in range(len(samples) - 1):
            if values[i] == 0.0:
                found = float(samples[i])
                break
            if values[i] * values[i + 1] < 0.0:
                found = float(brentq(f, samples[i], samples[i + 1]))
                break
        if found is None:
            raise RuntimeError(f"Could not find epoch for TA={target:g} deg")
        out.append((target, found))
    return out


def rotation_omega_alpha(et: float, alpha_dt: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Return rotation J2000->IAU_PHOBOS and omega/alpha in IAU_PHOBOS.

    spice.xf2rav returns angular velocity components in the input frame of the
    state transformation.  For sxform(J2000, IAU_PHOBOS), that input frame is
    J2000, so omega is rotated into IAU_PHOBOS before cross products with
    IAU_PHOBOS surface vectors.
    """
    xform = spice.sxform(FRAME_INERTIAL, FRAME_FIXED, et)
    rot, omega_j2000 = spice.xf2rav(xform)
    rot = np.asarray(rot, dtype=float)
    omega_j2000 = np.asarray(omega_j2000, dtype=float)

    xform_p = spice.sxform(FRAME_INERTIAL, FRAME_FIXED, et + alpha_dt)
    _, omega_p_j2000 = spice.xf2rav(xform_p)
    xform_m = spice.sxform(FRAME_INERTIAL, FRAME_FIXED, et - alpha_dt)
    _, omega_m_j2000 = spice.xf2rav(xform_m)
    alpha_j2000 = (np.asarray(omega_p_j2000) - np.asarray(omega_m_j2000)) / (2.0 * alpha_dt)

    omega_fixed = rot @ omega_j2000
    alpha_fixed = rot @ alpha_j2000
    return rot, omega_fixed, alpha_fixed


def load_surface(path: Path) -> pd.DataFrame:
    """
    Load a facet table and normalize GFandSlope public column names.

    Expected input header:
      ID Point.x Point.y Point.z Lon Lat CRefAcc.x CRefAcc.y CRefAcc.z
      GravAcc.x GravAcc.y GravAcc.z TotalAcc.x TotalAcc.y TotalAcc.z
      Gpotential Rpotential Tpotential GeopotentialSlope
      Normal.x Normal.y Normal.z Area

    Internally, short aliases are used:
      Point.x -> Cx, GravAcc.x -> Gx, Normal.x -> Nx, etc.
    """
    df = pd.read_csv(path, sep=r"\s+", comment="#")

    if set(["Point.x", "GravAcc.x", "Normal.x"]).issubset(df.columns):
        df = df.rename(columns=COLUMN_ALIASES)
        missing = [c for c in INTERNAL_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"Missing expected input columns after renaming: {missing}")
        df = df[INTERNAL_COLUMNS]
    else:
        # Backward-compatible positional fallback for older files.
        df = pd.read_csv(path, sep=r"\s+", comment="#", names=INTERNAL_COLUMNS, header=0)

    df = df.apply(pd.to_numeric, errors="coerce").dropna()
    return df


def local_north_east(lon_deg: np.ndarray, lat_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lon = np.radians(lon_deg)
    lat = np.radians(lat_deg)
    east = np.column_stack([-np.sin(lon), np.cos(lon), np.zeros_like(lon)])
    north = np.column_stack([
        -np.sin(lat) * np.cos(lon),
        -np.sin(lat) * np.sin(lon),
         np.cos(lat),
    ])
    return north, east


def sign_diagnostics(df: pd.DataFrame) -> dict[str, float]:
    """Check the expected vector-sign convention for the input table."""
    r = df[["Cx", "Cy", "Cz"]].to_numpy(float)
    g = df[["Gx", "Gy", "Gz"]].to_numpy(float)
    normal = df[["Nx", "Ny", "Nz"]].to_numpy(float)

    raw_g_outward = float(np.mean(np.einsum("ij,ij->i", g, r) > 0.0))
    normal_outward = float(np.mean(np.einsum("ij,ij->i", normal, r) > 0.0))

    print(f"  raw GravAcc outward fraction : {raw_g_outward:.8f}")
    print(f"  normal outward fraction      : {normal_outward:.8f}")

    if raw_g_outward < 0.90:
        warnings.warn(
            "Input GravAcc is expected to be outward, but it is not predominantly outward. "
            "Check the input convention before using the output.",
            RuntimeWarning,
        )
    if normal_outward < 0.90:
        warnings.warn("Facet normals are not predominantly outward.", RuntimeWarning)

    return {
        "raw_gravacc_outward_fraction": raw_g_outward,
        "normal_outward_fraction": normal_outward,
    }


def compute_at_epoch(
    df: pd.DataFrame,
    et: float,
    alpha_dt: float,
) -> tuple[pd.DataFrame, dict[str, float | str]]:
    """Compute physical-libration dynamic slope for all facets at one epoch."""
    if GM_MARS is None:
        raise RuntimeError("Mars GM has not been loaded")

    r_mars_j2000 = position_mars_from_phobos(et)
    rot, omega, alpha = rotation_omega_alpha(et, alpha_dt)
    r_mars = rot @ r_mars_j2000
    mars_distance = float(np.linalg.norm(r_mars))

    r = df[["Cx", "Cy", "Cz"]].to_numpy(float)        # km
    normal = df[["Nx", "Ny", "Nz"]].to_numpy(float)
    lon = df["Lon"].to_numpy(float)
    lat = df["Lat"].to_numpy(float)

    # GFandSlope GravAcc is outward for the files used in this study.
    # Convert it to inward self-gravity acceleration.
    raw_gravacc = df[["Gx", "Gy", "Gz"]].to_numpy(float)  # m/s^2, outward
    g_self = -raw_gravacc                                 # m/s^2, inward

    # Non-inertial accelerations in IAU_PHOBOS.
    # r is in km and omega/alpha are in rad/s and rad/s^2, so multiply by 1000.
    acc_cent = -np.cross(omega, np.cross(omega, r)) * KM_TO_M
    acc_euler = -np.cross(alpha, r) * KM_TO_M

    # Mars differential/tidal acceleration in IAU_PHOBOS.
    r_to_mars = r_mars[np.newaxis, :] - r
    d_to_mars = np.linalg.norm(r_to_mars, axis=1)
    acc_tidal = GM_MARS * (
        r_to_mars / d_to_mars[:, np.newaxis] ** 3
        - r_mars[np.newaxis, :] / mars_distance**3
    ) * KM_TO_M

    g_total = g_self + acc_cent + acc_tidal + acc_euler
    g_mag = np.linalg.norm(g_total, axis=1)

    n_mag = np.linalg.norm(normal, axis=1)
    n_hat = normal / n_mag[:, np.newaxis]

    # Dynamic slope angle: angle between the outward normal and the upward
    # direction, equivalently arccos[-(n dot g)/(|n||g|)].
    dot_n_g = np.einsum("ij,ij->i", normal, g_total)
    cos_slope = -dot_n_g / (n_mag * g_mag)
    slope = np.degrees(np.arccos(np.clip(cos_slope, -1.0, 1.0)))

    outward_total_fraction = float(np.mean(dot_n_g >= 0.0))
    if outward_total_fraction > 1.0e-4:
        warnings.warn(
            f"{outward_total_fraction:.6%} of facets have normal dot total acceleration >= 0. "
            "Check vector signs and frame consistency.",
            RuntimeWarning,
        )

    # Downslope azimuth: tangent projection of the total acceleration vector.
    g_dot_n = np.einsum("ij,ij->i", g_total, n_hat)
    g_tangent = g_total - g_dot_n[:, np.newaxis] * n_hat
    t_norm = np.linalg.norm(g_tangent, axis=1)

    t_hat = np.full_like(g_tangent, np.nan)
    valid = t_norm > 0.0
    t_hat[valid] = g_tangent[valid] / t_norm[valid, np.newaxis]

    north, east = local_north_east(lon, lat)
    east_component = np.einsum("ij,ij->i", t_hat, east)
    north_component = np.einsum("ij,ij->i", t_hat, north)
    azimuth = (np.degrees(np.arctan2(east_component, north_component)) + 360.0) % 360.0
    azimuth[~valid] = np.nan

    out = pd.DataFrame({
        "facet_id": df["ID"].astype(int),
        "lon_deg": lon,
        "lat_deg": lat,
        "dynamic_slope_deg": slope,
        "dynamic_slope_azimuth_deg": azimuth,
        "facet_area": df["Area"].to_numpy(float),
        "g_total_x_m_s2": g_total[:, 0],
        "g_total_y_m_s2": g_total[:, 1],
        "g_total_z_m_s2": g_total[:, 2],
        "g_total_mag_m_s2": g_mag,
    })

    mars_unit = r_mars / mars_distance

    def median_norm(v: np.ndarray) -> float:
        return float(np.median(np.linalg.norm(v, axis=1)))

    meta = {
        "utc": spice.et2utc(et, "C", 3),
        "actual_true_anomaly_deg": true_anomaly_deg(et),
        "mars_distance_km": mars_distance,
        "mars_lon_deg": float(np.degrees(np.arctan2(mars_unit[1], mars_unit[0])) % 360.0),
        "mars_lat_deg": float(np.degrees(np.arcsin(np.clip(mars_unit[2], -1.0, 1.0)))),
        "omega_x_fixed_rad_s": float(omega[0]),
        "omega_y_fixed_rad_s": float(omega[1]),
        "omega_z_fixed_rad_s": float(omega[2]),
        "alpha_x_fixed_rad_s2": float(alpha[0]),
        "alpha_y_fixed_rad_s2": float(alpha[1]),
        "alpha_z_fixed_rad_s2": float(alpha[2]),
        "median_self_m_s2": median_norm(g_self),
        "median_cent_m_s2": median_norm(acc_cent),
        "median_tidal_m_s2": median_norm(acc_tidal),
        "median_euler_m_s2": median_norm(acc_euler),
        "median_total_m_s2": median_norm(g_total),
        "outward_total_fraction": outward_total_fraction,
    }
    return out, meta


def write_output(path: Path, table: pd.DataFrame, header: list[str]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for line in header:
            f.write("# " + line.rstrip("\n") + "\n")
        table.to_csv(f, index=False)


def main() -> None:
    args = parse_args()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    load_kernels(args)

    epochs = target_epochs(args.start_time, args.ta)

    for input_name in args.input_files:
        input_path = Path(args.input_dir) / input_name
        print(f"\nInput: {input_path}")
        df = load_surface(input_path)
        diagnostics = sign_diagnostics(df)
        base = input_path.stem

        for target_ta, et in epochs:
            print(f"  Computing TA={target_ta:g} deg at {spice.et2utc(et, 'C', 3)}")
            table, meta = compute_at_epoch(df, et, alpha_dt=args.alpha_dt)

            header = [
                "script: make_NoSpin_result_TA000.py",
                "model: GFandSlope GravAcc plus SPICE-derived tidal, centrifugal, and Euler accelerations in IAU_PHOBOS",
                f"input_file: {input_path}",
                f"target_true_anomaly_deg: {target_ta}",
                f"actual_true_anomaly_deg: {meta['actual_true_anomaly_deg']}",
                f"epoch_utc: {meta['utc']}",
                f"mars_distance_km: {meta['mars_distance_km']}",
                f"mars_lon_lat_IAU_PHOBOS_deg: [{meta['mars_lon_deg']}, {meta['mars_lat_deg']}]",
                f"omega_fixed_rad_s_xyz: [{meta['omega_x_fixed_rad_s']}, {meta['omega_y_fixed_rad_s']}, {meta['omega_z_fixed_rad_s']}]",
                f"alpha_fixed_rad_s2_xyz: [{meta['alpha_x_fixed_rad_s2']}, {meta['alpha_y_fixed_rad_s2']}, {meta['alpha_z_fixed_rad_s2']}]",
                "include_euler_acceleration: True",
                "input_gravacc_convention: outward; self-gravity used here is -GravAcc",
                f"raw_gravacc_outward_fraction: {diagnostics['raw_gravacc_outward_fraction']}",
                f"normal_outward_fraction: {diagnostics['normal_outward_fraction']}",
                f"median_self_m_s2: {meta['median_self_m_s2']}",
                f"median_cent_m_s2: {meta['median_cent_m_s2']}",
                f"median_tidal_m_s2: {meta['median_tidal_m_s2']}",
                f"median_euler_m_s2: {meta['median_euler_m_s2']}",
                f"median_total_m_s2: {meta['median_total_m_s2']}",
                f"outward_total_fraction: {meta['outward_total_fraction']}",
                "dynamic_slope_azimuth_deg: downslope direction clockwise from local north toward east",
            ]
            out_path = Path(args.output_dir) / f"{base}_NoSpin_result_TA{int(round(target_ta)) % 360:03d}.csv"
            write_output(out_path, table, header)
            print(f"  Saved: {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
