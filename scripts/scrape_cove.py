# COVE Website Rebuild — scripts/scrape_cove.py — Step 1 content + image scraper
"""
Scrapes https://www.cove.de and subpages, caching all content to scraped_content/
and downloading every referenced image to static/images/cove_original/.

Run from the project root:
    python scripts/scrape_cove.py

The scraper is intentionally defensive: every page is wrapped in try/except so a
single failure never aborts the whole run. Whatever is successfully extracted is
written to disk so the Flask build can reference real data.
"""

import json
import os
import re
import time
import html
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE = "https://www.cove.de"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(ROOT, "scraped_content")
IMAGE_DIR = os.path.join(ROOT, "static", "images", "cove_original")

os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ---------------------------------------------------------------------------
# Static asset URLs explicitly called out in the spec
# ---------------------------------------------------------------------------
EXPLICIT_IMAGES = [
    f"{BASE}/wp-content/uploads/logo.svg",
    f"{BASE}/wp-content/uploads/2023/12/best-wedding-fashion-wedding-king-awards-sued.png",
    f"{BASE}/wp-content/uploads/2023/12/button_cocooning_rund.png",
    f"{BASE}/wp-content/uploads/2023/12/cove_qualitaetssiegel-480x477.png",
    f"{BASE}/wp-content/uploads/2023/12/deutscher-wirtschaftsfilmpreis.jpg",
    f"{BASE}/wp-content/uploads/2023/12/meisterkreis-logo.png",
    f"{BASE}/wp-content/uploads/2023/12/tbo-stilpartner.png",
    f"{BASE}/wp-content/uploads/2023/12/wedding-king-awards-480x63.png",
]
# Home cards 1..11
EXPLICIT_IMAGES += [f"{BASE}/wp-content/uploads/home-card-{i}.jpg" for i in range(1, 12)]
# Slides slide-1-1..20 and slide-2-1..20
EXPLICIT_IMAGES += [f"{BASE}/wp-content/uploads/slide-1-{i}.jpg" for i in range(1, 21)]
EXPLICIT_IMAGES += [f"{BASE}/wp-content/uploads/slide-2-{i}.jpg" for i in range(1, 21)]

LOCATION_SLUGS = [
    "berlin", "hamburg", "duesseldorf", "koeln", "frankfurt", "muenchen",
    "stuttgart", "bremen", "bochum", "dortmund", "hannover", "muenster",
    "essen", "wiesbaden", "frankfurt-2", "duesseldorf-2",
    "magazzino-duesseldorf", "bremen-2", "baden-baden",
]

PRODUCT_PAGES = {
    "massanzug": "/massanzug/",
    "masshemd": "/masshemd/",
    "hochzeit": "/hochzeit/",
    "sakko": "/das-sakko/",
    "mantel": "/der-mantel/",
    "schuhe": "/schuhwerk/",
    "cove-custom-shirt": "/cove-custom-shirt/",
    "herrenschuh-designen": "/herrenschuh-selber-designen/",
}

WIKI_SEEDS = [
    "bespoke", "full-canvas", "hochzeitsanzug",
    "kaschmir-cashmere", "harris-tweed", "flanell",
]

SHOP_CATEGORY_PAGES = [
    "/shop/",
    "/shop/produkt-kategorie/ready-to-wear/",
    "/shop/produkt-kategorie/schuhe/",
    "/shop/produkt-kategorie/accessoires/",
    "/shop/produkt-kategorie/duefte-pflege/",
    "/shop/produkt-kategorie/geschenke-gutscheine/",
    "/shop/produkt-kategorie/buecher/",
]

# Collect every image URL seen during the run, then download once at the end.
DISCOVERED_IMAGES = set(EXPLICIT_IMAGES)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def fetch(url):
    """Fetch a URL, returning a BeautifulSoup object or None on failure."""
    try:
        r = SESSION.get(url, timeout=25)
        if r.status_code == 200:
            r.encoding = r.apparent_encoding or "utf-8"
            return BeautifulSoup(r.text, "html.parser"), r.text
        print(f"  ! {url} -> HTTP {r.status_code}")
    except Exception as exc:  # noqa: BLE001
        print(f"  ! fetch failed {url}: {exc}")
    return None, None


def clean(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def collect_images(soup, base_url):
    """Record absolute http(s) image URLs found in a soup."""
    for img in soup.find_all("img"):
        for attr in ("data-src", "data-lazy-src", "src", "data-large_image"):
            src = img.get(attr)
            if src and not src.startswith("data:"):
                DISCOVERED_IMAGES.add(urljoin(base_url, src.split("?")[0]))
                break
    # background images in style attributes
    for el in soup.find_all(style=True):
        for m in re.findall(r"url\((['\"]?)(.*?)\1\)", el["style"]):
            src = m[1]
            if src and not src.startswith("data:"):
                DISCOVERED_IMAGES.add(urljoin(base_url, src.split("?")[0]))


def page_text_blocks(soup):
    """Return cleaned visible text blocks from the main content of a page."""
    body = soup.find("body")
    if not body:
        return []
    work = BeautifulSoup(str(body), "html.parser")
    for tag in work(["script", "style", "noscript", "nav", "header", "footer", "form"]):
        tag.decompose()
    blocks = []
    seen = set()
    for el in work.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        t = clean(el.get_text(" ", strip=True))
        if not t or len(t) < 3:
            continue
        # skip pure-navigation noise
        low = t.lower()
        if low in ("startseite", "shop", "warenkorb", "mehr lesen", "weiterlesen"):
            continue
        if t in seen:
            continue
        seen.add(t)
        blocks.append({"tag": el.name, "text": t})
    return blocks


def headings(soup, level):
    return [clean(h.get_text(" ", strip=True)) for h in soup.find_all(level) if clean(h.get_text())]


def save(name, data):
    path = os.path.join(CONTENT_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"  -> wrote {name} ({len(json.dumps(data))} bytes)")


# ---------------------------------------------------------------------------
# Scrapers
# ---------------------------------------------------------------------------
def scrape_homepage():
    print("[homepage]")
    soup, raw = fetch(BASE)
    if not soup:
        return
    collect_images(soup, BASE)
    data = {
        "url": BASE,
        "title": clean(soup.title.string) if soup.title else "",
        "meta_description": meta_desc(soup),
        "h1": headings(soup, "h1"),
        "h2": headings(soup, "h2"),
        "text_blocks": page_text_blocks(soup),
    }
    save("homepage.json", data)
    # reviews live on the homepage widget
    scrape_reviews(soup, raw)


def meta_desc(soup):
    tag = soup.find("meta", attrs={"name": "description"})
    if tag and tag.get("content"):
        return clean(tag["content"])
    tag = soup.find("meta", attrs={"property": "og:description"})
    return clean(tag["content"]) if tag and tag.get("content") else ""


def scrape_reviews(home_soup, raw):
    print("[reviews]")
    reviews = []
    summary = {"rating": None, "count": None}

    # 1) JSON-LD aggregateRating
    for script in home_soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            payload = json.loads(script.string or "{}")
        except Exception:  # noqa: BLE001
            continue
        for node in payload if isinstance(payload, list) else [payload]:
            agg = node.get("aggregateRating") if isinstance(node, dict) else None
            if agg:
                summary["rating"] = agg.get("ratingValue") or summary["rating"]
                summary["count"] = agg.get("reviewCount") or agg.get("ratingCount") or summary["count"]
            for rv in (node.get("review") or []) if isinstance(node, dict) else []:
                reviews.append({
                    "author": (rv.get("author") or {}).get("name") if isinstance(rv.get("author"), dict) else rv.get("author"),
                    "rating": (rv.get("reviewRating") or {}).get("ratingValue"),
                    "text": clean(rv.get("reviewBody") or rv.get("description") or ""),
                    "time": rv.get("datePublished", ""),
                })

    # 2) Inline JS review arrays (common Google-reviews widgets)
    if raw:
        for m in re.findall(r'"(?:review_text|reviewBody|text)"\s*:\s*"((?:[^"\\]|\\.){10,})"', raw):
            txt = clean(bytes(m, "utf-8").decode("unicode_escape", errors="ignore"))
            if txt and txt not in [r["text"] for r in reviews]:
                reviews.append({"author": "", "rating": 5, "text": txt, "time": ""})
        # author names paired loosely
        if not summary["count"]:
            mc = re.search(r'([0-9]{2,4})\s*(?:Rezensionen|reviews)', raw)
            if mc:
                summary["count"] = mc.group(1)
        if not summary["rating"]:
            mr = re.search(r'\b(4\.[0-9])\b', raw)
            if mr:
                summary["rating"] = mr.group(1)

    save("reviews.json", {"summary": summary, "reviews": reviews})


def scrape_about():
    print("[about]")
    soup, _ = fetch(f"{BASE}/ueber-uns/")
    if not soup:
        return
    collect_images(soup, f"{BASE}/ueber-uns/")
    save("about.json", {
        "url": f"{BASE}/ueber-uns/",
        "title": clean(soup.title.string) if soup.title else "",
        "meta_description": meta_desc(soup),
        "h1": headings(soup, "h1"),
        "h2": headings(soup, "h2"),
        "text_blocks": page_text_blocks(soup),
    })


def scrape_locations():
    print("[locations]")
    locations = []
    for slug in LOCATION_SLUGS:
        url = f"{BASE}/standorte/{slug}/"
        print(f"  - {slug}")
        soup, raw = fetch(url)
        if not soup:
            continue
        collect_images(soup, url)
        # phone
        phones = [a["href"].replace("tel:", "").strip()
                  for a in soup.find_all("a", href=True) if a["href"].startswith("tel:")]
        # maps embed
        maps = [i.get("src") for i in soup.find_all("iframe")
                if "google.com/maps" in (i.get("src") or "")]
        # coordinates from embed
        coords = None
        if maps:
            cm = re.search(r"!1d([0-9.]+)!2d([0-9.]+)", maps[0])
            if cm:
                coords = {"lat": float(cm.group(1)), "lng": float(cm.group(2))}
        # address heuristics: look for postal-code line
        addr = extract_address(soup)
        hours = extract_hours(soup)
        locations.append({
            "slug": slug,
            "city": slug_to_city(slug),
            "url": url,
            "title": clean(soup.title.string) if soup.title else "",
            "phone": phones[0] if phones else "+49 211 1712801",
            "address": addr,
            "hours": hours,
            "map_embed": maps[0] if maps else "",
            "coords": coords,
            "text_blocks": page_text_blocks(soup)[:12],
        })
        time.sleep(0.3)
    save("locations.json", locations)


CITY_NAMES = {
    "berlin": "Berlin", "hamburg": "Hamburg", "duesseldorf": "Düsseldorf",
    "koeln": "Köln", "frankfurt": "Frankfurt am Main", "muenchen": "München",
    "stuttgart": "Stuttgart", "bremen": "Bremen", "bochum": "Bochum",
    "dortmund": "Dortmund", "hannover": "Hannover", "muenster": "Münster",
    "essen": "Essen", "wiesbaden": "Wiesbaden", "frankfurt-2": "Frankfurt (Goethestraße)",
    "duesseldorf-2": "Düsseldorf (Altstadt)", "magazzino-duesseldorf": "Magazzino Düsseldorf",
    "bremen-2": "Bremen (Zweite Filiale)", "baden-baden": "Baden-Baden",
}


def slug_to_city(slug):
    return CITY_NAMES.get(slug, slug.replace("-", " ").title())


def extract_address(soup):
    text = soup.get_text("\n")
    # German postal code + city pattern, capture the preceding street line
    lines = [clean(l) for l in text.split("\n") if clean(l)]
    for i, line in enumerate(lines):
        if re.match(r"^\d{5}\s+\w", line):
            street = lines[i - 1] if i > 0 else ""
            return clean(f"{street}, {line}")
    return ""


def extract_hours(soup):
    text = soup.get_text("\n")
    days = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag",
            "Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")
    hours = []
    for line in text.split("\n"):
        l = clean(line)
        if any(l.startswith(d) for d in days) and re.search(r"\d{1,2}[:.]\d{2}", l):
            hours.append(l)
    return hours[:10]


def scrape_products():
    print("[products]")
    products = {}
    for key, path in PRODUCT_PAGES.items():
        url = f"{BASE}{path}"
        print(f"  - {key}")
        soup, _ = fetch(url)
        if not soup:
            continue
        collect_images(soup, url)
        products[key] = {
            "url": url,
            "title": clean(soup.title.string) if soup.title else "",
            "meta_description": meta_desc(soup),
            "h1": headings(soup, "h1"),
            "h2": headings(soup, "h2"),
            "text_blocks": page_text_blocks(soup),
            "images": page_images(soup, url),
        }
        time.sleep(0.3)
    save("products.json", products)


def page_images(soup, base_url):
    out = []
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src")
        if src and not src.startswith("data:") and "uploads" in src:
            out.append(urljoin(base_url, src.split("?")[0]))
    # dedupe preserving order
    seen, uniq = set(), []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq[:30]


def scrape_faq():
    print("[faq]")
    soup, _ = fetch(f"{BASE}/f-a-q/")
    if not soup:
        return
    collect_images(soup, f"{BASE}/f-a-q/")
    faqs = []
    # Elementor accordion / toggle items
    for item in soup.select(".elementor-accordion-item, .elementor-toggle-item, .elementor-tab-title"):
        q = item.select_one(".elementor-accordion-title, .elementor-toggle-title, .elementor-tab-title")
        a = item.select_one(".elementor-tab-content, .elementor-accordion-content")
        if q:
            faqs.append({"q": clean(q.get_text(" ")), "a": clean(a.get_text(" ")) if a else ""})
    # fallback: JSON-LD FAQPage
    if not faqs:
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                payload = json.loads(script.string or "{}")
            except Exception:  # noqa: BLE001
                continue
            for node in payload if isinstance(payload, list) else [payload]:
                if isinstance(node, dict) and node.get("@type") == "FAQPage":
                    for q in node.get("mainEntity", []):
                        faqs.append({
                            "q": clean(q.get("name", "")),
                            "a": clean((q.get("acceptedAnswer") or {}).get("text", "")),
                        })
    save("faq.json", {"url": f"{BASE}/f-a-q/", "faqs": faqs})


def scrape_wiki():
    print("[wiki index]")
    soup, _ = fetch(f"{BASE}/wiki/")
    index = []
    if soup:
        collect_images(soup, f"{BASE}/wiki/")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/wiki/" in href and href.rstrip("/") != f"{BASE}/wiki":
                slug = href.rstrip("/").split("/")[-1]
                title = clean(a.get_text(" "))
                if slug and title and len(title) < 80:
                    index.append({"slug": slug, "title": title, "url": href})
        # dedupe by slug
        seen, uniq = set(), []
        for e in index:
            if e["slug"] not in seen:
                seen.add(e["slug"])
                uniq.append(e)
        index = uniq
    save("wiki_index.json", index)

    print("[wiki articles]")
    articles = {}
    for slug in WIKI_SEEDS:
        url = f"{BASE}/wiki/{slug}/"
        print(f"  - {slug}")
        s, _ = fetch(url)
        if not s:
            continue
        collect_images(s, url)
        articles[slug] = {
            "slug": slug,
            "url": url,
            "title": (headings(s, "h1") or [clean(s.title.string) if s.title else slug])[0],
            "meta_description": meta_desc(s),
            "text_blocks": page_text_blocks(s),
            "images": page_images(s, url),
        }
        time.sleep(0.3)
    save("wiki_articles.json", articles)


def scrape_shop():
    print("[shop]")
    products = []
    seen = set()
    for path in SHOP_CATEGORY_PAGES:
        url = f"{BASE}{path}"
        print(f"  - {path}")
        soup, _ = fetch(url)
        if not soup:
            continue
        collect_images(soup, url)
        for li in soup.select("li.product, .product"):
            name_el = li.select_one(".woocommerce-loop-product__title, h2, h3, .product-title")
            price_el = li.select_one(".price, .woocommerce-Price-amount")
            link_el = li.select_one("a")
            img_el = li.select_one("img")
            name = clean(name_el.get_text(" ")) if name_el else ""
            if not name or name in seen:
                continue
            seen.add(name)
            img = ""
            if img_el:
                img = img_el.get("data-src") or img_el.get("src") or ""
                if img.startswith("data:"):
                    img = img_el.get("data-src") or ""
            products.append({
                "name": name,
                "price": clean(price_el.get_text(" ")) if price_el else "",
                "url": link_el["href"] if link_el and link_el.get("href") else url,
                "image": urljoin(url, img.split("?")[0]) if img and not img.startswith("data:") else "",
                "category": path.rstrip("/").split("/")[-1],
            })
        time.sleep(0.3)
    save("shop_products.json", products)


# ---------------------------------------------------------------------------
# Image download
# ---------------------------------------------------------------------------
def download_images():
    print(f"[images] downloading {len(DISCOVERED_IMAGES)} files")
    ok, fail = 0, 0
    for url in sorted(DISCOVERED_IMAGES):
        try:
            name = os.path.basename(urlparse(url).path)
            if not name:
                continue
            dest = os.path.join(IMAGE_DIR, name)
            if os.path.exists(dest) and os.path.getsize(dest) > 0:
                ok += 1
                continue
            r = SESSION.get(url, timeout=30)
            if r.status_code == 200 and r.content:
                with open(dest, "wb") as fh:
                    fh.write(r.content)
                ok += 1
            else:
                fail += 1
        except Exception as exc:  # noqa: BLE001
            fail += 1
            print(f"  ! image {url}: {exc}")
    print(f"[images] done: {ok} ok, {fail} failed")
    save("image_manifest.json", sorted(DISCOVERED_IMAGES))


def main():
    print("=== COVE scraper starting ===")
    scrape_homepage()
    scrape_about()
    scrape_locations()
    scrape_products()
    scrape_faq()
    scrape_wiki()
    scrape_shop()
    download_images()
    print("=== COVE scraper finished ===")


if __name__ == "__main__":
    main()
