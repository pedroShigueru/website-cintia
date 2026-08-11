"""Gera assets/favicon.svg recortando o monograma FK da logo.

A logo inteira num favicon de 16px vira um borrao: o wordmark ocupa 80% da
largura e some. Este script isola a moldura e o monograma, que sao os dois
paths em gradiente dourado, e os centraliza num quadrado sobre navy.

Uso:  py tools/make_favicon.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "assets" / "fukuoka-dental-clinic-transparente.svg"
DESTINO = RAIZ / "assets" / "favicon.svg"

NAVY = "#0F2D52"
MARGEM = 0.08  # respiro ao redor do monograma, em fracao do lado

# Bbox do monograma no espaco do viewBox, medido a partir dos paths em
# gradiente (os dois unicos que compoem moldura e FK).
CAIXA = (21.9, 24.2, 297.9, 340.0)


def main() -> int:
    if not ORIGEM.exists():
        print(f"nao encontrei {ORIGEM.relative_to(RAIZ)}")
        return 1

    svg = ORIGEM.read_text(encoding="utf-8")

    defs = re.search(r"<defs>.*?</defs>", svg, re.DOTALL)
    grupo = re.search(r'<g transform="[^"]+"', svg)
    dourados = re.findall(r'<path fill="url\(#gold[^"]*\)" d="[^"]+"/>', svg)
    if not (defs and grupo and dourados):
        print("A estrutura da logo mudou; revise CAIXA e os seletores.")
        return 1

    x0, y0, x1, y1 = CAIXA
    lado = max(x1 - x0, y1 - y0) * (1 + 2 * MARGEM)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    vx, vy = cx - lado / 2, cy - lado / 2

    saida = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{vx:.1f} {vy:.1f} {lado:.1f} {lado:.1f}" '
        f'role="img" aria-label="Fukuoka Dental Clinic">\n'
        f'  <rect x="{vx:.1f}" y="{vy:.1f}" width="{lado:.1f}" height="{lado:.1f}" fill="{NAVY}"/>\n'
        f"  {defs.group(0)}\n"
        f"  {grupo.group(0)}>\n"
        + "".join(f"   {p}\n" for p in dourados)
        + "  </g>\n</svg>\n"
    )

    DESTINO.write_text(saida, encoding="utf-8", newline="\n")
    print(f"gerado: {DESTINO.relative_to(RAIZ)}  ({len(saida)} bytes)")
    print(f"  viewBox {vx:.1f} {vy:.1f} {lado:.1f} {lado:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
