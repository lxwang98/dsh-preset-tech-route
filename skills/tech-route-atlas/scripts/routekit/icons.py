"""Asset catalogue + SVG rasteriser.

The catalogue is a flat JSON index built from the manifest.json files shipped
with each asset library:

    {"id": "sciglyph/05-ecology-biotech/habitats/008-gut-colon",
     "svg": "sciglyph/05-ecology-biotech/habitats/008-gut-colon.svg",
     "zh": "肠道-结肠", "en": "Gut colon", "tags": [...],
     "cat": "05-ecology-biotech", "series": "atlas", "license": "CC-BY-4.0"}

Rasterisation goes SVG -> reportlab drawing -> PDF -> PyMuPDF pixmap (alpha),
which keeps vector sharpness and a transparent background and needs no
Inkscape / cairo / browser. Results are cached by (id, px, tint).

CLI
---
    python -m routekit.icons search "gut microbiome" -k 12 --sheet out.png
    python -m routekit.icons stats
    python -m routekit.icons sheet "mouse|human|stool" out.png
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BUNDLE = Path(__file__).resolve().parents[4]
ASSETS = Path(os.environ.get("ROUTEKIT_ASSETS", BUNDLE / "assets"))
CACHE = ASSETS / ".cache"
INDEX = ASSETS / "index.json"


# ------------------------------------------------------------------ entries

@dataclass(frozen=True)
class Asset:
    id: str
    svg: str
    zh: str
    en: str
    tags: tuple[str, ...]
    cat: str
    series: str
    fmt: str
    license: str
    attribution: str

    @property
    def path(self) -> Path:
        return ASSETS / self.svg

    @property
    def slug(self) -> str:
        return self.id.rsplit("/", 1)[-1]

    def __str__(self) -> str:  # compact one-liner for tool output
        return f"{self.id}  [{self.zh} / {self.en}]  {self.series}"


# ------------------------------------------------------------------ catalog

class Catalog:
    def __init__(self, index: Path = INDEX):
        if not index.exists():
            raise FileNotFoundError(
                f"asset index missing: {index}\n"
                "run  python tools/build_index.py  from the preset root"
            )
        raw = json.loads(index.read_text(encoding="utf-8"))
        self.assets: list[Asset] = [
            Asset(
                id=r["id"], svg=r["svg"], zh=r.get("zh", ""), en=r.get("en", ""),
                tags=tuple(r.get("tags", [])), cat=r.get("cat", ""),
                series=r.get("series", ""), fmt=r.get("format", r.get("fmt", "")),
                license=r.get("license", ""), attribution=r.get("attribution", ""),
            )
            for r in raw
        ]
        self.by_id = {a.id: a for a in self.assets}

    # -- lookup ------------------------------------------------------
    def get(self, asset_id: str, default=None):
        if asset_id in self.by_id:
            return self.by_id[asset_id]
        # tolerate a bare slug: pick the first match
        hits = [a for a in self.assets if a.slug == asset_id or a.slug.startswith(asset_id)]
        if len(hits) == 1:
            return hits[0]
        return default

    def require(self, asset_id: str) -> Asset:
        a = self.get(asset_id)
        if a is None:
            hits = [x.id for x in self.assets if asset_id.lower() in x.id.lower()][:6]
            raise KeyError(f"asset not found: {asset_id!r}; did you mean {hits}?")
        return a

    # -- search ------------------------------------------------------
    def search(self, query: str, k: int = 10, *, cat: str | None = None,
               series: str | None = None, fmt: str | None = None) -> list[Asset]:
        q = query.strip().lower()
        if not q:
            pool = self.assets
            if cat:
                pool = [a for a in pool if a.cat == cat]
            return pool[:k]
        terms = [t for t in re.split(r"[\s,;|]+", q) if t]
        scored: list[tuple[float, Asset]] = []
        for a in self.assets:
            if cat and a.cat != cat:
                continue
            if series and a.series != series:
                continue
            if fmt and a.fmt != fmt:
                continue
            score = _score(a, terms, q)
            if score > 0:
                scored.append((score, a))
        scored.sort(key=lambda t: (-t[0], t[1].id))
        return [a for _, a in scored[:k]]

    def stats(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for a in self.assets:
            out[a.cat or "other"] = out.get(a.cat or "other", 0) + 1
        return dict(sorted(out.items()))


def _score(a: Asset, terms: list[str], q: str) -> float:
    slug = a.id.lower()
    zh = a.zh.lower()
    en = a.en.lower()
    tags = " ".join(a.tags).lower()
    score = 0.0
    for t in terms:
        if t in zh or t in en:
            score += 6.0
        if t in tags:
            score += 3.0
        if t in slug:
            score += 2.5
            if re.search(rf"(^|-){re.escape(t)}(-|$)", slug):
                score += 2.0
        if zh.startswith(t) or en.startswith(t):
            score += 2.0
    # whole-phrase bonus
    if q and (q in zh or q in en):
        score += 5.0
    return score


@lru_cache(maxsize=1)
def catalog() -> Catalog:
    return Catalog()


# ------------------------------------------------------------------ render

def _svg_to_image(svg_path: Path, px: int) -> Image.Image:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    import fitz  # PyMuPDF

    drawing = svg2rlg(str(svg_path))
    if drawing is None:
        raise ValueError(f"could not parse svg: {svg_path}")
    buf = io.BytesIO()
    renderPDF.drawToFile(drawing, buf, "a")
    buf.seek(0)
    doc = fitz.open(stream=buf.getvalue(), filetype="pdf")
    try:
        page = doc[0]
        scale = px / max(page.rect.width, page.rect.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=True)
        img = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    finally:
        doc.close()
    return img


def _flatten_tint(img: Image.Image, colour: str) -> Image.Image:
    from .palette import rgb

    r, g, b = rgb(colour)
    alpha = img.getchannel("A")
    solid = Image.new("RGBA", img.size, (r, g, b, 255))
    solid.putalpha(alpha)
    return solid


def png(asset_id: str, px: int = 900, *, tint: str | None = None,
        cat: Catalog | None = None) -> Path:
    """Rasterise an asset to a cached transparent PNG; returns the path."""
    cat = cat or catalog()
    a = cat.get(asset_id)
    CACHE.mkdir(parents=True, exist_ok=True)
    key = a.id.replace("/", "__") + (f"__t{tint.lstrip('#')}" if tint else "")
    out = CACHE / f"{key}@{px}.png"
    if out.exists():
        return out
    img = _svg_to_image(a.path, px)
    if tint:
        img = _flatten_tint(img, tint)
    img.save(out)
    return out


def image(asset_id: str, px: int = 900, *, tint: str | None = None) -> Image.Image:
    return Image.open(png(asset_id, px, tint=tint)).convert("RGBA")


def fit_box(iw: int, ih: int, w: float, h: float, *, pad: float = 0.0
            ) -> tuple[float, float]:
    """Aspect-preserving (w, h) inside a w x h box, with optional inner pad."""
    w = max(0.1, w - 2 * pad)
    h = max(0.1, h - 2 * pad)
    scale = min(w / iw, h / ih)
    return iw * scale, ih * scale


# ------------------------------------------------------------------ sheet

def contact_sheet(assets: list[Asset], out: Path, *, cols: int = 6,
                  cell_px: int = 220, label: bool = True) -> Path:
    """Grid contact sheet with ids + names, for visual candidate review."""
    if not assets:
        raise ValueError("no assets")
    rows = (len(assets) + cols - 1) // cols
    pad = 10
    lab_h = 46 if label else 0
    W = cols * cell_px + (cols + 1) * pad
    H = rows * (cell_px + lab_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        f_name = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 15)
        f_id = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 12)
        f_cjk = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 14)
    except Exception:  # pragma: no cover
        f_name = f_id = f_cjk = ImageFont.load_default()
    for i, a in enumerate(assets):
        r, c = divmod(i, cols)
        x = pad + c * (cell_px + pad)
        y = pad + r * (cell_px + lab_h + pad)
        try:
            img = image(a.id, cell_px - 8)
        except Exception:
            draw.rectangle([x, y, x + cell_px, y + cell_px], outline="red")
            continue
        iw, ih = img.size
        s = min((cell_px - 10) / iw, (cell_px - 10) / ih)
        img = img.resize((max(1, int(iw * s)), max(1, int(ih * s))), Image.LANCZOS)
        sheet.paste(img, (x + (cell_px - img.width) // 2,
                          y + (cell_px - img.height) // 2), img)
        if label:
            name = a.en or a.zh
            draw.text((x + 4, y + cell_px + 3), name[:34], font=f_name, fill="#16222b")
            draw.text((x + 4, y + cell_px + 21), a.slug[:40], font=f_id, fill="#76879a")
            if a.zh and a.zh != name:
                draw.text((x + cell_px - 70, y + cell_px + 3), a.zh[:8], font=f_cjk,
                          fill="#455766")
    sheet.save(out)
    return out


# ------------------------------------------------------------------ CLI

def _main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not argv:
        print(__doc__)
        return 0
    cmd = argv[0]
    cat = catalog()
    if cmd == "stats":
        print(f"{len(cat.assets)} assets in {ASSETS / 'index.json'}")
        for k, v in cat.stats().items():
            print(f"  {k:<28} {v:>5}")
        return 0
    if cmd in ("search", "sheet"):
        q = argv[1] if len(argv) > 1 else ""
        k = 12
        out = None
        args = argv[2:]
        i = 0
        while i < len(args):
            if args[i] in ("-k", "--k"):
                k = int(args[i + 1]); i += 2
            elif args[i].endswith(".png"):
                out = Path(args[i]); i += 1
            else:
                i += 1
        hits = cat.search(q, k=k)
        for a in hits:
            print(f"{a.id}\n    {a.zh} / {a.en}   series={a.series} fmt={a.fmt} "
                  f"lic={a.license} tags={','.join(a.tags[:6])}")
        if out:
            contact_sheet(hits, out)
            print(f"\nsheet -> {out}")
        return 0
    if cmd == "info":
        for arg in argv[1:]:
            a = cat.require(arg)
            print(f"id         : {a.id}")
            print(f"name       : {a.zh}  /  {a.en}")
            print(f"category   : {a.cat}")
            print(f"series/fmt : {a.series} / {a.fmt}")
            print(f"licence    : {a.license}")
            print(f"attribution: {a.attribution}")
            print(f"tags       : {', '.join(a.tags)}")
            print(f"file       : {a.path}")
            print()
        return 0
    print(f"unknown command {cmd!r}")
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
