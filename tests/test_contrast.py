"""Verifica que a paleta atende ao WCAG AA."""
from pathlib import Path

import pytest

from colors import contraste, luminancia, tokens_do_css

RAIZ = Path(__file__).resolve().parents[1]
CSS = (RAIZ / "css" / "style.css").read_text(encoding="utf-8")
TOKENS = tokens_do_css(CSS)

# (token do texto, token do fundo, minimo exigido)
PARES_DE_TEXTO = [
    ("ink", "offwhite", 4.5),
    ("ink-soft", "offwhite", 4.5),
    ("gold-text", "offwhite", 4.5),
    ("navy", "offwhite", 4.5),
    ("gold-light", "navy", 4.5),
    ("gold-light", "navy-deep", 4.5),
]


def test_valores_da_paleta_batem_com_o_briefing():
    assert TOKENS["navy"] == "#0F2D52"
    assert TOKENS["gold"] == "#B08D57"
    assert TOKENS["offwhite"] == "#F8F7F3"
    assert TOKENS["gray"] == "#D9D9D6"


def test_referencia_conhecida_da_formula():
    # Preto sobre branco e o maximo teorico da escala.
    assert contraste("#000000", "#FFFFFF") == pytest.approx(21.0, abs=0.01)
    assert luminancia("#FFFFFF") == pytest.approx(1.0, abs=0.001)


@pytest.mark.parametrize("texto,fundo,minimo", PARES_DE_TEXTO)
def test_par_de_texto_atende_aa(texto, fundo, minimo):
    razao = contraste(TOKENS[texto], TOKENS[fundo])
    assert razao >= minimo, (
        f"--{texto} sobre --{fundo} da {razao:.2f}:1, "
        f"abaixo do minimo AA de {minimo}:1"
    )


def test_branco_sobre_navy_atende_aa():
    assert contraste("#FFFFFF", TOKENS["navy"]) >= 4.5


def test_dourado_bruto_nunca_e_usado_em_texto():
    """#B08D57 da 2.88:1 sobre off-white. So pode ser decoracao."""
    ofensores = [
        linha.strip()
        for linha in CSS.splitlines()
        if "color:" in linha
        and "var(--gold)" in linha
        and "background" not in linha
        and "border" not in linha
        and "-color:" not in linha
    ]
    assert ofensores == [], f"--gold usado em texto: {ofensores}"
