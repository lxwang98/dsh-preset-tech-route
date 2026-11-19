---
name: sciglyph-catalog
description: 检索、预览、挑选素材——本机 3726 个矢量图元（SciGlyph 12 大类 + Bioicons 精选 + SciDraw 774 + 自制/参考 22），外加 2829 个联网取用的 Bioicons 全库（Servier Medical Art 1374 件、DBCLS 634 件，彩色写实插画）；按中英文关键词搜索、生成缩略图对照表、判断 format/series/尺寸适配与许可证。
whenToUse: 需要给路线图挑图标（细胞、菌群、脏器、小鼠、仪器、玻璃器皿、箭头、图表），或本机素材画风不够像 BioRender 时，改从远程库按需下载。
---

# 素材目录：本机 3726 + 联网 2829

两套索引，一个取用接口：

| 索引 | 规模 | 位置 | 取用 |
|---|---|---|---|
| 本机 | 3726 | `assets\index.json`，文件在 `assets\sciglyph\…`、`assets\bioicons\…`、`assets\custom\…` | 拷入即用，离线可用 |
| 远程 | 2829 | `assets\remote\index.json`（仅元数据 1.4 MB） | 首次使用时下载到 `assets\.remote\`，之后走缓存 |

远程库 = Bioicons 全库（`duerrsimon/bioicons`，上游 428 MB），其中 **Servier Medical Art 1374 件**
（CC BY 3.0）与 **DBCLS / Togo picture gallery 634 件**（CC BY 4.0）是彩色写实插画，
最接近 BioRender 的观感；SciGlyph 是线稿/扁平图元，两者不要混用在同一张图里。

本机 `custom/` 另含 22 个自制/参考图与 **SciDraw 774 件**（`scidraw/<category>/<slug>`，
CC BY 4.0 632 / CC0 142，逐条作者、DOI、许可在 `assets/custom/scidraw/metadata.json`）。
SciDraw 分类：other 247、cell 187、mouse 114、human 65、rat 59、fish 36、drosophila 35、bird 31。

## 一条命令挑素材

```powershell
cd D:\dsh-bundles\tech-route\skills\tech-route-atlas\scripts
python -m routekit.icons search "肠道菌群" -k 8 --sheet out\sheet-gut.png
python -m routekit.icons stats

# 远程库：先搜（不需要联网），再按需下载
python -m routekit.remote search "心脏" -k 7 --sheet out\cardiac.png
python -m routekit.remote search "colon" -c servier
python -m routekit.remote fetch bioicons/servier/Human_physiology/colon
python -m routekit.remote sync          # 只在想刷新目录时跑（要联网）
```

`--sheet` 会生成带 id 标签的缩略图网格（6 列 × 220 px），**先看图再定 id**；
名字像不代表画得像（"040-tube-centrifuge" 是线稿，"microtube-closed-blue" 才是彩色插画）。

Python 里等价写法：

```python
from routekit.icons import catalog, contact_sheet
from routekit import remote

c = catalog()
hits = c.search("结肠", k=6)                   # 本机：中文、英文、类别、系列过滤
contact_sheet(hits, "out/sheet.png", cols=6, cell_px=220)

remote.search("结肠", k=6)                      # 远程：同样支持中文
remote.sheet(remote.search("mouse", k=8), "out/sheet-mouse.png")
```

`remote.get(id)` 找记录，`remote.fetch(rec)` 下载原始 SVG 并写同目录 `.license.txt`；
日常直接写 id 即可，`Canvas.icon(box, "bioicons/servier/Human_physiology/colon")`
会在第一次用到时自动下载——本机找不到的 id 会自动转去远程库。

## 12 大类（SciGlyph，CC BY 4.0）

| 目录 | 数量 | 典型内容 | 路线图用法 |
|---|---|---|---|
| 01-cells-microbes | 295 | 细胞器、细菌形态、病毒、生物膜、细胞连接 | 机制图里的菌/细胞、屏障结构 |
| 02-genetics-omics | 233 | DNA/染色体、测序、CRISPR、群体遗传、系统发育 | 组学模态、基因位点、进化树 |
| 03-metabolism-phenotype | 105 | 代谢通路、发酵产物、表型测量、剂量反应 | SCFA/代谢物、表型轴 |
| 04-phylogeny-evolution | 201 | 树骨架、分支、时间轴、网络 | 进化/聚类/溯源 |
| 05-ecology-biotech | 121 | 生境（肠道、肺、土壤）、互作、发酵罐 | 肠道菌群、宿主-菌互作 |
| 06-lab-methods | 140 | 分析流程、电泳、培养、成像流程 | 方法流程、QC 步骤 |
| 07-glassware-consumables | 244 | 试管、离心管、培养皿、孔板、移液器、载玻片 | 采样/取材/反应体系 |
| 08-instruments-apparatus | 440 | 显微镜、离心机、测序仪、色谱、质谱、切片机 | 检测平台、仪器图标 |
| 09-safety-signage | 191 | 生物安全、警示、防护 | 动物伦理/生物安全标注 |
| 10-figure-elements | 325 | 箭头、括号、标签、图例构件、比例尺 | 图内构件（优先用 canvas 原生形状） |
| 11-diagrams-charts | 437 | 柱线散点、流程图语法、UML、电路、PID | 小图占位（正式数据图用 miniplot） |
| 12-icons-ui | 98 | 通用 UI 图标（时钟、文件、人员） | 时间/文档/人群等辅助符号 |

另有 Bioicons 精选 13 类 100 个（CC0 / CC BY 3.0）：`Animals`（小鼠 11 种体态、大鼠）、
`Human_physiology`（结肠、小肠、胃、肝、心、肾、脾、肺、脑、绒毛）、`Plants_Algae`（水稻、小麦、燕麦、面包）、
`People-Other`（男/女/老人/患者/儿童）、`Lab_apparatus`（显微镜、离心机、测序仪、流式、孔板、培养皿、
培养瓶、移液器、注射器、冻存管、离心管、色谱仪）、`Microbiology`（细菌、菌体内结构）、`General_items`（箭头等）。

## 三种 format，选错就毁图

| format | 视觉 | 适合尺寸 | 说明 |
|---|---|---|---|
| `illustration` | 彩色扁平插画（有填充色） | **≥8 mm** | 路线图主图元，BioRender 味 |
| `diagram` | 示意图/流程/图表，线+少量填充 | 10–60 mm | 矩阵、流程、图表占位 |
| `icon` | 粗黑线稿（stroke 2–3 px） | ≤6 mm | 放大像钢笔尖，**不要**当主图 |

五套 series（classic / atlas / icon24 / primitives / labflow）画风略有差异，
同一张图里**只用一种 series**（推荐 `atlas` 或 `classic`）；混用会显得拼凑。

## 取用与着色

```python
cv.icon(box, "bioicons/mouse-gray", pad=0.5)              # 等比内接，留白 pad mm
cv.icon(box, tube_id, tint_colour=p.zone_line(2))          # 单色化（线稿/纯色件有效）
cv.icon(box, colon_id, px=1400)                            # 大图提高栅格精度
```
- 彩色插画**不要** tint（会把整幅图压成一色），只在灰度/单色图版里用。
- 同一 zone 内图标视觉重量要接近；小鼠别和显微镜一样大（按真实比例感缩放）。
- 图标四周留 ≥0.4 mm 空白，别贴卡片边。

## 许可与署名（必须记账）

- SciGlyph 素材：**CC BY 4.0**，署名 `ZengZichao, https://github.com/ZengZichao`（AI 生成，
  投稿前需人工核对形态准确性）。
- Bioicons：逐文件不同（CC0 / CC BY 3.0 / CC BY 4.0 / MIT），
  管线优先取 CC0，其次 MIT，再次 CC BY；每个文件的 license 记在 `assets/bioicons/manifest.json`。
- 交付时在 `ATTRIBUTION.md` 写：用到的 id、原名、许可、来源链接；图注里写
  "Icons: SciGlyph (CC BY 4.0) / Bioicons (CC BY 3.0)"。
- 商用/投稿前若期刊要求"无第三方图元"，改用 `10-figure-elements` 的基本构件自绘。

## 缺口（别在这上面浪费时间）

- SciGlyph **没有**小鼠/人体的卡通插画 → 一律走 `bioicons/`（Mouse、Human_male 等）。
- 没有照片级组织切片、没有真实显微图 → 需要时让用户提供，或只用示意图形。
- 没有期刊 logo、没有具体仪器品牌外形 → 用通用仪器图标。
- 需要新素材时：先在 `11-diagrams-charts`、`10-figure-elements` 找可组合构件，
  再考虑用 `Canvas.rect/arrow` 自绘；**不要**去网上抓未授权图片。




