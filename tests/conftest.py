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
