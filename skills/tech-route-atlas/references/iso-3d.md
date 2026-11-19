# 立体（3D / 等距）图：能做到什么、怎么画

> 结论先行：本机**没有** Blender / OpenGL / 3D 渲染器，也**不应**引入——期刊与标书要的是
> 可编辑、可缩放、风格统一的矢量图。我们能稳定交付的"立体"只有一层：**等距投影 + 纯色三面明度**。
> 这一层已经覆盖 BioRender / Nature 系"3D 概念图"里 80% 的用法（剖面、田块、装置、分层）。

## 一、三档"立体"，先认清楚你在要哪一档

| 档位 | 形态 | 我们的能力 | 典型用途 |
|---|---|---|---|
| **A. 等距体块场景** | 45°/30° 轴测，体块组合成地形、装置、剖面 | 原生支持，`routekit.iso`，纯矢量可编辑 | 土壤-作物-地下水、实验平台示意、空间布局、工艺流程 |
| **B. 物体级 3D** | 单个器官 / 蛋白 / 细胞 / 病毒的三维渲染 | 只能取现成素材（`bioicons/liver-3d`、`scidraw/other/coronavirus-3d` 等）或外部渲染件 | 解剖图、分子结构、病原体 |
| **C. 2.5D 剖面块** | 正投影剖面（像切开的鱼缸），无透视 | 已有素材：`sciglyph/05-ecology-biotech/habitats/*` | 水体分层、土壤层、屏障结构 |

**判断口径**：需要"空间关系可读"（谁在谁上面、水往哪流）→ A；需要"这个器官长什么样"→ B；
只需要"分层"→ C，最省事也最不容易翻车。

## 二、等距的几何（照抄即可）

真等距（isometric）：

```
进深轴单位向量 = (cos30°, −sin30°) = (0.866, −0.500)      # 屏幕坐标，y 向下
高度轴         = (0, −1)
```

2:1 俯视（dimetric，游戏与流程图常用，更矮更稳）：

```
进深轴 = (2, −1)/√5 = (0.894, −0.447)
```

**同一张图只许用一种**。混用会让两个体块的地平线对不上，一眼假。

一个长方体 = 3 个可见面（顶 / 正 / 侧）+ 1 个被挡住的背面。给定前下左角 `(x, y)`、
宽 `w`、进深 `d`、高 `h`：

```
P0 = (x, y)                      前下左
P1 = (x + w, y)                  前下右
P2 = P1 + 进深向量                后下右
P3 = P0 + 进深向量                后下左
Up = (0, −h)

顶面 = P0+Up, P1+Up, P2+Up, P3+Up
正面 = P0, P1, P1+Up, P0+Up
侧面 = P1, P2, P2+Up, P1+Up
```

## 三、明度约定（这一条决定"像不像 3D"）

光源固定在**左上**，三面同色系、只改明度：

```
顶面 = tint(acc, 0.86)     # 最亮，受光
正面 = tint(acc, 0.62)     # 中间
侧面 = tint(acc, 0.42)     # 最暗，背光
描边 = shade(acc, 0.62)，lw = 0.35
```

**禁**：渐变、投影、环境光遮蔽、贴图、半透明叠加。预设层面这些都是禁的，等距图上尤其刺眼。
"立体感"由三面明度差承担，不靠特效。

堆叠剖面（`iso_layers`）只画最顶层的顶面；中间层若也画顶面，整摞会像"被切片炸开"。

## 四、文字只能水平放（硬约束）

等距平面里的文字要 shear（斜切变形），PowerPoint 只支持旋转、**不支持 shear**。
所以：

1. 标签一律水平，放在体块外侧；
2. 用 0.5 pt 引线（`cv.arrow(..., head=None)` 或直线）指到目标面；
3. 引线不许穿过其它体块或文字；
4. 一个体块最多挂 1 条标签；要标 3 个部位就拆成 3 个编号 + 图下注释。

## 五、什么时候**不要**用等距

- 纯机制图 / 组学流程 / 技术路线：等距会把"逻辑主干"稀释成"场景插画"，评审读不到主线。
- 页面已被 9 分区塞满：等距至少要独占 1/3 幅面才能读，塞在角落里只会脏。
- 需要精确数值比较：等距面积会被透视压缩，不该拿来编码数据。

## 六、代码

```python
from routekit import Canvas, Box, iso
from routekit.palette import P, tint, shade

cv = Canvas(150, 62, palette="cell")
WATER, SOIL1, SOIL2, ROCK = "#2e6e9e", "#bfae7c", "#a08f62", "#8a8477"

# 土壤剖面 + 地下水
iso.iso_layers(cv, 10, 50, w=40, d=24,
               layers=[(8, ROCK), (9, SOIL2), (7, SOIL1)])
iso.iso_plane(cv, 10, 26, w=40, d=24,
              fill=tint(WATER, 0.72), line=shade(WATER, 0.40))

# 地表田块（2:1 更矮）
iso.iso_plane(cv, 72, 34, w=26, d=14, k=0.5, fill=tint("#7d9c5c", 0.62))
iso.iso_block(cv, 118, 44, w=13, d=9, h=11, acc="#6c5aa0")
```

产物仍是 PPTX 自由形状：在 PowerPoint 里可以直接拖点改形状、改填充。示例图见
`examples/iso-demo.png`。

## 七、外部素材与许可（2026-11 调研结论：不整包引入）

**结论：没有可整包下载的 CC0/CC BY「等距科学 SVG 库」。** 实测：
Wikimedia Commons 的 `Category:Isometric_illustrations` 是空的（API 返回 0）；SVG Repo 的
isometric 只有约 20 个通用立方体，且其许可禁止再分发；BioRender / KEGG / NIH 3D 许可不干净
（NC、付费、逐件自选）。所以等距**场景**只能"造"，而不是"下载"——这正是 `routekit.iso` 存在的理由。

被评估过、但**决定不引入**的主要来源（留档，免得以后再调研一遍）：

| 来源 | 许可 | 为什么不用 |
|---|---|---|
| game-icons/icons（4239 SVG, 6.7 MB） | CC BY 3.0 | 线稿偏游戏风，与现有平涂插画混排会花；且 4239 件会稀释检索质量 |
| Reactome Icon Library（~2500 SVG） | CC BY 4.0（官网与仓库 LICENSE 打架：Apache-2.0 vs CC BY 4.0） | 图标质量最高、最接近 BioRender，但整包 ~70 MB；按需取单个更划算 |
| Kenney isometric / 3D kits | CC0 | 卡通低多边形，需重新配色才能进期刊图；zip 在捐赠弹窗后不可脚本化 |
| RCSB PDB | CC0 1.0 | 分子几何权威，但需要渲染器；**若要做分子图，从这里取坐标喂 `render3d`** |
| Poly Haven | CC0 | 照片级道具，无科学内容；ToS 禁抓站（只许走公开 API） |
| Sketchfab / Smithsonian / publicdomainvectors | 逐模型 / 403 | 要登录或对脚本 403，不可自动化，标注不可靠 |

要点：**素材库的短板不是"少"，而是"风格会散"**。每套外部 3D 素材的光源、色温、线宽都不同，
拼在一页反而脏。稳的做法是 `iso` 提供骨架 + 现有统一风格的平面图元"立"在体块上——
BioRender 的 3D 场景也是这么做的（底块 + 图标，不是全套 3D 模型）。

确需外部素材时才按 `docs/USER_PRESET.md` §5 记账：只收 CC0 / CC BY，逐条记名称、URL、许可、作者；
NC / ND / "仅限个人使用"一律不收。

## 七之二、模式与遮挡（`mode=` 与 `iso_scene`）

```python
iso.iso_block(cv, x, y, w=.., d=.., h=.., acc=.., mode="oblique")  # 默认：正面是矩形（斜投影）
iso.iso_block(cv, x, y, w=.., d=.., h=.., acc=.., mode="iso")      # 真等距：三面都是平行四边形
iso.iso_scene(cv, [dict(kind="block", x=.., y=.., w=.., d=.., h=.., acc=..), ...], mode="iso")
```

- `oblique`：宽沿屏幕水平、进深沿右上 30°。适合**剖面**（土壤/含水层/屏障），读者正对切面。
- `iso`：宽沿右上 30°、进深沿左上 30°，`(x, y)` 是**近角**。适合**场景**（地形、厂区、多体块）。
- 多体块互相遮挡时**必须**用 `iso_scene`（内部按 `iso_depth` 由远到近排序）；PPTX 没有 z-buffer，
  画序错了就是"近的被远的盖住"。
- 明度档 `levels=(顶, 左, 右)` 默认 `(0.78, 0.56, 0.38)`（`tint` 语义：0=原色，1=白）。
  再配 0.35 pt 描边 `shade(acc, 0.62)`——**是小尺寸下这条描边让它读成 3D，不是渐变**。


## 八、B 档（物体级 3D）现在能做

`routekit.render3d` 走 plotly + kaleido 离线出 PNG，本机实测可用（不需要 GPU/OpenGL）：

```python
from routekit import render3d as r3
fig = r3.ball_stick(atoms, bonds, width=760, height=620)   # atoms=[(x,y,z,r,colour)]
r3.export(fig, "cell.png", scale=3)                        # ≈ 600 dpi
```

适合：病毒颗粒、细胞/细胞器、纳米颗粒、分子球棍（**必须用真实 PDB/PubChem 坐标**）。
不合适：整幅场景（用 `iso`）、需要可编辑（用 `iso`）、需要期刊级写实渲染（需外部素材）。


