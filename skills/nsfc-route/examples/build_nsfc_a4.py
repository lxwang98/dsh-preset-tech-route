# -*- coding: utf-8 -*-
"""
国自然（NSFC）技术路线图 · A4 竖排范例
======================================
规格（4 行，画之前必须写）
  画布: 210 x 297 mm (CANVAS.nsfc_a4)，边距 12 mm；绝不跨页
  故事: 菌群来源丁酸 —GPR43→ 屏障完整性 —↓内毒素移位→ 缓解炎性衰老
        三个研究内容 串行递进（表型关联 → 分子机制 → 干预验证），落在 4 类可考核成果
  分区: A 前期基础/科学问题/工作假说   B 研究内容一~三（目标·关键技术·可验证产出）
        C 创新点（强调色，全图唯一高饱和）  D 预期成果   E 风险与对策
  箭头: 左侧竖向主干 A→B1→B2→B3；区内横向推进；跨区不交叉；实线主链

箭头拓扑表
  ID | From          | To        | 线型 | 语义                | 优先级
  B0 | 假说条        | 研究内容一 | 实线 | 假说落地            | P0
  B1 | 研究内容一    | 研究内容二 | 实线 | 表型发现→机制解析   | P0
  B2 | 研究内容二    | 研究内容三 | 实线 | 机制→干预验证       | P0
  H1 | 前期基础      | 科学问题   | 实线 | 发现→提炼问题       | P0
  H2 | 科学问题      | 工作假说   | 实线 | 问题→提出假说       | P0
  R1 | 创新点        | 预期成果   | 无   | 上下顺排（非因果）  | -
"""
import os
import sys

sys.path.insert(0, r"D:\dsh-bundles\tech-route\skills\tech-route-atlas\scripts")
from routekit import Canvas, Box, CANVAS
from routekit.audit import static_report, format_report
from routekit import export

# ---- 配色：2 主色（深浅三级）+ 1 强调色，低饱和，灰度可辨
NAVY = "#1b3a63"      # 一级
BLUE = "#2e6e9e"      # 二级
SKY = "#5a8fbf"       # 三级
AMBER = "#b87333"     # 强调色：只给创新点
RED = "#8a2f3a"
INK, INK2, INK3 = "#16222b", "#455766", "#76879a"
RULE, WASH = "#c2cfda", "#f6f9fb"

# ---- 字号阶梯（A4 实印，8 pt 为地板）
F_TITLE, F_SUB = 18.0, 9.6
F_SECT, F_MOD = 10.0, 13.0
F_HEAD, F_BODY, F_TINY = 9.0, 9.2, 8.2

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUTDIR, exist_ok=True)

W, H = CANVAS.nsfc_a4
M = 12.0
CW = W - 2 * M

cv = Canvas(W, H, palette="cell", cjk_font="SimHei", title="nsfc-route-demo")


# ------------------------------------------------------------------ helpers
def panel(b, title="", *, acc=NAVY, fill="#ffffff"):
    """学术风卡片：极浅底、细边、左色条标题。返回内容区。"""
    cv.rect(b, fill=fill, line=RULE, lw=0.5, radius=1.2)
    if not title:
        return b.inset(2.6)
    cv.rect(Box(b.x + 2.4, b.y + 2.0, 1.3, 6.2), fill=acc, line=None, radius=0.5)
    cv.text(Box(b.x + 5.2, b.y + 1.4, b.w - 7.4, 7.4), title, size=F_SECT, bold=True,
            colour=acc, align="l")
    cv.divider(b.x + 2.4, b.y + 9.4, b.x + b.w - 2.4, b.y + 9.4, colour=RULE, lw=0.5)
    return Box(b.x + 2.8, b.y + 10.6, b.w - 5.6, b.h - 12.4)


def numdot(b, s, colour):
    cv.rect(b, fill=colour, line=None, radius=b.w / 2)
    cv.text(b, s, size=9.6, bold=True, colour="#ffffff", wrap=False)


# ------------------------------------------------------------------ 标题
cv.text(Box(M, 9.0, CW, 11.0),
        "菌群来源丁酸经 GPR43 调控结肠屏障完整性缓解炎性衰老的机制研究",
        size=F_TITLE, bold=True, colour=NAVY)
cv.text(Box(M, 21.0, CW, 5.2),
        "国家自然科学基金面上项目（2026–2029）  ·  技术路线图  Technical Route",
        size=F_SUB, colour=INK3, align="l")

# ------------------------------------------------------------------ A 科学问题与假说
HYP = Box(M, 28.5, CW, 28.0)
hc = panel(HYP, "科学问题与工作假说", acc=NAVY)
segs = [("前期基础", NAVY, "老年小鼠结肠丁酸↓、GPR43↓、\n紧密连接↓、血清 LPS↑"),
        ("关键科学问题", RED, "丁酸–GPR43 轴是否为\n肠道屏障衰老的可干预节点？"),
        ("工作假说", "#2f7d55", "补丁酸→激活 GPR43→上调紧密连接\n→减少内毒素移位→抑制炎性衰老")]
gap = 9.0
bw = (hc.w - 2 * gap) / 3
for i, (head, col, body) in enumerate(segs):
    bb = Box(hc.x + i * (bw + gap), hc.y, bw, hc.h)
    cv.rect(bb, fill=WASH, line=RULE, lw=0.5, radius=1.2)
    cv.text(Box(bb.x + 2.4, bb.y + 1.6, bb.w - 4.8, 4.6), head, size=F_HEAD,
            bold=True, colour=col, align="l")
    cv.text(Box(bb.x + 2.4, bb.y + 6.6, bb.w - 4.8, bb.h - 8.0), body, size=F_BODY,
            align="l", colour=INK2, spacing=1.16)
    if i < 2:
        x0 = bb.x2 + 1.0
        cv.arrow((x0, bb.cy), (x0 + gap - 2.4, bb.cy), colour=INK3, lw=1.1)

# ------------------------------------------------------------------ B 研究内容
BODY = Box(M, 60.5, CW, 146.0)
cards = BODY.rows(3, gap=5.0)

CONTENT = [
    dict(tag="一", acc=NAVY, title="丁酸–GPR43 轴在肠道屏障衰老中的表达特征",
         goal="刻画该轴随增龄的变化及其与屏障、炎症、寿命的关联",
         keys=["自然衰老鼠队列（6–24 月龄）",
               "粪便 SCFA 靶向定量（GC-MS）",
               "GPR43 / 紧密连接蛋白定位"],
         outs=["丁酸–GPR43 的增龄变化曲线",
               "屏障–炎症–寿命关联数据集"]),
    dict(tag="二", acc=BLUE, title="GPR43 调控紧密连接组装与内毒素移位的机制",
         goal="阐明 GPR43 调控紧密连接装配、阻断内毒素移位的分子通路",
         keys=["类器官单层 + TEER 通透性",
               "Gpr43 肠上皮条件敲除鼠",
               "单细胞与空间转录组"],
         outs=["阐明 GPR43–MLCK–MLC 通路",
               "锁定 2 个可干预分子节点"]),
    dict(tag="三", acc=SKY, title="靶向该轴的营养干预与健康寿命效应",
         goal="验证靶向干预能否延缓屏障衰老、延长健康寿命",
         keys=["丁酸 / 益生元 32 周干预",
               "生存分析与健康寿命评分",
               "无菌鼠粪菌移植验证"],
         outs=["一套可转化的营养干预方案",
               "肠道屏障衰老评价指标集"]),
]

for card, spec in zip(cards, CONTENT):
    cv.rect(card, fill="#ffffff", line=spec["acc"], lw=0.7, radius=1.4)
    numdot(Box(card.x + 4.0, card.y + 3.6, 9.0, 9.0), spec["tag"], spec["acc"])
    cv.text(Box(card.x + 16.0, card.y + 2.8, card.w - 18.0, 10.0),
            "研究内容" + spec["tag"] + "  " + spec["title"],
            size=F_MOD, bold=True, colour=spec["acc"], align="l")
    cv.divider(card.x + 4.0, card.y + 13.6, card.x2 - 4.0, card.y + 13.6,
               colour=RULE, lw=0.5)

    # 目标行
    cv.text(Box(card.x + 4.0, card.y + 14.6, card.w - 8.0, 5.4),
            "研究目标：" + spec["goal"], size=F_TINY, colour=INK, align="l")

    body = Box(card.x + 4.0, card.y + 20.6, card.w - 8.0, card.h - 22.6)
    kcol, ocol = body.cols([body.w * 0.60, body.w * 0.40 - 3.0], gap=3.0)
    cv.text(Box(kcol.x, kcol.y, kcol.w, 4.6), "关键技术", size=F_HEAD, bold=True,
            colour=INK3, align="l")
    cv.text(Box(ocol.x, ocol.y, ocol.w, 4.6), "可验证产出", size=F_HEAD, bold=True,
            colour=INK3, align="l")
    for i, k in enumerate(spec["keys"]):
        yy = kcol.y + 6.4 + i * 7.4
        cv.rect(Box(kcol.x, yy, 2.4, 2.4), fill=spec["acc"], line=None, radius=1.2)
        cv.text(Box(kcol.x + 4.2, yy - 1.4, kcol.w - 4.2, 5.4), k, size=F_BODY,
                align="l", colour=INK2)
    for i, o in enumerate(spec["outs"]):
        yy = ocol.y + 6.4 + i * 7.4
        cv.text(Box(ocol.x, yy - 1.4, ocol.w, 5.4), "▸ " + o, size=F_BODY,
                align="l", colour=INK)
    cv.divider(ocol.x - 2.0, body.y + 1.0, ocol.x - 2.0, body.y2, colour=RULE, lw=0.5)

# ------------------------------------------------------------------ C 创新点
INNO = Box(M, 210.5, CW, 18.0)
cv.rect(INNO, fill="#fdf6ee", line="#e6c9a8", lw=0.7, radius=1.2)
cv.text(Box(INNO.x + 3.0, INNO.y + 1.2, 32.0, 5.0), "★ 创新点", size=F_SECT,
        bold=True, colour=AMBER, align="l")
inno_rows = ["① 首次构建「菌群–丁酸–GPR43」因果链",
             "② 建立可量化的屏障衰老评价指标集",
             "③ 提出可转化的精准营养干预方案"]
for i, t in enumerate(inno_rows):
    cv.text(Box(INNO.x + 3.0 + i * (CW - 6.0) / 3.0, INNO.y + 6.6,
                (CW - 6.0) / 3.0 - 3.0, 9.6), t, size=F_TINY, align="l", colour="#6b4a28")

# ------------------------------------------------------------------ D 预期成果
OUT = Box(M, 232.5, CW, 28.0)
oc = panel(OUT, "预期成果与考核指标", acc=NAVY)
quads = oc.cols(4, gap=4.0)
DELIV = [("论文", "SCI 5 篇\n（二区以上 3 篇）"), ("知识产权", "发明专利 1–2 项\n干预配方 1 套"),
         ("人才", "博士 1 名\n硕士 2–3 名"), ("转化", "营养方案 1 套\n临床合作 1 家")]
for q, (h, t) in zip(quads, DELIV):
    cv.text(Box(q.x, q.y, q.w, 4.6), h, size=F_HEAD, bold=True, colour=BLUE, align="l")
    cv.text(Box(q.x, q.y + 4.6, q.w, q.h - 5.0), t, size=F_BODY, align="l",
            colour=INK2, spacing=1.14)

# ------------------------------------------------------------------ E 风险与对策
RISK = Box(M, 264.0, CW, 24.0)
rc = panel(RISK, "风险与对策", acc=INK3)
trio = rc.cols(3, gap=4.0)
RISKS = [("干预效应不足", "剂量梯度 + 益生元联合"),
         ("敲除鼠表型轻微", "条件敲除 + 类器官互补"),
         ("人群样本受限", "多队列公共数据复核")]
for q, (risk, fix) in zip(trio, RISKS):
    cv.text(Box(q.x, q.y, q.w, 4.6), "风险：" + risk, size=F_TINY, bold=True,
            colour=RED, align="l")
    cv.text(Box(q.x, q.y + 4.4, q.w, 5.0), "对策：" + fix, size=F_TINY, align="l",
            colour=INK2)

# ------------------------------------------------------------------ 竖向主干
spine = M + 8.5
for y0, y1 in [(56.5, 60.5), (109.2, 114.2), (162.8, 167.8)]:
    cv.arrow((spine, y0), (spine, y1), colour=NAVY, lw=1.4)

# ------------------------------------------------------------------ 自检 + 导出
print(format_report(static_report(cv, mode="print")))
pptx = cv.save(os.path.join(OUTDIR, "nsfc-a4-demo.pptx"))
print(export.render(pptx, OUTDIR, dpi=600, also_pdf=True))



