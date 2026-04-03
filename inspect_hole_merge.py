#!/usr/bin/env python3

import argparse
import math
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")


Point = Tuple[float, float]
Polygon = List[Point]
CaseInput = Tuple[Polygon, List[Polygon]]


@dataclass
class EdgeRecord:
    edge_id: int
    origin: int
    dest: int
    next_edge: int
    prev_edge: int
    twin: int
    is_bridge: bool


@dataclass
class MergeCaseDump:
    case_index: int
    summary: Dict[str, int] = field(default_factory=dict)
    sources: List[Tuple[str, int, int]] = field(default_factory=list)
    vertices: Dict[int, Point] = field(default_factory=dict)
    edges: Dict[int, EdgeRecord] = field(default_factory=dict)
    boundary_order: List[int] = field(default_factory=list)
    bridge_pairs: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class MergeAnalysis:
    cycle_count: int
    boundary_cycle_length: int
    detached_sources: List[Tuple[str, int, int, int]]
    next_prev_issues: List[str]
    twin_issues: List[str]
    proper_crossings: List[Tuple[int, int]]

    @property
    def is_valid(self) -> bool:
        return (
            self.cycle_count == 1
            and not self.detached_sources
            and not self.next_prev_issues
            and not self.twin_issues
            and not self.proper_crossings
        )


def parse_input_file(path: Path) -> List[CaseInput]:
    tokens = path.read_text().split()
    pos = 0

    def next_token() -> str:
        nonlocal pos
        token = tokens[pos]
        pos += 1
        return token

    cases: List[CaseInput] = []
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


def run_solver_with_dump(input_path: Path, solver_path: Path, dump_path: Path) -> None:
    env = os.environ.copy()
    env["ART_GALLERY_MERGE_DEBUG"] = "1"
    env["ART_GALLERY_MERGE_DEBUG_FILE"] = str(dump_path)

    with input_path.open("rb") as handle:
        completed = subprocess.run(
            [str(solver_path)],
            stdin=handle,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

    if completed.returncode != 0:
        sys.stderr.write(completed.stderr.decode("utf-8", errors="replace"))
        raise RuntimeError(f"solver exited with code {completed.returncode}")


def parse_dump_file(path: Path) -> List[MergeCaseDump]:
    cases: List[MergeCaseDump] = []
    current: Optional[MergeCaseDump] = None

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split()
        tag = parts[0]
        if tag == "MERGE_DUMP_BEGIN":
            current = MergeCaseDump(case_index=int(parts[1]))
            continue
        if tag == "MERGE_DUMP_END":
            if current is None:
                raise ValueError("unexpected MERGE_DUMP_END")
            cases.append(current)
            current = None
            continue

        if current is None:
            raise ValueError(f"content outside merge dump block: {line}")

        if tag == "SUMMARY":
            for token in parts[1:]:
                key, value = token.split("=", 1)
                current.summary[key] = int(value)
        elif tag == "SOURCE":
            current.sources.append((parts[1], int(parts[2]), int(parts[3])))
        elif tag == "VERTEX":
            current.vertices[int(parts[1])] = (float(parts[2]), float(parts[3]))
        elif tag == "EDGE":
            edge_id = int(parts[1])
            current.edges[edge_id] = EdgeRecord(
                edge_id=edge_id,
                origin=int(parts[2]),
                dest=int(parts[3]),
                next_edge=int(parts[4]),
                prev_edge=int(parts[5]),
                twin=int(parts[6]),
                is_bridge=parts[7] == "1",
            )
        elif tag == "BOUNDARY_EDGE":
            current.boundary_order.append(int(parts[2]))
        elif tag == "BRIDGE_PAIR":
            current.bridge_pairs.append((int(parts[1]), int(parts[2])))
        else:
            raise ValueError(f"unknown dump tag: {tag}")

    return cases


def follow_cycle(edges: Dict[int, EdgeRecord], start_edge: int) -> List[int]:
    order: List[int] = []
    visited: Dict[int, int] = {}
    curr = start_edge
    while curr != -1 and curr not in visited:
        visited[curr] = len(order)
        order.append(curr)
        curr = edges[curr].next_edge

    if curr in visited:
        return order[visited[curr]:]
    return order


def compute_cycles(case: MergeCaseDump) -> List[List[int]]:
    cycles: List[List[int]] = []
    seen: set[int] = set()
    for edge_id in sorted(case.edges):
        if edge_id in seen:
            continue
        cycle = follow_cycle(case.edges, edge_id)
        cycles.append(cycle)
        seen.update(cycle)
    return cycles


def orientation(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def proper_intersection(a: Point, b: Point, c: Point, d: Point) -> bool:
    eps = 1e-9
    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)
    return (o1 > eps and o2 < -eps or o1 < -eps and o2 > eps) and (
        o3 > eps and o4 < -eps or o3 < -eps and o4 > eps
    )


def analyze_case(case: MergeCaseDump) -> MergeAnalysis:
    next_prev_issues: List[str] = []
    twin_issues: List[str] = []
    detached_sources: List[Tuple[str, int, int, int]] = []
    proper_crossings: List[Tuple[int, int]] = []

    for edge in case.edges.values():
        if edge.next_edge not in case.edges:
            next_prev_issues.append(f"edge {edge.edge_id} has missing next edge {edge.next_edge}")
        elif case.edges[edge.next_edge].prev_edge != edge.edge_id:
            next_prev_issues.append(
                f"edge {edge.edge_id} -> next {edge.next_edge}, but prev(next)={case.edges[edge.next_edge].prev_edge}"
            )

        if edge.prev_edge not in case.edges:
            next_prev_issues.append(f"edge {edge.edge_id} has missing prev edge {edge.prev_edge}")
        elif case.edges[edge.prev_edge].next_edge != edge.edge_id:
            next_prev_issues.append(
                f"edge {edge.edge_id} -> prev {edge.prev_edge}, but next(prev)={case.edges[edge.prev_edge].next_edge}"
            )

        if edge.twin == -1:
            continue

        if edge.twin not in case.edges:
            twin_issues.append(f"edge {edge.edge_id} has missing twin {edge.twin}")
            continue

        twin = case.edges[edge.twin]
        if twin.twin != edge.edge_id:
            twin_issues.append(f"edge {edge.edge_id} twin {edge.twin} points back to {twin.twin}")
        if twin.origin != edge.dest or twin.dest != edge.origin:
            twin_issues.append(
                f"edge {edge.edge_id} endpoints ({edge.origin}->{edge.dest}) mismatch twin ({twin.origin}->{twin.dest})"
            )

    boundary_set = set(case.boundary_order)
    for source_kind, source_idx, start_edge in case.sources:
        if source_kind == "boundary":
            continue
        if start_edge in boundary_set:
            continue
        detached_cycle = follow_cycle(case.edges, start_edge)
        detached_sources.append((source_kind, source_idx, start_edge, len(detached_cycle)))

    edge_ids = sorted(case.edges)
    for i, edge_id_a in enumerate(edge_ids):
        edge_a = case.edges[edge_id_a]
        points_a = (case.vertices[edge_a.origin], case.vertices[edge_a.dest])
        for edge_id_b in edge_ids[i + 1:]:
            edge_b = case.edges[edge_id_b]

            shared_vertices = {edge_a.origin, edge_a.dest} & {edge_b.origin, edge_b.dest}
            if shared_vertices:
                continue
            if edge_a.twin == edge_b.edge_id or edge_b.twin == edge_a.edge_id:
                continue
            if {edge_a.origin, edge_a.dest} == {edge_b.origin, edge_b.dest}:
                continue

            points_b = (case.vertices[edge_b.origin], case.vertices[edge_b.dest])
            if proper_intersection(points_a[0], points_a[1], points_b[0], points_b[1]):
                proper_crossings.append((edge_id_a, edge_id_b))

    cycles = compute_cycles(case)
    return MergeAnalysis(
        cycle_count=len(cycles),
        boundary_cycle_length=len(case.boundary_order),
        detached_sources=detached_sources,
        next_prev_issues=next_prev_issues,
        twin_issues=twin_issues,
        proper_crossings=proper_crossings,
    )


def save_case_plot(
    output_path: Path,
    case_index: int,
    original_case: Optional[CaseInput],
    dump_case: MergeCaseDump,
    analysis: MergeAnalysis,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#f8f5ef")
    ax.set_facecolor("#fcfaf5")

    if original_case is not None:
        outer, holes = original_case
        outer_x = [point[0] for point in outer] + [outer[0][0]]
        outer_y = [point[1] for point in outer] + [outer[0][1]]
        ax.plot(outer_x, outer_y, color="#8f8f8f", linewidth=1.5, alpha=0.65)
        for hole in holes:
            hx = [point[0] for point in hole] + [hole[0][0]]
            hy = [point[1] for point in hole] + [hole[0][1]]
            ax.plot(hx, hy, color="#b0b0b0", linewidth=1.1, alpha=0.7)

    drawn_bridge_segments: set[Tuple[int, int]] = set()
    for edge_id in dump_case.boundary_order:
        edge = dump_case.edges[edge_id]
        start = dump_case.vertices[edge.origin]
        end = dump_case.vertices[edge.dest]
        color = "#1f1f1f"
        linewidth = 1.8
        alpha = 0.9
        if edge.is_bridge:
            key = tuple(sorted((edge.origin, edge.dest)))
            if key in drawn_bridge_segments:
                continue
            drawn_bridge_segments.add(key)
            color = "#c62828"
            linewidth = 2.6
            alpha = 0.95
        ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=linewidth, alpha=alpha)

    vertex_x = [dump_case.vertices[idx][0] for idx in sorted(dump_case.vertices)]
    vertex_y = [dump_case.vertices[idx][1] for idx in sorted(dump_case.vertices)]
    ax.scatter(vertex_x, vertex_y, c="#1b1b1b", s=18, zorder=5)

    all_points = list(dump_case.vertices.values())
    min_x = min(point[0] for point in all_points)
    max_x = max(point[0] for point in all_points)
    min_y = min(point[1] for point in all_points)
    max_y = max(point[1] for point in all_points)
    span = max(max_x - min_x, max_y - min_y, 1.0)
    margin = 0.08 * span
    ax.set_xlim(min_x - margin, max_x + margin)
    ax.set_ylim(min_y - margin, max_y + margin)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.35)
    status = "OK" if analysis.is_valid else "FAIL"
    ax.set_title(
        f"Merge Case {case_index}: {status}, cycles={analysis.cycle_count}, "
        f"crossings={len(analysis.proper_crossings)}, detached={len(analysis.detached_sources)}"
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def format_issue_list(issues: Iterable[str], limit: int = 5) -> str:
    collected = list(issues)
    if not collected:
        return "none"
    trimmed = collected[:limit]
    suffix = "" if len(collected) <= limit else f" ... (+{len(collected) - limit} more)"
    return "; ".join(trimmed) + suffix


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect the post-merge half-edge graph before triangulation.")
    parser.add_argument("input", help="Assignment-format input file to inspect.")
    parser.add_argument(
        "--solver",
        default="build/art_gallery",
        help="Path to the solver executable. Default: build/art_gallery",
    )
    parser.add_argument(
        "--dump-file",
        help="Use an existing merge dump instead of running the solver.",
    )
    parser.add_argument(
        "--case",
        type=int,
        help="Only report a single 1-based case index.",
    )
    parser.add_argument(
        "--output-dir",
        default="plots/merge_debug",
        help="Directory where diagnostic plots are written.",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip writing matplotlib plots.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    solver_path = Path(args.solver)
    output_dir = Path(args.output_dir)

    cases = parse_input_file(input_path)

    if args.dump_file:
        dump_path = Path(args.dump_file)
    else:
        dump_handle = tempfile.NamedTemporaryFile(prefix="merge_dump_", suffix=".txt", delete=False)
        dump_handle.close()
        dump_path = Path(dump_handle.name)
        run_solver_with_dump(input_path, solver_path, dump_path)

    dump_cases = parse_dump_file(dump_path)

    if not args.dump_file:
        dump_path.unlink(missing_ok=True)

    if len(dump_cases) != len(cases):
        raise RuntimeError(
            f"expected {len(cases)} merge dumps, but found {len(dump_cases)} in the debug output"
        )

    if not args.no_plot:
        output_dir.mkdir(parents=True, exist_ok=True)

    warned_about_matplotlib = False

    for dump_case, original_case in zip(dump_cases, cases):
        if args.case is not None and dump_case.case_index != args.case:
            continue

        analysis = analyze_case(dump_case)
        print(
            f"Case {dump_case.case_index}: {'OK' if analysis.is_valid else 'FAIL'} | "
            f"boundary_edges={dump_case.summary.get('boundary_edges', len(dump_case.boundary_order))} | "
            f"tracked_edges={dump_case.summary.get('tracked_edges', len(dump_case.edges))} | "
            f"bridge_pairs={len(dump_case.bridge_pairs)} | "
            f"cycles={analysis.cycle_count} | "
            f"proper_crossings={len(analysis.proper_crossings)} | "
            f"detached_sources={len(analysis.detached_sources)}"
        )
        print(f"  next/prev: {format_issue_list(analysis.next_prev_issues)}")
        print(f"  twins: {format_issue_list(analysis.twin_issues)}")

        if analysis.detached_sources:
            detached = ", ".join(
                f"{kind}[{idx}] edge={edge_id} cycle_len={cycle_len}"
                for kind, idx, edge_id, cycle_len in analysis.detached_sources[:5]
            )
            if len(analysis.detached_sources) > 5:
                detached += f", ... (+{len(analysis.detached_sources) - 5} more)"
            print(f"  detached: {detached}")
        else:
            print("  detached: none")

        if analysis.proper_crossings:
            crossing_text = ", ".join(
                f"{a}x{b}" for a, b in analysis.proper_crossings[:8]
            )
            if len(analysis.proper_crossings) > 8:
                crossing_text += f", ... (+{len(analysis.proper_crossings) - 8} more)"
            print(f"  crossings: {crossing_text}")
        else:
            print("  crossings: none")

        if not args.no_plot:
            output_path = output_dir / f"{input_path.stem}_merge_case{dump_case.case_index}.png"
            try:
                save_case_plot(output_path, dump_case.case_index, original_case, dump_case, analysis)
                print(f"  plot: {output_path}")
            except ModuleNotFoundError:
                if not warned_about_matplotlib:
                    print(
                        "  plot: skipped because matplotlib is unavailable for this interpreter. "
                        "Use --no-plot or run with ~/aiml_lab/.venv/bin/python.",
                    )
                    warned_about_matplotlib = True


if __name__ == "__main__":
    main()
