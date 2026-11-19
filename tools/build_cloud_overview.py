# -*- coding: utf-8 -*-
"""云端素材库 · 六类主题总览（A3 横版 420×297）。

用途：README 顶部的一张"视觉索引"——让人一眼看出云端库里有什么。
**这张图不放 id**（A3 上 96 件素材的文字必然糊成一团），id 全在
`assets/remote/sheets/<theme>.png` 的六张全尺寸目录页里。

素材选择逻辑与 `build_cloud_sheets.py` 完全共用（同一套三道闸 + 白名单），
保证总览与目录页不会漂移。

    python tools/build_cloud_overview.py
    → assets/remote/sheets/overview.pptx / .png / .pdf
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "tech-route-atlas" / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))

from routekit import Canvas, Box  # noqa: E402
from routekit.audit import format_report, static_report  # noqa: E402
from routekit.export import render  # noqa: E402
from routekit.palette import P, shade, tint  # noqa: E402

import build_cloud_sheets as sheets  # noqa: E402

OUT = ROOT / "assets" / "remote" / "sheets"

PAGES = [
    ("organs", "器官 · 组织", 0, 16),
    ("cells", "细胞 · 免疫", 3, 16),
    ("lab", "仪器 · 器皿", 0, 16),
    ("microbes", "微生物 · 病毒", 1, 16),
    ("people", "人物 · 队列", 4, 8),
    ("clinical", "临床 · 场景", 2, 16),
]

W, H = 420.0, 297.0
M = 12.0
GAP = 8.0
BAND = 8.0
COLS, ROWS = 4, 4


def picks() -> dict:
    """与 build_cloud_sheets 同源的选件结果。"""
    out = {}
    for key, kws in sheets.KW_THEMES:
        seen: dict[str, int] = {}
        out[key] = [r for r in sheets.by_keywords(kws) if sheets.keep(r, seen)][:16]
    for key, pairs in sheets.CURATED.items():
        out[key] = sheets.by_whitelist(pairs)  # 白名单不再折叠，保持人工顺序
    return out


def main() -> int:
    recs = picks()
    cv = Canvas(W, H, palette="cell", margin=0.0, title="cloud-overview")
    p = P("cell")

    cv.text(Box(M, 7.4, W - 2 * M, 9.0),
            "云端素材库 · 六类主题总览", size=17.0, bold=True,
            colour=shade(p.accents[0], 0.45), align="l")
    cv.text(Box(M, 16.8, W - 2 * M, 5.6),
            "4978 件 · 按需下载、不占本地 · Servier CC BY 3.0 / DBCLS CC BY 4.0 / "
            "Reactome CC BY 4.0 / openclipart CC0",
            size=7.8, colour=p.ink2, align="l")

    top = 25.0
    grid_h = H - top - 14.0
    pw = (W - 2 * M - 2 * GAP) / 3.0
    ph = (grid_h - GAP) / 2.0

    for i, (key, label, acc, cap) in enumerate(PAGES):
        col, row = i % 3, i // 3
        b = Box(M + col * (pw + GAP), top + row * (ph + GAP), pw, ph)
        cv.rect(b, fill="#ffffff", line=p.rule, lw=0.6, radius=2.2)

        band = Box(b.x, b.y, b.w, BAND)
        cv.rect(band, fill=shade(p.accents[acc], 0.28), line=None, radius=2.2)
        cv.rect(Box(band.x, band.y + band.h - 3.0, band.w, 3.0),
                fill=shade(p.accents[acc], 0.28), line=None, radius=0.0)
        cv.text(Box(band.x + 4.0, band.y, band.w * 0.6, band.h),
                label, size=9.4, bold=True, colour="#ffffff", align="l")

        got = recs.get(key, [])[:cap]
        cv.text(Box(band.x + band.w - 24.0, band.y, 20.0, band.h),
                f"{len(got)} 件", size=7.8, colour=tint(p.accents[acc], 0.70), align="r")

        cell = Box(b.x + 2.6, b.y + BAND + 2.2, b.w - 5.2, b.h - BAND - 5.0)
        for j, rec in enumerate(got[:COLS * ROWS]):
            r_, c_ = divmod(j, COLS)
            slot = Box(cell.x + c_ * (cell.w / COLS), cell.y + r_ * (cell.h / ROWS),
                       cell.w / COLS, cell.h / ROWS)
            cv.icon(slot.inner(2.0), rec.id, px=460)

    cv.text(Box(M, H - 11.6, W - 2 * M, 5.4),
            "每件的 id、类别与许可见 assets/remote/sheets/ 下六张全尺寸目录页 —— "
            "挑中哪件，把 id 写进 cv.icon(box, id) 即可（首次使用自动下载）。",
            size=7.4, colour=p.ink3, align="l")

    pptx = OUT / "overview.pptx"
    cv.save(pptx)
    print(format_report(static_report(cv, mode="print")))
    print(render(pptx, OUT, dpi=300, stem="overview", also_pdf=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
