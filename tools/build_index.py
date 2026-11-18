"""Build assets/index.json from the library manifests.

The index is what `routekit.icons` reads: one flat list of records with a
stable id, the relative SVG path, bilingual names, tags and licence metadata.
Ids are `<library>/<category>/<subdir>/<stem>` so they sort by discipline and
survive an asset move inside its folder.

Chinese search terms are added to the tags through a glossary, because most
users ask for “小鼠” or “结肠”, not "mouse" or "colon", and Bioicons has no
Chinese names at all.

    python tools/build_index.py
    python tools/build_index.py --check      # verify every file exists
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
INDEX = ASSETS / "index.json"

# token -> Chinese aliases; any hit is appended to tags so search works in zh
GLOSSARY: dict[str, str] = {
    "mouse": "小鼠", "mice": "小鼠", "rat": "大鼠", "rodent": "啮齿动物",
    "hamster": "仓鼠", "guineapig": "豚鼠",
    "colon": "结肠", "intestine": "肠道", "gut": "肠道", "stomach": "胃",
    "villi": "绒毛", "duoden": "十二指肠", "cecum": "盲肠", "caecum": "盲肠",
    "liver": "肝脏", "brain": "脑", "heart": "心脏", "kidney": "肾脏",
    "lung": "肺", "pancrea": "胰腺", "spleen": "脾脏", "bladder": "膀胱",
    "fat": "脂肪", "adipose": "脂肪组织", "thyroid": "甲状腺",
    "rice": "水稻 大米", "wheat": "小麦", "oat": "燕麦", "bread": "面包",
    "cereal": "谷物", "diet": "膳食", "food": "食物", "nutrition": "营养",
    "human": "人", "people": "人群", "person": "人", "patient": "患者",
    "group": "分组", "cohort": "队列", "child": "儿童", "old": "老年",
    "microscope": "显微镜", "centrifuge": "离心机", "sequencer": "测序仪",
    "cytometer": "流式细胞仪", "plate": "孔板", "petri": "培养皿",
    "flask": "培养瓶", "pipette": "移液器", "syringe": "注射器",
    "vial": "样品瓶", "tube": "离心管", "incubator": "培养箱",
    "chromatograph": "色谱仪", "balance": "天平",
    "bacteri": "细菌", "bacterium": "细菌", "microbiome": "微生物组",
    "cell": "细胞", "tissue": "组织", "dna": "DNA", "gene": "基因",
    "arrow": "箭头", "cycle": "循环", "graph": "图", "chart": "图表",
    "feces": "粪便", "stool": "粪便", "serum": "血清", "blood": "血液",
    "muscle": "肌肉", "bone": "骨骼", "skin": "皮肤", "eye": "眼",
    "procedure": "实验流程", "protocol": "流程", "assay": "检测",
}

_STEM = re.compile(r"[^a-z0-9]+")

# the long-form keyword map lives in tools/glossary_zh.json so that both the
# local index and the remote catalogue (routekit.remote) share one vocabulary
EXTRA = Path(__file__).with_name("glossary_zh.json")
if EXTRA.exists():
    for _k, _v in json.loads(EXTRA.read_text(encoding="utf-8")).items():
        if not _k.startswith("_"):
            GLOSSARY.setdefault(_k, _v)


def zh_for(stem: str) -> list[str]:
    low = stem.lower()
    out: list[str] = []
    for key, zh in GLOSSARY.items():
        if key in low:
            out.extend(zh.split())
    return list(dict.fromkeys(out))


def sciglyph() -> list[dict]:
    out: list[dict] = []
    base = ASSETS / "sciglyph"
    for mf in sorted(base.glob("*/*/manifest.json")):
        meta = json.loads(mf.read_text(encoding="utf-8"))
        cat = meta.get("category", "other")
        sub = meta.get("subdir", "")
        for it in meta.get("items", []):
            fname = it["file"]
            if not fname.lower().endswith(".svg"):
                continue
            stem = fname[:-4]
            rid = f"sciglyph/{cat}/{sub}/{stem}"
            tags = list(dict.fromkeys(list(it.get("tags", [])) + zh_for(stem)))
            out.append({
                "id": rid,
                "svg": f"sciglyph/{cat}/{sub}/{fname}",
                "zh": it.get("name_zh", ""),
                "en": it.get("name_en", stem),
                "tags": tags,
                "cat": cat, "subdir": sub,
                "series": it.get("series", ""),
                "format": it.get("format", ""),
                "license": it.get("license", meta.get("license", "")),
                "license_uri": it.get("license_uri", meta.get("license_uri", "")),
                "attribution": it.get("attribution", meta.get("attribution", "")),
            })
    return out


def bioicons() -> list[dict]:
    out: list[dict] = []
    mf = ASSETS / "bioicons" / "manifest.json"
    if not mf.exists():
        return out
    meta = json.loads(mf.read_text(encoding="utf-8"))
    for it in meta.get("items", []):
        rel = it["file"]
        parts = Path(rel).parts          # <lic>/<category>/<author>/<file>.svg
        fname = Path(rel).name
        stem = fname[:-4]
        author = parts[2].replace("-", " ") if len(parts) > 3 else ""
        lic = it.get("license", "") or (parts[0] if parts else "")
        attrib = author or it.get("attribution", "")
        if attrib and "bioicons" not in attrib.lower():
            attrib = f"{attrib} via Bioicons (https://bioicons.com)"
        tags = list(dict.fromkeys(
            [fname[:-4].replace("-", " ").replace("_", " ")] + zh_for(stem)
            + [it.get("category", "").lower()]))
        out.append({
            "id": f"bioicons/{stem}",
            "svg": f"bioicons/{rel}",
            "zh": " ".join(zh_for(stem))[:40],
            "en": stem.replace("-", " ").replace("_", " "),
            "tags": tags,
            "cat": it.get("category", ""), "subdir": it.get("subdir", ""),
            "series": "bioicons", "format": "illustration",
            "license": lic, "license_uri": it.get("license_uri", ""),
            "attribution": attrib or "Bioicons (https://bioicons.com)",
        })
    return out


def custom() -> list[dict]:
    """Keep hand-curated assets already in the index.

    The custom records carry Chinese names, tags and attribution that cannot
    be inferred from a bare file, so they are read back from the previous
    index instead of being regenerated.
    """
    if not INDEX.exists():
        return []
    try:
        old = json.loads(INDEX.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for r in old:
        pid = r.get("id", "")
        if not pid.startswith("custom/"):
            continue
        p = r.get("svg")
        if p and (ASSETS / p).exists():
            out.append(r)
    return out


def scidraw() -> list[dict]:
    """SciDraw.io download manifest -> flat index records."""
    mf = ASSETS / "custom" / "scidraw" / "metadata.json"
    if not mf.exists():
        return []
    meta = json.loads(mf.read_text(encoding="utf-8"))
    lic_map = {
        "cc-by": ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
        "cc0": ("CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/"),
    }
    out: list[dict] = []
    for it in meta:
        rel = it.get("local_file")
        if not rel or not (ASSETS / rel).exists():
            continue
        cat = it.get("category_slug") or "other"
        name = it.get("name") or it.get("slug", "")
        slug = it.get("slug") or it.get("id", "")
        lic, uri = lic_map.get(it.get("license", ""), (it.get("license", ""), ""))
        author = (it.get("primary_author") or {}).get("full_name", "")
        doi = it.get("doi", "")
        attrib = f"{author} via SciDraw (https://scidraw.io)"
        if doi:
            attrib += f", DOI {doi}"
        if lic:
            attrib += f", {lic}"
        tags = list(dict.fromkeys(
            [name.lower(), cat] + zh_for(name + " " + cat)
        ))
        out.append({
            "id": f"scidraw/{cat}/{slug}",
            "svg": rel,
            "zh": " ".join(zh_for(name + " " + cat))[:40],
            "en": name,
            "tags": tags,
            "cat": cat, "subdir": cat,
            "series": "scidraw", "format": "illustration",
            "license": lic, "license_uri": uri,
            "attribution": attrib,
        })
    return out


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    recs = sciglyph() + bioicons() + custom() + scidraw()
    # duplicate ids would shadow each other in the catalog
    seen: dict[str, int] = {}
    for r in recs:
        seen[r["id"]] = seen.get(r["id"], 0) + 1
    dups = {k: v for k, v in seen.items() if v > 1}
    if dups:
        print(f"!! {len(dups)} duplicate ids, e.g. {list(dups)[:3]}")
    missing = [r["svg"] for r in recs if not (ASSETS / r["svg"]).exists()]
    if missing:
        print(f"!! {len(missing)} missing files, e.g. {missing[:3]}")
        if "--check" in argv:
            return 1
    recs.sort(key=lambda r: r["id"])
    INDEX.write_text(json.dumps(recs, ensure_ascii=False, indent=0), encoding="utf-8")
    # share the vocabulary with routekit.remote (zh labels for remote assets)
    (ASSETS / "glossary.json").write_text(
        json.dumps(GLOSSARY, ensure_ascii=False, indent=0), encoding="utf-8"
    )
    libs: dict[str, int] = {}
    for r in recs:
        lib = r["id"].split("/")[0]
        libs[lib] = libs.get(lib, 0) + 1
    print(f"wrote {INDEX}  ({INDEX.stat().st_size/1e6:.1f} MB, {len(recs)} records)")
    for k, v in libs.items():
        print(f"  {k:<10} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
