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
| `src/layouts/` | Esqueletos: `base`, `treatment`, `post` e as variantes `treatment-en`, `post-en` |
| `src/pages/` | Miolo de cada página, com front-matter |
| `src/content/pt/` | Filosofia, missão e valores — texto da Dra., fonte única |
| `src/content/en/` | Os mesmos textos em inglês |

Um partial com sufixo `-en` (`header-en.html`) tem precedência sobre o padrão
em páginas com `lang: en`; sem contraparte, o build cai no partial em português.
Layouts não têm essa regra — a página em inglês declara `layout: post-en`
explicitamente. Os blocos de avaliação são montados em Python, então os rótulos
em cada idioma ficam em `ROTULOS_AVALIACOES`, dentro de `tools/build.py`; as
páginas EN usam `{{ avaliacoes_faixa_en }}`, `{{ avaliacoes_todas_en }}` e
`{{ avaliacoes_selo_en }}`.

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

## Avaliações do Google

As avaliações vêm do Perfil da Empresa no Google e são buscadas **no build**, não no navegador. Isso mantém a chave de API fora do HTML, evita custo por visita e não adiciona JavaScript de terceiro à página.

```bash
$env:GOOGLE_MAPS_API_KEY="sua-chave"   # PowerShell
py tools/fetch_reviews.py              # grava src/data/avaliacoes.json
py tools/build.py                      # gera o HTML com as avaliações
```

**Pré-requisito**, uma vez só: uma chave de API no [Google Cloud Console](https://console.cloud.google.com/) com a **Places API (New)** habilitada. Restrinja a chave por API e por IP no console — o uso é cobrado na conta da clínica.

O `place_id` o script resolve sozinho a partir de `nome_no_maps` (hoje `Fukuoka Dental Clinic – Paulista`) e grava no JSON, então não é preciso procurá-lo à mão. Se o nome mudar no Maps, o `place_id` já gravado continua valendo — ele é estável.

**Onde aparecem**, a partir de três chaves geradas pelo build:

| Chave | Onde | O que mostra |
|---|---|---|
| `{{ avaliacoes_faixa }}` | Home | Nota, estrelas, total, 3 avaliações e o botão do Google |
| `{{ avaliacoes_todas }}` | `/depoimentos.html` | Todas as avaliações e o botão |
| `{{ avaliacoes_selo }}` | Junto aos CTAs | Linha compacta com nota e total, linkando o perfil |

Sem avaliações no JSON, as três saem vazias — uma clínica sem avaliações não pode exibir "nota 0" nem seção vazia. O teste `test_paginas_de_prova_social_nao_ficam_vazias` sinaliza esse estado; remova o `xfail` quando a integração estiver ativa.

**Limites da API, para não haver surpresa:** ela devolve no máximo 5 avaliações e não permite escolher quais. Para "atualização automática", agende o par `fetch_reviews.py` + `build.py` (tarefa agendada do Windows, cron ou GitHub Action). Diário é mais que suficiente.

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

## Publicar no GitHub Pages

Prévia para a Dra. revisar, servida em `https://pedroshigueru.github.io/website-cintia/`.
No GitHub: **Settings → Pages → Source: Deploy from a branch → `master` / `(root)`**.

Como é um Pages *de projeto*, o site fica sob o subcaminho `/website-cintia/` em vez
da raiz do domínio. Quase tudo funciona sem ajuste, porque o build gera links
relativos — a exceção é a 404, que precisa de caminho absoluto (é servida sob
qualquer URL inexistente, em qualquer profundidade). Daí `base_path` em
`src/data/site.json`:

| Onde o site está | `base_path` |
|---|---|
| GitHub Pages de projeto | `/website-cintia/` |
| Domínio próprio (raiz) | `/` |

**Ao migrar para `fukuokadentalclinic.com.br`, voltar `base_path` para `/` e rodar o
build de novo.** `.nojekyll` na raiz desliga o processamento Jekyll do Pages.

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
- [ ] Textos clínicos em inglês validados pela Dra. junto com a versão em português — e então remover `noindex: true` do front-matter das páginas EN
- [ ] Política de privacidade em inglês revisada pelo advogado junto com a versão em português
- [ ] `base_path` de volta para `/` ao sair do GitHub Pages para o domínio próprio
- [ ] Lighthouse mobile na Home: Performance ≥ 90, Acessibilidade ≥ 95, SEO ≥ 95

## Decisões registradas

- **Sem vídeo no hero.** MP4 no topo penaliza o LCP em mobile. Hero é imagem estática com `fetchpriority="high"`.
- **Sem verde WhatsApp nos botões.** Branco sobre `#1EBE5D` mede 2,45:1 e reprova AA, além de destoar da paleta. Os CTAs usam navy, mantendo o ícone do WhatsApp.
- **Noto Sans JP no corpo do texto.** O site tem conteúdo em japonês de verdade; uma fonte só-latina o jogaria para a fonte de sistema, fora do design.
- **Mapa como imagem estática**, não iframe, por desempenho. O iframe fica comentado em `src/pages/contato.html`.
- **Páginas EN com `noindex`.** A tradução já cobre o site inteiro, mas o texto clínico ainda não passou pela validação da Dra.; indexar antes disso publica informação médica não revisada em outro idioma.
- **Avaliações não são traduzidas.** São citações reais do Perfil no Google. Nas páginas EN elas aparecem no original, marcadas com `lang="pt-BR"` e acompanhadas de uma nota; reescrever a fala de um paciente em outro idioma e apresentá-la entre aspas seria falsear a citação.
- **`/atendimento-em-japones.html` não estava na lista de páginas do briefing**, mas foi criada porque o briefing pede otimização para "dentista para japoneses em São Paulo" e sem página dedicada esse termo não tem onde ranquear.
