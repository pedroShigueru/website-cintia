// O numero de WhatsApp vem de src/data/site.json e ja chega no HTML,
// para funcionar sem JS e ser indexavel.

// ===== Header: sombra ao rolar =====
const header = document.querySelector(".site-header");
if (header) {
  const onScroll = () => header.classList.toggle("is-scrolled", scrollY > 24);
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();
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
