"""Deriva a variante da logo para fundo claro.

A logo entregue pelo designer foi desenhada para fundo escuro: sobre o
off-white do header o wordmark cai para 1,40:1 e some. Este script gera
`assets/fukuoka-dental-clinic-escura.svg` a partir da versao transparente,
sem redesenhar nada — so remapeia cores.

PROVISORIO: quando o designer entregar a variante oficial para fundo claro,
apagar o arquivo gerado e este script, e apontar o header para o arquivo dela.

Uso:  py tools/make_logo_dark.py
"""
from pathlib import Path
import re
import sys

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "assets" / "fukuoka-dental-clinic-transparente.svg"
DESTINO = RAIZ / "assets" / "fukuoka-dental-clinic-escura.svg"

# Cores solidas: wordmark e subtitulo viram tokens do design system.
SUBSTITUICOES = {
    "#DBD1C7": "#0F2D52",  # FUKUOKA  -> --navy      (12,91:1 sobre off-white)
    "#D2B183": "#8A6A3B",  # DENTAL CLINIC -> --gold-text (4,66:1)
}

# Gradiente do monograma e da moldura: escurecido preservando a variacao
# metalica. 0.65 alinha a cor media com --gold-text e mantem o pior stop
# em 3,15:1, acima do minimo de 3:1 para elemento grafico.
FATOR_GRADIENTE = 0.65

STOP = re.compile(r'stop-color="#([0-9A-Fa-f]{6})"')


def escurecer(hexa: str, fator: float) -> str:
    r, g, b = (int(hexa[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % (round(r * fator), round(g * fator), round(b * fator))


def main() -> int:
    if not ORIGEM.exists():
        print(f"nao encontrei {ORIGEM.relative_to(RAIZ)}")
        return 1

    svg = ORIGEM.read_text(encoding="utf-8")
    for antes, depois in SUBSTITUICOES.items():
        if antes not in svg:
            print(f"AVISO: cor {antes} nao encontrada; a logo de origem mudou?")
        svg = svg.replace(antes, depois)

    svg = STOP.sub(
        lambda m: f'stop-color="{escurecer(m.group(1), FATOR_GRADIENTE)}"', svg
    )
    svg = svg.replace(
        'role="img"',
        'role="img" data-origem="derivado de fukuoka-dental-clinic-transparente.svg"',
        1,
    )

    DESTINO.write_text(svg, encoding="utf-8", newline="\n")
    print(f"gerado: {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
