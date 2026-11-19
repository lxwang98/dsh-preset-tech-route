"""Render PPTX to PNG / PDF with the installed PowerPoint, plus COM audit.

No LibreOffice, no cairo, no browser: this machine has Microsoft Office, so
PowerPoint itself is the renderer. That is also what makes the preview
trustworthy — it is the same engine the user will open the deck in.

    from routekit.export import to_png, to_pdf, render
    render("route.pptx", "out/", dpi=600)     # -> out/route.png + out/route.pdf
"""
from __future__ import annotations

import os
from pathlib import Path


def _app():
    import pythoncom
    import win32com.client as win32

    pythoncom.CoInitialize()
    app = win32.Dispatch("PowerPoint.Application")
    try:
        app.DisplayAlerts = 1  # ppAlertsNone
    except Exception:
        pass
    return app


def _open(app, path: Path, *, window: bool = False):
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    return app.Presentations.Open(str(path), ReadOnly=True, Untitled=False,
                                  WithWindow=bool(window))


def to_png(pptx: str | Path, png: str | Path, *, dpi: int = 300,
           width_px: int | None = None, slide: int = 1) -> Path:
    """Export one slide to PNG. Pixel size defaults to `dpi` at true size."""
    pptx, png = Path(pptx), Path(png)
    png.parent.mkdir(parents=True, exist_ok=True)
    app = _app()
    pres = _open(app, pptx)
    try:
        s = pres.Slides(slide)
        w = int(width_px) if width_px else int(round(s.Master.Width * dpi / 72.0))
        h = int(round(w * s.Master.Height / s.Master.Width))
        s.Export(str(png.resolve()), "PNG", w, h)
    finally:
        try:
            pres.Close()
        finally:
            app.Quit()
    return png


def to_pdf(pptx: str | Path, pdf: str | Path) -> Path:
    pptx, pdf = Path(pptx), Path(pdf)
    pdf.parent.mkdir(parents=True, exist_ok=True)
    app = _app()
    pres = _open(app, pptx)
    try:
        pres.SaveAs(str(pdf.resolve()), 32)  # ppSaveAsPDF
    finally:
        try:
            pres.Close()
        finally:
            app.Quit()
    return pdf


def to_svg(pptx: str | Path, svg: str | Path, *, slide: int = 1) -> Path:
    """PowerPoint's own SVG export (ppSaveAsSVG = 28), one file per slide."""
    pptx, svg = Path(pptx), Path(svg)
    svg.parent.mkdir(parents=True, exist_ok=True)
    app = _app()
    pres = _open(app, pptx)
    try:
        s = pres.Slides(slide)
        s.Export(str(svg.resolve()), "SVG")
    finally:
        try:
            pres.Close()
        finally:
            app.Quit()
    return svg


def to_tiff(png: str | Path, tiff: str | Path, *, dpi: int = 600,
            compression: str = "tiff_lzw") -> Path:
    """PNG → TIFF for journal submission.

    - 合到白底（多数期刊拒收带 alpha 的 TIFF）
    - 8 bit RGB（不做 CMYK；真要 CMYK 得在 Photoshop 里转，PIL 转出来偏色）
    - `tiff_lzw` 无损压缩，文件约为未压缩的 1/2–1/3
    - dpi 写进 TIFF 标签，审稿系统都读这个
    """
    from PIL import Image

    png, tiff = Path(png), Path(tiff)
    tiff.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(png) as im:
        im = im.convert("RGBA")
        flat = Image.new("RGB", im.size, (255, 255, 255))
        flat.paste(im, mask=im.split()[-1])
        flat.save(tiff, format="TIFF", dpi=(dpi, dpi), compression=compression)
    return tiff


def deliver(pptx: str | Path, out_dir: str | Path, *, dpi: int = 600,
            stem: str | None = None, slide: int = 1,
            tiff_dpi: int | None = None) -> dict[str, Path]:
    """技术路线图的标准交付：PNG(600) + PDF(矢量) + TIFF(600)，一次会话出齐。

    默认值即投稿规格；组会/PPT 场景显式传 `dpi=220` 并自行跳过 TIFF
    （用 `render(..., also_tiff=False)`）。
    """
    return render(pptx, out_dir, dpi=dpi, stem=stem, slide=slide,
                  also_pdf=True, also_tiff=True, tiff_dpi=tiff_dpi)


def render(pptx: str | Path, out_dir: str | Path, *, dpi: int = 600,
           stem: str | None = None, slide: int = 1,
           also_pdf: bool = True, also_tiff: bool = False,
           tiff_dpi: int | None = None) -> dict[str, Path]:
    """PNG (+ PDF, + TIFF) of one slide in a single PowerPoint session.

    TIFF 默认沿用 PNG 的 dpi；投稿用 600，幻灯片用 220 就够（文件小一个量级）。
    """
    pptx = Path(pptx)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = stem or pptx.stem
    png = out / f"{stem}.png"
    pdf = out / f"{stem}.pdf"

    app = _app()
    pres = _open(app, pptx)
    got: dict[str, Path] = {}
    try:
        s = pres.Slides(slide)
        w = int(round(s.Master.Width * dpi / 72.0))
        h = int(round(w * s.Master.Height / s.Master.Width))
        s.Export(str(png.resolve()), "PNG", w, h)
        got["png"] = png
        if also_pdf:
            pres.SaveAs(str(pdf.resolve()), 32)
            got["pdf"] = pdf
    finally:
        try:
            pres.Close()
        finally:
            app.Quit()

    if also_tiff:
        got["tiff"] = to_tiff(png, out / f"{stem}.tif", dpi=tiff_dpi or dpi)
    return got


def slide_size_pt(pptx: str | Path) -> tuple[float, float]:
    """Slide size in points, read straight from the XML (no PowerPoint)."""
    from pptx import Presentation
    from pptx.util import Emu

    prs = Presentation(str(pptx))
    return (Emu(prs.slide_width).pt, Emu(prs.slide_height).pt)


def com_audit(pptx: str | Path, *, tol_pt: float = 0.6) -> list[dict]:
    """Open in PowerPoint and report real text overflow / off-canvas shapes."""
    import pythoncom
    import win32com.client as win32

    pptx = Path(pptx).resolve()
    issues: list[dict] = []
    pythoncom.CoInitialize()
    app = win32.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(str(pptx), ReadOnly=True, Untitled=False,
                                  WithWindow=False)
    try:
        sw, sh = pres.PageSetup.SlideWidth, pres.PageSetup.SlideHeight
        for si in range(1, pres.Slides.Count + 1):
            for shp in pres.Slides(si).Shapes:
                name = str(shp.Name)
                try:
                    w, h = float(shp.Width), float(shp.Height)
                    l, t = float(shp.Left), float(shp.Top)
                except Exception:
                    continue
                if l < -0.5 or t < -0.5 or l + w > sw + 0.5 or t + h > sh + 0.5:
                    issues.append({"slide": si, "shape": name, "kind": "off-canvas",
                                   "detail": f"({l:.0f},{t:.0f}) {w:.0f}x{h:.0f} "
                                             f"canvas {sw:.0f}x{sh:.0f}"})
                try:
                    tf = shp.TextFrame2
                    if not tf.HasText:
                        continue
                    bw, bh = float(tf.TextRange.BoundWidth), float(tf.TextRange.BoundHeight)
                except Exception:
                    continue
                # inner margins count toward the usable box
                avail_w = w - float(tf.MarginLeft) - float(tf.MarginRight)
                avail_h = h - float(tf.MarginTop) - float(tf.MarginBottom)
                if bw > avail_w + tol_pt * 2 or bh > avail_h + tol_pt:
                    issues.append({"slide": si, "shape": name, "kind": "text-overflow",
                                   "detail": f"text {bw:.1f}x{bh:.1f} in box "
                                             f"{avail_w:.1f}x{avail_h:.1f}",
                                   "text": str(tf.TextRange.Text)[:60]})
    finally:
        try:
            pres.Close()
        finally:
            app.Quit()
    return issues


__all__ = ["to_png", "to_pdf", "to_svg", "render", "com_audit", "slide_size_pt"]
