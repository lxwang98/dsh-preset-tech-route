"""Journal colour systems.

A palette is a *semantic* system, not a bag of hex codes: every figure built
with routekit derives its text, rules, zone washes, accent bars and arrow
colours from the same six roles, which is what makes a set of figures look
like they came from one paper.

Roles
-----
ink / ink2 / ink3   text hierarchy, darkest to lightest
rule                hairlines, table borders, axis lines
paper / wash        page white / faintest background tint
zones               pastel panel washes (fill) used for section containers
zone_lines          the matching mid-tone stroke for each wash
accents             saturated series colours (groups, arms, phases)
link                connector / arrow colour (never pure black)
signal_pos/neg      up/down, increase/decrease, benefit/harm

Usage
-----
    from routekit.palette import P
    p = P("cell")
    p.ink, p.zone(2), p.accent(0), p.link
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


# ------------------------------------------------------------------ colours

def hx(c: str) -> str:
    """Normalise '#RGB' / 'RRGGBB' / '#rrggbb' to '#rrggbb'."""
    c = c.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        raise ValueError(f"bad colour {c!r}")
    return "#" + c.lower()


def rgb(c: str) -> tuple[int, int, int]:
    c = hx(c)
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


def from_rgb(rgb_: Sequence[float]) -> str:
    r, g, b = (max(0, min(255, int(round(v)))) for v in rgb_[:3])
    return f"#{r:02x}{g:02x}{b:02x}"


def mix(a: str, b: str, t: float) -> str:
    """Linear blend: t=0 -> a, t=1 -> b."""
    ra, ga, ba = rgb(a)
    rb, gb, bb = rgb(b)
    return from_rgb((ra + (rb - ra) * t, ga + (gb - ga) * t, ba + (bb - ba) * t))


def tint(c: str, k: float) -> str:
    """k in [0,1]: 0 = unchanged, 1 = white."""
    return mix(c, "#ffffff", k)


def shade(c: str, k: float) -> str:
    """k in [0,1]: 0 = unchanged, 1 = near-black."""
    return mix(c, "#101418", k)


def luminance(c: str) -> float:
    """WCAG relative luminance."""
    def chan(v: float) -> float:
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(c)
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def readable_on(bg: str, dark: str = "#16222b", light: str = "#ffffff") -> str:
    """Pick the text colour with better contrast against `bg`."""
    return dark if contrast(bg, dark) >= contrast(bg, light) else light


# ------------------------------------------------------------------ palette

@dataclass(frozen=True)
class Palette:
    key: str
    name: str
    note: str
    ink: str
    ink2: str
    ink3: str
    rule: str
    paper: str
    wash: str
    zones: tuple[str, ...]
    zone_lines: tuple[str, ...]
    accents: tuple[str, ...]
    link: str
    signal_pos: str = "#2f7d55"
    signal_neg: str = "#b03a48"
    muted: str = "#8c9aa5"

    # -- zone helpers -------------------------------------------------
    def zone(self, i: int) -> str:
        return self.zones[i % len(self.zones)]

    def zone_line(self, i: int) -> str:
        return self.zone_lines[i % len(self.zone_lines)]

    def zone_pair(self, i: int) -> tuple[str, str]:
        return self.zone(i), self.zone_line(i)

    # -- accent helpers -----------------------------------------------
    def accent(self, i: int) -> str:
        return self.accents[i % len(self.accents)]

    def series(self, n: int) -> list[str]:
        return [self.accent(i) for i in range(n)]

    def accent_soft(self, i: int, k: float = 0.78) -> str:
        return tint(self.accent(i), k)

    # -- ramp for ordered phases --------------------------------------
    def ramp(self, n: int, base: str | None = None, lo: float = 0.15, hi: float = 0.85) -> list[str]:
        base = base or self.accents[0]
        if n == 1:
            return [base]
        return [tint(base, lo + (hi - lo) * i / (n - 1)) for i in range(n)]

    # -- text on a wash ------------------------------------------------
    def on(self, bg: str) -> str:
        return readable_on(bg, self.ink, self.paper)


# ------------------------------------------------------------------ systems

_CELL = Palette(
    key="cell",
    name="Cell / modern biomedical",
    note="Cool blue-dominant, warm coral + gold counterpoints. The default for "
         "multi-panel methodology figures and graphical abstracts.",
    ink="#16222b", ink2="#455766", ink3="#76879a", rule="#cbd8e2",
    paper="#ffffff", wash="#f7fafc",
    zones=("#e9f2fa", "#eaf4ec", "#fdf1e6", "#fbe9ec", "#f1edf9", "#f0f4f7"),
    zone_lines=("#b9d2e7", "#bcd9c2", "#eccaa6", "#eec3c9", "#d2c8e8", "#c9d6df"),
    accents=("#2e6e9e", "#4c8c57", "#c98043", "#b4515f", "#6c5aa0", "#587f96"),
    link="#54646f", signal_pos="#2f7d55", signal_neg="#b03a48", muted="#8c9aa5",
)

_NATURE = Palette(
    key="nature",
    name="Okabe-Ito (Nature-safe)",
    note="Colour-blind-safe base set (Okabe & Ito 2008) on neutral greys. "
         "Choose this whenever the figure must survive greyscale printing.",
    ink="#1c1c1c", ink2="#4a4a4a", ink3="#7d7d7d", rule="#d0d0d0",
    paper="#ffffff", wash="#f7f7f6",
    zones=("#e6eef4", "#e7f1e9", "#fdf0e2", "#f6e9ef", "#eeeaf6", "#eef0f1"),
    zone_lines=("#b3cadb", "#b7d3bd", "#e8c7a2", "#dfbac8", "#cbc2e0", "#c6ccd0"),
    accents=("#0072b2", "#009e73", "#d55e00", "#cc79a7", "#56b4e9", "#e69f00"),
    link="#3d4a52", signal_pos="#009e73", signal_neg="#d55e00", muted="#8a8a8a",
)

_SCIENCE = Palette(
    key="science",
    name="Science / crisp editorial",
    note="Higher chroma, denser ink, sharp rules. Reads well at small print "
         "size and in slide projection.",
    ink="#111c24", ink2="#3f515e", ink3="#6f808c", rule="#c3d0d9",
    paper="#ffffff", wash="#f8fafb",
    zones=("#e4eff4", "#e8f2e6", "#fcefe0", "#fae7ea", "#ecebf6", "#edf1f3"),
    zone_lines=("#aecdd9", "#b6d5b2", "#edc79c", "#e9bcc4", "#c9c5e3", "#c2ced6"),
    accents=("#1b6c8c", "#2e8b57", "#e07b39", "#b03a5b", "#5b7db1", "#8a7a3f"),
    link="#33454f", signal_pos="#2e8b57", signal_neg="#b03a5b", muted="#87949c",
)

_LANCET = Palette(
    key="lancet",
    name="Lancet / clinical",
    note="Deep navy + brick red + sage, low chroma. Good for clinical trial "
         "schematics, CONSORT-style flows and epidemiology.",
    ink="#0f2430", ink2="#3a4f5c", ink3="#6b7d88", rule="#c5d2d9",
    paper="#ffffff", wash="#f7f9fa",
    zones=("#e5eef4", "#e9f0e9", "#f9ece4", "#f6e6e5", "#ecebf3", "#eef1f2"),
    zone_lines=("#b0c8d6", "#b9cdb6", "#e4bfa8", "#e0b9b6", "#cbc6dd", "#c8d2d7"),
    accents=("#0b3c5d", "#9e2a2b", "#2e7d5b", "#c8a165", "#5d7f96", "#7b5e8a"),
    link="#2f4450", signal_pos="#2e7d5b", signal_neg="#9e2a2b", muted="#8697a1",
)

_BIORENDER = Palette(
    key="biorender",
    name="Soft pastel (BioRender-like)",
    note="Light washes, low-contrast borders, generous rounding. Closest to "
         "the look of hand-assembled biomedical schematics; keep text at "
         ">=7 pt because contrast is deliberately soft.",
    ink="#22313f", ink2="#4d6172", ink3="#7e8f9e", rule="#d5e0e8",
    paper="#ffffff", wash="#fafcfd",
    zones=("#dcebfb", "#ddeedc", "#fdecd8", "#fbe3e7", "#ede7f6", "#eef3f6"),
    zone_lines=("#a9c9e6", "#aed6ad", "#f0c9a0", "#efbcc5", "#c9bde4", "#c3d2da"),
    accents=("#4a7fb5", "#5c9e62", "#d08a4a", "#c4697a", "#7b6ba8", "#5f8f9e"),
    link="#65788a", signal_pos="#5c9e62", signal_neg="#c4697a", muted="#93a3af",
)

_MONO = Palette(
    key="mono",
    name="Greyscale (B/W print)",
    note="For figures that must survive a photocopier or a black-only print "
         "run. Distinguish by value + hatching, never by hue.",
    ink="#101010", ink2="#3a3a3a", ink3="#6e6e6e", rule="#c9c9c9",
    paper="#ffffff", wash="#f6f6f6",
    zones=("#ececec", "#f1f1f1", "#e6e6e6", "#f4f4f4", "#e9e9e9", "#f0f0f0"),
    zone_lines=("#b8b8b8", "#c4c4c4", "#a8a8a8", "#cccccc", "#bdbdbd", "#c0c0c0"),
    accents=("#1a1a1a", "#4d4d4d", "#7a7a7a", "#a3a3a3", "#c4c4c4", "#8f8f8f"),
    link="#2b2b2b", signal_pos="#2b2b2b", signal_neg="#6a6a6a", muted="#8f8f8f",
)

PALETTES: dict[str, Palette] = {
    p.key: p for p in (_CELL, _NATURE, _SCIENCE, _LANCET, _BIORENDER, _MONO)
}

DEFAULT = "cell"


class _P:
    """Palette resolver: ``P("nature")`` or ``P(name, single_column=True)``."""

    def __new__(cls, key: str = DEFAULT) -> Palette:
        try:
            return PALETTES[key]
        except KeyError:
            raise KeyError(
                f"unknown palette {key!r}; choose from {sorted(PALETTES)}"
            ) from None


P = _P


# ------------------------------------------------------------------ semantic

POSITIVE_WORDS = {
    "increase", "up", "higher", "improved", "benefit", "enriched", "gain",
    "activation", "promotion", "rescue", "protective",
}
NEGATIVE_WORDS = {
    "decrease", "down", "lower", "reduced", "loss", "inflammation", "risk",
    "inhibition", "damage", "harm", "depletion",
}


def semantic_colour(word: str, p: Palette = _CELL) -> str:
    """Map an up/down style word to the signal colour of a palette."""
    w = word.strip().lower()
    if w in POSITIVE_WORDS:
        return p.signal_pos
    if w in NEGATIVE_WORDS:
        return p.signal_neg
    return p.ink2


def updown_arrows(p: Palette = _CELL) -> dict[str, tuple[str, str]]:
    """(glyph, colour) pairs for the classic ↑/↓ annotations."""
    return {
        "up": ("\u2191", p.signal_pos),
        "down": ("\u2193", p.signal_neg),
        "flat": ("\u2192", p.muted),
    }


__all__ = [
    "Palette", "PALETTES", "DEFAULT", "P", "hx", "rgb", "from_rgb", "mix", "tint",
    "shade", "luminance", "contrast", "readable_on", "semantic_colour",
    "updown_arrows",
]
