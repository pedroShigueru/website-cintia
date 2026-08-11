"""Gerador estatico do site da Fukuoka Dental Clinic.

Le src/ e escreve HTML estatico na raiz do repositorio.
Sem dependencias externas: apenas a stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from html import escape as html_escape
from pathlib import Path

# Chaves duplas em vez de string.Template porque `$` colide com CSS e JS.
PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")
DELIMITADOR = "---"

RAIZ = Path(__file__).resolve().parents[1]

# `header` consome `cta_bar`; `head` consome dados da pagina.
# Ordem explicita em vez de resolucao recursiva.
ORDEM_PARTIALS = ["cta_bar", "header", "footer", "head"]
MARCADOR_RESUMO = "<!--resumo-->"


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


@dataclass
class Pagina:
    origem: Path
    url: str
    meta: dict
    corpo: str


def carregar_dados(raiz: Path) -> dict:
    """Le src/data/*.json. site.json vira chaves `site_*`; o resto, uma por arquivo."""
    dados: dict = {}
    for arquivo in sorted((raiz / "src" / "data").glob("*.json")):
        conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
        if arquivo.stem == "site":
            dados.update({f"site_{k}": v for k, v in conteudo.items()})
        else:
            dados[arquivo.stem] = conteudo
    return dados


def carregar_conteudo(raiz: Path, lang: str) -> dict:
    """Le src/content/<lang>/*.html como chaves `content_<stem>`.

    Um arquivo com o marcador <!--resumo--> gera tambem `content_<stem>_resumo`,
    com o texto ate o marcador. Evita duplicar o texto da Dra. em dois arquivos.
    """
    pasta = raiz / "src" / "content" / lang
    conteudo: dict = {}
    if not pasta.is_dir():
        return conteudo
    for arquivo in sorted(pasta.glob("*.html")):
        texto = arquivo.read_text(encoding="utf-8")
        conteudo[f"content_{arquivo.stem}"] = texto.replace(MARCADOR_RESUMO, "")
        if MARCADOR_RESUMO in texto:
            conteudo[f"content_{arquivo.stem}_resumo"] = texto.split(MARCADOR_RESUMO)[0]
    return conteudo


def descobrir_paginas(raiz: Path) -> list[Pagina]:
    base = raiz / "src" / "pages"
    paginas: list[Pagina] = []
    for arquivo in sorted(base.rglob("*.html")):
        meta, corpo = parse_front_matter(arquivo.read_text(encoding="utf-8"))
        url = meta.get("url") or arquivo.relative_to(base).as_posix()
        paginas.append(Pagina(origem=arquivo, url=url, meta=meta, corpo=corpo))
    return paginas


def _ler_partials(raiz: Path, idioma: str = "pt") -> dict[str, str]:
    """Le os partials. A chave usa underscore; o arquivo, hifen.

    `header-en.html` tem precedencia sobre `header.html` em paginas com
    lang="en". Sem contraparte traduzida, cai no padrao — assim so os
    partials que precisam de traducao sao duplicados.
    """
    pasta = raiz / "src" / "partials"
    partials: dict[str, str] = {}
    for nome in ORDEM_PARTIALS:
        base = nome.replace("_", "-")
        candidatos = [
            pasta / f"{base}-{idioma}.html",
            pasta / f"{base}.html",
            pasta / f"{nome}.html",
        ]
        arquivo = next(c for c in candidatos if c.exists())
        partials[nome] = arquivo.read_text(encoding="utf-8")
    return partials


def _url_absoluta(base_url: str, url: str) -> str:
    caminho = "" if url == "index.html" else url
    return f"{base_url.rstrip('/')}/{caminho}"


def _montar_sitemap(base_url: str, paginas: list[Pagina]) -> str:
    entradas = "\n".join(
        f"  <url><loc>{_url_absoluta(base_url, p.url)}</loc></url>"
        for p in sorted(paginas, key=lambda p: p.url)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entradas}\n"
        "</urlset>\n"
    )


def _montar_robots(base_url: str) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {base_url.rstrip('/')}/sitemap.xml\n"


DESTAQUES = 3  # avaliacoes exibidas na Home e perto dos CTAs


def _estrelas(nota: float) -> str:
    """Cinco estrelas, as preenchidas ate a nota arredondada."""
    cheias = int(round(nota))
    marcas = "".join(
        f'<span class="estrela{"" if i < cheias else " estrela--vazia"}">&#9733;</span>'
        for i in range(5)
    )
    return f'<span class="estrelas" aria-hidden="true">{marcas}</span>'


def _cartao_avaliacao(av: dict, resumido: bool = False) -> str:
    """Um cartao de avaliacao. `resumido` limita a altura via CSS.

    Avaliacoes reais variam muito de tamanho: uma de tres linhas ao lado de
    uma de vinte desalinha a grade. Na Home elas ficam limitadas; na pagina
    de depoimentos aparecem inteiras.
    """
    autor = html_escape(str(av.get("autor", "")))
    quando = html_escape(str(av.get("quando", "")))
    nota = float(av.get("nota", 5))
    paragrafos = "".join(
        f"<p>{html_escape(t.strip())}</p>"
        for t in str(av.get("texto", "")).split("\n")
        if t.strip()
    )
    classe = "avaliacao avaliacao--resumida" if resumido else "avaliacao"
    # Sem data conhecida, o campo some em vez de deixar um espaco vazio.
    rodape = f"<strong>{autor}</strong>" + (f"<span>{quando}</span>" if quando else "")
    return (
        f'<blockquote class="{classe}">'
        f"{_estrelas(nota)}"
        f'<div class="avaliacao__texto">{paragrafos}</div>'
        f"<footer>{rodape}</footer>"
        "</blockquote>"
    )


def _blocos_avaliacoes(dados: dict) -> dict[str, str]:
    """Monta os blocos de avaliacoes do Google a partir de avaliacoes.json.

    Sem nota ou sem avaliacoes, devolve tudo vazio: uma clinica sem
    avaliacoes nao pode exibir 'nota 0' nem uma secao sem conteudo.
    """
    vazio = {"avaliacoes_faixa": "", "avaliacoes_todas": "", "avaliacoes_selo": ""}
    av = dados.get("avaliacoes") or {}
    lista = av.get("avaliacoes") or []
    nota = av.get("nota")
    if nota is None or not lista:
        return vazio

    nota_txt = f"{float(nota):.1f}".replace(".", ",")
    # Sem o total do perfil, nao inventamos um numero: o texto sai sem contagem.
    total = av.get("total")
    contagem = f"{total} avaliações no Google" if total else "avaliações no Google"
    perfil = av.get("url_perfil", "")
    botao = (
        f'<a class="btn btn--ghost" href="{perfil}" target="_blank" rel="noopener">'
        "Ver todas as avaliações no Google</a>"
    )

    faixa = (
        '<div class="avaliacoes-resumo">'
        f'<p class="avaliacoes-nota"><strong>{nota_txt}</strong>{_estrelas(float(nota))}'
        f'<span class="avaliacoes-total">{contagem}</span></p>'
        "</div>"
        '<div class="avaliacoes-grid">'
        + "".join(_cartao_avaliacao(a, resumido=True) for a in lista[:DESTAQUES])
        + "</div>"
        f'<p class="centralizado">{botao}</p>'
    )

    todas = (
        '<div class="avaliacoes-grid avaliacoes-todas">'
        + "".join(_cartao_avaliacao(a) for a in lista)
        + "</div>"
        f'<p class="centralizado">{botao}</p>'
    )

    selo = (
        f'<a class="avaliacoes-selo" href="{perfil}" target="_blank" rel="noopener">'
        f"{_estrelas(float(nota))}"
        f"<span><strong>{nota_txt}</strong> &middot; {contagem}</span>"
        "</a>"
    )

    return {
        "avaliacoes_faixa": faixa,
        "avaliacoes_todas": todas,
        "avaliacoes_selo": selo,
    }


MENU = re.compile(r'(<nav class="site-nav".*?</nav>)', re.DOTALL)


def _marcar_pagina_atual(header: str, url: str, prefixo: str) -> str:
    """Adiciona aria-current="page" ao item de menu da pagina em exibicao.

    Uma subpagina marca a secao pai: tratamentos/invisalign.html acende
    "Tratamentos". Restrito ao <nav class="site-nav"> para nao marcar o logo,
    que aponta para a home em todas as paginas.
    """
    alvos = {url}
    if "/" in url:
        secao = url.split("/")[0]
        alvos.add(f"{secao}.html")        # tratamentos/x.html -> tratamentos.html
        alvos.add(f"{secao}/index.html")  # blog/x.html       -> blog/index.html

    def marcar(bloco: re.Match) -> str:
        texto = bloco.group(1)
        for alvo in sorted(alvos, key=len, reverse=True):
            href = f'href="{prefixo}{alvo}"'
            if href in texto:
                return texto.replace(href, f"{href} aria-current=\"page\"", 1)
        return texto

    return MENU.sub(marcar, header)


def _e_indexavel(pagina: Pagina) -> bool:
    return pagina.meta.get("noindex", "").lower() not in {"true", "sim", "1"}


def _montar_alternates(base_url: str, url: str, lang: str, meta: dict) -> str:
    """Monta as tags hreflang a partir de `alternate_en` / `alternate_pt`.

    Cada pagina declara explicitamente sua contraparte. Sem declaracao,
    nenhum hreflang e emitido — melhor que apontar para uma URL inexistente.
    """
    alvos = [meta[c] for c in ("alternate_en", "alternate_pt") if meta.get(c)]
    if not alvos:
        return ""

    base = base_url.rstrip("/")
    propria = "en" if lang == "en" else "pt-BR"
    marcas = [f'<link rel="alternate" hreflang="{propria}" href="{_url_absoluta(base, url)}">']
    if propria == "pt-BR":
        marcas.append(f'<link rel="alternate" hreflang="x-default" href="{_url_absoluta(base, url)}">')
    for alvo in alvos:
        idioma = "en" if alvo.startswith("en/") else "pt-BR"
        marcas.append(f'<link rel="alternate" hreflang="{idioma}" href="{_url_absoluta(base, alvo)}">')
        if idioma == "pt-BR":
            marcas.append(
                f'<link rel="alternate" hreflang="x-default" href="{_url_absoluta(base, alvo)}">'
            )
    return "\n  ".join(marcas)


def construir(raiz: Path) -> dict[str, str]:
    """Devolve {caminho_relativo: conteudo} de tudo que deve existir no disco."""
    dados = carregar_dados(raiz)
    dados.update(_blocos_avaliacoes(dados))
    partials_por_idioma: dict[str, dict[str, str]] = {}
    layouts = {
        p.stem: p.read_text(encoding="utf-8")
        for p in (raiz / "src" / "layouts").glob("*.html")
    }
    paginas = descobrir_paginas(raiz)

    saida: dict[str, str] = {}
    for pagina in paginas:
        lang = pagina.meta.get("lang", "pt-BR")
        idioma = lang.split("-")[0]
        if idioma not in partials_por_idioma:
            partials_por_idioma[idioma] = _ler_partials(raiz, idioma)
        partials = partials_por_idioma[idioma]
        ctx: dict = {
            **dados,
            **carregar_conteudo(raiz, idioma),
            **pagina.meta,
            "lang": lang,
            "url": pagina.url,
            "url_absoluta": _url_absoluta(dados["site_base_url"], pagina.url),
            # Caminho relativo ate a raiz. Mantem os links corretos em
            # subpastas sem depender de o site estar servido na raiz do dominio.
            # O front-matter pode sobrescrever: a 404 precisa de caminho
            # absoluto, porque e servida sob qualquer URL inexistente.
            "prefixo": pagina.meta.get("prefixo", "../" * pagina.url.count("/")),
            "alternates": _montar_alternates(
                dados["site_base_url"], pagina.url, lang, pagina.meta
            ),
            "meta_robots": (
                "" if _e_indexavel(pagina)
                else '<meta name="robots" content="noindex, follow">'
            ),
            "ativo_pt": "" if lang == "en" else 'aria-current="true"',
            "ativo_en": 'aria-current="true"' if lang == "en" else "",
        }
        # Front-matter opcional: default vazio para nao quebrar o render.
        for chave in ("classe_body", "jsonld"):
            ctx.setdefault(chave, "")

        # O front-matter pode usar {{ }}. Sem isso, um JSON-LD teria de
        # repetir endereco e telefone em vez de referenciar site.json.
        for chave, valor in pagina.meta.items():
            if isinstance(valor, str) and "{{" in valor:
                ctx[chave] = render(valor, ctx)

        ctx["conteudo"] = render(pagina.corpo, ctx)
        for nome in ORDEM_PARTIALS:
            ctx[nome] = render(partials[nome], ctx)
        ctx["header"] = _marcar_pagina_atual(
            ctx["header"], pagina.url, ctx["prefixo"]
        )
        layout = layouts[pagina.meta.get("layout", "base")]
        saida[pagina.url] = render(layout, ctx)

    saida["sitemap.xml"] = _montar_sitemap(
        dados["site_base_url"], [p for p in paginas if _e_indexavel(p)]
    )
    saida["robots.txt"] = _montar_robots(dados["site_base_url"])
    return saida


def verificar(raiz: Path, saida: dict[str, str]) -> list[str]:
    """Devolve os caminhos cujo conteudo em disco difere do gerado."""
    divergentes = []
    for caminho, conteudo in saida.items():
        destino = raiz / caminho
        if not destino.exists() or destino.read_text(encoding="utf-8") != conteudo:
            divergentes.append(caminho)
    return sorted(divergentes)


def escrever(raiz: Path, saida: dict[str, str]) -> list[str]:
    """Grava apenas o que mudou e devolve a lista de caminhos alterados."""
    alterados = verificar(raiz, saida)
    for caminho in alterados:
        destino = raiz / caminho
        destino.parent.mkdir(parents=True, exist_ok=True)
        # newline explicito para a saida ser identica em qualquer plataforma.
        destino.write_text(saida[caminho], encoding="utf-8", newline="\n")
    return alterados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera o site estatico.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verifica se a saida esta sincronizada com src/, sem gravar",
    )
    args = parser.parse_args(argv)

    saida = construir(RAIZ)
    if args.check:
        divergentes = verificar(RAIZ, saida)
        if divergentes:
            print("Saida dessincronizada. Rode `py tools/build.py`:")
            for caminho in divergentes:
                print(f"  {caminho}")
            return 1
        print("Saida sincronizada.")
        return 0

    alterados = escrever(RAIZ, saida)
    print(f"{len(alterados)} arquivo(s) atualizado(s) de {len(saida)}.")
    for caminho in alterados:
        print(f"  {caminho}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
