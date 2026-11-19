# 云端素材库（不占本地，按需取用）

本地只有一份**元数据索引**（`assets/remote/index.json`，约 2.2 MB）；
用到哪一件才下载哪一件，落到 `assets/.remote/<provider>/` 缓存，之后永久复用、离线可用。
这正是"云端库"该有的形态：检索秒回、图不必先入库。

## 一、库里有什么

| 来源 | 件数 | 许可 | 长相 |
|---|---|---|---|
| **Servier Medical Art** | 1374 | CC BY 3.0 | 彩色、有明暗，**最接近 BioRender** |
| **DBCLS / Togo picture gallery** | 634 | CC BY 4.0 | 医学插画风，人物/器械好 |
| Reactome Icon Library | 2149 | CC BY 4.0 | 扁平通路图标（细胞、蛋白、受体） |
| Bioicons 其余（含 almacell 等） | 821 | CC0 / CC BY | 混编 |
| **合计** | **4978** | — | — |

> 为什么没有 BioRender：它的许可只允许在自家编辑器内使用，**禁止提取与再分发**。
> 把它的素材搬进来会让整张图的授权链断掉（期刊会追问来源），所以不收。
> 有订阅的话：在 BioRender 里出图 → 导出整图当**参考锚点** → 我用等价矢量重画。

## 二、怎么用（一行）

```python
from routekit import Canvas, Box
from routekit.remote import asset          # id -> 本地 PNG（首次下载，之后走缓存）

cv = Canvas(180, 110)
cv.icon(Box(10, 10, 30, 30), asset("servier/Human_physiology/heart"))
```

检索（离线、瞬时，返回带许可与署名的记录）：

```bash
python -m routekit.remote stats
python -m routekit.remote search "goblet" -k 12 --sheet out/x.png
python -m routekit.remote sync bioicons reactome      # 重建目录（联网）
```

## 三、主题目录页（先看再挑）

`assets/remote/sheets/` 下有六张 4×4 对照页，每格标了 **id + 类别 + 许可**，
看中哪件就把 id 抄给我：

| 文件 | 主题 | 适合 |
|---|---|---|
| `organs.png` | 器官 / 组织 | 心肝肺脑肾胃肠、皮肤剖面、肌肉 |
| `cells.png` | 细胞 | 巨噬、中性粒、树突、杯状、成纤维、红细胞 |
| `lab.png` | 仪器 / 器皿 | 显微镜、离心机、培养箱、电泳、分光、移液器 |
| `microbes.png` | 微生物 | 细菌、病毒、酵母、寄生虫、培养皿 |
| `people.png` | 人物 | 查体、采血、输液、超声、老年/儿童 |
| `clinical.png` | 临床场景 | X 光、安瓿、采血、输液、听诊、心电、药品 |

重建（加了筛选闸后）：

```bash
python tools/build_cloud_sheets.py
```

## 四、三道质量闸（v1 踩过的坑）

纯关键词检索会把"牙齿、佝偻病、DNA 序列、黑底酵母"当成"人物/微生物"。所以：

1. **来源优先**：servier > dbcls > almacell > bioicons > reactome（reactome 只兜底）；
2. **亮度闸**：渲染后非透明像素平均亮度 < 95 一律丢弃（黑底截图、深色照片件全清）；
3. **同族折叠**：按 stem 首词归族，每族最多 2 个（否则四张脂肪细胞刷屏）。
   人物/临床两类**不用关键词**，走人工白名单。

## 五、云端缺什么（这些用自制件补）

| 缺的 | 自制的替代 |
|---|---|
| 病房 / 病床 + 监护 | `custom/figures/hospital-ward` |
| 医护团队 | `custom/figures/clinician-team` |
| 输液（整套） | `custom/figures/iv-drip` |
| 采血管（真空三色） | `custom/figures/blood-collection-tubes` |
| 病历 / 知情同意 | `custom/figures/medical-record` |
| CT / 影像设备 | `custom/figures/imaging-scanner` |
| 队列人群（≤12 mm 可读） | `custom/figures/cohort-people-4` |
| 带细胞的培养皿 | `custom/figures/petri-dish-cells` |

## 六、许可记账（不能省）

每条记录都带 `license` 与 `attribution`，下载时同时写一份
`<asset>.license.txt` 到缓存目录。出图时按此规则落 `ATTRIBUTION.md`：

- **CC0**：免署名，仍记来源；
- **CC BY 3.0 / 4.0**：图注必须写 "… via Servier Medical Art (CC BY 3.0)" 之类；
- **CC BY-SA**：传染性许可，**不要**用在要投稿的图里（避免整图被迫同协议）。
