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
