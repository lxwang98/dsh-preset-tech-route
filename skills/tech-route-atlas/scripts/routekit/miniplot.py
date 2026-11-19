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
            fit: bool = False, ci: float | None = None, legend: bool = True,
            stats: bool = False):
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
                if ci:                                     # 回归置信带
                    n = len(xs)
                    resid = ys - (k * xs + b)
                    dof = max(n - 2, 1)
                    s = float(np.sqrt((resid ** 2).sum() / dof))
                    xbar = xs.mean()
                    sxx = float(((xs - xbar) ** 2).sum()) or 1e-9
                    half = 1.96 * s * np.sqrt(1.0 / n + (grid - xbar) ** 2 / sxx)
                    ax.fill_between(grid, k * grid + b - half, k * grid + b + half,
                                    color=p.ink3, alpha=0.16, lw=0, zorder=1)
                if stats:
                    from scipy import stats as _st
                    r, pv = _st.pearsonr(xs, ys)
                    ax.text(0.03, 0.95, f"r = {r:.2f}\nP = {pv:.2g}",
                            transform=ax.transAxes, va="top", ha="left",
                            fontsize=T.micro, color=p.ink2)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        if legend and len(groups) > 1:
            _legend(ax, p)

    return draw


def volcano(rows: list[tuple[float, float]], p: Palette, *,
            xlabel: str = "log$_2$ fold change", ylabel: str = "$-$log$_{10}$ P",
            fc_cut: float = 1.0, p_cut: float = 0.05, label_size=None,
            n_label: int = 0, up_colour: str = "#b03a48",
            down_colour: str = "#2e6e9e"):
    """火山图。rows = [(log2FC, P)]。

    四象限着色：|FC|≥fc_cut 且 P<p_cut → 上调（红）/ 下调（绿）；
    只有一边达标 → 中性灰；都不达标 → 更浅的灰。
    阈值线：竖虚线 ±fc_cut，横虚线 −log10(p_cut)。
    """
    import math

    def draw(fig):
        ax = _apply(fig, p, grid=False)
        thr = -math.log10(max(p_cut, 1e-300))
        xs = [max(min(r[0], 12.0), -12.0) for r in rows]
        ys = [-math.log10(max(r[1], 1e-300)) for r in rows]
        for x, y in zip(xs, ys):
            if y >= thr and x >= fc_cut:
                c, a, s = up_colour, 0.95, 16.0
            elif y >= thr and x <= -fc_cut:
                c, a, s = down_colour, 0.95, 16.0
            elif y >= thr or abs(x) >= fc_cut:
                c, a, s = p.ink3, 0.55, 9.0
            else:
                c, a, s = p.rule, 0.75, 7.0
            ax.scatter([x], [y], s=s, color=c, edgecolor="none", alpha=a, zorder=3)

        ax.axhline(thr, color=p.ink3, lw=0.6, ls=(0, (4, 3)), zorder=1)
        for xv in (fc_cut, -fc_cut):
            ax.axvline(xv, color=p.ink3, lw=0.6, ls=(0, (4, 3)), zorder=1)

        if n_label:
            # 只标真正显著的，左右分侧放标注，天然避开互相压
            cand = [i for i in range(len(ys)) if ys[i] >= thr and abs(xs[i]) >= fc_cut]
            for k, i in enumerate(sorted(cand, key=lambda i: -ys[i])[:n_label]):
                right = xs[i] >= 0
                # 相邻标注上下错开，避免同一点附近的两个标签叠在一起
                ax.annotate(f"g{i + 1}", (xs[i], ys[i]),
                            fontsize=(label_size or T.micro * 0.9), color=p.ink2,
                            xytext=(4 if right else -4, 2 + (k % 2) * 8),
                            textcoords="offset points",
                            ha="left" if right else "right", zorder=4)

        ax.set_xlabel(xlabel, fontsize=T.micro, color=p.ink2, labelpad=2)
        ax.set_ylabel(ylabel, fontsize=T.micro, color=p.ink2, labelpad=2)

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


# ------------------------------------------------------------------ manhattan

_MANHATTAN_A = "#3f7099"      # even chromosomes
_MANHATTAN_B = "#a8c2d6"      # odd chromosomes
_MANHATTAN_HIT = "#c0392b"    # p < genome-wide  (qqman highlight colour)
_MANHATTAN_SUG = "#2f9e44"    # suggestive peak


def manhattan(p: Palette, *, nchr: int = 12, n_per_chr: int = 150, seed: int = 11,
              labels: bool = True, ymax: float = 8.4, peak_chr=(2, 5, 8),
              genome_wide: float = 6.0, suggestive: float = 4.0,
              data: dict[int, list[float]] | None = None,
              label_size: float = 5.2):
    """GWAS Manhattan — x is cumulative chromosome position, y is -log10(P).

    Visual grammar (do not drop any of it, a bare dot cloud is not a Manhattan):
    alternating chromosome colours, a solid genome-wide threshold, a dashed
    suggestive threshold, and peaks recoloured red / green.  R equivalent is
    ``qqman::manhattan(..., highlight=...)``; the cumulative-position trick is
    the usual ``axisdf$cumulative`` dplyr recipe.

    Pass ``data={chrom: [p_values]}`` to plot real p-values; otherwise a
    schematic set is generated (exponential null + gaussian peaks) and the
    caption must say "schematic".

    ``labels=False`` drops all tick text — use it below ~25 mm panel width.
    """
    def draw(fig):
        import matplotlib as mpl
        import numpy as np

        mpl.rcParams["font.family"] = "serif"
        mpl.rcParams["font.serif"] = ["Cambria", "Times New Roman", "DejaVu Serif"]
        ax = _apply(fig, p, grid=False)
        rng = np.random.default_rng(seed)
        pos = 0.0
        ticks, labs = [], []
        for c in range(nchr):
            if data is not None:
                pv = np.asarray(data.get(c + 1, []), dtype=float)
                pv = pv[(pv > 0) & (pv <= 1)]
                y = -np.log10(pv) if pv.size else np.zeros(0)
            else:
                n = n_per_chr
                y = rng.exponential(0.62, n)
                if c in set(peak_chr):
                    k = int(rng.integers(int(n * 0.30), int(n * 0.70)))
                    bump = np.exp(-((np.arange(n) - k) ** 2) / (2 * (n * 0.022) ** 2))
                    y = np.maximum(y, bump * rng.uniform(genome_wide + 0.3, ymax - 0.4))
            n = max(len(y), 1)
            x = pos + (np.arange(len(y)) + rng.random(len(y))) / n * 0.92
            col = np.where(y >= genome_wide, _MANHATTAN_HIT,
                           np.where(y >= suggestive, _MANHATTAN_SUG,
                                    _MANHATTAN_A if c % 2 == 0 else _MANHATTAN_B))
            ax.scatter(x, y, s=1.1, color=col, linewidths=0, zorder=2, alpha=0.9)
            ticks.append(pos + 0.47)
            labs.append(str(c + 1) if c < 22 else ("X" if c == 22 else "Y"))
            pos += 1.0
        ax.axhline(genome_wide, color="#3b4a57", lw=0.65, zorder=1)
        ax.axhline(suggestive, color="#9fb0be", lw=0.55, ls=(0, (2.2, 1.8)),
                   zorder=1)
        ax.set_xlim(0, nchr)
        ax.set_ylim(0, ymax)
        if labels:
            ax.set_xticks(ticks)
            ax.set_xticklabels(labs)
            ax.set_yticks([t for t in (0, 4, 8) if t <= ymax])
            ax.tick_params(labelsize=label_size)
        else:
            ax.set_xticks([])
            ax.set_yticks([])
        return ax

    return draw


__all__ = ["bars", "lines", "survival", "heat", "scatter", "volcano",
           "sparkline", "manhattan", "roc", "forest"]


# ------------------------------------------------------------------ roc

def roc(curves: dict[str, tuple[list[float], list[float]]], p: Palette, *,
        xlabel: str = "1 − Specificity", ylabel: str = "Sensitivity",
        diagonal: bool = True, legend: bool = True,
        auc: dict[str, float] | None = None):
    """ROC 曲线：`curves = {"Model": (fpr, tpr), ...}`，两轴均 0-1。

    `auc={"Model": 0.86}` 给了就把 AUC 写进图例，比单独标文字省地方；
    临床诊断/预测模型图里 AUC 是硬指标，别省略。
    """

    def draw(fig):
        ax = _apply(fig, p)
        if diagonal:
            ax.plot([0, 1], [0, 1], ls=(0, (2.2, 1.8)), lw=0.7, color=p.ink3, zorder=1)
        for i, (name, (fpr, tpr)) in enumerate(curves.items()):
            lab = name
            if auc and name in auc:
                lab = f"{name}  AUC {auc[name]:.2f}"
            ax.plot(fpr, tpr, color=p.accent(i), lw=1.25, label=lab, zorder=3,
                    solid_capstyle="round")
        ax.set_xlim(0, 1.0)
        ax.set_ylim(0, 1.03)
        ax.set_xticks([0, 0.5, 1])
        ax.set_yticks([0, 0.5, 1])
        ax.set_xticklabels(["0", "0.5", "1"])
        ax.set_yticklabels(["0", "0.5", "1"])
        ax.set_xlabel(xlabel, fontsize=T.micro, color=p.ink2, labelpad=1.5)
        ax.set_ylabel(ylabel, fontsize=T.micro, color=p.ink2, labelpad=1.5)
        if legend:
            _legend(ax, p, loc="lower right", size=T.micro - 0.6)
        return ax

    return draw


# ------------------------------------------------------------------ forest

def forest(rows, p: Palette, *, xlabel: str = "Hazard ratio (95% CI)",
           null: float = 1.0, log: bool = False, values: bool = True,
           sizes: list[float] | None = None, label_size: float | None = None):
    """森林图：`rows = [(label, est, lo, hi), ...]`，自上而下按给定顺序画。

    点估计方块 + 95% CI 横线 + 无效线（HR/OR 为 1，均值差为 0）。
    `values=True` 时在图右侧空列写 `est (lo–hi)`，投稿图的标准做法。
    """

    def draw(fig):
        ax = _apply(fig, p)
        n = len(rows)
        ys = list(range(n))[::-1]
        for i, r in enumerate(rows):
            y = ys[i]
            est, lo, hi = float(r[1]), float(r[2]), float(r[3])
            ax.plot([lo, hi], [y, y], color=p.ink3, lw=1.0,
                    solid_capstyle="butt", zorder=2)
            ms = (sizes[i] / 22.0) if (sizes and i < len(sizes)) else 3.2
            ax.plot([est], [y], marker="s", ms=max(2.2, min(ms, 6.0)),
                    color=p.accent(0), zorder=3, mew=0)
            if values:
                txt = f"{est:.2f} ({lo:.2f}–{hi:.2f})"
                ax.text(1.03, y, txt, transform=ax.get_yaxis_transform(),
                        ha="left", va="center", fontsize=(label_size or T.micro) - 0.4,
                        color=p.ink2, clip_on=False)
        if null is not None:
            ax.axvline(null, color=p.ink3, lw=0.7, ls=(0, (2.2, 1.8)), zorder=1)
        if log:
            from matplotlib.ticker import NullLocator
            ax.set_xscale("log")
            # matplotlib's default log labels are mathtext (4×10⁻¹) and collide
            # at inset size; force plain decade-ish ticks inside the data range.
            lo_r = min(float(r[2]) for r in rows)
            hi_r = max(float(r[3]) for r in rows)
            cand = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
            ticks = [c for c in cand if lo_r * 0.85 <= c <= hi_r * 1.15] or [null]
            ax.set_xticks(ticks)
            ax.set_xticklabels([f"{t:g}" for t in ticks])
            ax.xaxis.set_minor_locator(NullLocator())
        ax.set_ylim(-0.7, n - 0.3)
        ax.set_yticks(ys)
        ax.set_yticklabels([str(r[0]) for r in rows], fontsize=label_size or T.micro)
        ax.tick_params(axis="y", length=0, pad=2)
        for side in ("left", "top", "right"):
            ax.spines[side].set_visible(False)
        ax.set_xlabel(xlabel, fontsize=T.micro, color=p.ink2, labelpad=1.5)
        return ax

    return draw



