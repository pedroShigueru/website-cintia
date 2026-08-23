"""Verifica que toda referencia local do site gerado existe em disco.

Roda contra a saida de build.construir(), nao contra o disco: assim uma
referencia quebrada e detectada antes de os arquivos serem gravados.
"""
import posixpath
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build  # noqa: E402

RAIZ = build.RAIZ
REFERENCIA = re.compile(
    r'(?:src|href|data-src|poster)="(?!https?:|data:|#|mailto:|tel:)([^"]+)"'
)
# Referencia dentro de comentario nao e carregada pelo navegador; nao verificamos.
COMENTARIO = re.compile(r"<!--.*?-->", re.DOTALL)


def main() -> int:
    saida = build.construir(RAIZ)
    gerados = set(saida)
    # Prefixo de publicacao (ex.: /website-cintia/ no GitHub Pages). Faz parte
    # da URL servida, mas nao do caminho em disco.
    base_path = build.carregar_dados(RAIZ)["site_base_path"]

    faltando: list[tuple[str, str]] = []
    total = 0
    for pagina, html in saida.items():
        if not pagina.endswith(".html"):
            continue
        base = posixpath.dirname(pagina)
        for ref in REFERENCIA.findall(COMENTARIO.sub("", html)):
            total += 1
            ref = ref.split("#", 1)[0].split("?", 1)[0]  # ancora nao e arquivo
            if not ref:
                continue
            # Caminho absoluto: a 404 usa, porque e servida sob qualquer URL.
            if ref.startswith(base_path):
                ref = "/" + ref[len(base_path):]
            partida = "" if ref.startswith("/") else base
            alvo = posixpath.normpath(
                posixpath.join(partida, ref.lstrip("/"))
            ).replace("\\", "/")
            if alvo in gerados or (RAIZ / alvo).exists():
                continue
            faltando.append((pagina, ref))

    if faltando:
        print("FALTANDO:")
        for pagina, ref in sorted(set(faltando)):
            print(f" - {ref}  (referenciado em {pagina})")
        return 1

    print(f"OK - {total} referencias locais verificadas em {len(gerados)} arquivos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
