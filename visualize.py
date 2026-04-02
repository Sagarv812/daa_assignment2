#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path
from typing import List, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PolygonPatch


Point = Tuple[float, float]
Triangle = Tuple[Point, Point, Point]
Polygon = List[Point]
Case = Tuple[Polygon, List[Polygon]]


def parse_input_file(path: Path) -> List[Case]:
    tokens = path.read_text().split()
    pos = 0

    def next_token() -> str:
        nonlocal pos
        token = tokens[pos]
        pos += 1
        return token

    cases: List[Case] = []
    total_cases = int(next_token())
    for _ in range(total_cases):
        outer_count = int(next_token())
        outer: Polygon = []
        for _ in range(outer_count):
            outer.append((float(next_token()), float(next_token())))

        hole_count = int(next_token())
        holes: List[Polygon] = []
        for _ in range(hole_count):
            hole_vertices = int(next_token())
            hole: Polygon = []
            for _ in range(hole_vertices):
                hole.append((float(next_token()), float(next_token())))
            holes.append(hole)

        cases.append((outer, holes))

    return cases


def parse_program_output(output: str, case_count: int) -> List[List[Triangle]]:
    tokens = output.split()
    pos = 0
    all_triangles: List[List[Triangle]] = []

    for _ in range(case_count):
        triangle_count = int(tokens[pos])
        pos += 1
        triangles: List[Triangle] = []
        for _ in range(triangle_count):
            triangle = (
                (float(tokens[pos]), float(tokens[pos + 1])),
                (float(tokens[pos + 2]), float(tokens[pos + 3])),
                (float(tokens[pos + 4]), float(tokens[pos + 5])),
            )
            pos += 6
            triangles.append(triangle)
        all_triangles.append(triangles)

    return all_triangles


def run_solver(repo_root: Path, input_path: Path, binary: str) -> str:
    subprocess.run(
        ["make", "-C", str(repo_root)],
        text=True,
        capture_output=True,
        check=True,
    )

    result = subprocess.run(
        [str(repo_root / binary)],
        input=input_path.read_text(),
        text=True,
        capture_output=True,
        check=True,
        cwd=repo_root,
    )
    return result.stdout


def load_program_output(repo_root: Path, input_path: Path, binary: str, output_path: str) -> str:
    if output_path:
        resolved_output = (repo_root / output_path).resolve() if not Path(output_path).is_absolute() else Path(output_path)
        return resolved_output.read_text()

    return run_solver(repo_root, input_path, binary)


def add_polygon_outline(ax, polygon: Sequence[Point], facecolor: str, edgecolor: str, linewidth: float) -> None:
    patch = PolygonPatch(
        polygon,
        closed=True,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        joinstyle="round",
    )
    ax.add_patch(patch)


def add_triangle_overlays(ax, triangles: Sequence[Triangle]) -> None:
    cmap = plt.get_cmap("tab20")
    for idx, triangle in enumerate(triangles):
        color = cmap(idx % 20)
        patch = PolygonPatch(
            triangle,
            closed=True,
            facecolor=color,
            edgecolor="#2b2b2b",
            linewidth=1.4,
            alpha=0.35,
            joinstyle="round",
        )
        ax.add_patch(patch)


def add_vertices(ax, polygons: Sequence[Sequence[Point]]) -> None:
    for polygon in polygons:
        xs = [x for x, _ in polygon]
        ys = [y for _, y in polygon]
        ax.scatter(xs, ys, c="#1b1b1b", s=18, zorder=5)


def configure_axes(ax, outer: Polygon, holes: Sequence[Polygon], triangles: Sequence[Triangle], title: str) -> None:
    xs = [x for x, _ in outer]
    ys = [y for _, y in outer]

    for hole in holes:
        xs.extend(x for x, _ in hole)
        ys.extend(y for _, y in hole)

    for triangle in triangles:
        for x, y in triangle:
            xs.append(x)
            ys.append(y)

    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)

    span = max(max_x - min_x, max_y - min_y, 1.0)
    margin = 0.08 * span

    ax.set_xlim(min_x - margin, max_x + margin)
    ax.set_ylim(min_y - margin, max_y + margin)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.35)


def save_case_plot(output_path: Path, case_index: int, outer: Polygon, holes: Sequence[Polygon], triangles: Sequence[Triangle]) -> None:
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#f8f5ef")
    ax.set_facecolor("#fcfaf5")

    add_polygon_outline(ax, outer, facecolor="#dfe8d5", edgecolor="#1f1f1f", linewidth=2.5)
    add_triangle_overlays(ax, triangles)

    for hole in holes:
        add_polygon_outline(ax, hole, facecolor="#ffffff", edgecolor="#1f1f1f", linewidth=2.0)

    add_polygon_outline(ax, outer, facecolor="none", edgecolor="#1f1f1f", linewidth=2.5)
    add_vertices(ax, [outer, *holes])
    configure_axes(ax, outer, holes, triangles, f"Case {case_index}: triangles={len(triangles)}")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate matplotlib plots for triangulated gallery inputs.")
    parser.add_argument("input", help="Path to an assignment-format input file.")
    parser.add_argument(
        "--output-dir",
        default="plots",
        help="Directory where plot files will be written.",
    )
    parser.add_argument(
        "--binary",
        default="build/art_gallery",
        help="Program to run relative to the repo root. Default: build/art_gallery",
    )
    parser.add_argument(
        "--solver-output",
        default="",
        help="Optional path to a file containing precomputed solver output.",
    )
    parser.add_argument(
        "--format",
        default="png",
        choices=["png", "pdf", "svg"],
        help="Output file format for plots. Default: png",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    input_path = (repo_root / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)
    output_dir = (repo_root / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cases = parse_input_file(input_path)
    program_output = load_program_output(repo_root, input_path, args.binary, args.solver_output)
    triangles_per_case = parse_program_output(program_output, len(cases))

    stem = input_path.stem
    for idx, ((outer, holes), triangles) in enumerate(zip(cases, triangles_per_case), start=1):
        output_path = output_dir / f"{stem}_case{idx}.{args.format}"
        save_case_plot(output_path, idx, outer, holes, triangles)
        print(output_path)


if __name__ == "__main__":
    main()
