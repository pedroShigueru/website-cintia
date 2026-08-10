"""Gerador estatico do site da Fukuoka Dental Clinic.

Le src/ e escreve HTML estatico na raiz do repositorio.
Sem dependencias externas: apenas a stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
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


def _ler_partials(raiz: Path) -> dict[str, str]:
    """Le os partials. A chave usa underscore; o arquivo, hifen."""
    pasta = raiz / "src" / "partials"
    partials: dict[str, str] = {}
    for nome in ORDEM_PARTIALS:
        arquivo = pasta / f"{nome.replace('_', '-')}.html"
        if not arquivo.exists():
            arquivo = pasta / f"{nome}.html"
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
    partials = _ler_partials(raiz)
    layouts = {
        p.stem: p.read_text(encoding="utf-8")
        for p in (raiz / "src" / "layouts").glob("*.html")
    }
    paginas = descobrir_paginas(raiz)

    saida: dict[str, str] = {}
    for pagina in paginas:
        lang = pagina.meta.get("lang", "pt-BR")
        ctx: dict = {
            **dados,
            **carregar_conteudo(raiz, lang.split("-")[0]),
            **pagina.meta,
            "lang": lang,
            "url": pagina.url,
            "url_absoluta": _url_absoluta(dados["site_base_url"], pagina.url),
            # Caminho relativo ate a raiz. Mantem os links corretos em
            # subpastas sem depender de o site estar servido na raiz do dominio.
            "prefixo": "../" * pagina.url.count("/"),
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

        ctx["conteudo"] = render(pagina.corpo, ctx)
        for nome in ORDEM_PARTIALS:
            ctx[nome] = render(partials[nome], ctx)
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
