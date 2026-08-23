// O numero de WhatsApp vem de src/data/site.json e ja chega no HTML,
// para funcionar sem JS e ser indexavel.

// ===== Header: sombra ao rolar =====
const header = document.querySelector(".site-header");
if (header) {
  const onScroll = () => header.classList.toggle("is-scrolled", scrollY > 24);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

// ===== Menu lateral (abaixo de 1080px) =====
// O site-nav vira uma gaveta: sem o botao os links do menu ficam
// inalcancaveis no celular.
const menu = document.getElementById("menu-lateral");
const abridor = document.querySelector(".nav-toggle");
if (menu && abridor) {
  const raiz = document.documentElement;
  const fechador = menu.querySelector(".menu-lateral__fechar");
  const overlay = document.querySelector(".menu-overlay");
  const desktop = matchMedia("(min-width: 1080px)");
  const aberto = () => raiz.classList.contains("menu-aberto");

  const definir = (abrir) => {
    if (abrir === aberto()) return;
    raiz.classList.toggle("menu-aberto", abrir);
    abridor.setAttribute("aria-expanded", String(abrir));
    (abrir ? fechador : abridor)?.focus();
  };

  abridor.addEventListener("click", () => definir(!aberto()));
  fechador?.addEventListener("click", () => definir(false));
  overlay?.addEventListener("click", () => definir(false));
  // Ancoras da mesma pagina nao recarregam nada: fechar na mao.
  menu.addEventListener("click", (e) => {
    if (e.target.closest("a")) definir(false);
  });

  addEventListener("keydown", (e) => {
    if (!aberto()) return;
    if (e.key === "Escape") return definir(false);
    if (e.key !== "Tab") return;
    // Prende o foco na gaveta: atras dela a pagina continua tabulavel.
    const itens = [...menu.querySelectorAll("a[href], button:not([disabled])")];
    if (!itens.length) return;
    const [primeiro] = itens;
    const ultimo = itens[itens.length - 1];
    const saindo = e.shiftKey ? primeiro : ultimo;
    if (document.activeElement === saindo || !menu.contains(document.activeElement)) {
      e.preventDefault();
      (e.shiftKey ? ultimo : primeiro).focus();
    }
  });

  // Ao girar para o desktop a gaveta some; fechar evita travar a rolagem.
  desktop.addEventListener("change", (e) => {
    if (e.matches) definir(false);
  });
}

// ===== Comparador antes/depois =====
document.querySelectorAll(".compare").forEach((fig) => {
  const range = fig.querySelector(".compare__range");
  if (range) {
    range.addEventListener("input", () =>
      fig.style.setProperty("--pos", range.value + "%")
    );
  }
});

// ===== Reveal on scroll =====
document.documentElement.classList.add("js"); // sem JS, .reveal fica visivel
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
