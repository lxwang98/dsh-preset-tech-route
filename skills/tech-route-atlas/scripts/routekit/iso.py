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


def iso_faces(x: float, y: float, w: float, d: float, h: float, k: float | None = None,
              mode: str = "oblique"):
    """返回 (top, front, side, back) 四条闭合多边形顶点表。

    ``mode="oblique"``：``(x, y)`` = 前下左角，正面是矩形（斜投影 / cabinet），
    适合"剖面 + 分层"这类需要正对读者的图。
    ``mode="iso"``：``(x, y)`` = **近角**，宽沿右上 30°、进深沿左上 30°，
    三面都是平行四边形（真等距），适合地形/场景/多体块。
    """
    up = (0.0, -h)
    if mode == "iso":
        u = (w * DEPTH_X, w * DEPTH_Y)      # 右上
        v = (-d * DEPTH_X, d * DEPTH_Y)     # 左上
        n = (x, y)
        pu = (n[0] + u[0], n[1] + u[1])
        pv = (n[0] + v[0], n[1] + v[1])
        pf = (n[0] + u[0] + v[0], n[1] + u[1] + v[1])
        top = [(n[0] + up[0], n[1] + up[1]), (pu[0] + up[0], pu[1] + up[1]),
               (pf[0] + up[0], pf[1] + up[1]), (pv[0] + up[0], pv[1] + up[1])]
        right = [n, pu, (pu[0] + up[0], pu[1] + up[1]), (n[0] + up[0], n[1] + up[1])]
        left = [n, pv, (pv[0] + up[0], pv[1] + up[1]), (n[0] + up[0], n[1] + up[1])]
        return top, right, left, None
    dx, dy = depth_vec(d, k)
    p0 = (x, y)
    p1 = (x + w, y)
    p2 = (x + w + dx, y + dy)
    p3 = (x + dx, y + dy)
    top = [(p0[0] + up[0], p0[1] + up[1]), (p1[0] + up[0], p1[1] + up[1]),
           (p2[0] + up[0], p2[1] + up[1]), (p3[0] + up[0], p3[1] + up[1])]
    front = [p0, p1, (p1[0] + up[0], p1[1] + up[1]), (p0[0] + up[0], p0[1] + up[1])]
    side = [p1, p2, (p2[0] + up[0], p2[1] + up[1]), (p1[0] + up[0], p1[1] + up[1])]
    back = [p3, p2, (p2[0] + up[0], p2[1] + up[1]), (p3[0] + up[0], p3[1] + up[1])]
    return top, front, side, back


def iso_block(cv, x: float, y: float, *, w: float, d: float, h: float,
              acc: str, k: float | None = None,
              levels: tuple[float, float, float] = (0.78, 0.56, 0.38),
              line: bool = True, lw: float = 0.35, top: bool = True,
              mode: str = "oblique"):
    """画一个等距长方体。返回 (top, face1, face2) 三个顶点表，便于后续贴图元。

    ``top=False`` 时不画顶面——堆叠剖面的中间层用它，否则每层顶面都会露出来，
    整摞看起来像"被切片并炸开"，而不是一整块岩芯。
    """
    top_pts, f1, f2, back = iso_faces(x, y, w, d, h, k, mode=mode)
    if line and back is not None:
        _poly(cv, back, tint(acc, 0.30), shade(acc, 0.62), lw)
    _poly(cv, f1, tint(acc, levels[1]), shade(acc, 0.62) if line else None, lw)
    _poly(cv, f2, tint(acc, levels[2]), shade(acc, 0.62) if line else None, lw)
    if top:
        _poly(cv, top_pts, tint(acc, levels[0]), shade(acc, 0.62) if line else None, lw)
    return top_pts, f1, f2


def iso_layers(cv, x: float, y: float, *, w: float, d: float,
               layers: Iterable[tuple[float, str]], k: float | None = None,
               levels: tuple[float, float, float] = (0.78, 0.56, 0.38),
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
              fill: str = "#ffffff", line: str | None = None, lw: float = 0.35,
              mode: str = "oblique"):
    """单个等距平行四边形（地表、水面、田块）。返回顶点表。

    ``mode="iso"`` 时 ``(x, y)`` 是**近角**，宽沿右上 30°、进深沿左上 30°（真等距）。
    """
    if mode == "iso":
        pts = [(x, y), (x + w * DEPTH_X, y + w * DEPTH_Y),
               (x + w * DEPTH_X - d * DEPTH_X, y + w * DEPTH_Y - d * DEPTH_Y),
               (x - d * DEPTH_X, y - d * DEPTH_Y)]
    else:
        dx, dy = depth_vec(d, k)
        pts = [(x, y), (x + w, y), (x + w + dx, y + dy), (x + dx, y + dy)]
    _poly(cv, pts, fill, line, lw)
    return pts


def iso_depth(x: float, y: float, w: float, d: float, *, mode: str = "iso") -> float:
    """绘画顺序键：**值小 = 更远 = 先画**。

    多个体块互相遮挡时必须先按它排序再画（PPTX 没有 z-buffer，后画的盖住先画的）。
    ``iso``：用远角的屏幕 y（越小越靠后）；``oblique``：用进深 d。
    """
    if mode == "iso":
        return y - (w + d) * 0.5
    return -d


def iso_scene(cv, items, *, mode: str = "iso", levels: tuple[float, float, float] = (0.78, 0.56, 0.38),
              line: bool = True, lw: float = 0.35):
    """按由远到近的次序画一组体块/平面，自动处理遮挡。

    ``items`` = ``[dict(kind="block"|"plane", x=, y=, w=, d=, h=0, acc=..., **kw)]``
    """
    def key(it):
        return iso_depth(it["x"], it["y"], it["w"], it["d"], mode=mode)

    out = []
    for it in sorted(items, key=key):
        kind = it.pop("kind", "block")
        if kind == "plane":
            out.append(iso_plane(cv, it["x"], it["y"], w=it["w"], d=it["d"], k=it.get("k"),
                                 fill=it.get("fill", "#ffffff"), line=it.get("line"),
                                 lw=it.get("lw", lw), mode=mode))
        else:
            out.append(iso_block(cv, it["x"], it["y"], w=it["w"], d=it["d"], h=it["h"],
                                 acc=it["acc"], k=it.get("k"), levels=it.get("levels", levels),
                                 line=line, lw=lw, top=it.get("top", True), mode=mode))
    return out



def iso_arrow(cv, p0: tuple[float, float], p1: tuple[float, float], *,
              colour: str = "#455766", lw: float = 0.9, head: float = 1.6):
    """等距平面上的箭头（用 cv.arrow 即可，这里只是语义化封装）。"""
    return cv.arrow(p0, p1, colour=colour, lw=lw, head="triangle", shrink=head * 0.5)

