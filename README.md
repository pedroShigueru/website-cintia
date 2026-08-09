# Fukuoka Dental Clinic — site

Site estático gerado por um script Python de stdlib pura. Sem npm, sem framework, sem dependência de runtime.

## Rodar localmente

```bash
py tools/build.py        # gera os HTML a partir de src/
py -m http.server 8000   # serve em http://localhost:8000
```

## Como o site é montado

Os HTML da raiz (`index.html`, `sobre.html`, `tratamentos/`, `blog/`, `en/`) são **gerados**. Nunca editar à mão — a próxima execução do build sobrescreve.

Editar sempre em `src/`:

| Pasta | O que fica lá |
|---|---|
| `src/data/site.json` | Endereço, telefone, WhatsApp, horários, IDs de analytics |
| `src/data/nav.json` | Estrutura documental do menu |
| `src/partials/` | Header, footer, barra de CTAs, `<head>` |
| `src/layouts/` | Esqueletos: `base`, `treatment`, `post` |
| `src/pages/` | Miolo de cada página, com front-matter |
| `src/content/pt/` | Filosofia, missão e valores — texto da Dra., fonte única |

Depois de editar, rodar `py tools/build.py` e commitar tanto `src/` quanto os HTML gerados.

### Front-matter de uma página

```
---
title: Invisalign na Paulista | Fukuoka Dental Clinic
description: Até 160 caracteres, único no site.
og_type: article
layout: treatment          # opcional: base (padrão), treatment ou post
alternate_en: en/...html   # opcional: contraparte em inglês
noindex: true              # opcional: exclui do sitemap e emite meta robots
jsonld: <script ...>       # opcional: dados estruturados
---
```

O build injeta `{{ prefixo }}` com o caminho relativo até a raiz (`""` na raiz, `"../"` em subpasta). Usar em todo link e asset interno de páginas que ficam em subpastas.

## Testes

```bash
py -m pytest                        # tudo
py -m pytest tests/test_contrast.py # só a paleta
py tools/build.py --check           # falha se os HTML estiverem dessincronizados de src/
py tools/check_assets.py            # falha se houver referência local quebrada
```

A suíte verifica, em toda página gerada: título e meta description únicos e no tamanho certo, H1 único, hierarquia de headings, canonical, Open Graph, `alt` e dimensões em imagens, JSON-LD válido, links internos não quebrados, hreflang recíproco, contraste da paleta contra o WCAG AA e ausência de expressões vedadas pelo Código de Ética Odontológica.

Um teste está marcado como `xfail` de propósito: `test_json_ld_nao_contem_dado_pendente`. Ele falha enquanto o schema `Dentist` tiver `TROCAR` no endereço e nas coordenadas. Ao preencher os dados reais, **remover o marcador `xfail`** — o teste passa a bloquear regressões.

## Paleta e a regra do dourado

`--gold` (`#B08D57`) é **decoração apenas**: bordas, filetes, ícones. Sobre o off-white ele mede 2,88:1 de contraste e reprova o WCAG AA. Para texto dourado existem `--gold-text` (fundo claro, 4,66:1) e `--gold-light` (fundo navy, 6,18:1). O teste `test_dourado_bruto_nunca_e_usado_em_texto` bloqueia o uso indevido.

## Substituir os placeholders

### Fotos

Os arquivos em `assets/` são **stock do Pexels**, presentes só para o site não ficar com quadrados vazios. O briefing pede fotos reais da clínica, da Dra., da equipe, dos equipamentos e do ambiente.

| Placeholder | Trocar por | Formato |
|---|---|---|
| `assets/hero.jpg` | ambiente da clínica, foto ampla | WebP 1600×1000 |
| `assets/clinica.jpg` | recepção ou sala de atendimento | WebP 800×1000 |
| `assets/dra.jpg` | foto profissional da Dra. Cíntia | WebP 800×1000 |
| `assets/invisalign.jpg` | tratamento com alinhadores | WebP 800×600 |
| `assets/implantes.jpg` | implante ou planejamento | WebP 800×600 |
| `assets/clareamento.jpg` | clareamento | WebP 800×600 |
| `assets/reabilitacao.jpg` | reabilitação oral | WebP 800×600 |
| `assets/estetica.jpg` | lentes e facetas | WebP 800×600 |
| `assets/casoN-antes/depois.jpg` | casos reais **autorizados** | WebP 800×600, mesmo enquadramento no par |
| `assets/mapa.jpg` | captura do mapa da localização | WebP 1600×700 |

`assets/hero.mp4` e `assets/hero-poster.jpg` sobraram da versão anterior e podem ser removidos.

Ao trocar as extensões, atualizar os `src` em `src/pages/` e rodar `py tools/check_assets.py`.

### Dados

Buscar `TROCAR` em `src/` e substituir tudo. Os principais estão em `src/data/site.json`: endereço, CEP, telefone, WhatsApp, coordenadas, Instagram, e-mail, nome completo da Dra., CRO, ID do GA4.

## Checklist antes de publicar

- [ ] Todos os `TROCAR` de `src/data/site.json` preenchidos
- [ ] Todos os `TROCAR` de `src/pages/` resolvidos (formação da Dra., horários, atendimento em japonês)
- [ ] Fotos reais no lugar do stock do Pexels
- [ ] Depoimentos reais com autorização **por escrito** (CFO e LGPD) — e o aviso de "ilustrativos" removido de `src/pages/depoimentos.html`
- [ ] Casos antes/depois reais e autorizados — e o aviso removido
- [ ] Textos das páginas de tratamento e dos posts **validados pela Dra.** (buscar `Validar com a Dra.`)
- [ ] Coordenadas e endereço reais no JSON-LD; remover o `xfail` de `test_json_ld_nao_contem_dado_pendente`
- [ ] ID do GA4 preenchido e o bloco descomentado em `src/partials/head.html`
- [ ] Search Console verificado e `sitemap.xml` submetido
- [ ] Após traduzir as páginas EN: remover `noindex: true` do front-matter delas
- [ ] Lighthouse mobile na Home: Performance ≥ 90, Acessibilidade ≥ 95, SEO ≥ 95

## Decisões registradas

- **Sem vídeo no hero.** MP4 no topo penaliza o LCP em mobile. Hero é imagem estática com `fetchpriority="high"`.
- **Sem verde WhatsApp nos botões.** Branco sobre `#1EBE5D` mede 2,45:1 e reprova AA, além de destoar da paleta. Os CTAs usam navy, mantendo o ícone do WhatsApp.
- **Noto Sans JP no corpo do texto.** O site tem conteúdo em japonês de verdade; uma fonte só-latina o jogaria para a fonte de sistema, fora do design.
- **Mapa como imagem estática**, não iframe, por desempenho. O iframe fica comentado em `src/pages/contato.html`.
- **Páginas EN com `noindex`** até serem traduzidas, para não criar conteúdo raso indexado.
- **`/atendimento-em-japones.html` não estava na lista de páginas do briefing**, mas foi criada porque o briefing pede otimização para "dentista para japoneses em São Paulo" e sem página dedicada esse termo não tem onde ranquear.
