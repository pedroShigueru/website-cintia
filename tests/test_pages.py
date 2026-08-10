"""Verificacoes de SEO e acessibilidade aplicadas a todas as paginas geradas."""
import json

MIN_DESCRICAO = 50
MAX_DESCRICAO = 160


def test_toda_pagina_tem_title(paginas):
    faltando = [url for url, p in paginas.items() if not p.title]
    assert faltando == []


def test_titles_sao_unicos(paginas):
    vistos: dict[str, str] = {}
    duplicados = []
    for url, p in paginas.items():
        if p.title in vistos:
            duplicados.append((vistos[p.title], url, p.title))
        vistos[p.title] = url
    assert duplicados == []


def test_toda_pagina_tem_description_no_tamanho_certo(paginas):
    problemas = []
    for url, p in paginas.items():
        d = p.meta.get("description", "")
        if not MIN_DESCRICAO <= len(d) <= MAX_DESCRICAO:
            problemas.append((url, len(d)))
    assert problemas == []


def test_descriptions_sao_unicas(paginas):
    descricoes = [p.meta.get("description", "") for p in paginas.values()]
    assert len(descricoes) == len(set(descricoes))


def test_exatamente_um_h1_por_pagina(paginas):
    problemas = [(url, len(p.h1)) for url, p in paginas.items() if len(p.h1) != 1]
    assert problemas == []


def test_hierarquia_de_headings_sem_salto(paginas):
    problemas = []
    for url, p in paginas.items():
        anterior = 0
        for nivel, texto in p.headings:
            if anterior and nivel > anterior + 1:
                problemas.append((url, f"h{anterior} -> h{nivel}", texto))
            anterior = nivel
    assert problemas == []


def test_toda_pagina_tem_canonical_absoluto(paginas):
    problemas = []
    for url, p in paginas.items():
        canonical = p.link("canonical")
        if not canonical or not canonical.get("href", "").startswith("http"):
            problemas.append(url)
    assert problemas == []


def test_toda_pagina_declara_lang(paginas):
    problemas = [url for url, p in paginas.items() if p.html_lang not in {"pt-BR", "en"}]
    assert problemas == []


def test_toda_pagina_tem_open_graph(paginas):
    obrigatorias = {"og:title", "og:description", "og:type", "og:url"}
    problemas = [
        (url, sorted(obrigatorias - set(p.meta)))
        for url, p in paginas.items()
        if obrigatorias - set(p.meta)
    ]
    assert problemas == []


def test_toda_imagem_tem_alt_e_dimensoes(paginas):
    problemas = []
    for url, p in paginas.items():
        for img in p.imgs:
            if "alt" not in img:
                problemas.append((url, img.get("src"), "sem alt"))
            if not img.get("width") or not img.get("height"):
                problemas.append((url, img.get("src"), "sem width/height"))
    assert problemas == []


def test_json_ld_e_valido(paginas):
    for url, p in paginas.items():
        for bloco in p.jsonld:
            json.loads(bloco)  # levanta se estiver malformado


def test_nenhum_placeholder_de_template_escapou(html_bruto):
    vazando = [url for url, texto in html_bruto.items() if "{{" in texto]
    assert vazando == []


def _caminho_de(href: str) -> str:
    """Converte uma URL absoluta do site no caminho relativo correspondente."""
    resto = href.split("//", 1)[-1]
    resto = resto.split("/", 1)[1] if "/" in resto else ""
    return resto or "index.html"


def test_hreflang_e_reciproco(paginas):
    """Se A aponta para B como alternate, B precisa apontar de volta para A."""
    alternates = {
        url: {
            _caminho_de(item["href"])
            for item in p.links
            if item.get("rel") == "alternate" and item.get("hreflang") != "x-default"
        }
        for url, p in paginas.items()
    }
    problemas = []
    for url, destinos in alternates.items():
        for destino in destinos - {url}:
            if destino not in alternates:
                problemas.append((url, destino, "destino nao existe"))
            elif url not in alternates[destino]:
                problemas.append((url, destino, "sem link de volta"))
    assert problemas == []


def test_paginas_em_ingles_estao_noindex(html_bruto):
    """Enquanto nao traduzidas, as paginas EN nao podem ser indexadas."""
    faltando = [
        url for url, texto in html_bruto.items()
        if url.startswith("en/") and 'content="noindex' not in texto
    ]
    assert faltando == []


def test_sitemap_nao_lista_paginas_noindex(saida):
    assert "/en/" not in saida["sitemap.xml"]


def test_nenhum_link_interno_quebrado(saida, paginas):
    """Todo href relativo deve corresponder a um arquivo que existe."""
    import posixpath
    from pathlib import Path

    raiz = Path(__file__).resolve().parents[1]
    gerados = set(saida)
    problemas = []
    for url, p in paginas.items():
        base = posixpath.dirname(url)
        for item in p.links:
            alvo = item.get("href", "")
            if not alvo or alvo.startswith(("http", "#", "mailto:", "tel:", "data:")):
                continue
            # A 404 usa caminho absoluto: ela e servida sob qualquer URL.
            partida = "" if alvo.startswith("/") else base
            resolvido = posixpath.normpath(
                posixpath.join(partida, alvo.lstrip("/"))
            ).replace("\\", "/")
            if resolvido in gerados or (raiz / resolvido).exists():
                continue
            problemas.append((url, alvo, resolvido))
    assert problemas == []
