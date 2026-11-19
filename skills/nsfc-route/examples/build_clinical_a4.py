# -*- coding: utf-8 -*-
"""
国自然技术路线图 · 临床研究口（前瞻性队列 + 分层干预）A4 竖排范例
=================================================================
规格（4 行，画之前必须写）
  画布: 210 x 297 mm (CANVAS.nsfc_a4)，边距 12 mm；绝不跨页
  故事: 老年住院患者 菌群–SCFA 轴 → 肌少症与不良结局；回顾性建队列 → 前瞻性验证
        → 随机分层干预 + 风险模型，落在 4 类可考核成果
  分区: A 科学问题与假说（含伦理/注册占位行）  B 研究内容一~三（目标·关键技术·可验证产出，
        内容三内嵌森林图）  C 创新点  D 预期成果  E 风险与对策
  箭头: 左侧竖向主干 A→B1→B2→B3；区内横向推进；实线主链；跨区不交叉

箭头拓扑表
  ID | From        | To          | 线型 | 语义                  | 优先级
  S0 | 假说条      | 研究内容一   | 实线 | 假说落地              | P0
  S1 | 研究内容一  | 研究内容二   | 实线 | 回顾→前瞻验证         | P0
  S2 | 研究内容二  | 研究内容三   | 实线 | 队列→随机干预         | P0
  H1 | 前期基础    | 科学问题     | 实线 | 发现→提炼临床问题     | P0
  H2 | 科学问题    | 工作假说     | 实线 | 问题→提出假说         | P0

临床口要点（见 references/clinical.md）：纳排、样本量、主要终点、随访、统计方法、伦理/注册
必须能在图上找到；图上统计图 ≤2 张，本范例只放 1 张森林图。
"""
import os
import sys

sys.path.insert(0, r"D:\dsh-bundles\tech-route\skills\tech-route-atlas\scripts")
from routekit import Canvas, Box, CANVAS
from routekit import miniplot as mp
from routekit.audit import static_report, format_report
from routekit import export

NAVY = "#1b3a63"
BLUE = "#2e6e9e"
SKY = "#5a8fbf"
AMBER = "#b87333"
RED = "#8a2f3a"
INK, INK2, INK3 = "#16222b", "#455766", "#76879a"
RULE, WASH = "#c2cfda", "#f6f9fb"

F_TITLE, F_SUB = 17.0, 9.6
F_SECT, F_MOD = 10.0, 12.6
F_HEAD, F_BODY, F_TINY = 9.0, 9.0, 8.2

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUTDIR, exist_ok=True)

W, H = CANVAS.nsfc_a4
M = 12.0
CW = W - 2 * M
cv = Canvas(W, H, palette="cell", cjk_font="SimHei", title="nsfc-clinical-demo")


def panel(b, title="", *, acc=NAVY, fill="#ffffff"):
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
        "老年住院患者菌群–SCFA 轴与肌少症不良结局：队列验证与分层干预研究",
        size=F_TITLE, bold=True, colour=NAVY)
cv.text(Box(M, 21.0, CW, 5.2),
        "国家自然科学基金面上项目（2026–2029） · 临床研究技术路线图  Clinical Route",
        size=F_SUB, colour=INK3, align="l")

# ------------------------------------------------------------------ A 问题与假说
HYP = Box(M, 28.5, CW, 30.0)
hc = panel(HYP, "临床问题与工作假说", acc=NAVY)
segs = [("前期基础（单中心回顾）", NAVY,
         "320 例老年住院患者：粪便 SCFA↓、\nSCFA 产生菌↓ 与肌少症、1 年全因死亡相关"),
        ("关键临床问题", RED,
         "菌群–SCFA 轴能否作为老年肌少症\n不良结局的早期预警与干预靶点？"),
        ("工作假说", "#2f7d55",
         "SCFA↓→屏障通透性↑→慢性炎症→\n肌肉分解↑→功能衰退；补丁酸可改善")]
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

# 伦理 / 注册 / 样本量 占位（临床口必须有）
ETH = Box(M + 22.0, 59.6, CW - 22.0, 5.0)
cv.rect(ETH, fill="#fbfcfd", line=RULE, lw=0.5, radius=1.0)
cv.text(Box(ETH.x + 2.0, ETH.y, ETH.w - 4.0, ETH.h),
        "伦理批号 ____-KY-____｜注册号 ChiCTR________（前瞻队列 / RCT）｜"
        "样本量按 α=0.05、power=0.80、失访 15% 估算",
        size=F_TINY, colour=INK2, align="l")

# ------------------------------------------------------------------ B 研究内容
BODY = Box(M, 66.0, CW, 146.0)
cards = BODY.rows(3, gap=4.9)

CONTENT = [
    dict(tag="一", acc=NAVY, title="回顾性队列：SCFA 轴与肌少症结局的关联",
         goal="在既有住院队列中确认 SCFA 轴与肌少症、不良结局的剂量–反应关系",
         keys=["2018–2024 单中心队列，n≈1200；入组 ≥65 岁、住院≥48 h",
               "排除：活动性感染、终末期肿瘤、近期抗生素",
               "粪便 SCFA 靶向定量 + 16S；血 hs-CRP、IL-6",
               "主要终点：1 年全因死亡；次要：握力、SPPB"],
         outs=["SCFA 三分位的 KM 曲线（OS）",
               "多因素 Cox + 倾向评分匹配结果"]),
    dict(tag="二", acc=BLUE, title="前瞻性队列与生物样本库：动态轨迹与机制",
         goal="刻画住院期至出院 12 个月的 SCFA 轨迹，明确其与功能衰退的时序关系",
         keys=["前瞻纳入 n=600；基线 / 6 / 12 月随访",
               "生物样本库：粪便、血清、外周血 PBMC",
               "宏基因组 + 靶向代谢组 + 炎症面板",
               "主要终点：12 月 SPPB 下降≥1 分或死亡"],
         outs=["SCFA 轨迹分型（latent class）",
               "菌群–代谢–炎症中介分析（mediation）"]),
    dict(tag="三", acc=SKY, title="随机分层干预与风险预测模型",
         goal="验证靶向补丁酸能否改善功能结局，并交付可用的风险分层工具",
         keys=["RCT 1:1，n=240；丁酸甘油酯 vs 安慰剂，12 周",
               "分层因素：肌少症分期、SCFA 三分位",
               "主要终点：12 周 SPPB 变化；次要：握力、IL-6、AE",
               "统计：ITT 分析 + 多因素 Cox + ROC/校准曲线"],
         outs=["干预效应量与安全性报告",
               "风险预测模型（AUC、校准）"]),
]

for idx, (card, spec) in enumerate(zip(cards, CONTENT)):
    cv.rect(card, fill="#ffffff", line=spec["acc"], lw=0.7, radius=1.4)
    numdot(Box(card.x + 4.0, card.y + 3.2, 8.6, 8.6), spec["tag"], spec["acc"])
    cv.text(Box(card.x + 15.4, card.y + 2.4, card.w - 17.4, 9.4),
            "研究内容" + spec["tag"] + "  " + spec["title"],
            size=F_MOD, bold=True, colour=spec["acc"], align="l")
    cv.divider(card.x + 4.0, card.y + 12.4, card.x2 - 4.0, card.y + 12.4,
               colour=RULE, lw=0.5)
    cv.text(Box(card.x + 4.0, card.y + 13.2, card.w - 8.0, 5.0),
            "研究目标：" + spec["goal"], size=F_TINY, colour=INK, align="l")

    body = Box(card.x + 4.0, card.y + 18.8, card.w - 8.0, card.h - 20.6)
    if idx < 2:
        kcol, ocol = body.cols([body.w * 0.62, body.w * 0.38 - 3.0], gap=3.0)
        vcol = None
    else:
        # 内容三右侧内嵌森林图（全图唯一统计图）
        kcol, ocol, vcol = body.cols([body.w * 0.46, body.w * 0.24,
                                      body.w * 0.30], gap=3.0)
    cv.text(Box(kcol.x, kcol.y, kcol.w, 4.6), "关键技术", size=F_HEAD, bold=True,
            colour=INK3, align="l")
    cv.text(Box(ocol.x, ocol.y, ocol.w, 4.6), "可验证产出", size=F_HEAD, bold=True,
            colour=INK3, align="l")
    for i, k in enumerate(spec["keys"]):
        yy = kcol.y + 5.2 + i * 4.9
        cv.rect(Box(kcol.x, yy, 2.4, 2.4), fill=spec["acc"], line=None, radius=1.2)
        cv.text(Box(kcol.x + 4.2, yy - 1.4, kcol.w - 4.2, 5.0), k, size=F_BODY,
                align="l", colour=INK2)
    for i, o in enumerate(spec["outs"]):
        yy = ocol.y + 5.2 + i * 4.9
        cv.text(Box(ocol.x, yy - 1.4, ocol.w, 5.0), "▸ " + o, size=F_BODY,
                align="l", colour=INK)
    cv.divider(ocol.x - 2.0, body.y + 1.0, ocol.x - 2.0, body.y2, colour=RULE, lw=0.5)
    if vcol is not None:
        cv.text(Box(vcol.x, vcol.y, vcol.w, 4.6), "亚组效应  HR（95% CI）",
                size=F_HEAD, bold=True, colour=INK3, align="l")
        forest_rows = [("SCFA 低", 1.92, 1.24, 2.97),
                       ("CRP 高", 1.55, 1.08, 2.23),
                       ("年龄>75", 1.41, 0.95, 2.10),
                       ("男性", 1.18, 0.82, 1.70)]
        cv.plot(Box(vcol.x, vcol.y + 5.4, vcol.w, vcol.h - 7.0),
                mp.forest(forest_rows, cv.p, log=True, values=False,
                          xlabel="", label_size=6.8),
                dpi=600, name="forest")

# ------------------------------------------------------------------ C 创新点
INNO = Box(M, 215.0, CW, 16.0)
cv.rect(INNO, fill="#fdf6ee", line="#e6c9a8", lw=0.7, radius=1.2)
cv.text(Box(INNO.x + 3.0, INNO.y + 1.2, 32.0, 5.0), "★ 创新点", size=F_SECT,
        bold=True, colour=AMBER, align="l")
inno_rows = ["① 首次刻画住院期 SCFA 轨迹分型",
             "② 菌群–SCFA–炎症–肌肉的中介链",
             "③ 可床旁使用的风险分层模型"]
for i, t in enumerate(inno_rows):
    cv.text(Box(INNO.x + 3.0 + i * (CW - 6.0) / 3.0, INNO.y + 6.4,
                (CW - 6.0) / 3.0 - 3.0, 9.4), t, size=F_TINY, align="l",
            colour="#6b4a28")

# ------------------------------------------------------------------ D 预期成果
OUT = Box(M, 234.0, CW, 26.0)
oc = panel(OUT, "预期成果与考核指标", acc=NAVY)
quads = oc.cols(4, gap=4.0)
DELIV = [("论文", "SCI 4 篇\n（二区以上 2 篇）"), ("知识产权", "预测模型软件 1 项\n检测试剂盒 1 套"),
         ("人才", "博士 1 名\n硕士 2 名"), ("转化", "临床路径 1 条\n多中心协议 1 份")]
for q, (h, t) in zip(quads, DELIV):
    cv.text(Box(q.x, q.y, q.w, 4.6), h, size=F_HEAD, bold=True, colour=BLUE, align="l")
    cv.text(Box(q.x, q.y + 4.6, q.w, q.h - 5.0), t, size=F_BODY, align="l",
            colour=INK2, spacing=1.14)

# ------------------------------------------------------------------ E 风险与对策
RISK = Box(M, 263.0, CW, 25.0)
rc = panel(RISK, "风险与对策", acc=INK3)
trio = rc.cols(3, gap=4.0)
RISKS = [("单中心样本偏倚", "多中心 + PSM + 敏感性分析"),
         ("失访率高", "随访专员 + 电话/上门双通道"),
         ("干预依从性差", "药盒计数 + 依从性亚组分析")]
for q, (risk, fix) in zip(trio, RISKS):
    cv.text(Box(q.x, q.y, q.w, 4.6), "风险：" + risk, size=F_TINY, bold=True,
            colour=RED, align="l")
    cv.text(Box(q.x, q.y + 4.4, q.w, 5.0), "对策：" + fix, size=F_TINY, align="l",
            colour=INK2)

# ------------------------------------------------------------------ 竖向主干
spine = M + 8.5
for y0, y1 in [(58.5, 66.0), (111.3, 116.2), (161.6, 166.5)]:
    cv.arrow((spine, y0), (spine, y1), colour=NAVY, lw=1.4)

# ------------------------------------------------------------------ 自检 + 导出
print(format_report(static_report(cv, mode="print")))
pptx = cv.save(os.path.join(OUTDIR, "nsfc-clinical-demo.pptx"))
print(export.render(pptx, OUTDIR, dpi=600, also_pdf=True))
