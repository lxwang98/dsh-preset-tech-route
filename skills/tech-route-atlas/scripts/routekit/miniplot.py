"""Small, palette-locked matplotlib insets for route figures.

A route diagram usually needs one or two real data panels (a survival curve,
a bar of SCFA concentrations, a heat strip). They must look like they were
drawn by the same hand as the schematic, so this module fixes the styling:
no top/right spines, palette series, tick labels at the caption size, and
nothing larger than the body type.

    from routekit import miniplot as mp
    c.plot(Box(120, 20, 40, 26), mp.survival([("WGBR", t, s), ("ST", t, s)], c.p))

Each factory returns `draw(fig)` suitable for `Canvas.plot`.
"""
from __future__ import annotations

import math

from .palette import Palette
from .tokens import S as Stroke
from .tokens import T


def _apply(fig, p: Palette, *, grid: bool = False, offset_x: float = 0.0):
    import matplotlib as mpl

    # CJK-safe defaults for insets that carry Chinese axis labels
    mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial", "DejaVu Sans"]
    mpl.rcParams["axes.unicode_minus"] = False
    ax = fig.axes[0] if fig.axes else fig.add_axes((0, 0, 1, 1))
    # Absolute mm margins instead of matplotlib's fractional defaults: on a
    # 55 x 21 mm inset the default 12.5 % left margin eats 7 mm of plot.
    w_mm = fig.get_size_inches()[0] * 25.4
    h_mm = fig.get_size_inches()[1] * 25.4
    left = min(0.34, 6.4 / max(w_mm, 1.0))
    bottom = min(0.34, 5.6 / max(h_mm, 1.0))
    ax.set_position((left, bottom, 1 - left - 0.018, 1 - bottom - 0.022))
    ax.set_facecolor("none")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(p.ink3)
        ax.spines[side].set_linewidth(0.6)
    ax.tick_params(colors=p.ink2, labelsize=T.micro, width=0.5, length=2,
                   pad=1.5)
    if grid:
        ax.grid(True, color=p.rule, lw=0.4, alpha=0.7, zorder=0)
        ax.set_axisbelow(True)
    else:
        ax.grid(False)
    return ax


def _legend(ax, p: Palette, *, ncol: int = 1, loc: str = "best", size: float = T.micro):
    leg = ax.legend(frameon=False, fontsize=size, ncol=ncol, loc=loc,
                    handlelength=1.1, handletextpad=0.4, borderaxespad=0.2,
                    labelcolor=p.ink2)
    return leg


# ------------------------------------------------------------------ bars

def bars(series: dict[str, list[float]], p: Palette, *, labels: list[str] | None = None,
         ylabel: str = "", xlabel: str = "", errors: dict[str, list[float]] | None = None,
         legend: bool = True, zero_base: bool = True):
    def draw(fig):
        ax = _apply(fig, p, grid=True)
        names = list(series)
        n = len(names)
        m = len(next(iter(series.values())))
        width = 0.72 / n
        xs = list(range(m))
        for i, name in enumerate(names):
            vals = series[name]
            off = (i - (n - 1) / 2) * width
            pos = [x + off for x in xs]
            ax.bar(pos, vals, width=width * 0.92, color=p.accent(i), label=name,
                   edgecolor="none", zorder=3)
            if errors and name in errors:
                ax.errorbar(pos, vals, yerr=errors[name], fmt="none",
                            ecolor=p.ink3, elinewidth=0.6, capsize=1.4, zorder=4)
        if labels:
            ax.set_xticks(xs)
            ax.set_xticklabels(labels)
        if zero_base:
            ax.set_ylim(bottom=0)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        if legend and n > 1:
            _legend(ax, p, ncol=min(n, 3), size=T.micro)

    return draw


# ------------------------------------------------------------------ lines

def lines(series: dict[str, tuple[list[float], list[float]]], p: Palette, *,
          xlabel: str = "", ylabel: str = "", legend: bool = True,
          markers: bool = False, log: bool = False, band: dict[str, tuple] | None = None):
    def draw(fig):
        ax = _apply(fig, p, grid=False)
        for i, (name, (xs, ys)) in enumerate(series.items()):
            ax.plot(xs, ys, color=p.accent(i), lw=1.1, label=name,
                    marker="o" if markers else None, ms=1.8, zorder=3)
            if band and name in band:
                lo, hi = band[name]
                ax.fill_between(xs, lo, hi, color=p.accent(i), alpha=0.16, lw=0)
        if log:
            ax.set_yscale("log")
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        if legend:
            _legend(ax, p)

    return draw


# ------------------------------------------------------------------ survival

def survival(curves: dict[str, tuple[list[float], list[float]]], p: Palette, *,
             xlabel: str = "Age (months)", ylabel: str = "Survival (%)",
             xticks: list[float] | None = None, legend: bool = True):
    """Kaplan–Meier steps: `curves = {"WGBR": (times, probs), ...}` with probs 0-1."""

    def draw(fig):
        ax = _apply(fig, p)
        for i, (name, (ts, ps)) in enumerate(curves.items()):
            ax.step(ts, [v * 100 for v in ps], where="post", color=p.accent(i),
                    lw=1.2, label=name, zorder=3)
        ax.set_ylim(0, 102)
        if xticks:
            ax.set_xticks(xticks)
        ax.set_xlabel(xlabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        ax.set_ylabel(ylabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        if legend:
            _legend(ax, p, loc="lower left", size=T.micro - 0.5)

    return draw


# ------------------------------------------------------------------ heat

def heat(matrix: list[list[float]], p: Palette, *, row_labels: list[str] | None = None,
         col_labels: list[str] | None = None, cmap: str = "RdBu_r",
         vmin: float | None = None, vmax: float | None = None, cbar: bool = True,
         center: float | None = 0.0):
    def draw(fig):
        nonlocal cmap
        ax = _apply(fig, p)
        from matplotlib import colormaps
        from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

        if isinstance(cmap, str) and cmap not in colormaps and cmap != "palette":
            hit = [n for n in colormaps if n.lower() == cmap.lower()]
            if hit:
                cmap = hit[0]
        if cmap == "palette":
            lo = p.tint(p.accent(0), 0.75) if hasattr(p, "tint") else "#dfeaf4"
            mid = "#ffffff"
            hi = p.accent(3)
            cmap_obj = LinearSegmentedColormap.from_list("pal", [lo, mid, hi])
        else:
            cmap_obj = cmap
        norm = None
        if (center is not None and vmin is not None and vmax is not None
                and vmin < center < vmax):
            norm = TwoSlopeNorm(vcenter=center, vmin=vmin, vmax=vmax)
        im = ax.imshow(matrix, aspect="auto", cmap=cmap_obj, norm=norm,
                       vmin=vmin, vmax=vmax, interpolation="none")
        if row_labels:
            ax.set_yticks(range(len(row_labels)))
            ax.set_yticklabels(row_labels, fontsize=T.micro - 0.5)
        if col_labels:
            ax.set_xticks(range(len(col_labels)))
            ax.set_xticklabels(col_labels, fontsize=T.micro - 0.5, rotation=0)
        if not row_labels and not col_labels:
            # schematic block (no real axes): keep the grid clean
            ax.set_xticks([])
            ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(length=0)
        if cbar:
            cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02)
            cb.outline.set_visible(False)
            cb.ax.tick_params(labelsize=T.micro - 0.5, colors=p.ink2, length=1.5)

    return draw


# ------------------------------------------------------------------ scatter

def scatter(points: list[tuple[float, float, str]], p: Palette, *,
            xlabel: str = "", ylabel: str = "", size: float = 14.0,
            fit: bool = False, legend: bool = True):
    def draw(fig):
        ax = _apply(fig, p, grid=False)
        groups: dict[str, list[tuple[float, float]]] = {}
        for x, y, g in points:
            groups.setdefault(g, []).append((x, y))
        for i, (g, pts) in enumerate(groups.items()):
            ax.scatter([q[0] for q in pts], [q[1] for q in pts], s=size,
                       color=p.accent(i), label=g, edgecolor="none", alpha=0.9,
                       zorder=3)
        if fit:
            import numpy as np

            xs = np.array([q[0] for q in points], dtype=float)
            ys = np.array([q[1] for q in points], dtype=float)
            if len(xs) > 2:
                k, b = np.polyfit(xs, ys, 1)
                grid = np.linspace(xs.min(), xs.max(), 50)
                ax.plot(grid, k * grid + b, color=p.ink3, lw=0.7, ls=(0, (3, 2)),
                        zorder=2)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        if legend and len(groups) > 1:
            _legend(ax, p)

    return draw


# ------------------------------------------------------------------ sparkline

def sparkline(values: list[float], p: Palette, *, colour: str | None = None,
              fill: bool = True):
    """Axis-free trend for inside a card (no ticks, no spines)."""

    def draw(fig):
        ax = fig.add_axes((0.02, 0.08, 0.96, 0.84))
        col = colour or p.accent(0)
        ax.plot(range(len(values)), values, color=col, lw=1.0)
        if fill:
            ax.fill_between(range(len(values)), values, min(values), color=col,
                            alpha=0.14, lw=0)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        pad = (max(values) - min(values)) * 0.15 or 1
        ax.set_ylim(min(values) - pad, max(values) + pad)

    return draw


__all__ = ["bars", "lines", "survival", "heat", "scatter", "sparkline"]
