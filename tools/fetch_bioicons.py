"""Build-time fetcher: pull a curated Bioicons subset into assets/bioicons.

github.com HTML is unreachable from this machine, but api.github.com and
raw.githubusercontent.com are, so the tree comes from the API and each file
from raw. Only a curated slice is fetched (the full repo is 428 MB); the
slice is chosen by topic so a biomedical route figure always has the
organisms, organs, lab hardware and food icons it needs.

    python tools/fetch_bioicons.py            # fetch
    python tools/fetch_bioicons.py --dry      # just report the selection
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "bioicons"
API = "https://api.github.com/repos/duerrsimon/bioicons/git/trees/main?recursive=1"
RAW = "https://raw.githubusercontent.com/duerrsimon/bioicons/main/"
UA = {"User-Agent": "dsh-agent"}

# licence directory -> (label, uri, preference rank; lower = preferred)
LIC = {
    "cc-0": ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/", 0),
    "mit": ("MIT", "https://opensource.org/license/mit", 1),
    "cc-by-4.0": ("CC-BY-4.0", "https://creativecommons.org/licenses/by/4.0/", 2),
    "cc-by-3.0": ("CC-BY-3.0", "https://creativecommons.org/licenses/by/3.0/", 3),
    "cc-by-sa-4.0": ("CC-BY-SA-4.0", "https://creativecommons.org/licenses/by-sa/4.0/", 4),
    "cc-by-sa-3.0": ("CC-BY-SA-3.0", "https://creativecommons.org/licenses/by-sa/3.0/", 5),
    "bsd": ("BSD-3-Clause", "https://opensource.org/license/bsd-3-clause", 6),
}

# family -> (regex on basename, cap)
FAMILIES: dict[str, tuple[str, int]] = {
    "rodent": (r"^(mouse|Mouse|rat)-?[A-Za-z0-9]*$|^rat[-_]|hamster|guineapig", 14),
    "gut": (r"colon|intestin|gut_|stomach|villi|duoden|cecum|caecum|cross-section", 12),
    "organ": (r"^(brain|heart|liver|kidney|lung|pancrea|spleen|fat-tissue|bladder|"
              r"thyroid|adipose|langerhans)", 16),
    "food": (r"^(rice|Rice|wheat|Oat|bread|cereal|Dietetics|TomatoFruit)", 8),
    "human": (r"^(Human_male|Human_female|old-man|old-women|patient|Child|"
              r"Examination_)", 8),
    "lab": (r"microscope|centrifuge|sequencer|cytometer|well[-_]plate|petri-dish|"
            r"flask|pipette|syringe|cryo_vial|TUBE|Vial|incubator|chromatograph|"
            r"^balance", 26),
    "micro": (r"Bacteria1M|Bacteria2M|generic-bacterium|Gram_|^bacterium", 14),
    "people": (r"group|cohort|people|family", 6),
    "arrow": (r"^arrow-(right|left|up|down|split|curved-clockwise-1|corner-up|"
              r"circular)", 10),
}

# oversized or raster-bundled files are useless in a vector pipeline
EXCLUDE = (r"spectral|_Maze|colony|fluke|mildew|drawio|\.drawio|giardia|"
           r"Trichomonas|anclystoma|metacercaria|cercaria")
MAX_BYTES = 520_000


def tree() -> list[dict]:
    req = urllib.request.Request(API, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return [e for e in data["tree"]
            if re.match(r"^static/icons/.*\.svg$", e["path"])]


def select(entries: list[dict]) -> list[dict]:
    picked: dict[str, dict] = {}   # family -> name -> entry  (one family per name)
    used: set[str] = set()
    order = list(FAMILIES)
    for fam in order:
        rx, cap = FAMILIES[fam]
        cands = []
        for e in entries:
            parts = e["path"].split("/")
            lic, name = parts[2], parts[-1]
            stem = name[:-4]
            if name in used or lic not in LIC:
                continue
            if not re.search(rx, stem) or re.search(EXCLUDE, stem):
                continue
            size = e.get("size", 0)
            if size > MAX_BYTES:
                continue
            rank = LIC[lic][2]
            # prefer small files (usually clean vector) within the same rank
            cands.append((rank, size, e))
        cands.sort(key=lambda t: (t[0], t[1]))
        got = []
        for rank, size, e in cands:
            if len(got) >= cap:
                break
            name = e["path"].split("/")[-1]
            if name in used:
                continue
            used.add(name)
            got.append(e)
        picked[fam] = got
        print(f"{fam:<8} {len(got):>3}")
    return [e for fam in order for e in picked[fam]]


def download(entry: dict) -> tuple[str, int]:
    rel = entry["path"].removeprefix("static/icons/")
    dest = OUT / rel
    if dest.exists() and dest.stat().st_size == entry.get("size", 0):
        return rel, dest.stat().st_size
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = RAW + urllib.request.quote(entry["path"])
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    dest.write_bytes(data)
    return rel, len(data)


def manifest(entries: list[dict]) -> None:
    items = []
    for e in entries:
        parts = e["path"].split("/")
        lic_dir, cat, name = parts[2], parts[3], parts[-1]
        lic, uri, _ = LIC[lic_dir]
        items.append({
            "file": e["path"].removeprefix("static/icons/"),
            "name_en": name[:-4].replace("_", " ").replace("-", " "),
            "name_zh": "",
            "tags": [cat.lower().replace("_", " "), lic_dir, name[:-4]],
            "category": cat, "subdir": lic_dir,
            "series": "bioicons", "format": "illustration",
            "license": lic, "license_uri": uri,
            "attribution": "Bioicons (https://bioicons.com)",
        })
    items.sort(key=lambda d: d["file"])
    (OUT / "manifest.json").write_text(json.dumps({
        "category": "bioicons", "subdir": "", "name_zh": "Bioicons 生命科学图标",
        "name_en": "Bioicons life-science icons", "count": len(items),
        "license": "mixed (per item)", "license_uri": "https://bioicons.com",
        "attribution": "Bioicons contributors, https://bioicons.com",
        "items": items,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"manifest: {len(items)} items")


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    entries = tree()
    print(f"repo has {len(entries)} icons")
    sel = select(entries)
    total = sum(e.get("size", 0) for e in sel) / 1e6
    print(f"selected {len(sel)} ({total:.1f} MB)")
    if "--dry" in argv:
        for e in sel:
            print("  ", e["path"], e.get("size", 0))
        return 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        got = list(ex.map(download, sel))
    ok = sum(1 for _, n in got if n > 0)
    print(f"downloaded {ok}/{len(got)} -> {OUT}")
    manifest(sel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
