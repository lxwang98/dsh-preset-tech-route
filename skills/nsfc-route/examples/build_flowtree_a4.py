# -*- coding: utf-8 -*-
"""
国自然 · 树状汇流式（flow-tree）A4 竖版范例
==========================================
规格（4 行）
  画布: 210 x 297 mm (CANVAS.nsfc_a4)，边距 10；绝不跨页
  故事: 临床 KPLA 病例 → 5 项临床检测 → 关联性结论 → 机制研究分双臂（体外/体内）
        → 各自读数与收口 → 底部总结论
  分区: L0 入口 / L1 临床检测（5 并列）/ L2 汇流结论 / L3 机制条 / L4-L6 双臂 / L7 结论
  箭头: 扇出走"竖干+横总线"，汇流反向；实线=主链，虚线=干预/可选；总结论只出现一次

箭头拓扑表
  ID | From        | To           | 线型 | 语义              | 优先级
  T0 | 入口        | 5 项检测      | 实线 | 扇出（总线）      | P0
  T1 | 5 项检测    | 关联性结论    | 实线 | 汇流（总线）      | P0
  T2 | 关联性结论  | 机制研究条    | 实线 | 由关联到机制      | P0
  T3 | 机制研究条  | 体外 / 体内   | 实线 | 二次分叉          | P0
  T4 | 体外        | 4 个干预盒    | 实线 | 扇出              | P1
  T5 | 干预盒      | 读数盒        | 实线 | 汇流              | P1
  T6 | 体内        | 造模→分组→模型 | 实线 | 串行              | P1
  T7 | 模型        | 干预药（虚线） | 虚线 | 可选干预          | P2
  T8 | 各臂读数    | 各臂结论      | 实线 | 收口（不得共用）  | P1
  T9 | 各臂结论    | 底部总结论    | 实线 | 全图唯一汇总      | P0
"""
import os
import sys

sys.path.insert(0, r"D:\dsh-bundles\tech-route\skills\tech-route-atlas\scripts")
from routekit import Canvas, Box, CANVAS
from routekit.audit import static_report, format_report
from routekit import export

# 语义配色：按"证据来源"分，不按美观分
CLIN = ("#fbeaf0", "#d9a7b4", "#7a2e3f")     # 临床
ASSAY = ("#eaf1f7", "#a8c2d6", "#1b3a63")    # 检测/读数
VITRO = ("#e8f2ee", "#96bfa6", "#24573c")    # 体外
VIVO = ("#efebf7", "#b9acd8", "#453173")     # 体内
CONC = ("#fdf6e3", "#e0c48a", "#6b4a28")     # 结论/期望
MECH = "#b85252"                              # 机制条 / 总结论（全图唯一高饱和）
INK3 = "#76879a"

F_TITLE, F_MOD, F_BODY = 15.0, 11.0, 8.4
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUTDIR, exist_ok=True)

W, H = CANVAS.nsfc_a4
M = 10.0
CW = W - 2 * M
cv = Canvas(W, H, palette="cell", cjk_font="SimHei", title="nsfc-flowtree")

LINE = INK3


def card(x, y, w, h, text, col, *, size=F_BODY, bold=False, dash=None, align="c"):
    fill, line, tc = col
    cv.rect(Box(x, y, w, h), fill=fill, line=line, lw=0.7, radius=1.2, dash=dash)
    cv.text(Box(x + 1.2, y + 0.8, w - 2.4, h - 1.6), text, size=size, bold=bold,
            colour=tc, align=align, spacing=1.05)
    return Box(x, y, w, h)


def bus(src_cx, src_y, targets, y_bus, *, colour=LINE, lw=0.9):
    """扇出：源盒底中点 → 竖干 → 横总线 → 各目标顶边中点（箭头落目标）。"""
    xs = [t[0] for t in targets] + [src_cx]
    cv.route([(src_cx, src_y), (src_cx, y_bus)], colour=colour, lw=lw, head="none")
    cv.route([(min(xs), y_bus), (max(xs), y_bus)], colour=colour, lw=lw, head="none")
    for cx, yt in targets:
        cv.route([(cx, y_bus), (cx, yt)], colour=colour, lw=lw, head="triangle")


def gather(parents, dst_cx, dst_y, y_bus, *, colour=LINE, lw=0.9):
    """汇流：各父盒底中点 → 横总线 → 目标顶边中点（箭头落目标）。"""
    xs = [p.cx for p in parents]
    for cx in xs:
        cv.route([(cx, parents[0].y2), (cx, y_bus)], colour=colour, lw=lw, head="none")
    cv.route([(min(xs), y_bus), (max(xs), y_bus)], colour=colour, lw=lw, head="none")
    cv.route([(dst_cx, y_bus), (dst_cx, dst_y)], colour=colour, lw=lw)


# ------------------------------------------------------------------ 标题
cv.text(Box(M, 6.0, CW, 9.0), "临床 KPLA 病例 → 高糖–NETs–内皮激活 → 迁徙性感染",
        size=F_TITLE, bold=True, colour="#1b3a63")
cv.text(Box(M, 15.4, CW, 4.4),
        "技术路线图（树状汇流式） · 国家自然科学基金面上项目",
        size=8.6, colour=INK3, align="l")

# ------------------------------------------------------------------ L0 入口
for i, aid in enumerate(["custom/figures/human-male", "custom/figures/human-female",
                         "custom/figures/human-child"]):
    cv.icon(Box(W / 2 - 16 + i * 11.5, 22.0, 9.0, 12.0), aid)
entry = card(W / 2 - 48, 37.0, 96, 9.0, "临床 KPLA 病例（肺炎克雷伯菌肝脓肿）",
             CLIN, size=9.2, bold=True)

# ------------------------------------------------------------------ L1 临床检测（5 并列）
L1Y, L1H = 52.0, 27.0
gap = 2.5
cw5 = (CW - 4 * gap) / 5
L1 = ["空腹血糖\n>7 / ≤7 mmol/L",
      "血清及脓液\nNETs：dsDNA\nMPO、NE",
      "血清内皮激活\nVCAM-1、vWF\nTM、HS",
      "肝增强 CT/MRI\n肝静脉血栓性\n静脉炎",
      "临床 + 影像\nKPLA 侵袭性\n（迁徙性感染）"]
l1 = [card(M + i * (cw5 + gap), L1Y, cw5, L1H, t, CLIN) for i, t in enumerate(L1)]
bus(entry.cx, entry.y2, [(b.cx, b.y) for b in l1], L1Y - 4.0)

# ------------------------------------------------------------------ L2 汇流结论
L2Y = 85.0
l2 = card(M, L2Y, CW, 11.0,
          "明确  高血糖 — NETs 形成 — 内皮细胞激活 — 免疫血栓形成 — 迁徙性感染  之间的关联性",
          ASSAY, size=9.0)
gather(l1, l2.cx, l2.y, L2Y - 4.0)

# ------------------------------------------------------------------ L3 机制条
L3Y = 101.0
cv.rect(Box(M, L3Y, CW, 12.0), fill=MECH, line=None, lw=0, radius=1.4)
cv.text(Box(M + 3, L3Y, CW - 6, 12.0), "机 制 研 究", size=F_MOD, bold=True,
        colour="#ffffff")
cv.route([(l2.cx, l2.y2), (l2.cx, L3Y)], colour=LINE, lw=1.1)

# ------------------------------------------------------------------ L4 双臂
L4Y, L4H = 119.0, 11.0
lv = card(M, L4Y, 88, L4H, "体外细胞实验", VITRO, size=10.0, bold=True)
rv = card(126.0, L4Y, 74, L4H, "体内动物实验", VIVO, size=10.0, bold=True)
bus((lv.cx + rv.cx) / 2, L3Y + 12.0, [(lv.cx, L4Y), (rv.cx, L4Y)], L4Y - 4.0, lw=1.1)

# ---- 左臂：培养皿 → 4 个干预盒 → 3 个读数盒
cv.icon(Box(lv.cx - 8, 134.0, 16.0, 12.0),
        "sciglyph/07-glassware-consumables/general-labware/044-petri-dish-3")
cv.text(Box(M + 2, 147.0, 84, 6.0), "KP 诱导 NETs 形成细胞模型", size=9.0,
        colour=VITRO[2], bold=True)
cv.route([(lv.cx, L4Y + L4H), (lv.cx, 133.5)], colour=LINE, lw=0.9, head="none")

L5Y, L5H = 158.0, 28.0
cw4 = (86 - 3 * 2.2) / 4
L5L = ["不同糖浓度\n不同时间点\n检测 NETs",
       "NADPH 氧化酶\n抑制剂 DPI\n干预",
       "① PMA 诱导\n② DNase 抑制\n③ 吞噬阻断",
       "提取 NETs\n刺激人脐静脉\n/ 肝窦内皮"]
l5l = [card(M + i * (cw4 + 2.2), L5Y, cw4, L5H, t, VITRO) for i, t in enumerate(L5L)]
bus(lv.cx, 153.0, [(b.cx, b.y) for b in l5l], L5Y - 3.5)

L6Y, L6H = 191.0, 22.0
cw3 = (56 - 2 * 2.2) / 3
L6L = ["扫描电镜\n透射电镜", "SytoxGreen\n染色", "免疫荧光\nMPO 双染"]
l6l = [card(M + i * (cw3 + 2.2), L6Y, cw3, L6H, t, ASSAY) for i, t in enumerate(L6L)]
gather(l5l[:3], M + 28.0, L6Y, L6Y - 4.0)

# ---- 中列：内皮信号（提取 NETs 后沉默 Rcn2 / 钙螯合）
MIDX, MIDW = 100.0, 22.0
mid0 = card(MIDX, L5Y, MIDW, 13.0, "① 沉默 Rcn2\n② 钙螯合剂", VITRO, size=8.0)
cv.route([(l5l[3].x2, l5l[3].y + 8.0), (98.0, l5l[3].y + 8.0),
          (98.0, mid0.cy), (MIDX, mid0.cy)], colour=LINE, lw=0.9)
rows = ["胞内 Ca²⁺", "Rcn2 表达", "eNOS 脱耦联", "NO、ROS", "VCAM-1、vWF"]
midr = [card(MIDX, 176.0 + i * 7.2, MIDW, 6.4, t, ASSAY, size=8.0) for i, t in enumerate(rows)]
cv.route([(mid0.cx, mid0.y2), (mid0.cx, midr[-1].y2)], colour=LINE, lw=0.9, head="none")
cfu = card(MIDX, 214.0, MIDW, 6.4, "菌落计数 CFU", ASSAY, size=8.0)
per = card(MIDX, 223.0, MIDW, 6.4, "通透性", ASSAY, size=8.0)

# ---- 右臂：造模 → 分组 → KPLA 模型（虚线）→ 干预（虚线）
RX = 126.0
cv.text(Box(RX + 2, 134.0, 44, 5.4), "高热量 + STZ", size=8.8, colour=VIVO[2], bold=True)
cv.icon(Box(RX + 50, 131.0, 18.0, 11.0), "bioicons/mouse-darkgray")
dm = card(RX, 144.0, 74, 9.0, "建立糖尿病小鼠模型", VIVO, size=8.8)
cv.route([(rv.cx, L4Y + L4H), (rv.cx, dm.y)], colour=LINE, lw=0.9)

grp = card(RX + 1, 159.0, 35, 9.5, "C57  Rcn2 ⁻/⁻", VIVO, size=8.4)
grp2 = card(RX + 38, 159.0, 35, 9.5, "C57  WT", VIVO, size=8.4)
cv.route([(dm.cx, dm.y2), (dm.cx, 156.5)], colour=LINE, lw=0.9, head="none")
cv.route([(grp.cx, 156.5), (grp2.cx, 156.5)], colour=LINE, lw=0.9, head="none")
for b in (grp, grp2):
    cv.route([(b.cx, 156.5), (b.cx, b.y)], colour=LINE, lw=0.9)

mod = Box(RX + 1, 174.0, 72, 50.0)
cv.rect(mod, fill="#fbfbfd", line=VIVO[1], lw=0.7, radius=1.4, dash=4)
cv.text(Box(mod.x + 2, mod.y + 1.8, mod.w - 4, 5.0), "建立 KPLA 模型（Rcn2 敲除 vs WT）",
        size=8.4, colour=VIVO[2], bold=True)
for b in (grp, grp2):
    cv.route([(b.cx, b.y2), (b.cx, mod.y)], colour=LINE, lw=0.9, head="none")
cells = ["NETs\n检测", "内皮\n激活", "免疫\n血栓"]
cw2 = (mod.w - 5 * 2.0) / 4
for i, t in enumerate(cells):
    card(mod.x + 2 + i * (cw2 + 2.0), mod.y + 9.0, cw2, 11.0, t, ASSAY, size=8.0)
drug = card(mod.x + 2 + 3 * (cw2 + 2.0), mod.y + 9.0, cw2, 11.0, "① DNase\n② 阿加曲班",
            CONC, size=7.6, dash=4)
card(mod.x + 2, mod.y + 24.0, (mod.w - 6.0) / 2, 9.0, "取材：肝、肺、血", VIVO, size=8.0)
card(mod.x + 4 + (mod.w - 6.0) / 2, mod.y + 24.0, (mod.w - 6.0) / 2, 9.0,
     "终点：迁徙灶计数、生存", VIVO, size=8.0)

# ---- 各臂结论（每臂各自收口）
CY, CH = 232.0, 26.0
c1 = card(M, CY, 60, CH, "分析不同条件下 NETs 形成特点，明确 KP 诱发 NETs 是否依赖 ROS",
          CONC, size=8.2)
c2 = card(72.0, CY, 46, CH, "阐明 Rcn2/eNOS 通路调控 NETs 激活内皮细胞的作用", CONC, size=8.2)
c3 = card(126.0, CY, 74, CH,
          "证实敲除 Rcn2 抑制 KPLA 小鼠内皮激活、血栓形成与迁徙感染；"
          "降解 NETs 与抑制免疫血栓可减轻迁徙感染", CONC, size=8.2)
gather(l6l, c1.cx + 14.0, c1.y, CY - 4.0)
cv.route([(per.cx, per.y2), (per.cx, CY - 4.0)], colour=LINE, lw=0.9)
cv.route([(mod.cx, mod.y2), (mod.cx, CY - 4.0)], colour=LINE, lw=0.9)

# ------------------------------------------------------------------ 底部总结论
SUMY = 266.0
cv.rect(Box(M, SUMY, CW, 15.0), fill=MECH, line=None, lw=0, radius=1.4)
cv.text(Box(M + 4, SUMY, CW - 8, 15.0),
        "解析高糖条件下中性粒细胞 NETs 激活内皮细胞、促进 KPLA 并发迁徙性感染的机制",
        size=10.0, bold=True, colour="#ffffff")
for b in (c1, c2, c3):
    cv.route([(b.cx, b.y2), (b.cx, SUMY)], colour=MECH, lw=1.0, head="none")

# ------------------------------------------------------------------ 自检 + 导出
print(format_report(static_report(cv, mode="print")))
pptx = cv.save(os.path.join(OUTDIR, "nsfc-flowtree-demo.pptx"))
print(export.render(pptx, OUTDIR, dpi=600, also_pdf=True))
