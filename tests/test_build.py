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
