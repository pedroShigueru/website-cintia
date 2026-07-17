# Landing Page Dra. Cíntia — Implantes e Invisalign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Landing page estática premium para dentista especializada em implantes e Invisalign, com hero em vídeo, CTA WhatsApp e orçamento de memória ≤200MB no navegador.

**Architecture:** Site 100% estático (um `index.html`, um CSS, um JS), sem build e sem dependências. Mídia pesada é controlada por um "gate" de vídeo em JS, imagens lazy e placeholders SVG gerados por script Python. Interações (slider antes/depois, reveal on-scroll, header) em JS puro.

**Tech Stack:** HTML5, CSS3 (custom properties, grid, scroll-snap), JavaScript vanilla (IntersectionObserver), Python 3 apenas para tooling local (placeholders e checagem de assets), Google Fonts (Fraunces + Inter).

## Global Constraints

- Stack: HTML + CSS + JS puros. **Proibido** adicionar frameworks, bibliotecas JS/CSS ou etapa de build.
- Memória no navegador do visitante: **≤200MB**. Página total (com placeholders): **≤1MB**. Vídeo real futuro: **≤3MB** (documentado, não incluso).
- Idioma de todo o conteúdo: **pt-BR**.
- Telefone WhatsApp: placeholder `5511999999999`, definido em **um único lugar** (`js/main.js`, const `WHATS_URL`). Links no HTML usam `href="#contato"` + atributo `data-whats`.
- Nome da cliente: **Dra. Cíntia** (sobrenome/CRO são placeholders marcados com `<!-- TROCAR -->`).
- Fontes: Google Fonts `Fraunces` (títulos) e `Inter` (texto) com `display=swap`.
- Acessibilidade mínima: `alt` em toda imagem informativa, contraste AA, foco visível, `prefers-reduced-motion` respeitado.
- Servidor local para verificação: `python -m http.server 8000` na raiz do projeto (verificar em `http://localhost:8000`).
- Commits frequentes: um por tarefa, mensagens `feat:`/`chore:` em inglês, com `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

## Paleta e tokens (referência para todas as tarefas)

| Token | Valor | Uso |
|---|---|---|
| `--bg` | `#FAF8F5` | fundo geral (branco quente) |
| `--surface` | `#FFFFFF` | cards |
| `--ink` | `#172A2C` | texto principal |
| `--ink-soft` | `#4A5D5F` | texto secundário |
| `--teal` | `#0E4F4F` | cor de marca (azul-petróleo) |
| `--teal-deep` | `#0A3B3B` | hover/fundos escuros |
| `--sand` | `#EFE7D8` | fundos alternados |
| `--gold` | `#B98A44` | acentos/overlines |
| `--whatsapp` | `#1EBE5D` | CTAs de WhatsApp |

---

### Task 1: Esqueleto HTML + design system CSS

**Files:**
- Create: `index.html`
- Create: `css/style.css`
- Create: `js/main.js` (vazio por enquanto, só o arquivo)

**Interfaces:**
- Produces: ids de âncora `#inicio`, `#especialidades`, `#sobre`, `#resultados`, `#como-funciona`, `#depoimentos`, `#faq`, `#contato` (consumidos pelo menu e tarefas 3–7); classes utilitárias `.container`, `.section`, `.section-head`, `.btn`, `.btn--whats`, `.btn--ghost` (consumidas por todas as seções).

- [ ] **Step 1: Criar `index.html` com o esqueleto completo**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dra. Cíntia — Implantes Dentários e Invisalign</title>
  <meta name="description" content="Recupere a confiança do seu sorriso com implantes dentários e Invisalign. Planejamento digital e atendimento humanizado. Agende sua avaliação.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css">
</head>
<body>

  <header class="site-header"><!-- Task 3 --></header>

  <main>
    <section class="hero" id="inicio"><!-- Task 3 --></section>
    <section class="section" id="especialidades"><!-- Task 4 --></section>
    <section class="section section--sand" id="sobre"><!-- Task 4 --></section>
    <section class="section" id="resultados"><!-- Task 5 --></section>
    <section class="section section--dark" id="como-funciona"><!-- Task 6 --></section>
    <section class="section" id="depoimentos"><!-- Task 6 --></section>
    <section class="section section--sand" id="faq"><!-- Task 6 --></section>
    <section class="section" id="contato"><!-- Task 7 --></section>
  </main>

  <footer class="site-footer"><!-- Task 7 --></footer>

  <!-- Task 7: botão flutuante WhatsApp -->

  <script src="js/main.js" defer></script>
</body>
</html>
```

- [ ] **Step 2: Criar `css/style.css` com tokens, reset e utilitários**

```css
/* ===== Tokens ===== */
:root {
  --bg: #FAF8F5;
  --surface: #FFFFFF;
  --ink: #172A2C;
  --ink-soft: #4A5D5F;
  --teal: #0E4F4F;
  --teal-deep: #0A3B3B;
  --sand: #EFE7D8;
  --gold: #B98A44;
  --whatsapp: #1EBE5D;
  --whatsapp-deep: #17A34E;

  --font-display: "Fraunces", Georgia, serif;
  --font-body: "Inter", system-ui, -apple-system, sans-serif;

  --container: 1120px;
  --radius: 20px;
  --radius-pill: 999px;
  --shadow-sm: 0 2px 10px rgba(23, 42, 44, .07);
  --shadow-md: 0 14px 40px rgba(23, 42, 44, .12);
  --space-section: clamp(4.5rem, 10vw, 8rem);
}

/* ===== Reset ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; scroll-padding-top: 6rem; }
body {
  font-family: var(--font-body);
  color: var(--ink);
  background: var(--bg);
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}
img, video { max-width: 100%; display: block; }
a { color: inherit; text-decoration: none; }
ul, ol { list-style: none; }
button, input { font: inherit; }
:focus-visible { outline: 3px solid var(--gold); outline-offset: 3px; }

/* ===== Tipografia ===== */
h1, h2, h3 {
  font-family: var(--font-display);
  font-weight: 500;
  line-height: 1.12;
  letter-spacing: -0.01em;
  text-wrap: balance;
}

/* ===== Layout ===== */
.container { max-width: var(--container); margin-inline: auto; padding-inline: 1.5rem; }
.section { padding-block: var(--space-section); }
.section--sand { background: var(--sand); }
.section--dark { background: var(--teal-deep); color: #F2EFE9; }

.section-head { max-width: 640px; margin-bottom: clamp(2.5rem, 6vw, 4rem); }
.section-head--center { margin-inline: auto; text-align: center; }
.overline {
  display: block;
  font-size: .8rem;
  font-weight: 600;
  letter-spacing: .18em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: .75rem;
}
.section--dark .overline { color: #D9B87C; }
.section-head h2 { font-size: clamp(1.9rem, 4vw, 2.75rem); }
.section-head p { margin-top: 1rem; color: var(--ink-soft); font-size: 1.06rem; }
.section--dark .section-head p { color: #C4D4D2; }

/* ===== Botões ===== */
.btn {
  display: inline-flex;
  align-items: center;
  gap: .6rem;
  padding: .95rem 1.9rem;
  border-radius: var(--radius-pill);
  font-weight: 600;
  font-size: 1rem;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform .2s ease, box-shadow .2s ease, background .2s ease;
}
.btn:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.btn--whats { background: var(--whatsapp); color: #fff; }
.btn--whats:hover { background: var(--whatsapp-deep); }
.btn--ghost { border-color: currentColor; color: var(--teal); background: transparent; }
.btn--ghost:hover { background: var(--teal); color: #fff; box-shadow: none; }
.btn svg { width: 1.25em; height: 1.25em; flex: none; }
```

- [ ] **Step 3: Criar `js/main.js` vazio**

```js
// Landing page Dra. Cíntia — interações (preenchido nas próximas tarefas)
```

- [ ] **Step 4: Verificar no navegador**

Run: `python -m http.server 8000` (na raiz do projeto), abrir `http://localhost:8000`.
Expected: página em branco com fundo `#FAF8F5`, sem erros no console (F12), fontes carregando na aba Network.

- [ ] **Step 5: Commit**

```bash
git add index.html css/style.css js/main.js
git commit -m "feat: add HTML skeleton and CSS design system"
```

---

### Task 2: Placeholders de mídia + checagem de assets

**Files:**
- Create: `tools/make_placeholders.py`
- Create: `tools/check_assets.py`
- Create: `assets/` (12 SVGs gerados pelo script)

**Interfaces:**
- Produces: `assets/hero-poster.svg`, `assets/dra.svg`, `assets/implantes.svg`, `assets/invisalign.svg`, `assets/caso{1,2,3}-antes.svg`, `assets/caso{1,2,3}-depois.svg`, `assets/paciente{1,2,3}.svg` — consumidos pelas tarefas 3–6. `tools/check_assets.py` é o teste de regressão de todas as tarefas seguintes.

- [ ] **Step 1: Escrever o teste — `tools/check_assets.py`**

```python
"""Verifica que toda referência local no index.html existe em disco."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPTIONAL = {"assets/hero.mp4"}  # vídeo real entra depois; o poster cobre

html = (ROOT / "index.html").read_text(encoding="utf-8")
refs = re.findall(
    r'(?:src|href|data-src|poster)="(?!https?:|#|mailto:|tel:)([^"]+)"', html
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
```

- [ ] **Step 2: Rodar e confirmar que passa (ainda não há refs de assets)**

Run: `python tools/check_assets.py`
Expected: `OK — 2 referências locais verificadas.` (css e js)

- [ ] **Step 3: Escrever o gerador — `tools/make_placeholders.py`**

```python
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
```

- [ ] **Step 4: Rodar o gerador**

Run: `python tools/make_placeholders.py`
Expected: `Placeholders gerados em ...\assets` e 13 arquivos `.svg` na pasta `assets/`.

- [ ] **Step 5: Rodar a checagem de novo**

Run: `python tools/check_assets.py`
Expected: `OK — 2 referências locais verificadas.`

- [ ] **Step 6: Commit**

```bash
git add tools/ assets/
git commit -m "chore: add placeholder generator and asset checker"
```

---

### Task 3: Header fixo + Hero com vídeo

**Files:**
- Modify: `index.html` (preencher `<header>` e `section.hero`)
- Modify: `css/style.css` (adicionar ao final)
- Modify: `js/main.js` (adicionar WhatsApp central, header scroll, gate de vídeo)

**Interfaces:**
- Consumes: `.btn--whats`, `.container`, âncoras da Task 1; `assets/hero-poster.svg` da Task 2.
- Produces: const `WHATS_URL` e o padrão `data-whats` (todo link WhatsApp das tarefas 4–7 usa `href="#contato" data-whats`); classe `.is-scrolled` no header.

- [ ] **Step 1: Preencher o `<header>` no `index.html`**

```html
<header class="site-header">
  <div class="container site-header__inner">
    <a href="#inicio" class="logo">Dra. <strong>Cíntia</strong></a>
    <nav class="site-nav" aria-label="Navegação principal">
      <a href="#especialidades">Especialidades</a>
      <a href="#resultados">Resultados</a>
      <a href="#sobre">Sobre</a>
      <a href="#faq">Dúvidas</a>
    </nav>
    <a href="#contato" data-whats class="btn btn--whats btn--sm">
      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.5 14.1c-.2.6-1.2 1.2-1.7 1.2-.4.1-1 .1-1.6-.1a13 13 0 0 1-5.9-5.2c-.6-1-.9-2-.9-2.6 0-.7.4-1.4.8-1.7.3-.3.7-.3 1-.3h.5c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .6l-.5.7c-.2.2-.3.4-.1.7a9 9 0 0 0 3.9 3.5c.3.1.5.1.7-.1l.8-1c.2-.3.4-.3.7-.2l2.2 1c.3.2.5.3.6.4 0 .1 0 .4-.1.6Z"/></svg>
      Agendar avaliação
    </a>
  </div>
</header>
```

- [ ] **Step 2: Preencher a `section.hero` no `index.html`**

```html
<section class="hero" id="inicio">
  <video class="hero__video" muted loop playsinline preload="none"
         poster="assets/hero-poster.svg" aria-hidden="true">
    <source data-src="assets/hero.mp4" type="video/mp4">
  </video>
  <div class="hero__overlay" aria-hidden="true"></div>
  <div class="container hero__content">
    <span class="overline">Implantes dentários &bull; Invisalign</span>
    <h1>Seu novo sorriso começa com uma conversa</h1>
    <p>Implantes e alinhadores invisíveis com planejamento digital e acompanhamento próximo — do primeiro exame ao sorriso final.</p>
    <div class="hero__actions">
      <a href="#contato" data-whats class="btn btn--whats">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.5 14.1c-.2.6-1.2 1.2-1.7 1.2-.4.1-1 .1-1.6-.1a13 13 0 0 1-5.9-5.2c-.6-1-.9-2-.9-2.6 0-.7.4-1.4.8-1.7.3-.3.7-.3 1-.3h.5c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .6l-.5.7c-.2.2-.3.4-.1.7a9 9 0 0 0 3.9 3.5c.3.1.5.1.7-.1l.8-1c.2-.3.4-.3.7-.2l2.2 1c.3.2.5.3.6.4 0 .1 0 .4-.1.6Z"/></svg>
        Agende sua avaliação
      </a>
      <a href="#resultados" class="btn btn--ghost btn--light">Ver resultados</a>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Adicionar CSS do header e hero ao final de `css/style.css`**

```css
/* ===== Header ===== */
.site-header {
  position: fixed;
  inset-inline: 0;
  top: 0;
  z-index: 50;
  padding-block: 1.1rem;
  transition: background .3s ease, box-shadow .3s ease, padding .3s ease;
}
.site-header.is-scrolled {
  background: rgba(250, 248, 245, .92);
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-sm);
  padding-block: .6rem;
}
.site-header__inner { display: flex; align-items: center; gap: 2rem; }
.logo {
  font-family: var(--font-display);
  font-size: 1.35rem;
  color: #fff;
  transition: color .3s ease;
}
.is-scrolled .logo { color: var(--teal); }
.site-nav { display: flex; gap: 1.75rem; margin-left: auto; }
.site-nav a {
  font-size: .95rem;
  font-weight: 500;
  color: rgba(255, 255, 255, .85);
  transition: color .2s ease;
}
.site-nav a:hover { color: #fff; }
.is-scrolled .site-nav a { color: var(--ink-soft); }
.is-scrolled .site-nav a:hover { color: var(--teal); }
.btn--sm { padding: .6rem 1.3rem; font-size: .9rem; }
@media (max-width: 760px) {
  .site-nav { display: none; } /* mobile: logo + CTA bastam numa landing */
}

/* ===== Hero ===== */
.hero {
  position: relative;
  min-height: 100svh;
  display: flex;
  align-items: center;
  color: #fff;
  overflow: hidden;
}
.hero__video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.hero__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, rgba(10, 47, 47, .88) 0%, rgba(10, 47, 47, .55) 55%, rgba(10, 47, 47, .25) 100%);
}
.hero__content { position: relative; max-width: 680px; padding-block: 8rem 6rem; }
.hero__content h1 { font-size: clamp(2.5rem, 6vw, 4.25rem); }
.hero__content p {
  margin-top: 1.25rem;
  font-size: clamp(1.05rem, 2vw, 1.2rem);
  color: rgba(255, 255, 255, .88);
  max-width: 34em;
}
.hero__actions { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 2.25rem; }
.btn--light { color: #fff; }
.btn--light:hover { background: #fff; color: var(--teal); }
```

- [ ] **Step 4: Adicionar interações em `js/main.js` (substituir o conteúdo)**

```js
// ===== WhatsApp: número definido UMA vez =====
const WHATS_URL =
  "https://wa.me/5511999999999?text=" + // TROCAR pelo número real
  encodeURIComponent("Olá! Vim pelo site e quero agendar uma avaliação.");
document.querySelectorAll("[data-whats]").forEach((a) => {
  a.href = WHATS_URL;
  a.target = "_blank";
  a.rel = "noopener";
});

// ===== Header: fundo ao rolar =====
const header = document.querySelector(".site-header");
const onScroll = () => header.classList.toggle("is-scrolled", scrollY > 24);
addEventListener("scroll", onScroll, { passive: true });
onScroll();

// ===== Hero: carrega o vídeo só quando vale a pena (orçamento de RAM) =====
const video = document.querySelector(".hero__video");
if (video) {
  const wantsVideo =
    matchMedia("(min-width: 768px)").matches &&
    !matchMedia("(prefers-reduced-motion: reduce)").matches &&
    !(navigator.connection && navigator.connection.saveData);
  if (wantsVideo) {
    video.querySelectorAll("source[data-src]").forEach((s) => (s.src = s.dataset.src));
    video.load();
    video.play().catch(() => {}); // autoplay bloqueado não é erro
  }
}
```

- [ ] **Step 5: Verificar**

Run: `python tools/check_assets.py`
Expected: `AVISO (opcional...): assets/hero.mp4` + `OK`.

No navegador (`http://localhost:8000`): hero ocupa a tela toda com o poster escuro, título grande, dois botões; ao rolar, header ganha fundo claro com blur; botões de WhatsApp abrem `wa.me` em nova aba. Console sem erros (o 404 de `hero.mp4` não deve aparecer em desktop se o arquivo não existir — se aparecer, é o gate funcionando e tentando carregar: aceitável nesta fase, o poster permanece visível).

- [ ] **Step 6: Commit**

```bash
git add index.html css/style.css js/main.js
git commit -m "feat: add fixed header and video hero with WhatsApp CTA"
```

---

### Task 4: Especialidades + Sobre a Dra.

**Files:**
- Modify: `index.html` (seções `#especialidades` e `#sobre`)
- Modify: `css/style.css` (adicionar ao final)

**Interfaces:**
- Consumes: `.section-head`, `.overline`, `.btn--ghost`, `data-whats`; `assets/implantes.svg`, `assets/invisalign.svg`, `assets/dra.svg`.
- Produces: classe `.card` (reutilizada visualmente pela Task 6 em depoimentos).

- [ ] **Step 1: Preencher `#especialidades` no `index.html`**

```html
<section class="section" id="especialidades">
  <div class="container">
    <div class="section-head section-head--center reveal">
      <span class="overline">Especialidades</span>
      <h2>Dois caminhos para o mesmo destino: seu melhor sorriso</h2>
    </div>
    <div class="cards-2">
      <article class="card reveal">
        <img src="assets/implantes.svg" alt="Implante dentário" loading="lazy" width="800" height="600">
        <div class="card__body">
          <h3>Implantes Dentários</h3>
          <p>Recupere dentes, mastigação e confiança. Planejamento 100% digital para cirurgias mais previsíveis, rápidas e confortáveis.</p>
          <ul class="checklist">
            <li>Tomografia e planejamento guiado</li>
            <li>Do unitário ao protocolo completo</li>
            <li>Acompanhamento em todas as fases</li>
          </ul>
          <a href="#contato" data-whats class="btn btn--ghost">Avaliar meu caso</a>
        </div>
      </article>
      <article class="card reveal">
        <img src="assets/invisalign.svg" alt="Alinhador transparente Invisalign" loading="lazy" width="800" height="600">
        <div class="card__body">
          <h3>Invisalign<sup>®</sup></h3>
          <p>Alinhe os dentes sem metal e sem interferir na sua rotina: alinhadores transparentes, removíveis e planejados com simulação do resultado.</p>
          <ul class="checklist">
            <li>Praticamente invisível</li>
            <li>Removível para comer e escovar</li>
            <li>Simulação digital do sorriso final</li>
          </ul>
          <a href="#contato" data-whats class="btn btn--ghost">Quero dentes alinhados</a>
        </div>
      </article>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Preencher `#sobre` no `index.html`**

```html
<section class="section section--sand" id="sobre">
  <div class="container sobre__grid">
    <figure class="sobre__foto reveal">
      <img src="assets/dra.svg" alt="Dra. Cíntia em seu consultório" loading="lazy" width="800" height="1000">
    </figure>
    <div class="sobre__texto reveal">
      <span class="overline">Sobre</span>
      <h2>Dra. Cíntia <!-- TROCAR: sobrenome --></h2>
      <p class="sobre__cro">CRO-SP 00.000 <!-- TROCAR --> &bull; Especialista em Implantodontia &bull; Credenciada Invisalign<sup>®</sup></p>
      <p>Cada sorriso chega ao consultório com uma história — e um motivo. Há mais de 10 anos <!-- TROCAR: tempo real -->, a Dra. Cíntia une tecnologia de planejamento digital a um atendimento que escuta antes de propor, para que cada tratamento caiba na vida (e no bolso) de quem o recebe.</p>
      <ul class="sobre__stats">
        <li><strong>+500</strong><span>implantes realizados</span></li>
        <li><strong>+300</strong><span>sorrisos alinhados</span></li>
        <li><strong>10+</strong><span>anos de experiência</span></li>
      </ul>
    </div>
  </div>
</section>
```

*(Números dos stats são placeholders — marcar na entrega para a cliente confirmar.)*

- [ ] **Step 3: Adicionar CSS ao final de `css/style.css`**

```css
/* ===== Cards de especialidades ===== */
.cards-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 2rem; }
@media (max-width: 860px) { .cards-2 { grid-template-columns: 1fr; } }
.card {
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: transform .3s ease, box-shadow .3s ease;
}
.card:hover { transform: translateY(-6px); box-shadow: var(--shadow-md); }
.card > img { aspect-ratio: 4 / 3; object-fit: cover; width: 100%; }
.card__body { padding: 2rem; display: grid; gap: 1rem; justify-items: start; }
.card__body h3 { font-size: 1.5rem; }
.card__body p { color: var(--ink-soft); }
.checklist { display: grid; gap: .5rem; }
.checklist li { padding-left: 1.6rem; position: relative; color: var(--ink-soft); }
.checklist li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: var(--gold);
  font-weight: 700;
}

/* ===== Sobre ===== */
.sobre__grid {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: clamp(2rem, 6vw, 5rem);
  align-items: center;
}
@media (max-width: 860px) { .sobre__grid { grid-template-columns: 1fr; } }
.sobre__foto img {
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  aspect-ratio: 4 / 5;
  object-fit: cover;
}
.sobre__texto h2 { font-size: clamp(1.9rem, 4vw, 2.75rem); }
.sobre__cro { margin: .75rem 0 1.25rem; font-size: .92rem; font-weight: 600; color: var(--gold); }
.sobre__texto > p:not(.sobre__cro) { color: var(--ink-soft); max-width: 54ch; }
.sobre__stats { display: flex; flex-wrap: wrap; gap: 2.5rem; margin-top: 2rem; }
.sobre__stats strong { display: block; font-family: var(--font-display); font-size: 2rem; color: var(--teal); }
.sobre__stats span { font-size: .9rem; color: var(--ink-soft); }
```

- [ ] **Step 4: Verificar**

Run: `python tools/check_assets.py` → `OK`.
Navegador: dois cards lado a lado (empilhados <860px), hover com elevação; seção Sobre com foto à esquerda e stats. Sem erros no console.

- [ ] **Step 5: Commit**

```bash
git add index.html css/style.css
git commit -m "feat: add specialties cards and about section"
```

---

### Task 5: Antes e Depois (comparador interativo)

**Files:**
- Modify: `index.html` (seção `#resultados`)
- Modify: `css/style.css` (adicionar ao final)
- Modify: `js/main.js` (adicionar ao final)

**Interfaces:**
- Consumes: `assets/caso{1,2,3}-antes.svg` e `-depois.svg` da Task 2.
- Produces: componente `.compare` (autônomo; nenhuma tarefa posterior depende dele).

- [ ] **Step 1: Preencher `#resultados` no `index.html`**

```html
<section class="section" id="resultados">
  <div class="container">
    <div class="section-head section-head--center reveal">
      <span class="overline">Resultados reais</span>
      <h2>Antes e depois que falam por si</h2>
      <p>Arraste o controle para comparar. Casos tratados pela Dra. Cíntia, com autorização dos pacientes.</p>
    </div>
    <div class="casos-track reveal" tabindex="0" aria-label="Galeria de casos, role horizontalmente">
      <figure class="compare" style="--pos: 50%">
        <img class="compare__before" src="assets/caso1-antes.svg" alt="Caso 1 antes do tratamento" loading="lazy" width="800" height="600">
        <img class="compare__after" src="assets/caso1-depois.svg" alt="Caso 1 depois do tratamento" loading="lazy" width="800" height="600">
        <input class="compare__range" type="range" min="0" max="100" value="50" aria-label="Comparar antes e depois do caso 1">
        <figcaption>Implante unitário</figcaption>
      </figure>
      <figure class="compare" style="--pos: 50%">
        <img class="compare__before" src="assets/caso2-antes.svg" alt="Caso 2 antes do tratamento" loading="lazy" width="800" height="600">
        <img class="compare__after" src="assets/caso2-depois.svg" alt="Caso 2 depois do tratamento" loading="lazy" width="800" height="600">
        <input class="compare__range" type="range" min="0" max="100" value="50" aria-label="Comparar antes e depois do caso 2">
        <figcaption>Invisalign — 14 meses</figcaption>
      </figure>
      <figure class="compare" style="--pos: 50%">
        <img class="compare__before" src="assets/caso3-antes.svg" alt="Caso 3 antes do tratamento" loading="lazy" width="800" height="600">
        <img class="compare__after" src="assets/caso3-depois.svg" alt="Caso 3 depois do tratamento" loading="lazy" width="800" height="600">
        <input class="compare__range" type="range" min="0" max="100" value="50" aria-label="Comparar antes e depois do caso 3">
        <figcaption>Protocolo completo</figcaption>
      </figure>
    </div>
  </div>
</section>
```

- [ ] **Step 2: CSS do comparador (final de `css/style.css`)**

```css
/* ===== Antes e Depois ===== */
.casos-track {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: min(420px, 82vw);
  gap: 1.5rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  padding-bottom: 1rem;
  scrollbar-width: thin;
}
.casos-track > * { scroll-snap-align: center; }
.compare {
  position: relative;
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.compare img { aspect-ratio: 4 / 3; object-fit: cover; width: 100%; }
.compare__after {
  position: absolute;
  inset: 0;
  clip-path: inset(0 0 0 var(--pos));
}
.compare::after { /* linha divisória */
  content: "";
  position: absolute;
  top: 0;
  bottom: 2.6rem;
  left: var(--pos);
  width: 3px;
  background: #fff;
  box-shadow: 0 0 8px rgba(0, 0, 0, .35);
  pointer-events: none;
}
.compare__range {
  position: absolute;
  inset: 0 0 2.6rem 0;
  width: 100%;
  height: auto;
  opacity: 0;      /* invisível, mas arrastável e focável */
  cursor: ew-resize;
}
.compare figcaption {
  padding: .7rem 1rem;
  background: var(--surface);
  font-size: .9rem;
  font-weight: 600;
  color: var(--teal);
}
```

- [ ] **Step 3: JS do comparador (final de `js/main.js`)**

```js
// ===== Comparador antes/depois =====
document.querySelectorAll(".compare").forEach((fig) => {
  const range = fig.querySelector(".compare__range");
  range.addEventListener("input", () =>
    fig.style.setProperty("--pos", range.value + "%")
  );
});
```

- [ ] **Step 4: Verificar**

Navegador: três casos em carrossel horizontal com scroll-snap; arrastar o controle revela a imagem "DEPOIS" da esquerda para a direita com linha divisória branca; funciona por teclado (setas com o range focado). `python tools/check_assets.py` → `OK`.

- [ ] **Step 5: Commit**

```bash
git add index.html css/style.css js/main.js
git commit -m "feat: add before/after comparison gallery"
```

---

### Task 6: Como funciona + Depoimentos + FAQ

**Files:**
- Modify: `index.html` (seções `#como-funciona`, `#depoimentos`, `#faq`)
- Modify: `css/style.css` (adicionar ao final)

**Interfaces:**
- Consumes: `.section--dark`, `.section--sand`, `.card`, `assets/paciente{1,2,3}.svg`.
- Produces: nada consumido depois.

- [ ] **Step 1: Preencher `#como-funciona` no `index.html`**

```html
<section class="section section--dark" id="como-funciona">
  <div class="container">
    <div class="section-head section-head--center reveal">
      <span class="overline">Como funciona</span>
      <h2>Três passos até o seu novo sorriso</h2>
    </div>
    <ol class="passos reveal">
      <li>
        <span class="passos__num">1</span>
        <h3>Avaliação completa</h3>
        <p>Exame clínico, imagens e escaneamento digital para entender seu caso — e ouvir o que você espera do tratamento.</p>
      </li>
      <li>
        <span class="passos__num">2</span>
        <h3>Plano personalizado</h3>
        <p>Você vê a simulação do resultado, as etapas, os prazos e os valores antes de decidir. Sem surpresas.</p>
      </li>
      <li>
        <span class="passos__num">3</span>
        <h3>Tratamento e acompanhamento</h3>
        <p>Execução com tecnologia guiada e revisões periódicas até (e depois de) o sorriso final.</p>
      </li>
    </ol>
  </div>
</section>
```

- [ ] **Step 2: Preencher `#depoimentos` no `index.html`**

```html
<section class="section" id="depoimentos">
  <div class="container">
    <div class="section-head section-head--center reveal">
      <span class="overline">Depoimentos</span>
      <h2>Quem já sorriu, recomenda</h2>
    </div>
    <!-- TROCAR: depoimentos ilustrativos — substituir por depoimentos reais AUTORIZADOS por escrito antes de publicar -->
    <div class="depo-grid">
      <blockquote class="card depo reveal">
        <p>"Passei anos escondendo o sorriso. O implante mudou minha relação com o espelho — e o processo foi muito mais tranquilo do que eu imaginava."</p>
        <footer>
          <img src="assets/paciente1.svg" alt="" width="200" height="200" loading="lazy">
          <div><strong>M. Silva</strong><span>Implante unitário</span></div>
        </footer>
      </blockquote>
      <blockquote class="card depo reveal">
        <p>"Fiz Invisalign trabalhando em reuniões o dia todo. Ninguém percebeu que eu estava em tratamento. Resultado impecável."</p>
        <footer>
          <img src="assets/paciente2.svg" alt="" width="200" height="200" loading="lazy">
          <div><strong>R. Almeida</strong><span>Invisalign</span></div>
        </footer>
      </blockquote>
      <blockquote class="card depo reveal">
        <p>"Da avaliação à prótese final, sempre soube exatamente o que ia acontecer. Atendimento humano de verdade."</p>
        <footer>
          <img src="assets/paciente3.svg" alt="" width="200" height="200" loading="lazy">
          <div><strong>C. Ferreira</strong><span>Protocolo completo</span></div>
        </footer>
      </blockquote>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Preencher `#faq` no `index.html`**

```html
<section class="section section--sand" id="faq">
  <div class="container container--narrow">
    <div class="section-head section-head--center reveal">
      <span class="overline">Dúvidas frequentes</span>
      <h2>O que todo mundo pergunta antes de começar</h2>
    </div>
    <div class="faq-list reveal">
      <details>
        <summary>Colocar implante dói?</summary>
        <p>O procedimento é feito com anestesia local e, na maioria dos casos, o pós-operatório é mais tranquilo que o de uma extração. Com o planejamento digital guiado, a cirurgia é menos invasiva e a recuperação, mais rápida.</p>
      </details>
      <details>
        <summary>Quanto tempo dura o tratamento com Invisalign?</summary>
        <p>Depende do caso: alinhamentos simples podem levar de 6 a 9 meses; casos mais complexos, de 12 a 24 meses. Na avaliação, você vê a simulação digital com a estimativa para o seu sorriso.</p>
      </details>
      <details>
        <summary>Quanto custa? Dá para parcelar?</summary>
        <p>Cada caso tem um plano — e um orçamento — próprio, apresentado com transparência na avaliação. Trabalhamos com parcelamento para o tratamento caber no seu planejamento.</p>
      </details>
      <details>
        <summary>Vocês atendem convênio?</summary>
        <p>Entre em contato pelo WhatsApp e informe seu convênio — a equipe confirma cobertura e condições de reembolso. <!-- TROCAR: política real de convênios --></p>
      </details>
      <details>
        <summary>Existe idade máxima para implantes ou Invisalign?</summary>
        <p>Não. Havendo saúde bucal adequada (avaliada no exame inicial), adultos de qualquer idade podem fazer os dois tratamentos.</p>
      </details>
    </div>
  </div>
</section>
```

- [ ] **Step 4: CSS (final de `css/style.css`)**

```css
/* ===== Passos ===== */
.passos {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2.5rem;
  counter-reset: passo;
}
@media (max-width: 860px) { .passos { grid-template-columns: 1fr; } }
.passos__num {
  display: inline-grid;
  place-items: center;
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  border: 2px solid var(--gold);
  color: #D9B87C;
  font-family: var(--font-display);
  font-size: 1.3rem;
  margin-bottom: 1.1rem;
}
.passos h3 { font-size: 1.3rem; margin-bottom: .5rem; }
.passos p { color: #C4D4D2; font-size: .98rem; }

/* ===== Depoimentos ===== */
.depo-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
@media (max-width: 860px) { .depo-grid { grid-template-columns: 1fr; } }
.depo { padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem; }
.depo p { color: var(--ink-soft); font-size: 1.02rem; flex: 1; }
.depo footer { display: flex; align-items: center; gap: .9rem; }
.depo footer img { width: 3rem; height: 3rem; border-radius: 50%; }
.depo footer strong { display: block; font-size: .95rem; }
.depo footer span { font-size: .85rem; color: var(--gold); }

/* ===== FAQ ===== */
.container--narrow { max-width: 760px; }
.faq-list { display: grid; gap: .9rem; }
.faq-list details {
  background: var(--surface);
  border-radius: 14px;
  padding: 1.1rem 1.4rem;
  box-shadow: var(--shadow-sm);
}
.faq-list summary {
  font-weight: 600;
  cursor: pointer;
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.faq-list summary::-webkit-details-marker { display: none; }
.faq-list summary::after {
  content: "+";
  font-family: var(--font-display);
  font-size: 1.5rem;
  color: var(--gold);
  transition: rotate .25s ease;
}
.faq-list details[open] summary::after { rotate: 45deg; }
.faq-list details p { margin-top: .8rem; color: var(--ink-soft); }
```

- [ ] **Step 5: Verificar**

Navegador: passos em 3 colunas sobre fundo escuro; depoimentos em 3 cards; FAQ abre/fecha com "+" girando. Teclado: `Tab` + `Enter` abrem o FAQ. `python tools/check_assets.py` → `OK`.

- [ ] **Step 6: Commit**

```bash
git add index.html css/style.css
git commit -m "feat: add process steps, testimonials and FAQ sections"
```

---

### Task 7: Contato + Footer + WhatsApp flutuante

**Files:**
- Modify: `index.html` (seção `#contato`, `<footer>`, botão flutuante antes do `<script>`)
- Modify: `css/style.css` (adicionar ao final)

**Interfaces:**
- Consumes: `data-whats` (Task 3).
- Produces: nada consumido depois.

- [ ] **Step 1: Preencher `#contato` no `index.html`**

```html
<section class="section" id="contato">
  <div class="container contato__box reveal">
    <div>
      <span class="overline">Agende sua avaliação</span>
      <h2>Pronta(o) para começar?</h2>
      <p>Chame no WhatsApp e receba um horário para sua avaliação — sem compromisso.</p>
      <a href="#contato" data-whats class="btn btn--whats btn--lg">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.5 14.1c-.2.6-1.2 1.2-1.7 1.2-.4.1-1 .1-1.6-.1a13 13 0 0 1-5.9-5.2c-.6-1-.9-2-.9-2.6 0-.7.4-1.4.8-1.7.3-.3.7-.3 1-.3h.5c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .6l-.5.7c-.2.2-.3.4-.1.7a9 9 0 0 0 3.9 3.5c.3.1.5.1.7-.1l.8-1c.2-.3.4-.3.7-.2l2.2 1c.3.2.5.3.6.4 0 .1 0 .4-.1.6Z"/></svg>
        Chamar no WhatsApp
      </a>
    </div>
    <address class="contato__info">
      <p><strong>Endereço</strong><br>Av. Exemplo, 1234 — Sala 56<br>Bairro, São Paulo — SP <!-- TROCAR --></p>
      <p><strong>Horários</strong><br>Seg a Sex, 9h às 19h<br>Sáb, 9h às 13h <!-- TROCAR --></p>
      <p>
        <a class="contato__link" href="https://maps.google.com/?q=Av.+Exemplo,+1234+Sao+Paulo" target="_blank" rel="noopener">Ver no Google Maps ↗</a><br>
        <a class="contato__link" href="https://instagram.com/dracintia" target="_blank" rel="noopener">@dracintia ↗ <!-- TROCAR --></a>
      </p>
    </address>
  </div>
</section>
```

- [ ] **Step 2: Preencher `<footer>` e botão flutuante no `index.html`**

```html
<footer class="site-footer">
  <div class="container">
    <p>© 2026 Dra. Cíntia — Todos os direitos reservados.</p>
    <p>Responsável técnica: Dra. Cíntia <!-- TROCAR: nome completo --> — CRO-SP 00.000 <!-- TROCAR --></p>
  </div>
</footer>

<a href="#contato" data-whats class="whats-float" aria-label="Conversar no WhatsApp">
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.5 14.1c-.2.6-1.2 1.2-1.7 1.2-.4.1-1 .1-1.6-.1a13 13 0 0 1-5.9-5.2c-.6-1-.9-2-.9-2.6 0-.7.4-1.4.8-1.7.3-.3.7-.3 1-.3h.5c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .6l-.5.7c-.2.2-.3.4-.1.7a9 9 0 0 0 3.9 3.5c.3.1.5.1.7-.1l.8-1c.2-.3.4-.3.7-.2l2.2 1c.3.2.5.3.6.4 0 .1 0 .4-.1.6Z"/></svg>
</a>
```

- [ ] **Step 3: CSS (final de `css/style.css`)**

```css
/* ===== Contato ===== */
.contato__box {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: clamp(2rem, 5vw, 4rem);
  background: var(--teal);
  color: #fff;
  border-radius: calc(var(--radius) * 1.4);
  padding: clamp(2rem, 6vw, 4.5rem);
  box-shadow: var(--shadow-md);
}
@media (max-width: 860px) { .contato__box { grid-template-columns: 1fr; } }
.contato__box h2 { font-size: clamp(1.9rem, 4vw, 2.6rem); }
.contato__box .overline { color: #D9B87C; }
.contato__box > div > p { margin: 1rem 0 2rem; color: rgba(255, 255, 255, .85); max-width: 40ch; }
.btn--lg { padding: 1.1rem 2.3rem; font-size: 1.08rem; }
.contato__info { font-style: normal; display: grid; gap: 1.25rem; align-content: center; }
.contato__info p { color: rgba(255, 255, 255, .85); font-size: .98rem; }
.contato__info strong { color: #fff; }
.contato__link { text-decoration: underline; text-underline-offset: 3px; }
.contato__link:hover { color: #D9B87C; }

/* ===== Footer ===== */
.site-footer { padding-block: 2.5rem; text-align: center; }
.site-footer p { font-size: .85rem; color: var(--ink-soft); }

/* ===== WhatsApp flutuante ===== */
.whats-float {
  position: fixed;
  right: 1.25rem;
  bottom: 1.25rem;
  z-index: 60;
  display: grid;
  place-items: center;
  width: 3.6rem;
  height: 3.6rem;
  border-radius: 50%;
  background: var(--whatsapp);
  color: #fff;
  box-shadow: 0 8px 24px rgba(30, 190, 93, .45);
  transition: transform .2s ease;
}
.whats-float:hover { transform: scale(1.08); }
.whats-float svg { width: 1.8rem; height: 1.8rem; }
```

- [ ] **Step 4: Verificar**

Navegador: bloco de contato em card teal com CTA grande; footer discreto; botão verde flutuante visível em toda a rolagem e clicável. `python tools/check_assets.py` → `OK`.

- [ ] **Step 5: Commit**

```bash
git add index.html css/style.css
git commit -m "feat: add contact section, footer and floating WhatsApp button"
```

---

### Task 8: Animações de entrada (reveal on-scroll)

**Files:**
- Modify: `css/style.css` (adicionar ao final)
- Modify: `js/main.js` (adicionar ao final)

**Interfaces:**
- Consumes: classe `.reveal` já presente nos elementos das tarefas 4–7.
- Produces: nada.

- [ ] **Step 1: CSS (final de `css/style.css`)**

```css
/* ===== Reveal on scroll ===== */
@media (prefers-reduced-motion: no-preference) {
  .reveal {
    opacity: 0;
    translate: 0 28px;
    transition: opacity .7s ease, translate .7s ease;
  }
  .reveal.is-visible { opacity: 1; translate: 0 0; }
}
```

- [ ] **Step 2: JS (final de `js/main.js`)**

```js
// ===== Reveal on scroll =====
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

- [ ] **Step 3: Verificar**

Navegador: seções surgem com fade + subida ao entrar na viewport, uma única vez. Com "reduzir movimento" ativado no SO, tudo aparece sem animação (testar via DevTools → Rendering → Emulate CSS prefers-reduced-motion).

- [ ] **Step 4: Commit**

```bash
git add css/style.css js/main.js
git commit -m "feat: add scroll reveal animations with reduced-motion support"
```

---

### Task 9: Auditoria final (memória, peso, acessibilidade) + polimento

**Files:**
- Modify: possivelmente `css/style.css` (ajustes pontuais achados na auditoria)
- Create: `README.md`

**Interfaces:**
- Consumes: tudo.

- [ ] **Step 1: Auditoria de memória**

No Chrome/Edge: abrir `http://localhost:8000`, rolar a página inteira, abrir `Shift+Esc` (gerenciador de tarefas do navegador) e anotar a memória da aba.
Expected: **bem abaixo de 200MB** (placeholders SVG devem ficar em ~30–80MB).

- [ ] **Step 2: Auditoria de peso e rede**

DevTools → Network → Disable cache → recarregar.
Expected: transferido **≤1MB** (sem o vídeo real); nenhuma request com erro exceto `hero.mp4` (opcional/documentado).

- [ ] **Step 3: Auditoria Lighthouse**

DevTools → Lighthouse → Mobile → rodar Performance + Accessibility + SEO.
Expected: Performance ≥90, Accessibility ≥95, SEO ≥90. Corrigir apontamentos simples (contraste, alt, meta) direto no código; anotar os demais.

- [ ] **Step 4: Passada visual final**

Conferir em 360px, 768px e 1440px de largura: nada estoura horizontalmente, textos legíveis, espaçamentos consistentes. Ajustes pontuais de CSS são esperados aqui — commitá-los junto.

- [ ] **Step 5: Criar `README.md` com instruções de troca de mídia**

```markdown
# Landing Page — Dra. Cíntia

Site estático: `index.html` + `css/style.css` + `js/main.js`. Sem build. Para rodar local: `python -m http.server 8000`.

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
```

- [ ] **Step 6: Verificação final completa**

Run: `python tools/check_assets.py` → `OK`.
Navegador: fluxo completo — carregar, rolar tudo, clicar nos CTAs, arrastar comparadores, abrir FAQ.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: final audit fixes and media swap documentation"
```
