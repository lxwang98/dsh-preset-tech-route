---
name: route-visual-qa
description: 技术路线图/框架图/图形摘要的视觉质检与导出：用 PowerPoint COM 把 pptx 渲染成 600 dpi PNG 与矢量 PDF，用真实文本边界审计溢出/越界/字号地板/标签碰撞，再按"一眼看过去能不能直接投稿"的清单做人工复核与修订。交付前必走。也用于批量导出、改图后回归检查。
whenToUse: 图已经画完要交付；或用户反馈"字挤了/框图错位/导出糊/颜色不对"；或要一次导出 PNG+PDF+SVG 多个格式。
---

# 视觉质检与导出

渲染引擎是**本机 PowerPoint COM**（不是 LibreOffice）。它给的文本边界是真实的排版结果，
所以"字有没有溢出框"这件事是**测出来的**，不靠猜。

## 一键出图 + 审计

```python
import sys; sys.path.insert(0, r"D:\dsh-bundles\tech-route\skills\tech-route-atlas\scripts")
from routekit.audit import static_report, format_report, design_check
from routekit.export import render, com_audit

issues = static_report(cv, mode="print")        # 幻灯片内图用 mode="deck"
print(format_report(issues))
design_check(cv, cv.p)                          # 对比度/配色自检

pptx = cv.save("out/fig.pptx")
paths = render(pptx, "out", dpi=600, stem="fig")   # -> {"png":…, "pdf":…}
print(com_audit(pptx, tol_pt=0.6))                # 真实文本 vs 形状框
```

或一行 `cv.export("out", dpi=600)`（= save + render）。

## 审计代码含义与处置

| code | 级别 | 含义 | 处置 |
|---|---|---|---|
| `off-canvas` | error | 元素超出画布 | 改坐标；通常是手算 x2 出错 |
| `trim` | error | 距裁切线 <2 mm | 内容区整体内缩 |
| `text-overflow` | error | 文本超出形状框 | 删字、缩字号、改 `rows()` 分配 |
| `label-collision` | warning | 两个文本块 IoU>55% | 挪位；时间轴标签最常见 |
| `small-text` | warning | 低于地板（print 5.0 / deck 5.5 pt） | 说明性小字可留，正文级必须提 |
| `icon-missing` | error | catalog 里没有该 id | `require()` 拿建议 id，或换素材 |
| `no-icons` | warning | 某 zone 一个图标都没有 | 补图标或确认是纯文字区 |
| `dense` / `empty` | warning | 元素过密 / 区域空 | 调整信息密度 |

**收敛标准**：0 error；warning 只剩"图注级小字"且总数 ≤ 8。
`com_audit` 另外报 `overflow`（BoundWidth/BoundHeight 超框）与 `outside`（越出画布）。

## 人工复核清单（渲图后逐条看）

1. **缩到 25%** 还看得出分区和主线吗？看不出 → 层级不够（加标题带/加大色差）。
2. **眯眼测试**：颜色块分布是否平衡？有没有一边重一边空？
3. 每个 zone 的标题是否都完整（没被裁、没换行成孤儿字）？
4. 所有卡片高度是否一致、底边是否对齐（差 1 mm 都看得出来）？
5. 箭头：有没有穿过文字？虚线是否连续？箭头尖端是否落在边上？
6. 图标：有没有明显风格不一致（线稿 vs 插画混用）、比例失衡（显微镜比小鼠大 3 倍）？
7. 文字：中文有没有方框/缺字？数字与单位是否被拆行？英文与中文基线是否协调？
8. 颜色：相邻 zone 是否撞色？语义色（绿↑红↓）是否用反？
9. 留白：四边是否 ≥2 mm？zone 之间是否有 ≥2 mm 缝？
10. 导出：PNG 是否 ≥300 dpi（印刷 600）、PDF 文字能否选中、字体是否内嵌？

## 常见缺陷 → 修法

| 症状 | 根因 | 修法 |
|---|---|---|
| 字压线/压图标 | 框高按"字数×行高"硬算 | 用 `Box.rows/cols`；`text()` 自动收缩 |
| 两行字变一行挤爆 | 用了 `wrap=False` 但文案太长 | 改 `wrap=True` 或缩短文案 |
| 卡片底部大片空白 | 固定高度 > 内容 | `rows(n, gap)` 均分，或垂直居中 `anchor="m"` |
| 热图色块糊成一片 | 无 cell 边界 + 低对比 cmap | `mp.heat(..., vmin=0, vmax=1)`；必要时加白描边 |
| 曲线压住图例 | 图例放角上但曲线也走角上 | 图例移到图外右侧，或 `legend=False` 用文字标注 |
| 导出 PNG 发灰/模糊 | dpi 不足或缩放过 | `dpi=600`；不要用 96 dpi 的截图放大 |
| PowerPoint 里字变形 | 用了系统没有的字体 | 只用 Arial / Microsoft YaHei / Times New Roman |
| 交付 pptx 打不开 | 保存时文件被占用 | 先关闭 PowerPoint 里的同名文件再导出 |

## 导出规格

| 用途 | 格式 | 参数 |
|---|---|---|
| 投稿（矢量） | PDF | `render(..., also_pdf=True)`；字体已内嵌 |
| 投稿（位图要求） | PNG/TIFF | `dpi=600`，宽 ≥3000 px |
| 汇报 PPT | PNG | `dpi=220`（16:9 全屏 ≈ 2200 px 宽） |
| 网页/预印本 | PNG | `dpi=150` |
| 二次编辑 | PPTX / SVG | `to_svg(pptx, "out/fig.svg")`（PowerPoint 导出 SVG） |

## 交付话术

给用户三件套 + 一句自检结论，例如：
"已导出 `fig.pptx`（可编辑）/ `fig.png`（600 dpi，6000×3376）/ `fig.pdf`（矢量）。
审计 0 error、5 warning（均为 5.2–5.3 pt 图注小字）；已按 25% 缩略与眯眼测试复核，
分区层级与箭头拓扑清晰。素材署名见 `ATTRIBUTION.md`。"
