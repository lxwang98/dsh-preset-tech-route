"""iso 能力测试：稻田（土壤剖面 + 水面）→ 餐桌（全谷黑米）等距底图。

只验证"能不能画"，不是成品图。所有标签横排、放在体块外，用引线指过去；
体块用 routekit.iso，作物与碗是现有平面图元"立"在等距地面上（BioRender 同样做法）。
"""
import math
import random
import sys

sys.path.insert(0, r"D:\dsh-bundles\tech-route\skills\tech-route-atlas\scripts")

from pptx.util import Mm

from routekit import Canvas, Box, iso
from routekit.palette import P, shade, tint

cv = Canvas(220, 118, palette="cell", margin=0.0, title="iso-paddy")
p = P("cell")

WATER = "#2e6e9e"
SOIL = ("#c3b184", "#a89468", "#8a8073")
TABLE = "#b07a4a"

U = (iso.DEPTH_X, iso.DEPTH_Y)          # 宽：右上 30°
V = (-iso.DEPTH_X, iso.DEPTH_Y)         # 进深：左上 30°


def on_ground(near, w, d, t1, t2, z=0.0):
    """地面上一点的屏幕坐标：``near`` 为近角，``t1/t2`` 是 0–1 参数。"""
    return (near[0] + U[0] * w * t1 + V[0] * d * t2,
            near[1] + U[1] * w * t1 + V[1] * d * t2 - z)


def poly(pts, fill, line=None, lw=0.35):
    b = cv.slide.shapes.build_freeform(Mm(pts[0][0]), Mm(pts[0][1]))
    b.add_line_segments([(Mm(x), Mm(y)) for x, y in pts[1:]], close=True)
    s = b.convert_to_shape()
    cv._set_fill(s, fill)
    cv._style_line(s, line, lw)
    s.shadow.inherit = False
    return s


def bowl(b, mound, grain, grain_hi, seed=3, n=15, edge="#a9b6c0"):
    rnd = random.Random(seed)
    rim = b.y + b.h * 0.40

    def heap_y(t):
        return rim - b.h * 0.36 * math.sin(math.pi * t) ** 0.72

    heap = [(b.x + b.w * 0.02, rim)]
    for k in range(1, 30):
        t = k / 29.0
        heap.append((b.x + b.w * (0.02 + 0.96 * t), heap_y(0.02 + 0.96 * t)))
    poly(heap, mound, shade(mound, 0.28), 0.45)
    for i in range(n):
        t = rnd.uniform(0.14, 0.86)
        top = heap_y(t)
        gy = rnd.uniform(top + b.h * 0.03, rim - b.h * 0.03)
        gw, gh = b.w * 0.115, b.h * 0.070
        s = cv.rect(Box(b.x + b.w * t - gw / 2, gy - gh / 2, gw, gh),
                    fill=grain if i % 4 else grain_hi, line=shade(grain, 0.18),
                    lw=0.22, radius=gh / 2)
        s.rotation = rnd.uniform(-38, 38)
    body = [(b.x + b.w * k / 40.0, rim + b.h * 0.40 * math.sin(math.pi * k / 40.0))
            for k in range(41)]
    poly(body, "#e9eef3", edge, 0.55)
    cv.rect(Box(b.x, rim - b.h * 0.055, b.w, b.h * 0.110), fill="#f9fbfd",
            line=edge, lw=0.55, radius=b.h * 0.055)
    cv.rect(Box(b.x + b.w * 0.30, rim + b.h * 0.20, b.w * 0.40, b.h * 0.05),
            fill="#dde5ec", line=None, radius=b.h * 0.025, alpha=0.6)


# ---------------------------------------------------------------- 左侧：稻田
PN = (56.0, 106.0)                       # 稻田近角
PW, PD = 60.0, 34.0
STACK = [(7, SOIL[2]), (6, SOIL[1]), (5, SOIL[0])]
PH = sum(h for h, _ in STACK)            # 18

iso.iso_layers(cv, PN[0], PN[1], w=PW, d=PD, layers=STACK, mode="iso")
iso.iso_plane(cv, PN[0], PN[1] - PH, w=PW, d=PD, fill=tint(WATER, 0.55),
              line=shade(WATER, 0.30), mode="iso")

# 稻株：立在田面上
for t1, t2, hh in ((0.28, 0.28, 16.0), (0.55, 0.20, 17.0), (0.46, 0.56, 15.0),
                   (0.72, 0.40, 14.0)):
    gx, gy = on_ground((PN[0], PN[1] - PH), PW, PD, t1, t2)
    cv.icon(Box(gx - 4.4, gy - hh + 1.2, 8.8, hh), "bioicons/Rice")

# 剖面标签 + 引线
cv.text(Box(4.0, 70.0, 32.0, 12.0), "土壤剖面\n稻季水分管理", size=7.8,
        colour=p.ink2, align="l")
cv.arrow((36.0, 76.4), (50.0, 87.6), colour=p.ink3, lw=0.5)

# ---------------------------------------------------------------- 右侧：餐桌
TN = (150.0, 96.0)
TW, TD, TH = 40.0, 26.0, 4.0
iso.iso_block(cv, TN[0], TN[1], w=TW, d=TD, h=TH, acc=TABLE, mode="iso")
ttop = TN[1] - TH
bowl(Box(TN[0] + U[0] * TW * 0.50 + V[0] * TD * 0.48 - 8.0,
         ttop + U[1] * TW * 0.50 + V[1] * TD * 0.48 - 12.2, 16.0, 12.4),
     mound="#2f2026", grain="#4a3038", grain_hi="#6b4a52")

cv.text(Box(170.0, 52.0, 46.0, 10.0), "餐桌：全谷黑米主食", size=7.8,
        colour=p.ink2, align="c")
cv.arrow((193.0, 62.4), (187.4, 73.6), colour=p.ink3, lw=0.5)

# ---------------------------------------------------------------- 中间：流程
sx, sy = on_ground((PN[0], PN[1] - PH), PW, PD, 0.98, 0.60, z=2.0)
ex, ey = on_ground((TN[0], ttop), TW, TD, 0.04, 0.46, z=2.0)
cv.route([(sx, sy), ((sx + ex) / 2, sy - 7.0), (ex, ey)],
         colour=p.accent(0), lw=1.6, head="triangle")
cv.text(Box((sx + ex) / 2 - 26, sy - 15.2, 52, 6.4),
        "收割 · 脱壳 · 蒸煮 → 主食化", size=7.8, bold=True, colour=p.accent(0))

cv.save(r"out\iso-paddy-test.pptx")
from routekit import export  # noqa: E402
from routekit.audit import static_report, format_report  # noqa: E402

issues = static_report(cv, mode="print")
print(format_report(issues) if issues else "OK — no issues found")
print(export.render(r"out\iso-paddy-test.pptx", r"out", dpi=300))
