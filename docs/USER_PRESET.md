# 用户审美 / 布局 / 字体预设（可复用）

本文件是从 2026-11 与用户的真实改图会话中提炼的硬约束。新会话先读本文件，再读
`skills/tech-route-atlas` 的 references。**不要再用默认 Arial + Microsoft YaHei**。

## 1. 用户与交付目标

- 中文科研工作者，面向论文投稿、基金本子、组会 PPT。
- 要“期刊级、能直接放进 PPT / 投稿系统”的多面板图，同时保留可编辑 `.pptx`。
- 三件套缺一不可：`.pptx` + 600 dpi `.png` + 字体已嵌入的矢量 `.pdf`。
- 用户会逐区看、逐字改；先给局部确认稿，不要一次性甩整图。

## 2. 审美

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
- 饲料：三粒圆柱形颗粒，上 1 下 2、边对边闭合成三角形；
  id `custom/figures/feed-pellet-triangle`；不要用碗。
- mGWAS：SNP 块（彩色竖块 + 虚线连接）在 Manhattan 上方；Manhattan 用用户原图
  `custom/references/manhattan-plot-reference`，不要重画。
- 肠壁：4 个上皮细胞 + 微绒毛 + 紧密连接 + 基底膜；
  id `custom/figures/gut-wall-epithelium`。
- 人群：男 / 女 / 儿童三个剪影，不要三个相同女性；
  ids `custom/figures/human-male|human-female|human-child`。
- 宿主基因组：蓝色 DNA 双螺旋；id `custom/figures/dna-double-helix-blue`。
- 禁止 AI 生图；照片级素材从 catalog / SciDraw 找，或明确告知需外部素材。

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
