from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


FIGURES_DIR = Path(__file__).resolve().parent / "figures"


BLUE = "#365C99"
BLUE_FILL = "#EDF3FF"
GREEN = "#2F8A57"
GREEN_FILL = "#EDF8F1"
ORANGE = "#D46A1D"
ORANGE_FILL = "#FFF4E8"
RED = "#C64A45"
RED_FILL = "#FDEEEE"
GRAY = "#738195"
BORDER = "#D6DCE5"
TEXT = "#1A1A1A"


def setup_panel(ax, title):
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_aspect("equal")
    ax.axis("off")

    panel = FancyBboxPatch(
        (0.02, 0.03),
        0.96,
        0.94,
        boxstyle="round,pad=0.012,rounding_size=0.03",
        linewidth=1.5,
        edgecolor=BORDER,
        facecolor="white",
        zorder=0,
    )
    ax.add_patch(panel)
    ax.text(
        0.06,
        0.93,
        title,
        fontsize=13,
        fontweight="bold",
        color=TEXT,
        ha="left",
        va="top",
        zorder=5,
    )


def draw_wall_and_level(ax, y_level=0.62):
    wall_x0, wall_y0 = 0.16, 0.16
    wall_x1, wall_y1 = 0.22, 0.84
    ax.plot(
        [wall_x0, wall_x1],
        [wall_y0, wall_y1],
        color=BLUE,
        linewidth=4.5,
        solid_capstyle="round",
        zorder=2,
    )
    ax.text(
        0.10,
        0.52,
        "active\nwall",
        color=BLUE,
        fontsize=11.5,
        ha="center",
        va="center",
        rotation=83,
        zorder=3,
    )

    ax.plot(
        [0.07, 0.94],
        [y_level, y_level],
        color=GRAY,
        linewidth=2.2,
        linestyle="--",
        zorder=1,
    )
    ax.text(
        0.72,
        y_level + 0.05,
        "locked y level",
        color=GRAY,
        fontsize=10.5,
        ha="left",
        va="bottom",
        zorder=3,
    )
    return y_level


def point(ax, x, y, color, label=None, filled=True, size=180, zorder=5):
    face = color if filled else "white"
    ax.scatter(
        [x],
        [y],
        s=size,
        facecolors=face,
        edgecolors=color,
        linewidths=2.0,
        zorder=zorder,
    )
    if label:
        ax.text(
            x + 0.018,
            y + 0.034,
            label,
            color=color,
            fontsize=11.5,
            fontweight="bold",
            zorder=zorder + 1,
        )


def state_box(ax, x, y, w, h, title, lines, fill):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.4,
        edgecolor=BORDER,
        facecolor=fill,
        zorder=2,
    )
    ax.add_patch(box)
    ax.text(
        x + 0.03,
        y + h - 0.06,
        title,
        fontsize=9.9,
        fontweight="bold",
        color=TEXT,
        ha="left",
        va="top",
        zorder=3,
    )
    ax.text(
        x + 0.03,
        y + h - 0.14,
        "\n".join(lines),
        fontsize=9.4,
        color=TEXT,
        ha="left",
        va="top",
        linespacing=1.35,
        zorder=3,
    )


def draw_cross(ax, x, y, color):
    dx = 0.028
    dy = 0.028
    ax.plot([x - dx, x + dx], [y - dy, y + dy], color=color, linewidth=2.2, zorder=7)
    ax.plot([x - dx, x + dx], [y + dy, y - dy], color=color, linewidth=2.2, zorder=7)


def main():
    fig, axes = plt.subplots(1, 3, figsize=(16.2, 5.0), dpi=220)
    fig.patch.set_facecolor("white")

    y0 = 0.62

    # Panel 1: lock creation by a hole-top event.
    ax = axes[0]
    setup_panel(ax, "1. Hole-top event locks the wall")
    draw_wall_and_level(ax, y0)

    h_x = 0.77
    point(ax, h_x, y0, ORANGE, label="h")
    ax.add_patch(
        FancyArrowPatch(
            posA=(0.22, y0),
            posB=(h_x - 0.03, y0),
            arrowstyle="-|>",
            mutation_scale=20,
            linewidth=2.8,
            linestyle="--",
            color=ORANGE,
            zorder=4,
        )
    )
    ax.text(
        h_x - 0.02,
        y0 + 0.17,
        "topmost hole vertex",
        color=ORANGE,
        fontsize=11.5,
        ha="right",
        va="center",
        bbox={"boxstyle": "round,pad=0.24", "facecolor": "white", "edgecolor": "none", "alpha": 0.95},
        zorder=6,
    )
    state_box(
        ax,
        0.28,
        0.12,
        0.58,
        0.30,
        "State after setHoleTopHelper(...)",
        [
            "helper = h",
            "minLockedHelper = h",
            "maxLockedHelper = h",
            "lockSameLevel = true, lockedAtY = h.y",
            "lockedComponentId = component(h)",
        ],
        ORANGE_FILL,
    )

    # Panel 2: same-level updates by the same component.
    ax = axes[1]
    setup_panel(ax, "2. Same y-level updates are filtered")
    draw_wall_and_level(ax, y0)

    u_x, v_x = 0.37, 0.67
    blocked_x = 0.53
    point(ax, u_x, y0, GREEN, label="u")
    point(ax, v_x, y0, GREEN, label="v")
    point(ax, blocked_x, y0, RED, filled=False, size=165, zorder=5)
    draw_cross(ax, blocked_x, y0, RED)

    ax.text(
        0.29,
        0.76,
        "same component + same y -> allowed",
        color=GREEN,
        fontsize=11.0,
        ha="left",
        va="center",
        bbox={"boxstyle": "round,pad=0.24", "facecolor": "white", "edgecolor": "none", "alpha": 0.95},
        zorder=6,
    )
    ax.text(
        0.60,
        0.46,
        "other component at same y\ncannot overwrite",
        color=RED,
        fontsize=10.3,
        ha="center",
        va="center",
        bbox={"boxstyle": "round,pad=0.24", "facecolor": "white", "edgecolor": "none", "alpha": 0.95},
        zorder=6,
    )
    ax.text(u_x, y0 - 0.085, "min", color=GREEN, fontsize=10.2, ha="center", zorder=6)
    ax.text(v_x, y0 - 0.085, "max", color=GREEN, fontsize=10.2, ha="center", zorder=6)
    state_box(
        ax,
        0.22,
        0.12,
        0.66,
        0.28,
        "Ordinary overwrite on the locked level",
        [
            "same y + same component -> update allowed",
            "helper = latest allowed candidate",
            "min/max track the leftmost and",
            "rightmost allowed helpers",
        ],
        GREEN_FILL,
    )

    # Panel 3: choosing the closer endpoint for a later bridge.
    ax = axes[2]
    setup_panel(ax, "3. getBridgeTarget() picks the nearer extreme")
    draw_wall_and_level(ax, y0)

    min_x, max_x, q_x = 0.36, 0.61, 0.82
    point(ax, min_x, y0, GREEN, label="u")
    point(ax, max_x, y0, GREEN, label="v")
    point(ax, q_x, y0, ORANGE, label="q", filled=False)

    ax.add_patch(
        FancyArrowPatch(
            posA=(q_x - 0.02, y0 + 0.01),
            posB=(max_x + 0.02, y0 + 0.01),
            arrowstyle="-|>",
            mutation_scale=18,
            linewidth=2.8,
            linestyle="--",
            color=ORANGE,
            zorder=4,
        )
    )
    ax.plot(
        [q_x - 0.02, min_x + 0.02],
        [y0 - 0.03, y0 - 0.03],
        color=GRAY,
        linewidth=2.0,
        linestyle=(0, (5, 4)),
        zorder=3,
    )
    ax.text(
        q_x - 0.03,
        y0 + 0.16,
        "later hole-top query",
        color=ORANGE,
        fontsize=11.2,
        ha="right",
        va="center",
        bbox={"boxstyle": "round,pad=0.24", "facecolor": "white", "edgecolor": "none", "alpha": 0.95},
        zorder=6,
    )
    ax.text(
        0.63,
        0.48,
        "chosen target",
        color=ORANGE,
        fontsize=10.8,
        ha="left",
        va="center",
        zorder=6,
    )
    state_box(
        ax,
        0.19,
        0.12,
        0.68,
        0.28,
        "Bridge-target query",
        [
            "compare |q.x - min.x| and |q.x - max.x|",
            "if left distance <= right distance",
            "    return minLockedHelper",
            "else return maxLockedHelper",
        ],
        BLUE_FILL,
    )

    fig.text(
        0.5,
        0.06,
        "Below lockedAtY, an ordinary update replaces the helper normally and clears the same-level lock.",
        ha="center",
        va="center",
        fontsize=11.0,
        color=GRAY,
    )

    fig.subplots_adjust(left=0.02, right=0.985, top=0.96, bottom=0.16, wspace=0.08)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / "helper_locking.pdf", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(FIGURES_DIR / "helper_locking.png", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


if __name__ == "__main__":
    main()
