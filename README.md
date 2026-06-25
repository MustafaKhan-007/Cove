# COVE — Die Maßschneider · Website Rebuild

A premium, editorial, bilingual (DE/EN) rebuild of [cove.de](https://www.cove.de),
built with **Flask** and deployed on **Render.com**. Dark/neutral design with a
single warm-gold accent, Cormorant Garamond headings and Inter body type.

---

## Quick start (local)

```bash
# 1. (optional) create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. install dependencies
pip install -r requirements.txt

# 3. (optional) re-scrape content + images from cove.de
python scripts/scrape_cove.py

# 4. run the dev server
python app.py
# -> http://127.0.0.1:5000
```

The scraper output already lives in `scraped_content/` and the downloaded
images in `static/images/cove_original/`, so step 3 is optional.

---

## Project structure

```
app.py                 Flask app factory (exposes `app` for gunicorn)
config.py              Dev/prod config via env vars
extensions.py          SQLAlchemy + (optional) Flask-Mail singletons
content.py             Loads scraped_content/*.json (with real-content fallbacks)
blueprints/            main · shop · wiki · booking · api
models/                appointment.py (DB) + location/wiki helpers
templates/             base.html + per-section templates + partials
static/css/            main.css (tokens + layout) · components.css
static/js/             language.js · main.js · booking.js · gallery.js
static/translations/   de.json (default) · en.json
static/images/cove_original/   images downloaded from cove.de
scraped_content/       JSON cached from the original site
scripts/scrape_cove.py Step-1 scraper
scripts/smoke_test.py  Renders every route via the test client
render.yaml / Procfile Render.com deployment
```

---

## Content pipeline

`scripts/scrape_cove.py` caches the original site into `scraped_content/`:

| File | Source |
|------|--------|
| `homepage.json` | hero copy, headings |
| `about.json` | /ueber-uns text |
| `locations.json` | all 19 `/standorte/*` pages (address, phone, map embed, coords) |
| `products.json` | the product/service pages |
| `wiki_index.json` / `wiki_articles.json` | A–Z index + 6 seed articles |
| `faq.json`, `reviews.json`, `shop_products.json` | best-effort widget data |

`content.py` reads these and falls back to genuine, hand-verified COVE content
where a page is JS-rendered (reviews / FAQ / shop are loaded client-side on the
original site). Fallbacks are clearly marked in `content.py`.

---

## Booking system

`/termin` is a 5-step vanilla-JS wizard (`static/js/booking.js`) that POSTs to
`/api/booking`. Appointments persist to the `appointments` table
(`models/appointment.py`). Confirmation email is sent via Flask-Mail if SMTP is
configured (see `.env.example`); otherwise it is logged.

To use the client's existing Shore booking instead, set `SHORE_URL` in
`blueprints/booking/routes.py`.

---

## Internationalisation

Client-side i18n (`static/js/language.js`): elements use `data-i18n="section.key"`
and strings come from `static/translations/{de,en}.json`. Language preference is
stored in `localStorage`. German is the default.

---

## Adding wiki articles

The wiki is a first draft: the full A–Z index renders, but only 6 seed articles
have full body content. To populate another entry, add its slug to `WIKI_SEEDS`
in `scripts/scrape_cove.py` and re-run the scraper (or add an object to
`scraped_content/wiki_articles.json`). See the header comment in
`blueprints/wiki/routes.py`.

---

## Deploy to Render.com

1. Push this folder to a GitHub repo.
2. In Render, create a **Blueprint** from `render.yaml` (region: Frankfurt) — it
   provisions the web service + a free Postgres database and wires `DATABASE_URL`.
3. `SECRET_KEY` is generated automatically; set any `MAIL_*` vars if you want
   confirmation emails.

Start command: `gunicorn app:app --workers 2 --timeout 120 --preload`

---

## Notes / TODOs

- The shop links out to the original cove.de product pages; a full cart/checkout
  backend is **not** reimplemented (see `blueprints/shop/routes.py`).
- Google Maps embeds use the scraped per-location embed URLs where available,
  otherwise a coordinate/query embed (no API key required).
- Place ID for reviews: `ChIJXxP_MxbKuEcR8_ExE13qEl0`.
```
