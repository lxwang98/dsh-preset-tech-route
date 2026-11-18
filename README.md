# 科研技术路线绘制模式（tech-route）

一个 DeepSeek Harness Agent 预设：把论文的研究设计、实验流程、多组学整合、机制假说、人群验证
画成**期刊级多面板技术路线图 / 图形摘要**，输出可编辑 `.pptx` + 600 dpi `.png` + 矢量 `.pdf`。

```
tech-route/
├─ cordis.patch.yml          # 预设组合（persona + 4 个技能 + 完整标准能力）
├─ package.json              # @local/dsh-preset-tech-route
├─ assets/
│  ├─ sciglyph/              # 2830 个矢量图元（CC BY 4.0，12 大类 5 种画风）
│  ├─ bioicons/              # 100 个精选插画（CC0 / CC BY，离线可用）
│  ├─ custom/                # 11 个自制/参考素材 + SciDraw 774 个插画
│  ├─ index.json             # 3715 条本机素材索引（中英名、标签、风格、许可、署名）
│  ├─ glossary.json          # 中英术语，供中文检索用
│  └─ remote/index.json      # 2829 条远程素材目录（元数据 1.4 MB，按需下载）
├─ tools/
│  ├─ build_index.py         # 重建本机索引（sciglyph + bioicons + custom + scidraw）
│  ├─ fetch_bioicons.py      # 拉取精选 Bioicons 子集
│  └─ fetch_scidraw.py       # 从 scidraw.io 公共 API 全量抓取 774 件
├─ skills/
│  ├─ tech-route-atlas/      # 核心方法 + routekit 库 + 示例（含 7 分区示范图）
│  │  ├─ references/api.md       # 全部 API 签名
│  │  ├─ references/patterns.md  # 12 种版式骨架（真实坐标）
│  │  ├─ references/arrows.md    # 箭头拓扑与走位规则
│  │  ├─ references/remote.md    # 远程素材库（Servier / DBCLS）用法与许可
│  │  └─ examples/               # build_demo.py + pptx/png/pdf 成品
│  ├─ sciglyph-catalog/      # 素材检索/预览/许可与格式规则（本机 + 远程）
│  ├─ route-visual-qa/       # 渲染、审计、10 点人工复查
│  └─ journal-route-spec/    # 期刊画布/字号/配色/图注规范与双输出
├─ docs/SOURCES.md           # 素材来源与许可
├─ docs/ATTRIBUTION.md       # 可直接抄的署名片段
└─ docs/USER_PRESET.md       # 用户审美 / 七区布局 / 字体与交付硬约束
```

## 素材：本机 3715 + 联网 2829

本机 3715 件开箱即用（离线）：SciGlyph 2830、Bioicons 精选 100、SciDraw 774、自制/参考 11。
SciDraw 来自 <https://scidraw.io>（CC BY 4.0 / CC0，逐条保留作者、DOI 与许可）。要 BioRender 那种彩色写实插画，用**远程库**——
Bioicons 全库 2829 件，其中 **Servier Medical Art 1374 件**（CC BY 3.0）与
**DBCLS 634 件**（CC BY 4.0）是人工绘制的彩色插画，脏器、小鼠、菌群、仪器都有。
仓库只带 1.4 MB 目录，图上用到哪张才下载哪张（缓存到 `assets/.remote/`，附许可文件）：

```powershell
python -m routekit.remote search "心脏" -k 8 --sheet out\cardiac.png
python -m routekit.remote search "colon" -c servier
python -m routekit.remote fetch bioicons/servier/Human_physiology/colon
```

写代码时直接写 id，`cv.icon(box, "bioicons/servier/Animals/mouse-gray")` 首次使用自动下载。

## 快速上手

```powershell
cd <本预设>\skills\tech-route-atlas\scripts
$env:PYTHONIOENCODING = 'utf-8'
python build_demo.py D:\out            # 生成示范图 pptx/png/pdf 并打印审计
python -m routekit.icons search "肠道菌群" -k 8 --sheet out\sheet.png
```

在自己的脚本里：

```python
from routekit import Canvas, Box, P, T, CANVAS, P as palette
from routekit import miniplot as mp
from routekit.audit import static_report, format_report

cv = Canvas(*CANVAS.slide_16x9, palette="cell",
            font="Cambria", cjk_font="KaiTi", title="研究技术路线")
c = cv.zone(Box(4, 20, 120, 60), "1 实验设计 Study design", acc=0)
cv.text(Box(c.x, c.y, c.w, 6), "全谷物黑米 × 4 组 × 33 月龄", size=T.small, bold=True)
cv.icon(Box(c.x, c.y + 8, 18, 18), "bioicons/Mouse")
cv.save("D:/out/route.pptx")
cv.export("D:/out", dpi=600)          # → route.png / route.pdf
print(format_report(static_report(cv, mode="deck")))
```

![示范图：全谷物黑米经肠道菌群–SCFA–炎症轴延长小鼠健康寿命](skills/tech-route-atlas/examples/black-rice-route.png)

## 安装到 DeepSeek Harness

```powershell
git clone https://github.com/lxwang98/dsh-preset-tech-route.git D:\dsh-bundles\tech-route
```

然后在 DeepSeek Harness 里二选一：

1. **插件管理器**（图形界面）：安装本地 bundle，目录选克隆下来的 `tech-route`；
2. **手动注册**（等价操作）：在 profile 的 `package.json` 里加

   ```json
   "dependencies": { "@local/dsh-preset-tech-route": "link:D:/dsh-bundles/tech-route" }
   ```

   并把 `"@local/dsh-preset-tech-route"` 加进 `dsh.profile.bundles` 数组，然后 `pnpm install` 并重启 Harness。

装好后新建对话，在预设选择器里选 **「科研技术路线绘制模式」**。

> 包名带 `@local/` 前缀只是本机约定。改成自己的 scope（如 `@lxwang98/dsh-preset-tech-route`）时，
> 要同步改 `package.json`、profile 依赖、`dsh.profile.bundles` 三处，以及 `cordis.patch.yml`
> 里 `customSkillDirs` 那行解析 `@local/dsh-preset-tech-route/package.json` 的写法。

## 依赖

python-pptx、matplotlib、Pillow、PyMuPDF、svglib+reportlab、pywin32，以及本机安装的
Microsoft PowerPoint（仅作渲染/导出/审计引擎，无需人工打开）。

## 许可

- 代码与技能文档：随本预设自由使用。
- SciGlyph：CC BY 4.0（署名 ZengZichao）；Bioicons：逐文件 CC0 / CC BY 3.0 / CC BY 4.0；
  SciDraw：逐文件 CC BY 4.0 / CC0，保留作者、DOI 与来源。
- 对外交付图件请附 `docs/ATTRIBUTION.md` 中的署名片段。详见 `docs/SOURCES.md`。
