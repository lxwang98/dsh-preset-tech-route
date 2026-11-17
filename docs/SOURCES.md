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

## 2. Bioicons — 精选 100 个插画

- 仓库：https://github.com/duerrsimon/bioicons（站点 https://bioicons.com）
- 取用方式：`tools/fetch_bioicons.py` 通过 GitHub API 树 + raw 链接按"家族"抓取，
  单文件上限 520 KB，优先级 CC0 > MIT > CC BY 4.0 > CC BY 3.0 > CC BY-SA。
- 逐文件许可记录在 `assets/bioicons/manifest.json`（字段 license / license_uri / attribution）。
- 主要来源作者：Servier Medical Art（CC BY 3.0）、Ben Murrell（CC0，Mouse 系列）、
  DBCLS / Togo picture gallery（CC BY 4.0）等，均以 manifest 内 attribution 为准。
- 本预设改动：仅复制 SVG 与元数据，未修改图形。

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
| routekit 代码 | — | 随预设自由使用 |
| 技能文档 | — | 随预设自由使用 |

对外交付图件时，若使用了 SciGlyph 或 Bioicons 素材，需在图注或致谢中署名，
并随交付附 `ATTRIBUTION.md` 片段（模板见 `docs/ATTRIBUTION.md`）。
