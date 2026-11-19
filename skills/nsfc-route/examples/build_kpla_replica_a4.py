# -*- coding: utf-8 -*-
"""临床 KPLA 技术路线图 —— 按用户参考图复刻（A4 竖版 210×297），学术风：纯色平涂、深色=一级。

规格 4 行
  画布：210×297 mm（A4 竖），边距 10，内容宽 190；中文 SimHei，正文 8.2 pt（实印地板 8）
  分区：L0 病例 → L1 五项临床检测（扇出）→ L2 关联性结论（汇流）→ L3 机制研究条 →
        L4 双臂（体外 10..102 / 体内 112..200）→ 各臂读数与收口 → 总结论条
  色彩层级：一级=深底白字（病例 / 机制研究 / 两臂标题 / 总结论）；二级=中色底深字（检测、读数、模型、收口）；
            三级=浅底深字（干预、信号、基因型）。全图 2 主色（藏青 / 深红）+ 体内臂深紫，纯色平涂，无渐变阴影
  箭头拓扑：T0 病例→五项检测（扇出总线）；T1 五项→关联性结论（汇流总线）；T2 结论→机制条；
            T3 机制条→双臂；T4 模型→干预三盒；T5 干预→读数；T6 提取 NETs→信号列；
            T7 读数→收口；T8 信号列→第三收口；T9 双基因型→KPLA 模型；T10 五条收口→总结论
"""
import sys

sys.path.insert(0, r"D:\dsh-bundles\tech-route\skills\tech-route-atlas\scripts")
from routekit import Canvas, Box
from routekit.audit import static_report, format_report

W, H = 210.0, 297.0
M = 10.0
CW = W - 2 * M

# ---- 一级（深底白字）
NAVY_D = "#1b3a63"
TEAL_D = "#26566b"
PURP_D = "#413a63"
RED_D = "#b03a48"
# ---- 二级（中色底深字）
BLUE_2 = "#c9dcec"
RED_2 = "#e9c0c4"
PURP_2 = "#cec7e3"
GOLD_2 = "#f2ddb4"
# ---- 三级（浅底深字）
BLUE_3 = "#e6f0f7"
RED_3 = "#fbe9ea"
PURP_3 = "#efeaf8"
# ---- 描边与文字
E_BLUE = "#9db8cc"
E_RED = "#c98f96"
E_PURP = "#aaa0c8"
E_GOLD = "#d8b478"
E_DASH = "#8fa0b2"
INK = "#1d2a35"
INK2 = "#3f5263"
INK3 = "#6b7c8c"
LINE = "#5b6d7e"

F_TITLE = 15.0
F_L0 = 11.0
F_L2 = 9.6
F_MECH = 12.5
F_ARM = 10.5
F_BOX = 8.2
F_SIGN = 7.8
F_CONC = 8.4

cv = Canvas(W, H, palette="cell", margin=0.0, title="临床 KPLA 技术路线图（复刻）")


def card(x, y, w, h, text, fill, edge, *, size=F_BOX, bold=False, dash=None,
         radius=1.2, colour=INK, align="c", lw=0.8):
    b = Box(x, y, w, h)
    cv.rect(b, fill=fill, line=edge, lw=lw, radius=radius, dash=dash)
    if text:
        cv.text(b.inset(1.3, 0.8), text, size=size, bold=bold, colour=colour,
                align=align, anchor="m", spacing=1.0)
    return b


def bus(src_cx, src_y, targets, y_bus, colour=LINE, lw=1.0):
    xs = [t[0] for t in targets]
    cv.route([(src_cx, src_y), (src_cx, y_bus)], colour=colour, lw=lw)
    cv.route([(min(xs), y_bus), (max(xs), y_bus)], colour=colour, lw=lw, head="none")
    for cx, ty in targets:
        cv.route([(cx, y_bus), (cx, ty)], colour=colour, lw=lw)


def gather(parents, dst_cx, dst_y, y_bus, colour=LINE, lw=1.0):
    for p in parents:
        cv.route([(p.cx, p.y2), (p.cx, y_bus)], colour=colour, lw=lw, head="none")
    cv.route([(min(p.cx for p in parents), y_bus), (max(p.cx for p in parents), y_bus)],
             colour=colour, lw=lw, head="none")
    cv.route([(dst_cx, y_bus), (dst_cx, dst_y)], colour=colour, lw=lw)


# ------------------------------------------------------------------ 标题
cv.text(Box(M, 6.2, CW, 8.0), "临床 KPLA 病例：高糖 – NETs – 内皮激活 – 迁徙性感染",
        size=F_TITLE, bold=True, colour=NAVY_D)
cv.text(Box(M, 14.4, CW, 4.2), "技术路线图 · 国家自然科学基金面上项目",
        size=8.4, colour=INK3, align="l")

# ------------------------------------------------------------------ L0 入口（一级）
cv.icon(Box(W / 2 - 19, 20.4, 38.0, 13.6), "custom/figures/cohort-people-4")
l0 = card(W / 2 - 52, 36.6, 104, 9.6, "临床 KPLA 病例", NAVY_D, NAVY_D,
          size=F_L0, bold=True, colour="#ffffff")
cv.route([(l0.cx, 34.0), (l0.cx, 36.6)], colour=LINE, lw=1.0)

# ------------------------------------------------------------------ L1 五项临床检测（二级）
L1Y, L1H = 52.0, 29.0
gap = 2.4
cw5 = (CW - 4 * gap) / 5
L1 = ["空腹血糖\n>7 mmol/L\n≤7 mmol/L",
      "血清及脓液中\nNETs 检测：\ndsDNA、MPO、NE",
      "血清中内皮细胞\n激活评价：\nVCAM-1、vWF、\nTM、HS",
      "肝增强 CT/MRI：\n肝静脉血栓性\n静脉炎",
      "临床 + 影像判断：\nKPLA 侵袭性\n（迁徙性感染）"]
l1 = [card(M + i * (cw5 + gap), L1Y, cw5, L1H, t, RED_2, E_RED) for i, t in enumerate(L1)]
bus(l0.cx, l0.y2, [(b.cx, b.y) for b in l1], L1Y - 5.0)

# ------------------------------------------------------------------ L2 关联性结论（三级 + 深描边）
L2Y = 89.0
l2 = card(M, L2Y, CW, 12.0,
          "明确  高血糖、NETs 形成、内皮细胞激活、免疫血栓形成及迁徙性感染  之间的关联性",
          RED_3, RED_D, size=F_L2, bold=True, colour="#6d2a31", lw=1.3)
gather(l1, l2.cx, l2.y, L2Y - 5.0)

# ------------------------------------------------------------------ L3 机制研究（一级）
L3Y, L3H = 106.5, 12.5
cv.rect(Box(M, L3Y, CW, L3H), fill=RED_D, line=None, lw=0, radius=1.2)
cv.text(Box(M, L3Y, CW, L3H), "机 制 研 究", size=F_MECH, bold=True, colour="#ffffff")
cv.route([(l2.cx, l2.y2), (l2.cx, L3Y)], colour=LINE, lw=1.1)

# ------------------------------------------------------------------ L4 双臂（一级）
L4Y, L4H = 123.5, 10.0
lv = card(M, L4Y, 92, L4H, "体外细胞实验", TEAL_D, TEAL_D, size=F_ARM, bold=True,
          colour="#ffffff")
rv = card(112.0, L4Y, 88, L4H, "体内动物实验", PURP_D, PURP_D, size=F_ARM, bold=True,
          colour="#ffffff")
bus((lv.cx + rv.cx) / 2, L3Y + L3H, [(lv.cx, L4Y), (rv.cx, L4Y)], L4Y - 4.5, lw=1.1)

# ------------------------------------------------------------------ 左臂：培养皿 → 模型 → 干预（三级）
DISH_Y = 135.0
cv.icon(Box(lv.cx - 15, DISH_Y, 30.0, 18.0), "custom/figures/petri-dish-cells")
cv.route([(lv.cx, L4Y + L4H), (lv.cx, DISH_Y + 0.6)], colour=LINE, lw=1.0)
cv.text(Box(M, 153.4, 92, 5.4), "KP 诱导 NETs 形成细胞模型", size=9.0, bold=True,
        colour=INK, align="c")

IV_Y, IV_H = 161.5, 29.0
iv_gap = 2.2
cw3 = (62.0 - 2 * iv_gap) / 3
IV = ["不同糖浓度、\n不同时间点\n检测 NETs",
      "NADPH 氧化酶\n抑制剂 DPI\n干预",
      "① NETs 诱导剂 PMA\n② NETs 抑制剂 DNase\n③ PMN 内吞噬菌阻断剂"]
iv = [card(M + i * (cw3 + iv_gap), IV_Y, cw3, IV_H, t, BLUE_3, E_BLUE)
      for i, t in enumerate(IV)]
xext = card(74.0, IV_Y, 28.0, 14.0, "提取 NETs 刺激\n人脐静脉 / 肝窦\n内皮细胞", BLUE_3, E_BLUE)
bus(56.0, 158.9, [(b.cx, b.y) for b in iv] + [(xext.cx, xext.y)], 160.2, lw=0.9)

# 信号列（三级）
s1 = card(74.0, 176.5, 28.0, 9.4, "① 慢病毒沉默 Rcn2\n② 钙离子螯合剂", PURP_3, E_PURP, size=F_SIGN)
cv.route([(xext.cx, xext.y2), (xext.cx, s1.y)], colour=LINE, lw=0.9)
SIGNALS = [["胞内 Ca²⁺", "Rcn2 表达水平", "eNOS 脱耦联", "检测 NO、ROS"],
           ["VCAM-1 / vWF", "菌落计数 CFU", "通透性"]]
colx = [74.0, 88.6]
colw = (28.0 - 1.2) / 2
sg = []
sy0 = s1.y2 + 1.4
sh = (219.5 - sy0 - 3 * 1.2) / 4
for ci, items in enumerate(SIGNALS):
    y = sy0
    for j, t in enumerate(items):
        b = card(colx[ci], y, colw, sh, t, PURP_3, E_PURP, size=F_SIGN)
        if j == 0:
            cv.route([(colx[ci] + colw / 2, s1.y2), (colx[ci] + colw / 2, y)], colour=LINE, lw=0.9)
        else:
            cv.route([(colx[ci] + colw / 2, y - 1.2), (colx[ci] + colw / 2, y)], colour=LINE, lw=0.9)
        sg.append(b)
        y += sh + 1.2
cv.route([(88.0, s1.y2), (88.0, sy0 - 0.4)], colour=LINE, lw=0.9, head="none")

# 读数三盒（二级）
RD_Y, RD_H = 195.5, 21.0
RD = ["扫描电镜 /\n透射电镜", "SytoxGreen\n染色", "免疫荧光\nCitH3、MPO 双染"]
rd = [card(M + i * (cw3 + iv_gap), RD_Y, cw3, RD_H, t, BLUE_2, E_BLUE) for i, t in enumerate(RD)]
bus(iv[1].cx, IV_Y + IV_H, [(b.cx, b.y) for b in rd], RD_Y - 3.6, lw=0.9)

# ------------------------------------------------------------------ 右臂：模型链（二/三级）
cv.icon(Box(148.0, 133.0, 36.0, 16.0), "bioicons/mouse-darkgray")
cv.text(Box(112.0, 136.2, 28.0, 9.0), "高热量\n+ STZ", size=8.6, colour=INK, align="l")
cv.route([(141.0, 141.0), (147.0, 141.0)], colour=LINE, lw=0.9)
cv.route([(166.0, 149.0), (166.0, 153.0)], colour=LINE, lw=1.0)

dm = card(112.0, 153.0, 88, 9.6, "建立糖尿病小鼠模型", PURP_2, E_PURP, size=9.4, bold=True)
st_gap = 3.0
st_w = (88 - st_gap) / 2
st = [card(112.0 + i * (st_w + st_gap), 167.0, st_w, 9.0, t, PURP_3, E_PURP, size=9.4)
      for i, t in enumerate(["C57 Rcn2⁻/⁻", "C57 WT"])]
bus(dm.cx, dm.y2, [(b.cx, b.y) for b in st], 164.0, lw=0.9)

MX, MY, MW, MH = 112.0, 181.0, 88.0, 38.0
cv.rect(Box(MX, MY, MW, MH), fill="#ffffff", line=E_DASH, lw=1.1, radius=1.2, dash=4)
cv.text(Box(MX + 2, MY + 1.8, MW - 4, 5.0), "建立 KPLA 模型（Rcn2 敲除 vs WT）",
        size=8.4, bold=True, colour=INK)
iw = (MW - 3 * 2.0) / 4
inner = []
for i, t in enumerate(["NETs\n检测", "内皮\n激活", "免疫\n血栓", "迁徙\n感染"]):
    inner.append(card(MX + i * (iw + 2.0), MY + 8.4, iw, 11.6, t, BLUE_2, E_BLUE, size=8.0))
drug = card(MX + 2.0, MY + 22.8, 34.0, 10.4, "① DNase\n② 阿加曲班", GOLD_2, E_GOLD, size=8.0,
            dash=4)
cv.route([(drug.x2, drug.cy), (inner[2].x - 0.8, inner[2].cy)], colour=LINE, lw=0.9, dash=2)
for b in st:
    cv.route([(b.cx, b.y2), (b.cx, MY)], colour=LINE, lw=0.9)

# ------------------------------------------------------------------ 收口（二级）
CC_Y, CC_H = 228.0, 24.0
cwc = (92.0 - 2 * iv_gap) / 3
CC = ["分析不同条件下 NETs 形成特点，明确 KP 诱发 NETs 是否依赖 ROS",
      "明确高糖下 NETs 对 PMN 胞外杀伤 KP 能力的影响",
      "阐明 Rcn2/eNOS 信号途径调控 NETs 激活内皮细胞的作用及分子机制"]
cc = [card(M + i * (cwc + iv_gap), CC_Y, cwc, CC_H, t, GOLD_2, E_GOLD, size=F_CONC,
           colour="#6b4a28") for i, t in enumerate(CC)]
for i, b in enumerate(rd):
    cv.route([(b.cx, b.y2), (b.cx, cc[i].y)], colour=LINE, lw=0.9)
cv.route([(sg[-1].cx, sg[-1].y2), (sg[-1].cx, CC_Y - 4.0)], colour=LINE, lw=0.9)
cv.route([(sg[-1].cx, CC_Y - 4.0), (cc[2].cx, CC_Y - 4.0)], colour=LINE, lw=0.9, head="none")
cv.route([(cc[2].cx, CC_Y - 4.0), (cc[2].cx, CC_Y)], colour=LINE, lw=0.9)

RC = ["期望证实敲除 Rcn2 抑制 KPLA 小鼠内皮细胞损伤、血栓形成及迁徙感染",
      "探究降解 NETs 和抑制免疫血栓形成对 KPLA 并发迁徙性感染的干预效果"]
rc = [card(112.0 + i * (43.0 + 2.0), CC_Y, 43.0, CC_H, t, GOLD_2, E_GOLD, size=F_CONC,
           colour="#6b4a28") for i, t in enumerate(RC)]
cv.route([(MX + MW / 2, MY + MH), (MX + MW / 2, CC_Y - 4.0)], colour=LINE, lw=0.9)
cv.route([(rc[0].cx, CC_Y - 4.0), (rc[1].cx, CC_Y - 4.0)], colour=LINE, lw=0.9, head="none")
for b in rc:
    cv.route([(b.cx, CC_Y - 4.0), (b.cx, CC_Y)], colour=LINE, lw=0.9)

# ------------------------------------------------------------------ 总结论（一级）
TY, TH = 265.0, 13.0
cv.rect(Box(M, TY, CW, TH), fill=RED_D, line=None, lw=0, radius=1.2)
cv.text(Box(M + 2, TY, CW - 4, TH),
        "解析高糖条件下中性粒细胞 NETs 激活内皮细胞、促进 KPLA 并发迁徙性感染的机制",
        size=9.6, bold=True, colour="#ffffff")
gather(cc + rc, W / 2, TY, 260.0, lw=1.0)

cv.text(Box(M, 282.0, CW, 4.4),
        "注：本图仅呈现研究逻辑与技术路线，不含实验数据；L0–L7 与正文「研究内容 / 技术路线」逐条对应。",
        size=7.6, colour=INK3, align="l")

cv.save(r"D:\HuaweiMoveData\Users\wanglinx\OneDrive\桌面\文章撰写\ops\out\kpla-replica.pptx")
issues = static_report(cv, mode="print")
print(format_report(issues) if issues else "OK — no issues found")
print(cv.summary())




