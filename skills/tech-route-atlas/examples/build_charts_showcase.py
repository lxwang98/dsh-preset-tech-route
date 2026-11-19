# -*- coding: utf-8 -*-
"""三张最常被问到的统计图：曼哈顿 / 火山 / 带置信带的散点+拟合线。

左中右三个面板都用 routekit.miniplot 的生成器现场画（示意数据，
图注必须写 schematic）。目的：证明"库里没有静态素材也能出这几张图"。

    python charts_showcase.py → out/charts-showcase.{pptx,png,pdf}
"""
import math
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "scripts"))

import numpy as np

from routekit import Canvas, Box
from routekit import miniplot as mp
from routekit.audit import format_report, static_report
from routekit.export import deliver
from routekit.palette import P, shade

OUT = str(__import__("pathlib").Path(__file__).resolve().parent / "out")
rng = np.random.default_rng(7)


def volcano_rows(n=900):
    """log2FC 与 P 的示意分布：两侧各一条显著带 + 中间无差别的灰云。"""
    rows = []
    for _ in range(n):
        fc = rng.normal(0, 1.15)
        # 效应越大 P 越小的倾向 + 噪声
        z = abs(fc) * rng.gamma(2.0, 0.9) + rng.normal(0, 0.6)
        pv = max(min(10 ** (-z), 0.999), 1e-9)
        rows.append((float(fc), float(pv)))
    return rows


def scatter_points(n=140):
    x = rng.uniform(0, 10, n)
    y = 0.85 * x + rng.normal(0, 1.15, n) + 1.2
    half = n // 2
    return [(float(a), float(b), "Training" if i < half else "Validation")
            for i, (a, b) in enumerate(zip(x, y))]


def main() -> int:
    cv = Canvas(300, 104, palette="cell", margin=0.0, title="charts-showcase")
    p = P("cell")

    cv.text(Box(8, 4.2, 284, 7.0),
            "三张常用统计图 · 由数据现场生成（miniplot）", size=13.0, bold=True,
            colour=shade(p.accents[0], 0.45), align="l")
    cv.text(Box(8, 11.4, 284, 4.6),
            "示意数据（schematic）；真实作图时把 mp.manhattan / mp.volcano / "
            "mp.scatter 的入参换成你的统计结果即可",
            size=7.4, colour=p.ink2, align="l")

    panels = [
        ("A  曼哈顿图  mp.manhattan", 0),
        ("B  火山图  mp.volcano", 3),
        ("C  回归 + 95% 置信带  mp.scatter(ci=)", 1),
    ]
    x = 8.0
    w = 92.0
    gap = 4.0
    for title, acc in panels:
        b = Box(x, 18.0, w, 80.0)
        cv.rect(b, fill="#ffffff", line=p.rule, lw=0.6, radius=2.2)
        band = Box(b.x, b.y, b.w, 6.6)
        cv.rect(band, fill=shade(p.accents[acc], 0.28), line=None, radius=2.2)
        cv.rect(Box(band.x, band.y + band.h - 2.6, band.w, 2.6),
                fill=shade(p.accents[acc], 0.28), line=None, radius=0.0)
        cv.text(Box(band.x + 3.0, band.y, band.w - 6.0, band.h),
                title, size=8.4, bold=True, colour="#ffffff", align="l")
        plot = Box(b.x + 2.0, b.y + 8.4, b.w - 4.0, b.h - 11.0)

        if title.startswith("A"):
            cv.plot(plot, mp.manhattan(p, nchr=12, n_per_chr=130, seed=5,
                                       labels=True, ymax=8.4), dpi=600)
        elif title.startswith("B"):
            cv.plot(plot, mp.volcano(volcano_rows(), p, fc_cut=1.0, p_cut=0.05,
                                     n_label=4), dpi=600)
        else:
            cv.plot(plot, mp.scatter(scatter_points(), p, xlabel="SCFA (μmol/g)",
                                     ylabel="GPR43 (a.u.)", fit=True, ci=0.95,
                                     stats=True), dpi=600)
        x += w + gap

    cv.text(Box(8, 97.4, 284, 4.2),
            "注：三图均为 illustrative / schematic，用于说明图示规范，不代表任何实测数据。",
            size=6.8, colour=p.ink3, align="l")

    pptx = rf"{OUT}\charts-showcase.pptx"
    cv.save(pptx)
    print(format_report(static_report(cv, mode="print")))
    print(deliver(pptx, OUT, dpi=600))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


