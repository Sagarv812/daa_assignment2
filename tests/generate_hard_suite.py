#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass


EPS = 1e-9
Point = tuple[float, float]


@dataclass(frozen=True)
class GalleryCase:
    name: str
    description: str
    outer: list[Point]
    holes: list[list[Point]]

    @property
    def total_vertices(self) -> int:
        return len(self.outer) + sum(len(hole) for hole in self.holes)

    @property
    def expected_triangles(self) -> int:
        return self.total_vertices + 2 * len(self.holes) - 2


def polygon_area(poly: list[Point]) -> float:
    area = 0.0
    for i, (x1, y1) in enumerate(poly):
        x2, y2 = poly[(i + 1) % len(poly)]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def ensure_ccw(poly: list[Point]) -> list[Point]:
    return poly if polygon_area(poly) > 0.0 else list(reversed(poly))


def ensure_cw(poly: list[Point]) -> list[Point]:
    return poly if polygon_area(poly) < 0.0 else list(reversed(poly))


def clean_polygon(poly: list[Point]) -> list[Point]:
    cleaned: list[Point] = []
    for point in poly:
        if not cleaned or abs(cleaned[-1][0] - point[0]) > EPS or abs(cleaned[-1][1] - point[1]) > EPS:
            cleaned.append(point)
    if len(cleaned) > 1:
        first = cleaned[0]
        last = cleaned[-1]
        if abs(first[0] - last[0]) <= EPS and abs(first[1] - last[1]) <= EPS:
            cleaned.pop()
    return cleaned


def orient(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def on_segment(a: Point, b: Point, p: Point) -> bool:
    if abs(orient(a, b, p)) > EPS:
        return False
    return (
        min(a[0], b[0]) - EPS <= p[0] <= max(a[0], b[0]) + EPS
        and min(a[1], b[1]) - EPS <= p[1] <= max(a[1], b[1]) + EPS
    )


def segments_intersect(a1: Point, a2: Point, b1: Point, b2: Point) -> bool:
    o1 = orient(a1, a2, b1)
    o2 = orient(a1, a2, b2)
    o3 = orient(b1, b2, a1)
    o4 = orient(b1, b2, a2)

    if (o1 > EPS and o2 < -EPS or o1 < -EPS and o2 > EPS) and (
        o3 > EPS and o4 < -EPS or o3 < -EPS and o4 > EPS
    ):
        return True

    return (
        on_segment(a1, a2, b1)
        or on_segment(a1, a2, b2)
        or on_segment(b1, b2, a1)
        or on_segment(b1, b2, a2)
    )


def polygon_simple(poly: list[Point]) -> bool:
    n = len(poly)
    for i in range(n):
        a1 = poly[i]
        a2 = poly[(i + 1) % n]
        for j in range(i + 1, n):
            if j == i or (j + 1) % n == i or (i + 1) % n == j:
                continue
            b1 = poly[j]
            b2 = poly[(j + 1) % n]
            if segments_intersect(a1, a2, b1, b2):
                return False
    return True


def point_in_polygon(point: Point, poly: list[Point]) -> bool:
    x, y = point
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if on_segment((x1, y1), (x2, y2), point):
            return False
        intersects = (y1 > y) != (y2 > y)
        if intersects:
            x_int = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
            if x_int > x:
                inside = not inside
    return inside


def polygons_disjoint(a: list[Point], b: list[Point]) -> bool:
    for i in range(len(a)):
        a1 = a[i]
        a2 = a[(i + 1) % len(a)]
        for j in range(len(b)):
            b1 = b[j]
            b2 = b[(j + 1) % len(b)]
            if segments_intersect(a1, a2, b1, b2):
                return False
    return point_in_polygon(a[0], b) is False and point_in_polygon(b[0], a) is False


def hole_inside_outer(hole: list[Point], outer: list[Point]) -> bool:
    if any(not point_in_polygon(point, outer) for point in hole):
        return False
    for i in range(len(hole)):
        h1 = hole[i]
        h2 = hole[(i + 1) % len(hole)]
        for j in range(len(outer)):
            o1 = outer[j]
            o2 = outer[(j + 1) % len(outer)]
            if segments_intersect(h1, h2, o1, o2):
                return False
    return True


def regular_polygon(cx: float, cy: float, radius: float, count: int, rotation: float = 0.0,
                    stretch_x: float = 1.0, stretch_y: float = 1.0) -> list[Point]:
    poly = []
    for i in range(count):
        angle = rotation + 2.0 * math.pi * i / count
        poly.append((cx + stretch_x * radius * math.cos(angle), cy + stretch_y * radius * math.sin(angle)))
    return poly


def star_polygon(cx: float, cy: float, outer_radius: float, inner_radius: float, spikes: int,
                 rotation: float = 0.0, stretch_x: float = 1.0, stretch_y: float = 1.0) -> list[Point]:
    poly = []
    for i in range(2 * spikes):
        angle = rotation + math.pi * i / spikes
        radius = outer_radius if i % 2 == 0 else inner_radius
        poly.append((cx + stretch_x * radius * math.cos(angle), cy + stretch_y * radius * math.sin(angle)))
    return poly


def rect(x1: float, y1: float, x2: float, y2: float) -> list[Point]:
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]


def diamond(cx: float, cy: float, rx: float, ry: float) -> list[Point]:
    return [(cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy)]


def triangle_up(cx: float, cy: float, width: float, height: float) -> list[Point]:
    half_w = width / 2.0
    return [(cx - half_w, cy - height / 2.0), (cx + half_w, cy - height / 2.0), (cx, cy + height / 2.0)]


def octagon(cx: float, cy: float, rx: float, ry: float) -> list[Point]:
    return [
        (cx - rx * 0.45, cy - ry),
        (cx + rx * 0.45, cy - ry),
        (cx + rx, cy - ry * 0.45),
        (cx + rx, cy + ry * 0.45),
        (cx + rx * 0.45, cy + ry),
        (cx - rx * 0.45, cy + ry),
        (cx - rx, cy + ry * 0.45),
        (cx - rx, cy - ry * 0.45),
    ]


def notched_rectangle(width: float, height: float,
                      bottom_notches: list[tuple[float, float, float]],
                      top_notches: list[tuple[float, float, float]]) -> list[Point]:
    points: list[Point] = [(0.0, 0.0)]

    current_x = 0.0
    for x1, x2, depth in sorted(bottom_notches):
        if x1 > current_x + EPS:
            points.append((x1, 0.0))
        points.extend([(x1, depth), (x2, depth), (x2, 0.0)])
        current_x = x2
    if current_x < width - EPS:
        points.append((width, 0.0))

    points.append((width, height))
    current_x = width
    for x1, x2, depth in sorted(top_notches, reverse=True):
        if x2 < current_x - EPS:
            points.append((x2, height))
        points.extend([(x2, height - depth), (x1, height - depth), (x1, height)])
        current_x = x1
    if current_x > EPS:
        points.append((0.0, height))

    return clean_polygon(points)


def build_cases() -> list[GalleryCase]:
    cases: list[GalleryCase] = []

    outer1 = notched_rectangle(
        140.0,
        90.0,
        bottom_notches=[(8.0, 20.0, 16.0), (30.0, 44.0, 12.0), (56.0, 72.0, 18.0), (84.0, 98.0, 14.0), (110.0, 124.0, 12.0)],
        top_notches=[(18.0, 34.0, 24.0), (48.0, 60.0, 16.0), (74.0, 88.0, 26.0), (100.0, 114.0, 18.0)],
    )
    holes1 = [
        octagon(24.0, 46.0, 5.0, 6.0),
        rect(42.0, 32.0, 52.0, 40.0),
        octagon(66.0, 46.0, 5.0, 6.0),
        rect(90.0, 30.0, 100.0, 40.0),
        octagon(116.0, 46.0, 4.5, 5.5),
        diamond(78.0, 52.0, 6.0, 8.0),
    ]
    cases.append(
        GalleryCase(
            "crenellated_corridors",
            "orthogonal outer boundary with alternating top and bottom bays and six mixed holes",
            outer1,
            holes1,
        )
    )

    outer2 = notched_rectangle(
        200.0,
        100.0,
        bottom_notches=[(20.0, 28.0, 18.0), (44.0, 52.0, 22.0), (88.0, 96.0, 18.0), (132.0, 140.0, 22.0), (176.0, 184.0, 18.0)],
        top_notches=[(10.0, 18.0, 38.0), (32.0, 40.0, 30.0), (54.0, 62.0, 42.0), (76.0, 84.0, 34.0),
                     (98.0, 106.0, 42.0), (120.0, 128.0, 30.0), (142.0, 150.0, 38.0), (164.0, 172.0, 34.0)],
    )
    holes2 = [
        rect(14.0, 44.0, 22.0, 56.0),
        rect(36.0, 44.0, 44.0, 56.0),
        rect(58.0, 44.0, 66.0, 56.0),
        rect(80.0, 44.0, 88.0, 56.0),
        rect(102.0, 44.0, 110.0, 56.0),
        rect(124.0, 44.0, 132.0, 56.0),
        rect(146.0, 44.0, 154.0, 56.0),
        rect(168.0, 44.0, 176.0, 56.0),
    ]
    cases.append(
        GalleryCase(
            "collinear_ladder",
            "long horizontal ladder with eight aligned holes sharing the same top y-level",
            outer2,
            holes2,
        )
    )

    outer3 = star_polygon(0.0, 0.0, 150.0, 92.0, 12, rotation=math.pi / 12.0)
    holes3 = [
        octagon(0.0, 0.0, 12.0, 12.0),
        rect(-46.0, -12.0, -26.0, 10.0),
        rect(24.0, -14.0, 42.0, 8.0),
        diamond(-12.0, 42.0, 10.0, 12.0),
        diamond(34.0, 32.0, 8.0, 10.0),
        triangle_up(-34.0, -36.0, 18.0, 18.0),
    ]
    cases.append(
        GalleryCase(
            "radial_star_cluster",
            "concave star-shaped gallery with a dense cluster of central holes",
            outer3,
            holes3,
        )
    )

    outer4 = notched_rectangle(
        180.0,
        130.0,
        bottom_notches=[(12.0, 26.0, 18.0), (36.0, 50.0, 28.0), (60.0, 74.0, 18.0), (84.0, 98.0, 30.0),
                        (112.0, 128.0, 22.0), (140.0, 154.0, 18.0)],
        top_notches=[(20.0, 34.0, 32.0), (46.0, 62.0, 22.0), (76.0, 92.0, 36.0), (102.0, 118.0, 20.0),
                     (132.0, 148.0, 34.0)],
    )
    holes4 = [
        rect(22.0, 54.0, 30.0, 64.0),
        octagon(48.0, 78.0, 5.0, 6.0),
        rect(68.0, 52.0, 76.0, 64.0),
        octagon(92.0, 80.0, 5.0, 6.0),
        rect(114.0, 50.0, 124.0, 62.0),
        octagon(138.0, 76.0, 5.0, 6.0),
        diamond(56.0, 38.0, 6.0, 8.0),
        rect(88.0, 38.0, 96.0, 48.0),
        diamond(124.0, 36.0, 6.0, 8.0),
        triangle_up(152.0, 46.0, 14.0, 14.0),
    ]
    cases.append(
        GalleryCase(
            "orthogonal_maze",
            "deep orthogonal bays on both sides with ten interior holes spread across narrow channels",
            outer4,
            holes4,
        )
    )

    outer5 = regular_polygon(0.0, 0.0, 185.0, 28, rotation=math.pi / 28.0)
    holes5 = [
        octagon(-72.0, -72.0, 9.0, 9.0),
        diamond(-24.0, -74.0, 8.0, 10.0),
        rect(20.0, -80.0, 38.0, -62.0),
        octagon(74.0, -70.0, 9.0, 9.0),
        rect(-104.0, -10.0, -88.0, 8.0),
        octagon(-52.0, 0.0, 8.0, 10.0),
        diamond(0.0, 0.0, 10.0, 10.0),
        octagon(52.0, 0.0, 8.0, 10.0),
        rect(88.0, -8.0, 104.0, 10.0),
        octagon(-74.0, 72.0, 9.0, 9.0),
        rect(-18.0, 62.0, 0.0, 80.0),
        octagon(32.0, 68.0, 9.0, 9.0),
        diamond(82.0, 74.0, 8.0, 10.0),
    ]
    cases.append(
        GalleryCase(
            "dense_many_holes",
            "large convex shell with thirteen mixed holes packed on a loose grid",
            outer5,
            holes5,
        )
    )

    outer6 = star_polygon(12.0, -6.0, 178.0, 118.0, 16, rotation=0.17, stretch_x=1.18, stretch_y=0.82)
    holes6 = [
        octagon(-58.0, -38.0, 9.0, 11.0),
        diamond(-18.0, -18.0, 8.0, 10.0),
        rect(8.0, -24.0, 26.0, -8.0),
        triangle_up(48.0, 8.0, 18.0, 18.0),
        octagon(82.0, 30.0, 8.0, 10.0),
        diamond(-32.0, 42.0, 10.0, 12.0),
        rect(2.0, 48.0, 18.0, 64.0),
        octagon(42.0, 66.0, 8.0, 9.0),
    ]
    cases.append(
        GalleryCase(
            "slanted_serrated_star",
            "non-axis-aligned serrated outer polygon with eight diagonally arranged holes",
            outer6,
            holes6,
        )
    )

    return cases


def validate_case(case: GalleryCase) -> None:
    outer = ensure_ccw(clean_polygon(case.outer))
    if len(outer) < 3 or not polygon_simple(outer):
        raise ValueError(f"{case.name}: outer polygon is not simple")

    normalized_holes: list[list[Point]] = []
    for idx, hole in enumerate(case.holes):
        normalized = ensure_cw(clean_polygon(hole))
        if len(normalized) < 3 or not polygon_simple(normalized):
            raise ValueError(f"{case.name}: hole {idx + 1} is not simple")
        if not hole_inside_outer(normalized, outer):
            raise ValueError(f"{case.name}: hole {idx + 1} is not strictly inside the outer polygon")
        for prev_idx, prev_hole in enumerate(normalized_holes):
            if not polygons_disjoint(normalized, prev_hole):
                raise ValueError(f"{case.name}: hole {idx + 1} intersects hole {prev_idx + 1}")
        normalized_holes.append(normalized)


def emit_suite(cases: list[GalleryCase]) -> str:
    lines = [str(len(cases))]
    for case in cases:
        outer = ensure_ccw(clean_polygon(case.outer))
        holes = [ensure_cw(clean_polygon(hole)) for hole in case.holes]
        lines.append(str(len(outer)))
        for x, y in outer:
            lines.append(f"{x:.3f} {y:.3f}")
        lines.append(str(len(holes)))
        for hole in holes:
            lines.append(str(len(hole)))
            for x, y in hole:
                lines.append(f"{x:.3f} {y:.3f}")
    return "\n".join(lines) + "\n"


def emit_summary(cases: list[GalleryCase]) -> str:
    lines = []
    for idx, case in enumerate(cases, 1):
        lines.append(
            f"{idx}. {case.name}: outer={len(case.outer)}, holes={len(case.holes)}, "
            f"total_vertices={case.total_vertices}, expected_triangles={case.expected_triangles}"
        )
        lines.append(f"   {case.description}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a deterministic hard testcase suite.")
    parser.add_argument("--summary", action="store_true", help="print case names and expected triangle counts")
    args = parser.parse_args()

    cases = build_cases()
    for case in cases:
        validate_case(case)

    if args.summary:
        print(emit_summary(cases))
    else:
        print(emit_suite(cases), end="")


if __name__ == "__main__":
    main()
