"""Gerador estatico do site da Fukuoka Dental Clinic.

Le src/ e escreve HTML estatico na raiz do repositorio.
Sem dependencias externas: apenas a stdlib.
"""
from __future__ import annotations

import re

# Chaves duplas em vez de string.Template porque `$` colide com CSS e JS.
PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")
DELIMITADOR = "---"


def parse_front_matter(texto: str) -> tuple[dict[str, str], str]:
    """Separa o front-matter do corpo.

    O front-matter e delimitado por linhas `---` e usa `chave: valor`,
    um par por linha. Linhas vazias e linhas iniciadas por `#` sao ignoradas.
    """
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != DELIMITADOR:
        return {}, texto

    fim = None
    for i, linha in enumerate(linhas[1:], start=1):
        if linha.strip() == DELIMITADOR:
            fim = i
            break
    if fim is None:
        raise ValueError("front-matter nao fechado: falta a linha `---` final")

    meta: dict[str, str] = {}
    for linha in linhas[1:fim]:
        despida = linha.strip()
        if not despida or despida.startswith("#"):
            continue
        if ":" not in despida:
            raise ValueError(f"linha de front-matter sem `:`: {despida!r}")
        chave, valor = despida.split(":", 1)
        meta[chave.strip()] = valor.strip()

    return meta, "\n".join(linhas[fim + 1:])


def render(template: str, context: dict) -> str:
    """Substitui `{{ chave }}` pelo valor correspondente do contexto."""
    ausentes: list[str] = []

    def substituir(m: re.Match) -> str:
        chave = m.group(1)
        if chave not in context:
            ausentes.append(chave)
            return ""
        return str(context[chave])

    saida = PLACEHOLDER.sub(substituir, template)
    if ausentes:
        raise KeyError("placeholders sem valor: " + ", ".join(sorted(set(ausentes))))
    return saida
