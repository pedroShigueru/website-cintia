"""Gera SVGs placeholder em assets/ nos tamanhos finais das imagens reais."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="{w}" height="{h}" fill="{bg}"/>
  <text x="50%" y="50%" fill="{fg}" font-family="sans-serif" font-size="{fs}"
        text-anchor="middle" dominant-baseline="middle">{label}</text>
</svg>"""


def svg(name: str, w: int, h: int, bg: str, fg: str, label: str) -> None:
    content = TEMPLATE.format(w=w, h=h, bg=bg, fg=fg, fs=max(h // 14, 16), label=label)
    (OUT / name).write_text(content, encoding="utf-8")


svg("hero-poster.svg", 1920, 1080, "#0A3B3B", "#EFE7D8", "VÍDEO HERO — trocar por assets/hero.mp4 (max 3MB)")
svg("dra.svg", 800, 1000, "#EFE7D8", "#0E4F4F", "FOTO DRA. CÍNTIA (800x1000)")
svg("implantes.svg", 800, 600, "#DCE7E7", "#0E4F4F", "FOTO IMPLANTES (800x600)")
svg("invisalign.svg", 800, 600, "#F0E6D2", "#0E4F4F", "FOTO INVISALIGN (800x600)")
for i in (1, 2, 3):
    svg(f"caso{i}-antes.svg", 800, 600, "#8FA6A6", "#FFFFFF", f"CASO {i} — ANTES")
    svg(f"caso{i}-depois.svg", 800, 600, "#0E4F4F", "#FFFFFF", f"CASO {i} — DEPOIS")
    svg(f"paciente{i}.svg", 200, 200, "#B98A44", "#FFFFFF", f"P{i}")
print(f"Placeholders gerados em {OUT}")
