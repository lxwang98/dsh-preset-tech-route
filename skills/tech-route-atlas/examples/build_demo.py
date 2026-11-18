"""Demo: a 7-panel technical route for a mouse gut-microbiome / lifespan study.

Run:  python build_demo.py [outdir]
Writes <outdir>/black-rice-route.pptx  +  .png / .pdf at 600 dpi.

The layout is pure millimetres on a 16:9 slide (254 x 142.9 mm) so the export
is reproducible. Every panel is built from the same three primitives:
zone -> rows -> (icon | text | chip).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from routekit import Canvas, Box, T, S, G, R, CANVAS  # noqa: E402
from routekit import miniplot as mp  # noqa: E402
from routekit.audit import static_report, format_report  # noqa: E402


def split(b: Box, weights: list[float], gap: float) -> list[Box]:
    total = sum(weights)
    usable = b.w - gap * (len(weights) - 1)
    out, x = [], b.x
    for wt in weights:
        w = usable * wt / total
        out.append(Box(x, b.y, w, b.h))
        x += w + gap
    return out


# ------------------------------------------------------------------- build
def build(out_dir: Path) -> Path:
    W, H = CANVAS.slide_16x9
    cv = Canvas(W, H, palette="cell", title="Whole-grain black rice route")
    p = cv.p
    cv.bg(p.paper)

    M = 4.0
    cv.text(Box(M, 3.4, 152, 7.4),
            "全谷物黑米经肠道菌群–SCFA–炎症轴延长小鼠健康寿命",
            size=14.5, bold=True, align="l", colour=p.ink)
    cv.text(Box(M + 154, 4.6, W - 2 * M - 154, 5.2),
            "多组学 + mGWAS 解析宿主–菌群互作，并在人群队列中验证",
            size=7.2, align="r", colour=p.ink2)
    cv.divider(M, 11.8, W - M, 11.8, colour=p.rule, lw=S.thin)

    top = Box(M, 13.6, W - 2 * M, 56.0)
    bot = Box(M, 71.4, W - 2 * M, H - 71.4 - 9.6)
    z1, z2, z3, z4 = split(top, [47, 79, 67, 45], 2.6)
    z5, z6, z7 = split(bot, [108, 72, 58], 2.6)

    zone1(cv, z1)
    zone2(cv, z2)
    zone3(cv, z3)
    zone4(cv, z4)
    zone5(cv, z5)
    zone6(cv, z6)
    zone7(cv, z7)

    cv.text(Box(M, H - 8.4, W - 2 * M, 5.2),
            "整合路线揭示：黑米 → 菌群重塑 → SCFA↑ → 屏障/炎症改善 → 健康寿命↑；"
            "宿主遗传背景决定菌群–表型关联的强度",
            size=7.0, align="c", colour=p.ink2)

    out_dir.mkdir(parents=True, exist_ok=True)
    pptx = cv.save(out_dir / "black-rice-route.pptx")

    issues = static_report(cv, mode="deck")
    print(format_report(issues))
    if cv.warnings:
        print("warnings:")
        for w in cv.warnings[:12]:
            print("  -", w)

    from routekit import export

    dpi = int(os.environ.get("ROUTEKIT_DPI", "600"))
    print(export.render(pptx, out_dir, dpi=dpi, stem="black-rice-route"))
    return pptx


# ------------------------------------------------------------------ zone 1
def zone1(cv: Canvas, b: Box):
    p = cv.p
    c = cv.zone(b, "1  实验设计  Study design", acc=0)

    arms = [("WGBR", "全谷物黑米", 0, "bioicons/servier/Animals/mouse-gray"),
            ("WGWR", "全谷物白米", 1, "bioicons/servier/Animals/mouse-gray"),
            ("PR", "精白米", 2, "bioicons/servier/Animals/mouse-gray"),
            ("ST", "标准饲料 AIN93", 3, "bioicons/servier/Animals/mouse-gray")]
    area = Box(c.x, c.y, c.w, c.h - 10.4)
    for (code, name, acc, ic), r in zip(arms, area.rows(4, gap=1.8)):
        cv.chip(Box(r.x, r.y + (r.h - 6.2) / 2, 15.0, 6.2), code, acc=acc,
                size=6.0, bold=True, mode="solid")
        cv.icon(Box(r.x + 16.6, r.y, 12.6, r.h), ic, pad=0.5)
        cv.text(Box(r.x + 30.2, r.y, r.w - 30.4, r.h), name, size=6.6, align="l",
                colour=p.ink)

    note = Box(c.x, c.y2 - 9.2, c.w, 9.2)
    cv.rect(note, fill=p.wash, line=None, radius=R.chip)
    cv.text(note.inner(1.2), "C57BL/6J · 400 只 · 雌雄各半\nn = 100/组 · 全程 33 月龄",
            size=6.0, colour=p.ink2, line_spacing=1.3)


# ------------------------------------------------------------------ zone 2
def zone2(cv: Canvas, b: Box):
    p = cv.p
    c = cv.zone(b, "2  纵向粪样与体液采集  Longitudinal sampling", acc=1)

    ax = Box(c.x + 2.0, c.y + 1.0, c.w - 4.0, 21.0)
    y_axis = ax.y + 6.2
    cv.divider(ax.x, y_axis, ax.x2 - 9.0, y_axis, colour=p.zone_line(1), lw=S.bold)

    ages = ["6", "10", "13", "17", "20", "33"]
    span = ax.w - 9.0
    step = span / (len(ages) - 1)
    for i, a in enumerate(ages):
        x = ax.x + step * i
        cv.rect(Box(x - 1.3, y_axis - 1.3, 2.6, 2.6), fill=p.paper,
                line=p.zone_line(1), lw=S.bold, radius=R.pill)
        cv.text(Box(x - 6.5, y_axis - 5.6, 13.0, 4.2), a, size=6.2, bold=True,
                colour=p.ink)
        cv.icon(Box(x - 3.8, y_axis + 2.2, 7.6, 10.4),
                "bioicons/servier/Microbiology/microtube-closed-blue", pad=0.0)
    cv.text(Box(ax.x, y_axis - 10.2, 14.0, 3.8), "月龄", size=5.6, align="l",
            colour=p.ink3)

    area = Box(c.x, c.y + 22.2, c.w, 20.0)
    cards = area.cols(2, gap=2.0)
    for card, (t, s) in zip(cards, [
        ("宏基因组", "纵向 6 个时间点\n240 只 / 时间点"),
        ("靶向 SCFA + 代谢组", "乙酸 / 丙酸 / 丁酸\n盲肠内容物 + 血浆"),
    ]):
        cv.rect(card, fill=p.wash, line=p.rule, lw=S.hair, radius=R.chip)
        cv.text(Box(card.x + 2.0, card.y + 1.3, card.w - 4.0, 4.0), t, size=6.4,
                bold=True, align="l", colour=p.zone_line(1))
        cv.text(Box(card.x + 2.0, card.y + 5.8, card.w - 4.0, card.h - 6.6), s,
                size=5.6, align="l", colour=p.ink2, line_spacing=1.4)

    cv.text(Box(c.x, c.y2 - 4.6, c.w, 4.0),
            "纵向追踪同一动物 → 抵消个体间差异",
            size=5.3, align="c", colour=p.ink3, italic=True)


# ------------------------------------------------------------------ zone 3
def zone3(cv: Canvas, b: Box):
    p = cv.p
    c = cv.zone(b, "3  平行取材 · 多组织多组学  Multi-tissue", acc=2)

    items = [
        ("盲肠内容物", "SCFA（GC-MS）\n菌群绝对定量", 0,
         "bioicons/servier/Microbiology/microtube-closed-blue"),
        ("结肠 + 粪便", "LC-MS/MS 代谢组\n16S / 宏基因组", 1,
         "bioicons/servier/Human_physiology/colon"),
        ("结肠组织", "H&E · 炎症评分\n免疫组化 / 屏障蛋白", 2,
         "bioicons/servier/Tissues/epithelium-cell-column"),
    ]
    area = Box(c.x, c.y, c.w, c.h - 5.2)
    for (t, s, _acc, icon), card in zip(items, area.rows(3, gap=2.2)):
        cv.rect(card, fill=p.paper, line=p.rule, lw=S.hair, radius=R.chip)
        cv.rect(Box(card.x, card.y, 1.1, card.h), fill=p.zone_line(2), line=None)
        cv.icon(Box(card.x + 2.4, card.y + 1.2, 14.0, card.h - 2.4), icon, pad=0.4)
        cv.text(Box(card.x + 18.0, card.y + 1.4, card.w - 19.0, 4.2), t,
                size=6.4, bold=True, align="l", colour=p.ink)
        cv.text(Box(card.x + 18.0, card.y + 5.8, card.w - 19.0, card.h - 6.4), s,
                size=5.5, align="l", colour=p.ink2, line_spacing=1.35)

    cv.text(Box(c.x, c.y2 - 4.6, c.w, 4.0),
            "同一时间点并行取样，模态可对齐",
            size=5.3, align="c", colour=p.ink3, italic=True)


# ------------------------------------------------------------------ zone 4
def zone4(cv: Canvas, b: Box):
    p = cv.p
    c = cv.zone(b, "4  结局：健康寿命  Outcome", acc=3)

    curves = {
        "WGBR": ([0, 10, 20, 28, 33, 37], [1.00, 0.99, 0.94, 0.84, 0.62, 0.34]),
        "WGWR": ([0, 10, 20, 28, 33, 35], [1.00, 0.98, 0.88, 0.70, 0.42, 0.18]),
        "PR": ([0, 10, 20, 26, 30, 33], [1.00, 0.96, 0.76, 0.52, 0.24, 0.06]),
        "ST": ([0, 9, 18, 23, 27, 30], [1.00, 0.92, 0.66, 0.38, 0.14, 0.02]),
    }
    pb = Box(c.x, c.y, c.w, 24.0)
    cv.rect(pb, fill=p.paper, line=p.rule, lw=S.hair, radius=R.chip)
    cv.plot(pb.inner(1.4), mp.survival(curves, p, xticks=[0, 10, 20, 30, 40],
                                       legend=True, ylabel="", xlabel=""))

    hyp = Box(c.x, c.y + 26.0, c.w, c.h - 26.0)
    cv.rect(hyp, fill=p.zone(3), line=p.zone_line(3), lw=S.hair, radius=R.chip)
    cv.text(Box(hyp.x + 1.8, hyp.y + 1.2, hyp.w - 3.6, 3.8), "关键假设", size=5.6,
            bold=True, align="l", colour=p.zone_line(3))
    cv.text(Box(hyp.x + 1.8, hyp.y + 5.2, hyp.w - 3.6, hyp.h - 6.4),
            "黑米膳食 → 有益菌富集 → SCFA↑ → 肠屏障↑、炎症↓ → 寿命↑",
            size=6.0, align="l", colour=p.ink, line_spacing=1.35)


# ------------------------------------------------------------------ zone 5
def zone5(cv: Canvas, b: Box):
    p = cv.p
    c = cv.zone(b, "5  多组学整合 · mGWAS 宿主–菌群互作  Integrative mGWAS", acc=4)

    # row 1: five modalities side by side
    mods = [
        ("宏基因组", "bioicons/james-lloyd/Microbiology/Bacteria_Swimming"),
        ("宿主基因组", "bioicons/servier/Nucleic_acids/dna-3"),
        ("SCFA 靶向", "sciglyph/03-metabolism-phenotype/metabolism/013-ferm-butyrate"),
        ("代谢组", "bioicons/sasha-sundstrom/Lab_apparatus/mass-spectrometer-MS"),
        ("病理 / 炎症", "bioicons/servier/Lab_apparatus/microscope"),
    ]
    band = Box(c.x, c.y, c.w, 12.4)
    for (name, icon), cell in zip(mods, band.cols(5, gap=1.4)):
        cv.rect(cell, fill=p.paper, line=p.rule, lw=S.hair, radius=R.chip)
        cv.icon(Box(cell.x + (cell.w - 6.4) / 2, cell.y + 0.9, 6.4, 6.0), icon,
                pad=0.0)
        cv.text(Box(cell.x + 0.6, cell.y + 7.0, cell.w - 1.2, 4.6), name,
                size=5.6, align="c", colour=p.ink)

    # row 2: one horizontal processing statement
    strip = Box(c.x + 2.0, band.y2 + 1.2, c.w - 4.0, 4.4)
    cv.rect(strip, fill=p.wash, line=None, radius=R.chip)
    cv.text(strip, "质控 · 比对 · 物种 / 功能注释 · 纵向对齐", size=5.8,
            align="c", colour=p.ink2)

    # row 3: matrix + reading + outputs
    c3 = Box(c.x, strip.y2 + 1.9, 34.0, c.h - (strip.y2 + 1.9 - c.y))
    c4 = Box(c3.x2 + 2.2, c3.y, c.w - 36.2, c3.h)
    cv.text(Box(c4.x, c4.y, c4.w, 3.6), "主要产出  Key outputs", size=5.6, bold=True,
            align="l", colour=p.ink2)

    mat = [[0.9, 0.3, 0.2, 0.5, 0.1],
           [0.2, 0.8, 0.4, 0.1, 0.3],
           [0.4, 0.2, 0.9, 0.3, 0.2],
           [0.1, 0.5, 0.3, 0.9, 0.4],
           [0.3, 0.1, 0.2, 0.4, 0.8],
           [0.8, 0.2, 0.1, 0.2, 0.3]]
    hb = Box(c3.x, c3.y, c3.w, 13.6)
    cv.plot(hb, mp.heat(mat, p, cmap="Blues", cbar=False, vmin=0, vmax=1))
    cv.text(Box(c3.x, hb.y2 + 0.7, c3.w, 4.2), "SNP × 微生物特征", size=5.6,
            align="c", colour=p.ink2)
    cv.text(Box(c3.x, hb.y2 + 5.0, c3.w, c3.h - (hb.y2 + 5.2 - c3.y)),
            "mGWAS\n宿主位点 → 菌群 / SCFA", size=5.8, bold=True, align="c",
            colour=p.zone_line(4), line_spacing=1.5)

    outs = ["宿主遗传变异关联菌群与 SCFA", "菌群–SCFA–宿主表型通路网络",
            "定位候选基因 / 菌属 / 代谢物", "独立亚组重复验证"]
    ob_area = Box(c4.x, c4.y + 4.0, c4.w, c4.h - 4.0)
    for i, (s, r) in enumerate(zip(outs, ob_area.rows(4, gap=1.0))):
        cv.badge((r.x + 1.5, r.cy), i + 1, r=1.5, colour=p.zone_line(4))
        cv.text(Box(r.x + 4.0, r.y, r.w - 4.2, r.h), s, size=6.0, align="l",
                colour=p.ink, line_spacing=1.3)


# ------------------------------------------------------------------ zone 6
def zone6(cv: Canvas, b: Box):
    p = cv.p
    c = cv.zone(b, "6  机制假说  Proposed mechanism", acc=5)

    steps = [
        ("全谷物黑米", "膳食纤维 · 多酚 · 花青素", 5),
        ("菌群结构重塑", "产 SCFA 菌↑ / 致病菌↓", 4),
        ("SCFA 产量↑", "乙酸 · 丙酸 · 丁酸", 2),
        ("肠屏障↑ 炎症↓", "紧密连接 · 黏液层 · 细胞因子", 1),
        ("健康寿命↑", "存活曲线右移", 0),
    ]
    area = Box(c.x, c.y, c.w, c.h - 5.0)
    cards = area.rows(5, gap=2.2)
    for i, ((t, s, acc), card) in enumerate(zip(steps, cards)):
        cv.rect(card, fill=p.paper, line=p.zone_line(acc), lw=S.base, radius=R.chip)
        cv.rect(Box(card.x, card.y, 1.2, card.h), fill=p.zone_line(acc), line=None)
        cv.text(Box(card.x + 3.0, card.y + 0.6, card.w - 4.2, 4.0), t, size=6.6,
                bold=True, align="l", colour=p.ink)
        cv.text(Box(card.x + 3.0, card.y + 4.7, card.w - 4.2, card.h - 4.9), s,
                size=5.6, align="l", colour=p.ink2, wrap=False)
        if i < 4:
            mid = card.x + card.w * 0.5
            cv.arrow((mid, card.y2 + 0.1), (mid, cards[i + 1].y - 0.1),
                     lw=S.base, colour=p.ink3)

    fx = c.x2 - 0.8
    cv.route([(fx, cards[3].cy), (fx + 0.9, cards[3].cy), (fx + 0.9, cards[1].cy),
              (fx, cards[1].cy)], colour=p.ink3, lw=S.hair, dash=4)
    cv.text(Box(c.x, c.y2 - 4.6, c.w, 4.2), "虚线：SCFA / 屏障状态反向塑造菌群",
            size=5.5, align="c", colour=p.ink3, italic=True)


# ------------------------------------------------------------------ zone 7
def zone7(cv: Canvas, b: Box):
    p = cv.p
    c = cv.zone(b, "7  人群验证与转化  Human validation", acc=1)

    items = [
        ("公共队列", "MetaHIT · HMP · UK Biobank\nNHANES · 中国人群队列"),
        ("关键关联复现", "膳食纤维 / 全谷物摄入\n↔ SCFA 产生菌 ↔ 炎症标志物"),
        ("转化", "膳食指导 · 精准营养\n健康老龄化干预"),
    ]
    area = Box(c.x, c.y, c.w, c.h - 5.0)
    for i, ((t, s), card) in enumerate(zip(items, area.rows(3, gap=2.2))):
        cv.rect(card, fill=p.paper, line=p.rule, lw=S.hair, radius=R.chip)
        cv.badge((card.x + 3.2, card.y + card.h / 2), i + 1, r=1.6,
                 colour=p.zone_line(1))
        cv.text(Box(card.x + 7.4, card.y + 1.3, card.w - 8.2, 4.2), t, size=6.2,
                bold=True, align="l", colour=p.ink)
        cv.text(Box(card.x + 6.6, card.y + 5.4, card.w - 7.4, card.h - 6.0), s,
                size=5.2, align="l", colour=p.ink2, line_spacing=1.35)

    cv.text(Box(c.x, c.y2 - 4.4, c.w, 4.0), "机制在人体中一致 → 可转化", size=5.5,
            align="c", colour=p.ink3, italic=True)


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "out"
    print(build(Path(out)))





