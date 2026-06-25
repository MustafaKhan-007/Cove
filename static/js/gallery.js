// COVE Website Rebuild — static/js/gallery.js — minimal lightbox for the photo grid
(function () {
  "use strict";

  const items = Array.from(document.querySelectorAll(".gallery__item"));
  if (!items.length) return;

  const lightbox = document.getElementById("lightbox");
  if (!lightbox) return;
  const imgEl = lightbox.querySelector(".lightbox__img");
  let current = 0;

  const sources = items.map((it) => {
    const img = it.querySelector("img");
    return img ? (img.dataset.full || img.src) : "";
  });

  function open(index) {
    current = index;
    imgEl.src = sources[current];
    lightbox.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }
  function close() {
    lightbox.classList.remove("is-open");
    document.body.style.overflow = "";
  }
  function show(delta) {
    current = (current + delta + sources.length) % sources.length;
    imgEl.src = sources[current];
  }

  items.forEach((it, i) => it.addEventListener("click", () => open(i)));
  lightbox.querySelector(".lightbox__close").addEventListener("click", close);
  lightbox.querySelector(".lightbox__nav--prev").addEventListener("click", () => show(-1));
  lightbox.querySelector(".lightbox__nav--next").addEventListener("click", () => show(1));
  lightbox.addEventListener("click", (e) => { if (e.target === lightbox) close(); });
  document.addEventListener("keydown", (e) => {
    if (!lightbox.classList.contains("is-open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(-1);
    if (e.key === "ArrowRight") show(1);
  });
})();
