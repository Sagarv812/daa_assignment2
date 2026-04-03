from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon


FIGURES_DIR = Path(__file__).resolve().parent / "figures"


def line_intersection_x(p1, p2, y):
    (x1, y1), (x2, y2) = p1, p2
    t = (y - y1) / (y2 - y1)
    return x1 + t * (x2 - x1)


def main():
    black = "#111111"
    wall_blue = "#365C99"
    wall_fill = "#EDF3FF"
    bridge_orange = "#D46A1D"
    event_red = "#D13E3E"
    sweep_gray = "#6B7788"
    gallery_fill = "#F7F4EE"

    outer = [
        (0.85, 0.75),
        (6.05, 0.75),
        (8.45, 1.8),
        (8.65, 5.75),
        (1.15, 5.95),
        (1.55, 4.65),
    ]

    hole = [
        (5.05, 4.05),
        (5.75, 3.2),
        (5.45, 1.95),
        (4.25, 2.05),
        (4.0, 3.15),
    ]

    m = hole[0]
    t = outer[-1]
    lower_wall_vertex = outer[0]
    sweep_y = m[1]
    sweep_x = line_intersection_x(t, lower_wall_vertex, sweep_y)

    fig, ax = plt.subplots(figsize=(11.2, 6.2), dpi=220)

    ax.add_patch(
        Polygon(
            outer,
            closed=True,
            facecolor=gallery_fill,
            edgecolor=black,
            linewidth=3.2,
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
            linewidth=3.2,
            joinstyle="round",
            zorder=2,
        )
    )

    ax.plot(
        [t[0], lower_wall_vertex[0]],
        [t[1], lower_wall_vertex[1]],
        color=wall_blue,
        linewidth=5.6,
        solid_capstyle="round",
        zorder=3,
    )

    ax.plot(
        [0.45, 9.05],
        [sweep_y, sweep_y],
        color=sweep_gray,
        linewidth=2.6,
        linestyle="--",
        zorder=0,
    )

    bridge = FancyArrowPatch(
        posA=m,
        posB=t,
        arrowstyle="-|>",
        mutation_scale=26,
        linewidth=3.2,
        linestyle="--",
        color=bridge_orange,
        shrinkA=4,
        shrinkB=4,
        zorder=4,
    )
    ax.add_patch(bridge)

    ax.scatter(
        [m[0]],
        [m[1]],
        s=150,
        color=event_red,
        edgecolors="white",
        linewidths=1.6,
        zorder=5,
    )
    ax.scatter(
        [t[0]],
        [t[1]],
        s=185,
        color=wall_blue,
        edgecolors="white",
        linewidths=2.0,
        zorder=5,
    )
    ax.scatter(
        [sweep_x],
        [sweep_y],
        s=58,
        color=wall_blue,
        edgecolors="white",
        linewidths=1.1,
        zorder=6,
    )

    label_box = {
        "boxstyle": "round,pad=0.3",
        "facecolor": "white",
        "edgecolor": "none",
        "alpha": 0.95,
    }

    ax.annotate(
        "helper on wall",
        xy=t,
        xytext=(2.35, 5.88),
        fontsize=14,
        color=wall_blue,
        ha="left",
        va="center",
        arrowprops={"arrowstyle": "->", "lw": 2.1, "color": wall_blue},
        bbox=label_box,
        zorder=7,
    )
    ax.annotate(
        "closest active wall",
        xy=(sweep_x, sweep_y),
        xytext=(0.35, 2.95),
        fontsize=14,
        color=wall_blue,
        ha="left",
        va="center",
        arrowprops={"arrowstyle": "->", "lw": 2.1, "color": wall_blue},
        bbox=label_box,
        zorder=7,
    )
    ax.annotate(
        "topmost hole vertex M",
        xy=m,
        xytext=(4.3, 5.2),
        fontsize=15,
        color=event_red,
        ha="center",
        va="center",
        arrowprops={"arrowstyle": "->", "lw": 2.1, "color": event_red},
        bbox=label_box,
        zorder=7,
    )

    ax.text(
        7.05,
        sweep_y + 0.28,
        "sweep line",
        color=sweep_gray,
        fontsize=15,
        fontweight="bold",
    )
    ax.text(
        2.65,
        4.82,
        "bridge chosen\nfrom HelperState",
        color=bridge_orange,
        fontsize=15,
        ha="center",
        va="center",
        bbox={
            "boxstyle": "round,pad=0.3",
            "facecolor": "#FFF6ED",
            "edgecolor": "none",
            "alpha": 0.95,
        },
        zorder=7,
    )
    ax.text(
        t[0] + 0.18,
        t[1] + 0.36,
        "T",
        color=wall_blue,
        fontsize=16,
        fontweight="bold",
        zorder=8,
    )
    ax.text(
        m[0] + 0.12,
        m[1] + 0.14,
        "M",
        color=event_red,
        fontsize=16,
        fontweight="bold",
        zorder=8,
    )

    ax.set_xlim(0.05, 9.25)
    ax.set_ylim(0.35, 6.45)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.03, top=0.98)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / "bridge_search.pdf", bbox_inches="tight", pad_inches=0.06)
    fig.savefig(FIGURES_DIR / "bridge_search.png", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


if __name__ == "__main__":
    main()
