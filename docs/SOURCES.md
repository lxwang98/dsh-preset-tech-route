# 来源与许可（SOURCES）

本预设的绘图库（routekit）为自研代码；素材全部来自开源项目，逐项记录如下。

## 1. SciGlyph — 2830 个科研矢量图元

- 仓库：https://github.com/ZengZichao/SciGlyph
- 版本：克隆自 `main`（2026-11），仓库内 `NOTICE` / `CITATION.cff` 一并保留在 `assets/sciglyph/`。
- 素材许可：**CC BY 4.0**（署名 `ZengZichao, https://github.com/ZengZichao`）；
  代码与工具：MIT。
- 内容：12 个学科大类（细胞微生物、遗传组学、代谢表型、系统演化、生态生物技术、实验方法、
  玻璃器皿、仪器装置、安全标识、图元构件、图表、图标），五种画风系列
  （classic / atlas / icon24 / primitives / labflow），三种格式
  （illustration / diagram / icon）。
- 说明：素材为 AI 生成并经仓库 QA 脚本检查；形态学准确性需在投稿前人工核对
  （已在 `sciglyph-catalog` 技能中写明）。
- 本预设改动：只做目录复制与索引（未修改 SVG 内容）；`assets/index.json` 由
  `tools/build_index.py` 从各子目录 `manifest.json` 生成。

## 2. Bioicons — 精选 100 个插画 + 远程全库 2829 件

- 仓库：https://github.com/duerrsimon/bioicons（站点 https://bioicons.com）
- 本机精选：`tools/fetch_bioicons.py` 通过 GitHub API 树 + raw 链接按"家族"抓取，
  单文件上限 520 KB，优先级 CC0 > MIT > CC BY 4.0 > CC BY 3.0 > CC BY-SA；
  逐文件许可记录在 `assets/bioicons/manifest.json`。
- 远程全库：`routekit.remote` 以 raw.githubusercontent.com 按需下载（默认缓存到
  `assets/.remote/`），目录在 `assets/remote/index.json`（只存元数据，1.4 MB）。
  上游共 428 MB / 2829 件，本仓库不分发这些 SVG 本体。
- 两个最接近 BioRender 观感的集合：
  **Servier Medical Art**（1374 件，**CC BY 3.0**，https://smart.servier.com/）与
  **DBCLS / Togo picture gallery**（634 件，**CC BY 4.0**，https://dbcls.rois.ac.jp/）；
  其余为各作者 CC0 / CC BY / MIT / BSD 素材，以记录内 `attribution` 为准。
- 许可分布（远程库）：CC BY 3.0 1019、CC BY 4.0 869、CC0 487、MIT 37、CC BY-SA 4.0 31、
  CC BY-SA 3.0 4、BSD 3。
- 本预设改动：仅复制/下载 SVG 与元数据，未修改图形；下载时在缓存目录写同名 `.license.txt`。

## 2b. SciDraw — 774 个科学插画

- 站点：https://scidraw.io；API：`/api/v1/drawings/`。
- 本机全量：`assets/custom/scidraw/<category>/<slug>.<ext>`，774 个文件；
  逐条元数据在 `assets/custom/scidraw/metadata.json`（作者、DOI、许可、原始 URL、分类、下载量）。
- 许可：CC BY 4.0 632 件、CC0 142 件；CC BY 必须署名，CC0 也保留来源。
- 分类：other 247、cell 187、mouse 114、human 65、rat 59、fish 36、drosophila 35、bird 31。
- 本预设改动：仅下载/复制，未修改图形；索引由 `tools/build_index.py` 的 `scidraw()` 生成，
  署名写入每条记录的 `attribution`。

## 3. 方法论参考（未复制代码）

| 项目 | 借鉴点 |
|---|---|
| https://github.com/LY2260789/routegraph-skill | 箭头拓扑表先行；一条逻辑箭头=一个形状；虚线必须单形状；层级顺序；字号取整 |
| https://github.com/Stephen-studying/tech-route-maker | 技术路线 JSON 规格（nodes/edges/stages）与证据锚定思路 |
| https://github.com/OpenDCAI/Paper2Any | "论文 → 可编辑图"的产品形态（仅作参考，未内嵌） |
| https://github.com/BinSpa/awesome-scientific-figures | 生态索引（CC0），用于穷举候选工具 |

## 4. 第三方运行依赖（本机已装，不随包分发）

python-pptx（MIT）、matplotlib（PSF-like）、Pillow（HPND）、PyMuPDF（AGPL-3.0，仅本机使用）、
svglib / reportlab（BSD）、pywin32（PSF）、Microsoft PowerPoint（商业软件，仅作渲染器）。

## 5. 许可证汇总

| 资产 | 数量 | 许可 |
|---|---|---|
| SciGlyph SVG | 2830 | CC BY 4.0 |
| Bioicons SVG | 100 | CC0 / CC BY 3.0 / CC BY 4.0 / MIT（逐文件） |
| SciDraw 插画 | 774 | CC BY 4.0（632）/ CC0（142），逐文件 |
| routekit 代码 | — | 随预设自由使用 |
| 技能文档 | — | 随预设自由使用 |

对外交付图件时，若使用了 SciGlyph、Bioicons 或 SciDraw 素材，需在图注或致谢中署名，
并随交付附 `ATTRIBUTION.md` 片段（模板见 `docs/ATTRIBUTION.md`）。
