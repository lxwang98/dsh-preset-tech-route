"""Remote asset providers — BioRender-class illustrations fetched on demand.

The bundle ships a *catalogue* of remote assets (metadata only, a few hundred KB)
so that searching is instant and offline.  When a figure actually needs one, the
SVG is downloaded once into ``assets/.remote/<provider>/`` and reused forever.

Providers
---------
``bioicons``
    The complete Bioicons library (2 830 SVG, 428 MB upstream) served from
    raw.githubusercontent.com.  It contains the two collections that get closest
    to BioRender's look: **Servier Medical Art** (1 374 files, CC BY 3.0) and
    **DBCLS / Togo picture gallery** (634 files, CC BY 4.0) — full-colour,
    shaded medical and biological illustrations, not line art.
``reactome``
    Reactome icon library (2 569 icons, CC BY 4.0) — flat pathway glyphs.

Usage
-----
    python -m routekit.remote sync                 # refresh the catalogue
    python -m routekit.remote stats
    python -m routekit.remote search "心脏" -k 12 --sheet out/cardiac.png
    python -m routekit.remote fetch servier/mouse
    python -m routekit.remote sheet servier/mouse servier/heart -o out.png

Inside a figure::

    from routekit import Canvas
    from routekit.remote import asset           # returns an Asset-like handle
    cv.icon(box, asset("servier/mouse"))        # downloads on first use

Licensing is carried per asset: Servier is CC BY 3.0, DBCLS CC BY 4.0, and both
require attribution in the caption.  ``attribution`` is part of every record and
``docs/ATTRIBUTION.md`` shows the caption form.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path

from . import icons as _icons

# --------------------------------------------------------------------------- #
# paths
# --------------------------------------------------------------------------- #

BUNDLE = Path(__file__).resolve().parents[4]
ASSETS = Path(os.environ.get("ROUTEKIT_ASSETS", BUNDLE / "assets"))
REMOTE_INDEX = ASSETS / "remote" / "index.json"
CACHE_DIR = Path(os.environ.get("ROUTEKIT_REMOTE_CACHE", ASSETS / ".remote"))

BIOICONS_REPO = "duerrsimon/bioicons"
BIOICONS_BRANCH = "main"
RAW = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"
TREE_API = "https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
USER_AGENT = "routekit-remote/1.0 (+https://github.com/lxwang98/dsh-preset-tech-route)"

LICENSE_LABEL = {
    "cc-0": ("CC0-1.0", "public domain"),
    "cc-by-3.0": ("CC-BY-3.0", "attribution required"),
    "cc-by-4.0": ("CC-BY-4.0", "attribution required"),
    "cc-by-sa-3.0": ("CC-BY-SA-3.0", "attribution + share-alike"),
    "cc-by-sa-4.0": ("CC-BY-SA-4.0", "attribution + share-alike"),
    "mit": ("MIT", "attribution required"),
    "bsd": ("BSD-3-Clause", "attribution required"),
}

AUTHOR_LABEL = {
    "Servier": "Servier Medical Art",
    "DBCLS": "DBCLS / Togo picture gallery",
    "OpenClipart": "Openclipart",
}

# collections worth surfacing by their own name (they are the BioRender-look sets)
COLLECTIONS = {
    "servier": "Servier Medical Art",
    "dbcls": "DBCLS Togo picture gallery",
    "openclipart": "Openclipart",
}


# --------------------------------------------------------------------------- #
# records
# --------------------------------------------------------------------------- #

@dataclass
class Remote:
    """One remote asset.  ``id`` is ``<provider>/<collection>/<stem>``."""

    id: str
    provider: str
    collection: str
    stem: str
    name: str
    zh: str
    cat: str
    author: str
    license: str
    attribution: str
    url: str
    bytes: int = 0
    tags: list[str] = field(default_factory=list)

    # ---- duck-typing so Canvas.icon() accepts it like a catalog Asset ---- #
    @property
    def slug(self) -> str:
        return self.id

    @property
    def svg(self) -> str:
        return self.url

    @property
    def fmt(self) -> str:
        return "illustration"

    @property
    def series(self) -> str:
        return self.collection

    @property
    def en(self) -> str:
        return self.name

    def path(self) -> Path:
        return fetch(self)

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, d: dict) -> "Remote":
        return cls(**{k: d[k] for k in d if k in cls.__dataclass_fields__})


# --------------------------------------------------------------------------- #
# name handling
# --------------------------------------------------------------------------- #

_SPLIT = re.compile(r"[-_\s]+")
_STRIP = re.compile(r"$^")  # keep numeric variants (-1/-2)


def _stem_name(path: str) -> str:
    stem = path.rsplit("/", 1)[-1][:-4]
    stem = _STRIP.sub("", stem)
    return stem


def _pretty(stem: str) -> str:
    words = [w for w in _SPLIT.split(stem) if w]
    out = " ".join(w if w.isupper() else w.replace("_", " ").capitalize() for w in words)
    return out[:1].upper() + out[1:]


def _translate(stem: str) -> str:
    """Best-effort Chinese name from the token glossary (heart -> 心脏)."""
    try:
        from . import icons as ic  # glossary lives with the local index builder
        glossary = getattr(ic, "GLOSSARY", None) or _load_glossary()
    except Exception:  # pragma: no cover
        glossary = _load_glossary()
    words = [w for w in _SPLIT.split(stem.lower()) if w]
    zh = [glossary[w] for w in words if w in glossary]
    return " ".join(dict.fromkeys(zh))


def _load_glossary() -> dict:
    """Fallback: reuse the glossary file written by tools/build_index.py."""
    for cand in (ASSETS / "glossary.json", BUNDLE / "tools" / "glossary.json"):
        if cand.exists():
            return json.loads(cand.read_text(encoding="utf-8"))
    return {}


# --------------------------------------------------------------------------- #
# provider: bioicons
# --------------------------------------------------------------------------- #

def _http(url: str, *, timeout: int = 60, binary: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read() if binary else r.read().decode("utf-8")


def bioicons_records(refresh: bool = False) -> list[Remote]:
    """Catalogue of every SVG in the Bioicons repository."""
    cache = ASSETS / "remote" / "bioicons-tree.json"
    raw = None
    if cache.exists() and not refresh:
        raw = json.loads(cache.read_text(encoding="utf-8"))
    if raw is None:
        raw = json.loads(_http(TREE_API.format(repo=BIOICONS_REPO, branch=BIOICONS_BRANCH)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(raw), encoding="utf-8")

    out: list[Remote] = []
    for node in raw.get("tree", []):
        path = node.get("path", "")
        if not path.startswith("static/icons/") or not path.endswith(".svg"):
            continue
        parts = path.split("/")
        if len(parts) < 5:
            continue
        lic_dir, cat = parts[2], parts[3]
        author = parts[4] if len(parts) == 6 else "Bioicons"
        lic, _ = LICENSE_LABEL.get(lic_dir, (lic_dir.upper(), ""))
        slug = re.sub(r"[^a-z0-9]+", "-", author.lower()).strip("-") or "bioicons"
        coll = slug if slug in COLLECTIONS else "bioicons"
        stem = _stem_name(path)
        pretty = _pretty(stem)
        out.append(
            Remote(
                id=f"bioicons/{slug}/{cat}/{stem}",
                provider="bioicons",
                collection=coll,
                stem=stem,
                name=pretty,
                zh=_translate(stem),
                cat=cat.replace("_", " "),
                author=AUTHOR_LABEL.get(author, author.replace("--", " ").replace("-", " ")),
                license=lic,
                attribution=f"{AUTHOR_LABEL.get(author, author)} via Bioicons (https://bioicons.com)",
                url=RAW.format(repo=BIOICONS_REPO, branch=BIOICONS_BRANCH, path=path),
                bytes=node.get("size", 0),
                tags=[w for w in _SPLIT.split(stem.lower()) if len(w) > 2],
            )
        )
    return out


def reactome_records(refresh: bool = False) -> list[Remote]:
    """Reactome icon library — flat pathway glyphs, CC BY 4.0."""
    cache = ASSETS / "remote" / "reactome.json"
    if cache.exists() and not refresh:
        return [Remote.from_json(d) for d in json.loads(cache.read_text(encoding="utf-8"))]

    cats = ["arrow", "background", "cell_element", "cell_type", "compound",
            "human_tissue", "protein", "receptor", "therapeutic", "transporter"]
    seen: dict[str, Remote] = {}
    for cat in cats:
        try:
            html = _http(f"https://reactome.org/icon-lib/{cat}")
        except Exception:
            continue
        for m in re.finditer(r"/icon/(R-ICO-\d+)\.svg", html):
            rid = m.group(1)
            if rid in seen:
                continue
            seen[rid] = Remote(
                id=f"reactome/{cat}/{rid}",
                provider="reactome",
                collection="reactome",
                stem=rid,
                name=f"{cat.replace('_', ' ').title()} {rid.replace('R-ICO-', '')}",
                zh="",
                cat=cat.replace("_", " "),
                author="Reactome",
                license="CC-BY-4.0",
                attribution="Reactome Icon Library (https://reactome.org/icon-lib)",
                url=f"https://reactome.org/icon/{rid}.svg",
                tags=[w for w in cat.split("_")],
            )
    recs = list(seen.values())
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps([r.to_json() for r in recs], ensure_ascii=False), encoding="utf-8")
    return recs


PROVIDERS = {"bioicons": bioicons_records, "reactome": reactome_records}


# --------------------------------------------------------------------------- #
# index
# --------------------------------------------------------------------------- #

def build_index(providers: list[str] | None = None, refresh: bool = True) -> list[Remote]:
    recs: list[Remote] = []
    for key in providers or ["bioicons"]:
        try:
            recs.extend(PROVIDERS[key](refresh=refresh))
        except Exception as exc:  # pragma: no cover - network
            print(f"! provider {key} failed: {exc}", file=sys.stderr)
    seen, uniq = set(), []
    for r in recs:
        if r.id in seen:
            continue
        seen.add(r.id)
        uniq.append(r)
    REMOTE_INDEX.parent.mkdir(parents=True, exist_ok=True)
    REMOTE_INDEX.write_text(json.dumps([r.to_json() for r in uniq], ensure_ascii=False), encoding="utf-8")
    return uniq


def all_records() -> list[Remote]:
    if not REMOTE_INDEX.exists():
        return []
    return [Remote.from_json(d) for d in json.loads(REMOTE_INDEX.read_text(encoding="utf-8"))]


def _score(rec: Remote, q: str) -> float:
    q = q.strip().lower()
    if not q:
        return 0.0
    hay = " ".join([rec.stem, rec.name, rec.zh, rec.cat, rec.collection, " ".join(rec.tags)]).lower()
    if q == rec.id.lower() or q == rec.stem.lower():
        return 100.0
    score = 0.0
    if q in rec.stem.lower():
        score += 40 + (10 if rec.stem.lower().startswith(q) else 0)
    if q in rec.zh:
        score += 35
    if q in rec.name.lower():
        score += 25
    if q in rec.cat.lower():
        score += 15
    if q in rec.collection:
        score += 10
    for tok in q.split():
        if tok and tok in hay:
            score += 5
    return score


def search(q: str = "", k: int = 12, *, collection: str | None = None,
           provider: str | None = None) -> list[Remote]:
    recs = all_records()
    if collection:
        recs = [r for r in recs if r.collection == collection]
    if provider:
        recs = [r for r in recs if r.provider == provider]
    if q:
        scored = [(_score(r, q), r) for r in recs]
        scored = [p for p in scored if p[0] > 0]
        scored.sort(key=lambda p: (-p[0], p[1].bytes))
        return [r for _, r in scored[:k]]
    return recs[:k]


def get(asset_id: str) -> Remote:
    for r in all_records():
        if r.id == asset_id or r.stem == asset_id:
            return r
    raise KeyError(f"unknown remote asset: {asset_id!r} (run `python -m routekit.remote sync`)")


# --------------------------------------------------------------------------- #
# fetch
# --------------------------------------------------------------------------- #

def fetch(rec: Remote, *, force: bool = False) -> Path:
    """Download (once) and return the local SVG path."""
    dest = CACHE_DIR / rec.provider / (rec.id.replace("/", "__") + ".svg")
    if dest.exists() and not force and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = _http(rec.url, binary=True)
    except urllib.error.HTTPError as exc:  # pragma: no cover - network
        raise RuntimeError(f"download failed ({exc.code}) {rec.url}") from exc
    if len(data) < 64:
        raise RuntimeError(f"download too small ({len(data)} B) {rec.url}")
    dest.write_bytes(data)
    (dest.with_suffix(".license.txt")).write_text(
        f"{rec.id}\n{rec.name} ({rec.cat})\n{rec.license}\n{rec.attribution}\n{rec.url}\n",
        encoding="utf-8",
    )
    return dest


def asset(asset_id: str, *, force: bool = False) -> Path:
    """Convenience for figure code: id -> local PNG path (transparent, 1100 px)."""
    rec = get(asset_id)
    return _icons.png(rec, px=1100)


# --------------------------------------------------------------------------- #
# review helpers
# --------------------------------------------------------------------------- #

def sheet(recs: list[Remote], out: str | Path, *, cols: int = 6, cell_px: int = 220) -> Path:
    """Contact sheet of remote assets; downloads what it needs."""
    from PIL import Image, ImageDraw, ImageFont

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not recs:
        raise ValueError("no assets to sheet")
    rows = (len(recs) + cols - 1) // cols
    pad, label_h = 10, 30
    W = cols * (cell_px + pad) + pad
    H = rows * (cell_px + label_h + pad) + pad
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 13)
    except Exception:  # pragma: no cover
        font = ImageFont.load_default()

    for i, rec in enumerate(recs):
        r, c = divmod(i, cols)
        x = pad + c * (cell_px + pad)
        y = pad + r * (cell_px + label_h + pad)
        try:
            png = _icons.png(rec, px=cell_px * 2)
            icon = Image.open(png).convert("RGBA")
            icon.thumbnail((cell_px, cell_px), Image.LANCZOS)
            img.paste(icon, (x + (cell_px - icon.width) // 2, y + (cell_px - icon.height) // 2), icon)
        except Exception as exc:  # pragma: no cover
            d.text((x + 6, y + 6), f"! {exc}"[:28], fill="red", font=font)
        label = f"{rec.id.split('/', 1)[1]}"[:34]
        d.text((x + 2, y + cell_px + 4), label, fill="#333333", font=font)
        d.text((x + 2, y + cell_px + 18), f"{rec.cat} · {rec.license}", fill="#888888", font=font)
    img.save(out)
    return out


def stats() -> dict:
    recs = all_records()
    by_lic, by_coll, by_cat = {}, {}, {}
    for r in recs:
        by_lic[r.license] = by_lic.get(r.license, 0) + 1
        by_coll[r.collection] = by_coll.get(r.collection, 0) + 1
        by_cat[r.cat] = by_cat.get(r.cat, 0) + 1
    return {
        "total": len(recs),
        "bytes": sum(r.bytes for r in recs),
        "by_license": dict(sorted(by_lic.items(), key=lambda kv: -kv[1])),
        "by_collection": dict(sorted(by_coll.items(), key=lambda kv: -kv[1])),
        "top_categories": dict(list(sorted(by_cat.items(), key=lambda kv: -kv[1]))[:12]),
        "cached": len(list(CACHE_DIR.rglob("*.svg"))) if CACHE_DIR.exists() else 0,
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "stats"
    if cmd == "sync":
        providers = argv[2:] or ["bioicons"]
        recs = build_index(providers, refresh=True)
        print(f"wrote {REMOTE_INDEX} ({len(recs)} records, {REMOTE_INDEX.stat().st_size/1024:.0f} KB)")
        return 0
    if cmd == "stats":
        print(json.dumps(stats(), indent=2, ensure_ascii=False))
        return 0
    if cmd == "search":
        args = [a for a in argv[2:] if not a.startswith("-")]
        q = args[0] if args else ""
        k, coll, sheet_out = 12, None, None
        for i, a in enumerate(argv):
            if a in ("-k", "--limit"):
                k = int(argv[i + 1])
            elif a in ("-c", "--collection"):
                coll = argv[i + 1]
            elif a in ("--sheet", "-s"):
                sheet_out = argv[i + 1]
        recs = search(q, k=k, collection=coll)
        for r in recs:
            print(f"{r.id:<58} {r.license:<12} {r.bytes//1024:>4} KB  {r.name[:40]}")
        if not recs:
            print("(no match — try an English keyword, or `sync` first)")
        if sheet_out and recs:
            print(f"sheet -> {sheet(sheet_out, recs) if False else sheet(recs, sheet_out)}")
        return 0
    if cmd == "fetch":
        for aid in [a for a in argv[2:] if not a.startswith("-")]:
            rec = get(aid)
            p = fetch(rec)
            print(f"{rec.id} -> {p} ({p.stat().st_size//1024} KB, {rec.license})")
        return 0
    if cmd == "sheet":
        ids = [a for a in argv[2:] if not a.startswith("-")]
        out = "remote-sheet.png"
        for i, a in enumerate(argv):
            if a in ("-o", "--out"):
                out = argv[i + 1]
        ids = [i for i in ids if i not in (out,)]
        recs = [get(i) for i in ids] or search("", k=24)
        print(sheet(recs, out))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main(sys.argv))
