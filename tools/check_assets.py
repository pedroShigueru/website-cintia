"""Verifica que toda referência local no index.html existe em disco."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPTIONAL = {"assets/hero.mp4"}  # vídeo real entra depois; o poster cobre

html = (ROOT / "index.html").read_text(encoding="utf-8")
refs = re.findall(
    r'(?:src|href|data-src|poster)="(?!https?:|data:|#|mailto:|tel:)([^"]+)"', html
)
missing = [r for r in refs if not (ROOT / r).exists() and r not in OPTIONAL]
skipped = [r for r in refs if r in OPTIONAL and not (ROOT / r).exists()]

for r in skipped:
    print(f"AVISO (opcional, ainda não existe): {r}")
if missing:
    print("FALTANDO:")
    for r in missing:
        print(f" - {r}")
    sys.exit(1)
print(f"OK — {len(refs)} referências locais verificadas.")
