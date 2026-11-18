# 远程素材库（routekit.remote）

本机素材是"够用"，远程库是"好看"。要接近 BioRender 观感，用远程库里的
**Servier Medical Art** 与 **DBCLS** 两套彩色写实插画。

## 一句 API

```python
from routekit import Canvas, remote
from routekit.layout import Box

cv = Canvas(*CANVAS.slide_16x9, palette="cell")

cv.icon(Box(10, 10, 30, 30), "bioicons/servier/Animals/mouse-gray")   # 自动下载+缓存
hits = remote.search("结肠", k=6)                                      # 只查目录，不联网
rec = remote.get("bioicons/servier/Human_physiology/colon")
remote.fetch(rec)                 # -> assets/.remote/<provider>/<id>.svg
remote.sheet(hits, "out/candidates.png")   # 候选缩略图网格（会下载所选项）
remote.stats()                    # 总量/许可分布/集合分布/已缓存数
```

`Canvas.icon()` 接收三种东西：本机 id、远程 id、`remote.Remote` 记录；
本机索引里找不到的字符串会自动落到远程目录，找不到就画红框并写 warning，
不会中断构建。

## 目录长什么样

```
id           bioicons/<author-slug>/<Category>/<stem>
例           bioicons/servier/Human_physiology/colon
             bioicons/dbcls/Nucleic_acids/DNA_colored
             bioicons/james-lloyd/Microbiology/Bacteria_Swimming
```

`remote.search(q, k, collection=..., provider=...)`：`q` 支持中文（走
`assets/glossary.json` 的词表，约 240 个常用生物医学术语）、英文、类别名。
`collection` 取值：`servier`（1374）、`dbcls`（634）、`openclipart`（57）、
`bioicons`（其余作者）。`provider` 目前只有 `bioicons`，`reactome` 目录已实现
（CC BY 4.0，2569 个通路图标）但默认不拉，需要时 `python -m routekit.remote sync reactome`。

## CLI

```powershell
python -m routekit.remote stats
python -m routekit.remote search "肝脏" -k 8
python -m routekit.remote search "mouse" -k 12 --sheet out\mice.png
python -m routekit.remote search "" -c servier -k 24        # 逛一逛某个集合
python -m routekit.remote fetch bioicons/servier/Animals/rat-adult
python -m routekit.remote sync                              # 刷新目录（要联网）
```

`sync` 只重写 `assets/remote/index.json`（元数据），不下载任何 SVG。

## 缓存与离线

- 下载落在 `assets/.remote/bioicons/<id 里的斜杠换成 __>.svg`，旁边一份 `.license.txt`
  （id / 名称 / 许可 / 署名 / 来源 URL），随图带走。
- 命中缓存后不再联网；把整个 `assets/.remote` 删掉也只是下次重新下。
- 仓库里不带这 428 MB，只带 1.4 MB 目录 —— 这是"素材可以在网上，不必落本地"的实现方式。

## 许可与署名（硬规则）

| 集合 | 许可 | 署名要求 |
|---|---|---|
| Servier Medical Art | CC BY 3.0 | 必须署名：`Servier Medical Art (smart.servier.com), CC BY 3.0` |
| DBCLS / Togo picture gallery | CC BY 4.0 | 必须署名：`DBCLS Togo picture gallery, CC BY 4.0` |
| Bioicons 其他作者 | CC0 / CC BY 3.0 / 4.0 / MIT / BSD | 按记录里的 `attribution` 原样写 |
| Reactome | CC BY 4.0 | `Reactome Icon Library (reactome.org/icon-lib), CC BY 4.0` |

规则：

1. 图注或 Acknowledgements 里必须出现用到的每个集合的署名，不能只写"图标来自网络"。
2. CC BY-SA 素材（35 件）传染性更强，商业稿尽量避开。
3. `remote.fetch()` 会在缓存目录写 `.license.txt`；交付时把用到的记录汇总进 `docs/ATTRIBUTION.md` 的表。
4. AI 生成的 SciGlyph 素材要做事实核对（结构、颜色、解剖位置）；Servier/DBCLS 是人工绘制的，可信度更高。

## 选材顺序（省时间）

1. 先想清楚要"写实插画"还是"示意图元"：写实 → 远程 Servier/DBCLS；示意 → 本机 SciGlyph。
2. 一张图只用一个画风系列（别把线稿和写实插画放同一分区）。
3. 一个分区里的图标，视线高度/大小要一致：写实插画建议 ≥12 mm，线稿图元 6–8 mm。
4. 找不到就换同义词（colon → intestine → digestive-system；mouse → rodent → rat-adult）。
5. 还是没有：用本机 `10-figure-elements` 的构件自己搭，别硬放大一个不合适的图。
