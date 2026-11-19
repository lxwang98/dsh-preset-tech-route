"""等距（isometric）图元：把"立体块"画成 3 个纯色多边形。

为什么不是 3D 渲染
------------------
本机没有 Blender / OpenGL，而且期刊与标书要的是**可编辑、可缩放、无锯齿**的图。
等距体块在数学上就是 3 个平行四边形：顶面、正面、侧面。用三条自由多边形就能
得到"像 3D"的效果，而且是纯矢量、能在 PowerPoint 里改颜色和位置。

约定
----
* 屏幕坐标系，y 向下。传入的 ``(x, y)`` 是**前下左角**。
* ``w`` 沿屏幕 +x（宽），``d`` 沿右上深轴（进深），``h`` 竖直向上。
* 深轴单位向量 ``DEPTH = (cos30°, -sin30°) = (0.866, -0.5)``，即真等距。
  要 2:1（游戏常用、更矮）就传 ``k=0.5`` 给 ``iso_block``，等价 ``(0.894, -0.447)``。
* 光影约定（**所有图共用**，否则拼在一起会脏）：顶面最亮、正面居中、侧面最暗。
  三面同色系，只改明度：``tint(acc, 0.86) / tint(acc, 0.62) / tint(acc, 0.42)``。
* 描边统一 ``lw=0.35``、颜色 ``shade(acc, 0.55)``；不画阴影（预设禁止堆阴影）。

文字
----
等距平面内的文字需要 shear，而 PowerPoint 只支持旋转不支持斜切，所以**标签一律
水平放在体块外侧**，用 0.5 pt 引线指过去。本模块不提供"贴在斜面上的文字"。
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

from pptx.util import Mm

from .palette import shade, tint

__all__ = [
    "DEPTH_X",
    "DEPTH_Y",
    "depth_vec",
    "iso_faces",
    "iso_block",
    "iso_layers",
    "iso_plane",
    "iso_arrow",
]

DEPTH_X = math.cos(math.radians(30.0))   # 0.8660
DEPTH_Y = -math.sin(math.radians(30.0))  # -0.5000


def depth_vec(d: float, k: float | None = None) -> tuple[float, float]:
    """进深向量。``k=None`` 用真等距 tan30°（≈0.577，单位向量 0.866/−0.5）；
    ``k=0.5`` 用 2:1 俯视（0.894/−0.447，更矮、更像游戏与流程图）。"""
    kk = math.tan(math.radians(30.0)) if k is None else float(k)
    n = math.hypot(1.0, kk)
    return d / n, -d * kk / n


def _poly(cv, pts: Sequence[tuple[float, float]], fill, line=None, lw: float = 0.35):
    """闭合自由多边形（PPTX 原生形状，可在 PowerPoint 里继续编辑）。"""
    builder = cv.slide.shapes.build_freeform(Mm(pts[0][0]), Mm(pts[0][1]))
    builder.add_line_segments([(Mm(px), Mm(py)) for px, py in pts[1:]], close=True)
    shp = builder.convert_to_shape()
    cv._set_fill(shp, fill)
    cv._style_line(shp, line, lw)
    shp.shadow.inherit = False
    return shp


def iso_faces(x: float, y: float, w: float, d: float, h: float, k: float | None = None):
    """返回 (top, front, side, back) 四条闭合多边形顶点表。``(x, y)`` 为前下左角。"""
    dx, dy = depth_vec(d, k)
    p0 = (x, y)
    p1 = (x + w, y)
    p2 = (x + w + dx, y + dy)
    p3 = (x + dx, y + dy)
    up = (0.0, -h)
    top = [(p0[0] + up[0], p0[1] + up[1]), (p1[0] + up[0], p1[1] + up[1]),
           (p2[0] + up[0], p2[1] + up[1]), (p3[0] + up[0], p3[1] + up[1])]
    front = [p0, p1, (p1[0] + up[0], p1[1] + up[1]), (p0[0] + up[0], p0[1] + up[1])]
    side = [p1, p2, (p2[0] + up[0], p2[1] + up[1]), (p1[0] + up[0], p1[1] + up[1])]
    back = [p3, p2, (p2[0] + up[0], p2[1] + up[1]), (p3[0] + up[0], p3[1] + up[1])]
    return top, front, side, back


def iso_block(cv, x: float, y: float, *, w: float, d: float, h: float,
              acc: str, k: float | None = None,
              levels: tuple[float, float, float] = (0.86, 0.62, 0.42),
              line: bool = True, lw: float = 0.35, top: bool = True):
    """画一个等距长方体。返回 (top, front, side) 三个顶点表，便于后续贴图元。

    ``top=False`` 时不画顶面——堆叠剖面的中间层用它，否则每层顶面都会露出来，
    整摞看起来像"被切片并炸开"，而不是一整块岩芯。
    """
    top_pts, front, side, back = iso_faces(x, y, w, d, h, k)
    if line:
        _poly(cv, back, tint(acc, 0.30), shade(acc, 0.62), lw)
    _poly(cv, front, tint(acc, levels[1]), shade(acc, 0.62) if line else None, lw)
    _poly(cv, side, tint(acc, levels[2]), shade(acc, 0.62) if line else None, lw)
    if top:
        _poly(cv, top_pts, tint(acc, levels[0]), shade(acc, 0.62) if line else None, lw)
    return top_pts, front, side


def iso_layers(cv, x: float, y: float, *, w: float, d: float,
               layers: Iterable[tuple[float, str]], k: float | None = None,
               levels: tuple[float, float, float] = (0.86, 0.62, 0.42),
               line: bool = True, lw: float = 0.35):
    """自下而上堆叠分层（土壤剖面 / 含水层 / 沉积）。``layers`` = [(厚度 mm, 颜色), ...]

    只有最顶层的顶面会被绘制；返回最顶层顶面的四个顶点（便于往上放作物、建筑等）。
    """
    seq = list(layers)
    top_pts = None
    yy = y
    for i, (hh, acc) in enumerate(seq):
        top_pts, _f, _s = iso_block(cv, x, yy, w=w, d=d, h=hh, acc=acc, k=k,
                                    levels=levels, line=line, lw=lw,
                                    top=(i == len(seq) - 1))
        yy -= hh
    return top_pts


def iso_plane(cv, x: float, y: float, *, w: float, d: float, k: float | None = None,
              fill: str = "#ffffff", line: str | None = None, lw: float = 0.35):
    """单个等距平行四边形（地表、水面、田块）。返回顶点表。"""
    dx, dy = depth_vec(d, k)
    pts = [(x, y), (x + w, y), (x + w + dx, y + dy), (x + dx, y + dy)]
    _poly(cv, pts, fill, line, lw)
    return pts


def iso_arrow(cv, p0: tuple[float, float], p1: tuple[float, float], *,
              colour: str = "#455766", lw: float = 0.9, head: float = 1.6):
    """等距平面上的箭头（用 cv.arrow 即可，这里只是语义化封装）。"""
    return cv.arrow(p0, p1, colour=colour, lw=lw, head="triangle", shrink=head * 0.5)
