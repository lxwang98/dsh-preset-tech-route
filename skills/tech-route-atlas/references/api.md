# routekit API 速查

导入（脚本必须先把 `scripts/` 加进 sys.path）：

```python
import sys
sys.path.insert(0, r"D:\dsh-bundles\tech-route\skills\tech-route-atlas\scripts")
from routekit import Canvas, Box, T, S, G, R, CANVAS, DPI, P, PALETTES, tint, shade, mix
from routekit import miniplot as mp
from routekit.export import render, to_png, to_pdf, to_svg, com_audit
from routekit.audit import static_report, format_report, design_check
```

## tokens（尺寸记号）

| 记号 | 值 | 用途 |
|---|---|---|
| `T.micro 4.5 / caption 5.5 / small 6 / body 7 / sub 8 / head 9 / panel 9.5 / title 12 / hero 16` | pt | 印刷体字号阶梯 |
| `T.deck_body 10 / deck_head 12 / deck_title 18` | pt | 纯文字幻灯片 |
| `S.hair .4 / thin .6 / base .8 / bold 1.1 / heavy 1.6 / rule .9` | pt | 线宽 |
| `R.chip .9 / card 1.4 / zone 1.8 / pill 99` | mm | 圆角半径 |
| `G.xxs .8 / xs 1.2 / s 1.8 / m 2.6 / l 3.6 / xl 5 / xxl 7` | mm | 间距 |
| `CANVAS.double_column 180×110` | mm | Nature 双栏满宽 |
| `CANVAS.single_column 85×90` | mm | 单栏 |
| `CANVAS.full_page 180×235` | mm | 整页竖版 |
| `CANVAS.slide_16x9 254×142.9` / `slide_4x3 203.2×152.4` | mm | 汇报 |
| `CANVAS.graphical_abstract 120×60` / `poster_band 300×80` | mm | 图形摘要 / 海报条 |
| `DPI.print 600 / review 150 / deck 220 / web 96` | dpi | 导出 |
| `line_height_mm(pt, spacing=0.95)` | mm | 行高换算（在 `.tokens` 里） |

## Box（毫米矩形，frozen dataclass）

`Box(x, y, w, h)`，属性 `x2 y2 cx cy area`，方法：

```python
b.inset(dx, dy=None)      # 内缩
b.inner(pad)              # 四边等距内缩
b.moved(dx, dy)
b.with_h(h) / b.with_w(w)
b.align(other, "center"|"left"|"right"|"top"|"bottom")
b.rows(n_or_weights, gap) # 纵向均分，返回 list[Box]（权重列表可不等分）
b.cols(n_or_weights, gap) # 横向均分
b.row(i, n, gap) / b.col(i, n, gap)
b.flow(n, axis="h", gap)
b.anchor("top"|"bottom"|"left"|"right"|"center", frac=0.5)  # -> (x, y) 连线锚点
```

模块级：`even_slots(b, n, axis, gap)`、`center_in(b, w, h)`、`stack_top(b, heights, gap)`、
`stack_left(b, widths, gap)`、`grid(b, rows, cols, gap)`、`ladder(b, n, step, axis)`、
`radial(b, n, radius, start_deg)`。

## Canvas

```python
Canvas(w, h, *, palette="cell", margin=0.0, background=True,
       font="Arial", cjk_font="Microsoft YaHei", title="")
```
字段：`prs slide p frame bbox notes warnings`。

```python
bg(colour)
rect(b, *, fill=None, line=None, lw=S.base, radius=None, dash=None,
        shadow=False, alpha=None, line_alpha=None, name="")
zone(b, title="", *, acc=0, fill=True, band=True, pad=G.xs, radius=R.card,
        title_pt=None, edge=True) -> Box          # 返回内容区
band_header(b, title, *, acc=0, height=7.0, sub="")
text(b, s, *, size=None, bold=False, italic=False, colour=None, align="c",
        anchor="m", font=None, spacing=0.95, min_size=T.micro*0.85,
        wrap=True, line_spacing=None, margin=0.0, autofit=True, name="")
icon(b, asset, *, pad=0.0, tint_colour=None, px=1100, name="")   # 等比内接
chip(b, s, *, acc=0, size=None, mode="fill"|"solid"|"wash"|"outline",
        bold=False, radius=None)
badge(centre, n, *, r=2.2, colour=None, text_colour=None)         # 圆形编号
arrow(p1, p2, *, colour=None, lw=S.bold, head="triangle", dash=None,
        start=None, shrink=0.0)
route(pts, *, colour=None, lw=S.bold, head="triangle", start=None, dash=None)
elbow(p1, p2, *, mode="hv"|"vh", colour=None, lw=S.bold, head="triangle", dash=None)
block_arrow(b, direction="right"|"down"|"left"|"up", *, acc=0, label="", size=None)
chevron(b, label, *, acc=0, size=None, first=False, last=False)
divider(x1, y1, x2, y2, *, colour=None, lw=S.rule, dash=None)
number_bar(b, n, *, acc=0, size=None)
legend(b, items: [(label, colour)], *, size=None, marker="line"|"dot"|"box",
        cols=None, gap=G.s)
plot(b, draw, *, dpi=300, transparent=False, cache_dir=None, name="plot")
save(path) -> Path
summary() -> dict
```

**plot() 的落地规则**：图按 `b` 的毫米尺寸建 fig，`savefig(bbox_inches="tight")`
（因此刻度与轴标题永远不会被裁掉），再按比例居中放进 `b`（同比例缩放、留白），
不会拉伸变形。轴标题建议用英文（`Age (months)` / `Survival (%)`）：4.5–5 pt 的中英混排
在 20 mm 高的插图中会挤在一起。

**text() 的排版契约**：`s` 里的 `\n` 是硬换行；每段再按真实字宽折行；
`word_wrap=False`（PowerPoint 不会二次折行），因此高度由 `fit_paragraphs` 预先算准；
`autofit=True` 时从 `size` 逐 0.25 pt 降到 `min_size`。返回 `None`。

## palette

```python
p = P("cell")            # cell | nature | science | lancet | biorender | mono
p.paper p.ink p.ink2 p.ink3 p.rule p.wash p.muted
p.zone(i) p.zone_line(i) p.zone_pair(i) p.accent(i) p.accent_soft(i, k=.78)
p.series(n) p.ramp(n, base=None, lo=.15, hi=.85) p.on(bg)
semantic_colour("up"|"down"|"neutral"|"acute"|"chronic", p)
updown_arrows(p)
tint(c,k) shade(c,k) mix(a,b,t) luminance(c) contrast(a,b) readable_on(bg)
```

`p.zone(i)` 是分区淡底，`p.zone_line(i)` 是同色系标题带 / 描边色；
相邻分区 `acc` 必须不同，且 `design_check` 要求 `ink` 对 `zone` 的对比度 ≥7。

## miniplot（配色已锁定调色板）

```python
mp.bars(series, p, *, labels=None, ylabel="", xlabel="", errors=None,
        legend=True, zero_base=True)
mp.lines(series, p, *, xlabel="", ylabel="", legend=True, markers=True,
        log=False, band=None)              # series: {name: (xs, ys)}
mp.survival(curves, p, *, xlabel="Age (months)", ylabel="Survival (%)",
        xticks=None, legend=True)          # 阶梯 post，纵轴 0–100
mp.heat(matrix, p, *, row_labels=None, col_labels=None, cmap="Blues",
        vmin=None, vmax=None, cbar=False, center=None)
mp.scatter(points, p, *, xlabel="", ylabel="", size=None, fit=False, legend=True)
mp.sparkline(values, p, *, colour=None, fill=True)
```

全部返回 `draw(fig)` 回调，交给 `cv.plot(box, draw)` 落地成图片（b 决定图幅与纵横比）。

## audit / export

```python
issues = static_report(cv, mode="print"|"deck")
print(format_report(issues, limit=40))
design_check(cv, cv.p)

render(pptx, out_dir, dpi=600, stem=None, slide=1, also_pdf=True)  # -> {"png":…, "pdf":…}
to_png(pptx, png, dpi=300, width_px=None, slide=1)
to_pdf(pptx, pdf, slide=1); to_svg(pptx, svg, slide=1)
com_audit(pptx, tol_pt=0.6)   # TextFrame2 真实文本边界 vs 形状框
```

`static_report` 的 code：`off-canvas` `trim` `small-text` `text-overflow`
`label-collision` `icon-missing` `no-icons` `dense` `empty`。
error 必须清零；warning 只允许"说明性小字"存在（并在图注里交代）。
