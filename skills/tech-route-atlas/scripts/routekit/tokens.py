"""Design tokens for publication-grade technical-route figures.

Every number here is in millimetres (geometry) or points (type / stroke).
The defaults are calibrated against 180 mm double-column and 85 mm
single-column journal widths, so a figure built with the defaults is
print-correct without rescaling.

Import convention::

    from routekit.tokens import T, S, R, G, DPI
"""
from __future__ import annotations

# ---------------------------------------------------------------- type scale

class T:
    """Type scale (points). Journal figures live in 5-9 pt; PPT decks 9-14 pt."""
    micro = 4.5      # panel letters, units, axis ticks (print only)
    caption = 5.5    # secondary captions under icons
    small = 6.0      # dense annotations, legends
    body = 7.0       # default label text
    sub = 8.0        # emphasis labels inside a card
    head = 9.0       # sub-panel headings
    panel = 9.5      # zone / section headers
    title = 12.0     # figure title
    hero = 16.0      # graphical-abstract claim line

    # deck variants (wider figures shown on screen)
    deck_body = 10.0
    deck_head = 12.0
    deck_title = 18.0


# ---------------------------------------------------------------- strokes

class S:
    """Stroke widths (points)."""
    hair = 0.4       # internal grid, tick marks
    thin = 0.6       # card borders, light connectors
    base = 0.8       # default border / arrow
    bold = 1.1       # emphasis border, primary flow arrow
    heavy = 1.6      # block arrow outline, figure frame
    rule = 0.9       # section divider rule


# ---------------------------------------------------------------- radii

class R:
    """Corner radii (mm). Radius must stay <= half the short side."""
    chip = 0.9
    card = 1.4
    zone = 1.8
    pill = 99.0      # clamps to a stadium


# ---------------------------------------------------------------- spacing

class G:
    """Layout gutters (mm)."""
    xxs = 0.8
    xs = 1.2
    s = 1.8
    m = 2.6
    l = 3.6
    xl = 5.0
    xxl = 7.0


# ---------------------------------------------------------------- canvas

class CANVAS:
    """Named canvases (w_mm, h_mm)."""
    double_column = (180.0, 110.0)
    single_column = (85.0, 90.0)
    full_page = (180.0, 235.0)
    slide_16x9 = (254.0, 142.9)
    slide_4x3 = (203.2, 152.4)
    graphical_abstract = (120.0, 60.0)
    poster_band = (300.0, 80.0)


# ---------------------------------------------------------------- output

class DPI:
    """Raster export targets."""
    print = 600        # journals: 300 min, 600 preferred for line art
    review = 150       # fast visual review
    deck = 220         # 16:9 deck images
    web = 96


# ---------------------------------------------------------------- helpers

MM_PER_INCH = 25.4


def pt_to_mm(pt: float) -> float:
    return pt * MM_PER_INCH / 72.0


def mm_to_pt(mm: float) -> float:
    return mm * 72.0 / MM_PER_INCH


def line_height_mm(pt: float, spacing: float = 1.0) -> float:
    """Approximate rendered line height for a given point size."""
    return pt_to_mm(pt) * 1.32 * spacing
