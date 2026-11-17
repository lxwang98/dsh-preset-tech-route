"""Pre-flight checks: catch the mistakes that ruin a printed figure.

Two passes:

* `static_report(canvas)` — runs before the file is even saved. Uses the
  recorded notes + FreeType metrics, so it catches text that only *just*
  fits, boxes that slipped off the canvas, missing icons, colliding labels
  and figures that are too sparse or too crowded.
* `export.com_audit(pptx)` — after export, asks PowerPoint for the real text
  bounds. That is the ground truth; the static pass exists to keep the
  iteration loop short (no file round-trips).

Everything returns plain dicts so a caller (agent or human) can print or
filter them.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .layout import Box
from .measure import text_fits
from .tokens import T

PRINT_MIN_PT = 5.0      # below this a label is unreadable at 1:1 in print
DECK_MIN_PT = 5.5  # type inside a figure that will be placed on a 16:9 slide       # below this it is unreadable when projected
TRIM_MM = 2.0           # keep content this far from the canvas edge


@dataclass
class Issue:
    level: str          # "error" | "warn" | "note"
    code: str
    detail: str
    where: str = ""

    def as_dict(self) -> dict:
        return {"level": self.level, "code": self.code, "detail": self.detail,
                "where": self.where}


def _overlap(a: Box, b: Box) -> float:
    w = min(a.x2, b.x2) - max(a.x, b.x)
    h = min(a.y2, b.y2) - max(a.y, b.y)
    if w <= 0 or h <= 0:
        return 0.0
    inter = w * h
    return inter / max(1e-6, min(a.area, b.area))


def static_report(canvas, *, mode: str = "print") -> list[Issue]:
    min_pt = DECK_MIN_PT if mode == "deck" else PRINT_MIN_PT
    out: list[Issue] = []
    frame = canvas.frame

    # 1. canvas bounds + trim
    for n in canvas.notes:
        b = n.box
        if b.x < -0.01 or b.y < -0.01 or b.x2 > canvas.w + 0.01 or b.y2 > canvas.h + 0.01:
            out.append(Issue("error", "off-canvas",
                             f"{n.kind} at {b.as_tuple()} exceeds canvas "
                             f"{canvas.w}x{canvas.h}", n.text[:40]))
        elif n.kind in ("text", "icon"):
            m = min(b.x, b.y, canvas.w - b.x2, canvas.h - b.y2)
            if m < TRIM_MM - 0.01:
                out.append(Issue("warn", "trim-margin",
                                 f"{n.kind} only {m:.1f} mm from the edge "
                                 f"(want >={TRIM_MM})", n.text[:40]))

    # 2. text size + real fit
    for n in canvas.notes:
        if n.kind != "text":
            continue
        if n.size and n.size < min_pt - 0.01:
            out.append(Issue("warn", "small-text",
                             f"{n.size:.1f} pt < {min_pt} pt readable floor",
                             n.text[:40]))
        if n.size and not text_fits(n.text, w_mm=n.box.w, h_mm=n.box.h, pt=n.size,
                                    font=n.font):
            out.append(Issue("error", "text-overflow",
                             f"{n.size:.1f} pt does not fit {n.box.w:.1f}x"
                             f"{n.box.h:.1f} mm", n.text[:40]))

    # 3. label collisions (text vs text, different boxes)
    texts = [n for n in canvas.notes if n.kind == "text" and n.text.strip()]
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i], texts[j]
            if a.text == b.text:
                continue
            ov = _overlap(a.box, b.box)
            if ov > 0.55:
                out.append(Issue("warn", "label-collision",
                                 f"text boxes overlap {ov:.0%}",
                                 f"{a.text[:20]!r} / {b.text[:20]!r}"))

    # 4. missing icons
    for w in canvas.warnings:
        out.append(Issue("error", "icon", w))

    # 5. composition heuristics
    kinds: dict[str, int] = {}
    for n in canvas.notes:
        kinds[n.kind] = kinds.get(n.kind, 0) + 1
    if kinds.get("icon", 0) == 0:
        out.append(Issue("warn", "no-icons",
                         "no catalogue assets placed — a route diagram without "
                         "figurative elements reads as a text flowchart"))
    if kinds.get("text", 0) > 90 and canvas.frame.area < 200 * 120:
        out.append(Issue("note", "dense",
                         f"{kinds['text']} text boxes on a "
                         f"{canvas.w:.0f}x{canvas.h:.0f} mm canvas"))
    if not canvas.notes:
        out.append(Issue("error", "empty", "nothing was drawn"))

    return out


def format_report(issues: list[Issue], *, limit: int = 40) -> str:
    if not issues:
        return "OK — no issues found"
    order = {"error": 0, "warn": 1, "note": 2}
    issues = sorted(issues, key=lambda i: (order.get(i.level, 3), i.code))
    lines = [f"{sum(1 for i in issues if i.level == 'error')} errors, "
             f"{sum(1 for i in issues if i.level == 'warn')} warnings, "
             f"{sum(1 for i in issues if i.level == 'note')} notes"]
    for i in issues[:limit]:
        tag = {"error": "E", "warn": "W", "note": "N"}.get(i.level, "?")
        where = f"  [{i.where}]" if i.where else ""
        lines.append(f"  {tag} {i.code}: {i.detail}{where}")
    if len(issues) > limit:
        lines.append(f"  … {len(issues) - limit} more")
    return "\n".join(lines)


def design_check(canvas, palette) -> list[str]:
    """Palette-level sanity: contrast of the text roles on the washes used."""
    from .palette import contrast

    notes: list[str] = []
    for i in range(min(len(palette.zones), 6)):
        c = contrast(palette.ink, palette.zones[i])
        if c < 7.0:
            notes.append(f"zone {i} wash contrast ink/wash = {c:.1f} (<7)")
    if contrast(palette.ink2, palette.paper) < 7.0:
        notes.append("secondary ink on paper below 7:1")
    return notes


__all__ = ["Issue", "static_report", "format_report", "design_check",
           "PRINT_MIN_PT", "DECK_MIN_PT"]
