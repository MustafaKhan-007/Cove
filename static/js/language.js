// COVE Website Rebuild — static/js/language.js — lightweight DE/EN i18n
const TRANSLATIONS = {};

async function loadLanguage(lang) {
  try {
    if (!TRANSLATIONS[lang]) {
      const response = await fetch(`/static/translations/${lang}.json`);
      TRANSLATIONS[lang] = await response.json();
    }
    localStorage.setItem("cove_lang", lang);
    applyTranslations(lang);
    updateLangButtons(lang);
    document.dispatchEvent(new CustomEvent("languagechange", { detail: { lang } }));
  } catch (err) {
    console.error("Failed to load language", lang, err);
  }
}

function getNestedValue(obj, path) {
  return path.split(".").reduce((acc, key) => (acc ? acc[key] : undefined), obj);
}

function interpolate(str, vars) {
  if (!vars) return str;
  return str.replace(/\{(\w+)\}/g, (m, k) => (vars[k] != null ? vars[k] : m));
}

function applyTranslations(lang) {
  const dict = TRANSLATIONS[lang];
  if (!dict) return;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    let value = getNestedValue(dict, key);
    if (value == null) return;
    // optional interpolation vars via data-i18n-vars='{"count":"837"}'
    const rawVars = el.getAttribute("data-i18n-vars");
    if (rawVars) {
      try { value = interpolate(value, JSON.parse(rawVars)); } catch (e) {}
    }
    el.innerHTML = value;
  });
  document.querySelectorAll("[data-i18n-attr]").forEach((el) => {
    // format: data-i18n-attr="placeholder:locations.search"
    el.getAttribute("data-i18n-attr").split(",").forEach((pair) => {
      const [attr, key] = pair.split(":").map((s) => s.trim());
      const value = getNestedValue(dict, key);
      if (value != null) el.setAttribute(attr, value);
    });
  });
  document.documentElement.lang = lang;
}

function updateLangButtons(lang) {
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.lang === lang);
  });
}

function currentLang() {
  return localStorage.getItem("cove_lang") || "de";
}

document.addEventListener("DOMContentLoaded", () => {
  loadLanguage(currentLang());
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => loadLanguage(btn.dataset.lang));
  });
});

window.coveI18n = { loadLanguage, currentLang, getNestedValue, t: (key) => getNestedValue(TRANSLATIONS[currentLang()], key) };
