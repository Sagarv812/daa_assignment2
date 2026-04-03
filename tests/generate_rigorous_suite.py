#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math

from generate_hard_suite import (
    GalleryCase,
    diamond,
    emit_suite,
    emit_summary,
    notched_rectangle,
    octagon,
    rect,
    regular_polygon,
    star_polygon,
    triangle_up,
    validate_case,
)


def build_cases() -> list[GalleryCase]:
    cases: list[GalleryCase] = []

    outer1 = rect(0.0, 0.0, 260.0, 190.0)
    holes1 = [
        rect(182.0, 150.0, 196.0, 166.0),
        diamond(164.0, 132.0, 8.0, 10.0),
        rect(176.0, 114.0, 190.0, 130.0),
        diamond(158.0, 96.0, 8.0, 10.0),
        rect(170.0, 78.0, 184.0, 94.0),
        octagon(150.0, 60.0, 8.0, 10.0),
        rect(94.0, 136.0, 106.0, 148.0),
        rect(88.0, 96.0, 100.0, 108.0),
        rect(82.0, 56.0, 94.0, 68.0),
        diamond(116.0, 118.0, 7.0, 9.0),
        diamond(112.0, 80.0, 7.0, 9.0),
        rect(44.0, 112.0, 56.0, 124.0),
    ]
    cases.append(
        GalleryCase(
            "outer_wall_pressure_grid",
            "wide rectangle with descending right-side holes and staggered middle blockers to stress repeated helper updates on a far wall",
            outer1,
            holes1,
        )
    )

    outer2 = rect(0.0, 0.0, 300.0, 180.0)
    holes2: list[list[tuple[float, float]]] = []
    for i in range(10):
        x1 = 18.0 + 26.0 * i
        holes2.append(rect(x1, 106.0, x1 + 10.0, 120.0))
    for i in range(8):
        cx = 30.0 + 30.0 * i
        holes2.append(diamond(cx, 64.0, 7.0, 10.0))
    for cx in (70.0, 150.0, 230.0):
        holes2.append(octagon(cx, 34.0, 8.0, 9.0))
    cases.append(
        GalleryCase(
            "double_equal_y_fields",
            "two dense horizontal bands of flat-top holes plus a lower octagon row to hammer equal-y event ordering",
            outer2,
            holes2,
        )
    )

    outer3 = notched_rectangle(
        280.0,
        170.0,
        bottom_notches=[(18.0, 34.0, 22.0), (50.0, 68.0, 34.0), (84.0, 102.0, 22.0), (118.0, 136.0, 36.0),
                        (154.0, 172.0, 24.0), (190.0, 210.0, 34.0), (226.0, 244.0, 22.0)],
        top_notches=[(24.0, 42.0, 46.0), (60.0, 78.0, 28.0), (96.0, 116.0, 44.0), (132.0, 150.0, 30.0),
                     (168.0, 188.0, 42.0), (204.0, 222.0, 28.0), (240.0, 258.0, 40.0)],
    )
    holes3 = [
        rect(24.0, 98.0, 36.0, 110.0),
        octagon(58.0, 122.0, 7.0, 8.0),
        rect(88.0, 96.0, 100.0, 110.0),
        diamond(122.0, 118.0, 8.0, 12.0),
        rect(156.0, 94.0, 168.0, 108.0),
        octagon(194.0, 120.0, 7.0, 8.0),
        rect(228.0, 92.0, 240.0, 106.0),
        diamond(76.0, 54.0, 8.0, 10.0),
        rect(136.0, 50.0, 148.0, 62.0),
        triangle_up(214.0, 52.0, 16.0, 16.0),
        octagon(108.0, 74.0, 6.0, 7.0),
        rect(174.0, 70.0, 186.0, 82.0),
    ]
    cases.append(
        GalleryCase(
            "ledge_stair_mixture",
            "stair-stepped orthogonal shell with holes tucked under alternating ledges and above deep floor pockets",
            outer3,
            holes3,
        )
    )

    outer4 = notched_rectangle(
        300.0,
        190.0,
        bottom_notches=[(18.0, 34.0, 26.0), (46.0, 62.0, 42.0), (74.0, 90.0, 26.0), (102.0, 120.0, 48.0),
                        (132.0, 148.0, 26.0), (160.0, 176.0, 42.0), (188.0, 204.0, 26.0), (216.0, 234.0, 48.0),
                        (246.0, 262.0, 26.0)],
        top_notches=[(26.0, 44.0, 50.0), (58.0, 76.0, 34.0), (90.0, 108.0, 54.0), (122.0, 140.0, 36.0),
                     (154.0, 172.0, 52.0), (186.0, 204.0, 34.0), (218.0, 236.0, 54.0), (250.0, 268.0, 36.0)],
    )
    holes4 = [
        rect(28.0, 74.0, 38.0, 86.0),
        diamond(54.0, 112.0, 7.0, 10.0),
        rect(80.0, 72.0, 90.0, 84.0),
        diamond(110.0, 118.0, 7.0, 10.0),
        rect(136.0, 70.0, 146.0, 82.0),
        octagon(166.0, 112.0, 6.0, 8.0),
        rect(194.0, 74.0, 204.0, 86.0),
        diamond(222.0, 116.0, 7.0, 10.0),
        rect(250.0, 72.0, 260.0, 84.0),
        rect(120.0, 52.0, 132.0, 64.0),
        rect(178.0, 52.0, 190.0, 64.0),
        triangle_up(72.0, 52.0, 14.0, 14.0),
        triangle_up(236.0, 58.0, 14.0, 14.0),
        octagon(146.0, 92.0, 6.0, 8.0),
    ]
    cases.append(
        GalleryCase(
            "three_channel_maze",
            "deep maze-like orthogonal shell with many narrow channels and mixed hole heights across three active bands",
            outer4,
            holes4,
        )
    )

    outer5 = regular_polygon(0.0, 0.0, 220.0, 32, rotation=math.pi / 32.0)
    holes5: list[list[tuple[float, float]]] = []
    xs = (-96.0, -36.0, 24.0, 84.0)
    ys = (90.0, 30.0, -30.0, -90.0)
    for row, cy in enumerate(ys):
        for col, cx in enumerate(xs):
            shape = (row + col) % 4
            if shape == 0:
                holes5.append(rect(cx - 9.0, cy - 7.0, cx + 9.0, cy + 7.0))
            elif shape == 1:
                holes5.append(diamond(cx, cy, 8.0, 10.0))
            elif shape == 2:
                holes5.append(octagon(cx, cy, 8.0, 8.0))
            else:
                holes5.append(triangle_up(cx, cy, 16.0, 16.0))
    cases.append(
        GalleryCase(
            "convex_gridpack_32gon",
            "large convex 32-gon packed with a 4x4 mixed-shape grid to stress dense bridging inside a benign shell",
            outer5,
            holes5,
        )
    )

    outer6 = star_polygon(0.0, 0.0, 210.0, 146.0, 14, rotation=0.11, stretch_x=1.12, stretch_y=0.86)
    holes6 = [
        diamond(-74.0, 18.0, 8.0, 10.0),
        octagon(-42.0, 50.0, 7.0, 8.0),
        rect(-8.0, 50.0, 8.0, 62.0),
        triangle_up(34.0, 48.0, 14.0, 14.0),
        diamond(74.0, 18.0, 8.0, 10.0),
        octagon(52.0, -16.0, 7.0, 8.0),
        rect(2.0, -24.0, 18.0, -10.0),
        diamond(-42.0, -22.0, 8.0, 10.0),
        octagon(0.0, 18.0, 8.0, 10.0),
        rect(-28.0, 0.0, -14.0, 12.0),
        diamond(28.0, 10.0, 7.0, 9.0),
    ]
    cases.append(
        GalleryCase(
            "rotated_star_ring",
            "rotated star shell with a compact inner ring of mixed holes and many near-tie bridge candidates",
            outer6,
            holes6,
        )
    )

    outer7 = rect(0.0, 0.0, 340.0, 150.0)
    holes7: list[list[tuple[float, float]]] = []
    for i in range(12):
        x = 14.0 + 26.0 * i
        if i % 2 == 0:
            holes7.append(rect(x, 96.0, x + 10.0, 108.0))
        else:
            holes7.append(octagon(x + 5.0, 102.0, 5.0, 6.0))
    for i in range(9):
        holes7.append(diamond(24.0 + 30.0 * i, 58.0, 7.0, 10.0))
    for cx in (70.0, 170.0, 270.0):
        holes7.append(triangle_up(cx, 34.0, 14.0, 14.0))
    cases.append(
        GalleryCase(
            "collinear_multiband_extreme",
            "very wide gallery with two separate equal-y hole bands and extra low triangles to stress collinearity across many events",
            outer7,
            holes7,
        )
    )

    outer8 = rect(0.0, 0.0, 240.0, 240.0)
    holes8: list[list[tuple[float, float]]] = []
    for row, cy in enumerate((180.0, 126.0, 72.0)):
        for col, cx in enumerate((36.0, 84.0, 132.0, 180.0)):
            shape = (row + col) % 3
            if shape == 0:
                holes8.append(rect(cx - 8.0, cy - 8.0, cx + 8.0, cy + 8.0))
            elif shape == 1:
                holes8.append(diamond(cx, cy, 8.0, 10.0))
            else:
                holes8.append(octagon(cx, cy, 8.0, 8.0))
    cases.append(
        GalleryCase(
            "column_stack_same_x",
            "four aligned columns of holes sharing repeated x-values to stress vertical predecessor changes and helper reuse",
            outer8,
            holes8,
        )
    )

    outer9 = star_polygon(0.0, 0.0, 230.0, 158.0, 18, rotation=0.03, stretch_x=1.08, stretch_y=0.82)
    holes9 = [
        diamond(-88.0, 66.0, 8.0, 10.0),
        octagon(-50.0, 38.0, 7.0, 8.0),
        rect(-18.0, 2.0, -2.0, 16.0),
        diamond(34.0, -18.0, 7.0, 9.0),
        octagon(76.0, -46.0, 7.0, 8.0),
        rect(-84.0, -26.0, -68.0, -12.0),
        diamond(-34.0, 8.0, 7.0, 9.0),
        octagon(8.0, 36.0, 7.0, 8.0),
        rect(42.0, 58.0, 58.0, 72.0),
        diamond(96.0, 30.0, 8.0, 10.0),
    ]
    cases.append(
        GalleryCase(
            "serrated_spokes",
            "18-spike serrated shell with holes laid out along two diagonal spokes and an offset lower band",
            outer9,
            holes9,
        )
    )

    outer10 = notched_rectangle(
        320.0,
        180.0,
        bottom_notches=[(18.0, 34.0, 26.0), (50.0, 68.0, 36.0), (84.0, 100.0, 24.0), (116.0, 134.0, 42.0),
                        (150.0, 168.0, 24.0), (184.0, 202.0, 36.0), (218.0, 236.0, 24.0), (252.0, 270.0, 40.0),
                        (286.0, 302.0, 24.0)],
        top_notches=[(28.0, 46.0, 44.0), (62.0, 80.0, 28.0), (96.0, 114.0, 46.0), (130.0, 148.0, 30.0),
                     (164.0, 182.0, 44.0), (198.0, 216.0, 28.0), (232.0, 250.0, 46.0), (266.0, 284.0, 30.0)],
    )
    holes10 = [
        rect(28.0, 96.0, 40.0, 108.0),
        diamond(60.0, 120.0, 8.0, 10.0),
        rect(92.0, 94.0, 104.0, 106.0),
        octagon(54.0, 62.0, 7.0, 8.0),
        triangle_up(94.0, 56.0, 16.0, 16.0),
        rect(130.0, 100.0, 142.0, 112.0),
        diamond(162.0, 118.0, 8.0, 10.0),
        rect(194.0, 98.0, 206.0, 110.0),
        octagon(158.0, 66.0, 7.0, 8.0),
        triangle_up(198.0, 58.0, 16.0, 16.0),
        rect(232.0, 96.0, 244.0, 108.0),
        diamond(264.0, 120.0, 8.0, 10.0),
        rect(294.0, 94.0, 306.0, 106.0),
        octagon(258.0, 64.0, 7.0, 8.0),
        triangle_up(298.0, 56.0, 16.0, 16.0),
    ]
    cases.append(
        GalleryCase(
            "orthogonal_pocket_triples",
            "three repeated orthogonal pocket clusters spread across a long shell to stress consistency across similar local patterns",
            outer10,
            holes10,
        )
    )

    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a larger deterministic rigorous testcase suite.")
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
