from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np


FIGURES_DIR = Path(__file__).resolve().parent / "figures"

TEXT = "#1B1B1B"
GRAY = "#6C7889"
BLUE = "#365C99"
BLUE_FILL = "#EDF3FF"
ORANGE = "#D46A1D"
ORANGE_FILL = "#FFF4E8"
LIGHT = "#C9D1DC"


def add_arrow(ax, start, end, color, lw=2.8, rad=0.0, z=3):
    arrow = FancyArrowPatch(
        posA=start,
        posB=end,
        arrowstyle="-|>",
        mutation_scale=16,
        linewidth=lw,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=7,
        shrinkB=7,
        zorder=z,
    )
    ax.add_patch(arrow)


def main():
    fig, ax = plt.subplots(figsize=(7.6, 5.2), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.25, 1.38)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.text(
        0.0,
        1.26,
        "Circular Embedding",
        ha="center",
        va="center",
        fontsize=16,
        fontweight="bold",
        color=TEXT,
    )

    n = 8
    angles = [2.0 * np.pi * i / n for i in range(n)]
    points = np.array([(np.cos(a), np.sin(a)) for a in angles])

    # Boundary edges in the same counter-clockwise order used by buildOuterplanarEmbedding().
    for i in range(n):
        a = points[i]
        b = points[(i + 1) % n]
        ax.plot([a[0], b[0]], [a[1], b[1]], color=BLUE, linewidth=2.4, zorder=1)

    # Noncrossing diagonals from one fan at vertex 0.
    for j in [2, 3, 4, 5]:
        a = points[0]
        b = points[j]
        ax.plot([a[0], b[0]], [a[1], b[1]], color=LIGHT, linewidth=2.0, zorder=1)

    # Highlight the exact directed-edge step used in the face walk.
    add_arrow(ax, points[0], points[4], BLUE, lw=3.2, z=4)
    add_arrow(ax, points[4], points[5], ORANGE, lw=3.2, z=4)

    # Vertices.
    for i, (x, y) in enumerate(points):
        fill = "white"
        edge = TEXT
        if i == 4:
            fill = BLUE_FILL
            edge = BLUE
        elif i in (0, 5):
            fill = ORANGE_FILL
            edge = ORANGE
        circ = Circle((x, y), 0.073, facecolor=fill, edgecolor=edge, linewidth=1.6, zorder=5)
        ax.add_patch(circ)
        ax.text(
            x * 1.17,
            y * 1.17,
            str(i),
            ha="center",
            va="center",
            fontsize=12.4,
            color=edge if i in (0, 4, 5) else TEXT,
            fontweight="bold" if i in (0, 4, 5) else None,
            zorder=6,
        )

    ax.text(
        -1.18,
        -1.05,
        "arrive on 0 → 4",
        ha="left",
        va="center",
        fontsize=11.2,
        color=BLUE,
        fontweight="bold",
    )
    ax.text(
        0.0,
        -1.18,
        "around 4, sorted neighbors are [5, 0, 3]",
        ha="center",
        va="center",
        fontsize=10.8,
        color=GRAY,
    )
    ax.text(
        0.26,
        -1.05,
        "continue on 4 → 5",
        ha="left",
        va="center",
        fontsize=11.2,
        color=ORANGE,
        fontweight="bold",
    )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / "outerplanar_embedding.pdf", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(FIGURES_DIR / "outerplanar_embedding.png", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


if __name__ == "__main__":
    main()
