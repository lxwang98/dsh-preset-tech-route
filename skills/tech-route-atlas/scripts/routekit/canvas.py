"""Canvas: a thin, typographic layer over python-pptx.

Everything is laid out in millimetres on a slide whose size equals the target
figure size, so 1 mm on the canvas is 1 mm on the printed page and font sizes
are true point sizes. Every primitive records what it placed in `Canvas.notes`
so `audit.py` can check overflow and collisions afterwards.

    c = Canvas(180, 110, palette="cell")
    c.zone(Box(4, 4, 40, 28), "1 · 试验设计")
    c.text(Box(5, 30, 38, 5), "全谷物黑米", size=T.caption)
    c.icon(Box(8, 10, 14, 14), "sciglyph/07-glassware-consumables/.../001-beaker")
    c.arrow((20, 40), (40, 40))
    c.save("route.pptx")
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Mm, Pt

from . import icons as _icons
from .layout import Box
from .measure import fit_paragraphs, has_cjk
from .palette import P, Palette, mix, rgb, tint
from .tokens import G, R, S, T, line_height_mm

ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT, "j": PP_ALIGN.JUSTIFY}
ANCHOR = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}


@dataclass
class Note:
    """One placed element, for the audit pass."""

    kind: str
    box: Box
    text: str = ""
    size: float = 0.0
    shape: object = None
    font: str = ""


class Canvas:
    def __init__(self, w: float, h: float, *, palette: str = "cell",
                 margin: float = 0.0, background: bool = True,
                 font: str = "Arial", cjk_font: str = "Microsoft YaHei",
                 title: str = ""):
        self.w, self.h = float(w), float(h)
        self.p: Palette = P(palette)
        self.font = font
        self.cjk_font = cjk_font
        self.notes: list[Note] = []
        self.warnings: list[str] = []
        self.title = title

        self.prs = Presentation()
        self.prs.slide_width = Mm(self.w)
        self.prs.slide_height = Mm(self.h)
        self.slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self.frame = Box(0, 0, self.w, self.h)
        self.bbox = self.frame.inner(margin) if margin else self.frame
        if background:
            self.bg(self.p.paper)

    # ------------------------------------------------------------ base
    def _font_for(self, s: str) -> str:
        return self.cjk_font if has_cjk(s) else self.font

    def _colour(self, c) -> RGBColor:
        if isinstance(c, RGBColor):
            return c
        return RGBColor(*rgb(c))

    def _style_line(self, shape, colour, lw, dash=None, head=None, tail=None,
                    alpha=None):
        ln = shape.line
        if colour is None:
            ln.fill.background()
            return
        ln.color.rgb = self._colour(colour)
        ln.width = Pt(lw)
        if dash:
            ln.dash_style = dash
        lnel = ln._get_or_add_ln()
        if alpha is not None:
            solid = lnel.find(qn("a:solidFill"))
            if solid is not None:
                clr = solid.find(qn("a:srgbClr"))
                if clr is not None:
                    el = clr.makeelement(qn("a:alpha"), {"val": str(int(alpha * 100000))})
                    clr.append(el)
        for tag, val in (("a:headEnd", head), ("a:tailEnd", tail)):
            if val:
                el = lnel.makeelement(qn(tag), {"type": val, "w": "med", "len": "med"})
                lnel.append(el)

    def _set_fill(self, shape, colour, alpha=None, grad=None):
        if colour is None:
            shape.fill.background()
            return
        shape.fill.solid()
        shape.fill.fore_color.rgb = self._colour(colour)
        if alpha is not None:
            spPr = shape._element.spPr
            for solid in spPr.iter(qn("a:solidFill")):
                clr = solid.find(qn("a:srgbClr"))
                if clr is not None and clr.find(qn("a:alpha")) is None:
                    clr.append(clr.makeelement(qn("a:alpha"),
                                               {"val": str(int(alpha * 100000))}))

    # ------------------------------------------------------------ shapes
    def bg(self, colour: str):
        s = self.slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                                        Mm(self.w), Mm(self.h))
        self._set_fill(s, colour)
        s.line.fill.background()
        s.shadow.inherit = False
        s.name = "bg"
        return s

    def rect(self, b: Box, *, fill=None, line=None, lw: float = S.base,
             radius: float | None = None, dash=None, shadow: bool = False,
             alpha: float | None = None, line_alpha: float | None = None,
             name: str = ""):
        kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
        s = self.slide.shapes.add_shape(kind, Mm(b.x), Mm(b.y), Mm(b.w), Mm(b.h))
        if radius:
            adj = min(0.5, radius / max(0.01, min(b.w, b.h)))
            try:
                s.adjustments[0] = adj
            except Exception:
                pass
        self._set_fill(s, fill, alpha)
        self._style_line(s, line, lw, dash, alpha=line_alpha)
        s.shadow.inherit = shadow
        s.name = name or "rect"
        return s

    def zone(self, b: Box, title: str = "", *, acc: int = 0, fill: bool = True,
             band: bool = True, pad: float = G.xs, radius: float = R.card,
             title_pt: float | None = None, edge: bool = True):
        """A numbered panel: tinted body + coloured title band.

        Returns the content Box (inside the band and padding).
        """
        body = self.p.zone(acc)
        if fill:
            self.rect(b, fill=body, line=None, radius=radius)
        if edge:
            self.rect(b, fill=None, line=self.p.zone_line(acc), lw=S.thin,
                      radius=radius)
        content = b
        if title:
            pt = title_pt or T.head
            lines = 1 if len(title) <= int(b.w / (pt * 0.16)) else 2
            hh = line_height_mm(pt) * lines + 2 * G.xxs
            head = Box(b.x, b.y, b.w, min(hh, b.h * 0.4))
            if band:
                self.rect(head, fill=self.p.zone_line(acc), line=None,
                          radius=radius)
                # square off the bottom so the band reads as a header
                self.rect(Box(head.x, head.cy, head.w, head.h / 2 + 0.2),
                          fill=self.p.zone_line(acc), line=None)
            self.text(head.inner(G.xxs), title, size=pt, bold=True,
                      colour=self.p.on(self.p.zone_line(acc)) if band else self.p.ink,
                      align="c")
            content = Box(b.x, head.y2, b.w, b.h - head.h)
        inner = content.inner(pad)
        return inner

    def band_header(self, b: Box, title: str, *, acc: int = 0, height: float = 7.0,
                    sub: str = ""):
        """Standalone coloured bar with centred title (used on top of a zone)."""
        head = Box(b.x, b.y, b.w, height)
        self.rect(head, fill=self.p.zone_line(acc), line=None, radius=R.card)
        self.text(head.inner(G.xxs, 0), title, size=T.head, bold=True,
                  colour=self.p.on(self.p.zone_line(acc)), align="c")
        if sub:
            self.text(Box(b.x, head.y2 + G.xxs, b.w, 4.2), sub, size=T.caption,
                      colour=self.p.ink2, align="c")
        return Box(b.x, head.y2, b.w, b.h - height)

    def text(self, b: Box, s: str, *, size: float | None = None, bold: bool = False,
             italic: bool = False, colour: str | None = None, align: str = "c",
             anchor: str = "m", font: str | None = None, spacing: float = 0.95,
             min_size: float = T.micro * 0.85, wrap: bool = True,
             line_spacing: float | None = None, margin: float = 0.0,
             autofit: bool = True, name: str = ""):
        """Place text; auto-shrinks to fit the box when `autofit`."""
        s = str(s)
        if not s:
            return None
        size = size or T.body
        fnt = font or self._font_for(s)
        paras = s.split("\n")
        lines: Sequence[str] = [s]
        if autofit:
            got = fit_paragraphs(paras, w_mm=max(0.5, b.w - 2 * margin),
                                 h_mm=max(0.5, b.h - 2 * margin), max_pt=size,
                                 min_pt=min(min_size, size), bold=bold, font=fnt,
                                 spacing=spacing, allow_wrap=wrap)
            size, lines = got
        elif wrap:
            from .measure import wrap_lines

            lines = []
            for seg in paras:
                lines.extend(wrap_lines(seg, (b.w - 2 * margin) * 72.0 / 25.4, size,
                                        bold=bold, font=fnt) or [seg])

        if size < min_size - 0.01:
            self.warnings.append(f"tiny text {size:.1f}pt in {b.as_tuple()} {s[:30]!r}")

        tb = self.slide.shapes.add_textbox(Mm(b.x + margin), Mm(b.y + margin),
                                           Mm(max(0.5, b.w - 2 * margin)),
                                           Mm(max(0.5, b.h - 2 * margin)))
        tf = tb.text_frame
        # we pre-wrap with real font metrics; letting PowerPoint re-wrap would
        # break every height decision made in this module
        tf.word_wrap = False
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = ANCHOR[anchor]
        tf.auto_size = None
        colour = colour or self.p.ink
        lsp = line_spacing if line_spacing is not None else (
            (size * spacing) / size if size else 0.95)
        for i, line in enumerate(lines):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.alignment = ALIGN.get(align, PP_ALIGN.CENTER)
            para.line_spacing = 0.92
            para.space_before = Pt(0)
            para.space_after = Pt(0)
            run = para.add_run()
            run.text = line
            f = run.font
            f.size = Pt(size)
            f.bold = bold
            f.italic = italic
            f.name = fnt
            f.color.rgb = self._colour(colour)
            rpr = run._r.get_or_add_rPr()
            for tag in ("a:ea", "a:cs"):
                el = rpr.find(qn(tag))
                if el is None:
                    el = rpr.makeelement(qn(tag), {})
                    rpr.append(el)
                el.set("typeface", fnt)
        tb.name = name or "text"
        self.notes.append(Note("text", b, s, size, tb, fnt))
        return tb

    # ------------------------------------------------------------ icons
    def icon(self, b: Box, asset: str, *, pad: float = 0.0, tint_colour: str | None = None,
             px: int = 1100, name: str = ""):
        """Place a catalogue asset, aspect-preserved and centred in `b`."""
        try:
            path = _icons.png(asset, px, tint=tint_colour)
        except Exception as exc:  # pragma: no cover - missing asset
            self.rect(b, fill=tint(self.p.signal_neg, 0.85), line=self.p.signal_neg,
                      lw=S.thin, radius=0.6)
            self.text(b, f"? {asset}", size=T.micro, colour=self.p.signal_neg)
            self.warnings.append(f"icon missing: {asset} ({exc})")
            return None
        from PIL import Image

        with Image.open(path) as im:
            iw, ih = im.size
        iw, ih = _icons.fit_box(iw, ih, b.w, b.h, pad=pad)
        x = b.x + (b.w - iw) / 2
        y = b.y + (b.h - ih) / 2
        pic = self.slide.shapes.add_picture(str(path), Mm(x), Mm(y), Mm(iw), Mm(ih))
        pic.name = name or Path(asset).name
        self.notes.append(Note("icon", Box(x, y, iw, ih), asset, 0, pic))
        return pic

    # ------------------------------------------------------------ motifs
    def chip(self, b: Box, s: str, *, acc: int = 0, size: float | None = None,
             mode: str = "fill", bold: bool = False, radius: float | None = None):
        fill = line = None
        if mode == "fill":
            fill = self.p.accent_soft(acc, 0.78)
            line = self.p.zone_line(acc)
            colour = self.p.ink
        elif mode == "solid":
            fill = self.p.zone_line(acc)
            colour = self.p.on(fill)
        elif mode == "wash":
            fill = self.p.wash
            line = self.p.rule
            colour = self.p.ink2
        else:  # outline
            line = self.p.zone_line(acc)
            colour = self.p.zone_line(acc)
        r = radius if radius is not None else min(b.h / 2, R.pill)
        self.rect(b, fill=fill, line=line, lw=S.thin, radius=r)
        return self.text(b.inner(0), s, size=size or (T.bold if bold else T.body),
                         bold=bold, colour=colour, align="c", anchor="m",
                         min_size=T.micro * 0.8)

    def badge(self, centre: tuple[float, float], n, *, r: float = 2.2,
              colour: str | None = None, text_colour: str | None = None):
        b = Box(centre[0] - r, centre[1] - r, 2 * r, 2 * r)
        col = colour or self.p.zone_line(0)
        self.rect(b, fill=col, line=None, radius=r)
        return self.text(b, str(n), size=T.caption, bold=True,
                         colour=text_colour or self.p.on(col), align="c")

    def arrow(self, p1: tuple[float, float], p2: tuple[float, float], *, colour=None,
              lw: float = S.bold, head: str = "triangle", dash=None,
              start: str | None = None, shrink: float = 0.0):
        """Straight arrow between two points (mm)."""
        x1, y1 = p1
        x2, y2 = p2
        if shrink:
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1.0
            ux, uy = dx / L, dy / L
            x1, y1 = x1 + ux * shrink, y1 + uy * shrink
            x2, y2 = x2 - ux * shrink, y2 - uy * shrink
        s = self.slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Mm(x1), Mm(y1),
                                            Mm(x2), Mm(y2))
        s.line.width = Pt(lw)
        s.line.color.rgb = self._colour(colour or self.p.ink2)
        if dash:
            s.line.dash_style = dash
        ln = s.line._get_or_add_ln()
        if head and head != "none":
            ln.append(ln.makeelement(qn("a:tailEnd"),
                                     {"type": head, "w": "med", "len": "med"}))
        if start and start != "none":
            ln.append(ln.makeelement(qn("a:headEnd"),
                                     {"type": start, "w": "med", "len": "med"}))
        s.name = "arrow"
        return s

    def route(self, pts: Sequence[tuple[float, float]], *, colour=None,
              lw: float = S.bold, head: str = "triangle", start: str | None = None,
              dash=None):
        """One continuous native shape through `pts` (mm).

        A single freeform keeps a dashed pattern continuous across bends and
        lets the user drag the whole route as one object — the difference
        between a figure that looks drawn and one that looks stitched.
        """
        pts = [(float(x), float(y)) for x, y in pts]
        if len(pts) < 2:
            raise ValueError("route needs >= 2 points")
        builder = self.slide.shapes.build_freeform(Mm(pts[0][0]), Mm(pts[0][1]))
        builder.add_line_segments([(Mm(x), Mm(y)) for x, y in pts[1:]], close=False)
        s = builder.convert_to_shape()
        s.fill.background()
        s.line.width = Pt(lw)
        s.line.color.rgb = self._colour(colour or self.p.ink2)
        if dash:
            s.line.dash_style = dash
        ln = s.line._get_or_add_ln()
        if head and head != "none":
            ln.append(ln.makeelement(qn("a:tailEnd"),
                                     {"type": head, "w": "med", "len": "med"}))
        if start and start != "none":
            ln.append(ln.makeelement(qn("a:headEnd"),
                                     {"type": start, "w": "med", "len": "med"}))
        s.name = "route"
        return s

    def connector_path(self, pts: Sequence[tuple[float, float]], *, colour=None,
                       lw: float = S.bold, head: str = "triangle", dash=None):
        """Orthogonal polyline as one shape (see `route`)."""
        return self.route(pts, colour=colour, lw=lw, head=head, dash=dash)

    def elbow(self, p1, p2, *, mode: str = "hv", colour=None, lw: float = S.bold,
              head: str = "triangle", dash=None):
        """Two-segment connector as one native elbow shape ('hv' or 'vh')."""
        (x1, y1), (x2, y2) = p1, p2
        s = self.slide.shapes.add_connector(MSO_CONNECTOR.ELBOW, Mm(x1), Mm(y1),
                                            Mm(x2), Mm(y2))
        s.line.width = Pt(lw)
        s.line.color.rgb = self._colour(colour or self.p.ink2)
        if dash:
            s.line.dash_style = dash
        ln = s.line._get_or_add_ln()
        if head and head != "none":
            ln.append(ln.makeelement(qn("a:tailEnd"),
                                     {"type": head, "w": "med", "len": "med"}))
        s.name = "elbow"
        return s

    def block_arrow(self, b: Box, direction: str = "right", *, acc: int = 0,
                    label: str = "", size: float | None = None):
        shape = {"right": MSO_SHAPE.RIGHT_ARROW, "left": MSO_SHAPE.LEFT_ARROW,
                 "down": MSO_SHAPE.DOWN_ARROW, "up": MSO_SHAPE.UP_ARROW}[direction]
        s = self.slide.shapes.add_shape(shape, Mm(b.x), Mm(b.y), Mm(b.w), Mm(b.h))
        col = self.p.zone_line(acc)
        self._set_fill(s, col)
        s.line.fill.background()
        s.shadow.inherit = False
        if label:
            self.text(b, label, size=size or T.caption, bold=True,
                      colour=self.p.on(col), align="c")
        return s

    def chevron(self, b: Box, label: str, *, acc: int = 0, size: float | None = None,
                first: bool = False, last: bool = False):
        shape = (MSO_SHAPE.PENTAGON if first else
                 MSO_SHAPE.CHEVRON if not last else MSO_SHAPE.CHEVRON)
        s = self.slide.shapes.add_shape(shape, Mm(b.x), Mm(b.y), Mm(b.w), Mm(b.h))
        col = self.p.zone_line(acc)
        self._set_fill(s, col)
        s.line.fill.background()
        s.shadow.inherit = False
        self.text(b.inner(G.xxs, 0), label, size=size or T.caption, bold=True,
                  colour=self.p.on(col), align="c")
        return s

    def divider(self, x1, y1, x2, y2, *, colour=None, lw: float = S.rule, dash=None):
        return self.arrow((x1, y1), (x2, y2), colour=colour or self.p.rule, lw=lw,
                          head="none", dash=dash)

    def number_bar(self, b: Box, n: int, *, acc: int = 0, size: float | None = None):
        """Small numbered pill used to order steps."""
        self.badge((b.x + b.h / 2, b.cy), n, r=b.h / 2, colour=self.p.zone_line(acc))

    # ------------------------------------------------------------ legend
    def legend(self, b: Box, items: Iterable[tuple[str, str]], *, size: float | None = None,
               marker: str = "line", cols: int | None = None, gap: float = G.s):
        items = list(items)
        cols = cols or len(items)
        rows = math.ceil(len(items) / cols)
        cells = [row for row in zip(*[c.cols(cols, gap) for c in b.rows(rows, gap)])]
        flat = [c for row in cells for c in row]
        for cell, (label, colour) in zip(flat, items):
            mk = Box(cell.x, cell.cy - 0.7, 6.0, 1.4)
            if marker == "line":
                self.rect(mk, fill=colour, line=None, radius=0.3)
            elif marker == "dot":
                d = min(cell.h, 3.2)
                self.rect(Box(cell.x, cell.cy - d / 2, d, d), fill=colour, line=None,
                          radius=d)
            elif marker == "box":
                self.rect(mk, fill=tint(colour, 0.8), line=colour, lw=S.thin,
                          radius=0.4)
            self.text(Box(cell.x + 7.0, cell.y, cell.w - 7.0, cell.h), label,
                      size=size or T.caption, colour=self.p.ink2, align="l")
        return flat

    # ------------------------------------------------------------ plots
    def plot(self, b: Box, draw, *, dpi: int = 300, transparent: bool = False,
             cache_dir: str | Path | None = None, name: str = "plot"):
        """Render a matplotlib figure (mm-sized) and place it in `b`.

        `draw(fig, ax)` is called with a figure exactly `b` mm in size. The
        saved image uses `bbox_inches="tight"`, so tick labels and axis labels
        are never clipped; the result is letterboxed inside `b` keeping its
        aspect ratio.
        """
        import hashlib
        import io

        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from PIL import Image

        w_in, h_in = b.w / 25.4, b.h / 25.4
        fig = plt.figure(figsize=(w_in, h_in), dpi=dpi)
        key = hashlib.sha1(f"{b.as_tuple()}{dpi}{name}{id(draw)}".encode()).hexdigest()[:10]
        base = Path(cache_dir or Path.cwd() / ".routekit_plots")
        base.mkdir(parents=True, exist_ok=True)
        out = base / f"{name}-{key}.png"
        try:
            draw(fig)
            fig.savefig(out, dpi=dpi, transparent=transparent,
                        bbox_inches="tight", pad_inches=0.012)
        finally:
            plt.close(fig)

        with Image.open(out) as im:
            iw, ih = im.size
        aspect = iw / max(ih, 1)
        box_aspect = b.w / max(b.h, 0.01)
        if aspect > box_aspect:          # wider than the slot: fit width
            w, h = b.w, b.w / aspect
        else:                            # taller: fit height
            h, w = b.h, b.h * aspect
        x = b.x + (b.w - w) / 2
        y = b.y + (b.h - h) / 2
        pic = self.slide.shapes.add_picture(str(out), Mm(x), Mm(y), Mm(w), Mm(h))
        pic.name = name
        self.notes.append(Note("plot", Box(x, y, w, h), name, 0, pic))
        return pic

    # ------------------------------------------------------------ output
    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(path))
        return path

    def summary(self) -> dict:
        kinds: dict[str, int] = {}
        for n in self.notes:
            kinds[n.kind] = kinds.get(n.kind, 0) + 1
        return {"canvas_mm": (self.w, self.h), "palette": self.p.key,
                "elements": kinds, "warnings": self.warnings}

    # convenience
    def mm_to_pt(self, mm: float) -> float:
        return mm * 72 / 25.4

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Canvas {self.w}x{self.h}mm palette={self.p.key} notes={len(self.notes)}>"


__all__ = ["Canvas", "Note"]
