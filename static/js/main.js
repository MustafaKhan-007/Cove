// COVE Website Rebuild — static/js/main.js — nav, scroll reveal, smooth scroll, misc
(function () {
  "use strict";

  // 1. Scroll reveal -------------------------------------------------
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }
  );
  document.querySelectorAll(".animate-on-scroll").forEach((el) => observer.observe(el));

  // 2. Nav scroll behaviour -----------------------------------------
  let lastScroll = 0;
  const nav = document.getElementById("nav");
  if (nav) {
    window.addEventListener("scroll", () => {
      const current = window.scrollY;
      if (current > 80) nav.classList.add("nav--scrolled");
      else nav.classList.remove("nav--scrolled");
      if (current > lastScroll && current > 200 && !nav.classList.contains("is-open")) {
        nav.classList.add("nav--hidden");
      } else {
        nav.classList.remove("nav--hidden");
      }
      lastScroll = current;
    }, { passive: true });
  }

  // 3. Hamburger / overlay menu -------------------------------------
  const menuToggle = document.getElementById("menuToggle");
  if (menuToggle && nav) {
    menuToggle.addEventListener("click", () => {
      nav.classList.toggle("is-open");
      document.body.style.overflow = nav.classList.contains("is-open") ? "hidden" : "";
    });
    nav.querySelectorAll(".nav__overlay a").forEach((link) => {
      link.addEventListener("click", () => {
        nav.classList.remove("is-open");
        document.body.style.overflow = "";
      });
    });
  }
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nav && nav.classList.contains("is-open")) {
      nav.classList.remove("is-open");
      document.body.style.overflow = "";
    }
  });

  // 4. Smooth scroll for in-page anchors ----------------------------
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (id.length > 1) {
        const target = document.querySelector(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    });
  });

  // 5. "View all" gallery toggle ------------------------------------
  const galleryMore = document.getElementById("galleryMore");
  if (galleryMore) {
    galleryMore.addEventListener("click", () => {
      const hidden = document.querySelectorAll(".gallery__item--hidden");
      const expanded = galleryMore.dataset.expanded === "true";
      hidden.forEach((el) => {
        el.style.display = expanded ? "none" : "block";
      });
      galleryMore.dataset.expanded = expanded ? "false" : "true";
      galleryMore.setAttribute("data-i18n", expanded ? "gallery.view_all" : "gallery.view_less");
      if (window.coveI18n) {
        const v = window.coveI18n.t(expanded ? "gallery.view_all" : "gallery.view_less");
        if (v) galleryMore.textContent = v;
      }
    });
  }
})();
