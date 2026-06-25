// COVE Website Rebuild — static/js/booking.js — multi-step appointment wizard
(function () {
  "use strict";

  const root = document.getElementById("booking");
  if (!root) return;

  const TOTAL_STEPS = 5;
  let step = 1;
  const state = {
    service: null,
    location_id: null,
    location_name: null,
    preferred_date: null,
    preferred_time: null,
    salutation: "Keine Angabe",
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    message: "",
    privacy: false,
  };

  const steps = Array.from(root.querySelectorAll(".booking__step"));
  const progress = Array.from(root.querySelectorAll(".booking-progress__step"));
  const stepLabel = root.querySelector(".booking__step-label");
  const nextBtn = root.querySelector("#bookingNext");
  const backBtn = root.querySelector("#bookingBack");
  const confirmBtn = root.querySelector("#bookingConfirm");
  const successEl = root.querySelector(".booking__success");
  const cardEl = root.querySelector(".booking__card");

  // ---- STEP 1: services -------------------------------------------
  root.querySelectorAll(".service-tile").forEach((tile) => {
    tile.addEventListener("click", () => {
      root.querySelectorAll(".service-tile").forEach((t) => t.classList.remove("is-selected"));
      tile.classList.add("is-selected");
      state.service = tile.dataset.service;
      validate();
    });
  });

  // ---- STEP 2: location -------------------------------------------
  const locSelect = root.querySelector("#bookingLocation");
  if (locSelect) {
    locSelect.addEventListener("change", () => {
      state.location_id = locSelect.value;
      const opt = locSelect.options[locSelect.selectedIndex];
      state.location_name = opt ? opt.textContent.trim() : "";
      validate();
    });
  }

  // ---- STEP 3: calendar + time ------------------------------------
  const calTitle = root.querySelector("#calTitle");
  const calGrid = root.querySelector("#calGrid");
  const slotWrap = root.querySelector("#timeslots");
  let viewDate = new Date();
  viewDate.setDate(1);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const MONTHS = {
    de: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    en: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
  };
  const DOW = { de: ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"], en: ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"] };

  function lang() { return (window.coveI18n && window.coveI18n.currentLang()) || "de"; }

  function renderCalendar() {
    if (!calGrid) return;
    const l = lang();
    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();
    calTitle.textContent = `${MONTHS[l][month]} ${year}`;
    calGrid.innerHTML = "";
    DOW[l].forEach((d) => {
      const el = document.createElement("div");
      el.className = "calendar__dow";
      el.textContent = d;
      calGrid.appendChild(el);
    });
    // Monday-first offset
    let firstDow = new Date(year, month, 1).getDay(); // 0=Sun
    firstDow = (firstDow + 6) % 7;
    for (let i = 0; i < firstDow; i++) {
      const e = document.createElement("div");
      e.className = "calendar__day is-empty";
      calGrid.appendChild(e);
    }
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    for (let d = 1; d <= daysInMonth; d++) {
      const date = new Date(year, month, d);
      const el = document.createElement("div");
      el.className = "calendar__day";
      el.textContent = d;
      const isSunday = date.getDay() === 0;
      const isPast = date < today;
      if (isSunday || isPast) {
        el.classList.add("is-disabled");
      } else {
        el.classList.add("is-available");
        const iso = isoDate(date);
        if (state.preferred_date === iso) el.classList.add("is-selected");
        el.addEventListener("click", () => {
          state.preferred_date = iso;
          renderCalendar();
          validate();
        });
      }
      calGrid.appendChild(el);
    }
  }

  function isoDate(d) {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  }

  root.querySelector("#calPrev")?.addEventListener("click", () => {
    viewDate.setMonth(viewDate.getMonth() - 1);
    renderCalendar();
  });
  root.querySelector("#calNext")?.addEventListener("click", () => {
    viewDate.setMonth(viewDate.getMonth() + 1);
    renderCalendar();
  });

  if (slotWrap) {
    slotWrap.querySelectorAll(".timeslot").forEach((slot) => {
      slot.addEventListener("click", () => {
        slotWrap.querySelectorAll(".timeslot").forEach((s) => s.classList.remove("is-selected"));
        slot.classList.add("is-selected");
        state.preferred_time = slot.dataset.time;
        validate();
      });
    });
  }

  // ---- STEP 4: details --------------------------------------------
  root.querySelectorAll(".radio-pill input[name='salutation']").forEach((r) => {
    r.addEventListener("change", () => { state.salutation = r.value; });
  });
  const fields = ["first_name", "last_name", "email", "phone", "message"];
  fields.forEach((f) => {
    const el = root.querySelector(`#field_${f}`);
    if (el) el.addEventListener("input", () => { state[f] = el.value.trim(); validate(); });
  });
  const privacyEl = root.querySelector("#field_privacy");
  if (privacyEl) privacyEl.addEventListener("change", () => { state.privacy = privacyEl.checked; validate(); });

  // ---- navigation -------------------------------------------------
  function stepValid(s) {
    switch (s) {
      case 1: return !!state.service;
      case 2: return !!state.location_id;
      case 3: return !!state.preferred_date && !!state.preferred_time;
      case 4: return state.first_name && state.last_name && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(state.email) && state.privacy;
      default: return true;
    }
  }

  function validate() {
    if (nextBtn) nextBtn.disabled = !stepValid(step);
    if (confirmBtn) confirmBtn.disabled = !stepValid(4);
  }

  function render() {
    steps.forEach((el, i) => el.classList.toggle("is-active", i === step - 1));
    progress.forEach((el, i) => {
      el.classList.toggle("booking-progress__step--active", i === step - 1);
      el.classList.toggle("booking-progress__step--complete", i < step - 1);
    });
    if (stepLabel) {
      const t = window.coveI18n;
      const lbl = t ? t.t(`booking.step`) : "Schritt";
      const of = t ? t.t(`booking.of`) : "von";
      stepLabel.textContent = `${lbl} ${step} ${of} ${TOTAL_STEPS}`;
    }
    if (backBtn) backBtn.style.visibility = step === 1 ? "hidden" : "visible";
    if (nextBtn) nextBtn.style.display = step >= TOTAL_STEPS ? "none" : "inline-flex";
    if (confirmBtn) confirmBtn.style.display = step === TOTAL_STEPS ? "inline-flex" : "none";
    if (step === 3) renderCalendar();
    if (step === TOTAL_STEPS) fillSummary();
    validate();
  }

  function fillSummary() {
    const set = (id, val) => { const e = root.querySelector(id); if (e) e.textContent = val || "—"; };
    set("#sum_service", state.service);
    set("#sum_location", state.location_name);
    set("#sum_datetime", `${state.preferred_date || ""} · ${state.preferred_time || ""}`);
    set("#sum_name", `${state.salutation} ${state.first_name} ${state.last_name}`.trim());
    set("#sum_contact", `${state.email}${state.phone ? " · " + state.phone : ""}`);
  }

  nextBtn?.addEventListener("click", () => {
    if (step < TOTAL_STEPS && stepValid(step)) { step++; render(); window.scrollTo({ top: root.offsetTop - 100, behavior: "smooth" }); }
  });
  backBtn?.addEventListener("click", () => {
    if (step > 1) { step--; render(); }
  });

  // summary edit buttons
  root.querySelectorAll("[data-goto]").forEach((btn) => {
    btn.addEventListener("click", () => { step = parseInt(btn.dataset.goto, 10); render(); });
  });

  // ---- submit -----------------------------------------------------
  confirmBtn?.addEventListener("click", async () => {
    confirmBtn.disabled = true;
    const payload = Object.assign({}, state, { language: lang() });
    try {
      const res = await fetch("/api/booking", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.success) {
        cardEl.querySelectorAll(".booking__step, .booking__actions, .booking-progress, .booking__step-label").forEach((el) => (el.style.display = "none"));
        successEl.classList.add("is-active");
        const msgEl = successEl.querySelector(".booking__success-msg");
        if (msgEl) msgEl.textContent = data.message;
      } else {
        alert(data.message || "Fehler. Bitte versuchen Sie es erneut.");
        confirmBtn.disabled = false;
      }
    } catch (err) {
      alert("Netzwerkfehler. Bitte versuchen Sie es erneut.");
      confirmBtn.disabled = false;
    }
  });

  // re-render labels when language changes
  document.addEventListener("languagechange", () => render());

  render();
})();
