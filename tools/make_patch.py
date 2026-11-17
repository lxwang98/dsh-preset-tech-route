"""Build tech-route/cordis.patch.yml from the proven sci-figure preset.

Keeps every tool row of the installed sci-figure bundle (which is itself a
verified copy of the standard preset) and replaces: preset id, roster name,
description, skill directory package name, and the persona prefix.
"""
from __future__ import annotations

import io
import re
from pathlib import Path

SRC = Path(r"D:\dsh-bundles\sci-figure\cordis.patch.yml")
DST = Path(r"D:\dsh-bundles\tech-route\cordis.patch.yml")
PERSONA = Path(r"D:\dsh-bundles\tech-route\docs\persona.md")

text = io.open(SRC, encoding="utf-8").read()
lines = text.splitlines()

# --- locate the persona prefix block -------------------------------------
start = next(i for i, ln in enumerate(lines) if ln.strip() == "prefix: |-")
end = next(i for i in range(start + 1, len(lines))
           if lines[i].startswith("          - id:"))
print("persona block: lines", start + 1, "..", end)

persona = io.open(PERSONA, encoding="utf-8").read().rstrip("\n")
body = "\n".join("                " + ln if ln.strip() else ""
                 for ln in persona.splitlines())
new_lines = lines[: start + 1] + body.splitlines() + lines[end:]

out = "\n".join(new_lines) + "\n"

# --- identity rewrites ----------------------------------------------------
out = out.replace("id: preset-sci-figure", "id: preset-tech-route")
out = out.replace("        id: sci-figure", "        id: tech-route")
out = out.replace("        name: 科研绘图模式", "        name: 科研技术路线绘制模式")
out = out.replace("@local/dsh-preset-sci-figure", "@local/dsh-preset-tech-route")
out = re.sub(r"(?m)^        description: .*$",
             "        description: " + io.open(
                 Path(r"D:\dsh-bundles\tech-route\docs\roster-description.txt"),
                 encoding="utf-8").read().strip(), out, count=1)

DST.write_text(out, encoding="utf-8")
print("wrote", DST, len(out.splitlines()), "lines")
