---
name: tech-route-atlas
description: 用 routekit 绘制期刊级技术路线图、研究框架图、机制图与图形摘要（BioRender / SciDraw 风格）。当用户要做"技术路线图""研究框架图""实验流程图""机制假说图""图形摘要""方案总览""课题路线"或在 PPT/论文里插入多面板路线图时使用。给出画布规格、分区结构、箭头拓扑、毫米级布局、原生 PowerPoint 形状、600 dpi PNG + 矢量 PDF 的完整实现路径，并附 7 分区黑米-菌群范例脚本。
whenToUse: 用户要画或改一张技术路线图 / 框架图 / 图形摘要；或者需要把已有图整理成分区+箭头+卡片的结构。
---

# 技术路线图绘制（routekit 主流程）

一张合格的路线图 = **分区骨架 + 箭头拓扑 + 图标语义 + 期刊排版**。
routekit 把前两件事变成可计算的毫米坐标，把第三件事接到 3715 个矢量素材上，第四件事交给 6 套调色板。

## 先写规格，再写代码

每次开工先产出这 5 行（写进 `spec.md` 或回答开头），缺一不可：

```
画布: slide_16x9 254×142.9 / double_column 180×110 / single_column 85×90 / graphical_abstract 120×60
故事: 一句话论点（谁 → 做了什么 → 得到什么结论）
分区: zone 编号 + 标题（中英）+ 每区一句话结论 + 相对宽度权重
箭头: 箭头拓扑表（见下）
风格: palette=cell|nature|science|lancet|biorender|mono；字体 KaiTi + Times/Cambria（PDF 用 Cambria 确保嵌入）
```

箭头拓扑表（画之前必须写，改图时先核对它）：

| ID | From | To | 线型 | 语义 | 优先级 |
|----|------|----|------|------|--------|
| A1 | Zone1 分组 | Zone2 时间轴 | 实线粗 | 同一批动物进入纵向追踪 | P0 |
| A2 | Zone6 卡片3 | Zone6 卡片4 | 实线细 | 因果推进 | P1 |
| A3 | Zone6 卡片4 | Zone6 卡片2 | 虚线 | 反向调控 | P2 |

## 六步工作流

1. **规格**：上面 5 行 + 箭头拓扑表。
2. **检索素材**：每个图标位先 `python -m routekit.icons search "<中文关键词>" -k 8 --sheet sheet.png`，
   看缩略图再定 id（详见 `sciglyph-catalog` 技能）。放 ≥8 mm 的位置只用 `format="illustration"`。
   要写实插画级（BioRender 观感）就用远程库：`python -m routekit.remote search "colon" -c servier --sheet s.png`，
   id 形如 `bioicons/servier/Human_physiology/colon`，`cv.icon()` 会在首次使用时自动下载，
   许可与署名规则见 `references/remote.md`。
3. **搭骨架**：只放分区 + 标题 + 卡片外框，先不写正文，导出看一眼版面比例。
4. **填内容**：按 `Box.rows/cols` 分配，逐块填图标 + 标题 + 副文案；`Canvas.text` 自动收缩，
   但**先量后放**仍要守：文案长度 ≈ 框宽 ÷ (字号 × 0.35) 个汉字。
5. **连箭头**：按拓扑表逐条落地，折线用 `cv.route([...])`，L/Z 用 `cv.elbow()`。
6. **渲染 + 自检**：`cv.export(out_dir, dpi=600)` → 看 PNG → 修 → 复看，直到
   `static_report` 0 error 且肉眼无遮挡（见 `route-visual-qa`）。

## 最小可运行骨架

```python
import sys; sys.path.insert(0, r"D:\dsh-bundles\tech-route\skills\tech-route-atlas\scripts")
from routekit import Canvas, Box, T, S, G, R, CANVAS
from routekit.audit import static_report, format_report

W, H = CANVAS.slide_16x9          # 254 × 142.9 mm
cv = Canvas(W, H, palette="cell", title="demo")
M = 4.0
top = Box(M, 14, W - 2*M, 56)
z1, z2 = top.cols([47, 79], gap=2.6)

c = cv.zone(z1, "1  实验设计  Study design", acc=0)     # 返回内容区 Box
for arm, r in zip(["WGBR", "WGWR", "PR", "ST"], c.rows(4, gap=1.8)):
    cv.chip(Box(r.x, r.cy - 3.1, 15, 6.2), arm, acc=0, mode="solid", size=6.0, bold=True)
    cv.icon(Box(r.x + 16.6, r.y, 12.6, r.h), "bioicons/mouse-gray")
    cv.text(Box(r.x + 30.4, r.y, r.w - 30.6, r.h), "全谷物黑米", size=6.6)

pptx = cv.save("out/demo.pptx")
print(format_report(static_report(cv, mode="deck")))
cv.export("out", dpi=600)          # → demo.png (600 dpi) + demo.pdf
```

`cv.export()` 是 `save` + PowerPoint COM 渲染的合体（`__init__.py` 里挂上去的）。想分步就
`from routekit import export; export.render(pptx, "out", dpi=600)`。

## 布局模式库（照抄即可）

**A. 顶四底三（最像 BioRender 的综述图）**
顶排 4 区（研究设计 / 采样 / 取材 / 结局）权重 `[47,79,67,45]`，底排 3 区
（多组学 / 机制 / 人群验证）权重 `[108,72,58]`，中间留 2.6 mm 缝，底部一条 7 pt 总括句。
范例：`examples/build_demo.py`。

**B. 单列流水线（Pipeline）**
`CANVAS.double_column 180×110`，3–5 个 `block_arrow` 竖排，每段左边图标右边文字；
段间用 `cv.block_arrow(Box(...), direction="down", acc=i)`。

**C. 漏斗 / 筛选（Cohort → 纳入 → 分析）**
左侧竖排 4 个卡片逐级缩窄宽度（`ladder(b, 4, step=8, axis="h")`），右侧挂对应样本量。

**D. 循环机制（Feedback loop）**
中间一个圆形 `radial(b, 5, radius=30)` 取 5 个锚点放卡片，箭头沿线用 `cv.route` 连成闭环；
反向调控一律虚线 + 图注说明。

**E. 时间轴 / 剂量梯度**
`divider` 画轴线，`chip` 标时间点，下方挂图标；轴线右端标单位（月龄 / 周 / Gy）。

## 分区（zone）约定

- 每个 zone 有独立淡色底 + 同色系标题带；`acc` 0–7 轮转，**相邻 zone 不要同色**。
- 标题写「序号 + 中文 + 英文」：`5  多组学整合 · mGWAS 宿主–菌群互作  Integrative mGWAS`。
- zone 内部留白 1.2 mm（`G.xs`），卡片圆角 `R.chip=0.9`，分区圆角 `R.card=1.4`。
- 卡片正文左对齐、标题加粗 6.4–6.6 pt、副文案 5.6–5.8 pt；数值不要和单位拆行。

## 常见坑（都踩过）

| 现象 | 原因 | 修法 |
|---|---|---|
| 图标放大后像钢笔尖 / 一团黑 | 用了 SciGlyph `format="icon"` 线稿 | 换 `format="illustration"` 同主题素材 |
| 文字溢出卡片 | 手算坐标 + 未自动收缩 | 用 `Box.rows/cols`，让 `text()` 自动收缩 |
| 虚线在每个拐点"断" | 多段独立线段 | `cv.route([...])` 一条 freeform |
| 卡片高低不齐 / 底部空白大 | 高度写死 | `area.rows(n, gap)` 均分 |
| 中文变方框 / 字号忽大忽小 | 未设 ea 字体或用了 .5 字号 | 统一 `KaiTi`；字号取整或 .5 |
| 热图/曲线配色跳脱 | 默认 matplotlib | 用 `routekit.miniplot` 的 palette-locked 系列 |
| 图整体发灰 | zone 底与卡片底太接近 | 卡片用 `p.paper`，zone 用 `p.zone(i)` |

## 参考

- `references/api.md` — Canvas / Box / palette / miniplot 全量签名与语义
- `references/patterns.md` — 12 种分区骨架的坐标写法
- `references/arrows.md` — 箭头拓扑、折线、避让、图注约定
- `examples/build_demo.py` + `examples/black-rice-route.png/.pptx` — 7 分区完整范例
