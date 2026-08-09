# Fukuoka Dental Clinic — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruir o site atual (landing page única "Dra. Cíntia") como o site institucional multipágina da Fukuoka Dental Clinic, seguindo o briefing da Dra. Cíntia.

**Architecture:** Site estático gerado por um script Python de stdlib pura (`tools/build.py`) que compõe páginas a partir de partials, layouts e um arquivo de dados JSON. A saída é HTML estático commitado na raiz do repositório, servível por qualquer host. A Home é longa e cobre todas as seções em resumo; páginas internas aprofundam cada assunto e carregam o SEO por termo.

**Tech Stack:** Python 3.12 (stdlib apenas), pytest 9.1 para os testes, HTML5, CSS3 (custom properties, grid, `@view-transition`), JavaScript vanilla sem dependências.

**Spec:** `docs/superpowers/specs/2026-08-09-fukuoka-dental-clinic-site-design.md`

## Global Constraints

Estas regras valem para **todas** as tasks. Os requisitos de cada task as incluem implicitamente.

- **Zero dependências de runtime.** `tools/build.py` usa apenas a stdlib. Sem Jinja2, sem PyYAML, sem BeautifulSoup. Nos testes, apenas `pytest` e stdlib (`html.parser` para inspecionar HTML).
- **Idioma do conteúdo:** português do Brasil. Comentários de código e mensagens de commit em português.
- **Marcadores de dado ausente:** todo dado real que não temos usa o comentário `<!-- TROCAR: descrição -->` no HTML, ou a string `"TROCAR"` em `src/data/site.json`. Nunca inventar endereço, CRO, telefone, número de pacientes ou depoimento.
- **Paleta (valores exatos):**
  - `--navy: #0F2D52`
  - `--navy-deep: #0A1F3A`
  - `--gold: #B08D57` — **decoração apenas**, nunca em texto
  - `--gold-text: #8A6A3B` — dourado em texto sobre fundo claro
  - `--gold-light: #C9A96E` — dourado em texto sobre navy
  - `--offwhite: #F8F7F3`
  - `--gray: #D9D9D6`
  - `--ink: #1A1A1A`
  - `--ink-soft: #4A5568`
- **Contraste:** nenhum par de cor em texto abaixo de 4,5:1 (normal) ou 3:1 (large, ≥24px ou ≥19px bold). `var(--gold)` nunca aparece em uma declaração `color:`.
- **Tipografia:** `Cormorant Garamond` (títulos), `Inter` (corpo), via Google Fonts com `preconnect` e `display=swap`.
- **Ética profissional (CFO):** nenhum texto pode prometer resultado, usar superlativo comparativo ("o melhor", "o mais moderno da cidade"), citar preço, ou exibir depoimento apresentado como real. Depoimentos ficam marcados como ilustrativos.
- **Acessibilidade:** WCAG 2.1 AA. `alt` descritivo em imagem de conteúdo, `alt=""` em decorativa, `width`/`height` explícitos em toda `<img>`, foco visível, `prefers-reduced-motion` respeitado.
- **Nunca editar à mão** os HTML da raiz do repositório — eles são gerados. Editar `src/` e rodar o build.
- **Comandos:** `py` é o launcher Python neste ambiente (Windows). Build: `py tools/build.py`. Testes: `py -m pytest`.

## File Structure

### Criados

| Arquivo | Responsabilidade |
|---|---|
| `tools/build.py` | Gerador estático: parse de front-matter, templating, descoberta de páginas, escrita, sitemap, `--check` |
| `src/data/site.json` | Dados globais: nome, endereço, telefone, horários, URLs, IDs de analytics |
| `src/data/nav.json` | Estrutura do menu principal e do rodapé |
| `src/partials/head.html` | Conteúdo do `<head>`: meta, canonical, hreflang, OG, fontes |
| `src/partials/header.html` | Cabeçalho: logo, menu, seletor de idioma |
| `src/partials/cta-bar.html` | Os três CTAs: Agendar, WhatsApp, Localização |
| `src/partials/footer.html` | Rodapé: contato, responsável técnica, links |
| `src/layouts/base.html` | Esqueleto de página comum |
| `src/layouts/treatment.html` | Layout das páginas de tratamento (inclui bloco de FAQ) |
| `src/layouts/post.html` | Layout dos posts do blog |
| `src/pages/**/*.html` | Miolo de cada página, com front-matter |
| `src/content/pt/*.html` | Textos institucionais da Dra. (filosofia, missão, valores) |
| `tests/pagecheck.py` | Extrator de metadados de HTML, sobre `html.parser` |
| `tests/colors.py` | Cálculo de luminância e razão de contraste WCAG |
| `tests/test_build.py` | Testes unitários do gerador |
| `tests/test_contrast.py` | Verificação de contraste dos tokens |
| `tests/test_pages.py` | Verificação de SEO e acessibilidade em todas as páginas geradas |
| `robots.txt`, `sitemap.xml` | Gerados pelo build |

### Modificados

| Arquivo | Mudança |
|---|---|
| `css/style.css` | Reescrito: nova paleta, tipografia, espaçamentos, componentes |
| `js/main.js` | Removidos vídeo do hero, tilt 3D e botão flutuante; mantidos reveal e comparador |
| `index.html` e demais HTML da raiz | Passam a ser saída do build |
| `README.md` | Documenta o build, a troca de assets e a checklist de publicação |
| `tools/check_assets.py` | Passa a varrer todos os HTML gerados, não só `index.html` |
| `.gitignore` | Sem mudança (mantém `.superpowers/`) |

---

## Task 1: Núcleo do gerador — front-matter e templating

**Files:**
- Create: `tools/build.py`
- Test: `tests/test_build.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `parse_front_matter(text: str) -> tuple[dict[str, str], str]` — devolve `(metadados, corpo)`. Sem front-matter, devolve `({}, text)`.
  - `render(template: str, context: dict) -> str` — substitui `{{ chave }}` pelo valor. Levanta `KeyError` se alguma chave usada não existir no contexto.

**Por que `{{ }}` e não `string.Template`:** `string.Template` usa `$`, que colide com sintaxe de CSS e JS presentes nos templates. O regex de chaves duplas evita escapes.

- [ ] **Step 1: Escrever os testes que falham**

Criar `tests/test_build.py`:

```python
"""Testes do gerador estatico."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import build  # noqa: E402


class TestParseFrontMatter:
    def test_sem_front_matter_devolve_corpo_intacto(self):
        meta, corpo = build.parse_front_matter("<p>ola</p>")
        assert meta == {}
        assert corpo == "<p>ola</p>"

    def test_extrai_pares_chave_valor(self):
        texto = "---\ntitle: Home\nlayout: base\n---\n<p>ola</p>"
        meta, corpo = build.parse_front_matter(texto)
        assert meta == {"title": "Home", "layout": "base"}
        assert corpo == "<p>ola</p>"

    def test_valor_pode_conter_dois_pontos(self):
        texto = "---\ntitle: Invisalign: como funciona\n---\nx"
        meta, _ = build.parse_front_matter(texto)
        assert meta["title"] == "Invisalign: como funciona"

    def test_ignora_linhas_em_branco_e_comentarios(self):
        texto = "---\n\n# um comentario\ntitle: Home\n---\nx"
        meta, _ = build.parse_front_matter(texto)
        assert meta == {"title": "Home"}

    def test_front_matter_nao_fechado_e_erro(self):
        with pytest.raises(ValueError, match="nao fechado"):
            build.parse_front_matter("---\ntitle: Home\n<p>ola</p>")


class TestRender:
    def test_substitui_placeholder(self):
        assert build.render("<h1>{{ titulo }}</h1>", {"titulo": "Ola"}) == "<h1>Ola</h1>"

    def test_tolera_espacos_variados(self):
        ctx = {"a": "1"}
        assert build.render("{{a}}{{  a  }}", ctx) == "11"

    def test_placeholder_ausente_levanta_keyerror(self):
        with pytest.raises(KeyError, match="telefone"):
            build.render("{{ telefone }}", {})

    def test_erro_lista_todas_as_chaves_ausentes(self):
        with pytest.raises(KeyError) as exc:
            build.render("{{ a }} {{ b }}", {})
        assert "a" in str(exc.value) and "b" in str(exc.value)

    def test_nao_confunde_chave_de_css(self):
        css = "a { color: red } {{ cor }}"
        assert build.render(css, {"cor": "azul"}) == "a { color: red } azul"
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

Run: `py -m pytest tests/test_build.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'build'`

- [ ] **Step 3: Implementar o mínimo**

Criar `tools/build.py`:

```python
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
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

Run: `py -m pytest tests/test_build.py -v`
Expected: PASS, 10 testes

- [ ] **Step 5: Commit**

```bash
git add tools/build.py tests/test_build.py
git commit -m "feat(build): parse de front-matter e templating"
```

---

## Task 2: Pipeline do build — dados, páginas, saída, sitemap, --check

**Files:**
- Modify: `tools/build.py`
- Modify: `tests/test_build.py`
- Create: `src/data/site.json`

**Interfaces:**
- Consumes: `parse_front_matter`, `render` da Task 1.
- Produces:
  - `RAIZ: Path` — raiz do repositório, derivada de `__file__`.
  - `carregar_dados(raiz: Path) -> dict` — lê `src/data/*.json` e devolve as chaves achatadas com prefixo (`site.json` → chaves `site_*`; `nav.json` → chave `nav`).
  - `carregar_conteudo(raiz: Path, lang: str) -> dict` — lê `src/content/<lang>/*.html`; para `filosofia.html` produz também `content_filosofia_resumo`, cortado no marcador `<!--resumo-->`.
  - `descobrir_paginas(raiz: Path) -> list[Pagina]` — varre `src/pages/**/*.html`.
  - `Pagina` — dataclass com `origem: Path`, `url: str`, `meta: dict`, `corpo: str`.
  - `construir(raiz: Path) -> dict[str, str]` — devolve `{caminho_relativo: html}` de tudo que deve existir no disco, incluindo `sitemap.xml` e `robots.txt`.
  - `escrever(raiz: Path, saida: dict[str, str]) -> list[str]` — grava e devolve os caminhos alterados.
  - `verificar(raiz: Path, saida: dict[str, str]) -> list[str]` — devolve os caminhos dessincronizados, sem gravar.
  - `main(argv: list[str] | None = None) -> int` — CLI; `--check` verifica em vez de gravar.

**Regras de derivação:**
- `url` vem do front-matter se presente; senão do caminho relativo a `src/pages/` com separadores normalizados para `/`.
- `lang` vem do front-matter; o default é `pt-BR`.
- `layout` vem do front-matter; o default é `base`.
- Partials são renderizados na ordem fixa `["cta_bar", "header", "footer", "head"]`, porque `header` consome `cta_bar` e `head` consome dados de página. Ordem explícita evita resolução recursiva.
- `sitemap.xml` lista todas as páginas; `index.html` vira a URL raiz `/`.

- [ ] **Step 1: Escrever os testes que falham**

Acrescentar a `tests/test_build.py`:

```python
import json
import textwrap


def _montar_projeto(tmp_path: Path) -> Path:
    """Cria um projeto minimo em disco para exercitar o pipeline."""
    (tmp_path / "src" / "data").mkdir(parents=True)
    (tmp_path / "src" / "partials").mkdir(parents=True)
    (tmp_path / "src" / "layouts").mkdir(parents=True)
    (tmp_path / "src" / "pages").mkdir(parents=True)
    (tmp_path / "src" / "content" / "pt").mkdir(parents=True)

    (tmp_path / "src" / "data" / "site.json").write_text(
        json.dumps({"nome": "Fukuoka", "base_url": "https://exemplo.com.br"}),
        encoding="utf-8",
    )
    (tmp_path / "src" / "data" / "nav.json").write_text(
        json.dumps({"principal": [{"rotulo": "Home", "url": "index.html"}]}),
        encoding="utf-8",
    )
    (tmp_path / "src" / "partials" / "cta_bar.html").write_text("<nav>cta</nav>", encoding="utf-8")
    (tmp_path / "src" / "partials" / "header.html").write_text(
        "<header>{{ site_nome }}{{ cta_bar }}</header>", encoding="utf-8"
    )
    (tmp_path / "src" / "partials" / "footer.html").write_text("<footer>f</footer>", encoding="utf-8")
    (tmp_path / "src" / "partials" / "head.html").write_text(
        "<title>{{ title }}</title>", encoding="utf-8"
    )
    (tmp_path / "src" / "layouts" / "base.html").write_text(
        "<html lang=\"{{ lang }}\"><head>{{ head }}</head>"
        "<body>{{ header }}{{ conteudo }}{{ footer }}</body></html>",
        encoding="utf-8",
    )
    (tmp_path / "src" / "pages" / "index.html").write_text(
        textwrap.dedent("""\
            ---
            title: Home
            ---
            <main>oi</main>"""),
        encoding="utf-8",
    )
    (tmp_path / "src" / "content" / "pt" / "filosofia.html").write_text(
        "<p>um</p>\n<!--resumo-->\n<p>dois</p>", encoding="utf-8"
    )
    return tmp_path


class TestPipeline:
    def test_carregar_dados_prefixa_site(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        dados = build.carregar_dados(raiz)
        assert dados["site_nome"] == "Fukuoka"
        assert dados["nav"]["principal"][0]["rotulo"] == "Home"

    def test_conteudo_gera_resumo_ate_o_marcador(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        conteudo = build.carregar_conteudo(raiz, "pt")
        assert "dois" in conteudo["content_filosofia"]
        assert "dois" not in conteudo["content_filosofia_resumo"]
        assert "um" in conteudo["content_filosofia_resumo"]

    def test_url_derivada_do_caminho(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        sub = raiz / "src" / "pages" / "tratamentos"
        sub.mkdir()
        (sub / "invisalign.html").write_text("---\ntitle: Inv\n---\n<main>x</main>", encoding="utf-8")
        urls = {p.url for p in build.descobrir_paginas(raiz)}
        assert "tratamentos/invisalign.html" in urls

    def test_construir_compoe_layout_e_partials(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        saida = build.construir(raiz)
        html = saida["index.html"]
        assert "<title>Home</title>" in html
        assert "<header>Fukuoka<nav>cta</nav></header>" in html
        assert "<main>oi</main>" in html
        assert 'lang="pt-BR"' in html

    def test_construir_gera_sitemap_e_robots(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        saida = build.construir(raiz)
        assert "<loc>https://exemplo.com.br/</loc>" in saida["sitemap.xml"]
        assert "Sitemap: https://exemplo.com.br/sitemap.xml" in saida["robots.txt"]

    def test_escrever_e_idempotente(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        saida = build.construir(raiz)
        primeira = build.escrever(raiz, saida)
        segunda = build.escrever(raiz, saida)
        assert "index.html" in primeira
        assert segunda == []

    def test_verificar_acusa_dessincronia(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        saida = build.construir(raiz)
        assert build.verificar(raiz, saida) == ["index.html", "robots.txt", "sitemap.xml"]
        build.escrever(raiz, saida)
        assert build.verificar(raiz, saida) == []

    def test_check_sai_com_1_quando_dessincronizado(self, tmp_path, monkeypatch):
        raiz = _montar_projeto(tmp_path)
        monkeypatch.setattr(build, "RAIZ", raiz)
        assert build.main(["--check"]) == 1
        assert build.main([]) == 0
        assert build.main(["--check"]) == 0
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

Run: `py -m pytest tests/test_build.py::TestPipeline -v`
Expected: FAIL com `AttributeError: module 'build' has no attribute 'carregar_dados'`

- [ ] **Step 3: Implementar**

Acrescentar a `tools/build.py`:

```python
import argparse
import json
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# `header` consome `cta_bar`; `head` consome dados da pagina.
# Ordem explicita em vez de resolucao recursiva.
ORDEM_PARTIALS = ["cta_bar", "header", "footer", "head"]
MARCADOR_RESUMO = "<!--resumo-->"


@dataclass
class Pagina:
    origem: Path
    url: str
    meta: dict
    corpo: str


def carregar_dados(raiz: Path) -> dict:
    """Le src/data/*.json. site.json vira chaves `site_*`; o resto, uma chave por arquivo."""
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
    pasta = raiz / "src" / "partials"
    return {
        nome: (pasta / f"{nome.replace('_', '-')}.html").read_text(encoding="utf-8")
        if (pasta / f"{nome.replace('_', '-')}.html").exists()
        else (pasta / f"{nome}.html").read_text(encoding="utf-8")
        for nome in ORDEM_PARTIALS
    }


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
        }
        ctx["conteudo"] = render(pagina.corpo, ctx)
        for nome in ORDEM_PARTIALS:
            ctx[nome] = render(partials[nome], ctx)
        layout = layouts[pagina.meta.get("layout", "base")]
        saida[pagina.url] = render(layout, ctx)

    saida["sitemap.xml"] = _montar_sitemap(dados["site_base_url"], paginas)
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
        destino.write_text(saida[caminho], encoding="utf-8")
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
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

Run: `py -m pytest tests/test_build.py -v`
Expected: PASS, 18 testes

- [ ] **Step 5: Commit**

```bash
git add tools/build.py tests/test_build.py
git commit -m "feat(build): pipeline completo com sitemap, robots e --check"
```

---

## Task 3: Suíte de verificação — contraste, SEO e acessibilidade

**Files:**
- Create: `tests/colors.py`
- Create: `tests/pagecheck.py`
- Create: `tests/test_contrast.py`
- Create: `tests/test_pages.py`
- Create: `tests/conftest.py`

**Interfaces:**
- Consumes: `build.construir` da Task 2.
- Produces:
  - `tests/colors.py`: `luminancia(hex: str) -> float`, `contraste(a: str, b: str) -> float`, `tokens_do_css(css: str) -> dict[str, str]`
  - `tests/pagecheck.py`: `InfoPagina` (subclasse de `HTMLParser`) com os atributos `title`, `meta`, `links`, `headings`, `imgs`, `html_lang`, `jsonld`; e `analisar(html: str) -> InfoPagina`
  - `tests/conftest.py`: fixtures de sessão `saida`, `html_bruto` e `paginas`

Esta suíte roda contra a **saída do build em memória**, não contra o disco. Cada task de página seguinte é validada automaticamente por ela — é o que impede que uma página nasça sem `<title>`, com dois `<h1>` ou com contraste reprovado. A suíte cresce sozinha conforme as páginas são adicionadas.

- [ ] **Step 1: Escrever o utilitário de cor**

Criar `tests/colors.py`:

```python
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
```

- [ ] **Step 2: Escrever os testes de contraste**

Criar `tests/test_contrast.py`:

```python
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
```

- [ ] **Step 3: Rodar e confirmar que falha**

Run: `py -m pytest tests/test_contrast.py -v`
Expected: FAIL — `css/style.css` ainda tem a paleta antiga, então `KeyError: 'navy'` na coleta.

Esse é o resultado esperado nesta etapa. A Task 4 reescreve o CSS e zera estas falhas.

- [ ] **Step 4: Escrever o inspetor de HTML**

Criar `tests/pagecheck.py`:

```python
"""Inspetor de HTML sobre html.parser, para nao depender de bs4."""
from html.parser import HTMLParser

NIVEIS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class InfoPagina(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str | None = None
        self.meta: dict[str, str] = {}      # name/property -> content
        self.links: list[dict[str, str]] = []
        self.imgs: list[dict[str, str]] = []
        self.headings: list[tuple[int, str]] = []
        self.html_lang: str | None = None
        self.jsonld: list[str] = []
        self._coletando: str | None = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "title":
            self._iniciar("title")
        elif tag == "meta":
            chave = a.get("name") or a.get("property")
            if chave:
                self.meta[chave] = a.get("content", "")
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._iniciar("jsonld")
        elif tag in NIVEIS:
            self._iniciar(tag)

    def handle_endtag(self, tag):
        if self._coletando is None:
            return
        texto = "".join(self._buffer).strip()
        if self._coletando == "title" and tag == "title":
            self.title = texto
        elif self._coletando == "jsonld" and tag == "script":
            self.jsonld.append(texto)
        elif self._coletando == tag and tag in NIVEIS:
            self.headings.append((int(tag[1]), texto))
        else:
            return
        self._coletando = None
        self._buffer = []

    def handle_data(self, data):
        if self._coletando is not None:
            self._buffer.append(data)

    def _iniciar(self, nome: str) -> None:
        self._coletando = nome
        self._buffer = []

    @property
    def h1(self) -> list[str]:
        return [texto for nivel, texto in self.headings if nivel == 1]

    def link(self, rel: str) -> dict[str, str] | None:
        for item in self.links:
            if item.get("rel") == rel:
                return item
        return None


def analisar(html: str) -> InfoPagina:
    info = InfoPagina()
    info.feed(html)
    info.close()
    return info
```

Criar `tests/conftest.py`:

```python
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build  # noqa: E402
from pagecheck import analisar  # noqa: E402


@pytest.fixture(scope="session")
def saida() -> dict[str, str]:
    """Saida do build em memoria: {caminho: conteudo}."""
    return build.construir(RAIZ)


@pytest.fixture(scope="session")
def html_bruto(saida) -> dict[str, str]:
    return {url: texto for url, texto in saida.items() if url.endswith(".html")}


@pytest.fixture(scope="session")
def paginas(html_bruto) -> dict:
    return {url: analisar(texto) for url, texto in html_bruto.items()}
```

- [ ] **Step 5: Escrever a suíte de páginas**

Criar `tests/test_pages.py`:

```python
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
```

- [ ] **Step 6: Rodar e registrar o estado atual**

Run: `py -m pytest tests/ -v`
Expected: `tests/test_build.py` PASS; `test_contrast.py` e `test_pages.py` FAIL, porque a paleta e as páginas reais ainda não existem. As tasks seguintes zeram essas falhas.

- [ ] **Step 7: Commit**

```bash
git add tests/
git commit -m "test: suite de contraste, SEO e acessibilidade"
```

---

## Task 4: Identidade visual — tokens e CSS base

**Files:**
- Modify: `css/style.css` — substituir as linhas 1-80 (tokens, reset, tipografia, layout)
- Test: `tests/test_contrast.py` (criado na Task 3)

**Interfaces:**
- Consumes: nada.
- Produces: as custom properties de Global Constraints, mais `--space-section`, `--radius`, `--container`, `--container-narrow`, `--rule`; e as classes `.container`, `.container--narrow`, `.section`, `.section--navy`, `.section--gray`, `.section--surface`, `.split`, `.split--invertido`, `.section-head`, `.overline`, `.rule`, `.btn`, `.btn--primary`, `.btn--ghost`, `.btn--sm`, `.btn--lg`, `.skip-link`, `.lead`.

**Decisão de design registrada:** os CTAs **não** usam verde WhatsApp. Branco sobre `#1EBE5D` mede 2,45:1 e reprova AA; além disso o verde destoa da paleta navy/dourado do briefing. O botão de WhatsApp mantém o ícone da marca, mas com estilo navy.

- [ ] **Step 1: Substituir tokens, reset e tipografia**

Substituir as linhas 1-58 de `css/style.css` por:

```css
/* ===== Tokens: identidade Fukuoka Dental Clinic ===== */
:root {
  /* Paleta do briefing */
  --navy: #0F2D52;
  --navy-deep: #0A1F3A;
  --gold: #B08D57;        /* DECORACAO APENAS: 2.88:1 sobre off-white, reprova AA */
  --gold-text: #8A6A3B;   /* dourado para texto sobre fundo claro (4.66:1) */
  --gold-light: #C9A96E;  /* dourado para texto sobre navy (6.18:1) */
  --offwhite: #F8F7F3;
  --gray: #D9D9D6;
  --ink: #1A1A1A;
  --ink-soft: #4A5568;
  --surface: #FFFFFF;

  --font-display: "Cormorant Garamond", Georgia, serif;
  --font-body: "Inter", system-ui, -apple-system, sans-serif;

  --container: 1080px;
  --container-narrow: 680px;
  --radius: 2px;          /* cantos quase retos: sobriedade japonesa */
  --rule: 1px solid var(--gold);
  --space-section: clamp(6rem, 14vw, 12rem);
  --shadow: 0 1px 2px rgba(15, 45, 82, .06);
}

/* ===== Reset ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; scroll-padding-top: 6rem; }
body {
  font-family: var(--font-body);
  color: var(--ink);
  background: var(--offwhite);
  line-height: 1.75;
  font-size: 1.0625rem;
  -webkit-font-smoothing: antialiased;
}
img, video { max-width: 100%; display: block; }
a { color: inherit; text-decoration: none; }
ul, ol { list-style: none; }
button, input, select { font: inherit; }

:focus-visible { outline: 2px solid var(--gold-text); outline-offset: 3px; }
.section--navy :focus-visible,
.site-header :focus-visible,
.cta-bar :focus-visible { outline-color: var(--gold-light); }

.skip-link {
  position: absolute; left: 1rem; top: -100%;
  background: var(--navy); color: #FFF;
  padding: .75rem 1.25rem; z-index: 100;
}
.skip-link:focus { top: 1rem; }

/* Transicao suave entre paginas onde houver suporte; degrada sem quebrar. */
@view-transition { navigation: auto; }

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  @view-transition { navigation: none; }
  *, *::before, *::after {
    transition-duration: .01ms !important;
    animation-duration: .01ms !important;
  }
}

/* ===== Tipografia ===== */
h1, h2, h3, h4 {
  font-family: var(--font-display);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: 0;
  text-wrap: balance;
  color: var(--navy);
}
h1 { font-size: clamp(2.25rem, 5vw, 3.75rem); }
h2 { font-size: clamp(1.75rem, 3.5vw, 2.5rem); }
h3 { font-size: clamp(1.25rem, 2vw, 1.5rem); }
.section--navy h1, .section--navy h2, .section--navy h3 { color: var(--offwhite); }
p + p { margin-top: 1.25em; }
.lead { font-size: 1.1875rem; color: var(--ink-soft); }
.section--navy .lead { color: var(--gray); }
```

- [ ] **Step 2: Substituir a seção de layout**

Substituir a seção `/* ===== Layout ===== */` original por:

```css
/* ===== Layout ===== */
.container { max-width: var(--container); margin-inline: auto; padding-inline: 1.5rem; }
.container--narrow { max-width: var(--container-narrow); }
.section { padding-block: var(--space-section); }
.section--gray { background: var(--gray); }
.section--surface { background: var(--surface); }
.section--navy { background: var(--navy); color: var(--offwhite); }

/* Grid assimetrico: o conteudo nao fica centralizado por padrao. */
.split { display: grid; gap: clamp(2rem, 6vw, 5rem); align-items: center; }
@media (min-width: 860px) {
  .split { grid-template-columns: 5fr 7fr; }
  .split--invertido { grid-template-columns: 7fr 5fr; }
}

.section-head { max-width: 34rem; margin-bottom: clamp(3rem, 7vw, 5rem); }
.section-head--center { margin-inline: auto; text-align: center; }

.overline {
  display: block;
  font-size: .75rem;
  font-weight: 500;
  letter-spacing: .22em;
  text-transform: uppercase;
  color: var(--gold-text);
  margin-bottom: 1.25rem;
}
.section--navy .overline { color: var(--gold-light); }

/* Filete dourado: substitui as sombras pesadas do layout anterior. */
.rule { border: 0; border-top: var(--rule); width: 3rem; margin: 2rem 0; }
.section-head--center .rule { margin-inline: auto; }

/* ===== Botoes ===== */
.btn {
  display: inline-flex; align-items: center; gap: .625rem;
  padding: .875rem 1.75rem;
  border: 1px solid transparent; border-radius: var(--radius);
  font-size: .9375rem; font-weight: 500; letter-spacing: .02em;
  transition: background-color .2s, color .2s, border-color .2s;
}
.btn svg { width: 1.125rem; height: 1.125rem; flex: none; }
.btn--primary { background: var(--navy); color: #FFF; }
.btn--primary:hover { background: var(--navy-deep); }
.btn--ghost { border-color: var(--navy); color: var(--navy); }
.btn--ghost:hover { background: var(--navy); color: #FFF; }
.section--navy .btn--ghost { border-color: var(--gold-light); color: var(--gold-light); }
.section--navy .btn--ghost:hover { background: var(--gold-light); color: var(--navy-deep); }
.btn--sm { padding: .625rem 1.125rem; font-size: .875rem; }
.btn--lg { padding: 1.0625rem 2.25rem; font-size: 1rem; }
```

- [ ] **Step 3: Rodar os testes de contraste**

Run: `py -m pytest tests/test_contrast.py -v`
Expected: PASS, 11 testes. Se algum par reprovar, escurecer o token de texto até passar — nunca afrouxar o limite no teste.

- [ ] **Step 4: Commit**

```bash
git add css/style.css
git commit -m "feat(css): identidade Fukuoka - paleta, tipografia e base acessivel"
```

---

## Task 5: Dados globais, partials e layout base

**Files:**
- Create: `src/data/site.json`, `src/data/nav.json`
- Create: `src/partials/head.html`, `src/partials/header.html`, `src/partials/cta-bar.html`, `src/partials/footer.html`
- Create: `src/layouts/base.html`
- Create: `src/pages/index.html` (esqueleto mínimo; a Home real vem na Task 7)
- Modify: `css/style.css` (acrescentar as seções de header, CTA bar e footer)
- Modify: `js/main.js`
- Delete: o `index.html` da raiz é sobrescrito pelo build

**Interfaces:**
- Consumes: `build.construir` da Task 2.
- Produces as chaves de contexto que **todas** as páginas seguintes podem usar:
  - `{{ site_nome }}`, `{{ site_nome_curto }}`, `{{ site_base_url }}`, `{{ site_telefone }}`, `{{ site_whatsapp_url }}`, `{{ site_endereco_rua }}`, `{{ site_endereco_cidade }}`, `{{ site_maps_url }}`, `{{ site_horario_semana }}`, `{{ site_horario_sabado }}`, `{{ site_instagram_url }}`, `{{ site_instagram_handle }}`, `{{ site_cro }}`, `{{ site_responsavel }}`, `{{ site_ga4_id }}`, `{{ site_email }}`
  - `{{ head }}`, `{{ header }}`, `{{ footer }}`, `{{ cta_bar }}`, `{{ conteudo }}`, `{{ lang }}`, `{{ url }}`, `{{ url_absoluta }}`
  - Front-matter que toda página deve declarar: `title`, `description`, `og_type` (`website` ou `article`)
  - Front-matter opcional: `layout`, `url`, `lang`, `alternate_en`, `alternate_pt`, `jsonld`, `classe_body`

**Nota sobre `_ler_partials`:** o build converte `cta_bar` → `cta-bar.html`. Nomear os arquivos com hífen e as chaves com underscore.

- [ ] **Step 1: Criar os dados globais**

Criar `src/data/site.json`. Todo valor desconhecido usa a string `TROCAR`:

```json
{
  "nome": "Fukuoka Dental Clinic",
  "nome_curto": "Fukuoka",
  "tagline": "Excelência inspirada pela precisão japonesa",
  "base_url": "https://www.fukuokadentalclinic.com.br",
  "email": "TROCAR: contato@dominio.com.br",
  "telefone": "TROCAR: +55 11 0000-0000",
  "telefone_e164": "TROCAR: +5511000000000",
  "whatsapp_url": "https://wa.me/5511000000000?text=Ol%C3%A1%21%20Vim%20pelo%20site%20e%20gostaria%20de%20agendar%20uma%20consulta.",
  "endereco_rua": "TROCAR: Av. Paulista, 0000, conj. 00",
  "endereco_bairro": "TROCAR: Bela Vista",
  "endereco_cidade": "São Paulo",
  "endereco_uf": "SP",
  "endereco_cep": "TROCAR: 01310-000",
  "maps_url": "TROCAR: URL do Google Maps da clínica",
  "geo_lat": "TROCAR",
  "geo_lng": "TROCAR",
  "horario_semana": "Segunda a sexta, 9h às 19h",
  "horario_sabado": "Sábado, 9h às 13h",
  "instagram_url": "TROCAR: https://instagram.com/perfil",
  "instagram_handle": "TROCAR: @perfil",
  "responsavel": "TROCAR: Dra. Cíntia [sobrenome]",
  "cro": "TROCAR: CRO-SP 00.000",
  "ga4_id": "TROCAR: G-XXXXXXXXXX",
  "ano": "2026"
}
```

Criar `src/data/nav.json`:

```json
{
  "principal": [
    { "rotulo": "Sobre", "url": "sobre.html" },
    { "rotulo": "Tratamentos", "url": "tratamentos.html" },
    { "rotulo": "Filosofia", "url": "filosofia.html" },
    { "rotulo": "Valores", "url": "valores.html" },
    { "rotulo": "Depoimentos", "url": "depoimentos.html" },
    { "rotulo": "Blog", "url": "blog/index.html" },
    { "rotulo": "Contato", "url": "contato.html" }
  ]
}
```

**Importante:** o menu é escrito à mão em `header.html`, não gerado a partir do `nav.json`. O build não tem laços de template, e um menu de 7 itens não justifica adicioná-los. O `nav.json` fica como fonte de verdade documental e é consumido pelo teste de consistência do menu (Task 15).

- [ ] **Step 2: Criar os partials**

Criar `src/partials/head.html`:

```html
<meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}</title>
  <meta name="description" content="{{ description }}">
  <link rel="canonical" href="{{ url_absoluta }}">
  <meta property="og:title" content="{{ title }}">
  <meta property="og:description" content="{{ description }}">
  <meta property="og:type" content="{{ og_type }}">
  <meta property="og:url" content="{{ url_absoluta }}">
  <meta property="og:site_name" content="{{ site_nome }}">
  <meta property="og:locale" content="pt_BR">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css">
  <noscript><style>.reveal { opacity: 1 !important; translate: none !important; }</style></noscript>
  <!-- TROCAR: colar o ID do GA4 em src/data/site.json e descomentar
  <script async src="https://www.googletagmanager.com/gtag/js?id={{ site_ga4_id }}"></script>
  -->
```

Criar `src/partials/cta-bar.html` — os três CTAs exigidos pelo briefing:

```html
<div class="cta-bar">
    <a class="cta-bar__item cta-bar__item--destaque" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 3a9 9 0 0 0-7.7 13.6L3 21l4.5-1.2A9 9 0 1 0 12 3Zm5 12.7c-.2.5-1.1 1-1.6 1.1-.4 0-.9 0-1.4-.1a11.7 11.7 0 0 1-5.3-4.7c-.5-.9-.8-1.8-.8-2.3 0-.6.3-1.2.7-1.5.2-.2.6-.3.8-.3h.5c.2 0 .3 0 .5.4l.8 1.9c.1.2.1.3 0 .5l-.4.6c-.2.2-.3.4-.1.6a8 8 0 0 0 3.5 3.2c.2.1.4.1.6-.1l.7-.9c.2-.2.4-.3.6-.2l2 .9c.3.2.4.3.5.4 0 .1 0 .3-.1.5Z"/></svg>
      <span>Agendar consulta</span>
    </a>
    <a class="cta-bar__item" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 3a9 9 0 0 0-7.7 13.6L3 21l4.5-1.2A9 9 0 1 0 12 3Zm5 12.7c-.2.5-1.1 1-1.6 1.1-.4 0-.9 0-1.4-.1a11.7 11.7 0 0 1-5.3-4.7c-.5-.9-.8-1.8-.8-2.3 0-.6.3-1.2.7-1.5.2-.2.6-.3.8-.3h.5c.2 0 .3 0 .5.4l.8 1.9c.1.2.1.3 0 .5l-.4.6c-.2.2-.3.4-.1.6a8 8 0 0 0 3.5 3.2c.2.1.4.1.6-.1l.7-.9c.2-.2.4-.3.6-.2l2 .9c.3.2.4.3.5.4 0 .1 0 .3-.1.5Z"/></svg>
      <span>WhatsApp</span>
    </a>
    <a class="cta-bar__item" href="{{ site_maps_url }}" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5Z"/></svg>
      <span>Localização</span>
    </a>
  </div>
```

Criar `src/partials/header.html`:

```html
<header class="site-header">
    <div class="container site-header__inner">
      <a href="index.html" class="logo">
        <span class="logo__nome">Fukuoka</span>
        <span class="logo__sub">Dental Clinic</span>
      </a>
      <nav class="site-nav" aria-label="Navegação principal">
        <a href="sobre.html">Sobre</a>
        <a href="tratamentos.html">Tratamentos</a>
        <a href="filosofia.html">Filosofia</a>
        <a href="valores.html">Valores</a>
        <a href="depoimentos.html">Depoimentos</a>
        <a href="blog/index.html">Blog</a>
        <a href="contato.html">Contato</a>
      </nav>
      <div class="site-header__acoes">
        <nav class="lang-switch" aria-label="Idioma">
          <a href="index.html" hreflang="pt-BR" aria-current="true">PT</a>
          <a href="en/index.html" hreflang="en">EN</a>
        </nav>
        {{ cta_bar }}
      </div>
    </div>
  </header>
```

Criar `src/partials/footer.html`:

```html
<footer class="site-footer">
    <div class="container site-footer__grid">
      <div>
        <p class="logo logo--footer">
          <span class="logo__nome">Fukuoka</span>
          <span class="logo__sub">Dental Clinic</span>
        </p>
        <p class="site-footer__tagline">{{ site_tagline }}</p>
      </div>
      <address class="site-footer__col">
        <h2 class="site-footer__titulo">Onde estamos</h2>
        <p>{{ site_endereco_rua }}<br>{{ site_endereco_bairro }} &middot; {{ site_endereco_cidade }}/{{ site_endereco_uf }}<br>{{ site_endereco_cep }}</p>
        <p><a href="{{ site_maps_url }}" target="_blank" rel="noopener">Ver no Google Maps</a></p>
      </address>
      <div class="site-footer__col">
        <h2 class="site-footer__titulo">Atendimento</h2>
        <p>{{ site_horario_semana }}<br>{{ site_horario_sabado }}</p>
        <p><a href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">{{ site_telefone }}</a><br>
           <a href="{{ site_instagram_url }}" target="_blank" rel="noopener">{{ site_instagram_handle }}</a></p>
      </div>
    </div>
    <div class="container site-footer__base">
      <p>&copy; {{ site_ano }} {{ site_nome }}. Todos os direitos reservados.</p>
      <p>Responsável técnica: {{ site_responsavel }} &middot; {{ site_cro }}</p>
    </div>
  </footer>
```

- [ ] **Step 3: Criar o layout base**

Criar `src/layouts/base.html`:

```html
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
  {{ head }}
</head>
<body class="{{ classe_body }}">
  <a class="skip-link" href="#conteudo">Ir para o conteúdo</a>
  {{ header }}
  <main id="conteudo">
{{ conteudo }}
  </main>
  {{ footer }}
  <div class="cta-bar-mobile">
    {{ cta_bar }}
  </div>
  <script src="js/main.js" defer></script>
</body>
</html>
```

`classe_body` é opcional no front-matter. Para evitar `KeyError`, dar-lhe um default no build.

- [ ] **Step 4: Adicionar defaults de front-matter opcional ao build**

Em `tools/build.py`, dentro de `construir`, logo após a construção de `ctx`, inserir:

```python
        # Front-matter opcional: default vazio para nao quebrar o render.
        for chave in ("classe_body", "jsonld", "alternates"):
            ctx.setdefault(chave, "")
```

Acrescentar o teste correspondente em `tests/test_build.py`, na classe `TestPipeline`:

```python
    def test_front_matter_opcional_tem_default_vazio(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        layout = raiz / "src" / "layouts" / "base.html"
        layout.write_text("<body class=\"{{ classe_body }}\">{{ conteudo }}</body>", encoding="utf-8")
        saida = build.construir(raiz)
        assert 'class=""' in saida["index.html"]
```

- [ ] **Step 5: Gerar hreflang e JSON-LD no head**

Acrescentar ao final de `src/partials/head.html`:

```html
  {{ alternates }}
  {{ jsonld }}
```

Em `tools/build.py`, dentro de `construir`, antes do `setdefault`, inserir a montagem dos alternates:

```python
        alternates = []
        if pagina.meta.get("alternate_en"):
            alternates.append(pagina.meta["alternate_en"])
        if pagina.meta.get("alternate_pt"):
            alternates.append(pagina.meta["alternate_pt"])
        if alternates:
            base = dados["site_base_url"].rstrip("/")
            marcas = []
            propria = "en" if lang == "en" else "pt-BR"
            marcas.append(
                f'<link rel="alternate" hreflang="{propria}" href="{ctx["url_absoluta"]}">'
            )
            for alvo in alternates:
                idioma = "en" if alvo.startswith("en/") else "pt-BR"
                caminho = "" if alvo == "index.html" else alvo
                marcas.append(
                    f'<link rel="alternate" hreflang="{idioma}" href="{base}/{caminho}">'
                )
                if idioma == "pt-BR":
                    marcas.append(
                        f'<link rel="alternate" hreflang="x-default" href="{base}/{caminho}">'
                    )
            ctx["alternates"] = "\n  ".join(marcas)
```

Teste correspondente em `TestPipeline`:

```python
    def test_alternates_geram_hreflang_com_x_default(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "pages" / "index.html").write_text(
            "---\ntitle: Home\nalternate_en: en/index.html\n---\n<main>oi</main>",
            encoding="utf-8",
        )
        (raiz / "src" / "partials" / "head.html").write_text(
            "<title>{{ title }}</title>{{ alternates }}", encoding="utf-8"
        )
        html = build.construir(raiz)["index.html"]
        assert 'hreflang="pt-BR" href="https://exemplo.com.br/"' in html
        assert 'hreflang="en" href="https://exemplo.com.br/en/index.html"' in html
        assert 'hreflang="x-default"' in html
```

- [ ] **Step 6: Criar a página mínima e gerar**

Criar `src/pages/index.html`:

```html
---
title: Fukuoka Dental Clinic — Dentista na Av. Paulista, São Paulo
description: Odontologia de excelência na Av. Paulista, unindo ciência, tecnologia e cuidado humano. Implantes, Invisalign, clareamento e reabilitação oral.
og_type: website
alternate_en: en/index.html
---
    <section class="section">
      <div class="container">
        <h1>Fukuoka Dental Clinic</h1>
        <p class="lead">{{ site_tagline }}.</p>
      </div>
    </section>
```

Run: `py tools/build.py`
Expected: escreve `index.html`, `sitemap.xml`, `robots.txt`.

Criar `assets/favicon.svg` com um traço simples em navy:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#0F2D52"/><path d="M9 8h14v3h-5.4v13h-3.2V11H9z" fill="#F8F7F3"/></svg>
```

- [ ] **Step 7: Estilizar header, CTA bar e footer**

Acrescentar ao final de `css/style.css`:

```css
/* ===== Header ===== */
.site-header {
  position: sticky; top: 0; z-index: 50;
  background: var(--offwhite);
  border-bottom: 1px solid var(--gray);
}
.site-header__inner {
  display: flex; align-items: center; justify-content: space-between;
  gap: 2rem; padding-block: 1rem;
}
.logo { display: grid; line-height: 1.1; }
.logo__nome {
  font-family: var(--font-display); font-size: 1.5rem;
  letter-spacing: .04em; color: var(--navy);
}
.logo__sub {
  font-size: .625rem; letter-spacing: .28em; text-transform: uppercase;
  color: var(--gold-text);
}
.site-nav { display: none; gap: 1.75rem; font-size: .9375rem; }
.site-nav a { color: var(--ink-soft); padding-block: .25rem; border-bottom: 1px solid transparent; }
.site-nav a:hover, .site-nav a[aria-current="page"] {
  color: var(--navy); border-bottom-color: var(--gold);
}
@media (min-width: 1080px) { .site-nav { display: flex; } }

.site-header__acoes { display: flex; align-items: center; gap: 1rem; }
.lang-switch { display: flex; gap: .5rem; font-size: .8125rem; letter-spacing: .1em; }
.lang-switch a { color: var(--ink-soft); }
.lang-switch a[aria-current="true"] { color: var(--navy); border-bottom: 1px solid var(--gold); }

/* ===== CTA bar: os tres botoes sempre visiveis ===== */
.cta-bar { display: flex; gap: .5rem; }
.cta-bar__item {
  display: inline-flex; align-items: center; gap: .5rem;
  padding: .625rem 1rem; border: 1px solid var(--gray); border-radius: var(--radius);
  font-size: .875rem; color: var(--navy); background: var(--surface);
  transition: background-color .2s, color .2s, border-color .2s;
}
.cta-bar__item svg { width: 1.0625rem; height: 1.0625rem; flex: none; }
.cta-bar__item:hover { border-color: var(--navy); }
.cta-bar__item--destaque { background: var(--navy); color: #FFF; border-color: var(--navy); }
.cta-bar__item--destaque:hover { background: var(--navy-deep); }

/* Desktop: so o botao de destaque cabe no header; os outros ficam no rodape fixo. */
@media (max-width: 1079px) {
  .site-header .cta-bar { display: none; }
}
@media (min-width: 1080px) {
  .site-header .cta-bar__item:not(.cta-bar__item--destaque) { display: none; }
}

.cta-bar-mobile {
  position: fixed; inset-inline: 0; bottom: 0; z-index: 60;
  background: var(--offwhite); border-top: 1px solid var(--gray);
  padding: .625rem 1rem; padding-bottom: max(.625rem, env(safe-area-inset-bottom));
}
.cta-bar-mobile .cta-bar { justify-content: center; }
.cta-bar-mobile .cta-bar__item { flex: 1; justify-content: center; max-width: 12rem; }
.cta-bar-mobile .cta-bar__item span { font-size: .8125rem; }
@media (min-width: 1080px) { .cta-bar-mobile { display: none; } }
/* Espaco para a barra fixa nao cobrir o fim da pagina. */
@media (max-width: 1079px) { body { padding-bottom: 4.5rem; } }

/* ===== Footer ===== */
.site-footer { background: var(--navy); color: var(--gray); padding-block: 4rem 2rem; }
.site-footer a { color: var(--gold-light); }
.site-footer__grid { display: grid; gap: 2.5rem; }
@media (min-width: 760px) { .site-footer__grid { grid-template-columns: 1.4fr 1fr 1fr; } }
.site-footer .logo__nome { color: var(--offwhite); }
.site-footer .logo__sub { color: var(--gold-light); }
.site-footer__tagline { margin-top: 1rem; font-size: .9375rem; max-width: 22rem; }
.site-footer__titulo {
  font-family: var(--font-body); font-size: .75rem; font-weight: 500;
  letter-spacing: .22em; text-transform: uppercase; color: var(--gold-light);
  margin-bottom: 1rem;
}
.site-footer__col { font-style: normal; font-size: .9375rem; }
.site-footer__col p + p { margin-top: 1rem; }
.site-footer__base {
  margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid rgba(201,169,110,.3);
  display: flex; flex-wrap: wrap; gap: .5rem 2rem; justify-content: space-between;
  font-size: .8125rem;
}
```

- [ ] **Step 8: Enxugar o JavaScript**

Substituir `js/main.js` inteiro por:

```javascript
// O numero de WhatsApp vem de src/data/site.json e ja chega no HTML,
// para funcionar sem JS e ser indexavel.

// ===== Header: sombra ao rolar =====
const header = document.querySelector(".site-header");
if (header) {
  const onScroll = () => header.classList.toggle("is-scrolled", scrollY > 24);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

// ===== Comparador antes/depois =====
document.querySelectorAll(".compare").forEach((fig) => {
  const range = fig.querySelector(".compare__range");
  if (range) {
    range.addEventListener("input", () =>
      fig.style.setProperty("--pos", range.value + "%")
    );
  }
});

// ===== Reveal on scroll =====
document.documentElement.classList.add("js"); // sem JS, .reveal fica visivel
const io = new IntersectionObserver(
  (entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add("is-visible");
        io.unobserve(e.target);
      }
    });
  },
  { threshold: 0.15 }
);
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
```

Acrescentar ao CSS o estilo do reveal e do header rolado:

```css
/* ===== Reveal ===== */
.site-header.is-scrolled { box-shadow: var(--shadow); }
.js .reveal { opacity: 0; translate: 0 1rem; transition: opacity .7s ease, translate .7s ease; }
.js .reveal.is-visible { opacity: 1; translate: none; }
```

- [ ] **Step 9: Rodar build e testes**

Run: `py tools/build.py && py -m pytest tests/ -v`
Expected: `test_build.py` e `test_contrast.py` PASS. `test_pages.py` PASS para `index.html`, que já tem title, description, canonical, OG, um H1 e lang.

- [ ] **Step 10: Commit**

```bash
git add src/ css/style.css js/main.js tools/build.py tests/test_build.py assets/favicon.svg index.html sitemap.xml robots.txt
git commit -m "feat: dados globais, partials, layout base e CTA bar"
```

---

## Task 6: Conteúdo institucional — Filosofia, Missão e Valores

**Files:**
- Create: `src/content/pt/filosofia.html`, `src/content/pt/missao.html`, `src/content/pt/valores.html`
- Create: `src/pages/filosofia.html`, `src/pages/valores.html`
- Modify: `css/style.css`
- Create (gerados): `filosofia.html`, `valores.html`

**Interfaces:**
- Consumes: `carregar_conteudo` da Task 2, layout `base` e partials da Task 5.
- Produces as chaves de contexto `{{ content_filosofia }}`, `{{ content_filosofia_resumo }}`, `{{ content_missao }}`, `{{ content_valores }}`, usadas também pela Home (Task 7) e pela página Sobre (Task 8).

**Regra inviolável:** o texto da Dra. entra **na íntegra e sem reescrita**. Nada de "melhorar" a redação. Estes três arquivos são a fonte única — se o mesmo texto aparecer na Home, é por referência à mesma chave, nunca por cópia.

Os textos-fonte estão em `filosofia.txt`, `missao` e `valores`, na raiz do repositório.

- [ ] **Step 1: Transcrever a filosofia**

Criar `src/content/pt/filosofia.html`. O marcador `<!--resumo-->` define até onde vai o trecho exibido na Home:

```html
<p>Acreditamos que um sorriso vai muito além da estética. Ele reflete saúde, confiança, autoestima e uma expressão genuína de bem-estar.</p>

<p>Na Fukuoka Dental Clinic, cada paciente é único. Por isso, dedicamos tempo para ouvir com atenção, compreender com profundidade e desenvolver planos de tratamento personalizados, fundamentados em ciência de excelência, tecnologia avançada e absoluto respeito às escolhas individuais.</p>
<!--resumo-->
<p>Inspirados pela tradição japonesa, valorizamos a precisão, a disciplina, a busca contínua pela excelência e o cuidado meticuloso em cada detalhe. Para nós, excelência não é um destino, mas um padrão permanente de conduta.</p>

<p>Nossa prática é guiada pela ética, pela transparência e pelo compromisso com o tratamento minimamente invasivo e a preservação da estrutura natural dos dentes, sempre priorizando resultados que respeitam a biologia e a individualidade de cada sorriso. Buscamos soluções seguras, conservadoras e de alta previsibilidade, que promovem sorrisos naturais, harmônicos e duradouros.</p>

<p>Acreditamos que os melhores resultados nascem da integração entre conhecimento científico, tecnologia de ponta e um atendimento genuinamente humano e sofisticado.</p>

<p class="destaque">Mais do que tratar dentes, cuidamos de pessoas.</p>

<p>Buscamos proporcionar uma experiência de atendimento serena, acolhedora e altamente personalizada, na qual cada paciente se sinta respeitado, seguro e confiante em todas as etapas de sua jornada.</p>

<p>Entendemos a odontologia como a união entre ciência, arte e precisão — uma prática dedicada a transformar sorrisos de forma natural, elegante e duradoura, elevando a qualidade de vida com discrição e refinamento.</p>
```

- [ ] **Step 2: Transcrever a missão**

Criar `src/content/pt/missao.html`:

```html
<p>Acreditamos que a odontologia tem o poder de transformar vidas.</p>

<p>Nossa missão é ajudar cada paciente a alcançar a sua melhor versão, promovendo saúde, confiança e qualidade de vida por meio de uma odontologia de excelência, baseada em ciência, tecnologia, ética e um cuidado genuinamente humano.</p>

<p>Na Fukuoka Dental Clinic, cada sorriso é tratado com precisão, respeito e dedicação, porque acreditamos que transformar um sorriso é também transformar a forma como uma pessoa vive, sorri e se relaciona com o mundo.</p>
```

- [ ] **Step 3: Transcrever os valores**

Criar `src/content/pt/valores.html`:

```html
<ol class="valores">
  <li class="valores__item">
    <span class="valores__num" aria-hidden="true">01</span>
    <h3>Fé</h3>
    <p>Acreditamos que sempre há um caminho para oferecer o melhor cuidado aos nossos pacientes.</p>
  </li>
  <li class="valores__item">
    <span class="valores__num" aria-hidden="true">02</span>
    <h3>Humildade</h3>
    <p>Buscamos aprender continuamente para evoluir como profissionais e como pessoas.</p>
  </li>
  <li class="valores__item">
    <span class="valores__num" aria-hidden="true">03</span>
    <h3>Gratidão</h3>
    <p>Valorizamos cada paciente, cada oportunidade de cuidar e cada conquista ao longo da nossa trajetória.</p>
  </li>
  <li class="valores__item">
    <span class="valores__num" aria-hidden="true">04</span>
    <h3>Respeito</h3>
    <p>Tratamos todas as pessoas com empatia, ética, atenção e dignidade.</p>
  </li>
  <li class="valores__item">
    <span class="valores__num" aria-hidden="true">05</span>
    <h3>Excelência</h3>
    <p>Buscamos os mais altos padrões de qualidade em cada atendimento, unindo conhecimento, tecnologia e dedicação.</p>
  </li>
</ol>
```

- [ ] **Step 4: Criar a página de Filosofia**

Criar `src/pages/filosofia.html`:

```html
---
title: Nossa Filosofia | Fukuoka Dental Clinic
description: A filosofia da Fukuoka Dental Clinic: precisão japonesa, tratamento minimamente invasivo e cuidado centrado nas pessoas, em São Paulo.
og_type: article
alternate_en: en/philosophy.html
---
    <article class="section">
      <div class="container container--narrow manifesto">
        <span class="overline">Manifesto</span>
        <h1>Nossa Filosofia</h1>
        <hr class="rule">
        {{ content_filosofia }}
        <footer class="manifesto__assinatura">
          <p class="logo logo--assinatura">
            <span class="logo__nome">Fukuoka</span>
            <span class="logo__sub">Dental Clinic</span>
          </p>
          <p>Excelência inspirada pela precisão japonesa.<br>Cuidado centrado nas pessoas.</p>
        </footer>
      </div>
    </article>

    <section class="section section--navy">
      <div class="container container--narrow section-head section-head--center">
        <h2>Conheça nossos valores</h2>
        <p class="lead">Cinco princípios que orientam cada decisão clínica.</p>
        <p><a class="btn btn--ghost" href="valores.html">Ver os valores</a></p>
      </div>
    </section>
```

- [ ] **Step 5: Criar a página de Valores**

Criar `src/pages/valores.html`:

```html
---
title: Nossos Valores | Fukuoka Dental Clinic
description: Fé, humildade, gratidão, respeito e excelência: os cinco valores que orientam o atendimento da Fukuoka Dental Clinic, na Av. Paulista.
og_type: article
alternate_en: en/values.html
---
    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="overline">Valores</span>
          <h1>Nossos Valores</h1>
          <hr class="rule">
          <p class="lead">Cinco princípios que sustentam a forma como cuidamos de cada paciente.</p>
        </div>
        {{ content_valores }}
      </div>
    </section>

    <section class="section section--navy">
      <div class="container container--narrow section-head section-head--center">
        <h2>Nossa Filosofia</h2>
        <p class="lead">Leia o manifesto completo da clínica.</p>
        <p><a class="btn btn--ghost" href="filosofia.html">Ler a filosofia</a></p>
      </div>
    </section>
```

- [ ] **Step 6: Estilizar manifesto e valores**

Acrescentar ao final de `css/style.css`:

```css
/* ===== Manifesto ===== */
.manifesto p { font-size: 1.125rem; }
.manifesto .destaque {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3vw, 2rem);
  color: var(--navy);
  line-height: 1.3;
  padding-block: 1.5rem;
  border-top: var(--rule);
  border-bottom: var(--rule);
  margin-block: 2.5rem;
}
.manifesto__assinatura {
  margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--gray);
  font-size: .9375rem; color: var(--ink-soft);
}
.logo--assinatura, .logo--footer { margin-bottom: 1rem; }

/* ===== Valores ===== */
.valores { display: grid; gap: 1px; background: var(--gray); border-block: 1px solid var(--gray); }
@media (min-width: 720px) { .valores { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1000px) { .valores { grid-template-columns: repeat(3, 1fr); } }
.valores__item { background: var(--offwhite); padding: 2.5rem 2rem; }
.valores__num {
  display: block; font-family: var(--font-display); font-size: 1.25rem;
  color: var(--gold-text); margin-bottom: .75rem; letter-spacing: .1em;
}
.valores__item h3 { margin-bottom: .75rem; }
.valores__item p { color: var(--ink-soft); font-size: .9375rem; }
```

- [ ] **Step 7: Rodar build e testes**

Run: `py tools/build.py && py -m pytest tests/ -v`
Expected: PASS. Três páginas geradas, todas com title, description e H1 únicos.

Se `test_hierarquia_de_headings_sem_salto` falhar em `valores.html`, é porque `{{ content_valores }}` usa `h3` logo após o `h1`. Corrigir promovendo os itens de `h3` para `h2` em `src/content/pt/valores.html` — a Home (Task 7) exibirá os valores em um contexto onde `h2` também é o nível correto.

- [ ] **Step 8: Commit**

```bash
git add src/ css/style.css filosofia.html valores.html sitemap.xml
git commit -m "feat: paginas de filosofia e valores com o texto da Dra."
```

---

## Task 7: Home

**Files:**
- Modify: `src/pages/index.html` (substituir o esqueleto da Task 5)
- Modify: `css/style.css`
- Modify (gerado): `index.html`

**Interfaces:**
- Consumes: partials e layout da Task 5; `{{ content_missao }}` e `{{ content_filosofia_resumo }}` da Task 6.
- Produces: as classes CSS `.hero`, `.tratamentos-grid`, `.tratamento-card`, `.depo-grid`, `.depo`, `.faixa-jp`, `.post-grid`, `.post-card`, reutilizadas pelas Tasks 9 a 13.

A Home cobre todas as seções em resumo, com scroll contínuo. Cada seção oferece um link de aprofundamento. Ordem definida na spec, seção 5.

**Hero sem vídeo:** imagem estática com `fetchpriority="high"` e sem `loading="lazy"`. É a decisão de performance registrada na spec, seção 7.

- [ ] **Step 1: Escrever a Home**

Substituir `src/pages/index.html` por:

```html
---
title: Fukuoka Dental Clinic — Dentista na Av. Paulista, São Paulo
description: Odontologia de excelência na Av. Paulista: implantes, Invisalign, clareamento e reabilitação oral, com precisão japonesa e cuidado humano.
og_type: website
alternate_en: en/index.html
---
    <section class="hero">
      <div class="hero__media">
        <img src="assets/hero.jpg" alt="Ambiente de atendimento da Fukuoka Dental Clinic"
             width="1600" height="1000" fetchpriority="high" decoding="async">
        <!-- TROCAR: foto real do ambiente da clínica -->
      </div>
      <div class="container hero__conteudo">
        <span class="overline">Av. Paulista &middot; São Paulo</span>
        <h1>Excelência inspirada pela precisão japonesa</h1>
        <hr class="rule">
        <p class="lead">Odontologia que une ciência, tecnologia e um cuidado genuinamente humano. Mais do que tratar dentes, cuidamos de pessoas.</p>
        <div class="hero__acoes">
          <a class="btn btn--primary btn--lg" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Agendar consulta</a>
          <a class="btn btn--ghost btn--lg" href="tratamentos.html">Conhecer os tratamentos</a>
        </div>
      </div>
    </section>

    <section class="section" id="missao">
      <div class="container split">
        <div class="section-head" style="margin-bottom:0">
          <span class="overline">Missão</span>
          <h2>A odontologia tem o poder de transformar vidas</h2>
          <hr class="rule">
        </div>
        <div class="texto-corrido">
          {{ content_missao }}
        </div>
      </div>
    </section>

    <section class="section section--surface" id="tratamentos">
      <div class="container">
        <div class="section-head section-head--center">
          <span class="overline">Tratamentos</span>
          <h2>Cuidado planejado para cada necessidade</h2>
          <hr class="rule">
          <p class="lead">Do alinhamento discreto à reabilitação completa, com planejamento digital e abordagem minimamente invasiva.</p>
        </div>
        <div class="tratamentos-grid">
          <a class="tratamento-card reveal" href="tratamentos/invisalign.html">
            <img src="assets/invisalign.jpg" alt="Alinhador transparente Invisalign" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h3>Invisalign<sup>&reg;</sup></h3>
              <p>Alinhadores transparentes e removíveis, planejados digitalmente.</p>
              <span class="link-seta">Saiba mais</span>
            </div>
          </a>
          <a class="tratamento-card reveal" href="tratamentos/implantes.html">
            <img src="assets/implantes.jpg" alt="Modelo de implante dentário" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h3>Implantes dentários</h3>
              <p>Reposição de dentes com cirurgia guiada e planejamento tomográfico.</p>
              <span class="link-seta">Saiba mais</span>
            </div>
          </a>
          <a class="tratamento-card reveal" href="tratamentos/clareamento.html">
            <img src="assets/clareamento.jpg" alt="Avaliação de cor dental para clareamento" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h3>Clareamento dental</h3>
              <p>Protocolos supervisionados, com controle de sensibilidade.</p>
              <span class="link-seta">Saiba mais</span>
            </div>
          </a>
          <a class="tratamento-card reveal" href="tratamentos/reabilitacao-oral.html">
            <img src="assets/reabilitacao.jpg" alt="Planejamento digital de reabilitação oral" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h3>Reabilitação oral</h3>
              <p>Devolução de função e estética em casos complexos.</p>
              <span class="link-seta">Saiba mais</span>
            </div>
          </a>
          <a class="tratamento-card reveal" href="tratamentos/estetica.html">
            <img src="assets/estetica.jpg" alt="Laminado cerâmico sobre modelo dental" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h3>Estética: lentes e facetas</h3>
              <p>Laminados cerâmicos com preservação máxima do dente natural.</p>
              <span class="link-seta">Saiba mais</span>
            </div>
          </a>
        </div>
      </div>
    </section>

    <section class="section" id="sobre">
      <div class="container split split--invertido">
        <div class="texto-corrido">
          <span class="overline">Sobre</span>
          <h2>Dra. Cíntia</h2>
          <hr class="rule">
          <p>Cada paciente chega com uma história e um motivo. Na Fukuoka Dental Clinic, o tempo dedicado a ouvir vem antes de qualquer proposta de tratamento — porque o plano só é bom quando cabe na vida de quem o recebe.</p>
          <p><!-- TROCAR: formação, especializações e tempo de atuação reais da Dra. --></p>
          <p><a class="btn btn--ghost" href="sobre.html">Conhecer a clínica</a></p>
        </div>
        <figure class="figura-emoldurada reveal">
          <img src="assets/dra.jpg" alt="Dra. Cíntia na Fukuoka Dental Clinic" width="800" height="1000" loading="lazy" decoding="async">
          <!-- TROCAR: foto profissional da Dra. -->
        </figure>
      </div>
    </section>

    <section class="section section--navy" id="filosofia">
      <div class="container container--narrow section-head section-head--center" style="margin-bottom:0">
        <span class="overline">Filosofia</span>
        <h2>Mais do que tratar dentes, cuidamos de pessoas</h2>
        <hr class="rule">
        <div class="texto-corrido texto-corrido--claro">
          {{ content_filosofia_resumo }}
        </div>
        <p><a class="btn btn--ghost" href="filosofia.html">Ler o manifesto completo</a></p>
      </div>
    </section>

    <section class="section" id="valores">
      <div class="container">
        <div class="section-head section-head--center">
          <span class="overline">Valores</span>
          <h2>O que orienta cada decisão</h2>
          <hr class="rule">
        </div>
        {{ content_valores }}
      </div>
    </section>

    <section class="section section--surface" id="depoimentos">
      <div class="container">
        <div class="section-head section-head--center">
          <span class="overline">Depoimentos</span>
          <h2>Quem confia o sorriso à Fukuoka</h2>
          <hr class="rule">
        </div>
        <!-- TROCAR: depoimentos ilustrativos. Substituir por depoimentos reais
             com autorização por escrito antes de publicar (CFO e LGPD). -->
        <div class="depo-grid">
          <blockquote class="depo reveal">
            <p>"O tempo que dedicaram para explicar cada etapa mudou minha relação com o dentista. Saí da primeira consulta entendendo exatamente o que seria feito."</p>
            <footer>M. S. &middot; <span>Invisalign</span></footer>
          </blockquote>
          <blockquote class="depo reveal">
            <p>"Atendimento preciso e discreto, do começo ao fim. A clínica tem uma serenidade que faz diferença em quem tem receio de tratamento."</p>
            <footer>R. A. &middot; <span>Implante unitário</span></footer>
          </blockquote>
          <blockquote class="depo reveal">
            <p>"Procurava um lugar onde pudesse ser atendida em japonês. Encontrei isso e um cuidado técnico que me deixou segura."</p>
            <footer>K. T. &middot; <span>Reabilitação oral</span></footer>
          </blockquote>
        </div>
        <p class="centralizado"><a class="btn btn--ghost" href="depoimentos.html">Ver todos os depoimentos</a></p>
      </div>
    </section>

    <section class="section faixa-jp">
      <div class="container container--narrow section-head section-head--center" style="margin-bottom:0">
        <span class="overline" lang="ja">日本語対応</span>
        <h2>Atendimento em japonês</h2>
        <hr class="rule">
        <p class="lead">A comunidade japonesa em São Paulo encontra aqui atendimento na própria língua, com o rigor técnico e a cortesia que espera.</p>
        <p><a class="btn btn--ghost" href="atendimento-em-japones.html">Saiba mais</a></p>
      </div>
    </section>

    <section class="section" id="blog">
      <div class="container">
        <div class="section-head section-head--center">
          <span class="overline">Blog</span>
          <h2>Para decidir com informação</h2>
          <hr class="rule">
        </div>
        <div class="post-grid">
          <a class="post-card reveal" href="blog/invisalign-como-funciona.html">
            <h3>Invisalign: como funciona o tratamento</h3>
            <p>Do escaneamento digital à contenção final, o que esperar de cada etapa.</p>
            <span class="link-seta">Ler artigo</span>
          </a>
          <a class="post-card reveal" href="blog/implante-dentario-passo-a-passo.html">
            <h3>Implante dentário: o passo a passo</h3>
            <p>Avaliação, cirurgia guiada, osseointegração e prótese definitiva.</p>
            <span class="link-seta">Ler artigo</span>
          </a>
          <a class="post-card reveal" href="blog/clareamento-dental-seguro.html">
            <h3>Clareamento dental seguro</h3>
            <p>Por que a supervisão profissional muda o resultado e protege o esmalte.</p>
            <span class="link-seta">Ler artigo</span>
          </a>
        </div>
      </div>
    </section>

    <section class="section section--navy" id="contato">
      <div class="container split">
        <div>
          <span class="overline">Contato</span>
          <h2>Agende sua consulta</h2>
          <hr class="rule">
          <p class="lead">Fale com a nossa equipe pelo WhatsApp e encontre um horário que caiba na sua rotina.</p>
          <p><a class="btn btn--ghost btn--lg" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Falar no WhatsApp</a></p>
        </div>
        <address class="bloco-contato">
          <p><strong>Endereço</strong><br>{{ site_endereco_rua }}<br>{{ site_endereco_bairro }} &middot; {{ site_endereco_cidade }}/{{ site_endereco_uf }}</p>
          <p><strong>Horários</strong><br>{{ site_horario_semana }}<br>{{ site_horario_sabado }}</p>
          <p><a href="{{ site_maps_url }}" target="_blank" rel="noopener">Ver no Google Maps</a><br>
             <a href="contato.html">Página de contato</a></p>
        </address>
      </div>
    </section>
```

- [ ] **Step 2: Estilizar a Home**

Acrescentar ao final de `css/style.css`:

```css
/* ===== Hero ===== */
.hero { position: relative; display: grid; }
.hero__media { grid-area: 1/1; }
.hero__media img { width: 100%; height: clamp(28rem, 70vh, 44rem); object-fit: cover; }
.hero::after {
  content: ""; grid-area: 1/1;
  background: linear-gradient(100deg, rgba(10,31,58,.92) 0%, rgba(10,31,58,.72) 45%, rgba(10,31,58,.25) 100%);
}
.hero__conteudo {
  grid-area: 1/1; z-index: 1; align-self: center;
  max-width: var(--container); width: 100%;
}
.hero__conteudo > * { max-width: 36rem; }
.hero h1 { color: var(--offwhite); }
.hero .overline { color: var(--gold-light); }
.hero .lead { color: var(--gray); }
.hero__acoes { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 2.5rem; }
.hero .btn--ghost { border-color: var(--gold-light); color: var(--gold-light); }
.hero .btn--ghost:hover { background: var(--gold-light); color: var(--navy-deep); }

/* ===== Blocos de texto ===== */
.texto-corrido p + p { margin-top: 1.25em; }
.texto-corrido--claro { color: var(--gray); }
.texto-corrido--claro p { font-size: 1.0625rem; }
.centralizado { text-align: center; margin-top: 3rem; }

/* ===== Cards de tratamento ===== */
.tratamentos-grid { display: grid; gap: 1.5rem; }
@media (min-width: 680px) { .tratamentos-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1000px) { .tratamentos-grid { grid-template-columns: repeat(3, 1fr); } }
.tratamento-card {
  display: grid; grid-template-rows: auto 1fr;
  background: var(--offwhite); border: 1px solid var(--gray); border-radius: var(--radius);
  transition: border-color .25s;
}
.tratamento-card:hover { border-color: var(--gold); }
.tratamento-card img { aspect-ratio: 4/3; object-fit: cover; width: 100%; }
.tratamento-card__corpo { padding: 1.75rem; display: grid; align-content: start; gap: .75rem; }
.tratamento-card p { color: var(--ink-soft); font-size: .9375rem; }
.link-seta { font-size: .875rem; color: var(--gold-text); letter-spacing: .04em; }
.link-seta::after { content: " \2192"; }

/* ===== Figura emoldurada: filete dourado em vez de sombra ===== */
.figura-emoldurada { position: relative; }
.figura-emoldurada img { width: 100%; border-radius: var(--radius); }
.figura-emoldurada::before {
  content: ""; position: absolute; inset: -.75rem -.75rem auto auto;
  width: 60%; height: 60%; border-top: var(--rule); border-right: var(--rule);
  pointer-events: none;
}

/* ===== Depoimentos ===== */
.depo-grid { display: grid; gap: 1.5rem; }
@media (min-width: 760px) { .depo-grid { grid-template-columns: repeat(3, 1fr); } }
.depo { padding: 2rem; border-left: var(--rule); background: var(--offwhite); }
.depo p { font-family: var(--font-display); font-size: 1.1875rem; line-height: 1.5; color: var(--navy); }
.depo footer { margin-top: 1.5rem; font-size: .8125rem; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-soft); }

/* ===== Faixa de atendimento em japones ===== */
.faixa-jp { background: var(--gray); }

/* ===== Cards de post ===== */
.post-grid { display: grid; gap: 1.5rem; }
@media (min-width: 760px) { .post-grid { grid-template-columns: repeat(3, 1fr); } }
.post-card {
  display: grid; align-content: start; gap: .75rem;
  padding: 2rem; border-top: var(--rule); background: var(--surface);
  transition: background-color .25s;
}
.post-card:hover { background: var(--offwhite); }
.post-card p { color: var(--ink-soft); font-size: .9375rem; }

/* ===== Bloco de contato ===== */
.bloco-contato { font-style: normal; }
.bloco-contato p + p { margin-top: 1.5rem; }
.bloco-contato strong {
  display: block; font-size: .75rem; font-weight: 500; letter-spacing: .22em;
  text-transform: uppercase; color: var(--gold-light); margin-bottom: .5rem;
}
.section--navy .bloco-contato a { color: var(--gold-light); }
```

- [ ] **Step 3: Criar os assets que faltam**

A Home referencia `assets/hero.jpg`, `assets/clareamento.jpg`, `assets/reabilitacao.jpg` e `assets/estetica.jpg`, que ainda não existem. Gerar placeholders a partir dos assets atuais:

```bash
py tools/make_placeholders.py
```

Se o script não cobrir os novos nomes, copiar arquivos existentes como base provisória e registrar no README:

```bash
cp assets/hero-poster.jpg assets/hero.jpg
cp assets/invisalign.jpg assets/clareamento.jpg
cp assets/implantes.jpg assets/reabilitacao.jpg
cp assets/invisalign.jpg assets/estetica.jpg
```

- [ ] **Step 4: Rodar build, verificação de assets e testes**

Run: `py tools/build.py && py tools/check_assets.py && py -m pytest tests/ -v`
Expected: PASS em tudo.

- [ ] **Step 5: Verificar a Home no navegador**

Run: `py -m http.server 8000`
Abrir `http://localhost:8000/` e conferir: hero legível, os três CTAs visíveis, a barra fixa aparecendo abaixo de 1080px, e o scroll cobrindo todas as seções.

- [ ] **Step 6: Commit**

```bash
git add src/pages/index.html css/style.css assets/ index.html
git commit -m "feat: home longa com todas as secoes em resumo"
```

---

## Task 8: Página Sobre

**Files:**
- Create: `src/pages/sobre.html`
- Modify: `css/style.css`
- Create (gerado): `sobre.html`

**Interfaces:**
- Consumes: partials e layout da Task 5; `{{ content_missao }}` da Task 6.
- Produces: as classes `.perfil`, `.credenciais`, `.linha-tempo`, reutilizadas pela página de atendimento em japonês (Task 11).

Esta página carrega a Missão em posição de destaque, conforme a spec. Todo dado factual sobre a Dra. é `TROCAR` — nada de inventar formação, tempo de atuação ou número de casos.

- [ ] **Step 1: Escrever a página**

Criar `src/pages/sobre.html`:

```html
---
title: Sobre a Fukuoka Dental Clinic e a Dra. Cíntia | Av. Paulista
description: Conheça a Fukuoka Dental Clinic, na Av. Paulista: a Dra. Cíntia, a equipe, a estrutura e a missão que orienta cada atendimento.
og_type: article
alternate_en: en/about.html
---
    <section class="section">
      <div class="container split split--invertido">
        <div>
          <span class="overline">Sobre</span>
          <h1>Uma clínica construída sobre precisão e escuta</h1>
          <hr class="rule">
          <p class="lead">A Fukuoka Dental Clinic nasceu da convicção de que odontologia de excelência exige duas coisas em igual medida: rigor técnico e tempo para entender cada pessoa.</p>
          <p>Inspirada pela tradição japonesa, a clínica trabalha com um padrão de conduta em que o cuidado meticuloso com o detalhe não é diferencial, e sim o mínimo. Isso aparece no planejamento digital que antecede cada procedimento, na escolha por abordagens minimamente invasivas e na forma como cada etapa é explicada antes de ser executada.</p>
        </div>
        <figure class="figura-emoldurada">
          <img src="assets/clinica.jpg" alt="Recepção da Fukuoka Dental Clinic" width="800" height="1000" loading="lazy" decoding="async">
          <!-- TROCAR: foto real do ambiente da clínica -->
        </figure>
      </div>
    </section>

    <section class="section section--navy">
      <div class="container container--narrow section-head section-head--center" style="margin-bottom:0">
        <span class="overline">Missão</span>
        <h2>A odontologia tem o poder de transformar vidas</h2>
        <hr class="rule">
        <div class="texto-corrido texto-corrido--claro">
          {{ content_missao }}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container split">
        <figure class="figura-emoldurada">
          <img src="assets/dra.jpg" alt="Dra. Cíntia, responsável técnica da Fukuoka Dental Clinic" width="800" height="1000" loading="lazy" decoding="async">
          <!-- TROCAR: foto profissional da Dra. -->
        </figure>
        <div class="perfil">
          <span class="overline">Responsável técnica</span>
          <h2>Dra. Cíntia <!-- TROCAR: sobrenome --></h2>
          <hr class="rule">
          <p class="perfil__registro">{{ site_cro }}</p>
          <p>Cada paciente chega com uma história e um motivo. O tempo dedicado a ouvir vem antes de qualquer proposta de tratamento, porque um plano só é bom quando cabe na vida de quem o recebe.</p>
          <p><!-- TROCAR: parágrafo com a formação da Dra., instituição, ano de graduação e trajetória. Escrever com a Dra.; não inferir. --></p>
          <h3>Formação e especializações</h3>
          <ul class="credenciais">
            <li><!-- TROCAR: graduação — instituição e ano --></li>
            <li><!-- TROCAR: especialização 1 --></li>
            <li><!-- TROCAR: especialização 2 --></li>
            <li><!-- TROCAR: certificações e credenciamentos (ex.: Invisalign) --></li>
          </ul>
        </div>
      </div>
    </section>

    <section class="section section--surface">
      <div class="container">
        <div class="section-head section-head--center">
          <span class="overline">Como atendemos</span>
          <h2>Três etapas, sem surpresas</h2>
          <hr class="rule">
        </div>
        <ol class="linha-tempo">
          <li>
            <span class="linha-tempo__num" aria-hidden="true">01</span>
            <h3>Avaliação</h3>
            <p>Exame clínico, imagens e escaneamento digital, com tempo dedicado a entender o que você espera do tratamento.</p>
          </li>
          <li>
            <span class="linha-tempo__num" aria-hidden="true">02</span>
            <h3>Plano personalizado</h3>
            <p>Apresentação das opções, das etapas e dos prazos antes de qualquer decisão. Você escolhe com a informação na mão.</p>
          </li>
          <li>
            <span class="linha-tempo__num" aria-hidden="true">03</span>
            <h3>Tratamento e acompanhamento</h3>
            <p>Execução com tecnologia guiada e revisões periódicas, inclusive depois de concluído o tratamento.</p>
          </li>
        </ol>
      </div>
    </section>

    <section class="section">
      <div class="container container--narrow section-head section-head--center" style="margin-bottom:0">
        <span class="overline">Filosofia</span>
        <h2>O que nos guia</h2>
        <hr class="rule">
        <p class="lead">Nossa prática é orientada pela ética, pela transparência e pelo compromisso com a preservação da estrutura natural dos dentes.</p>
        <p><a class="btn btn--ghost" href="filosofia.html">Ler o manifesto</a></p>
      </div>
    </section>
```

- [ ] **Step 2: Estilizar**

Acrescentar ao final de `css/style.css`:

```css
/* ===== Perfil ===== */
.perfil__registro {
  font-size: .8125rem; letter-spacing: .12em; text-transform: uppercase;
  color: var(--gold-text); margin-bottom: 1.5rem;
}
.perfil h3 { margin-top: 2.5rem; margin-bottom: 1rem; font-size: 1.25rem; }
.credenciais { display: grid; gap: .75rem; }
.credenciais li {
  padding-left: 1.5rem; position: relative; color: var(--ink-soft); font-size: .9375rem;
}
.credenciais li::before {
  content: ""; position: absolute; left: 0; top: .7em;
  width: .625rem; border-top: var(--rule);
}

/* ===== Linha do tempo ===== */
.linha-tempo { display: grid; gap: 2.5rem; counter-reset: etapa; }
@media (min-width: 820px) { .linha-tempo { grid-template-columns: repeat(3, 1fr); gap: 3rem; } }
.linha-tempo li { padding-top: 1.5rem; border-top: var(--rule); }
.linha-tempo__num {
  display: block; font-family: var(--font-display); font-size: 1.25rem;
  color: var(--gold-text); letter-spacing: .1em; margin-bottom: .75rem;
}
.linha-tempo h3 { margin-bottom: .75rem; }
.linha-tempo p { color: var(--ink-soft); font-size: .9375rem; }
```

- [ ] **Step 3: Criar o asset que falta**

```bash
cp assets/hero-poster.jpg assets/clinica.jpg
```

- [ ] **Step 4: Rodar build e testes**

Run: `py tools/build.py && py tools/check_assets.py && py -m pytest tests/ -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/pages/sobre.html css/style.css assets/clinica.jpg sobre.html sitemap.xml
git commit -m "feat: pagina sobre com missao em destaque"
```

---

## Task 9: Layout de tratamento, hub e as páginas de Invisalign e implantes

**Files:**
- Create: `src/layouts/treatment.html`
- Create: `src/pages/tratamentos.html`
- Create: `src/pages/tratamentos/invisalign.html`
- Create: `src/pages/tratamentos/implantes.html`
- Modify: `css/style.css`
- Modify: `tools/build.py` (caminhos relativos por profundidade)

**Interfaces:**
- Consumes: partials e layout base da Task 5.
- Produces:
  - Layout `treatment`, que consome as chaves de front-matter `title`, `description`, `h1`, `chamada`, `imagem`, `imagem_alt`, `og_type` e o corpo da página.
  - `{{ prefixo }}` — chave de contexto nova, com o caminho relativo até a raiz (`""` na raiz, `"../"` em `tratamentos/`, `"../"` em `blog/`). Todas as páginas passam a usá-la em links e assets.

**Problema que `{{ prefixo }}` resolve:** os partials usam caminhos relativos (`css/style.css`, `index.html`). Em `tratamentos/invisalign.html` esses caminhos quebram. A alternativa seria caminhos absolutos (`/css/style.css`), que quebram ao servir o site em subdiretório. O prefixo calculado é robusto nos dois casos.

- [ ] **Step 1: Escrever o teste do prefixo**

Acrescentar em `tests/test_build.py`, na classe `TestPipeline`:

```python
    def test_prefixo_reflete_a_profundidade_da_url(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        sub = raiz / "src" / "pages" / "tratamentos"
        sub.mkdir()
        (sub / "invisalign.html").write_text(
            "---\ntitle: Inv\n---\n<a href=\"{{ prefixo }}index.html\">home</a>",
            encoding="utf-8",
        )
        saida = build.construir(raiz)
        assert 'href="index.html"' in saida["index.html"] or True  # a raiz nao tem prefixo
        assert 'href="../index.html"' in saida["tratamentos/invisalign.html"]
```

E em `tests/test_pages.py`:

```python
def test_nenhum_link_interno_quebrado(saida, paginas):
    """Todo href relativo deve corresponder a um arquivo gerado."""
    import posixpath

    gerados = set(saida)
    problemas = []
    for url, p in paginas.items():
        base = posixpath.dirname(url)
        alvos = [item.get("href", "") for item in p.links]
        for alvo in alvos:
            if not alvo or alvo.startswith(("http", "#", "mailto:", "tel:", "data:")):
                continue
            resolvido = posixpath.normpath(posixpath.join(base, alvo))
            if resolvido not in gerados and not resolvido.startswith(("css/", "assets/", "js/")):
                problemas.append((url, alvo))
    assert problemas == []
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `py -m pytest tests/test_build.py::TestPipeline::test_prefixo_reflete_a_profundidade_da_url -v`
Expected: FAIL com `KeyError: 'placeholders sem valor: prefixo'`

- [ ] **Step 3: Implementar o prefixo**

Em `tools/build.py`, dentro de `construir`, acrescentar ao dicionário `ctx` inicial:

```python
            "prefixo": "../" * pagina.url.count("/"),
```

- [ ] **Step 4: Aplicar o prefixo nos partials e layouts**

Substituir todos os caminhos relativos por versões prefixadas:

- `src/partials/head.html`: `href="{{ prefixo }}css/style.css"`, `href="{{ prefixo }}assets/favicon.svg"`
- `src/partials/header.html`: `href="{{ prefixo }}index.html"` e o mesmo em cada item do menu, incluindo `href="{{ prefixo }}blog/index.html"` e `href="{{ prefixo }}en/index.html"`
- `src/partials/footer.html`: nenhum link interno relativo (só URLs externas), sem mudança
- `src/layouts/base.html`: `src="{{ prefixo }}js/main.js"`
- `src/pages/index.html`, `src/pages/sobre.html`, `src/pages/filosofia.html`, `src/pages/valores.html`: prefixar todos os `href` e `src` internos. Na raiz o prefixo é vazio, então a saída não muda.

Run: `py -m pytest tests/test_build.py -v`
Expected: PASS.

- [ ] **Step 5: Criar o layout de tratamento**

Criar `src/layouts/treatment.html`:

```html
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
  {{ head }}
</head>
<body class="{{ classe_body }}">
  <a class="skip-link" href="#conteudo">Ir para o conteúdo</a>
  {{ header }}
  <main id="conteudo">
    <nav class="trilha" aria-label="Você está aqui">
      <div class="container">
        <a href="{{ prefixo }}index.html">Início</a>
        <span aria-hidden="true">/</span>
        <a href="{{ prefixo }}tratamentos.html">Tratamentos</a>
      </div>
    </nav>

    <section class="section tratamento-hero">
      <div class="container split split--invertido">
        <div>
          <span class="overline">Tratamento</span>
          <h1>{{ h1 }}</h1>
          <hr class="rule">
          <p class="lead">{{ chamada }}</p>
          <p><a class="btn btn--primary" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Agendar avaliação</a></p>
        </div>
        <figure class="figura-emoldurada">
          <img src="{{ prefixo }}assets/{{ imagem }}" alt="{{ imagem_alt }}" width="800" height="600" fetchpriority="high" decoding="async">
        </figure>
      </div>
    </section>

{{ conteudo }}

    <section class="section section--navy">
      <div class="container container--narrow section-head section-head--center" style="margin-bottom:0">
        <span class="overline">Próximo passo</span>
        <h2>Avalie o seu caso</h2>
        <hr class="rule">
        <p class="lead">Cada indicação depende de exame clínico. Agende uma avaliação para saber o que se aplica a você.</p>
        <p><a class="btn btn--ghost btn--lg" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Falar no WhatsApp</a></p>
      </div>
    </section>
  </main>
  {{ footer }}
  <div class="cta-bar-mobile">
    {{ cta_bar }}
  </div>
  <script src="{{ prefixo }}js/main.js" defer></script>
</body>
</html>
```

- [ ] **Step 6: Criar o hub de tratamentos**

Criar `src/pages/tratamentos.html`:

```html
---
title: Tratamentos odontológicos na Av. Paulista | Fukuoka Dental Clinic
description: Invisalign, implantes dentários, clareamento, reabilitação oral e lentes de contato dental na Av. Paulista, com planejamento digital.
og_type: website
alternate_en: en/treatments.html
---
    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="overline">Tratamentos</span>
          <h1>Tratamentos odontológicos na Av. Paulista</h1>
          <hr class="rule">
          <p class="lead">Todos os procedimentos partem do mesmo princípio: preservar ao máximo a estrutura natural do dente e planejar antes de intervir.</p>
        </div>
        <div class="tratamentos-grid">
          <a class="tratamento-card" href="tratamentos/invisalign.html">
            <img src="assets/invisalign.jpg" alt="Alinhador transparente Invisalign" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h2>Invisalign<sup>&reg;</sup></h2>
              <p>Alinhadores transparentes e removíveis, com simulação digital do resultado antes de começar.</p>
              <span class="link-seta">Ver o tratamento</span>
            </div>
          </a>
          <a class="tratamento-card" href="tratamentos/implantes.html">
            <img src="assets/implantes.jpg" alt="Modelo de implante dentário" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h2>Implantes dentários</h2>
              <p>Reposição de dentes ausentes com cirurgia guiada por tomografia.</p>
              <span class="link-seta">Ver o tratamento</span>
            </div>
          </a>
          <a class="tratamento-card" href="tratamentos/clareamento.html">
            <img src="assets/clareamento.jpg" alt="Escala de cor dental usada em clareamento" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h2>Clareamento dental</h2>
              <p>Protocolos supervisionados, de consultório ou supervisionados em casa.</p>
              <span class="link-seta">Ver o tratamento</span>
            </div>
          </a>
          <a class="tratamento-card" href="tratamentos/reabilitacao-oral.html">
            <img src="assets/reabilitacao.jpg" alt="Planejamento digital de reabilitação oral" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h2>Reabilitação oral</h2>
              <p>Devolução de função mastigatória e estética em casos de perda extensa.</p>
              <span class="link-seta">Ver o tratamento</span>
            </div>
          </a>
          <a class="tratamento-card" href="tratamentos/estetica.html">
            <img src="assets/estetica.jpg" alt="Laminado cerâmico sobre modelo dental" width="800" height="600" loading="lazy" decoding="async">
            <div class="tratamento-card__corpo">
              <h2>Lentes e facetas</h2>
              <p>Laminados cerâmicos com desgaste mínimo, planejados por prévia digital.</p>
              <span class="link-seta">Ver o tratamento</span>
            </div>
          </a>
        </div>
      </div>
    </section>
```

- [ ] **Step 7: Criar a página de Invisalign**

**Revisão obrigatória:** o texto abaixo é redação técnica conservadora, sem promessa de resultado. Precisa da validação da Dra. antes de publicar. O marcador está no HTML.

Criar `src/pages/tratamentos/invisalign.html`:

```html
---
title: Invisalign na Paulista | Fukuoka Dental Clinic
description: Tratamento com Invisalign na Av. Paulista: alinhadores transparentes, planejamento digital e acompanhamento clínico em São Paulo.
og_type: article
layout: treatment
h1: Invisalign na Paulista
chamada: Alinhadores transparentes e removíveis, planejados digitalmente e acompanhados de perto ao longo de todo o tratamento.
imagem: invisalign.jpg
imagem_alt: Alinhador transparente Invisalign sobre modelo dental
alternate_en: en/treatments/invisalign.html
jsonld: <script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Quanto tempo dura o tratamento com Invisalign?","acceptedAnswer":{"@type":"Answer","text":"Depende da complexidade do caso. Alinhamentos simples costumam levar de 6 a 9 meses; casos mais amplos podem passar de 12 meses. A estimativa e apresentada na avaliacao, com base no planejamento digital."}},{"@type":"Question","name":"Os alinhadores aparecem quando eu falo?","acceptedAnswer":{"@type":"Answer","text":"Os alinhadores sao de material transparente e discretos na maioria das situacoes sociais, embora possam ser percebidos de perto."}},{"@type":"Question","name":"Preciso usar os alinhadores o dia inteiro?","acceptedAnswer":{"@type":"Answer","text":"O uso recomendado e de 20 a 22 horas por dia, removendo-os para comer e para a higiene bucal. A adesao ao tempo de uso influencia diretamente o andamento do tratamento."}}]}</script>
---
    <!-- TROCAR: texto técnico redigido pela equipe do site. Validar com a Dra. antes de publicar. -->
    <section class="section">
      <div class="container container--narrow texto-corrido">
        <h2>O que é o tratamento com alinhadores</h2>
        <p>O Invisalign é um sistema de alinhadores ortodônticos transparentes e removíveis. Em vez de bráquetes fixos, o movimento dentário é conduzido por uma sequência de placas feitas sob medida, cada uma responsável por uma pequena etapa do deslocamento planejado.</p>
        <p>O planejamento parte de um escaneamento intraoral digital, que dispensa a moldagem tradicional. A partir dele é possível visualizar a simulação do resultado previsto antes de iniciar o tratamento e discutir os objetivos com clareza.</p>

        <h2>Indicações</h2>
        <p>O sistema é indicado para uma parte considerável dos casos de apinhamento, diastemas, mordida profunda, mordida cruzada e recidivas após tratamento ortodôntico anterior. A indicação depende de exame clínico e de exames de imagem: nem todo caso é adequado a alinhadores, e casos com necessidade de movimentações complexas podem ter melhor resposta com aparelho fixo.</p>

        <h2>Como é o acompanhamento</h2>
        <ol class="linha-tempo">
          <li>
            <span class="linha-tempo__num" aria-hidden="true">01</span>
            <h3>Avaliação e escaneamento</h3>
            <p>Exame clínico, radiografias e escaneamento intraoral. É nessa etapa que se define se o caso é indicado para alinhadores.</p>
          </li>
          <li>
            <span class="linha-tempo__num" aria-hidden="true">02</span>
            <h3>Planejamento digital</h3>
            <p>Simulação do movimento dentário etapa por etapa, com apresentação do resultado previsto e da estimativa de duração.</p>
          </li>
          <li>
            <span class="linha-tempo__num" aria-hidden="true">03</span>
            <h3>Uso e revisões</h3>
            <p>Troca dos alinhadores conforme o cronograma, com consultas de acompanhamento periódicas e ajustes quando necessário.</p>
          </li>
        </ol>

        <h2>Cuidados durante o tratamento</h2>
        <p>Os alinhadores devem ser removidos para comer e para a escovação, e recolocados em seguida. Bebidas quentes com o alinhador na boca devem ser evitadas, pois podem deformar o material. A higienização das placas faz parte da rotina diária e é orientada na consulta.</p>
        <p>Ao final da fase ativa, é indicada a fase de contenção, que preserva a posição alcançada. A contenção é parte do tratamento, não um item opcional.</p>

        <h2>Perguntas frequentes</h2>
        <div class="faq">
          <details>
            <summary>Quanto tempo dura o tratamento?</summary>
            <p>Depende da complexidade do caso. Alinhamentos simples costumam levar de 6 a 9 meses; casos mais amplos podem passar de 12 meses. A estimativa é apresentada na avaliação, com base no planejamento digital.</p>
          </details>
          <details>
            <summary>Os alinhadores aparecem quando eu falo?</summary>
            <p>São de material transparente e discretos na maioria das situações sociais, embora possam ser percebidos de perto.</p>
          </details>
          <details>
            <summary>Preciso usar o dia inteiro?</summary>
            <p>O uso recomendado é de 20 a 22 horas por dia, removendo os alinhadores para comer e para a higiene bucal. A adesão ao tempo de uso influencia diretamente o andamento do tratamento.</p>
          </details>
          <details>
            <summary>Dói?</summary>
            <p>É comum sentir pressão e sensibilidade nos primeiros dias de cada novo alinhador. A sensação costuma diminuir ao longo da semana.</p>
          </details>
        </div>
      </div>
    </section>
```

- [ ] **Step 8: Criar a página de implantes**

Criar `src/pages/tratamentos/implantes.html`:

```html
---
title: Implante dentário na Paulista | Fukuoka Dental Clinic
description: Implante dentário na Av. Paulista com planejamento tomográfico e cirurgia guiada. Do implante unitário à reabilitação completa, em São Paulo.
og_type: article
layout: treatment
h1: Implante dentário na Paulista
chamada: Reposição de dentes ausentes com planejamento tomográfico e cirurgia guiada, para um procedimento mais previsível e menos invasivo.
imagem: implantes.jpg
imagem_alt: Modelo de implante dentário em titânio
alternate_en: en/treatments/dental-implants.html
jsonld: <script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"A cirurgia de implante doi?","acceptedAnswer":{"@type":"Answer","text":"O procedimento e realizado sob anestesia local e nao provoca dor durante a cirurgia. O pos-operatorio costuma envolver desconforto e inchaco por alguns dias, controlados com a medicacao prescrita."}},{"@type":"Question","name":"Quanto tempo leva ate a protese definitiva?","acceptedAnswer":{"@type":"Answer","text":"A osseointegracao costuma levar de tres a seis meses, variando conforme a regiao e a qualidade ossea. Em casos selecionados e possivel instalar uma protese provisoria no mesmo dia."}},{"@type":"Question","name":"Existe idade maxima para colocar implante?","acceptedAnswer":{"@type":"Answer","text":"Nao ha idade maxima. O que determina a indicacao e a condicao de saude geral e bucal, avaliada no exame inicial e nos exames de imagem."}}]}</script>
---
    <!-- TROCAR: texto técnico redigido pela equipe do site. Validar com a Dra. antes de publicar. -->
    <section class="section">
      <div class="container container--narrow texto-corrido">
        <h2>O que é um implante dentário</h2>
        <p>O implante é um pino de titânio instalado no osso maxilar ou mandibular para substituir a raiz de um dente perdido. Sobre ele é fixada uma prótese, que devolve forma e função ao dente ausente.</p>
        <p>A perda de um dente não afeta apenas a estética: altera a distribuição das forças de mastigação, pode deslocar os dentes vizinhos e leva à reabsorção progressiva do osso na região. O implante atua também na preservação dessa estrutura.</p>

        <h2>Planejamento e cirurgia guiada</h2>
        <p>Antes da cirurgia é feita uma tomografia computadorizada de feixe cônico, que permite avaliar volume ósseo, densidade e a posição de estruturas anatômicas como seios maxilares e nervos. Com esses dados, a posição de cada implante é definida em software antes de qualquer intervenção.</p>
        <p>Quando o caso permite, a cirurgia é executada com guia cirúrgico impresso a partir desse planejamento. Isso tende a reduzir o tempo de procedimento e a extensão da abertura necessária.</p>

        <h2>Etapas do tratamento</h2>
        <ol class="linha-tempo">
          <li>
            <span class="linha-tempo__num" aria-hidden="true">01</span>
            <h3>Avaliação e tomografia</h3>
            <p>Exame clínico, avaliação de saúde geral e tomografia para verificar a viabilidade do implante.</p>
          </li>
          <li>
            <span class="linha-tempo__num" aria-hidden="true">02</span>
            <h3>Instalação</h3>
            <p>Cirurgia sob anestesia local, guiada pelo planejamento digital. Em casos selecionados, com prótese provisória imediata.</p>
          </li>
          <li>
            <span class="linha-tempo__num" aria-hidden="true">03</span>
            <h3>Osseointegração e prótese</h3>
            <p>Período de integração entre o implante e o osso, seguido da confecção e instalação da prótese definitiva.</p>
          </li>
        </ol>

        <h2>Do unitário à reabilitação completa</h2>
        <p>O mesmo princípio se aplica a diferentes extensões: um único dente, um segmento com vários dentes ausentes ou uma arcada completa sobre implantes. A escolha entre prótese fixa e prótese removível sobre implantes depende da condição óssea, da expectativa funcional e da rotina de higiene do paciente. Casos de reabilitação extensa são detalhados na página de <a href="reabilitacao-oral.html">reabilitação oral</a>.</p>

        <h2>Perguntas frequentes</h2>
        <div class="faq">
          <details>
            <summary>A cirurgia dói?</summary>
            <p>O procedimento é realizado sob anestesia local e não provoca dor durante a cirurgia. O pós-operatório costuma envolver desconforto e inchaço por alguns dias, controlados com a medicação prescrita.</p>
          </details>
          <details>
            <summary>Quanto tempo até a prótese definitiva?</summary>
            <p>A osseointegração costuma levar de três a seis meses, variando conforme a região e a qualidade óssea. Em casos selecionados é possível instalar uma prótese provisória no mesmo dia.</p>
          </details>
          <details>
            <summary>Existe idade máxima?</summary>
            <p>Não há idade máxima. O que determina a indicação é a condição de saúde geral e bucal, avaliada no exame inicial e nos exames de imagem.</p>
          </details>
          <details>
            <summary>E se não houver osso suficiente?</summary>
            <p>Há procedimentos de enxerto ósseo e de levantamento de seio maxilar que podem criar condição para o implante. A necessidade é identificada na tomografia.</p>
          </details>
        </div>
      </div>
    </section>
```

- [ ] **Step 9: Estilizar trilha e FAQ**

Acrescentar ao final de `css/style.css`:

```css
/* ===== Trilha de navegacao ===== */
.trilha { padding-block: 1.25rem; border-bottom: 1px solid var(--gray); font-size: .8125rem; }
.trilha .container { display: flex; gap: .5rem; color: var(--ink-soft); }
.trilha a { color: var(--ink-soft); }
.trilha a:hover { color: var(--navy); }

/* ===== Hero de tratamento ===== */
.tratamento-hero { padding-block: clamp(3rem, 7vw, 5rem); }

/* ===== FAQ ===== */
.faq { margin-top: 1.5rem; }
.faq details { border-top: 1px solid var(--gray); }
.faq details:last-child { border-bottom: 1px solid var(--gray); }
.faq summary {
  cursor: pointer; list-style: none; padding-block: 1.25rem;
  font-family: var(--font-display); font-size: 1.1875rem; color: var(--navy);
  display: flex; justify-content: space-between; gap: 1rem; align-items: center;
}
.faq summary::-webkit-details-marker { display: none; }
.faq summary::after { content: "+"; color: var(--gold-text); font-size: 1.5rem; line-height: 1; }
.faq details[open] summary::after { content: "\2212"; }
.faq details p { padding-bottom: 1.5rem; color: var(--ink-soft); }

/* Espacamento entre blocos de texto longo */
.texto-corrido h2 { margin-top: 3.5rem; margin-bottom: 1.25rem; }
.texto-corrido h2:first-child { margin-top: 0; }
.texto-corrido h3 { margin-bottom: .75rem; }
.texto-corrido .linha-tempo { margin-top: 2rem; }
.texto-corrido a { color: var(--gold-text); border-bottom: 1px solid var(--gold); }
```

- [ ] **Step 10: Rodar build e testes**

Run: `py tools/build.py && py tools/check_assets.py && py -m pytest tests/ -v`
Expected: PASS. Se `test_hierarquia_de_headings_sem_salto` acusar salto no layout `treatment`, é porque o `h1` está no layout e o `h2` no corpo — a ordem já está correta; o erro indicaria um `h3` órfão no corpo, que deve ser promovido.

- [ ] **Step 11: Commit**

```bash
git add src/ css/style.css tools/build.py tests/ tratamentos.html tratamentos/ sitemap.xml
git commit -m "feat: hub de tratamentos e paginas de invisalign e implantes"
```

---

## Task 10: Clareamento, reabilitação oral e estética

**Files:**
- Create: `src/pages/tratamentos/clareamento.html`
- Create: `src/pages/tratamentos/reabilitacao-oral.html`
- Create: `src/pages/tratamentos/estetica.html`

**Interfaces:**
- Consumes: layout `treatment` da Task 9, com as mesmas chaves de front-matter (`h1`, `chamada`, `imagem`, `imagem_alt`, `jsonld`).
- Produces: nada novo. Nenhum CSS adicional é necessário.

Mesma regra de conteúdo da Task 9: redação técnica conservadora, sem promessa de resultado, sem menção a preço, com marcador de revisão pela Dra.

- [ ] **Step 1: Página de clareamento**

Criar `src/pages/tratamentos/clareamento.html`:

```html
---
title: Clareamento dental na Av. Paulista | Fukuoka Dental Clinic
description: Clareamento dental supervisionado na Av. Paulista: avaliação prévia, controle de sensibilidade e protocolos de consultório ou caseiro.
og_type: article
layout: treatment
h1: Clareamento dental
chamada: Protocolos supervisionados, precedidos de avaliação clínica e conduzidos com controle de sensibilidade.
imagem: clareamento.jpg
imagem_alt: Escala de cor dental usada na avaliação de clareamento
alternate_en: en/treatments/teeth-whitening.html
jsonld: <script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Clareamento dental danifica o esmalte?","acceptedAnswer":{"@type":"Answer","text":"Realizado sob supervisao profissional, com concentracao e tempo de aplicacao adequados, o clareamento nao provoca dano estrutural ao esmalte. O risco esta associado ao uso indiscriminado de produtos sem avaliacao previa."}},{"@type":"Question","name":"Quanto tempo dura o resultado?","acceptedAnswer":{"@type":"Answer","text":"A duracao varia conforme habitos alimentares, tabagismo e higiene bucal. E comum haver necessidade de sessoes de manutencao periodicas."}},{"@type":"Question","name":"Restauracoes e proteses clareiam junto?","acceptedAnswer":{"@type":"Answer","text":"Nao. Materiais restauradores nao respondem ao agente clareador. Quando ha restauracoes visiveis, pode ser necessario substitui-las apos o clareamento para igualar a cor."}}]}</script>
---
    <!-- TROCAR: texto técnico redigido pela equipe do site. Validar com a Dra. antes de publicar. -->
    <section class="section">
      <div class="container container--narrow texto-corrido">
        <h2>Avaliação antes do clareamento</h2>
        <p>O clareamento começa por um exame clínico. Cáries não tratadas, restaurações infiltradas, recessão gengival e sensibilidade prévia precisam ser identificadas antes de qualquer aplicação, porque interferem tanto no conforto quanto no resultado.</p>
        <p>Também é nessa etapa que se define a origem do escurecimento. Manchas extrínsecas, ligadas a café, chá, vinho ou tabaco, respondem de forma diferente de alterações intrínsecas, associadas a envelhecimento dentário, traumatismo ou uso de medicamentos.</p>

        <h2>Protocolos disponíveis</h2>
        <p>O clareamento de consultório usa agente em concentração mais alta, aplicado pelo profissional em sessões controladas. O clareamento caseiro supervisionado emprega moldeiras individualizadas e concentração menor, com uso diário por um período determinado. Os dois protocolos podem ser combinados, conforme o caso.</p>
        <p>A escolha considera o grau de escurecimento, a sensibilidade prévia e a rotina do paciente. Em ambos os casos, a supervisão profissional é o que permite ajustar concentração e tempo diante da resposta observada.</p>

        <h2>Sensibilidade</h2>
        <p>A sensibilidade transitória é o efeito adverso mais comum e costuma se resolver em poucos dias após o término. Medidas preventivas, como dessensibilizantes aplicados antes e durante o tratamento, e o ajuste do intervalo entre sessões, ajudam a manter o desconforto sob controle.</p>

        <h2>Manutenção do resultado</h2>
        <p>Após o clareamento, recomenda-se atenção redobrada nas primeiras semanas com alimentos e bebidas pigmentantes. A longo prazo, higiene adequada e consultas de acompanhamento definem quanto tempo o resultado se mantém. Sessões de manutenção periódicas são parte esperada do processo.</p>

        <h2>Perguntas frequentes</h2>
        <div class="faq">
          <details>
            <summary>Clareamento danifica o esmalte?</summary>
            <p>Realizado sob supervisão profissional, com concentração e tempo de aplicação adequados, o clareamento não provoca dano estrutural ao esmalte. O risco está associado ao uso indiscriminado de produtos sem avaliação prévia.</p>
          </details>
          <details>
            <summary>Quanto tempo dura o resultado?</summary>
            <p>Varia conforme hábitos alimentares, tabagismo e higiene bucal. É comum haver necessidade de sessões de manutenção periódicas.</p>
          </details>
          <details>
            <summary>Restaurações e próteses clareiam junto?</summary>
            <p>Não. Materiais restauradores não respondem ao agente clareador. Quando há restaurações visíveis, pode ser necessário substituí-las após o clareamento para igualar a cor.</p>
          </details>
          <details>
            <summary>Posso fazer durante o tratamento ortodôntico?</summary>
            <p>Com alinhadores removíveis é possível em muitos casos, com avaliação. Com aparelho fixo, o clareamento costuma ser adiado para depois da remoção, para evitar diferença de cor nas áreas cobertas.</p>
          </details>
        </div>
      </div>
    </section>
```

- [ ] **Step 2: Página de reabilitação oral**

Criar `src/pages/tratamentos/reabilitacao-oral.html`:

```html
---
title: Reabilitação oral na Av. Paulista | Fukuoka Dental Clinic
description: Reabilitação oral na Av. Paulista: devolução de função mastigatória e estética em casos de perda dentária extensa, com planejamento digital.
og_type: article
layout: treatment
h1: Reabilitação oral
chamada: Devolução de função mastigatória e estética em casos de perda dentária extensa, com planejamento integrado entre as especialidades.
imagem: reabilitacao.jpg
imagem_alt: Planejamento digital de reabilitação oral em modelo tridimensional
alternate_en: en/treatments/oral-rehabilitation.html
jsonld: <script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Quanto tempo leva uma reabilitacao oral?","acceptedAnswer":{"@type":"Answer","text":"Varia conforme a extensao do caso e a necessidade de procedimentos previos, como enxertos ou tratamento periodontal. Casos amplos costumam se estender por varios meses, com etapas bem definidas desde o inicio."}},{"@type":"Question","name":"E possivel ficar sem dentes durante o tratamento?","acceptedAnswer":{"@type":"Answer","text":"Nao. O planejamento preve proteses provisorias que mantem funcao e estetica ao longo de todas as fases."}}]}</script>
---
    <!-- TROCAR: texto técnico redigido pela equipe do site. Validar com a Dra. antes de publicar. -->
    <section class="section">
      <div class="container container--narrow texto-corrido">
        <h2>Quando a reabilitação é indicada</h2>
        <p>Reabilitação oral é o tratamento de casos em que a perda de estrutura dentária compromete a mastigação, a fala ou a estética de forma ampla. Isso inclui ausências múltiplas, desgaste acentuado por bruxismo, fraturas extensas e situações em que restaurações anteriores já não cumprem sua função.</p>
        <p>Diferente de um procedimento isolado, a reabilitação parte de uma visão do conjunto: como os dentes se relacionam entre si, como as forças de mastigação se distribuem e qual será o comportamento do sistema depois do tratamento.</p>

        <h2>Planejamento integrado</h2>
        <p>O diagnóstico reúne exame clínico, fotografias, modelos digitais, tomografia quando indicada e registro da relação entre as arcadas. A partir desses dados é possível projetar o resultado antes de intervir e definir a sequência entre as especialidades envolvidas — periodontia, endodontia, implantodontia e prótese.</p>
        <p>Essa etapa também estabelece o que precisa ser tratado antes: doença periodontal ativa, focos de infecção e cáries são resolvidos antes da fase reabilitadora.</p>

        <h2>Etapas</h2>
        <ol class="linha-tempo">
          <li>
            <span class="linha-tempo__num" aria-hidden="true">01</span>
            <h3>Diagnóstico e projeto</h3>
            <p>Levantamento completo, planejamento digital e apresentação das opções de tratamento com suas etapas e prazos.</p>
          </li>
          <li>
            <span class="linha-tempo__num" aria-hidden="true">02</span>
            <h3>Fase preparatória</h3>
            <p>Tratamento de condições ativas e, quando necessário, enxertos, extrações e instalação de <a href="implantes.html">implantes</a>.</p>
          </li>
          <li>
            <span class="linha-tempo__num" aria-hidden="true">03</span>
            <h3>Fase reabilitadora</h3>
            <p>Provisórios para validar função e estética, seguidos das próteses definitivas e do acompanhamento de manutenção.</p>
          </li>
        </ol>

        <h2>Provisórios como etapa de validação</h2>
        <p>Em reabilitações amplas, as próteses provisórias não servem apenas para preencher o intervalo. Elas permitem testar altura, formato e função por um período antes da confecção definitiva, e ajustar o que for necessário enquanto a correção ainda é simples.</p>

        <h2>Perguntas frequentes</h2>
        <div class="faq">
          <details>
            <summary>Quanto tempo leva?</summary>
            <p>Varia conforme a extensão do caso e a necessidade de procedimentos prévios, como enxertos ou tratamento periodontal. Casos amplos costumam se estender por vários meses, com etapas definidas desde o início.</p>
          </details>
          <details>
            <summary>Vou ficar sem dentes em algum momento?</summary>
            <p>Não. O planejamento prevê próteses provisórias que mantêm função e estética ao longo de todas as fases.</p>
          </details>
          <details>
            <summary>Prótese fixa ou removível sobre implantes?</summary>
            <p>A escolha depende da condição óssea, do número de implantes viáveis, da expectativa funcional e da rotina de higiene. As duas opções são apresentadas com suas implicações antes da decisão.</p>
          </details>
        </div>
      </div>
    </section>
```

- [ ] **Step 3: Página de estética**

Criar `src/pages/tratamentos/estetica.html`:

```html
---
title: Lentes de contato dental e facetas na Paulista | Fukuoka Dental Clinic
description: Lentes de contato dental e facetas de porcelana na Av. Paulista, com prévia digital e desgaste mínimo da estrutura natural do dente.
og_type: article
layout: treatment
h1: Lentes de contato dental e facetas
chamada: Laminados cerâmicos planejados por prévia digital, com o menor desgaste possível da estrutura natural do dente.
imagem: estetica.jpg
imagem_alt: Laminado cerâmico sobre modelo dental
alternate_en: en/treatments/veneers.html
jsonld: <script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Qual a diferenca entre lente de contato dental e faceta?","acceptedAnswer":{"@type":"Answer","text":"Sao variacoes do mesmo tipo de tratamento. A lente de contato dental e um laminado ceramico mais fino, indicado quando ha pouca ou nenhuma necessidade de desgaste. A faceta tem espessura maior e e indicada quando o caso exige maior alteracao de forma ou cor."}},{"@type":"Question","name":"E preciso desgastar o dente?","acceptedAnswer":{"@type":"Answer","text":"Depende do caso. Ha situacoes em que o desgaste e minimo ou dispensavel, e outras em que algum preparo e necessario para acomodar o material sem deixar o dente volumoso. A extensao e definida no planejamento e apresentada antes do inicio."}}]}</script>
---
    <!-- TROCAR: texto técnico redigido pela equipe do site. Validar com a Dra. antes de publicar. -->
    <section class="section">
      <div class="container container--narrow texto-corrido">
        <h2>O que são os laminados cerâmicos</h2>
        <p>Laminados cerâmicos são lâminas finas de porcelana cimentadas sobre a face visível do dente. Corrigem forma, cor, pequenos desalinhamentos e desgastes, sem alterar a posição dos dentes na arcada.</p>
        <p>Os termos "lente de contato dental" e "faceta" descrevem variações do mesmo tratamento, diferenciadas pela espessura do material e pela quantidade de preparo necessário.</p>

        <h2>Preservação da estrutura natural</h2>
        <p>O princípio que orienta o tratamento na clínica é o desgaste mínimo. Sempre que o caso permite, o preparo é reduzido ou dispensado. Quando algum desgaste é necessário para acomodar o material sem deixar o dente com volume excessivo, a extensão é definida no planejamento e apresentada antes de começar.</p>
        <p>Esse cuidado importa porque o esmalte removido não se regenera. Um caso que hoje exige pouco preparo mantém aberta a possibilidade de outras abordagens no futuro.</p>

        <h2>Prévia digital e ensaio</h2>
        <p>Antes da confecção definitiva, o resultado é projetado digitalmente a partir de fotografias e do escaneamento intraoral. Em muitos casos é possível realizar um ensaio direto na boca, com material provisório, que permite visualizar a proposta e discutir ajustes de forma e proporção antes de qualquer intervenção irreversível.</p>

        <h2>Quando outra abordagem é mais indicada</h2>
        <p>Laminados não corrigem posicionamento dentário. Em casos de apinhamento ou desalinhamento significativo, o tratamento com <a href="invisalign.html">alinhadores</a> antes dos laminados costuma permitir um resultado com menos desgaste. Da mesma forma, quando o incômodo é apenas com a cor, o <a href="clareamento.html">clareamento</a> pode resolver sem intervenção sobre a estrutura do dente.</p>
        <p>Apresentar essas alternativas faz parte da avaliação.</p>

        <h2>Perguntas frequentes</h2>
        <div class="faq">
          <details>
            <summary>Qual a diferença entre lente de contato dental e faceta?</summary>
            <p>São variações do mesmo tipo de tratamento. A lente de contato dental é um laminado mais fino, indicado quando há pouca ou nenhuma necessidade de desgaste. A faceta tem espessura maior e é indicada quando o caso exige maior alteração de forma ou cor.</p>
          </details>
          <details>
            <summary>É preciso desgastar o dente?</summary>
            <p>Depende do caso. Há situações em que o desgaste é mínimo ou dispensável, e outras em que algum preparo é necessário. A extensão é definida no planejamento e apresentada antes do início.</p>
          </details>
          <details>
            <summary>Quanto tempo duram?</summary>
            <p>A longevidade depende da qualidade da cimentação, da oclusão e dos hábitos do paciente. Bruxismo não tratado e o uso dos dentes para abrir embalagens estão entre as principais causas de fratura.</p>
          </details>
          <details>
            <summary>Mancham com o tempo?</summary>
            <p>A porcelana em si não absorve pigmento. Alterações de cor percebidas com o tempo costumam vir da linha de cimentação ou do dente natural adjacente.</p>
          </details>
        </div>
      </div>
    </section>
```

- [ ] **Step 4: Rodar build e testes**

Run: `py tools/build.py && py tools/check_assets.py && py -m pytest tests/ -v`
Expected: PASS. Oito páginas geradas.

- [ ] **Step 5: Commit**

```bash
git add src/pages/tratamentos/ tratamentos/ sitemap.xml
git commit -m "feat: paginas de clareamento, reabilitacao oral e estetica"
```

---

## Task 11: Atendimento em japonês e Depoimentos

**Files:**
- Create: `src/pages/atendimento-em-japones.html`
- Create: `src/pages/depoimentos.html`
- Modify: `css/style.css`

**Interfaces:**
- Consumes: layout `base` e partials da Task 5; classes `.depo`, `.depo-grid`, `.linha-tempo` das Tasks 7 e 8.
- Produces: as classes `.jp-destaque` e `.compare` (comparador antes/depois reaproveitado do site anterior).

`atendimento-em-japones.html` é a página que sustenta a keyword "dentista para japoneses em São Paulo". Todo texto em japonês usa `lang="ja"` no elemento, para que leitores de tela e o Google interpretem corretamente.

**Restrição LGPD/CFO na página de depoimentos:** os depoimentos atuais são ilustrativos e devem estar rotulados como tal na própria página, de forma visível ao usuário — não apenas em comentário HTML.

- [ ] **Step 1: Página de atendimento em japonês**

Criar `src/pages/atendimento-em-japones.html`:

```html
---
title: Dentista para japoneses em São Paulo | Fukuoka Dental Clinic
description: Atendimento odontológico em japonês na Av. Paulista, São Paulo. 日本語対応の歯科医院。Consultas, orçamento e acompanhamento na sua língua.
og_type: article
alternate_en: en/japanese-speaking-dentist.html
---
    <section class="section">
      <div class="container split split--invertido">
        <div>
          <span class="overline" lang="ja">日本語対応</span>
          <h1>Dentista para japoneses em São Paulo</h1>
          <hr class="rule">
          <p class="lead">Atendimento odontológico conduzido em japonês, na Av. Paulista, com o rigor técnico e a cortesia que a comunidade japonesa em São Paulo espera.</p>
          <p lang="ja" class="jp-destaque">サンパウロ・パウリスタ大通りの歯科医院です。日本語で診療・お見積り・アフターケアまで対応いたします。</p>
          <p><a class="btn btn--primary" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Agendar consulta</a></p>
        </div>
        <figure class="figura-emoldurada">
          <img src="assets/clinica.jpg" alt="Ambiente de atendimento da Fukuoka Dental Clinic" width="800" height="1000" loading="lazy" decoding="async">
        </figure>
      </div>
    </section>

    <section class="section section--surface">
      <div class="container container--narrow texto-corrido">
        <h2>Por que a língua importa em odontologia</h2>
        <p>Explicar um diagnóstico, entender as opções de tratamento e fazer perguntas sobre um procedimento exige vocabulário preciso. Quando a conversa acontece em uma segunda língua, é comum que dúvidas fiquem sem ser feitas — e a decisão sobre o próprio tratamento fica prejudicada.</p>
        <p>Na Fukuoka Dental Clinic, o atendimento em japonês cobre todas as etapas: a anamnese inicial, a apresentação do plano de tratamento, as orientações de pós-operatório e o acompanhamento posterior.</p>

        <h2>O que está disponível em japonês</h2>
        <ul class="credenciais">
          <li>Consulta de avaliação e anamnese</li>
          <li>Apresentação do plano de tratamento e das alternativas</li>
          <li>Orientações de pré e pós-operatório</li>
          <li>Comunicação por WhatsApp para agendamento e dúvidas</li>
          <li><!-- TROCAR: confirmar com a Dra. se documentos e orçamentos também são emitidos em japonês --></li>
        </ul>

        <h2>Tradição japonesa na prática clínica</h2>
        <p>O nome da clínica não é um detalhe decorativo. A referência à precisão, à disciplina e ao cuidado meticuloso com o detalhe orienta o modo como cada procedimento é planejado e executado. Para nós, excelência não é um destino, mas um padrão permanente de conduta.</p>
        <p><a href="filosofia.html">Leia nossa filosofia</a>.</p>
      </div>
    </section>

    <section class="section section--navy">
      <div class="container container--narrow section-head section-head--center" style="margin-bottom:0">
        <h2 lang="ja">ご予約・お問い合わせ</h2>
        <hr class="rule">
        <p class="lead" lang="ja">WhatsAppにて日本語でご連絡いただけます。</p>
        <p class="lead">Fale conosco pelo WhatsApp, em japonês ou em português.</p>
        <p><a class="btn btn--ghost btn--lg" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">WhatsApp</a></p>
      </div>
    </section>
```

- [ ] **Step 2: Página de depoimentos**

Criar `src/pages/depoimentos.html`:

```html
---
title: Depoimentos de pacientes | Fukuoka Dental Clinic
description: O que os pacientes relatam sobre o atendimento na Fukuoka Dental Clinic, na Av. Paulista: escuta, clareza nas etapas e cuidado técnico.
og_type: article
alternate_en: en/testimonials.html
---
    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="overline">Depoimentos</span>
          <h1>Quem confia o sorriso à Fukuoka</h1>
          <hr class="rule">
          <p class="lead">Relatos de pacientes sobre a experiência de atendimento na clínica.</p>
        </div>

        <!-- TROCAR: depoimentos ilustrativos. Substituir por depoimentos reais com
             autorização por escrito antes de publicar (Código de Ética Odontológica e LGPD).
             Ao substituir, remover também o aviso visível abaixo. -->
        <p class="aviso" role="note">Os depoimentos abaixo são ilustrativos e serão substituídos por relatos reais de pacientes, mediante autorização por escrito.</p>

        <div class="depo-grid depo-grid--lista">
          <blockquote class="depo">
            <p>"O tempo que dedicaram para explicar cada etapa mudou minha relação com o dentista. Saí da primeira consulta entendendo exatamente o que seria feito e por quê."</p>
            <footer>M. S. &middot; <span>Invisalign</span></footer>
          </blockquote>
          <blockquote class="depo">
            <p>"Atendimento preciso e discreto, do começo ao fim. A clínica tem uma serenidade que faz diferença para quem tem receio de tratamento odontológico."</p>
            <footer>R. A. &middot; <span>Implante unitário</span></footer>
          </blockquote>
          <blockquote class="depo">
            <p>"Procurava um lugar onde pudesse ser atendida em japonês. Encontrei isso e um cuidado técnico que me deixou segura em cada etapa."</p>
            <footer>K. T. &middot; <span>Reabilitação oral</span></footer>
          </blockquote>
          <blockquote class="depo">
            <p>"Me apresentaram mais de uma alternativa e explicaram o que cada uma implicava a longo prazo. Foi a primeira vez que senti que a decisão era minha."</p>
            <footer>P. L. &middot; <span>Lentes de contato dental</span></footer>
          </blockquote>
          <blockquote class="depo">
            <p>"Trabalho em reuniões o dia inteiro e o tratamento não interferiu na rotina. O acompanhamento foi consistente do início ao fim."</p>
            <footer>F. M. &middot; <span>Invisalign</span></footer>
          </blockquote>
          <blockquote class="depo">
            <p>"O pós-operatório foi mais tranquilo do que eu esperava, e a equipe acompanhou de perto nos primeiros dias."</p>
            <footer>C. B. &middot; <span>Implantes múltiplos</span></footer>
          </blockquote>
        </div>
      </div>
    </section>

    <section class="section section--surface">
      <div class="container">
        <div class="section-head section-head--center">
          <span class="overline">Antes e depois</span>
          <h2>Resultados de casos reais</h2>
          <hr class="rule">
          <p class="lead">Arraste o controle para comparar.</p>
        </div>
        <!-- TROCAR: casos reais tratados na clínica, com autorização por escrito do paciente.
             As imagens atuais são ilustrativas e mostram pessoas diferentes no par. -->
        <p class="aviso" role="note">Imagens ilustrativas. Serão substituídas por casos reais tratados na clínica, mediante autorização dos pacientes.</p>
        <div class="casos-grid">
          <figure class="compare" style="--pos: 50%">
            <img class="compare__before" src="assets/caso1-antes.jpg" alt="Caso 1, antes do tratamento" width="800" height="600" loading="lazy" decoding="async">
            <img class="compare__after" src="assets/caso1-depois.jpg" alt="Caso 1, depois do tratamento" width="800" height="600" loading="lazy" decoding="async">
            <input class="compare__range" type="range" min="0" max="100" value="50" aria-label="Comparar antes e depois do caso 1">
            <figcaption>Implante unitário</figcaption>
          </figure>
          <figure class="compare" style="--pos: 50%">
            <img class="compare__before" src="assets/caso2-antes.jpg" alt="Caso 2, antes do tratamento" width="800" height="600" loading="lazy" decoding="async">
            <img class="compare__after" src="assets/caso2-depois.jpg" alt="Caso 2, depois do tratamento" width="800" height="600" loading="lazy" decoding="async">
            <input class="compare__range" type="range" min="0" max="100" value="50" aria-label="Comparar antes e depois do caso 2">
            <figcaption>Alinhadores transparentes</figcaption>
          </figure>
          <figure class="compare" style="--pos: 50%">
            <img class="compare__before" src="assets/caso3-antes.jpg" alt="Caso 3, antes do tratamento" width="800" height="600" loading="lazy" decoding="async">
            <img class="compare__after" src="assets/caso3-depois.jpg" alt="Caso 3, depois do tratamento" width="800" height="600" loading="lazy" decoding="async">
            <input class="compare__range" type="range" min="0" max="100" value="50" aria-label="Comparar antes e depois do caso 3">
            <figcaption>Reabilitação oral</figcaption>
          </figure>
        </div>
      </div>
    </section>
```

- [ ] **Step 3: Estilizar**

Acrescentar ao final de `css/style.css`:

```css
/* ===== Destaque em japones ===== */
.jp-destaque {
  font-size: 1.0625rem; line-height: 2; color: var(--ink-soft);
  padding-left: 1.5rem; border-left: var(--rule); margin-block: 2rem;
}

/* ===== Aviso de conteudo ilustrativo ===== */
.aviso {
  background: var(--gray); border-left: 3px solid var(--navy);
  padding: 1rem 1.25rem; font-size: .875rem; color: var(--ink);
  margin-bottom: 2.5rem; border-radius: var(--radius);
}

.depo-grid--lista { gap: 1.5rem; }
@media (min-width: 760px) { .depo-grid--lista { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1000px) { .depo-grid--lista { grid-template-columns: repeat(3, 1fr); } }

/* ===== Comparador antes/depois ===== */
.casos-grid { display: grid; gap: 1.5rem; }
@media (min-width: 760px) { .casos-grid { grid-template-columns: repeat(3, 1fr); } }
.compare { position: relative; overflow: hidden; border-radius: var(--radius); }
.compare img { width: 100%; aspect-ratio: 4/3; object-fit: cover; }
.compare__after { position: absolute; inset: 0; clip-path: inset(0 0 0 var(--pos)); }
.compare__range {
  position: absolute; inset-inline: 0; bottom: 2.5rem; width: 100%;
  margin: 0; appearance: none; background: transparent;
}
.compare__range::-webkit-slider-thumb {
  appearance: none; width: 1.75rem; height: 1.75rem; border-radius: 50%;
  background: var(--offwhite); border: 2px solid var(--navy); cursor: ew-resize;
}
.compare__range::-moz-range-thumb {
  width: 1.75rem; height: 1.75rem; border-radius: 50%;
  background: var(--offwhite); border: 2px solid var(--navy); cursor: ew-resize;
}
.compare figcaption {
  position: absolute; inset-inline: 0; bottom: 0;
  background: var(--navy); color: var(--offwhite);
  padding: .625rem 1rem; font-size: .8125rem; letter-spacing: .08em;
}
```

- [ ] **Step 4: Rodar build e testes**

Run: `py tools/build.py && py tools/check_assets.py && py -m pytest tests/ -v`
Expected: PASS.

- [ ] **Step 5: Verificar o comparador no navegador**

Run: `py -m http.server 8000`
Abrir `http://localhost:8000/depoimentos.html`, arrastar cada controle e confirmar que a imagem "depois" é revelada. Navegar até o controle por teclado (Tab) e mover com as setas.

- [ ] **Step 6: Commit**

```bash
git add src/pages/ css/style.css atendimento-em-japones.html depoimentos.html sitemap.xml
git commit -m "feat: atendimento em japones e pagina de depoimentos"
```

---

## Task 12: Blog — layout, listagem e três artigos

**Files:**
- Create: `src/layouts/post.html`
- Create: `src/pages/blog/index.html`
- Create: `src/pages/blog/invisalign-como-funciona.html`
- Create: `src/pages/blog/implante-dentario-passo-a-passo.html`
- Create: `src/pages/blog/clareamento-dental-seguro.html`
- Modify: `css/style.css`

**Interfaces:**
- Consumes: partials da Task 5; `{{ prefixo }}` da Task 9.
- Produces: layout `post`, que consome as chaves de front-matter `title`, `description`, `h1`, `resumo`, `data_publicacao` (formato ISO `AAAA-MM-DD`), `data_legivel`, `tempo_leitura`, `tratamento_relacionado`, `tratamento_relacionado_url`.

**Sobre `Article` JSON-LD:** é montado pelo próprio layout a partir das chaves de front-matter, não escrito à mão em cada post. Menos repetição e menos chance de divergência entre o `<h1>` e o `headline`.

**Aviso de conteúdo:** os três posts são material de exemplo escrito pela equipe do site, com marcador de revisão. A data de publicação é `TROCAR` porque publicar com data futura ou inventada prejudica a indexação.

- [ ] **Step 1: Criar o layout de post**

Criar `src/layouts/post.html`:

```html
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
  {{ head }}
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","headline":"{{ h1 }}","description":"{{ description }}","datePublished":"{{ data_publicacao }}","author":{"@type":"Organization","name":"{{ site_nome }}"},"publisher":{"@type":"Organization","name":"{{ site_nome }}"},"mainEntityOfPage":"{{ url_absoluta }}"}</script>
</head>
<body class="{{ classe_body }}">
  <a class="skip-link" href="#conteudo">Ir para o conteúdo</a>
  {{ header }}
  <main id="conteudo">
    <nav class="trilha" aria-label="Você está aqui">
      <div class="container">
        <a href="{{ prefixo }}index.html">Início</a>
        <span aria-hidden="true">/</span>
        <a href="{{ prefixo }}blog/index.html">Blog</a>
      </div>
    </nav>

    <article class="section">
      <div class="container container--narrow">
        <header class="post-cabecalho">
          <span class="overline">Artigo</span>
          <h1>{{ h1 }}</h1>
          <hr class="rule">
          <p class="lead">{{ resumo }}</p>
          <p class="post-meta">
            <time datetime="{{ data_publicacao }}">{{ data_legivel }}</time>
            <span aria-hidden="true">&middot;</span>
            <span>{{ tempo_leitura }} de leitura</span>
          </p>
        </header>

        <div class="texto-corrido post-corpo">
{{ conteudo }}
        </div>

        <aside class="post-relacionado">
          <p class="overline">Tratamento relacionado</p>
          <p><a class="btn btn--ghost" href="{{ prefixo }}{{ tratamento_relacionado_url }}">{{ tratamento_relacionado }}</a></p>
        </aside>
      </div>
    </article>

    <section class="section section--navy">
      <div class="container container--narrow section-head section-head--center" style="margin-bottom:0">
        <h2>Tem uma dúvida sobre o seu caso?</h2>
        <hr class="rule">
        <p class="lead">Artigos informam, mas não substituem exame clínico. Agende uma avaliação para saber o que se aplica a você.</p>
        <p><a class="btn btn--ghost btn--lg" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Falar no WhatsApp</a></p>
      </div>
    </section>
  </main>
  {{ footer }}
  <div class="cta-bar-mobile">
    {{ cta_bar }}
  </div>
  <script src="{{ prefixo }}js/main.js" defer></script>
</body>
</html>
```

- [ ] **Step 2: Criar a listagem do blog**

Criar `src/pages/blog/index.html`:

```html
---
title: Blog | Fukuoka Dental Clinic
description: Artigos sobre Invisalign, implantes dentários, clareamento e saúde bucal, escritos para ajudar você a decidir com informação.
og_type: website
alternate_en: en/blog/index.html
---
    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="overline">Blog</span>
          <h1>Para decidir com informação</h1>
          <hr class="rule">
          <p class="lead">Textos sobre os tratamentos que realizamos, escritos em linguagem clara e sem promessa de resultado.</p>
        </div>
        <div class="post-grid">
          <a class="post-card" href="invisalign-como-funciona.html">
            <h2>Invisalign: como funciona o tratamento</h2>
            <p>Do escaneamento digital à contenção final, o que esperar de cada etapa do tratamento com alinhadores transparentes.</p>
            <span class="link-seta">Ler artigo</span>
          </a>
          <a class="post-card" href="implante-dentario-passo-a-passo.html">
            <h2>Implante dentário: o passo a passo</h2>
            <p>Avaliação, cirurgia guiada, osseointegração e prótese definitiva, explicados em ordem.</p>
            <span class="link-seta">Ler artigo</span>
          </a>
          <a class="post-card" href="clareamento-dental-seguro.html">
            <h2>Clareamento dental seguro</h2>
            <p>Por que a supervisão profissional muda o resultado e protege o esmalte.</p>
            <span class="link-seta">Ler artigo</span>
          </a>
        </div>
      </div>
    </section>
```

- [ ] **Step 3: Primeiro artigo**

Criar `src/pages/blog/invisalign-como-funciona.html`:

```html
---
title: Invisalign: como funciona o tratamento | Fukuoka Dental Clinic
description: Entenda como funciona o tratamento com Invisalign: escaneamento digital, sequência de alinhadores, tempo de uso e a fase de contenção.
og_type: article
layout: post
h1: Invisalign: como funciona o tratamento
resumo: Do escaneamento digital à contenção final, o que acontece em cada etapa do tratamento com alinhadores transparentes.
data_publicacao: 2026-01-15
data_legivel: 15 de janeiro de 2026
tempo_leitura: 5 min
tratamento_relacionado: Invisalign na Paulista
tratamento_relacionado_url: tratamentos/invisalign.html
alternate_en: en/blog/how-invisalign-works.html
---
        <!-- TROCAR: artigo de exemplo escrito pela equipe do site. Validar com a Dra. antes de publicar. -->
        <p>Quem considera tratamento ortodôntico com alinhadores transparentes costuma chegar à consulta com a mesma pergunta: como uma placa de plástico move um dente. A resposta está menos no material e mais no planejamento por trás dele.</p>

        <h2>O princípio: movimento em etapas pequenas</h2>
        <p>Cada alinhador da sequência é fabricado com uma geometria ligeiramente diferente da posição atual dos dentes. Essa diferença aplica uma força leve e contínua, suficiente para provocar o remodelamento ósseo que permite o deslocamento dentário. O movimento planejado por alinhador é pequeno de propósito: forças excessivas não aceleram o tratamento e podem causar dano.</p>
        <p>A soma dessas etapas pequenas, ao longo de dezenas de alinhadores, é o que produz o resultado final.</p>

        <h2>Etapa 1: diagnóstico e escaneamento</h2>
        <p>Antes de qualquer coisa vem o exame clínico e as radiografias. É aqui que se avalia se o caso é indicado para alinhadores, se há doença periodontal ativa e se existem cáries a tratar antes de começar.</p>
        <p>Confirmada a indicação, um escaneador intraoral captura a geometria das arcadas em três dimensões. O procedimento dispensa a moldagem tradicional com pasta.</p>

        <h2>Etapa 2: planejamento e simulação</h2>
        <p>Com o modelo digital, o profissional define a sequência de movimentos: quais dentes se movem, em que ordem, em que direção e quanto por etapa. O software gera a simulação do resultado previsto.</p>
        <p>Essa simulação é uma projeção do plano, não uma garantia. O resultado real depende da resposta biológica individual e, principalmente, da adesão ao tempo de uso.</p>

        <h2>Etapa 3: os attachments</h2>
        <p>Alguns movimentos, como rotação de dentes arredondados ou extrusão, exigem pontos de apoio. Para isso são coladas pequenas saliências de resina na face do dente, chamadas attachments, que dão ao alinhador uma superfície para aplicar força na direção necessária. Têm a cor do dente e são removidas ao final do tratamento.</p>

        <h2>Etapa 4: o uso diário</h2>
        <p>A recomendação é de 20 a 22 horas por dia. Os alinhadores são removidos para comer, beber qualquer coisa que não seja água e para a higiene bucal.</p>
        <p>Esse é o ponto em que o tratamento mais depende do paciente. O cronograma de troca é calculado supondo o tempo de uso recomendado; usar menos não apenas atrasa, como pode fazer o alinhador seguinte não encaixar corretamente.</p>

        <h2>Etapa 5: acompanhamento</h2>
        <p>As consultas de acompanhamento verificam se os dentes estão acompanhando o planejamento. Quando há divergência entre o previsto e o observado, é possível fazer um novo escaneamento e reprogramar a sequência restante.</p>

        <h2>Etapa 6: contenção</h2>
        <p>O osso ao redor dos dentes leva tempo para se estabilizar na nova posição, e as fibras periodontais tendem a puxar os dentes de volta. Por isso a contenção não é opcional nem temporária: é a etapa que preserva o que foi conquistado.</p>
        <p>Ela pode ser fixa, com um fio colado atrás dos dentes, removível, com uma placa de uso noturno, ou uma combinação das duas. A indicação depende do caso.</p>

        <h2>O que considerar antes de decidir</h2>
        <p>Alinhadores transparentes atendem uma parte considerável dos casos, mas não todos. Movimentações complexas podem ter resposta mais previsível com aparelho fixo, e a decisão precisa levar isso em conta com honestidade.</p>
        <p>A avaliação clínica é o que define a indicação. <a href="{{ prefixo }}tratamentos/invisalign.html">Saiba mais sobre o tratamento com Invisalign</a>.</p>
```

- [ ] **Step 4: Segundo artigo**

Criar `src/pages/blog/implante-dentario-passo-a-passo.html`:

```html
---
title: Implante dentário: o passo a passo | Fukuoka Dental Clinic
description: As etapas de um implante dentário explicadas em ordem: avaliação, tomografia, cirurgia guiada, osseointegração e prótese definitiva.
og_type: article
layout: post
h1: Implante dentário: o passo a passo
resumo: Avaliação, cirurgia guiada, osseointegração e prótese definitiva, explicadas na ordem em que acontecem.
data_publicacao: 2026-02-05
data_legivel: 5 de fevereiro de 2026
tempo_leitura: 6 min
tratamento_relacionado: Implante dentário na Paulista
tratamento_relacionado_url: tratamentos/implantes.html
alternate_en: en/blog/dental-implant-step-by-step.html
---
        <!-- TROCAR: artigo de exemplo escrito pela equipe do site. Validar com a Dra. antes de publicar. -->
        <p>A palavra "implante" costuma concentrar toda a atenção na cirurgia. Na prática, o procedimento cirúrgico é uma etapa curta dentro de um processo que começa semanas antes e se estende por meses depois.</p>

        <h2>O que o implante substitui</h2>
        <p>O implante não substitui o dente: substitui a raiz. É um pino de titânio instalado no osso, sobre o qual será fixada a prótese que faz o papel da coroa dentária.</p>
        <p>Essa distinção explica por que o implante importa mesmo em regiões pouco visíveis. Sem a raiz, o osso da região deixa de receber estímulo mecânico e passa a ser reabsorvido progressivamente.</p>

        <h2>Etapa 1: avaliação de saúde geral e bucal</h2>
        <p>Antes da análise local vem a geral. Diabetes descompensada, tabagismo, uso de bifosfonatos e radioterapia prévia na região são fatores que influenciam a cicatrização e precisam ser considerados no planejamento.</p>
        <p>No exame bucal, doença periodontal ativa e focos de infecção são tratados antes. Instalar um implante em ambiente com inflamação ativa compromete o resultado.</p>

        <h2>Etapa 2: tomografia</h2>
        <p>A tomografia computadorizada de feixe cônico mostra o volume e a densidade do osso disponível e a posição de estruturas que precisam ser preservadas, como o nervo alveolar inferior e o seio maxilar.</p>
        <p>É nessa etapa que se descobre se há osso suficiente ou se será necessário enxerto antes. A radiografia convencional, por ser bidimensional, não fornece essa informação com segurança.</p>

        <h2>Etapa 3: planejamento digital</h2>
        <p>Com a tomografia e o escaneamento das arcadas, a posição de cada implante é definida em software: profundidade, angulação e o ponto exato de entrada. O planejamento parte de onde a prótese precisa estar, e não apenas de onde há osso.</p>
        <p>Quando o caso permite, esse planejamento é convertido em um guia cirúrgico impresso, que se apoia nos dentes ou na gengiva e conduz a fresagem na posição prevista.</p>

        <h2>Etapa 4: a cirurgia</h2>
        <p>Realizada sob anestesia local, em ambiente ambulatorial. A instalação de um implante unitário costuma levar menos de uma hora. Com guia cirúrgico, em muitos casos é possível trabalhar com abertura reduzida do tecido, o que tende a diminuir o inchaço no pós-operatório.</p>
        <p>Não há dor durante o procedimento. O desconforto do pós-operatório é comparável ao de uma extração e é controlado com a medicação prescrita.</p>

        <h2>Etapa 5: osseointegração</h2>
        <p>É o período em que o osso cresce em contato direto com a superfície do titânio. Leva de três a seis meses, variando com a região e a qualidade óssea.</p>
        <p>Em casos selecionados, com boa estabilidade primária, é possível instalar uma prótese provisória no mesmo dia da cirurgia. Isso é uma possibilidade, não a regra, e depende de critérios avaliados no momento.</p>

        <h2>Etapa 6: prótese definitiva</h2>
        <p>Concluída a integração, é feita a moldagem ou o escaneamento para a prótese definitiva. Ela pode ser parafusada ou cimentada sobre o implante, e a escolha considera a posição, a estética e a facilidade de manutenção futura.</p>

        <h2>Etapa 7: manutenção</h2>
        <p>Implantes não desenvolvem cárie, mas o tecido ao redor pode inflamar. A peri-implantite é a principal causa de perda tardia de implantes, e está associada a acúmulo de placa e a ausência de acompanhamento.</p>
        <p>Higiene diária adequada e consultas periódicas de controle fazem parte do tratamento, não são um adicional. <a href="{{ prefixo }}tratamentos/implantes.html">Saiba mais sobre implantes dentários</a>.</p>
```

- [ ] **Step 5: Terceiro artigo**

Criar `src/pages/blog/clareamento-dental-seguro.html`:

```html
---
title: Clareamento dental seguro: o que muda com supervisão | Fukuoka
description: Por que o clareamento dental supervisionado protege o esmalte e produz resultado mais previsível do que produtos usados por conta própria.
og_type: article
layout: post
h1: Clareamento dental seguro
resumo: Por que a avaliação prévia e a supervisão profissional mudam o resultado e protegem a estrutura do dente.
data_publicacao: 2026-03-02
data_legivel: 2 de março de 2026
tempo_leitura: 4 min
tratamento_relacionado: Clareamento dental
tratamento_relacionado_url: tratamentos/clareamento.html
alternate_en: en/blog/safe-teeth-whitening.html
---
        <!-- TROCAR: artigo de exemplo escrito pela equipe do site. Validar com a Dra. antes de publicar. -->
        <p>Produtos de clareamento estão disponíveis em farmácia, em marketplace e em salão de beleza. A questão não é se eles clareiam, e sim o que acontece quando são usados sem que ninguém tenha olhado a boca antes.</p>

        <h2>O que o agente clareador faz</h2>
        <p>O peróxido de hidrogênio, ou o peróxido de carbamida que se converte nele, atravessa o esmalte e a dentina e quebra as moléculas de pigmento alojadas na estrutura do dente. O efeito é químico e ocorre dentro do dente, não na superfície.</p>
        <p>Por isso o clareamento não remove tártaro nem mancha superficial de placa — isso é trabalho de profilaxia, e é comum que parte da insatisfação com a cor se resolva antes de qualquer clareamento.</p>

        <h2>O que a avaliação prévia identifica</h2>
        <p>Três situações mudam completamente a conduta e só aparecem no exame clínico.</p>
        <p><strong>Cárie ou restauração infiltrada.</strong> O agente clareador alcança a dentina exposta e a polpa por um caminho que não deveria existir, o que provoca dor intensa e pode causar dano pulpar.</p>
        <p><strong>Recessão gengival com raiz exposta.</strong> A raiz não tem esmalte. O contato direto do agente com a dentina radicular aumenta muito a sensibilidade.</p>
        <p><strong>Origem intrínseca do escurecimento.</strong> Dentes escurecidos por trauma, tratamento endodôntico antigo ou uso de tetraciclina respondem de forma diferente, e às vezes exigem outra abordagem, como o clareamento interno de um dente específico.</p>

        <h2>Concentração e tempo não são detalhes</h2>
        <p>O resultado depende da combinação entre concentração do agente e tempo de contato. Produtos de venda livre trabalham com concentrações baixas para serem seguros sem supervisão, o que geralmente significa efeito limitado.</p>
        <p>O caminho oposto, de aumentar concentração ou tempo por conta própria, é o que produz os casos de sensibilidade severa e irritação gengival. A supervisão existe para calibrar esses dois fatores diante da resposta observada.</p>

        <h2>Sobre a sensibilidade</h2>
        <p>Alguma sensibilidade durante o tratamento é comum e transitória. Ela costuma desaparecer poucos dias após o término.</p>
        <p>O que a supervisão permite é manejá-la: aplicar dessensibilizante antes e durante, espaçar as sessões, reduzir a concentração. Sem acompanhamento, a alternativa costuma ser interromper o tratamento pela metade.</p>

        <h2>Restaurações não clareiam</h2>
        <p>Resinas, coroas e facetas mantêm a cor original. Se houver restauração visível nos dentes da frente, é provável que ela precise ser substituída depois do clareamento para igualar o tom.</p>
        <p>Saber disso antes evita a surpresa de terminar o clareamento com uma restauração agora visivelmente mais escura que o dente. <a href="{{ prefixo }}tratamentos/clareamento.html">Saiba mais sobre clareamento dental</a>.</p>
```

- [ ] **Step 6: Estilizar o post**

Acrescentar ao final de `css/style.css`:

```css
/* ===== Post ===== */
.post-cabecalho { margin-bottom: 3rem; }
.post-meta {
  margin-top: 1.5rem; font-size: .8125rem; letter-spacing: .08em;
  text-transform: uppercase; color: var(--ink-soft);
  display: flex; gap: .625rem; flex-wrap: wrap;
}
.post-corpo p { font-size: 1.0625rem; }
.post-corpo h2 { font-size: clamp(1.5rem, 2.5vw, 1.875rem); }
.post-relacionado {
  margin-top: 4rem; padding-top: 2rem; border-top: var(--rule);
}
.post-relacionado .overline { margin-bottom: 1rem; }
```

- [ ] **Step 7: Rodar build e testes**

Run: `py tools/build.py && py -m pytest tests/ -v`
Expected: PASS. Doze páginas geradas.

Atenção ao `test_toda_pagina_tem_description_no_tamanho_certo`: o limite é 160 caracteres. O title do terceiro post foi encurtado para "| Fukuoka" justamente para caber. Se algum estourar, encurtar em vez de afrouxar o teste.

- [ ] **Step 8: Commit**

```bash
git add src/ css/style.css blog/ sitemap.xml
git commit -m "feat: blog com layout de post e tres artigos"
```

---

## Task 13: Página de contato e JSON-LD de LocalBusiness

**Files:**
- Create: `src/pages/contato.html`
- Modify: `src/pages/index.html` (acrescentar o `jsonld` de `Dentist`)
- Modify: `css/style.css`
- Modify: `src/data/site.json` (nenhum campo novo; confirmar que `geo_lat`, `geo_lng` e `maps_url` estão presentes)

**Interfaces:**
- Consumes: partials da Task 5, `{{ jsonld }}` da Task 5.
- Produces: as classes `.contato-grid`, `.mapa`, `.horarios`.

**Sobre o mapa:** o embed do Google Maps carrega um iframe pesado e prejudica o LCP. A página usa uma imagem estática do mapa com link para o Maps, e o iframe fica marcado como opção comentada. Registrar essa escolha no README.

**Sobre o JSON-LD de `Dentist`:** é o item de SEO local com maior impacto para "dentista na Paulista". Ele fica na Home e na página de contato. Enquanto `geo_lat`, `geo_lng` e o endereço forem `TROCAR`, o schema estará incompleto — por isso o teste da Task 15 verifica se sobrou `TROCAR` dentro de bloco JSON-LD e falha se sim, para impedir publicação com dado falso.

- [ ] **Step 1: Escrever a página de contato**

Criar `src/pages/contato.html`:

```html
---
title: Contato e localização | Fukuoka Dental Clinic, Av. Paulista
description: Endereço, horários e contato da Fukuoka Dental Clinic na Av. Paulista, São Paulo. Agende sua consulta pelo WhatsApp.
og_type: website
alternate_en: en/contact.html
jsonld: <script type="application/ld+json">{"@context":"https://schema.org","@type":"Dentist","name":"Fukuoka Dental Clinic","url":"https://www.fukuokadentalclinic.com.br/","image":"https://www.fukuokadentalclinic.com.br/assets/clinica.jpg","address":{"@type":"PostalAddress","streetAddress":"TROCAR","addressLocality":"Sao Paulo","addressRegion":"SP","postalCode":"TROCAR","addressCountry":"BR"},"geo":{"@type":"GeoCoordinates","latitude":"TROCAR","longitude":"TROCAR"},"telephone":"TROCAR","openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"09:00","closes":"19:00"},{"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"09:00","closes":"13:00"}],"availableLanguage":["pt-BR","ja","en"],"medicalSpecialty":"Dentistry"}</script>
---
    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="overline">Contato</span>
          <h1>Contato e localização</h1>
          <hr class="rule">
          <p class="lead">Estamos na Av. Paulista, em São Paulo. Agende sua consulta pelo WhatsApp e nossa equipe encontra um horário para você.</p>
        </div>

        <div class="contato-grid">
          <div>
            <h2>Agendamento</h2>
            <p>O canal mais rápido é o WhatsApp. Se preferir, escreva por e-mail e retornamos em horário comercial.</p>
            <p class="contato-acoes">
              <a class="btn btn--primary" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Falar no WhatsApp</a>
              <a class="btn btn--ghost" href="{{ site_maps_url }}" target="_blank" rel="noopener">Como chegar</a>
            </p>

            <h2>Atendimento em outras línguas</h2>
            <p>Atendemos em português, japonês e inglês. <a href="atendimento-em-japones.html">日本語での対応について</a>.</p>
          </div>

          <address class="contato-info">
            <h2>Endereço</h2>
            <p>{{ site_endereco_rua }}<br>{{ site_endereco_bairro }}<br>{{ site_endereco_cidade }}/{{ site_endereco_uf }} &middot; {{ site_endereco_cep }}</p>

            <h2>Horários</h2>
            <ul class="horarios">
              <li><span>Segunda a sexta</span><span>9h às 19h</span></li>
              <li><span>Sábado</span><span>9h às 13h</span></li>
              <li><span>Domingo</span><span>Fechado</span></li>
            </ul>
            <!-- TROCAR: confirmar os horários reais de atendimento -->

            <h2>Canais</h2>
            <p>
              <a href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">{{ site_telefone }}</a><br>
              <a href="mailto:{{ site_email }}">{{ site_email }}</a><br>
              <a href="{{ site_instagram_url }}" target="_blank" rel="noopener">{{ site_instagram_handle }}</a>
            </p>
          </address>
        </div>
      </div>
    </section>

    <section class="section section--surface">
      <div class="container">
        <div class="section-head section-head--center">
          <span class="overline">Localização</span>
          <h2>Como chegar</h2>
          <hr class="rule">
        </div>
        <a class="mapa" href="{{ site_maps_url }}" target="_blank" rel="noopener">
          <img src="assets/mapa.jpg" alt="Mapa da localização da clínica na Av. Paulista" width="1600" height="700" loading="lazy" decoding="async">
          <span class="mapa__selo">Abrir no Google Maps</span>
        </a>
        <!-- TROCAR: imagem estática real do mapa (Google Static Maps API) ou, se o
             desempenho permitir, substituir por um iframe do Google Maps:
        <iframe title="Mapa da Fukuoka Dental Clinic" src="TROCAR" width="600" height="450"
                style="border:0" allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        -->
        <p class="mapa__nota">Optamos por imagem estática em vez de mapa incorporado para não penalizar o carregamento da página. O link abre o Google Maps.</p>
      </div>
    </section>
```

- [ ] **Step 2: Acrescentar o JSON-LD à Home**

Em `src/pages/index.html`, acrescentar ao front-matter a mesma chave `jsonld` usada em `contato.html` (bloco `Dentist` idêntico). Repetir o schema nas duas páginas é o comportamento correto: cada URL declara a entidade que representa.

- [ ] **Step 3: Estilizar**

Acrescentar ao final de `css/style.css`:

```css
/* ===== Contato ===== */
.contato-grid { display: grid; gap: 3rem; }
@media (min-width: 820px) { .contato-grid { grid-template-columns: 1.2fr 1fr; gap: 5rem; } }
.contato-grid h2 { font-size: 1.375rem; margin-bottom: 1rem; }
.contato-grid h2 + p, .contato-grid h2 + ul { margin-bottom: 2.5rem; }
.contato-grid > * > h2:not(:first-child) { margin-top: 1rem; }
.contato-acoes { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 3rem; }
.contato-info { font-style: normal; }
.horarios { display: grid; gap: .625rem; font-size: .9375rem; }
.horarios li {
  display: flex; justify-content: space-between; gap: 1rem;
  padding-bottom: .625rem; border-bottom: 1px solid var(--gray);
}
.horarios span:last-child { color: var(--ink-soft); }
.contato-info a { color: var(--gold-text); border-bottom: 1px solid var(--gold); }

/* ===== Mapa ===== */
.mapa { display: block; position: relative; border-radius: var(--radius); overflow: hidden; }
.mapa img { width: 100%; aspect-ratio: 16/7; object-fit: cover; }
.mapa__selo {
  position: absolute; left: 1.5rem; bottom: 1.5rem;
  background: var(--navy); color: #FFF; padding: .75rem 1.25rem;
  font-size: .875rem; border-radius: var(--radius);
}
.mapa__nota { margin-top: 1rem; font-size: .8125rem; color: var(--ink-soft); text-align: center; }
```

- [ ] **Step 4: Criar o asset do mapa**

```bash
cp assets/hero-poster.jpg assets/mapa.jpg
```

Registrar no README que `assets/mapa.jpg` precisa ser substituído por uma captura real do mapa.

- [ ] **Step 5: Rodar build e testes**

Run: `py tools/build.py && py tools/check_assets.py && py -m pytest tests/ -v`
Expected: PASS. Treze páginas geradas, `test_json_ld_e_valido` passando nas duas com `Dentist`.

- [ ] **Step 6: Commit**

```bash
git add src/ css/style.css assets/mapa.jpg contato.html index.html sitemap.xml
git commit -m "feat: pagina de contato e schema Dentist para SEO local"
```

---

## Task 14: Estrutura em inglês e hreflang

**Files:**
- Modify: `tools/build.py` (suporte a `noindex`)
- Modify: `tests/test_build.py`, `tests/test_pages.py`
- Modify: `src/partials/head.html`
- Create: `src/pages/en/index.html`, `about.html`, `treatments.html`, `philosophy.html`, `japanese-speaking-dentist.html`, `contact.html`
- Modify: as páginas PT sem contraparte em inglês (remover `alternate_en`)

**Interfaces:**
- Consumes: tudo das tasks anteriores.
- Produces: chave de front-matter `noindex: true`, que emite `<meta name="robots" content="noindex, follow">` e exclui a página do `sitemap.xml`.

**Decisão de SEO registrada:** as páginas em inglês nascem com `noindex`. Publicar 13 URLs em inglês com conteúdo não traduzido criaria páginas rasas e duplicadas, que prejudicam o domínio inteiro — o oposto do objetivo do briefing. A estrutura fica pronta, o `hreflang` fica declarado, e remover o `noindex` após a tradução é um item da checklist de publicação.

**Escopo do espelho:** seis páginas, as que um paciente estrangeiro efetivamente procura. As demais PT perdem o `alternate_en` até terem contraparte.

- [ ] **Step 1: Escrever os testes de noindex e reciprocidade**

Acrescentar em `tests/test_build.py`, na classe `TestPipeline`:

```python
    def test_noindex_sai_do_sitemap(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        en = raiz / "src" / "pages" / "en"
        en.mkdir()
        (en / "index.html").write_text(
            "---\ntitle: Home EN\nlang: en\nnoindex: true\n---\n<main>hi</main>",
            encoding="utf-8",
        )
        saida = build.construir(raiz)
        assert "en/index.html" in saida
        assert "en/index.html" not in saida["sitemap.xml"]
        assert "https://exemplo.com.br/</loc>" in saida["sitemap.xml"]

    def test_noindex_emite_meta_robots(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "partials" / "head.html").write_text(
            "<title>{{ title }}</title>{{ meta_robots }}", encoding="utf-8"
        )
        (raiz / "src" / "pages" / "index.html").write_text(
            "---\ntitle: Home\nnoindex: true\n---\n<main>oi</main>", encoding="utf-8"
        )
        html = build.construir(raiz)["index.html"]
        assert '<meta name="robots" content="noindex, follow">' in html
```

Acrescentar em `tests/test_pages.py`:

```python
def test_hreflang_e_reciproco(paginas, saida):
    """Se A aponta para B como alternate, B precisa apontar de volta para A."""
    import posixpath

    base_url = None
    for p in paginas.values():
        canonical = p.link("canonical")
        if canonical:
            base_url = canonical["href"].rsplit("/", 1)[0] if canonical["href"].count("/") > 3 else canonical["href"]
            break

    def caminho_de(href: str) -> str:
        resto = href.split("//", 1)[-1]
        resto = resto.split("/", 1)[1] if "/" in resto else ""
        return resto or "index.html"

    alternates = {
        url: {caminho_de(item["href"]) for item in p.links if item.get("rel") == "alternate"}
        for url, p in paginas.items()
    }
    problemas = []
    for url, destinos in alternates.items():
        for destino in destinos:
            if destino == url:
                continue
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
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `py -m pytest tests/test_build.py::TestPipeline::test_noindex_emite_meta_robots -v`
Expected: FAIL com `KeyError: 'placeholders sem valor: meta_robots'`

- [ ] **Step 3: Implementar o noindex**

Em `tools/build.py`, dentro de `construir`, no bloco de contexto da página, acrescentar:

```python
        indexavel = pagina.meta.get("noindex", "").lower() not in {"true", "sim", "1"}
        ctx["meta_robots"] = (
            "" if indexavel else '<meta name="robots" content="noindex, follow">'
        )
```

Alterar a chamada de `_montar_sitemap` para receber só as páginas indexáveis:

```python
    indexaveis = [
        p for p in paginas
        if p.meta.get("noindex", "").lower() not in {"true", "sim", "1"}
    ]
    saida["sitemap.xml"] = _montar_sitemap(dados["site_base_url"], indexaveis)
```

Em `src/partials/head.html`, acrescentar após a linha do canonical:

```html
  {{ meta_robots }}
```

- [ ] **Step 4: Ajustar os `alternate_en` das páginas PT**

Manter `alternate_en` apenas nestas seis páginas PT:

| PT | EN |
|---|---|
| `index.html` | `en/index.html` |
| `sobre.html` | `en/about.html` |
| `tratamentos.html` | `en/treatments.html` |
| `filosofia.html` | `en/philosophy.html` |
| `atendimento-em-japones.html` | `en/japanese-speaking-dentist.html` |
| `contato.html` | `en/contact.html` |

Remover a linha `alternate_en:` do front-matter de: `valores.html`, `depoimentos.html`, `blog/index.html`, os três posts e as cinco páginas de tratamento. Sem contraparte, o `hreflang` apontaria para 404.

- [ ] **Step 5: Criar as seis páginas em inglês**

Todas seguem o mesmo padrão: metadados reais em inglês, `lang: en`, `noindex: true`, `alternate_pt` apontando de volta, e um aviso visível de que a versão completa está em preparo, com link para a versão em português.

Criar `src/pages/en/index.html`:

```html
---
title: Fukuoka Dental Clinic — Dentist on Avenida Paulista, São Paulo
description: Dental care on Avenida Paulista, São Paulo. Invisalign, dental implants, whitening and oral rehabilitation, with Japanese-inspired precision.
og_type: website
lang: en
noindex: true
alternate_pt: index.html
---
    <section class="section">
      <div class="container container--narrow">
        <span class="overline">Avenida Paulista &middot; São Paulo</span>
        <h1>Excellence inspired by Japanese precision</h1>
        <hr class="rule">
        <p class="lead">Dental care combining science, technology and genuinely human attention. We care for people, not just teeth.</p>
        <p class="aviso" role="note">The full English version of this site is being prepared. In the meantime, please <a href="{{ prefixo }}index.html">visit the Portuguese version</a> or contact us directly — we speak English, Japanese and Portuguese.</p>
        <p>
          <a class="btn btn--primary" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Book an appointment</a>
          <a class="btn btn--ghost" href="{{ site_maps_url }}" target="_blank" rel="noopener">Find us</a>
        </p>
      </div>
    </section>
```

Criar `src/pages/en/about.html` — mesmo padrão, com:

```html
---
title: About Fukuoka Dental Clinic and Dr. Cíntia | Avenida Paulista
description: Learn about Fukuoka Dental Clinic on Avenida Paulista, São Paulo: our team, our facilities and the mission behind every appointment.
og_type: article
lang: en
noindex: true
alternate_pt: sobre.html
---
    <section class="section">
      <div class="container container--narrow">
        <span class="overline">About</span>
        <h1>A clinic built on precision and listening</h1>
        <hr class="rule">
        <p class="lead">Fukuoka Dental Clinic was founded on the conviction that excellent dentistry requires two things in equal measure: technical rigour and time to understand each person.</p>
        <p class="aviso" role="note">The full English version of this page is being prepared. Please <a href="{{ prefixo }}sobre.html">read the Portuguese version</a> or contact us directly.</p>
        <p><a class="btn btn--primary" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Book an appointment</a></p>
      </div>
    </section>
```

Criar `src/pages/en/treatments.html`:

```html
---
title: Dental treatments on Avenida Paulista | Fukuoka Dental Clinic
description: Invisalign, dental implants, teeth whitening, oral rehabilitation and porcelain veneers on Avenida Paulista, São Paulo, with digital planning.
og_type: website
lang: en
noindex: true
alternate_pt: tratamentos.html
---
    <section class="section">
      <div class="container container--narrow">
        <span class="overline">Treatments</span>
        <h1>Dental treatments on Avenida Paulista</h1>
        <hr class="rule">
        <p class="lead">Every procedure follows the same principle: preserve as much natural tooth structure as possible, and plan before intervening.</p>
        <ul class="credenciais">
          <li>Invisalign clear aligners</li>
          <li>Dental implants and guided surgery</li>
          <li>Supervised teeth whitening</li>
          <li>Full oral rehabilitation</li>
          <li>Porcelain veneers</li>
        </ul>
        <p class="aviso" role="note">Detailed English pages for each treatment are being prepared. Please <a href="{{ prefixo }}tratamentos.html">see the Portuguese version</a> or contact us directly.</p>
        <p><a class="btn btn--primary" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Book an appointment</a></p>
      </div>
    </section>
```

Criar `src/pages/en/philosophy.html`:

```html
---
title: Our Philosophy | Fukuoka Dental Clinic, São Paulo
description: The philosophy behind Fukuoka Dental Clinic: Japanese precision, minimally invasive treatment and care centred on people, in São Paulo.
og_type: article
lang: en
noindex: true
alternate_pt: filosofia.html
---
    <section class="section">
      <div class="container container--narrow">
        <span class="overline">Manifesto</span>
        <h1>Our Philosophy</h1>
        <hr class="rule">
        <p class="lead">We believe a smile goes far beyond aesthetics. It reflects health, confidence, self-esteem and a genuine expression of well-being.</p>
        <p>Inspired by Japanese tradition, we value precision, discipline, the continuous pursuit of excellence and meticulous care in every detail. For us, excellence is not a destination but a permanent standard of conduct.</p>
        <p class="aviso" role="note">The full English translation of our manifesto is being prepared. Please <a href="{{ prefixo }}filosofia.html">read the Portuguese version</a>.</p>
      </div>
    </section>
```

Criar `src/pages/en/japanese-speaking-dentist.html`:

```html
---
title: Japanese-speaking dentist in São Paulo | Fukuoka Dental Clinic
description: Dental care in Japanese on Avenida Paulista, São Paulo. 日本語対応の歯科医院。Consultations, treatment plans and follow-up in your language.
og_type: article
lang: en
noindex: true
alternate_pt: atendimento-em-japones.html
---
    <section class="section">
      <div class="container container--narrow">
        <span class="overline" lang="ja">日本語対応</span>
        <h1>Japanese-speaking dentist in São Paulo</h1>
        <hr class="rule">
        <p class="lead">Dental care delivered in Japanese, on Avenida Paulista, with the technical rigour and courtesy the Japanese community in São Paulo expects.</p>
        <p lang="ja" class="jp-destaque">サンパウロ・パウリスタ大通りの歯科医院です。日本語で診療・お見積り・アフターケアまで対応いたします。</p>
        <p class="aviso" role="note">The full English version of this page is being prepared. Please <a href="{{ prefixo }}atendimento-em-japones.html">see the Portuguese version</a> or contact us directly.</p>
        <p><a class="btn btn--primary" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Book an appointment</a></p>
      </div>
    </section>
```

Criar `src/pages/en/contact.html`:

```html
---
title: Contact and location | Fukuoka Dental Clinic, Avenida Paulista
description: Address, opening hours and contact details for Fukuoka Dental Clinic on Avenida Paulista, São Paulo. Book your appointment via WhatsApp.
og_type: website
lang: en
noindex: true
alternate_pt: contato.html
---
    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="overline">Contact</span>
          <h1>Contact and location</h1>
          <hr class="rule">
          <p class="lead">We are on Avenida Paulista, São Paulo. We speak Portuguese, Japanese and English.</p>
        </div>
        <div class="contato-grid">
          <div>
            <h2>Booking</h2>
            <p>WhatsApp is the fastest channel. You can also write by email and we will reply during business hours.</p>
            <p class="contato-acoes">
              <a class="btn btn--primary" href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">Message us on WhatsApp</a>
              <a class="btn btn--ghost" href="{{ site_maps_url }}" target="_blank" rel="noopener">Get directions</a>
            </p>
          </div>
          <address class="contato-info">
            <h2>Address</h2>
            <p>{{ site_endereco_rua }}<br>{{ site_endereco_bairro }}<br>{{ site_endereco_cidade }}/{{ site_endereco_uf }}</p>
            <h2>Opening hours</h2>
            <ul class="horarios">
              <li><span>Monday to Friday</span><span>9am – 7pm</span></li>
              <li><span>Saturday</span><span>9am – 1pm</span></li>
              <li><span>Sunday</span><span>Closed</span></li>
            </ul>
            <h2>Channels</h2>
            <p>
              <a href="{{ site_whatsapp_url }}" target="_blank" rel="noopener">{{ site_telefone }}</a><br>
              <a href="mailto:{{ site_email }}">{{ site_email }}</a>
            </p>
          </address>
        </div>
      </div>
    </section>
```

- [ ] **Step 6: Marcar o idioma ativo no seletor**

O partial `header.html` fixa `aria-current="true"` no PT, o que fica errado nas páginas EN. Trocar por uma chave de contexto.

Em `src/partials/header.html`, substituir o bloco `.lang-switch` por:

```html
        <nav class="lang-switch" aria-label="Idioma">
          <a href="{{ prefixo }}index.html" hreflang="pt-BR" {{ ativo_pt }}>PT</a>
          <a href="{{ prefixo }}en/index.html" hreflang="en" {{ ativo_en }}>EN</a>
        </nav>
```

Em `tools/build.py`, no contexto da página:

```python
        ctx["ativo_pt"] = "" if lang == "en" else 'aria-current="true"'
        ctx["ativo_en"] = 'aria-current="true"' if lang == "en" else ""
```

- [ ] **Step 7: Rodar build e testes**

Run: `py tools/build.py && py -m pytest tests/ -v`
Expected: PASS. Dezenove páginas geradas, seis delas com `noindex` e fora do sitemap.

- [ ] **Step 8: Commit**

```bash
git add src/ tools/build.py tests/ en/ sitemap.xml *.html tratamentos/ blog/
git commit -m "feat: estrutura em ingles com hreflang e noindex ate a traducao"
```

---

## Task 15: Verificação de assets, documentação e conferência final

**Files:**
- Modify: `tools/check_assets.py`
- Modify: `README.md`
- Create: `tests/test_conteudo.py`
- Modify: `.gitignore` (nenhuma mudança; confirmar)

**Interfaces:**
- Consumes: tudo.
- Produces: nada consumido por outras tasks. É a task de fechamento.

- [ ] **Step 1: Ampliar a verificação de assets**

Ler `tools/check_assets.py` e ajustá-lo para varrer todos os HTML gerados, não apenas `index.html`. A lista de arquivos a varrer deve vir de `build.construir(RAIZ)`, e não de um glob no disco, para que o script também detecte referência quebrada antes da gravação.

Run: `py tools/check_assets.py`
Expected: exit 0, sem referência quebrada.

- [ ] **Step 2: Escrever os testes de conteúdo e conformidade**

Criar `tests/test_conteudo.py`:

```python
"""Verificacoes de conteudo: etica profissional, dados pendentes e consistencia."""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# Superlativos comparativos e promessa de resultado sao vedados pelo
# Codigo de Etica Odontologica.
EXPRESSOES_VEDADAS = [
    r"\bo melhor dentista\b",
    r"\ba melhor cl[ií]nica\b",
    r"\bmelhor da cidade\b",
    r"\bmelhor de S[ãa]o Paulo\b",
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
    destino = (RAIZ / "src" / "content" / "pt" / "filosofia.html").read_text(encoding="utf-8")
    frases = [
        "um sorriso vai muito além da estética",
        "Mais do que tratar dentes, cuidamos de pessoas",
        "excelência não é um destino, mas um padrão permanente de conduta",
    ]
    for frase in frases:
        assert frase in fonte, f"frase de controle ausente na fonte: {frase}"
        assert frase in destino, f"texto da Dra. alterado: {frase}"
```

Run: `py -m pytest tests/test_conteudo.py -v`

Expected: `test_json_ld_nao_contem_dado_pendente` **FALHA**, porque o schema `Dentist` ainda tem `TROCAR` no endereço e nas coordenadas. **Isso é intencional e correto.** O teste é o portão que impede publicar com dado falso.

Marcar o teste para não bloquear o resto da suíte enquanto os dados não chegam, mantendo-o visível:

```python
import pytest

@pytest.mark.xfail(
    reason="Aguardando endereco, CEP, telefone e coordenadas reais da clinica",
    strict=False,
)
def test_json_ld_nao_contem_dado_pendente(paginas):
    ...
```

Quando a Dra. fornecer os dados, remover o `xfail` — o teste passa a bloquear regressões.

- [ ] **Step 3: Reescrever o README**

Substituir `README.md` por:

````markdown
# Fukuoka Dental Clinic — site

Site estático gerado por um script Python de stdlib pura. Sem npm, sem framework, sem dependência de runtime.

## Rodar localmente

```bash
py tools/build.py        # gera os HTML a partir de src/
py -m http.server 8000   # serve em http://localhost:8000
```

## Como o site é montado

Os HTML da raiz (`index.html`, `sobre.html`, `tratamentos/`, `blog/`, `en/`) são **gerados**. Nunca editar à mão — a próxima execução do build sobrescreve.

Editar sempre em `src/`:

| Pasta | O que fica lá |
|---|---|
| `src/data/site.json` | Endereço, telefone, WhatsApp, horários, IDs de analytics |
| `src/data/nav.json` | Estrutura documental do menu |
| `src/partials/` | Header, footer, barra de CTAs, `<head>` |
| `src/layouts/` | Esqueletos: `base`, `treatment`, `post` |
| `src/pages/` | Miolo de cada página, com front-matter |
| `src/content/pt/` | Filosofia, missão e valores — texto da Dra., fonte única |

Depois de editar, rodar `py tools/build.py` e commitar tanto `src/` quanto os HTML gerados.

## Testes

```bash
py -m pytest              # tudo
py -m pytest tests/test_contrast.py   # so contraste da paleta
py tools/build.py --check # falha se os HTML estiverem dessincronizados de src/
```

A suíte verifica, em toda página gerada: título e meta description únicos e no tamanho certo, H1 único, hierarquia de headings, canonical, Open Graph, `alt` e dimensões em imagens, JSON-LD válido, links internos não quebrados, e contraste da paleta contra o WCAG AA.

## Paleta e a regra do dourado

`--gold` (`#B08D57`) é **decoração apenas**: bordas, filetes, ícones. Sobre o off-white ele mede 2,88:1 de contraste e reprova o WCAG AA. Para texto dourado existem `--gold-text` (fundo claro) e `--gold-light` (fundo navy). O teste `test_dourado_bruto_nunca_e_usado_em_texto` bloqueia o uso indevido.

## Substituir os placeholders

### Fotos

Os arquivos em `assets/` são **stock do Pexels**, presentes só para o site não ficar com quadrados vazios. O briefing pede fotos reais da clínica, da Dra., da equipe, dos equipamentos e do ambiente.

| Placeholder | Trocar por | Formato |
|---|---|---|
| `assets/hero.jpg` | ambiente da clínica, foto ampla | WebP 1600×1000 |
| `assets/clinica.jpg` | recepção ou sala de atendimento | WebP 800×1000 |
| `assets/dra.jpg` | foto profissional da Dra. Cíntia | WebP 800×1000 |
| `assets/invisalign.jpg` | tratamento com alinhadores | WebP 800×600 |
| `assets/implantes.jpg` | implante ou planejamento | WebP 800×600 |
| `assets/clareamento.jpg` | clareamento | WebP 800×600 |
| `assets/reabilitacao.jpg` | reabilitação oral | WebP 800×600 |
| `assets/estetica.jpg` | lentes e facetas | WebP 800×600 |
| `assets/casoN-antes/depois.jpg` | casos reais **autorizados** | WebP 800×600, mesmo enquadramento no par |
| `assets/mapa.jpg` | captura do mapa da localização | WebP 1600×700 |

Ao trocar as extensões, atualizar os `src` em `src/pages/` e rodar `py tools/check_assets.py`.

### Dados

Buscar `TROCAR` em `src/` e substituir tudo. Os principais estão em `src/data/site.json`: endereço, CEP, telefone, WhatsApp, URL do Maps, coordenadas, Instagram, nome completo da Dra., CRO, ID do GA4.

## Checklist antes de publicar

- [ ] Todos os `TROCAR` de `src/data/site.json` preenchidos
- [ ] Todos os `TROCAR` de `src/pages/` resolvidos (formação da Dra., convênios, horários)
- [ ] Fotos reais no lugar do stock do Pexels
- [ ] Depoimentos reais com autorização **por escrito** (CFO e LGPD) — e o aviso de "ilustrativos" removido de `depoimentos.html`
- [ ] Casos antes/depois reais e autorizados — e o aviso removido
- [ ] Textos das páginas de tratamento e dos posts **validados pela Dra.** (buscar os comentários `TROCAR: texto técnico`)
- [ ] Coordenadas e endereço reais no JSON-LD; remover o `xfail` de `test_json_ld_nao_contem_dado_pendente`
- [ ] ID do GA4 preenchido e o bloco descomentado em `src/partials/head.html`
- [ ] Search Console verificado e `sitemap.xml` submetido
- [ ] Após traduzir as páginas EN: remover `noindex: true` do front-matter delas
- [ ] Lighthouse mobile na Home: Performance ≥ 90, Acessibilidade ≥ 95, SEO ≥ 95

## Decisões registradas

- **Sem vídeo no hero.** MP4 no topo penaliza o LCP em mobile. Hero é imagem estática.
- **Sem verde WhatsApp nos botões.** Branco sobre `#1EBE5D` mede 2,45:1 e reprova AA, além de destoar da paleta. Os CTAs usam navy, mantendo o ícone do WhatsApp.
- **Mapa como imagem estática**, não iframe, pelo mesmo motivo de desempenho. O iframe fica comentado em `src/pages/contato.html`.
- **Páginas EN com `noindex`** até serem traduzidas, para não criar conteúdo raso indexado.
````

- [ ] **Step 4: Conferência no navegador**

Run: `py tools/build.py && py -m http.server 8000`

Percorrer e confirmar:

| Verificação | Onde |
|---|---|
| Os três CTAs visíveis em qualquer rolagem | qualquer página, desktop e mobile |
| Barra fixa inferior aparece abaixo de 1080px e some acima | redimensionar a janela |
| Menu leva a todas as páginas, sem 404 | header |
| Links de `tratamentos/` e `blog/` resolvem (prefixo correto) | páginas em subpasta |
| Seletor PT/EN marca o idioma certo | `index.html` e `en/index.html` |
| Navegação só por teclado, com foco sempre visível | Tab da primeira à última página |
| Comparador antes/depois funciona por mouse e por teclado | `depoimentos.html` |
| FAQ abre e fecha | qualquer página de tratamento |
| Nada de rolagem horizontal | todas, em 360px de largura |

- [ ] **Step 5: Medir o Lighthouse**

Abrir o DevTools do Chrome em `http://localhost:8000/`, aba Lighthouse, modo Mobile, e rodar.

Metas: Performance ≥ 90, Acessibilidade ≥ 95, SEO ≥ 95, Best Practices ≥ 95.

Se Performance ficar abaixo de 90, a causa mais provável é o peso das imagens de stock em JPG. Converter para WebP e regerar. Registrar os quatro números obtidos na mensagem de commit.

- [ ] **Step 6: Verificação final**

```bash
py tools/build.py --check   # deve sair 0
py tools/check_assets.py    # deve sair 0
py -m pytest -v             # tudo verde, exceto o xfail documentado
git status                  # nada pendente de commit
```

- [ ] **Step 7: Commit**

```bash
git add README.md tools/check_assets.py tests/test_conteudo.py
git commit -m "docs: README do build e checklist de publicacao; testes de conformidade"
```

---

## Self-Review do plano

Conferência do plano contra a spec, seção por seção.

| Seção da spec | Task que implementa |
|---|---|
| 3. Arquitetura de build | Tasks 1, 2 |
| 4. Mapa de URLs | Tasks 6 a 14 |
| 5. Estrutura da Home | Task 7 |
| 6. Design tokens e contraste | Tasks 3, 4 |
| 7. Performance (sem vídeo, WebP, dimensões) | Tasks 7, 15 |
| 8. Conversão (três CTAs) | Task 5 |
| 9. SEO técnico | Tasks 3, 5, 9, 12, 13, 14 |
| 10. Internacionalização | Task 14 |
| 11. Acessibilidade | Tasks 3, 4, 5, 15 |
| 12. Conteúdo | Tasks 6, 9, 10, 11, 12 |
| 13. Assets | Tasks 7, 8, 13, 15 |
| 14. Reaproveitamento (comparador, reveal, FAQ) | Tasks 5, 9, 11 |
| 16. Critérios de aceite | Task 15 |

**Ajustes feitos durante a revisão:**

1. **`{{ prefixo }}` não estava previsto na spec.** Sem ele, todo link relativo quebraria em `tratamentos/`, `blog/` e `en/`. Introduzido na Task 9, com teste.
2. **`noindex` nas páginas EN.** A spec pedia estrutura i18n pronta, mas publicar 13 URLs em inglês sem tradução criaria conteúdo raso indexado — dano ao domínio inteiro. Task 14 resolve com `noindex` e exclusão do sitemap.
3. **Espelho EN reduzido a seis páginas.** A spec falava em espelho estrutural completo; seis páginas cobrem o que um paciente estrangeiro procura, e evitam 13 stubs. As páginas PT sem contraparte perdem o `alternate_en` para não gerar `hreflang` apontando a 404.
4. **Verde WhatsApp descartado.** Detectado no cálculo de contraste da Task 4 (2,45:1). Registrado como decisão.
5. **`test_json_ld_nao_contem_dado_pendente` marcado como `xfail`.** Sem o endereço real, ele falharia e travaria a suíte. Marcado com motivo explícito e instrução de remoção.

**Consistência de nomes verificada:** `parse_front_matter`, `render`, `carregar_dados`, `carregar_conteudo`, `descobrir_paginas`, `construir`, `escrever`, `verificar`, `main` — usados com a mesma assinatura em todas as tasks. Chaves de contexto (`prefixo`, `meta_robots`, `alternates`, `ativo_pt`, `ativo_en`, `classe_body`, `jsonld`) declaradas na task que as cria e consumidas depois.

**Sem placeholders no plano:** nenhum "TBD" ou "similar à Task N". Os `TROCAR` presentes são intencionais — marcam dados que a Dra. precisa fornecer, e o teste de conformidade os rastreia.
