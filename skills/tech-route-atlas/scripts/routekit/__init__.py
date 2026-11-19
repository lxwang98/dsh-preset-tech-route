"""routekit — build publication-grade technical-route figures as PPTX.

The kit is deliberately small: five modules and no exotic dependencies.

    tokens    type/stroke/radius/gutter scales, canvas presets, DPI targets
    palette   six journal colour systems with semantic roles
    measure   real font metrics (FreeType) for pre-flight text fitting
    layout    Box geometry: split, flow, anchor, ladder
    icons     2 800+ SVG assets, searchable, rasterised on demand
    canvas    python-pptx primitives that speak millimetres
    export    PowerPoint -> PNG / PDF / SVG, plus COM text-bound audit
    audit     static pre-flight (overflow, collisions, margins, density)
    miniplot  matplotlib insets themed to the active palette
    iso      isometric primitives (block / layers / plane) as editable polygons
    render3d plotly+kaleido offline 3D objects (sphere / cylinder / ball-and-stick) -> 600 dpi PNG

Typical script::

    from routekit import Canvas, Box, T, G, CANVAS
    c = Canvas(*CANVAS.double_column, palette="cell")
    inner = c.zone(Box(4, 4, 58, 34), "1 · Experimental design", acc=0)
    c.icon(Box(8, 12, 14, 14), "sciglyph/.../001-mouse")
    c.save("route.pptx")
    c.export("out", dpi=600)      # PNG + PDF via PowerPoint
"""
from __future__ import annotations

from .audit import Issue, design_check, format_report, static_report
from . import iso, render3d
from .canvas import Canvas, Note
from .layout import (Box, center_in, even_slots, grid, ladder, radial,
                     stack_left, stack_top)
from .palette import PALETTES, Palette, P, contrast, mix, shade, tint
from .tokens import CANVAS, DPI, G, R, S, T, line_height_mm, mm_to_pt, pt_to_mm

__version__ = "1.0.0"

__all__ = [
    "Canvas", "Note", "Box", "T", "S", "R", "G", "CANVAS", "DPI",
    "P", "PALETTES", "Palette", "tint", "shade", "mix", "contrast",
    "even_slots", "center_in", "stack_top", "stack_left", "grid", "ladder",
    "radial", "static_report", "format_report", "design_check", "Issue",
    "pt_to_mm", "mm_to_pt", "line_height_mm", "__version__",
]


def _export(self, out_dir, *, dpi: int = 600, stem: str | None = None, **kw):
    """Convenience: save + render in one call (keeps PowerPoint out of the tail)."""
    from .export import render

    d = self.save(Path(out_dir) / f"{stem or 'figure'}.pptx")
    return render(d, out_dir, dpi=dpi, stem=stem, **kw)


from pathlib import Path  # noqa: E402  (used by the helper above)

Canvas.export = _export  # type: ignore[attr-defined]


