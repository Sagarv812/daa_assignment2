from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon


FIGURES_DIR = Path(__file__).resolve().parent / "figures"


def line_intersection_x(p1, p2, y):
    (x1, y1), (x2, y2) = p1, p2
    t = (y - y1) / (y2 - y1)
    return x1 + t * (x2 - x1)


def main():
    black = "#171717"
    gallery_fill = "#F7F4EE"
    wall_blue = "#315D9A"
    wall_blue_light = "#EAF1FF"
    bridge_orange = "#D97721"
    helper_orange = "#B85C19"
    event_red = "#CF4545"
    sweep_gray = "#6F7B8B"
    ray_gray = "#9AA6B4"

    outer = [
        (0.9, 0.9),
        (6.6, 0.9),
        (8.3, 1.9),
        (8.45, 5.85),
        (1.1, 6.05),
        (1.55, 4.55),
    ]

    hole = [
        (4.8, 4.1),
        (5.7, 3.2),
        (5.45, 1.95),
        (4.15, 2.05),
        (3.95, 3.2),
    ]

    m = hole[0]
    target = outer[-1]
    lower_wall_vertex = outer[0]
    sweep_y = m[1]
    hit_x = line_intersection_x(target, lower_wall_vertex, sweep_y)
    hit = (hit_x, sweep_y)

    fig, ax = plt.subplots(figsize=(11.2, 6.2), dpi=220)

    ax.add_patch(
        Polygon(
            outer,
            closed=True,
            facecolor=gallery_fill,
            edgecolor=black,
            linewidth=3.0,
            joinstyle="round",
            zorder=1,
        )
    )
    ax.add_patch(
        Polygon(
            hole,
            closed=True,
            facecolor="white",
            edgecolor=black,
            linewidth=3.0,
            joinstyle="round",
            zorder=2,
        )
    )

    ax.plot(
        [target[0], lower_wall_vertex[0]],
        [target[1], lower_wall_vertex[1]],
        color=wall_blue,
        linewidth=6.0,
        solid_capstyle="round",
        zorder=3,
    )

    ax.plot(
        [0.45, 9.0],
        [sweep_y, sweep_y],
        color=sweep_gray,
        linewidth=2.3,
        linestyle=(0, (6, 5)),
        zorder=0,
    )

    query_ray = FancyArrowPatch(
        posA=m,
        posB=hit,
        arrowstyle="-|>",
        mutation_scale=20,
        linewidth=2.6,
        linestyle=(0, (4, 4)),
        color=ray_gray,
        shrinkA=4,
        shrinkB=3,
        zorder=4,
    )
    bridge = FancyArrowPatch(
        posA=m,
        posB=target,
        arrowstyle="-|>",
        mutation_scale=24,
        linewidth=3.0,
        linestyle=(0, (3, 3)),
        color=bridge_orange,
        shrinkA=4,
        shrinkB=4,
        zorder=5,
    )
    ax.add_patch(query_ray)
    ax.add_patch(bridge)

    ax.scatter(
        [m[0]],
        [m[1]],
        s=165,
        color=event_red,
        edgecolors="white",
        linewidths=1.8,
        zorder=6,
    )
    ax.scatter(
        [target[0]],
        [target[1]],
        s=195,
        color=helper_orange,
        edgecolors="white",
        linewidths=2.0,
        zorder=6,
    )
    ax.scatter(
        [hit[0]],
        [hit[1]],
        s=72,
        color=wall_blue,
        edgecolors="white",
        linewidths=1.1,
        zorder=7,
    )

    label_box = {
        "boxstyle": "round,pad=0.25",
        "facecolor": "white",
        "edgecolor": "none",
        "alpha": 0.95,
    }

    ax.annotate(
        "topmost hole vertex M",
        xy=m,
        xytext=(4.95, 5.25),
        fontsize=15,
        color=event_red,
        ha="center",
        va="center",
        arrowprops={"arrowstyle": "->", "lw": 2.0, "color": event_red},
        bbox=label_box,
        zorder=8,
    )
    ax.annotate(
        "stored helper target T",
        xy=target,
        xytext=(2.65, 5.8),
        fontsize=14,
        color=helper_orange,
        ha="left",
        va="center",
        arrowprops={"arrowstyle": "->", "lw": 2.0, "color": helper_orange},
        bbox=label_box,
        zorder=8,
    )
    ax.annotate(
        "left-ray hit on closest active wall",
        xy=hit,
        xytext=(0.38, 3.0),
        fontsize=14,
        color=wall_blue,
        ha="left",
        va="center",
        arrowprops={"arrowstyle": "->", "lw": 2.0, "color": wall_blue},
        bbox=label_box,
        zorder=8,
    )

    ax.text(
        6.75,
        sweep_y + 0.28,
        "sweep y",
        color=sweep_gray,
        fontsize=15,
        fontweight="bold",
    )
    ax.text(
        2.25,
        4.55,
        "horizontal left-ray query",
        color=ray_gray,
        fontsize=14,
        ha="left",
        va="center",
        bbox={"boxstyle": "round,pad=0.22", "facecolor": wall_blue_light, "edgecolor": "none", "alpha": 0.92},
        zorder=8,
    )
    ax.text(
        2.05,
        4.95,
        "bridge chosen from HelperState",
        color=bridge_orange,
        fontsize=14,
        ha="left",
        va="center",
        bbox={"boxstyle": "round,pad=0.22", "facecolor": "#FFF3E8", "edgecolor": "none", "alpha": 0.95},
        zorder=8,
    )

    ax.text(target[0] + 0.18, target[1] + 0.34, "T", color=helper_orange, fontsize=16, fontweight="bold", zorder=9)
    ax.text(m[0] + 0.12, m[1] + 0.14, "M", color=event_red, fontsize=16, fontweight="bold", zorder=9)
    ax.text(hit[0] - 0.18, hit[1] + 0.22, "H", color=wall_blue, fontsize=14, fontweight="bold", zorder=9)

    ax.set_xlim(0.05, 9.15)
    ax.set_ylim(0.3, 6.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.03, top=0.98)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / "bridge_search.pdf", bbox_inches="tight", pad_inches=0.06)
    fig.savefig(FIGURES_DIR / "bridge_search.png", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


if __name__ == "__main__":
    main()
