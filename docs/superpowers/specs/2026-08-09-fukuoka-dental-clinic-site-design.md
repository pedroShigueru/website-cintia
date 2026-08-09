# Fukuoka Dental Clinic — Design do site

Data: 2026-08-09
Status: aprovado para planejamento

## 1. Objetivo

Reconstruir o site atual (landing page única "Dra. Cíntia") como o site institucional da **Fukuoka Dental Clinic**, seguindo o briefing entregue pela Dra. Cíntia.

O site deve transmitir confiança, sofisticação, autoridade científica e acolhimento, e deve ser construído **priorizando SEO e conversão**, não apenas estética — exigência explícita do briefing.

### Público-alvo

Adultos e famílias; pacientes de médio e alto padrão; executivos; comunidade japonesa; pessoas buscando tratamentos estéticos e reabilitação oral.

### Termos de busca alvo

- `dentista na Paulista`
- `Invisalign na Paulista`
- `implante dentário na Paulista`
- `clareamento dental`
- `dentista para japoneses em São Paulo`

## 2. Decisões tomadas no brainstorming

| Questão | Decisão |
|---|---|
| Arquitetura | Híbrido: Home longa e completa + páginas internas de aprofundamento com URL própria |
| Tratamentos | Hub `/tratamentos.html` + uma página por tratamento |
| Idiomas | Estrutura i18n pronta (PT/EN, extensível a JA); apenas PT com conteúdo completo nesta entrega |
| Fotos | Manter stock atual como placeholder + marcadores `TROCAR` e checklist no README |
| Blog | Estrutura completa + 3 posts de exemplo otimizados |
| Conteúdo médico | Escrito por Claude, conservador, marcado para revisão da Dra. antes de publicar |
| Dados da clínica | Não disponíveis; usar marcadores `TROCAR` |

### Pendência para a Dra.

O briefing traz `"Preparar estrutura para Português,  e English"` — com espaço duplo e vírgula órfã, sugerindo um terceiro idioma removido. Dado que o público-alvo inclui a comunidade japonesa e uma das keywords é "dentista para japoneses em São Paulo", a hipótese é **日本語**. A estrutura de i18n será desenhada para 3 idiomas; confirmar antes de traduzir.

## 3. Arquitetura de build

O site é estático, sem framework. Com ~20 páginas, header/menu/rodapé repetidos seriam uma armadilha de manutenção. Solução: **gerador estático em Python puro (stdlib, zero dependências)**.

```
src/
  partials/
    head.html          <head> comum, com slots de title/description/canonical
    header.html        logo + menu + seletor de idioma
    cta-bar.html       Agendar · WhatsApp · Localização
    footer.html
  layouts/
    base.html          esqueleto que compõe os partials
    treatment.html     layout das páginas de tratamento
    post.html          layout dos posts do blog
  pages/               miolo de cada página + front-matter de metadados
  content/
    filosofia.md       texto integral da Dra.
    missao.md
    valores.md
  data/
    site.json          dados globais: nome, endereço, telefone, horários, IDs de analytics
    nav.json           estrutura do menu
tools/
  build.py             gera os HTML estáticos
  check_assets.py      (existente) valida referências de assets
```

### Contrato do build

- Entrada: `src/`. Saída: HTML estático na raiz do repositório.
- Sem dependências externas: front-matter e templating implementados com `re` e `string.Template` da stdlib. Sem Jinja2 e sem PyYAML — os dados globais são **JSON**, lidos pelo módulo `json` da stdlib. O front-matter das páginas usa `chave: valor` simples, um por linha, delimitado por `---`.
- Idempotente: rodar duas vezes produz saída idêntica.
- `python tools/build.py --check` falha (exit 1) se a saída estiver dessincronizada de `src/`, para uso em CI.
- Os HTML gerados **são commitados**, para deploy em qualquer host estático sem etapa de build.

### Unidades e responsabilidades

| Unidade | Faz | Depende de |
|---|---|---|
| `build.py::load_page` | Lê um arquivo de `pages/`, separa front-matter do corpo | stdlib |
| `build.py::render` | Substitui slots do layout pelos partials e pelo corpo | `load_page` |
| `build.py::write_sitemap` | Gera `sitemap.xml` a partir da lista de páginas | lista de páginas |
| `build.py::main` | Orquestra, escreve saída, reporta o que mudou | as acima |

Cada função é testável isoladamente com strings em memória, sem tocar o disco.

## 4. Mapa de URLs

| URL | H1 | Termo alvo |
|---|---|---|
| `/` | Fukuoka Dental Clinic — odontologia de excelência na Av. Paulista | dentista na Paulista |
| `/sobre.html` | Sobre a Dra. Cíntia e a Fukuoka Dental Clinic | — |
| `/tratamentos.html` | Tratamentos | — |
| `/tratamentos/invisalign.html` | Invisalign na Paulista | Invisalign na Paulista |
| `/tratamentos/implantes.html` | Implante dentário na Paulista | implante dentário na Paulista |
| `/tratamentos/clareamento.html` | Clareamento dental | clareamento dental |
| `/tratamentos/reabilitacao-oral.html` | Reabilitação oral | — |
| `/tratamentos/estetica.html` | Estética: lentes e facetas | — |
| `/atendimento-em-japones.html` | Dentista para japoneses em São Paulo / 日本語対応 | dentista para japoneses em São Paulo |
| `/filosofia.html` | Nossa Filosofia | — |
| `/valores.html` | Nossos Valores | — |
| `/depoimentos.html` | Depoimentos | — |
| `/blog/index.html` | Blog | — |
| `/blog/invisalign-como-funciona.html` | Invisalign: como funciona o tratamento | cauda longa |
| `/blog/implante-dentario-passo-a-passo.html` | Implante dentário: o passo a passo | cauda longa |
| `/blog/clareamento-dental-seguro.html` | Clareamento dental seguro | cauda longa |
| `/contato.html` | Contato e localização | — |
| `/en/…` | espelho estrutural | — |

A **Missão** não ganha página própria: é curta e institucional demais para sustentar uma URL. Aparece em destaque na Home e no topo de `/sobre.html`.

`/atendimento-em-japones.html` não estava na lista de páginas do briefing, mas o briefing pede explicitamente otimização para "dentista para japoneses em São Paulo" e lista a comunidade japonesa como público-alvo. Sem uma página dedicada, não há onde esse termo ranquear.

## 5. Estrutura da Home

Home longa, com scroll contínuo, cobrindo todas as seções em resumo. Quem quiser conhecer a clínica inteira consegue sem clicar em nada; cada seção oferece um link de aprofundamento.

1. **Hero** — imagem estática, headline, CTA duplo
2. **Missão** — texto integral (é curto)
3. **Tratamentos** — 5 cards → páginas dedicadas
4. **Sobre** — resumo da Dra. + clínica → `/sobre.html`
5. **Filosofia** — 2 parágrafos de abertura do manifesto → `/filosofia.html`
6. **Valores** — os 5 valores, título + uma linha cada → `/valores.html`
7. **Depoimentos** — 3 destaques → `/depoimentos.html`
8. **Atendimento em japonês** — faixa curta → página dedicada
9. **Blog** — 3 posts recentes → `/blog/`
10. **Contato** — mapa, endereço, horários, CTAs

## 6. Design tokens

```css
--navy:       #0F2D52;   /* institucional: headings, seções escuras */
--navy-deep:  #0A1F3A;   /* fundos escuros, derivado */
--gold:       #B08D57;   /* SÓ decoração: filetes, ícones, molduras */
--gold-text:  #8A6A3B;   /* dourado em texto sobre fundo claro */
--gold-light: #C9A96E;   /* dourado em texto sobre navy */
--offwhite:   #F8F7F3;   /* fundo padrão */
--gray:       #D9D9D6;   /* divisores, superfícies */
--ink:        #1A1A1A;   /* corpo de texto */
--ink-soft:   #4A5568;   /* texto secundário */
```

### Correção de contraste (obrigatória)

O dourado do briefing, `#B08D57`, sobre o off-white `#F8F7F3`, mede **2,88:1** — reprova o WCAG AA, que exige 4,5:1 para texto normal. Sobre o navy `#0F2D52` mede **4,48:1**, também reprovando por margem estreita.

Consequência: `#B08D57` **nunca é usado em texto**. Fica restrito a filetes, bordas, ícones decorativos e molduras. Para texto dourado existem `--gold-text` (fundo claro) e `--gold-light` (fundo navy).

Isso está alinhado ao briefing, que já determina "tons dourados usados apenas como detalhes elegantes, evitando excesso".

Todos os pares de cor em texto devem ser verificados ≥ 4,5:1 (normal) ou ≥ 3:1 (large, ≥ 24px ou ≥ 19px bold) antes da entrega.

### Linguagem visual

Estética japonesa minimalista, traduzida em decisões concretas:

- **Espaço em branco muito mais generoso** que o site atual: `--space-section: clamp(6rem, 14vw, 12rem)`
- **Cantos quase retos**: `--radius: 2px` (hoje: 20px)
- **Filetes de 1px em dourado** no lugar de sombras pesadas; sombras apenas sutis, se houver
- **Grid assimétrico** nas seções de conteúdo, evitando o centralizado simétrico
- **Tipografia**: **Cormorant Garamond** nos títulos e **Inter** no corpo. Fraunces, usada hoje, tem contraste alto e eixo óptico expressivo demais para a sobriedade pretendida; Cormorant é mais fina, clássica e silenciosa. Ambas via Google Fonts, com `preconnect` e `display=swap`
- **Motion contido**: fades e deslocamentos curtos; nada de bounce ou parallax exagerado

## 7. Performance

O briefing exige excelente PageSpeed e otimização mobile.

- **O vídeo do hero é removido.** Um MP4 no hero é o pior inimigo do LCP em mobile. Substituído por imagem estática com animação de entrada sutil. Se a Dra. exigir o vídeo, ele retorna como seção secundária abaixo da dobra, com `preload="none"`.
- Imagens em WebP, com `width`/`height` explícitos para evitar CLS, `loading="lazy"` fora da dobra e `fetchpriority="high"` na imagem do hero.
- CSS único e inline-crítico se necessário; JS mínimo e `defer`.
- Fontes com `preconnect` e `display=swap`.
- **Metas**: Lighthouse mobile ≥ 90 em Performance, ≥ 95 em Acessibilidade, SEO e Best Practices.

## 8. Conversão

Três botões sempre visíveis, conforme o briefing: **Agendar consulta**, **WhatsApp**, **Localização**.

- Desktop: no header, fixo no topo.
- Mobile: barra fixa inferior com os três.
- A bolinha flutuante de WhatsApp atual é removida, substituída por essa barra.
- O número do WhatsApp permanece definido em um único lugar (`data/site.json`, injetado no build), preservando o padrão atual de fonte única.

## 9. SEO técnico

Por página:

- `<title>` e meta description únicos
- H1 único, hierarquia H2/H3 correta
- `<link rel="canonical">`
- `hreflang` para PT/EN (e JA quando confirmado), com `x-default`
- Open Graph e Twitter Card
- URLs amigáveis, sem query strings
- `alt` descritivo em todas as imagens de conteúdo; `alt=""` nas decorativas

Globais:

- `JSON-LD` de `Dentist` / `LocalBusiness` na Home: nome, endereço, geo, horários, telefone, `priceRange`, `sameAs`
- `JSON-LD` de `FAQPage` nas páginas de tratamento (gera rich snippets)
- `JSON-LD` de `Article` nos posts do blog
- `sitemap.xml` gerado pelo build
- `robots.txt`
- Snippets de GA4, Search Console e Meta Pixel comentados, com `TROCAR` no lugar do ID

## 10. Internacionalização

- `/` = PT-BR (idioma padrão). `/en/` = espelho estrutural.
- `<html lang>` correto por página.
- `hreflang` recíproco entre as versões, mais `x-default` apontando para PT.
- Seletor de idioma no header.
- Nesta entrega, apenas PT tem conteúdo completo. As páginas EN são geradas com a estrutura e os metadados, e conteúdo marcado para tradução — **nunca** com texto institucional traduzido por máquina sem revisão.
- Textos ficam em `src/content/<lang>/`, para que adicionar JA não exija mudança no build.

## 11. Acessibilidade

- WCAG 2.1 AA como piso.
- Foco visível em todos os interativos, com cor legível sobre fundo claro e sobre navy.
- Navegação completa por teclado; skip link para o conteúdo principal.
- `prefers-reduced-motion` respeitado em todas as animações.
- Landmarks semânticos e `aria-label` nas regiões de navegação.

## 12. Conteúdo

- **Filosofia, Missão e Valores**: usar o texto da Dra. na íntegra, sem reescrever. Ficam em `src/content/` como fonte única.
- **Páginas de tratamento**: texto técnico conservador, escrito por Claude. Sem promessa de resultado, sem superlativo comparativo, sem "melhor da cidade" — vedado pelo Código de Ética Odontológica (CFO). Cada página traz um marcador visível pedindo validação da Dra. antes de publicar.
- **Posts do blog**: 3 exemplos otimizados para cauda longa, mesmas restrições.
- **Depoimentos**: os atuais são ilustrativos. Mantidos com marcador reforçado — depoimento real exige autorização por escrito (CFO e LGPD).
- **Tom**: elegante, humano, claro, baseado em credibilidade científica.

## 13. Assets

Os arquivos em `assets/` são stock do Pexels e permanecem como placeholder visual. O briefing pede fotos reais da clínica, da Dra., da equipe, dos equipamentos e do ambiente.

O README ganha uma tabela atualizada de substituição, cobrindo os novos assets, e a checklist de publicação é revisada. `tools/check_assets.py` continua validando as referências.

## 14. Reaproveitamento do site atual

Preservados e reestilizados para a nova identidade:

- Comparador antes/depois (`.compare` + o handler de `input`)
- Reveal on scroll via `IntersectionObserver`, com o fallback no-JS existente
- FAQ em `<details>`, que já é acessível por padrão
- Padrão de WhatsApp com fonte única de número

Removidos: hero em vídeo, tilt 3D nas imagens (destoa da sobriedade pretendida), bolinha flutuante de WhatsApp.

Reescritos: toda a paleta, tipografia, espaçamentos e a marca.

## 15. Fora de escopo

- Tradução do conteúdo para EN ou JA
- CMS ou área administrativa
- Formulário de contato com backend (o CTA é WhatsApp; se houver formulário, é `mailto:` ou serviço externo)
- Integração com sistema de agendamento
- Fotos reais e depoimentos reais
- Dados reais da clínica (endereço, CRO, telefone, horários)

## 16. Critérios de aceite

1. `python tools/build.py` gera todas as páginas do mapa de URLs sem erro.
2. `python tools/build.py --check` sai com 0 quando a saída está sincronizada.
3. `python tools/check_assets.py` passa.
4. Toda página tem `<title>`, meta description, H1 único e canonical.
5. Nenhum par de cor em texto abaixo do mínimo AA.
6. Lighthouse mobile na Home: Performance ≥ 90, Acessibilidade ≥ 95, SEO ≥ 95, Best Practices ≥ 95.
7. Os três CTAs estão visíveis em qualquer ponto da página, no desktop e no mobile.
8. `sitemap.xml` e `robots.txt` presentes e coerentes.
9. Nenhum dado inventado publicado como real: tudo o que falta está marcado com `TROCAR`.
10. Navegação por teclado completa, com foco visível em fundo claro e escuro.
