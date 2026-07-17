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

// ===== Tilt 3D nas imagens das especialidades =====
if (
  matchMedia("(hover: hover) and (pointer: fine)").matches &&
  !matchMedia("(prefers-reduced-motion: reduce)").matches
) {
  document.querySelectorAll(".cards-2 .card > img").forEach((img) => {
    img.addEventListener("pointermove", (e) => {
      const r = img.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;  // -0.5 … 0.5
      const y = (e.clientY - r.top) / r.height - 0.5;
      img.style.setProperty("--ry", (x * 10).toFixed(2) + "deg");
      img.style.setProperty("--rx", (-y * 8).toFixed(2) + "deg");
    });
    img.addEventListener("pointerleave", () => {
      img.style.setProperty("--ry", "0deg");
      img.style.setProperty("--rx", "0deg");
    });
  });
}

// ===== Comparador antes/depois =====
document.querySelectorAll(".compare").forEach((fig) => {
  const range = fig.querySelector(".compare__range");
  range.addEventListener("input", () =>
    fig.style.setProperty("--pos", range.value + "%")
  );
});

// ===== Reveal on scroll =====
document.documentElement.classList.add("js"); // sem JS, .reveal fica visível
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
