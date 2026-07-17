# Landing Page — Dentista (Implantes e Invisalign)

**Data:** 2026-07-17
**Status:** Aprovado em conversa

## Objetivo

Landing page moderna para uma dentista especializada em **implantes** e **Invisalign**.
Conversão primária: clique no botão de **WhatsApp** ("Agende sua avaliação").

## Restrições

- **Máx. 200MB de RAM no navegador do visitante.** Resolvido por disciplina de mídia,
  não por stack: vídeo curto comprimido (`poster` + `preload="none"`), imagens WebP
  com `srcset` e `loading="lazy"`, sem iframe de Google Maps, sem bibliotecas JS.
- Stack: **HTML + CSS + JavaScript puros.** Zero build, zero dependências.
- Materiais (vídeo/fotos): **placeholders** nos formatos/tamanhos corretos; a cliente
  troca pelos reais depois.

## Estrutura de arquivos

```
index.html
css/style.css
js/main.js
assets/   (imagens e vídeo)
```

## Seções da página (em ordem)

1. **Hero** — vídeo de fundo (mudo, loop, poster) + headline + CTA WhatsApp. Menu fixo.
2. **Especialidades** — 2 cards: Implantes e Invisalign, com imagem, benefícios e CTA secundário.
3. **Sobre a Dra.** — foto, nome, CRO, especializações, parágrafo humanizado.
4. **Antes e Depois** — slider de casos em CSS/JS puro (sem biblioteca).
5. **Como funciona** — 3 passos: Avaliação → Plano → Novo sorriso.
6. **Depoimentos** — 2–3 depoimentos com foto.
7. **FAQ** — 4–6 perguntas com `<details>/<summary>` nativo.
8. **Localização + Footer** — endereço, horários, link Google Maps, Instagram, CTA final.

**Fixo:** botão flutuante de WhatsApp no canto inferior direito durante toda a rolagem.

## Direção de design

Pedido explícito da cliente: **caprichar no design** — visual premium e moderno.

- Estética clean/premium de clínica: muito espaço em branco, tipografia elegante
  (serifada para títulos ou sans moderna, via Google Fonts com `font-display: swap`).
- Paleta: base branca/neutra clara + um tom profundo (teal/azul-petróleo) + acento
  quente sutil (dourado/areia). Definir tokens CSS (custom properties).
- Micro-interações: animações de entrada on-scroll (IntersectionObserver),
  hover states nos cards e botões, tudo em CSS/JS puro.
- Mobile-first e responsivo; acessibilidade básica (contraste, alt, foco visível,
  `prefers-reduced-motion`).

## Fora de escopo

- Backend, formulários, CMS, blog, múltiplas páginas.
- Agendamento online integrado (WhatsApp cobre).
