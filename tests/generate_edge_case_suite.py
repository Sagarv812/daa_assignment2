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
    star_polygon,
    triangle_up,
    validate_case,
)


def build_cases() -> list[GalleryCase]:
    cases: list[GalleryCase] = []

    outer1 = rect(0.0, 0.0, 190.0, 180.0)
    holes1 = [
        rect(118.0, 146.0, 132.0, 160.0),
        diamond(102.0, 128.0, 8.0, 12.0),
        rect(116.0, 102.0, 130.0, 116.0),
        diamond(100.0, 84.0, 8.0, 12.0),
        rect(114.0, 58.0, 128.0, 72.0),
        octagon(98.0, 40.0, 8.0, 10.0),
        rect(62.0, 118.0, 76.0, 132.0),
        rect(58.0, 74.0, 72.0, 88.0),
    ]
    cases.append(
        GalleryCase(
            "same_wall_cascade",
            "descending mixed holes arranged so many bridge rays initially compete for the same far-left wall",
            outer1,
            holes1,
        )
    )

    outer2 = rect(0.0, 0.0, 240.0, 126.0)
    holes2 = [
        rect(12.0, 68.0, 22.0, 82.0),
        rect(34.0, 68.0, 44.0, 82.0),
        rect(56.0, 68.0, 66.0, 82.0),
        rect(78.0, 68.0, 88.0, 82.0),
        rect(100.0, 68.0, 110.0, 82.0),
        rect(122.0, 68.0, 132.0, 82.0),
        rect(144.0, 68.0, 154.0, 82.0),
        rect(166.0, 68.0, 176.0, 82.0),
        rect(188.0, 68.0, 198.0, 82.0),
        rect(210.0, 68.0, 220.0, 82.0),
        diamond(52.0, 38.0, 7.0, 10.0),
        diamond(118.0, 38.0, 7.0, 10.0),
        diamond(184.0, 38.0, 7.0, 10.0),
    ]
    cases.append(
        GalleryCase(
            "equal_y_event_band",
            "ten flat-top holes sharing the same top y-level plus lower diamonds to stress event-order ties",
            outer2,
            holes2,
        )
    )

    outer3 = notched_rectangle(
        220.0,
        144.0,
        bottom_notches=[(18.0, 42.0, 22.0), (62.0, 86.0, 24.0), (108.0, 128.0, 18.0), (150.0, 176.0, 24.0)],
        top_notches=[(24.0, 48.0, 40.0), (72.0, 96.0, 32.0), (118.0, 142.0, 42.0), (164.0, 190.0, 30.0)],
    )
    holes3 = [
        rect(18.0, 88.0, 30.0, 100.0),
        rect(44.0, 88.0, 56.0, 100.0),
        diamond(84.0, 92.0, 8.0, 8.0),
        rect(102.0, 90.0, 114.0, 102.0),
        diamond(154.0, 90.0, 8.0, 10.0),
        rect(182.0, 88.0, 194.0, 100.0),
        rect(88.0, 48.0, 100.0, 60.0),
        triangle_up(136.0, 54.0, 16.0, 16.0),
    ]
    cases.append(
        GalleryCase(
            "horizontal_ledge_alignment",
            "orthogonal gallery with many horizontal ledges and several hole tops aligned to those ledges",
            outer3,
            holes3,
        )
    )

    outer4 = notched_rectangle(
        240.0,
        112.0,
        bottom_notches=[
            (10.0, 20.0, 20.0),
            (30.0, 40.0, 20.0),
            (50.0, 60.0, 20.0),
            (70.0, 80.0, 20.0),
            (90.0, 100.0, 20.0),
            (110.0, 120.0, 20.0),
            (130.0, 140.0, 20.0),
            (150.0, 160.0, 20.0),
            (170.0, 180.0, 20.0),
            (190.0, 200.0, 20.0),
            (210.0, 220.0, 20.0),
        ],
        top_notches=[
            (18.0, 28.0, 32.0),
            (48.0, 58.0, 32.0),
            (78.0, 88.0, 32.0),
            (108.0, 118.0, 32.0),
            (138.0, 148.0, 32.0),
            (168.0, 178.0, 32.0),
            (198.0, 208.0, 32.0),
        ],
    )
    holes4 = [
        octagon(26.0, 56.0, 7.0, 8.0),
        octagon(62.0, 56.0, 7.0, 8.0),
        octagon(98.0, 56.0, 7.0, 8.0),
        octagon(134.0, 56.0, 7.0, 8.0),
        octagon(170.0, 56.0, 7.0, 8.0),
        octagon(206.0, 56.0, 7.0, 8.0),
        diamond(44.0, 56.0, 6.0, 8.0),
        diamond(116.0, 56.0, 6.0, 8.0),
        diamond(188.0, 56.0, 6.0, 8.0),
    ]
    cases.append(
        GalleryCase(
            "dense_collinear_bridge_band",
            "many holes share the same top y and sit on long collinear horizontal bands inside a serrated shell",
            outer4,
            holes4,
        )
    )

    outer5 = star_polygon(10.0, -4.0, 188.0, 122.0, 14, rotation=0.12, stretch_x=1.16, stretch_y=0.80)
    holes5 = [
        diamond(-92.0, 28.0, 8.0, 12.0),
        octagon(-52.0, 30.0, 8.0, 10.0),
        rect(-10.0, 20.0, 8.0, 40.0),
        triangle_up(46.0, 32.0, 18.0, 16.0),
        diamond(94.0, 26.0, 8.0, 14.0),
        octagon(22.0, -6.0, 10.0, 12.0),
        rect(-54.0, -24.0, -34.0, -8.0),
        diamond(70.0, -24.0, 9.0, 11.0),
    ]
    cases.append(
        GalleryCase(
            "slanted_equal_height_cluster",
            "non-axis-aligned star shell with several hole tops landing on the same y despite mixed shapes",
            outer5,
            holes5,
        )
    )

    outer6 = notched_rectangle(
        260.0,
        160.0,
        bottom_notches=[
            (14.0, 30.0, 24.0),
            (42.0, 58.0, 36.0),
            (72.0, 88.0, 24.0),
            (100.0, 118.0, 40.0),
            (132.0, 148.0, 24.0),
            (160.0, 176.0, 36.0),
            (190.0, 206.0, 24.0),
            (220.0, 238.0, 34.0),
        ],
        top_notches=[
            (20.0, 38.0, 42.0),
            (52.0, 70.0, 28.0),
            (84.0, 102.0, 46.0),
            (116.0, 134.0, 30.0),
            (148.0, 166.0, 44.0),
            (180.0, 198.0, 28.0),
            (212.0, 230.0, 40.0),
        ],
    )
    holes6 = [
        rect(24.0, 62.0, 34.0, 74.0),
        rect(60.0, 92.0, 70.0, 104.0),
        diamond(94.0, 62.0, 6.0, 8.0),
        rect(122.0, 96.0, 132.0, 108.0),
        octagon(156.0, 66.0, 6.0, 8.0),
        rect(184.0, 90.0, 194.0, 102.0),
        diamond(216.0, 68.0, 6.0, 9.0),
        rect(106.0, 46.0, 116.0, 58.0),
        rect(168.0, 40.0, 178.0, 52.0),
        triangle_up(76.0, 40.0, 14.0, 14.0),
    ]
    cases.append(
        GalleryCase(
            "thin_channel_mixture",
            "deep orthogonal maze with thin corridors, mixed hole shapes, and repeated same-x / same-y alignments",
            outer6,
            holes6,
        )
    )

    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a deterministic edge-case testcase suite.")
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
