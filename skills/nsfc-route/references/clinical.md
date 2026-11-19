# 临床研究的技术路线图（队列 / 干预 / RCT）

> 这一篇是 `nsfc-route` 的临床分册。基础研究口（细胞–动物–机制）走主 SKILL.md 的三段式即可；
> **临床口的评审看的是另一套东西**：你的病人从哪来、怎么分组、终点是什么、统计站不站得住。
> 图里缺任何一环，都会被判"方案不可行"而不是"图画得不好"。

## 一、临床口和基础口的差别

| | 基础研究口 | 临床研究口 |
|---|---|---|
| 起点 | 分子/通路假说 | **临床问题**（诊断难、疗效差、预后不明） |
| 中段 | 细胞 → 动物 → 机制 | **人群**（队列/病例/ RCT）→ 样本 → 检测 |
| 终点 | 表型/通路 | **硬终点**（OS、PFS、MACE、住院率、AE）+ 替代终点 |
| 评审追问 | 机制是否闭环 | **样本量够不够、混杂控没控、结论能不能推广** |
| 图里必须有 | 关键技术、通路 | 纳排标准、分组、随访时长、统计方法、伦理/注册号 |
| 常见致命伤 | 内容=实验步骤 | 没有终点、没有样本量、没有伦理、分组说不清 |

## 二、三种获批构型（按研究设计选，不要混用）

### 构型 A：回顾性队列 / 病例对照（最常见，也最容易画成流水账）

```
[临床问题] ──► [研究对象] ──► [暴露/分组] ──► [检测] ──► [结局] ──► [转化]
  诊断延迟?      纳排+样本量     高/低暴露       组学+病理     OS/PFS      预测模型
                 伦理号                    ↕ 混杂校正（PSM / 多因素）        ↕ 外部验证
```

模块卡写法：

- **研究对象**：单中心/多中心、年份区间、纳排标准各 1 行、`n = 目标样本量`（写清怎么算的）。
- **暴露与分组**：按什么切的（cut-off 来源要写：中位数 / ROC 约登指数 / 文献阈值）。
- **检测**：临床指标（实验室/影像/病理）+ 组学，两栏并列。
- **结局**：主要终点 1 个 + 次要终点 ≤2 个，写随访中位数。
- **转化**：预测模型 / 列线图 / 临床路径，以及**外部验证队列**。

### 构型 B：前瞻性队列（含干预性随访）

在 A 的骨架上加两件东西：**时间轴上的随访节点**（基线 / 3 / 6 / 12 月）和**失访处理**。
注意：国自然正文里时间轴只画"随访节点"这一个用途，不要画成甘特图。

### 构型 C：RCT（CONSORT 骨架，评审最认这一套）

```
[筛选] n = ___  ──► [随机化 1:1]  ──┬──► [试验组] ──► [随访] ──► [主要终点]
      ↓ 排除 (n=___, 原因)          └──► [对照组] ──► [随访] ──► [主要终点]
[入组] n = ___（ITT 集）                    ↓ 失访/AE 记录
```

必须有：注册号（ChiCTR / NCT）、随机方法与盲法、样本量估算依据、ITT/PP 分析集、不良事件。

## 三、必备要素清单（缺一项就可能被质疑可行性）

1. **伦理与注册**：伦理批号占位、临床试验注册号（RCT 必填，队列建议填）。
2. **纳排标准**：入组 3 条、排除 3 条，写具体切点。
3. **样本量**：给出依据（效应量、α=0.05、power=0.8、失访率 15%）。
4. **分组依据**：cut-off 的来源必须写，不能只写"高/低表达"。
5. **终点定义**：主要终点 1 个；次要终点 ≤2 个；写随访中位数（月）。
6. **统计方法**：主分析 + 混杂校正（PSM / 多因素 Cox）+ 敏感性分析。
7. **验证**：内部（Bootstrap/交叉验证）+ 外部（独立中心/公共数据库）。
8. **转化落点**：临床路径、指南条目、专利、试剂盒——写一个具体的。

## 四、统计图怎么选（图上只放 1–2 张，别堆）

| 研究目的 | 图 | routekit 调用 |
|---|---|---|
| 生存/预后（OS、PFS、无事件生存） | Kaplan–Meier + 风险人数表 | `mp.survival({name: (t, p)}, p)` |
| 诊断/预测效能 | ROC（多模型对比 + AUC） | `mp.roc({name: (fpr, tpr)}, p, auc={...})` |
| 亚组 / 多因素 | 森林图（HR/OR + 95% CI） | `mp.forest([(lab, est, lo, hi)], p, log=True)` |
| 预测模型 | 列线图 / 校准曲线 | 原生形状 + `mp.lines` |
| 组学差异 | 火山图 / 热图 | `mp.heat(matrix, p)` |

```python
from routekit import miniplot as mp

# ROC：AUC 写进图例，省一块文字
cv.plot(Box(20, 40, 40, 32), mp.roc(
    {"Model A": (fpr_a, tpr_a), "Model B": (fpr_b, tpr_b)}, cv.p,
    auc={"Model A": 0.88, "Model B": 0.74}), dpi=600, name="roc")

# 森林图：log=True 走 HR/OR，右侧自动列 "est (lo–hi)"
cv.plot(Box(70, 40, 46, 32), mp.forest(
    [("Age > 65", 1.82, 1.21, 2.74), ("SCFA high", 0.58, 0.37, 0.91)],
    cv.p, log=True), dpi=600, name="forest")
```

**数据纪律**：图上的 HR、AUC、P 值必须来自真实分析或已在正文写明的预实验/文献值；
示意值要在图注写 `schematic`。临床口评审会对着正文数字核图，编一个数就前功尽弃。

完整可跑范例：`examples/build_clinical_a4.py`（产物 `examples/nsfc-clinical-demo.png`）——
回顾性队列 → 前瞻性队列 + 样本库 → RCT + 森林图，含伦理/注册/样本量占位行。

## 五、临床图元（本机已有，直接 `cv.icon`）

| 场景 | asset id |
|---|---|
| 医护团队 | `custom/figures/clinician-team` |
| 病房 / 病床 + 监护 | `custom/figures/hospital-ward` |
| 静脉输液 | `custom/figures/iv-drip` |
| 采血管（紫/红/黄） | `custom/figures/blood-collection-tubes` |
| 病历 / 随访表 | `custom/figures/medical-record`、`custom/figures/questionnaire-sheet` |
| 影像检查（CT/MRI 机架） | `custom/figures/imaging-scanner`、`scidraw/other/mri-scanner-c7545601` |
| 人群队列 / 生物样本库 | `custom/figures/cohort-people`、`custom/figures/biobank-rack` |
| 患者个体 | `bioicons/patient`、`custom/figures/human-male` / `human-female` |
| 药物（胶囊 / 片剂 / 注射） | `scidraw/other/pill-capsule-medicine-7ee92768`、`scidraw/other/tablet-e081faab`、`bioicons/simple-syringe-cartoon` |
| 手术 / 急救 / 记录 | `sciglyph/07-glassware-consumables/hardware-tools/029-scalpel-handle-blade`、`sciglyph/09-safety-signage/ppe-emergency/015-first-aid-kit`、`sciglyph/12-icons-ui/icons-ui/038-clipboard` |
| 器官 | `bioicons/brain-1`、`bioicons/liver`、`bioicons/kidney-2`、`sciglyph/12-icons-ui/icons-ui/040-heart`、`sciglyph/05-ecology-biotech/habitats/021-lung` |

判据：临床图里**图元总数 ≤8 个**，每个 ≥12 mm；其余用文字卡。堆图元会让评审觉得"没想清楚"。

## 六、临床口常见退回原因

| 现象 | 评审第一反应 | 修法 |
|---|---|---|
| 只画"收集样本→测序→分析" | 这是实验流程，不是临床研究 | 补纳排、分组、终点、随访 |
| 没有样本量 | 做不完 | 加 `n = ___` 与估算依据 |
| 没有伦理 / 注册号 | 不合规 | 第一区底下加一行小字占位 |
| 终点写成"观察疗效" | 不可考核 | 换成 OS/PFS/ORR/AE 等硬指标 |
| 分组只有"高/低" | cut-off 来路不明 | 写中位数 / 约登指数 / 文献阈值 |
| 统计只写"t 检验" | 混杂没控 | 写 PSM / 多因素 Cox / 敏感性分析 |
| 只有内部数据 | 结论不可推广 | 加外部验证队列（或公共数据库） |
| 图里塞 6 张统计图 | 重点不清 | 全图最多 2 张，其余进正文 |

## 七、自检（在 checklist.md 的 20 条之外，临床口额外加这 6 条）

1. 图里能找到**一个**明确的临床问题（不是机制问题）。
2. 能一眼看出**病人从哪来、多少个、怎么分的组**。
3. 主要终点有名字（OS/PFS/MACE/ORR/AE），不是一个箭头。
4. 有统计方法的落点（PSM / Cox / ROC），而不是"进行统计分析"。
5. 有伦理/注册占位与随访时长。
6. 结论箭头指向一个**可落地**的东西（模型、路径、指南、专利）。
