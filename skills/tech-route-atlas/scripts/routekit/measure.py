"""Text metrics without launching PowerPoint.

PowerPoint only reports real text bounds after the file is opened, which is
too late to make layout decisions. This module measures with the *actual*
system font files through FreeType, so width estimates are within a few
percent of PowerPoint's own line breaking — enough to size boxes, choose a
font size and pre-wrap labels before the file is even written.

    w = text_w_mm("Whole-grain black rice", 7.5)
    size, lines = fit_text("...", w_mm=30, h_mm=8, max_pt=8)
"""
from __future__ import annotations

import re
from functools import lru_cache

from PIL import ImageFont

from .tokens import pt_to_mm

_CJK_RE = re.compile(r"[\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef\u3000-\u303f]")
_LATIN_RE = re.compile(r"[A-Za-z0-9]")
_WORD_RE = re.compile(r"\s+")

FONT_FILES: dict[str, tuple[str, str]] = {
    "Arial": (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
    "Helvetica": (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
    "Microsoft YaHei": (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc"),
    "SimHei": (r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simhei.ttf"),
    "Noto Sans SC": (
        r"C:\Windows\Fonts\NotoSansSC-Regular.otf",
        r"C:\Users\wanglinx\AppData\Local\Microsoft\Windows\Fonts\NotoSansSC-Bold.otf",
    ),
    "Times New Roman": (r"C:\Windows\Fonts\times.ttf", r"C:\Windows\Fonts\timesbd.ttf"),
    "Calibri": (r"C:\Windows\Fonts\calibri.ttf", r"C:\Windows\Fonts\calibrib.ttf"),
}

CJK_FONT = "Microsoft YaHei"
_REF = 100  # reference px size for ratio measurement


def has_cjk(s: str) -> bool:
    return bool(_CJK_RE.search(s))


@lru_cache(maxsize=64)
def _font(name: str, bold: bool):
    reg, bol = FONT_FILES.get(name, FONT_FILES["Arial"])
    path = bol if bold else reg
    idx = 0
    try:
        return ImageFont.truetype(path, _REF, index=idx)
    except Exception:
        try:
            return ImageFont.truetype(FONT_FILES["Arial"][0], _REF)
        except Exception:
            return ImageFont.load_default()


def text_w_pt(s: str, pt: float, *, bold: bool = False, font: str = "Arial") -> float:
    """Advance width of `s` at `pt` points, in points."""
    if not s:
        return 0.0
    f = _font(font, bold)
    cjkf = _font(CJK_FONT if font not in ("Noto Sans SC", "SimHei") else font, bold)
    total = 0.0
    for chunk in _segment(s):
        use = cjkf if _CJK_RE.match(chunk[0]) else f
        total += use.getlength(chunk) / _REF
    return total * pt


def text_w_mm(s: str, pt: float, *, bold: bool = False, font: str = "Arial") -> float:
    return pt_to_mm(text_w_pt(s, pt, bold=bold, font=font))


def _segment(s: str) -> list[str]:
    """Split into CJK / non-CJK runs so each is measured with the right face."""
    out: list[str] = []
    if not s:
        return out
    cur = s[0]
    cur_cjk = bool(_CJK_RE.match(s[0]))
    for ch in s[1:]:
        is_cjk = bool(_CJK_RE.match(ch))
        if is_cjk == cur_cjk:
            cur += ch
        else:
            out.append(cur)
            cur = ch
            cur_cjk = is_cjk
    out.append(cur)
    return out


def wrap_lines(s: str, width_pt: float, pt: float, *, bold: bool = False,
               font: str = "Arial") -> list[str]:
    """Greedy wrap that mirrors PowerPoint's behaviour for Arial/CJK."""
    s = s.replace("\n", " ")
    if not s:
        return [""]
    lines: list[str] = []
    for para in s.split("\n"):
        words = _WORD_RE.split(para.strip())
        cur = ""
        for w in words:
            if not w:
                continue
            cand = (cur + " " + w).strip()
            if not cur or text_w_pt(cand, pt, bold=bold, font=font) <= width_pt:
                cur = cand
                continue
            if text_w_pt(w, pt, bold=bold, font=font) <= width_pt:
                lines.append(cur)
                cur = w
            else:  # single word too long -> hard character wrap
                piece = cur
                for ch in w:
                    if text_w_pt(piece + ch, pt, bold=bold, font=font) <= width_pt:
                        piece += ch
                    else:
                        lines.append(piece)
                        piece = ch
                cur = piece
        lines.append(cur)
    return [ln for ln in lines if ln != ""] or [""]


def fit_text(s: str, *, w_mm: float, h_mm: float, max_pt: float = 8.0,
             min_pt: float = 4.5, bold: bool = False, font: str = "Arial",
             spacing: float = 0.95, allow_wrap: bool = True) -> tuple[float, list[str]]:
    """Largest point size (<= max_pt) at which `s` fits the box.

    Returns (size_pt, lines). If even min_pt overflows, returns min_pt with
    the overflow lines so the caller can shorten the text instead.
    """
    from .tokens import line_height_mm

    width_pt = w_mm * 72.0 / 25.4
    height_pt = h_mm * 72.0 / 25.4
    size = max_pt
    while size >= min_pt:
        if allow_wrap:
            lines = wrap_lines(s, width_pt, size, bold=bold, font=font)
        else:
            lines = [s] if text_w_pt(s, size, bold=bold, font=font) <= width_pt else ["\u2026"]
        need_h = len(lines) * pt_to_mm(size) * 1.32 * spacing
        widest = max(text_w_pt(ln, size, bold=bold, font=font) for ln in lines)
        if need_h <= height_pt + 0.05 and (widest <= width_pt + 0.05 or allow_wrap):
            return size, lines
        if not allow_wrap and widest > width_pt:
            pass
        size -= 0.25
    return min_pt, (wrap_lines(s, width_pt, min_pt, bold=bold, font=font) if allow_wrap else [s])


def fit_paragraphs(paras: Sequence[str], *, w_mm: float, h_mm: float,
                   max_pt: float = 8.0, min_pt: float = 4.5, bold: bool = False,
                   font: str = "Arial", spacing: float = 0.95,
                   allow_wrap: bool = True) -> tuple[float, list[str]]:
    """Largest size at which every paragraph fits `w_mm` x `h_mm`.

    Explicit newlines in the caller's string are hard paragraph breaks; each
    paragraph is then wrapped independently. This is the only wrapping model
    that survives `word_wrap = False`.
    """
    from .tokens import line_height_mm

    width_pt = w_mm * 72.0 / 25.4

    def layout(size: float) -> list[str]:
        out: list[str] = []
        for seg in paras:
            if allow_wrap:
                out.extend(wrap_lines(seg, width_pt, size, bold=bold, font=font) or [seg])
            else:
                out.append(seg)
        return out

    size = max_pt
    while size >= min_pt - 0.001:
        lines = layout(size)
        need = len(lines) * line_height_mm(size, spacing)
        widest = max((text_w_pt(ln, size, bold=bold, font=font) for ln in lines),
                     default=0.0)
        if need <= h_mm + 0.05 and widest <= width_pt + 0.05:
            return size, lines
        size -= 0.25
    return min_pt, layout(min_pt)


def text_fits(s: str, *, w_mm: float, h_mm: float, pt: float, bold: bool = False,
              font: str = "Arial", spacing: float = 0.95, tol: float = 0.04) -> bool:
    from .tokens import line_height_mm

    width_pt = w_mm * 72.0 / 25.4
    lines: list[str] = []
    for seg in str(s).split("\n"):
        lines.extend(wrap_lines(seg, width_pt, pt, bold=bold, font=font) or [seg])
    need_h = len(lines) * line_height_mm(pt, spacing)
    return need_h <= h_mm * (1 + tol) and max(
        text_w_pt(ln, pt, bold=bold, font=font) for ln in lines
    ) <= width_pt * (1 + tol)


def ellipsize(s: str, width_mm: float, pt: float, *, bold: bool = False,
              font: str = "Arial") -> str:
    """Trim with an ellipsis until it fits the width."""
    if text_w_mm(s, pt, bold=bold, font=font) <= width_mm:
        return s
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if text_w_mm(s[:mid] + "\u2026", pt, bold=bold, font=font) <= width_mm:
            lo = mid
        else:
            hi = mid - 1
    return s[:lo].rstrip() + "\u2026"


__all__ = [
    "text_w_pt", "text_w_mm", "wrap_lines", "fit_text", "text_fits",
    "ellipsize", "has_cjk", "FONT_FILES", "CJK_FONT",
]
