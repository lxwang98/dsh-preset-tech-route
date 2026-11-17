"""Geometry helpers: boxes, splitting, flow layout, anchoring.

All values are millimetres in *canvas* space, origin top-left, y down. This
matches PowerPoint's coordinate system, so a Box can be handed straight to
canvas primitives.

    root = Box(0, 0, 180, 100)
    zones = root.cols([1, 2, 1], gap=G.m)      # -> 4 Boxes
    inner = zones[1].inner(G.s)                 # padding
    row = inner.rows([1, 2], gap=G.s)
    steps = row[1].flow(4, axis="h", gap=G.s)   # 4 equal cells
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    # -- derived -----------------------------------------------------
    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    @property
    def area(self) -> float:
        return self.w * self.h

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.w, self.h)

    # -- transforms --------------------------------------------------
    def inset(self, dx: float, dy: float | None = None) -> "Box":
        dy = dx if dy is None else dy
        return Box(self.x + dx, self.y + dy, max(0.1, self.w - 2 * dx),
                   max(0.1, self.h - 2 * dy))

    def inner(self, pad: float) -> "Box":
        return self.inset(pad)

    def moved(self, dx: float = 0, dy: float = 0) -> "Box":
        return Box(self.x + dx, self.y + dy, self.w, self.h)

    def with_h(self, h: float) -> "Box":
        return Box(self.x, self.y, self.w, h)

    def with_w(self, w: float) -> "Box":
        return Box(self.x, self.y, w, self.h)

    def align(self, other: "Box", how: str = "center") -> "Box":
        """Re-centre this box against another on 'x', 'y' or 'center'."""
        dx = dy = 0.0
        if how in ("x", "center"):
            dx = other.cx - self.cx
        if how in ("y", "center"):
            dy = other.cy - self.cy
        return self.moved(dx, dy)

    # -- splitting ---------------------------------------------------
    def rows(self, weights: Sequence[float] | int, gap: float = 0.0) -> list["Box"]:
        return _split(self, weights, gap, axis="v")

    def cols(self, weights: Sequence[float] | int, gap: float = 0.0) -> list["Box"]:
        return _split(self, weights, gap, axis="h")

    def row(self, i: int, n: int, gap: float = 0.0) -> "Box":
        return self.rows([1] * n, gap)[i]

    def col(self, i: int, n: int, gap: float = 0.0) -> "Box":
        return self.cols([1] * n, gap)[i]

    def flow(self, n: int, axis: str = "h", gap: float = 0.0) -> list["Box"]:
        return [Box(self.x, self.y, self.w, self.h)] if n <= 0 else (
            self.cols([1] * n, gap) if axis == "h" else self.rows([1] * n, gap)
        )

    # -- anchoring ---------------------------------------------------
    def anchor(self, side: str, frac: float = 0.5) -> tuple[float, float]:
        f = min(1.0, max(0.0, frac))
        return {
            "l": (self.x, self.y + self.h * f),
            "r": (self.x2, self.y + self.h * f),
            "t": (self.x + self.w * f, self.y),
            "b": (self.x + self.w * f, self.y2),
            "c": (self.cx, self.cy),
        }[side]


def _split(b: Box, weights: Sequence[float] | int, gap: float, axis: str) -> list[Box]:
    if isinstance(weights, int):
        weights = [1.0] * weights
    n = len(weights)
    total = float(sum(weights)) or 1.0
    span = (b.w if axis == "h" else b.h) - gap * (n - 1)
    out: list[Box] = []
    pos = b.x if axis == "h" else b.y
    for wt in weights:
        size = span * (wt / total)
        out.append(Box(pos, b.y, size, b.h) if axis == "h" else Box(b.x, pos, b.w, size))
        pos += size + gap
    return out


# ------------------------------------------------------------------ presets

def even_slots(b: Box, n: int, axis: str = "h", gap: float = 0.0) -> list[Box]:
    return b.flow(n, axis=axis, gap=gap)


def center_in(b: Box, w: float, h: float) -> Box:
    return Box(b.cx - w / 2, b.cy - h / 2, w, h)


def stack_top(b: Box, heights: Iterable[float], gap: float = 0.0) -> list[Box]:
    out: list[Box] = []
    y = b.y
    for hh in heights:
        out.append(Box(b.x, y, b.w, hh))
        y += hh + gap
    return out


def stack_left(b: Box, widths: Iterable[float], gap: float = 0.0) -> list[Box]:
    out: list[Box] = []
    x = b.x
    for ww in widths:
        out.append(Box(x, b.y, ww, b.h))
        x += ww + gap
    return out


def grid(b: Box, rows: int, cols: int, gap: float = 0.0) -> list[list[Box]]:
    return [r.rows(rows, gap) if False else r for r in
            [col for col in zip(*[rr.cols(cols, gap) for rr in b.rows(rows, gap)])]]


def ladder(b: Box, n: int, *, step: float, axis: str = "h") -> list[Box]:
    """Staircase of n equal cells, each offset by `step` mm — the classic
    'phase progression' look for a process timeline."""
    cells = b.flow(n, axis=axis, gap=0.0)
    out: list[Box] = []
    for i, c in enumerate(cells):
        off = step * i
        out.append(c.moved(0, off) if axis == "h" else c.moved(off, 0))
    return out


def radial(b: Box, n: int, radius: float, start_deg: float = 0.0) -> list[tuple[float, float]]:
    """n points on a circle centred in `b` (degrees, 0 = east, clockwise)."""
    import math

    pts = []
    for i in range(n):
        a = math.radians(start_deg + 360.0 * i / max(1, n))
        pts.append((b.cx + radius * math.cos(a), b.cy + radius * math.sin(a)))
    return pts


__all__ = [
    "Box", "even_slots", "center_in", "stack_top", "stack_left", "grid",
    "ladder", "radial",
]
