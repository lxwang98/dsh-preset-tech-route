"""物体级 3D（球 / 圆柱 / 球棍模型）→ 600 dpi PNG。

与 ``iso`` 的分工
-----------------
* ``iso``      —— 空间关系（谁在谁上面、水往哪流），纯矢量、可编辑，**首选**。
* ``render3d`` —— 需要"这个东西长什么样"时的单个立体物件（病毒、细胞、纳米颗粒、
  分子球棍模型）。走 plotly + kaleido 离线出 PNG（kaleido 自带 Chromium，不需要 GPU/OpenGL，
  本机实测可用；plotly 7.1 + kaleido 1.5）。

注意
----
* 输出是**位图**（PNG），不是可编辑矢量；在 PPTX 里是图片。要可编辑就用 ``iso``。
* 光照与配色由本模块统一：单一方向光、matte 材质、无环境光遮蔽，
  与平面图的"纯色平涂"尽量靠近；**不要**加镜面高光、渐变天空盒、地面阴影。
* 分子请喂真实坐标（PDB / PubChem 导出），**不要编原子位置**。
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

__all__ = ["sphere", "cylinder", "ball_stick", "export"]


def _fig():
    import plotly.graph_objects as go  # 延迟导入：不用 3D 的脚本不受影响

    return go.Figure()


def sphere(centre: Sequence[float], r: float, colour: str, *, n: int = 28):
    """按经纬网格生成一个球面 Mesh3d。``colour`` 支持任意 hex。"""
    import numpy as np
    import plotly.graph_objects as go

    u = np.linspace(0, 2 * math.pi, n)
    v = np.linspace(0, math.pi, max(8, n // 2))
    U, V = np.meshgrid(u, v)
    cx, cy, cz = centre
    x = cx + r * np.cos(U) * np.sin(V)
    y = cy + r * np.sin(U) * np.sin(V)
    z = cz + r * np.cos(V)
    # Mesh3d 只吃一维数组（Surface 才吃二维）；展平后三角化。
    X, Y, Z = x.ravel(), y.ravel(), z.ravel()
    nv = V.shape[0]
    ni = U.shape[1]
    idx = np.arange(nv * ni).reshape(nv, ni)
    a = idx[:-1, :-1].ravel()
    b = idx[:-1, 1:].ravel()
    c = idx[1:, :-1].ravel()
    d = idx[1:, 1:].ravel()
    return go.Mesh3d(x=X, y=Y, z=Z, color=colour, opacity=1.0, flatshading=False,
                     i=np.concatenate([a, b]), j=np.concatenate([b, d]),
                     k=np.concatenate([c, c]),
                     lighting=dict(ambient=0.55, diffuse=0.85, specular=0.10))



def cylinder(p0: Sequence[float], p1: Sequence[float], r: float, colour: str, *, n: int = 16):
    """两点之间的圆柱（用于化学键、菌毛、纳米管）。"""
    import numpy as np
    import plotly.graph_objects as go

    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    axis = p1 - p0
    L = float(np.linalg.norm(axis))
    if L < 1e-9:
        raise ValueError("cylinder: p0 == p1")
    z = axis / L
    tmp = np.array([0.0, 1.0, 0.0]) if abs(z[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    x = np.cross(tmp, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    t = np.linspace(0, 2 * math.pi, n)
    ring = np.outer(np.cos(t), x) + np.outer(np.sin(t), y)
    c0 = p0 + ring * r
    c1 = p1 + ring * r
    X = np.vstack([c0[:, 0], c1[:, 0]])
    Y = np.vstack([c0[:, 1], c1[:, 1]])
    Z = np.vstack([c0[:, 2], c1[:, 2]])
    i = list(range(n - 1)) + [n - 1]
    j = [(k + 1) % n for k in range(n)]
    kk = [k + n for k in range(n)]
    return go.Mesh3d(x=X.ravel(), y=Y.ravel(), z=Z.ravel(),
                     i=i + kk, j=j + kk, k=j + i,
                     color=colour, lighting=dict(ambient=0.55, diffuse=0.85, specular=0.10))


def ball_stick(atoms: Iterable[tuple], bonds: Iterable[tuple[int, int]] = (),
               *, width: int = 900, height: int = 700, transparent: bool = True):
    """球棍模型。

    ``atoms``: ``[(x, y, z, r, colour), ...]``
    ``bonds``: ``[(i, j), ...]``，键半径默认 = min(r_i, r_j) * 0.28
    """
    fig = _fig()
    atoms = list(atoms)
    for a, b in bonds:
        r = min(atoms[a][3], atoms[b][3]) * 0.28
        fig.add_trace(cylinder(atoms[a][:3], atoms[b][:3], r, "#9aa7b4"))
    for x, y, z, r, col in atoms:
        fig.add_trace(sphere((x, y, z), r, col))
    fig.update_layout(width=width, height=height, margin=dict(l=0, r=0, t=0, b=0),
                      paper_bgcolor="rgba(0,0,0,0)" if transparent else "#ffffff",
                      scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                                 aspectmode="data",
                                 camera=dict(eye=dict(x=1.35, y=1.35, z=1.0),
                                             up=dict(x=0, y=0, z=1))))
    return fig


def export(fig, path, *, scale: float = 3.0, dpi_note: str = ""):
    """导出 PNG。``scale`` 是相对 96 dpi 的倍数：宽 900 px × 3 ≈ 2700 px，
    放在 11 cm 宽的位置上约等于 600 dpi。"""
    fig.write_image(str(path), scale=scale)
    return path
