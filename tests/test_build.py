"""Testes do gerador estatico."""
import json
import sys
import textwrap
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
    (tmp_path / "src" / "partials" / "cta-bar.html").write_text(
        "<nav>cta</nav>", encoding="utf-8"
    )
    (tmp_path / "src" / "partials" / "header.html").write_text(
        "<header>{{ site_nome }}{{ cta_bar }}</header>", encoding="utf-8"
    )
    (tmp_path / "src" / "partials" / "footer.html").write_text(
        "<footer>f</footer>", encoding="utf-8"
    )
    (tmp_path / "src" / "partials" / "head.html").write_text(
        "<title>{{ title }}</title>", encoding="utf-8"
    )
    (tmp_path / "src" / "layouts" / "base.html").write_text(
        '<html lang="{{ lang }}"><head>{{ head }}</head>'
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
        (sub / "invisalign.html").write_text(
            "---\ntitle: Inv\n---\n<main>x</main>", encoding="utf-8"
        )
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


class TestContextoDePagina:
    def test_prefixo_reflete_a_profundidade_da_url(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        sub = raiz / "src" / "pages" / "tratamentos"
        sub.mkdir()
        (sub / "invisalign.html").write_text(
            '---\ntitle: Inv\n---\n<a href="{{ prefixo }}index.html">home</a>',
            encoding="utf-8",
        )
        (raiz / "src" / "pages" / "index.html").write_text(
            '---\ntitle: Home\n---\n<a href="{{ prefixo }}index.html">home</a>',
            encoding="utf-8",
        )
        saida = build.construir(raiz)
        assert 'href="index.html"' in saida["index.html"]
        assert 'href="../index.html"' in saida["tratamentos/invisalign.html"]

    def test_front_matter_opcional_tem_default_vazio(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "layouts" / "base.html").write_text(
            '<body class="{{ classe_body }}">{{ jsonld }}{{ conteudo }}</body>',
            encoding="utf-8",
        )
        assert 'class=""' in build.construir(raiz)["index.html"]

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
        assert 'hreflang="x-default" href="https://exemplo.com.br/"' in html

    def test_sem_alternates_nao_emite_hreflang(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "partials" / "head.html").write_text(
            "<title>{{ title }}</title>{{ alternates }}", encoding="utf-8"
        )
        assert "hreflang" not in build.construir(raiz)["index.html"]

    def test_noindex_emite_meta_robots_e_sai_do_sitemap(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "partials" / "head.html").write_text(
            "<title>{{ title }}</title>{{ meta_robots }}", encoding="utf-8"
        )
        en = raiz / "src" / "pages" / "en"
        en.mkdir()
        (en / "index.html").write_text(
            "---\ntitle: Home EN\nlang: en\nnoindex: true\n---\n<main>hi</main>",
            encoding="utf-8",
        )
        saida = build.construir(raiz)
        assert '<meta name="robots" content="noindex, follow">' in saida["en/index.html"]
        assert "meta name=\"robots\"" not in saida["index.html"]
        assert "en/index.html" not in saida["sitemap.xml"]
        assert "<loc>https://exemplo.com.br/</loc>" in saida["sitemap.xml"]

    def test_front_matter_aceita_variaveis(self, tmp_path):
        """Evita duplicar endereco e telefone no JSON-LD de cada pagina."""
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "pages" / "index.html").write_text(
            "---\ntitle: {{ site_nome }} - Home\n---\n<main>x</main>",
            encoding="utf-8",
        )
        html = build.construir(raiz)["index.html"]
        assert "<title>Fukuoka - Home</title>" in html
        assert "{{" not in html

    def test_partial_traduzido_tem_precedencia(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "partials" / "header-en.html").write_text(
            "<header>EN</header>", encoding="utf-8"
        )
        en = raiz / "src" / "pages" / "en"
        en.mkdir()
        (en / "index.html").write_text(
            "---\ntitle: Home EN\nlang: en\n---\n<main>hi</main>", encoding="utf-8"
        )
        saida = build.construir(raiz)
        assert "<header>EN</header>" in saida["en/index.html"]
        # Sem contraparte traduzida, a pagina PT segue com o partial padrao.
        assert "<header>Fukuoka" in saida["index.html"]

    def test_menu_marca_a_pagina_atual(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "partials" / "header.html").write_text(
            '<a href="{{ prefixo }}index.html" class="logo">L</a>'
            '<nav class="site-nav">'
            '<a href="{{ prefixo }}sobre.html">Sobre</a>'
            '<a href="{{ prefixo }}tratamentos.html">Tratamentos</a>'
            "</nav>",
            encoding="utf-8",
        )
        (raiz / "src" / "pages" / "sobre.html").write_text(
            "---\ntitle: Sobre\n---\n<main>x</main>", encoding="utf-8"
        )
        saida = build.construir(raiz)
        assert '<a href="sobre.html" aria-current="page">Sobre</a>' in saida["sobre.html"]
        assert 'href="tratamentos.html" aria-current' not in saida["sobre.html"]
        # O logo aponta para a home mas nao faz parte do menu.
        assert '<a href="index.html" class="logo">' in saida["index.html"]

    def test_menu_marca_a_secao_pai_em_subpaginas(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "partials" / "header.html").write_text(
            '<nav class="site-nav"><a href="{{ prefixo }}tratamentos.html">T</a></nav>',
            encoding="utf-8",
        )
        sub = raiz / "src" / "pages" / "tratamentos"
        sub.mkdir()
        (sub / "invisalign.html").write_text(
            "---\ntitle: Inv\n---\n<main>x</main>", encoding="utf-8"
        )
        html = build.construir(raiz)["tratamentos/invisalign.html"]
        assert '<a href="../tratamentos.html" aria-current="page">T</a>' in html

    def test_seletor_de_idioma_marca_a_lingua_ativa(self, tmp_path):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "partials" / "header.html").write_text(
            '<a {{ ativo_pt }}>PT</a><a {{ ativo_en }}>EN</a>', encoding="utf-8"
        )
        en = raiz / "src" / "pages" / "en"
        en.mkdir()
        (en / "index.html").write_text(
            "---\ntitle: EN\nlang: en\n---\n<main>hi</main>", encoding="utf-8"
        )
        saida = build.construir(raiz)
        assert '<a aria-current="true">PT</a><a >EN</a>' in saida["index.html"]
        assert '<a ><a' not in saida["en/index.html"]
        assert '<a aria-current="true">EN</a>' in saida["en/index.html"]


class TestAvaliacoes:
    """Blocos gerados a partir do Perfil da Empresa no Google."""

    def _com_avaliacoes(self, tmp_path, dados):
        raiz = _montar_projeto(tmp_path)
        (raiz / "src" / "data" / "avaliacoes.json").write_text(
            json.dumps(dados), encoding="utf-8"
        )
        (raiz / "src" / "pages" / "index.html").write_text(
            "---\ntitle: Home\n---\n<main>{{ avaliacoes_faixa }}{{ avaliacoes_selo }}"
            "{{ avaliacoes_todas }}</main>",
            encoding="utf-8",
        )
        return raiz

    def test_sem_avaliacoes_os_blocos_ficam_vazios(self, tmp_path):
        """Uma clinica sem avaliacoes nao pode exibir 'nota 0' nem secao vazia."""
        raiz = self._com_avaliacoes(tmp_path, {"nota": None, "total": None, "avaliacoes": []})
        html = build.construir(raiz)["index.html"]
        assert "<main></main>" in html

    def test_faixa_traz_nota_total_e_link(self, tmp_path):
        raiz = self._com_avaliacoes(tmp_path, {
            "nota": 5.0,
            "total": 47,
            "url_perfil": "https://maps.google.com/?cid=123",
            "avaliacoes": [
                {"autor": "M. S.", "nota": 5, "quando": "há 2 meses", "texto": "Excelente."},
            ],
        })
        html = build.construir(raiz)["index.html"]
        assert "5,0" in html                      # virgula decimal, pt-BR
        assert "47" in html
        assert "https://maps.google.com/?cid=123" in html
        assert "Ver todas as avaliações no Google" in html
        assert "M. S." in html
        assert "Excelente." in html

    def test_faixa_limita_o_destaque_a_tres(self, tmp_path):
        raiz = self._com_avaliacoes(tmp_path, {
            "nota": 4.9, "total": 30, "url_perfil": "https://x",
            "avaliacoes": [
                {"autor": f"A{i}", "nota": 5, "quando": "hoje", "texto": f"Texto {i}"}
                for i in range(5)
            ],
        })
        html = build.construir(raiz)["index.html"]
        faixa = html.split("avaliacoes-todas")[0]
        assert faixa.count('class="avaliacao"') == 3
        # A pagina de depoimentos mostra todas.
        assert html.count('class="avaliacao"') == 3 + 5

    @pytest.mark.parametrize("nota,esperado", [(5.0, "5,0"), (4.9, "4,9"), (4.0, "4,0")])
    def test_nota_com_uma_casa_e_virgula(self, tmp_path, nota, esperado):
        raiz = self._com_avaliacoes(tmp_path, {
            "nota": nota, "total": 12, "url_perfil": "https://x",
            "avaliacoes": [{"autor": "A", "nota": 5, "quando": "hoje", "texto": "t"}],
        })
        assert esperado in build.construir(raiz)["index.html"]

    def test_texto_do_autor_e_escapado(self, tmp_path):
        """Conteudo vindo da API nao pode injetar HTML."""
        raiz = self._com_avaliacoes(tmp_path, {
            "nota": 5.0, "total": 1, "url_perfil": "https://x",
            "avaliacoes": [{
                "autor": "<script>x</script>", "nota": 5, "quando": "hoje",
                "texto": 'Ótimo & "recomendo" <b>muito</b>',
            }],
        })
        html = build.construir(raiz)["index.html"]
        assert "<script>x</script>" not in html
        assert "&lt;script&gt;" in html
        assert "&amp;" in html

    def test_selo_e_compacto_e_linka_o_perfil(self, tmp_path):
        raiz = self._com_avaliacoes(tmp_path, {
            "nota": 5.0, "total": 47, "url_perfil": "https://maps.google.com/?cid=9",
            "avaliacoes": [{"autor": "A", "nota": 5, "quando": "hoje", "texto": "t"}],
        })
        html = build.construir(raiz)["index.html"]
        selo = html.split('class="avaliacoes-selo"')[1].split("</a>")[0]
        assert "5,0" in selo and "47" in selo
