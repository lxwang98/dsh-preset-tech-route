"""Fetch the public SciDraw catalogue into ``assets/custom/scidraw``.

Usage:
    python tools/fetch_scidraw.py [--out DIR] [--limit N] [--workers 12]

SciDraw (https://scidraw.io) exposes a public paginated JSON API at
``/api/v1/drawings/``.  We keep the original author, DOI and licence for every
asset in ``metadata.json``; CC BY 4.0 requires attribution, CC0 does not but we
still record the source.  The script is idempotent: existing non-empty files
are skipped, so it can be re-run to repair a partial download.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import time
import urllib.request
from pathlib import Path

API = "https://scidraw.io/api/v1/drawings/"
UA = "Mozilla/5.0 (compatible; dsh-preset-tech-route/1.1)"


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def catalogue(limit: int | None = None) -> list[dict]:
    items: list[dict] = []
    url: str | None = API
    while url:
        page = get_json(url)
        items.extend(page.get("results", []))
        if limit and len(items) >= limit:
            return items[:limit]
        url = page.get("next")
    return items


def ext_for(item: dict) -> str:
    return {
        "svg": "svg",
        "png": "png",
        "jpeg": "jpg",
        "jpg": "jpg",
    }.get(str(item.get("image_type", "")).lower(), "svg")


def download(item: dict, root: Path) -> tuple[str, bool, str]:
    cat = item.get("category_slug") or "other"
    slug = item.get("slug") or str(item.get("id"))
    out = root / cat / f"{slug}.{ext_for(item)}"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 20:
        return str(item.get("id")), True, str(out)
    url = item.get("image_url")
    if not url:
        return str(item.get("id")), False, "missing image_url"
    last = ""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            if len(data) < 20:
                raise ValueError("short response")
            out.write_bytes(data)
            return str(item.get("id")), True, str(out)
        except Exception as exc:  # noqa: BLE001 - report per-asset failures
            last = f"{url} :: {exc}"
            time.sleep(1.5 * (attempt + 1))
    return str(item.get("id")), False, last


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("assets/custom/scidraw"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    items = catalogue(args.limit)
    print(f"catalogue: {len(items)} records")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(lambda it: download(it, args.out), items))
    bad = [r for r in results if not r[1]]
    print(f"downloaded: {len(results) - len(bad)}  failed: {len(bad)}")
    for r in bad[:10]:
        print("FAIL", r[0], r[2])
    for it in items:
        it["local_file"] = (
            f"custom/scidraw/{it.get('category_slug') or 'other'}/"
            f"{it.get('slug')}.{ext_for(it)}"
        )
    (args.out / "metadata.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("metadata:", args.out / "metadata.json")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
