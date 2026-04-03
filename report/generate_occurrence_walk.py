from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


FIGURES_DIR = Path(__file__).resolve().parent / "figures"

TEXT = "#1B1B1B"
GRAY = "#59677A"
BLUE = "#365C99"
BLUE_FILL = "#EDF3FF"
ORANGE = "#D46A1D"
ORANGE_FILL = "#FFF4E8"
RED = "#D13E3E"
RED_FILL = "#FDEEEE"


def add_box(ax, center, label, fill, edge):
    w = 10.2
    h = 5.8
    x = center[0] - w / 2.0
    y = center[1] - h / 2.0
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.28",
        linewidth=2.0,
        edgecolor=edge,
        facecolor=fill,
        zorder=3,
    )
    ax.add_patch(patch)
    ax.text(
        center[0],
        center[1],
        label,
        ha="center",
        va="center",
        fontsize=13.2,
        fontweight="bold",
        color=TEXT,
        zorder=4,
    )


def add_arrow(ax, start, end, rad=0.0):
    arrow = FancyArrowPatch(
        posA=start,
        posB=end,
        arrowstyle="-|>",
        mutation_scale=18,
        linewidth=2.5,
        color=GRAY,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=7,
        shrinkB=7,
        zorder=2,
    )
    ax.add_patch(arrow)


def main():
    fig, ax = plt.subplots(figsize=(12.0, 5.2), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 112)
    ax.set_ylim(0, 62)
    ax.axis("off")

    ax.text(
        56,
        56.4,
        "Merged Boundary Walk After One Bridge",
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        color=TEXT,
    )

    centers = [
        (11, 30),   # 0:v0
        (26, 41),   # 1:v1
        (42, 45),   # 2:T
        (57, 32),   # 3:M
        (73, 45),   # 4:h1
        (88, 41),   # 5:h2
        (101, 27),  # 6:M
        (84, 9),    # 7:T
        (34, 9),    # 8:v3
    ]

    labels = ["0:v0", "1:v1", "2:T", "3:M", "4:h1", "5:h2", "6:M", "7:T", "8:v3"]
    fills = [
        BLUE_FILL,
        BLUE_FILL,
        ORANGE_FILL,
        RED_FILL,
        BLUE_FILL,
        BLUE_FILL,
        RED_FILL,
        ORANGE_FILL,
        BLUE_FILL,
    ]
    edges = [
        BLUE,
        BLUE,
        ORANGE,
        RED,
        BLUE,
        BLUE,
        RED,
        ORANGE,
        BLUE,
    ]

    for center, label, fill, edge in zip(centers, labels, fills, edges):
        add_box(ax, center, label, fill, edge)

    for i in range(len(centers) - 1):
        add_arrow(ax, centers[i], centers[i + 1])
    add_arrow(ax, centers[-1], centers[0], rad=-0.18)

    ax.text(42, 39.4, "same original T", ha="center", va="bottom", fontsize=11.6, color=ORANGE, fontweight="bold")
    ax.text(84, 13.0, "same original T", ha="center", va="bottom", fontsize=11.6, color=ORANGE, fontweight="bold")
    ax.text(72, 19.8, "same original M", ha="center", va="center", fontsize=11.6, color=RED, fontweight="bold")

    ax.text(
        56,
        3.0,
        "Occurrence index = walk position. Different indices can still refer to the same original Vertex*.",
        ha="center",
        va="center",
        fontsize=12.3,
        color=GRAY,
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / "occurrence_walk.pdf", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(FIGURES_DIR / "occurrence_walk.png", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


if __name__ == "__main__":
    main()
