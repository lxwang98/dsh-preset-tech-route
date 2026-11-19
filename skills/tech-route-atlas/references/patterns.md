# 分区骨架（12 种，可直接抄坐标）

所有坐标单位为 mm；`M` 为页边距（印刷 4–6，幻灯片 4）。`W, H = CANVAS.xxx`。

## 1. 顶四底三（综述型总图）

```python
top = Box(M, 13.6, W - 2*M, 56)
bot = Box(M, 71.4, W - 2*M, H - 71.4 - 9.6)
z1, z2, z3, z4 = top.cols([47, 79, 67, 45], gap=2.6)
z5, z6, z7    = bot.cols([108, 72, 58], gap=2.6)
```
适合"设计 → 采样 → 检测 → 结局 / 多组学 → 机制 → 人群验证"。
底部留 7 pt 总括句：`cv.text(Box(M, H-8.4, W-2*M, 5.2), "一句话结论", size=7, align="c")`。

## 2. 左竖右横（队列 / 分组 + 分析）

```python
left = Box(M, 14, 52, H - 30)
right = Box(M + 54, 14, W - 2*M - 54, H - 30)
for i, grp in enumerate(["WGBR", "WGWR", "PR", "ST"]):
    cv.chip(...)  # 左列每行一个分组
```

## 3. 三行流水线

```python
rows = Box(M, 14, W - 2*M, H - 30).rows(3, gap=6)
for r, (t, s) in zip(rows, steps):
    cv.zone(r.with_h(38), t)
```
行间用 `cv.block_arrow(Box(cx-6, r.y2+1, 12, 4), "down", acc=i)` 连接。

## 4. 漏斗 / 逐级筛选

```python
for i, n in enumerate([1240, 890, 610, 420]):
    b = Box(M + i*10, y + i*16, 90 - i*20, 14)   # 逐级缩窄
```
右侧用 `cv.text` 标样本量与排除原因。

## 5. 循环 / 反馈闭环

```python
pts = radial(Box(cx-30, cy-30, 60, 60), 5, radius=28, start_deg=-90)
for (x, y), (t, s) in zip(pts, cards):
    cv.chip(Box(x-11, y-4, 22, 8), t, mode="fill")
```
顺时针正向实线，逆时针反向虚线（`dash=4`），并在图注写"虚线=反向调控"。

## 6. 时间轴（纵向追踪）

```python
ax = Box(c.x+2, c.y+1, c.w-4, 21); y = ax.y + 6.2
cv.divider(ax.x, y, ax.x2-9, y, colour=p.zone_line(1), lw=S.bold)
step = (ax.w-9)/(len(ages)-1)
for i, a in enumerate(ages):
    x = ax.x + step*i
    cv.rect(Box(x-1.3, y-1.3, 2.6, 2.6), fill=p.paper, line=p.zone_line(1), radius=R.pill)
    cv.text(Box(x-6.5, y-5.6, 13, 4.2), a, size=6.2, bold=True)
    cv.icon(Box(x-3.8, y+2.2, 7.6, 10.4), tube_icon)
```

## 7. 模态条 + 输出（多组学）

```python
band = Box(c.x, c.y, c.w, 12.4)
for cell, (name, icon) in zip(band.cols(5, gap=1.4), mods):
    cv.rect(cell, fill=p.paper, line=p.rule, radius=R.chip)
    cv.icon(Box(cell.x+(cell.w-6.4)/2, cell.y+0.9, 6.4, 6.0), icon)
    cv.text(Box(cell.x+0.6, cell.y+7.0, cell.w-1.2, 4.6), name, size=5.6)
strip = Box(c.x+2, band.y2+1.2, c.w-4, 4.4)          # 处理步骤一句话
cv.rect(strip, fill=p.wash, radius=R.chip); cv.text(strip, "质控 · 比对 · 注释", size=5.8)
```

## 8. 编号步骤列（产出 / 结论）

```python
for i, (s, r) in enumerate(zip(outs, area.rows(4, gap=1.0))):
    cv.badge((r.x+1.5, r.cy), i+1, r=1.5, colour=p.zone_line(acc))
    cv.text(Box(r.x+4.0, r.y, r.w-4.2, r.h), s, size=6.0, align="l")
```

## 9. 机制阶梯（因果链）

```python
for i, ((t, s, a), card) in enumerate(zip(steps, area.rows(5, gap=2.2))):
    cv.rect(card, fill=p.paper, line=p.zone_line(a), lw=S.base, radius=R.chip)
    cv.rect(Box(card.x, card.y, 1.2, card.h), fill=p.zone_line(a), line=None)  # 左侧色条
    cv.text(Box(card.x+3, card.y+0.6, card.w-4.2, 4.0), t, size=6.6, bold=True, align="l")
    cv.text(Box(card.x+3, card.y+4.7, card.w-4.2, card.h-4.9), s, size=5.6, align="l", wrap=False)
    cv.arrow((card.x+card.w/2, card.y2+0.1), (card.x+card.w/2, cards[i+1].y-0.1))
```

## 10. 对比双栏（干预 vs 对照）

两栏 `cols([1,1], gap=3)`，中缝放 `cv.divider`，每栏顶部 `band_header` 上色区分（绿 vs 灰）。

## 11. 图形摘要（120×60）

只允许 3–5 个意象 + 1 条主箭头：`graphical_abstract` 画布下每块 ≤ 35 mm 宽，
字号 ≥6 pt，全部图标 `illustration`，不要小字注释。

## 12. 数据集 × 方法矩阵

`grid(b, rows, cols)` 出格子，对角/命中格填 `p.accent_soft(i,.6)` + 勾，
行列标签用 `T.caption`，命中率数字放格子中心。

## 13. GWAS Manhattan 面板（mGWAS / 人群验证两处通吃）

```python
# 左：SNP 矩阵 → 曼哈顿；右：复现（曼哈顿 + 相关散点）
cv.text(Box(p3.x+2, p3.y+7.4, 30, 3.2), "SNPs", size=6.6, bold=True, align="c")
snp_blocks(Box(p3.x+3, p3.y+11.0, 26, 12.2))
cv.plot(Box(p3.x+3, p3.y+24.6, 26, 20.4), mp.manhattan(cv.p, nchr=10, n_per_chr=110))
# 窄面板（< 25 mm）只留形状：labels=False
cv.plot(Box(c.x+1, c.y+11, 23, 15.4), mp.manhattan(cv.p, nchr=10, n_per_chr=70, labels=False))
```

硬规则（缺一条就不叫 Manhattan，见 `USER_PRESET.md` §5.1）：

1. x 轴是**累加染色体位置**，不是 bp/Mb；刻度落在染色体段中心、文字写染色体号。
2. y 轴是 `−log10(P)`，只标 `0 / 4 / 8` 三个刻度。
3. 染色体**奇偶交替**上色（`#3f7099` / `#a8c2d6`），否则读不出"分了几条染色体"。
4. 两条阈值线：genome-wide 实线（`p<5e-7`→6）与 suggestive 虚线（`p<1e-4`→4）。
5. 阈值之上的峰必须**换色**（红 `#c0392b` = 显著，绿 `#2f9e44` = 提示性），
   qqman 的 `highlight=` 就是这个语义；否则只是一团散点。
6. 面板宽度 < 25 mm 时不写任何刻度文字（删字，不要 3 pt 硬塞）。
7. 数据来源：真实 p 值走 `data={chrom: [pvals]}`；示意值必须用同一函数生成，
   图注写 "schematic / 示意值"，禁止贴截图、禁止换字体。

## 通用准绳

- 分区之间 gap ≥ 2.2 mm；卡片之间 ≥ 1.6 mm；正文与边框 ≥ 1.2 mm。
- 同一层级的卡片必须**等宽等高**（用 `rows/cols`），不允许 1 mm 级别的手工微调。
- 每个 zone 至少 1 个图标；纯文字 zone 超过 60 字就该拆。
- 视觉重心：左上/中部放最重要的一块，右下放"结论/转化"。
- 顶部标题 ≤ 16 pt，副标题 7–7.5 pt 右对齐；底部总括句 7 pt 居中。
