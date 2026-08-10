"""Verificacoes de conteudo: etica profissional, dados pendentes e consistencia."""
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]

# Superlativos comparativos e promessa de resultado sao vedados pelo
# Codigo de Etica Odontologica.
EXPRESSOES_VEDADAS = [
    r"\bo melhor dentista\b",
    r"\ba melhor cl[ií]nica\b",
    r"\bmelhor da cidade\b",
    r"\bmelhor de s[ãa]o paulo\b",
    r"\bresultado garantido\b",
    r"\bgarantimos\b",
    r"\bsem dor\b",
    r"\bindolor\b",
    r"\bpre[çc]o imbat[ií]vel\b",
]


def test_nenhuma_expressao_vedada_pelo_cfo(html_bruto):
    problemas = []
    for url, texto in html_bruto.items():
        baixo = texto.lower()
        for padrao in EXPRESSOES_VEDADAS:
            if re.search(padrao, baixo):
                problemas.append((url, padrao))
    assert problemas == []


@pytest.mark.xfail(
    reason="Aguardando endereco, CEP, telefone e coordenadas reais da clinica",
    strict=False,
)
def test_json_ld_nao_contem_dado_pendente(paginas):
    """Publicar schema com TROCAR informa dado falso ao Google."""
    problemas = []
    for url, p in paginas.items():
        for bloco in p.jsonld:
            if "TROCAR" in bloco:
                problemas.append(url)
    assert problemas == [], (
        "JSON-LD com dado pendente. Preencher src/data/site.json e o "
        f"front-matter antes de publicar: {problemas}"
    )


def test_menu_do_header_bate_com_nav_json():
    nav = json.loads((RAIZ / "src" / "data" / "nav.json").read_text(encoding="utf-8"))
    header = (RAIZ / "src" / "partials" / "header.html").read_text(encoding="utf-8")
    faltando = [item["url"] for item in nav["principal"] if item["url"] not in header]
    assert faltando == []


def test_texto_da_dra_nao_foi_alterado():
    """Filosofia, missao e valores sao fonte unica e nao podem ser reescritos."""
    fonte = (RAIZ / "filosofia.txt").read_text(encoding="utf-8")
    destino = (RAIZ / "src" / "content" / "pt" / "filosofia.html").read_text(
        encoding="utf-8"
    )
    frases = [
        "um sorriso vai muito além da estética",
        "Mais do que tratar dentes, cuidamos de pessoas",
        "excelência não é um destino, mas um padrão permanente de conduta",
    ]
    for frase in frases:
        assert frase in fonte, f"frase de controle ausente na fonte: {frase}"
        assert frase in destino, f"texto da Dra. alterado: {frase}"


def test_paginas_com_texto_medico_tem_marcador_de_revisao():
    """Todo texto clinico escrito pela equipe precisa ser validado pela Dra."""
    pastas = [
        RAIZ / "src" / "pages" / "tratamentos",
        RAIZ / "src" / "pages" / "blog",
    ]
    faltando = []
    for pasta in pastas:
        for arquivo in pasta.glob("*.html"):
            if arquivo.name == "index.html":
                continue
            if "Validar com a Dra." not in arquivo.read_text(encoding="utf-8"):
                faltando.append(arquivo.name)
    assert faltando == []
