# 用户审美 / 布局 / 字体预设（可复用）

本文件是从 2026-11 与用户的真实改图会话中提炼的硬约束。新会话先读本文件，再读
`skills/tech-route-atlas` 的 references。**不要再用默认 Arial + Microsoft YaHei**。

## 1. 用户与交付目标

- 中文科研工作者，面向论文投稿、基金本子、组会 PPT。
- 要“期刊级、能直接放进 PPT / 投稿系统”的多面板图，同时保留可编辑 `.pptx`。
- 三件套缺一不可：`.pptx` + 600 dpi `.png` + 字体已嵌入的矢量 `.pdf`。
- 用户会逐区看、逐字改；先给局部确认稿，不要一次性甩整图。

## 2. 审美

- **学术风 = 纯色平涂 + 深色=一级**。三层明度阶梯，一张图里只能有这三档：
  - **一级（深底白字）**：入口 / 机制研究 / 各臂标题 / 总结论条 —— 全图 ≤5 条深色块；
  - **二级（中色底深字）**：研究内容、关键检测、模型、收口（成果）；
  - **三级（浅色底深字）**：干预手段、读数、指标、信号列。
  - 判据：眯眼看，深色块应该自然连成"主干"，浅块退成"枝叶"；若满屏都是同一种浅色，
    就是层级没做出来，必须把主干压深。
- 白底、干净、克制；靠**分区色头 + 细边框 + 留白层级**建立结构，不靠阴影、渐变、3D。
- 深色区头（藏青 / 玫红 / 深蓝）配白字；浅色区（实验设计/采样/取材/结局）用浅底 + 深字。
- 同一张图只用一个主强调色系；6 组饲料用同色系深浅，不铺彩虹色。
- 每个分区必须“填满但不挤”：文字与图、图与图之间留 1–2 mm 呼吸位；
  不允许出现整块无意义的空白带，也不允许文字贴边/压线。
- 图标是辅助，不是主角；同一张图里写实插画与线稿不要混用。
- 所有正文 **黑色加粗**（标题带内白字除外）；不要灰色正文。

## 3. 布局

- 七区参考骨架：
  1 Experimental design；
  2 Longitudinal fecal sampling (metagenomics)；
  3 Parallel sacrifice & multi-tissue sampling；
  4 Outcome；
  5 Multi-omics integration and mGWAS；
  6 Proposed mechanism；
  7 Validation in human cohorts (public databases)。
- 顶部 1–4 横排；中部 5 通栏；底部 6 左 / 7 右；最底一条 summary。
- 保持参考图的列语义，但**优先保字号**：
  - 254 mm 宽放不下时，画布加宽到 300 mm；
  - 仍放不下就合并列（如 P5 的 Validation 并入 Key outputs，P7 的 Translation 并入 Consistency），
    **不要**把正文压到 5 pt 以下。
- 任何“重复标题 / 两套编号 / 图例与标题重叠 / 标签压线”都视为错误。
- 反馈箭头类文字：文字放在箭头三角旁，右端贴近箭头尖但留 1 mm，不压三角、不悬空。
- 箭头不得穿文字；折线一次画完；并列关系不要加箭头。

## 4. 字体与字号

- 中文：**KaiTi（楷体）**。
- 英文/数字：首选 **Times New Roman**；但 PowerPoint COM 导出 PDF 时
  `TimesNewRomanPSMT` / `TimesNewRomanPS-BoldMT` 可能不嵌入，投稿不合格。
  因此**最终 PDF 用 Cambria**（Times 风格衬线，四字重可嵌入）；PPTX 可保留 Times 供编辑，
  但交付前必须确认 PDF 字体全部 embedded。
- 正文 ≥5.5 pt（幻灯片图），印刷图 ≥5.0 pt；分区标题 ≥9 pt；正文级说明 ≥6.0 pt。
- 不使用 Arial、Microsoft YaHei 作为本预设的默认字体（历史版残留，需改）。
- 字号不够时：删字、合并列、加宽画布；**不许 autofit 到 3.8–4.8 pt**。

## 5. 素材与图标

- 用户给的参考图/截图：**优先原样入库**，不要手绘近似；原图放
  `assets/custom/references/`，索引里标 `user-supplied-reference`，仅内部复用。
- 自制示意图放 `assets/custom/figures/`，默认 CC0；文件名用英文 kebab-case。
- SciDraw 素材放 `assets/custom/scidraw/<category>/<slug>.<ext>`（全量 774 件），保留作者、DOI、许可；
  CC BY 4.0 必须署名，CC0 可免署名但仍记录来源。索引 id 为 `scidraw/<category>/<slug>`。
- 小鼠：本课题用 **KM 白小鼠**（正面、白身、粉耳、红眼、长尾），
  id `custom/figures/km-white-mouse`；不要用灰鼠/黑鼠代替。
  例外：1:1 复刻用户给的参考图时按原图配色走（参考图是灰鼠就用
  `bioicons/mouse-darkgray`），并在交付说明里写清“改这一处即可换回 KM 白鼠”。
- 饲料：三粒圆柱形颗粒，上 1 下 2、边对边闭合成三角形；
  id `custom/figures/feed-pellet-triangle`；不要用碗。
- mGWAS：SNP 块（两列彩色竖块 + 虚线配对）在 Manhattan 上方；Manhattan **必须重绘**
  （规范见 §5.1），用户原图 `custom/references/manhattan-plot-reference*` 只作样式校准，
  不得直接贴图。
- 肠壁：4 个上皮细胞 + 微绒毛 + 紧密连接 + 基底膜；
  id `custom/figures/gut-wall-epithelium`。
- 人群：男 / 女 / 儿童三个剪影，不要三个相同女性；
  ids `custom/figures/human-male|human-female|human-child`。
  队列/病例组用 4 人站立组图（含一位裙装，臂腿分开、肩宽>髋宽，缩到 12 mm 仍可读）：
  id `custom/figures/cohort-people-4`。
- 体外细胞实验：带细胞的培养皿（3/4 俯视，盘径:盘高≈2.7:1，皿内 7 个大细胞带同色系描边，
  互不重叠）；id `custom/figures/petri-dish-cells`。线稿版 `044-petri-dish-3` 只在 ≥30 mm 用。
- 宿主基因组：蓝色 DNA 双螺旋；id `custom/figures/dna-double-helix-blue`。
- **立体图三档，先认档再动手**（详见 `skills/tech-route-atlas/references/iso-3d.md`）：
  ① 等距体块场景 → `routekit.iso`（纯多边形、PPT 可改，**首选**）；
  ② 物体级 3D（病毒/细胞/纳米颗粒/分子球棍）→ `routekit.render3d`（plotly+kaleido 离线出图，
  位图，分子必须用真实 PDB/PubChem 坐标，**不许编原子位置**）；
  ③ 只缺"分层"→ 直接用 `sciglyph/05-ecology-biotech/habitats/*` 的剖面块，最省事。
  硬约束：等距图**文字一律水平放体块外**（PPTX 无 shear）；一张图只许一种进深比
  （真等距 0.866/−0.5 或 2:1 的 0.894/−0.447）；禁渐变/投影/天空盒/地面阴影，
  立体感只由三面明度承担（顶 0.86 / 正 0.62 / 侧 0.42）。
- **素材必须清晰：一律纯矢量（SVG 自绘或带许可的矢量件），禁止把参考图截图/抠图塞进去。**
  判定：600 dpi 出图后放大 4 倍，边缘不许有锯齿、白边、原图底色残留。
  参考图只用来"看风格"，要复现就照比例重画；用户原图只进
  `assets/custom/references/` 并在索引标 `user-supplied-reference`，**不进正式图**。
- 禁止 AI 生图；照片级素材从 catalog / SciDraw 找，或明确告知需外部素材。

### 5.1 GWAS Manhattan 图（2026-11 定稿，硬规范）

用户原话：“GWAS 的曼哈顿图一定要是这种哈，**不止是散点**哦。”
判定标准不是“画了一堆点”，而是读者一眼能看出**基因组分段、显著性阈值、哪些峰显著**。
以下 7 条缺一不可：

1. **x 轴 = 染色体累加位置**，不是 BP 原值；每条染色体一段，段内点随机抖动，段间留 0 间隙
   （R: `axisdf$cumulative` 累加做法）。
2. **y 轴 = −log₁₀(P)**，只标 0 / 4 / 8 三档；y 上限比最高峰高 0.4 左右，别把峰顶压到框上。
3. **奇偶染色体交替配色**（R 标准 `rep(c("grey","skyblue"),22)`）。本预设用
   `#3f7099` / `#a8c2d6` 深浅蓝；单色图可用 `#5b6b7a` / `#aebdc9`。
4. **两条阈值线都要有**，缺一条读者无法判断显著性：
   - genome-wide `P = 1e-6` → y = 6 **实线**，深灰 `#3b4a57`，线宽约 0.65 pt；
   - suggestive `P = 1e-4` → y = 4 **虚线**，浅灰 `#9fb0be`；
   - 两线都压在其他点下面（zorder 最低），只穿过点云、不压文字。
5. **峰点高亮**：y ≥ 6 的点改**红** `#c0392b`（主峰），4 ≤ y < 6 的点改**绿** `#2f9e44`
   （次级/提示性峰）；其余点保持染色体色。红绿只用于“显著”，不要拿来做分类色。
6. **x 轴刻度落在每段中心**，标签只写染色体号 `1…22 / X / Y`，轴名 `Chr` 放最左；
   **不要**写 “Chromosome position (Mb)”。
7. **尺寸分档**：面板宽 ≥25 mm 才写染色体刻度；<25 mm 时保留“分色 + 双阈值线 + 红绿峰点”，
   删掉全部刻度文字。宁可无标签，不许出现 3–4 pt 字。

实现与数据：

- **优先直接调用库函数**：`from routekit import miniplot as mp` →
  `cv.plot(box, mp.manhattan(cv.p, nchr=10, n_per_chr=110))`。该函数已把下面 7 条规则
  全部写死（分色 / 双阈值 / 红绿峰 / 刻度 / serif 字体 / 窄面板 `labels=False`），
  并支持 `data={染色体: [p 值]}` 传真实数据。下面的自写版本是**等价参考实现**，
  只在新画布需要特殊比例（例如 3:1 超宽条）时改它。
- 一律 **matplotlib 经 `cv.plot(b, draw, dpi=600)`** 生成（真数据点上千个，用原生形状会撑爆
  pptx）。600 dpi 位图内嵌于矢量图是期刊通行做法；整图 PDF 仍是矢量 + 内嵌点阵插图。
- 字体必须跟图一致：`mpl.rcParams["font.family"]="serif"`、`font.serif=["Cambria"]`，
  刻度 `labelsize=5.0`；字体不一致会被审稿人一眼看出是“贴进来的图”。
- **数据不许编**：有真实 GWAS 就用真实 p 值；没有就生成示意值（指数分布 + 在若干染色体上
  叠加高斯峰把峰顶抬到 6.3–8.0），并在图注写 “schematic”。
- 一处以上复用（mGWAS 框架 + 人群复现列）时，同一个函数不同参数（`nchr / n_per_chr /
  labels`）出两张，保证风格统一。

参考实现（routekit 构建脚本内，已实测 0 error；`INK2` = 调色板 `ink2` 灰 `#455766`）：

```python
def manhattan(b, *, nchr=12, seed=11, yticks=True, xlabels=True,
              pts=150, name="mh", dpi=600):
    import numpy as np

    def draw(fig):
        import matplotlib as mpl
        mpl.rcParams["font.family"] = "serif"
        mpl.rcParams["font.serif"] = ["Cambria"]
        rng = np.random.default_rng(seed)
        ax = fig.add_axes((0.115, 0.17, 0.875, 0.78))
        lo, hi = "#3f7099", "#a8c2d6"          # 奇 / 偶染色体
        peaks = {2, 5, 8}                       # 示意：哪几条染色体上放显著峰
        pos = 0.0
        tick_pos, tick_lab = [], []
        for c in range(nchr):
            n = pts
            x = pos + (np.arange(n) + rng.random(n)) / n * 0.92
            y = rng.exponential(0.62, n)
            if c in peaks:                      # 高斯峰抬到 6.3–8.0
                k = rng.integers(int(n * 0.3), int(n * 0.7))
                bump = np.exp(-((np.arange(n) - k) ** 2) / (2 * (n * 0.022) ** 2))
                y = np.maximum(y, bump * rng.uniform(6.3, 8.0))
            col = np.where(y >= 6.0, "#c0392b",
                           np.where(y >= 4.0, "#2f9e44",
                                    lo if c % 2 == 0 else hi))
            ax.scatter(x, y, s=1.1, color=col, linewidths=0, zorder=2, alpha=0.9)
            tick_pos.append(pos + 0.47)
            tick_lab.append(str(c + 1 if c < 10 else "X" if c == 10 else "Y"))
            pos += 1.0
        ax.axhline(6.0, color="#3b4a57", lw=0.65, zorder=1)
        ax.axhline(4.0, color="#9fb0be", lw=0.55, ls=(0, (2.2, 1.8)), zorder=1)
        ax.set_xlim(0, nchr)
        ax.set_ylim(0, 8.4)
        ax.set_yticks([0, 4, 8] if yticks else [])
        if xlabels:
            ax.set_xticks(tick_pos)
            ax.set_xticklabels(tick_lab)
        else:
            ax.set_xticks([])
        ax.tick_params(labelsize=5.0, colors=INK2, width=0.5, length=1.6, pad=1.0)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color("#9aa7b2")
            ax.spines[s].set_linewidth(0.55)

    cv.plot(b, draw, dpi=dpi, name=name)
```

用法（同一张图里两处）——**首选库函数**：

```python
cv.plot(Box(xa, y, 26, 18.6), mp.manhattan(cv.p, nchr=10, n_per_chr=110))       # 有刻度
cv.plot(Box(x7, y, 23, 15.4),
        mp.manhattan(cv.p, nchr=10, n_per_chr=70, labels=False))               # 无刻度

# 有真实数据时（p 值，非 −log10）：
cv.plot(Box(xa, y, 26, 18.6), mp.manhattan(cv.p, nchr=19, data={1: p1, 2: p2, ...}))
```

自写版本（仅在需要非标比例时改写）：见上方参考实现代码块（`b` 为 `Box`，
`INK2` = 调色板 `ink2` `#455766`）。

反面清单（见到就判错）：只有一色散点、没有阈值线、阈值只有一条、x 轴写 Mb 坐标、
峰点不高亮、刻度用 3 pt、把用户截图直接贴进图里、图和正文的字体不是同一套。

## 6. 交付与自检

- 先写 4 行规格：画布、分区、每区一句话、箭头拓扑表；没有拓扑表不写代码。
- 逐区确认：P1+2 → P3+4 → P5 → P6+7 → 拼版；每区单独 300 dpi 预览给用户看。
- 每轮交付前：
  - `static_report(mode="deck")` **0 error / 0 warning**；
  - COM `com_audit` 无越界；
  - PNG 600 dpi；PDF 单页、字体全部 embedded；
  - 目标目录只留结果图，脚本/预览/临时目录删除。
- 不要把“过程稿/半成品”说成最终稿；不合格就明说哪里不合格。

## 7. 交互

- 中文为主，先给结论，再给“改了什么、为什么”。
- 不倒过程日志；不重复问已经确认过的偏好。
- 只有遇到“字号/列数/画布”这类硬冲突时才让用户二选一，并给推荐项。
- 用户说“继续”时直接推进，不要停在解释上。

## 8. 预设落地

- 本文件随 `dsh-preset-tech-route` 仓库分发；新会话选择「科研技术路线绘制模式」后应首先读取。
- 仓库：`https://github.com/lxwang98/dsh-preset-tech-route`。
- 修改预设后：`git add/commit/push` → 在插件管理器重装/重载本地 bundle → 重启 Harness；
  当前会话不会热加载。
- 素材索引由 `tools/build_index.py` 重建；新增 custom/SciDraw 后必须重建并检查 `static_report`。

## 9. 国自然（NSFC）技术路线图（2026-11 定稿，硬规范）

**触发**：用户说"技术路线图""国自然 / 基金本子 / 标书 画图""研究方案总览"。走 `nsfc-route` 技能，
不要直接套 `tech-route-atlas` 的横向期刊版式。

### 9.1 六条硬规则

1. **A4 竖版、单页、绝不跨页**：`CANVAS.nsfc_a4`（210×297，边距 12）。只在正文本来就横排时才用
   `nsfc_a4_landscape`。放不下就砍模块，不许缩字号。
2. **中文黑体**：`Canvas(..., cjk_font="SimHei")`。国自然不用 KaiTi / 宋体；SimHei 的伪粗体实测
   比 regular 多 26.6% 墨量，`bold=True` 可放心用。
3. **字号地板 8.0 pt**（实印、按正文插图宽度 160 mm 换算）。阶梯：标题 18–20 / 副标题 9.6 /
   分区 10 / 模块 13 / 小标题 9 / 正文 9.2 / 最小 8.2。`static_report` 用 `mode="print"`，
   但看到 `small-text` 一律按 error 处理。
4. **模块三要素**：每张研究内容卡必须有「研究目标（≤30 字）+ 关键技术（≤3 条具体手段）+
   可验证产出（≤2 条）」。缺"产出"栏 = 评审直接扣分。
5. **2 主色深浅三级 + 1 强调色**（示范 `#1b3a63 / #2e6e9e / #5a8fbf` + 创新点 `#b87333`）。
   禁渐变 / 阴影 / 3D；交付前必须过灰度测试（`Image.open(png).convert("L")` 后层级仍可分）。
6. **构型不许自创**：面上/青年默认"三段式（问题—内容—成果）"；时间轴式/甘特图在正文里禁用
   （与"研究计划"重复）；青年别用层进漏斗。五种构型见 `skills/nsfc-route/references/archetypes.md`。

### 9.2 与期刊图的差异（别混用）

| 维度 | 期刊技术路线图 | 国自然技术路线图 |
|---|---|---|
| 读者任务 | 发现了什么 | **该不该资助** |
| 版式 | 254×142.9 / 300×189.5 横版 | **A4 竖版 210×297** |
| 字体 | Times / Cambria | **SimHei** |
| 图元 | 30–60 个插画 | 0–6 个，文字卡为主 |
| 内容边界 | 只画已发表机制 | 可画未完成计划 + 风险预案 |
| 字号地板 | 5.0–5.5 pt | **8.0 pt** |
| 颜色 | 4–6 分区色 | 2 主色 + 1 强调色 |

### 9.3 交付

三件套同上（pptx + 600 dpi PNG + 矢量 PDF），另附**灰度版**自看；图注写清"模块 → 产出"对应关系。
范例：`skills/nsfc-route/examples/build_nsfc_a4.py` + `nsfc-a4-demo.png`（菌群–丁酸–GPR43–屏障衰老）。

