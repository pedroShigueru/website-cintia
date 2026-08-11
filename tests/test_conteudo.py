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
    reason="Aguardando o dominio real; o resto dos dados de contato ja chegou",
    strict=False,
)
def test_nenhum_placeholder_critico_sobrou():
    """Valores que sao URLs validas e por isso nao carregam a marca TROCAR.

    Sem este teste eles passariam despercebidos numa busca por TROCAR.
    """
    site = json.loads((RAIZ / "src" / "data" / "site.json").read_text(encoding="utf-8"))
    pendentes = []
    if "5511000000000" in site["whatsapp_url"]:
        pendentes.append("whatsapp_url: numero de exemplo, todos os CTAs vao para ele")
    if "fukuokadentalclinic.com.br" in site["base_url"]:
        pendentes.append("base_url: dominio presumido, usado em canonical/hreflang/sitemap")
    if "/maps/search/" in site["maps_url"]:
        pendentes.append(
            "maps_url: busca por endereco. O ideal e o link da ficha no Google "
            "Business, que mostra avaliacoes e horario"
        )
    assert pendentes == [], "Placeholders criticos:\n  - " + "\n  - ".join(pendentes)


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


def test_paginas_de_prova_social_nao_ficam_vazias(html_bruto):
    """A Home e /depoimentos.html anunciam avaliacoes; precisam ter alguma."""
    vazias = [
        url
        for url in ("depoimentos.html", "index.html")
        if "<blockquote" not in html_bruto[url]
    ]
    assert vazias == [], (
        "Sem nenhuma avaliacao renderizada em: "
        + ", ".join(vazias)
        + ". Rode `py tools/fetch_reviews.py`."
    )
