# Landing Page — Dra. Cíntia

Site estático: `index.html` + `css/style.css` + `js/main.js`. Sem build. Para rodar local: `py -m http.server 8000` (Windows) / `python3 -m http.server 8000` (Mac/Linux).

## Trocando os placeholders pelos arquivos reais

| Placeholder | Trocar por | Formato recomendado |
|---|---|---|
| `assets/hero.mp4` (não existe ainda) | vídeo do consultório/sorrisos | MP4 H.264, 1920x1080, 10–20s, **max 3MB**, sem áudio |
| `assets/hero-poster.svg` | frame do vídeo | WebP 1920x1080, ~100KB (atualizar `poster` no HTML) |
| `assets/dra.svg` | foto profissional da Dra. | WebP 800x1000 |
| `assets/implantes.svg`, `assets/invisalign.svg` | fotos dos tratamentos | WebP 800x600 |
| `assets/casoN-antes/depois.svg` | casos reais **autorizados** | WebP 800x600, mesmo enquadramento no par |
| `assets/pacienteN.svg` | fotos dos pacientes (autorizadas) | WebP 200x200 |

Ao trocar, atualizar as extensões nos `src` do `index.html` e rodar `python tools/check_assets.py`.

## Checklist antes de publicar

- [ ] Número real do WhatsApp em `js/main.js` (const `WHATS_URL`)
- [ ] Buscar `TROCAR` no `index.html` e substituir tudo (CRO, endereço, Instagram, convênios, stats)
- [ ] Depoimentos reais com autorização por escrito (exigência CFO/LGPD)
- [ ] Comprimir o vídeo (ex.: HandBrake, preset Web) para ≤3MB
