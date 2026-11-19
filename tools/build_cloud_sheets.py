# -*- coding: utf-8 -*-
"""云端素材库 → 主题目录页（v2，带质量过滤）。

v1 的教训：纯关键词检索会把"牙齿、佝偻病、DNA 序列、黑底酵母"当成"人物/微生物"。
v2 加三道闸：
  1. 来源优先 servier > dbcls > almacell > bioicons > reactome（reactome 是扁平图标，只在兜底）；
  2. **亮度闸**：渲染后非透明像素平均亮度 < 95 的丢掉（黑底/深色截图一律不要）；
  3. **同族折叠**：按 stem 首词归族，每族最多留 2 个（避免 4 张脂肪细胞刷屏）。
人物/临床两个主题改为**人工白名单**（关键词根本选不对）。

输出：assets/remote/sheets/{organs,cells,lab,people,microbes,clinical}.png
"""
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\dsh-bundles\tech-route")
sys.path.insert(0, str(ROOT / "skills" / "tech-route-atlas" / "scripts"))

from PIL import Image  # noqa: E402

from routekit import icons, remote  # noqa: E402

OUT = ROOT / "assets" / "remote" / "sheets"
PREF = {"servier": 0, "dbcls": 1, "almacell": 2, "bioicons": 3, "openclipart": 4, "reactome": 6}
TARGET = 16

KW_THEMES = [
    ("organs", ["heart", "lung", "brain", "liver", "kidney", "stomach", "intestine",
                "pancreas", "spleen", "bone", "muscle", "eye", "skin", "bladder",
                "uterus", "thyroid", "spinal-cord", "esophagus"]),
    ("cells", ["neuron", "macrophage", "neutrophil", "platelet", "goblet-cell",
               "adipocyte", "fibroblast", "hepatocyte", "stem-cell", "red-blood-cell",
               "dendritic-cell", "mast-cell", "eosinophil", "osteoblast",
               "endothelial-cell", "t-cell"]),
    ("lab", ["microscope", "centrifuge", "incubator", "spectrophotometer", "beaker",
             "flask", "pipette", "gel-electrophoresis", "microplate", "pcr",
             "flow-cytometer", "bunsen", "balance", "water-bath", "shaker", "autoclave"]),
    ("microbes", ["bacterium", "virus", "coccus", "yeast", "bacteriophage",
                  "parasite", "toxoplasma", "fungus", "protozoa", "biofilm"]),
]

# 人工白名单：(collection, stem 前缀) —— 这些是看图确认过能用的
CURATED = {
    "people": [
        ("dbcls", "Examination_Man"), ("dbcls", "Examination_Woman"),
        ("dbcls", "Examination_child"), ("dbcls", "taking-blood-sample"),
        ("dbcls", "drip_iv_treatment"), ("dbcls", "ultrasonic-examination"),
        ("servier", "desk-job"), ("servier", "patient"),
    ],
    "clinical": [
        ("dbcls", "X-ray_Male"), ("dbcls", "X-ray_Female"),
        ("dbcls", "Medical_ampoule"), ("dbcls", "taking-blood-sample"),
        ("dbcls", "drip_iv_treatment"), ("dbcls", "Examination_Woman"),
        ("servier", "syringe"), ("servier", "infusion-bag-blue"),
        ("servier", "infusion-bag-green"), ("servier", "electrocardiogram-ecg"),
        ("servier", "drug-tablet"), ("servier", "drug-capsule"),
        ("servier", "bottle-drug"), ("servier", "stethoscope"),
    ],
}


def luminance(png: Path) -> float:
    im = Image.open(png).convert("RGBA").resize((64, 64))
    px = im.load()
    vals = [0.299 * px[x, y][0] + 0.587 * px[x, y][1] + 0.114 * px[x, y][2]
            for x in range(64) for y in range(64) if px[x, y][3] > 8]
    return sum(vals) / len(vals) if vals else 0.0


def family(stem: str) -> str:
    return re.split(r"[-_ ]+", stem.lower())[0]


def keep(rec, seen_fam: dict, *, check_lum=True) -> bool:
    fam = family(rec.stem)
    if seen_fam.get(fam, 0) >= 2:
        return False
    try:
        png = icons.png(rec, px=420)
    except Exception:
        return False
    if check_lum and luminance(png) < 95:
        return False
    seen_fam[fam] = seen_fam.get(fam, 0) + 1
    return True


DENY = ('plasmid', 'plaque', 'assay', 'titer', 'root', 'shoot', 'seed', 'leaf')


def by_keywords(kws, *, max_pref: int = 4):
    """按关键词收候选。max_pref 默认 4：把 Reactome（纯扁平通路图标）
    挡在主题页之外——它的"圆环通路图"放到微生物/仪器格里完全是误认。"""
    cands = {}
    for kw in kws:
        for r in remote.search(kw, k=4):
            if PREF.get(r.collection, 5) <= max_pref and not any(d in r.stem.lower() for d in DENY):
                cands.setdefault(r.id, r)
    return sorted(cands.values(), key=lambda r: (PREF.get(r.collection, 5), len(r.stem)))


def by_whitelist(pairs):
    recs = remote.all_records()
    out, seen = [], set()
    for coll, pref in pairs:
        for r in recs:
            if r.collection == coll and r.stem.startswith(pref) and r.id not in seen:
                out.append(r)
                seen.add(r.id)
                break
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"catalogue: {len(remote.all_records())} remote records")
    plan = [(k, by_keywords(v)) for k, v in KW_THEMES]
    plan += [(k, by_whitelist(v)) for k, v in CURATED.items()]

    for key, cands in plan:
        seen_fam: dict[str, int] = {}
        got = [r for r in cands if keep(r, seen_fam)][:TARGET]
        if not got:
            print(f"! {key}: nothing survived the filters")
            continue
        remote.sheet(got, OUT / f"{key}.png", cols=4, cell_px=210)
        print(f"{key:<9} {len(got):>2}/{TARGET}  -> {key}.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

