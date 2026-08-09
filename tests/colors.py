"""Calculo de contraste conforme WCAG 2.1."""
import re

TOKEN = re.compile(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})\s*;")


def _canal_linear(valor: int) -> float:
    c = valor / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(cor: str) -> float:
    """Luminancia relativa de uma cor `#RRGGBB`."""
    cor = cor.lstrip("#")
    r, g, b = (int(cor[i:i + 2], 16) for i in (0, 2, 4))
    return (
        0.2126 * _canal_linear(r)
        + 0.7152 * _canal_linear(g)
        + 0.0722 * _canal_linear(b)
    )


def contraste(a: str, b: str) -> float:
    """Razao de contraste entre duas cores, de 1 a 21."""
    la, lb = luminancia(a), luminancia(b)
    claro, escuro = max(la, lb), min(la, lb)
    return (claro + 0.05) / (escuro + 0.05)


def tokens_do_css(css: str) -> dict[str, str]:
    """Extrai as custom properties de cor declaradas no CSS."""
    return {nome: valor.upper() for nome, valor in TOKEN.findall(css)}
