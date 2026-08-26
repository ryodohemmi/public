#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Physically interpretable mesh smoothing for triangular OBJ meshes.

This script applies implicit diffusion using the cotangent Laplace-Beltrami
operator and a lumped mass matrix while preserving face connectivity and face
ordering in the written OBJ.
"""

from __future__ import annotations

import argparse
import math
import multiprocessing as mp
import os
import re
import signal
import sys
import time
import traceback
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np
import trimesh
from scipy.sparse import coo_matrix, csc_matrix, diags
from scipy.sparse.linalg import splu


HEADER_EDGE_MEAN_RE = re.compile(
    r"^\s*#\s*Edge\s+Length\s+Mean\s*=\s*([0-9.+\-eE]+)\s*km\s*$"
)
VERTEX_LINE_RE = re.compile(r"^\s*v\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)(?:\s|$)")
DEFAULT_OUTPUT_SENTINEL = "<input_without_ext>_diffuse_<definition>_<scale>.obj"
DEFAULT_REPORT_SENTINEL = "<output>.report.txt"
DefaultHandler = argparse.ArgumentDefaultsHelpFormatter


@dataclass
class OperatorStats:
    face_count_used: int
    face_count_skipped: int
    min_face_area: float
    max_face_area: float
    mean_face_area: float
    min_mass: float
    max_mass: float
    mean_mass: float


@dataclass
class ScaleInfo:
    scale_definition: str
    scale_input_m: float
    total_diffusion_time_m2: float
    equivalent_efold_wavelength_m: float
    equivalent_half_amplitude_wavelength_m: float
    equivalent_gaussian_sigma_m: float
    continuous_reference_attenuation: float
    actual_reference_attenuation_with_nsteps: float


@dataclass
class MeshUnitInfo:
    raw_unit: str
    raw_to_m: float
    raw_geometric_mean_edge: float
    geometric_mean_edge_m: float
    edge_mean_from_header_m: Optional[float]


@dataclass
class DiffusionControl:
    requested_workers: int
    assembly_workers: int
    solve_workers: int
    assembly_chunk_size: int
    chunks: int


def print_progress(i: int, total: int, width: int = 50, suffix: str = "") -> None:
    if total <= 0:
        return
    i = max(0, min(i, total))
    filled = int(round(i / total * width))
    percent = int(round(i / total * 100))
    bar = "[" + "#" * filled + "-" * (width - filled) + "]"
    end = "" if i < total else "\n"
    text = f"\r{bar} {percent}%"
    if suffix:
        text += f" {suffix}"
    print(text, end=end, flush=True)


def read_obj_header_and_edge_mean(obj_path: Path) -> Tuple[List[str], Optional[float]]:
    header_lines: List[str] = []
    edge_mean_km: Optional[float] = None
    with obj_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.startswith("#"):
                break
            stripped = line[1:]
            if stripped.startswith(" "):
                stripped = stripped[1:]
            header_lines.append(stripped.rstrip("\n"))
            m = HEADER_EDGE_MEAN_RE.match(line.rstrip("\n"))
            if m and edge_mean_km is None:
                try:
                    edge_mean_km = float(m.group(1))
                except ValueError:
                    edge_mean_km = None
    return header_lines, edge_mean_km


def write_header_txt(obj_path: Path, header_lines: List[str]) -> Path:
    stem_no_ext = obj_path.with_suffix("")
    header_path = stem_no_ext.parent / (stem_no_ext.name + ".header.txt")
    with header_path.open("w", encoding="utf-8") as f:
        for line in header_lines:
            f.write(line + "\n")
    return header_path


def default_output_path(
    input_obj: Path,
    scale_m: float,
    scale_definition: str,
    preserve_volume: bool = False,
) -> Path:
    stem_no_ext = input_obj.with_suffix("")
    definition_tag = {
        "efold_wavelength": "efold",
        "half_amplitude_wavelength": "halfamp",
        "gaussian_sigma": "sigma",
    }[scale_definition]
    scale_tag = f"{scale_m:g}"
    preserve_tag = "_preserve" if preserve_volume else ""
    return stem_no_ext.parent / f"{stem_no_ext.name}_diffuse_{definition_tag}_{scale_tag}{preserve_tag}.obj"


def default_report_path(output_obj: Path) -> Path:
    return output_obj.with_suffix(".report.txt")


def keep_output_path(final_output_obj: Path) -> Path:
    stem = final_output_obj.stem
    if stem.endswith("_preserve"):
        keep_stem = stem[:-len("_preserve")]
        if not keep_stem:
            keep_stem = stem + "_pre_preserve"
    else:
        keep_stem = stem + "_pre_preserve"
    keep_path = final_output_obj.with_name(keep_stem + final_output_obj.suffix)
    if keep_path == final_output_obj:
        keep_path = final_output_obj.with_name(stem + "_pre_preserve" + final_output_obj.suffix)
    return keep_path


def keep_report_path(final_report_path: Path) -> Path:
    name = final_report_path.name
    if "_preserve.report.txt" in name:
        return final_report_path.with_name(name.replace("_preserve.report.txt", ".report.txt"))
    if name.endswith(".report.txt"):
        return final_report_path.with_name(name[:-len(".report.txt")] + "_pre_preserve.report.txt")
    return final_report_path.with_name(final_report_path.stem + "_pre_preserve" + final_report_path.suffix)


def normalize_output_path(path_like: str | Path) -> Path:
    path = Path(path_like)
    if path.suffix.lower() != ".obj":
        path = Path(str(path) + ".obj")
    return path


def decimal_places_in_obj_number(token: str) -> int:
    token = token.strip()
    if not token:
        return 0
    try:
        normalized = format(Decimal(token), "f")
    except (InvalidOperation, ValueError):
        mantissa = token
        if "e" in mantissa.lower():
            mantissa = re.split(r"[eE]", mantissa, maxsplit=1)[0]
        normalized = mantissa
    if "." not in normalized:
        return 0
    return len(normalized.partition(".")[2])


def detect_input_vertex_decimal_places(obj_path: Path, fallback: int = 15) -> int:
    max_decimals = 0
    found_vertex = False
    with obj_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = VERTEX_LINE_RE.match(line)
            if m is None:
                continue
            found_vertex = True
            for tok in m.groups():
                max_decimals = max(max_decimals, decimal_places_in_obj_number(tok))
    return max_decimals if found_vertex else fallback


def write_obj_preserve_faces(
    out_path: Path,
    vertices: np.ndarray,
    faces: np.ndarray,
    vertex_decimal_places: int,
) -> None:
    total = int(vertices.shape[0] + faces.shape[0])
    vertex_decimal_places = max(0, int(vertex_decimal_places))
    vertex_fmt = f"{{:.{vertex_decimal_places}f}}"
    with out_path.open("w", encoding="utf-8") as f:
        for i, v in enumerate(vertices, start=1):
            x = vertex_fmt.format(float(v[0]))
            y = vertex_fmt.format(float(v[1]))
            z = vertex_fmt.format(float(v[2]))
            f.write(f"v {x} {y} {z}\n")
            print_progress(i, total)
        offset = int(vertices.shape[0])
        for j, tri in enumerate(faces, start=1):
            a, b, c = int(tri[0]), int(tri[1]), int(tri[2])
            f.write(f"f {a+1} {b+1} {c+1}\n")
            print_progress(offset + j, total)


def infer_mesh_unit(
    raw_geometric_mean_edge: float,
    edge_mean_from_header_m: Optional[float],
    requested_unit: str,
) -> MeshUnitInfo:
    if raw_geometric_mean_edge <= 0.0 or not np.isfinite(raw_geometric_mean_edge):
        raise ValueError("raw geometric mean edge length must be positive and finite")

    if requested_unit in {"m", "km"}:
        raw_to_m = 1.0 if requested_unit == "m" else 1000.0
        return MeshUnitInfo(
            raw_unit=requested_unit,
            raw_to_m=raw_to_m,
            raw_geometric_mean_edge=float(raw_geometric_mean_edge),
            geometric_mean_edge_m=float(raw_geometric_mean_edge * raw_to_m),
            edge_mean_from_header_m=edge_mean_from_header_m,
        )

    if edge_mean_from_header_m is None:
        raise ValueError(
            "--mesh_unit auto requires the OBJ header to contain 'Edge Length Mean = ... km', "
            "or specify --mesh_unit explicitly as m or km."
        )

    ratio = edge_mean_from_header_m / float(raw_geometric_mean_edge)
    if 0.5 <= ratio <= 2.0:
        raw_unit = "m"
        raw_to_m = 1.0
    elif 500.0 <= ratio <= 2000.0:
        raw_unit = "km"
        raw_to_m = 1000.0
    else:
        raise ValueError(
            "Could not infer mesh coordinate unit from header/geometry comparison. "
            f"Header mean edge = {edge_mean_from_header_m:.12g} m, "
            f"raw geometric mean edge = {raw_geometric_mean_edge:.12g}, ratio = {ratio:.12g}. "
            "Specify --mesh_unit m or --mesh_unit km explicitly."
        )

    return MeshUnitInfo(
        raw_unit=raw_unit,
        raw_to_m=raw_to_m,
        raw_geometric_mean_edge=float(raw_geometric_mean_edge),
        geometric_mean_edge_m=float(raw_geometric_mean_edge * raw_to_m),
        edge_mean_from_header_m=edge_mean_from_header_m,
    )


def unique_edge_lengths(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    edges = np.vstack((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
    edges = np.sort(edges, axis=1)
    edges = np.unique(edges, axis=0)
    dv = vertices[edges[:, 0]] - vertices[edges[:, 1]]
    return np.linalg.norm(dv, axis=1)


def build_cotangent_stiffness_and_lumped_mass(
    vertices: np.ndarray,
    faces: np.ndarray,
    area_eps: float = 1.0e-30,
) -> Tuple[csc_matrix, np.ndarray, OperatorStats]:
    n_vertices = int(vertices.shape[0])
    rows: List[int] = []
    cols: List[int] = []
    data: List[float] = []
    mass = np.zeros(n_vertices, dtype=np.float64)
    used_areas: List[float] = []
    skipped = 0

    for tri in faces:
        i, j, k = int(tri[0]), int(tri[1]), int(tri[2])
        vi, vj, vk = vertices[i], vertices[j], vertices[k]
        nvec = np.cross(vj - vi, vk - vi)
        twice_area = float(np.linalg.norm(nvec))
        area = 0.5 * twice_area
        if not np.isfinite(area) or area <= area_eps:
            skipped += 1
            continue

        cot_i = float(np.dot(vj - vi, vk - vi) / twice_area)
        cot_j = float(np.dot(vi - vj, vk - vj) / twice_area)
        cot_k = float(np.dot(vi - vk, vj - vk) / twice_area)

        edge_terms = (
            (j, k, 0.5 * cot_i),
            (i, k, 0.5 * cot_j),
            (i, j, 0.5 * cot_k),
        )
        for a, b, w in edge_terms:
            rows.extend((a, a, b, b))
            cols.extend((a, b, a, b))
            data.extend((w, -w, -w, w))

        lump = area / 3.0
        mass[i] += lump
        mass[j] += lump
        mass[k] += lump
        used_areas.append(area)

    if not used_areas:
        raise ValueError("No valid triangles remained after filtering degenerate faces.")

    K = coo_matrix((data, (rows, cols)), shape=(n_vertices, n_vertices), dtype=np.float64)
    K.sum_duplicates()
    K = K.tocsc()

    positive_mass = mass[mass > 0.0]
    if positive_mass.size != mass.size:
        zero_count = int(mass.size - positive_mass.size)
        raise ValueError(
            f"Found {zero_count} vertices with zero lumped mass. "
            "This usually indicates isolated vertices or a severely invalid mesh."
        )

    areas = np.asarray(used_areas, dtype=np.float64)
    stats = OperatorStats(
        face_count_used=int(len(used_areas)),
        face_count_skipped=int(skipped),
        min_face_area=float(areas.min()),
        max_face_area=float(areas.max()),
        mean_face_area=float(areas.mean()),
        min_mass=float(positive_mass.min()),
        max_mass=float(positive_mass.max()),
        mean_mass=float(positive_mass.mean()),
    )
    return K, mass, stats


def scale_to_diffusion_time(scale_m: float, scale_definition: str) -> float:
    if scale_m <= 0.0:
        raise ValueError("scale_m must be positive.")
    if scale_definition == "efold_wavelength":
        return (scale_m / (2.0 * math.pi)) ** 2
    if scale_definition == "half_amplitude_wavelength":
        return math.log(2.0) * (scale_m / (2.0 * math.pi)) ** 2
    if scale_definition == "gaussian_sigma":
        return 0.5 * scale_m**2
    raise ValueError(f"Unknown scale_definition: {scale_definition}")


def diffusion_time_to_equivalents(t_m2: float) -> Tuple[float, float, float]:
    if t_m2 < 0.0:
        raise ValueError("diffusion time must be nonnegative.")
    efold_wavelength = 2.0 * math.pi * math.sqrt(t_m2)
    half_amplitude_wavelength = 2.0 * math.pi * math.sqrt(t_m2 / math.log(2.0))
    gaussian_sigma = math.sqrt(2.0 * t_m2)
    return efold_wavelength, half_amplitude_wavelength, gaussian_sigma


def build_scale_info(scale_m: float, scale_definition: str, nsteps: int) -> ScaleInfo:
    t_total = scale_to_diffusion_time(scale_m, scale_definition)
    efold, halfamp, sigma = diffusion_time_to_equivalents(t_total)

    if scale_definition == "efold_wavelength":
        z_ref = 1.0
        continuous = math.exp(-1.0)
    elif scale_definition == "half_amplitude_wavelength":
        z_ref = math.log(2.0)
        continuous = 0.5
    elif scale_definition == "gaussian_sigma":
        z_ref = None
        continuous = float("nan")
    else:
        raise ValueError(scale_definition)

    actual = float("nan") if z_ref is None else (1.0 + z_ref / float(nsteps)) ** (-float(nsteps))

    return ScaleInfo(
        scale_definition=scale_definition,
        scale_input_m=float(scale_m),
        total_diffusion_time_m2=float(t_total),
        equivalent_efold_wavelength_m=float(efold),
        equivalent_half_amplitude_wavelength_m=float(halfamp),
        equivalent_gaussian_sigma_m=float(sigma),
        continuous_reference_attenuation=float(continuous),
        actual_reference_attenuation_with_nsteps=float(actual),
    )


def resolve_workers(requested_workers: int) -> int:
    if requested_workers == 0:
        return max(1, os.cpu_count() or 1)
    if requested_workers < 0:
        raise ValueError("--workers must be nonnegative")
    return requested_workers


def flatten_scale_args(scale_groups: Optional[Sequence[Sequence[float]]]) -> List[float]:
    if not scale_groups:
        return [150.0]
    out: List[float] = []
    for group in scale_groups:
        out.extend(float(v) for v in group)
    return out


def diffuse_columns_parallel(lu, rhs: np.ndarray, solve_workers: int) -> np.ndarray:
    if solve_workers <= 1:
        return np.column_stack([lu.solve(rhs[:, d]) for d in range(3)])
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=solve_workers) as ex:
        cols = list(ex.map(lambda d: lu.solve(rhs[:, d]), range(3)))
    return np.column_stack(cols)


def _diffuse_vertices_worker(
    conn,
    shm_name: str,
    shape: Tuple[int, int],
    vertices: np.ndarray,
    K: csc_matrix,
    mass: np.ndarray,
    total_diffusion_time_m2: float,
    nsteps: int,
    solve_workers: int,
) -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    shm = None
    try:
        shm = SharedMemory(name=shm_name)
        out = np.ndarray(shape, dtype=np.float64, buffer=shm.buf)

        dt = total_diffusion_time_m2 / float(nsteps)

        conn.send(("stage", "build_mass"))
        M = diags(mass, offsets=0, format="csc")
        conn.send(("stage_done", "build_mass"))

        conn.send(("stage", "build_system"))
        A = (M + dt * K).tocsc()
        conn.send(("stage_done", "build_system"))

        conn.send(("stage", "factorization"))
        lu = splu(A)
        conn.send(("stage_done", "factorization"))

        conn.send(("stage", "solve_steps", nsteps, solve_workers))
        rhs_scale = mass[:, None]
        X = np.array(vertices, dtype=np.float64, copy=True)
        for s in range(nsteps):
            t0 = time.time()
            rhs = rhs_scale * X
            X = diffuse_columns_parallel(lu, rhs, solve_workers)
            conn.send(("progress", s + 1, nsteps, time.time() - t0))

        out[:] = X
        conn.send(("done",))
    except BaseException as exc:
        try:
            conn.send(("error", repr(exc), traceback.format_exc()))
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass
        if shm is not None:
            try:
                shm.close()
            except Exception:
                pass


def diffuse_vertices_implicit(
    vertices: np.ndarray,
    K: csc_matrix,
    mass: np.ndarray,
    total_diffusion_time_m2: float,
    nsteps: int,
    solve_workers: int,
) -> np.ndarray:
    if nsteps <= 0:
        raise ValueError("nsteps must be a positive integer.")
    if total_diffusion_time_m2 < 0.0:
        raise ValueError("total_diffusion_time_m2 must be nonnegative.")
    if total_diffusion_time_m2 == 0.0:
        return np.array(vertices, copy=True)

    start_methods = mp.get_all_start_methods()
    ctx = mp.get_context("fork" if "fork" in start_methods else start_methods[0])
    parent_conn, child_conn = ctx.Pipe(duplex=False)
    shm = SharedMemory(create=True, size=int(vertices.nbytes))
    proc = ctx.Process(
        target=_diffuse_vertices_worker,
        args=(child_conn, shm.name, tuple(vertices.shape), vertices, K, mass, total_diffusion_time_m2, nsteps, solve_workers),
        daemon=True,
    )

    cancel_requested = False
    sigint_count = 0
    previous_handler = signal.getsignal(signal.SIGINT)

    def _terminate_worker(force: bool = False) -> None:
        if not proc.is_alive():
            return
        try:
            if force and hasattr(proc, "kill"):
                proc.kill()
            else:
                proc.terminate()
        except Exception:
            pass

    def _handle_sigint(signum, frame):
        nonlocal cancel_requested, sigint_count
        sigint_count += 1
        cancel_requested = True
        if sigint_count == 1:
            print("\n[INFO] Ctrl+C received. Cancelling diffusion...", flush=True)
            _terminate_worker(force=False)
        else:
            print("\n[INFO] Second Ctrl+C received. Forcing immediate exit.", flush=True)
            _terminate_worker(force=True)
            raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _handle_sigint)
    if hasattr(signal, "siginterrupt"):
        try:
            signal.siginterrupt(signal.SIGINT, True)
        except Exception:
            pass

    last_stage: Optional[str] = None
    stage_start_time: Optional[float] = None
    last_heartbeat = 0.0
    factorization_line_active = False
    done = False

    try:
        proc.start()
        child_conn.close()
        while True:
            if cancel_requested:
                _terminate_worker(force=False)
            if parent_conn.poll(0.1):
                msg = parent_conn.recv()
                tag = msg[0]
                if tag == "stage":
                    last_stage = str(msg[1])
                    stage_start_time = time.time()
                    last_heartbeat = stage_start_time
                    if last_stage == "build_mass":
                        print("[INFO] diffusion substage 1/4: building diagonal lumped-mass matrix...")
                    elif last_stage == "build_system":
                        print("[INFO] diffusion substage 2/4: building implicit system matrix A = M + dt*K...")
                    elif last_stage == "factorization":
                        factorization_line_active = True
                        print(
                            "[INFO] diffusion substage 3/4: LU factorization started... elapsed=0.0 s",
                            end="",
                            flush=True,
                        )
                    elif last_stage == "solve_steps":
                        print(
                            f"[INFO] diffusion substage 4/4: implicit Euler steps started "
                            f"(nsteps={int(msg[2])}, solve_workers={int(msg[3])})"
                        )
                elif tag == "stage_done":
                    elapsed = 0.0 if stage_start_time is None else time.time() - stage_start_time
                    stage_name = str(msg[1])
                    if stage_name == "build_mass":
                        print(f"[TIME] diffusion substage 1/4 = {elapsed:.2f} s")
                    elif stage_name == "build_system":
                        print(f"[TIME] diffusion substage 2/4 = {elapsed:.2f} s")
                    elif stage_name == "factorization":
                        if factorization_line_active:
                            print(
                                f"\r[INFO] diffusion substage 3/4: LU factorization started... elapsed={elapsed:.1f} s"
                            )
                            factorization_line_active = False
                        print(f"[TIME] diffusion substage 3/4 = {elapsed:.2f} s")
                    last_stage = None
                    stage_start_time = None
                    last_heartbeat = 0.0
                elif tag == "progress":
                    completed, total, step_elapsed = int(msg[1]), int(msg[2]), float(msg[3])
                    print_progress(completed, total, suffix=f"({completed}/{total} steps)")
                    print(
                        f"[INFO] diffusion step {completed}/{total} finished "
                        f"(step={step_elapsed:.2f} s)",
                        flush=True,
                    )
                elif tag == "done":
                    done = True
                elif tag == "error":
                    if factorization_line_active:
                        print()
                        factorization_line_active = False
                    raise RuntimeError(f"Diffusion worker failed: {msg[1]}\n{msg[2]}")
            else:
                if (
                    last_stage == "factorization"
                    and stage_start_time is not None
                    and time.time() - last_heartbeat >= 5.0
                ):
                    elapsed = time.time() - stage_start_time
                    print(
                        f"\r[INFO] diffusion substage 3/4: LU factorization started... elapsed={elapsed:.1f} s",
                        end="",
                        flush=True,
                    )
                    last_heartbeat = time.time()

            if cancel_requested:
                proc.join(timeout=0.2)
                if not proc.is_alive():
                    if factorization_line_active:
                        print()
                        factorization_line_active = False
                    raise KeyboardInterrupt
            if done:
                break
            if not proc.is_alive() and not parent_conn.poll():
                if cancel_requested:
                    if factorization_line_active:
                        print()
                        factorization_line_active = False
                    raise KeyboardInterrupt
                if proc.exitcode == 0:
                    break
                raise RuntimeError(f"Diffusion worker exited unexpectedly with code {proc.exitcode}.")

        proc.join()
        out = np.ndarray(vertices.shape, dtype=np.float64, buffer=shm.buf).copy()
        return out
    finally:
        if factorization_line_active:
            print()
        try:
            if previous_handler is not None:
                signal.signal(signal.SIGINT, previous_handler)
            else:
                signal.signal(signal.SIGINT, signal.default_int_handler)
        except Exception:
            signal.signal(signal.SIGINT, signal.default_int_handler)
        try:
            parent_conn.close()
        except Exception:
            pass
        if proc.is_alive():
            _terminate_worker(force=True)
            proc.join(timeout=1.0)
        try:
            shm.close()
        finally:
            shm.unlink()


def write_report(
    report_path: Path,
    input_obj: Path,
    output_obj: Path,
    header_txt: Path,
    vertex_count: int,
    face_count: int,
    unit_info: MeshUnitInfo,
    scale: ScaleInfo,
    nsteps: int,
    volume_before: Optional[float],
    volume_after: Optional[float],
    volume_scale_factor: Optional[float],
    op_stats: OperatorStats,
    kept_pre_preserve_obj: Optional[Path] = None,
    preserve_volume_applied: bool = False,
) -> None:
    with report_path.open("w", encoding="utf-8") as f:
        f.write("Physical diffusion smoothing report\n")
        f.write("==================================\n\n")
        f.write(f"Input OBJ: {input_obj}\n")
        f.write(f"Output OBJ: {output_obj}\n")
        if kept_pre_preserve_obj is not None:
            f.write(f"Kept pre-preserve OBJ: {kept_pre_preserve_obj}\n")
        f.write(f"Saved header text: {header_txt}\n\n")

        f.write("Mesh summary\n")
        f.write("------------\n")
        f.write(f"Vertices: {vertex_count}\n")
        f.write(f"Faces: {face_count}\n")
        if unit_info.edge_mean_from_header_m is not None:
            f.write(f"Header edge-length mean: {unit_info.edge_mean_from_header_m:.12g} m\n")
        else:
            f.write("Header edge-length mean: not present\n")
        f.write(f"Raw coordinate unit inferred/requested: {unit_info.raw_unit}\n")
        f.write(f"Raw geometric mean unique-edge length: {unit_info.raw_geometric_mean_edge:.12g} {unit_info.raw_unit}\n")
        f.write(f"Geometric mean unique-edge length after unit conversion: {unit_info.geometric_mean_edge_m:.12g} m\n\n")

        f.write("Scale definition\n")
        f.write("----------------\n")
        f.write(f"scale_definition: {scale.scale_definition}\n")
        f.write(f"scale_input_m: {scale.scale_input_m:.12g}\n")
        f.write(f"total_diffusion_time_m2: {scale.total_diffusion_time_m2:.12g}\n")
        f.write(f"equivalent_efold_wavelength_m: {scale.equivalent_efold_wavelength_m:.12g}\n")
        f.write(f"equivalent_half_amplitude_wavelength_m: {scale.equivalent_half_amplitude_wavelength_m:.12g}\n")
        f.write(f"equivalent_gaussian_sigma_m: {scale.equivalent_gaussian_sigma_m:.12g}\n")
        f.write(f"nsteps: {nsteps}\n")
        if math.isfinite(scale.continuous_reference_attenuation):
            f.write(f"continuous_reference_attenuation: {scale.continuous_reference_attenuation:.12g}\n")
            f.write(f"actual_reference_attenuation_with_nsteps: {scale.actual_reference_attenuation_with_nsteps:.12g}\n")
        else:
            f.write("continuous_reference_attenuation: n/a for gaussian_sigma\n")
            f.write("actual_reference_attenuation_with_nsteps: n/a for gaussian_sigma\n")
        f.write("\n")

        f.write("Operator summary\n")
        f.write("----------------\n")
        f.write(f"Used faces in operator assembly: {op_stats.face_count_used}\n")
        f.write(f"Skipped degenerate faces: {op_stats.face_count_skipped}\n")
        f.write(
            f"Face area min/mean/max [m^2]: {op_stats.min_face_area:.12g} / {op_stats.mean_face_area:.12g} / {op_stats.max_face_area:.12g}\n"
        )
        f.write(
            f"Lumped mass min/mean/max [m^2]: {op_stats.min_mass:.12g} / {op_stats.mean_mass:.12g} / {op_stats.max_mass:.12g}\n\n"
        )

        f.write("Volume summary\n")
        f.write("--------------\n")
        if volume_before is not None:
            f.write(f"volume_before [m^3]: {volume_before:.12g}\n")
        else:
            f.write("volume_before [m^3]: unavailable\n")
        if volume_after is not None:
            f.write(f"volume_after [m^3]: {volume_after:.12g}\n")
        else:
            f.write("volume_after [m^3]: unavailable\n")
        if preserve_volume_applied:
            if volume_scale_factor is not None:
                f.write(f"volume_preserving_scale_factor: {volume_scale_factor:.12g}\n")
            else:
                f.write("volume_preserving_scale_factor: requested but unavailable\n")
        else:
            f.write("volume_preserving_scale_factor: not applied\n")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=(
            "Smooth a triangular OBJ mesh by implicit diffusion using a cotangent "
            "Laplace-Beltrami operator and a lumped mass matrix, while preserving "
            "face connectivity and face ordering in the written OBJ."
        ),
        formatter_class=DefaultHandler,
    )
    ap.add_argument("input_obj", help="Input triangular OBJ file.")
    ap.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_SENTINEL,
        help=(
            "Optional output OBJ path. Default: <input_without_ext>_diffuse_<definition>_<scale>.obj "
            "and, with --preserve_volume, <input_without_ext>_diffuse_<definition>_<scale>_preserve.obj"
        ),
    )
    ap.add_argument(
        "-L",
        "--scale_m",
        type=float,
        nargs="+",
        action="append",
        default=None,
        help=(
            "Physical smoothing scale in meters. Interpretation depends on --scale_definition. "
            "Specify one or more values, for example '-L 80 100 125' or '-L 100 -L 200'."
        ),
    )
    ap.add_argument(
        "--scale_definition",
        choices=["efold_wavelength", "half_amplitude_wavelength", "gaussian_sigma"],
        default="efold_wavelength",
        help=(
            "How to interpret -L/--scale_m. For studies of smoothing-vs-scale, "
            "efold_wavelength is recommended."
        ),
    )
    ap.add_argument(
        "--mesh_unit",
        choices=["auto", "m", "km"],
        default="auto",
        help=(
            "Unit of OBJ vertex coordinates. auto compares the raw mesh edge length "
            "against the header edge-length mean. Many planetary shape-model OBJs store "
            "coordinates in km. Use --mesh_unit km to force that."
        ),
    )
    ap.add_argument(
        "--nsteps",
        type=int,
        default=20,
        help=(
            "Number of implicit Euler steps used to approximate total diffusion time. "
            "Higher values better approximate exact heat diffusion."
        ),
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=0,
        help=(
            "Parallel worker count. 0 uses all available logical CPUs. Operator assembly uses up to this "
            "many worker threads, while the implicit solve uses up to min(3, workers)."
        ),
    )
    ap.add_argument(
        "--assembly_chunk_size",
        type=int,
        default=50000,
        help=(
            "Number of faces per chunk during operator assembly. Kept for CLI compatibility."
        ),
    )
    ap.add_argument(
        "--preserve_volume",
        action="store_true",
        help="Uniformly rescale the smoothed mesh to match the original enclosed volume.",
    )
    ap.add_argument(
        "--keep",
        action="store_true",
        help="When used with --preserve_volume, also keep the pre-preserve smoothed OBJ and its report.",
    )
    ap.add_argument(
        "--no_face_check",
        action="store_true",
        help="Disable strict face-array equality check before writing output.",
    )
    ap.add_argument(
        "--report",
        default=DEFAULT_REPORT_SENTINEL,
        help=(
            "Optional path for a text report. Default: <output>.report.txt"
        ),
    )
    ap.add_argument(
        "--prec",
        type=int,
        default=None,
        help="Decimal places for written vertex coordinates. Default: match the input OBJ vertex precision.",
    )
    return ap


def load_mesh_with_logs(in_path: Path) -> tuple[list[str], Path, Optional[float], int, trimesh.Trimesh, np.ndarray, np.ndarray, float]:
    print(f"[INFO] input path resolved = {in_path}")

    t0 = time.time()
    print("[INFO] reading OBJ header comments and edge-length metadata...")
    header_lines, edge_mean_km = read_obj_header_and_edge_mean(in_path)
    print(f"[TIME] header read = {time.time() - t0:.2f} s")

    t0 = time.time()
    print("[INFO] writing extracted header text sidecar...")
    header_txt = write_header_txt(in_path, header_lines)
    print(f"[TIME] header sidecar write = {time.time() - t0:.2f} s")

    edge_mean_from_header_m = None if edge_mean_km is None else 1000.0 * edge_mean_km

    t0 = time.time()
    print("[INFO] scanning input vertex decimal precision...")
    input_vertex_decimal_places = detect_input_vertex_decimal_places(in_path)
    print(f"[TIME] precision scan = {time.time() - t0:.2f} s")

    t0 = time.time()
    print("[INFO] loading OBJ mesh geometry with trimesh (vertices / faces)...")
    mesh = trimesh.load(in_path, process=False)
    print(f"[TIME] trimesh load = {time.time() - t0:.2f} s")
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError("Loaded object is not a single Trimesh. Provide a single-mesh OBJ.")

    t0 = time.time()
    print("[INFO] converting loaded mesh buffers to NumPy arrays...")
    vertices_raw = np.asarray(mesh.vertices, dtype=np.float64)
    faces0 = np.array(mesh.faces, copy=True)
    print(f"[TIME] NumPy conversion = {time.time() - t0:.2f} s")
    if faces0.ndim != 2 or faces0.shape[1] != 3:
        raise ValueError("Input mesh must be triangular.")

    t0 = time.time()
    print("[INFO] computing unique edge lengths from triangle connectivity...")
    raw_geometric_edge_lengths = unique_edge_lengths(vertices_raw, faces0)
    raw_geometric_mean_edge = float(raw_geometric_edge_lengths.mean())
    print(f"[TIME] unique-edge statistics = {time.time() - t0:.2f} s")

    return (
        header_lines,
        header_txt,
        edge_mean_from_header_m,
        input_vertex_decimal_places,
        mesh,
        vertices_raw,
        faces0,
        raw_geometric_mean_edge,
    )


def summarize_workers(args, face_count: int) -> DiffusionControl:
    requested = int(args.workers)
    resolved = resolve_workers(requested)
    solve_workers = min(3, resolved)
    chunk_size = max(1, int(args.assembly_chunk_size))
    chunks = max(1, math.ceil(int(face_count) / chunk_size))
    return DiffusionControl(
        requested_workers=requested,
        assembly_workers=resolved,
        solve_workers=solve_workers,
        assembly_chunk_size=chunk_size,
        chunks=chunks,
    )


def run_single_scale(
    args,
    in_path: Path,
    header_txt: Path,
    edge_mean_from_header_m: Optional[float],
    input_vertex_decimal_places: int,
    vertices_raw: np.ndarray,
    faces0: np.ndarray,
    raw_geometric_mean_edge: float,
    scale_m: float,
    multiple_scales: bool,
    scale_index: int,
    scale_count: int,
) -> None:
    unit_info = infer_mesh_unit(
        raw_geometric_mean_edge=raw_geometric_mean_edge,
        edge_mean_from_header_m=edge_mean_from_header_m,
        requested_unit=args.mesh_unit,
    )
    vertices0 = vertices_raw * unit_info.raw_to_m
    scale = build_scale_info(scale_m, args.scale_definition, args.nsteps)
    control = summarize_workers(args, int(faces0.shape[0]))

    if args.output == DEFAULT_OUTPUT_SENTINEL:
        out_path = default_output_path(in_path, scale_m, args.scale_definition, preserve_volume=args.preserve_volume)
        pre_preserve_keep_path = default_output_path(in_path, scale_m, args.scale_definition, preserve_volume=False)
    else:
        base_output = normalize_output_path(args.output)
        if multiple_scales:
            scale_tag = f"{scale_m:g}"
            out_path = base_output.with_name(f"{base_output.stem}_{scale_tag}{base_output.suffix}")
        else:
            out_path = base_output
        pre_preserve_keep_path = keep_output_path(out_path)

    if args.report == DEFAULT_REPORT_SENTINEL:
        report_path = default_report_path(out_path)
        pre_preserve_keep_report = default_report_path(pre_preserve_keep_path)
    else:
        report_path = Path(args.report)
        if multiple_scales:
            scale_tag = f"{scale_m:g}"
            report_path = report_path.with_name(f"{report_path.stem}_{scale_tag}{report_path.suffix}")
        pre_preserve_keep_report = keep_report_path(report_path)

    keep_pre_preserve_obj = args.preserve_volume and args.keep
    kept_pre_preserve_obj = pre_preserve_keep_path if keep_pre_preserve_obj else None
    kept_pre_preserve_report = pre_preserve_keep_report if keep_pre_preserve_obj else None

    vertex_decimal_places = input_vertex_decimal_places if args.prec is None else int(args.prec)

    if multiple_scales:
        print(f"[INFO] run {scale_index}/{scale_count}: scale_m = {scale_m:g}")
    print(
        f"[INFO] parallel workers: requested={control.requested_workers}, "
        f"assembly={control.assembly_workers}, solve={control.solve_workers}, "
        f"assembly_chunk_size={control.assembly_chunk_size}, chunks={control.chunks}"
    )
    if math.isfinite(scale.actual_reference_attenuation_with_nsteps):
        print(
            "[INFO] actual reference attenuation with nsteps = "
            f"{scale.actual_reference_attenuation_with_nsteps:.6f}"
        )
    print(f"[INFO] output = {out_path}")
    print(f"[INFO] report = {report_path}")
    if kept_pre_preserve_obj is not None:
        print(f"[INFO] keep pre-preserve OBJ = {kept_pre_preserve_obj}")
        print(f"[INFO] keep pre-preserve report = {kept_pre_preserve_report}")
    print(f"[INFO] vertex decimal places = {vertex_decimal_places}")
    print("[INFO] assembling cotangent stiffness matrix and lumped mass matrix...")

    t0 = time.time()
    K, mass, op_stats = build_cotangent_stiffness_and_lumped_mass(vertices0, faces0)
    print_progress(control.chunks, control.chunks)
    print(f"[TIME] operator assembly = {time.time() - t0:.2f} s")

    volume_before = None
    try:
        volume_before = float(abs(trimesh.Trimesh(vertices=vertices0, faces=faces0, process=False).volume))
    except Exception:
        volume_before = None

    print("[INFO] diffusing vertex coordinates...")
    vertices1 = diffuse_vertices_implicit(
        vertices=vertices0,
        K=K,
        mass=mass,
        total_diffusion_time_m2=scale.total_diffusion_time_m2,
        nsteps=args.nsteps,
        solve_workers=control.solve_workers,
    )

    pre_preserve_vertices_out_raw: Optional[np.ndarray] = None
    if kept_pre_preserve_obj is not None:
        pre_preserve_vertices_out_raw = np.asarray(vertices1) / unit_info.raw_to_m

    mesh_out = trimesh.Trimesh(vertices=vertices1, faces=faces0, process=False)
    if not args.no_face_check:
        if mesh_out.faces.shape != faces0.shape or not np.array_equal(mesh_out.faces, faces0):
            raise RuntimeError(
                "Face connectivity or ordering changed during processing. "
                "Facet IDs are not preserved. Aborting."
            )

    volume_after = None
    try:
        volume_after = float(abs(mesh_out.volume))
    except Exception:
        volume_after = None

    pre_preserve_volume_after = volume_after

    volume_scale_factor = None
    if args.preserve_volume and volume_before and volume_before > 0.0 and volume_after and volume_after > 0.0:
        volume_scale_factor = float((volume_before / volume_after) ** (1.0 / 3.0))
        print(f"[INFO] applied uniform volume-preserving scale factor s = {volume_scale_factor:.10f}")

        if kept_pre_preserve_obj is not None and pre_preserve_vertices_out_raw is not None:
            print(f"[INFO] writing kept pre-preserve OBJ = {kept_pre_preserve_obj}")
            write_obj_preserve_faces(kept_pre_preserve_obj, pre_preserve_vertices_out_raw, faces0, vertex_decimal_places)
            print(f"[INFO] writing kept pre-preserve report = {kept_pre_preserve_report}")
            write_report(
                report_path=kept_pre_preserve_report,
                input_obj=in_path,
                output_obj=kept_pre_preserve_obj,
                header_txt=header_txt,
                vertex_count=int(vertices0.shape[0]),
                face_count=int(faces0.shape[0]),
                unit_info=unit_info,
                scale=scale,
                nsteps=int(args.nsteps),
                volume_before=volume_before,
                volume_after=pre_preserve_volume_after,
                volume_scale_factor=None,
                op_stats=op_stats,
                preserve_volume_applied=False,
            )

        mesh_out.apply_scale(volume_scale_factor)
        vertices1 = np.asarray(mesh_out.vertices)
        try:
            volume_after = float(abs(mesh_out.volume))
        except Exception:
            pass

    vertices_out_raw = np.asarray(vertices1) / unit_info.raw_to_m
    print(f"[INFO] writing output OBJ = {out_path}")
    write_obj_preserve_faces(out_path, vertices_out_raw, faces0, vertex_decimal_places)

    print(f"[INFO] writing report = {report_path}")
    write_report(
        report_path=report_path,
        input_obj=in_path,
        output_obj=out_path,
        header_txt=header_txt,
        vertex_count=int(vertices0.shape[0]),
        face_count=int(faces0.shape[0]),
        unit_info=unit_info,
        scale=scale,
        nsteps=int(args.nsteps),
        volume_before=volume_before,
        volume_after=volume_after,
        volume_scale_factor=volume_scale_factor,
        op_stats=op_stats,
        kept_pre_preserve_obj=kept_pre_preserve_obj,
        preserve_volume_applied=bool(args.preserve_volume),
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    in_path = Path(args.input_obj)
    if not in_path.exists():
        raise FileNotFoundError(in_path)

    (
        _header_lines,
        header_txt,
        edge_mean_from_header_m,
        input_vertex_decimal_places,
        _mesh,
        vertices_raw,
        faces0,
        raw_geometric_mean_edge,
    ) = load_mesh_with_logs(in_path)

    scale_values = flatten_scale_args(args.scale_m)
    multiple_scales = len(scale_values) > 1

    for idx, scale_m in enumerate(scale_values, start=1):
        run_single_scale(
            args=args,
            in_path=in_path,
            header_txt=header_txt,
            edge_mean_from_header_m=edge_mean_from_header_m,
            input_vertex_decimal_places=input_vertex_decimal_places,
            vertices_raw=vertices_raw,
            faces0=faces0,
            raw_geometric_mean_edge=raw_geometric_mean_edge,
            scale_m=scale_m,
            multiple_scales=multiple_scales,
            scale_index=idx,
            scale_count=len(scale_values),
        )

    print("[DONE] wrote smoothed OBJ, header text, and method report.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[CANCELLED] interrupted by user.", file=sys.stderr)
        sys.exit(130)
