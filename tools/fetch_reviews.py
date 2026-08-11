"""Busca as avaliacoes do Perfil da Empresa no Google e grava em src/data/avaliacoes.json.

Roda no build, nunca no navegador do paciente. Isso mantem a chave de API
fora do HTML, evita custo por visita e nao adiciona JavaScript de terceiro
a uma pagina que precisa de PageSpeed alto.

Uso:
    set GOOGLE_MAPS_API_KEY=...        (Windows, cmd)
    $env:GOOGLE_MAPS_API_KEY="..."     (PowerShell)
    py tools/fetch_reviews.py

Depois rode `py tools/build.py` para as avaliacoes entrarem no HTML.

Limites da API, para nao haver surpresa:
  - devolve no maximo 5 avaliacoes, e nao da para escolher quais;
  - os Termos do Google exigem exibir o nome do autor e link para o perfil,
    o que este projeto faz;
  - a chamada e cobrada. Um build por dia e irrelevante; um por visita nao.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "src" / "data" / "avaliacoes.json"
ENDPOINT = "https://places.googleapis.com/v1/places/{place_id}?languageCode=pt-BR"
CAMPOS = "rating,userRatingCount,googleMapsUri,reviews"


def _pedir(place_id: str, chave: str) -> dict:
    req = urllib.request.Request(
        ENDPOINT.format(place_id=place_id),
        headers={"X-Goog-Api-Key": chave, "X-Goog-FieldMask": CAMPOS},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _converter(bruto: dict) -> list[dict]:
    """Reduz a resposta da API ao minimo que o site exibe."""
    avaliacoes = []
    for r in bruto.get("reviews", []):
        texto = (r.get("originalText") or r.get("text") or {}).get("text", "").strip()
        autor = (r.get("authorAttribution") or {}).get("displayName", "").strip()
        if not texto or not autor:
            continue
        avaliacoes.append({
            "autor": autor,
            "nota": r.get("rating", 5),
            "quando": r.get("relativePublishTimeDescription", ""),
            "texto": texto,
        })
    return avaliacoes


def main() -> int:
    atual = json.loads(DESTINO.read_text(encoding="utf-8"))
    place_id = atual.get("place_id", "")
    if not place_id or place_id.startswith("TROCAR"):
        print("Falta o place_id em src/data/avaliacoes.json.")
        print("Como obter: https://developers.google.com/maps/documentation/places/web-service/place-id")
        return 1

    chave = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not chave:
        print("Defina a variavel de ambiente GOOGLE_MAPS_API_KEY.")
        return 1

    try:
        bruto = _pedir(place_id, chave)
    except urllib.error.HTTPError as e:
        print(f"A API respondeu {e.code}: {e.read().decode('utf-8', 'replace')[:400]}")
        return 1
    except urllib.error.URLError as e:
        print(f"Falha de rede: {e.reason}")
        return 1

    avaliacoes = _converter(bruto)
    if not avaliacoes:
        print("A API nao devolveu nenhuma avaliacao com texto. Nada foi gravado.")
        return 1

    atual.update({
        "url_perfil": bruto.get("googleMapsUri", atual.get("url_perfil", "")),
        "nota": bruto.get("rating"),
        "total": bruto.get("userRatingCount"),
        "atualizado_em": date.today().isoformat(),
        "avaliacoes": avaliacoes,
    })
    DESTINO.write_text(
        json.dumps(atual, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"{len(avaliacoes)} avaliacao(oes) gravadas. "
        f"Nota {atual['nota']} de {atual['total']} avaliacoes."
    )
    print("Agora rode: py tools/build.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
