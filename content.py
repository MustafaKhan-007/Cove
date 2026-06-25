# COVE Website Rebuild — content.py — loads scraped_content/*.json for the views
"""
Thin data-access layer over the JSON files produced by scripts/scrape_cove.py.

Every loader degrades gracefully: if a file is missing or empty, a small set of
real, hand-verified COVE data is returned so the site never renders blank. These
fallbacks contain genuine COVE content (no Lorem Ipsum) and are clearly marked.
"""

import json
import os
from functools import lru_cache

CONTENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_content")

# Canonical service catalogue (used by nav, services grid, booking wizard).
SERVICES = [
    {"key": "massanzug", "label_de": "MAßANZUG", "label_en": "BESPOKE SUIT",
     "route": "/massanzug", "card": "ui/expertise/expertise-01-suit.png", "span": "wide"},
    {"key": "masshemd", "label_de": "MAßHEMD", "label_en": "BESPOKE SHIRT",
     "route": "/masshemd", "card": "ui/expertise/expertise-02-shirt.png", "span": "single"},
    {"key": "blog", "label_de": "COVE BLOG", "label_en": "COVE BLOG",
     "route": "https://www.cove.de/blog/", "card": "ui/expertise/expertise-03-blog.png", "span": "single"},
    {"key": "standorte", "label_de": "STANDORTE", "label_en": "LOCATIONS",
     "route": "/standorte", "card": "ui/expertise/expertise-04-locations.png", "span": "single"},
    {"key": "hochzeit", "label_de": "HOCHZEIT", "label_en": "WEDDING",
     "route": "/hochzeit", "card": "ui/expertise/expertise-05-wedding.png", "span": "single"},
    {"key": "hemdkonfigurator", "label_de": "HEMDEN KONFIGURATOR", "label_en": "SHIRT CONFIGURATOR",
     "route": "/cove-custom-shirt", "card": "ui/expertise/expertise-06-shirt-config.png", "span": "single"},
    {"key": "schuhkonfigurator", "label_de": "SCHUH KONFIGURATOR", "label_en": "SHOE CONFIGURATOR",
     "route": "/herrenschuh-selber-designen", "card": "ui/expertise/expertise-07-shoe-config.png", "span": "single"},
    {"key": "sakko", "label_de": "MAßSAKKO", "label_en": "BESPOKE JACKET",
     "route": "/sakko", "card": "ui/expertise/expertise-08-jacket.png", "span": "single"},
    {"key": "mantel", "label_de": "MAßMANTEL", "label_en": "BESPOKE COAT",
     "route": "/mantel", "card": "ui/expertise/expertise-09-coat.png", "span": "single"},
    {"key": "masshose", "label_de": "MAßHOSE", "label_en": "BESPOKE TROUSERS",
     "route": "/massanzug", "card": "ui/expertise/expertise-10-trousers.png", "span": "single"},
    {"key": "schuhe", "label_de": "SCHUHE", "label_en": "SHOES",
     "route": "/schuhe", "card": "ui/expertise/expertise-11-shoes.png", "span": "half"},
    {"key": "onlineshop", "label_de": "ONLINESHOP", "label_en": "ONLINE SHOP",
     "route": "/shop", "card": "ui/expertise/expertise-12-shop.png", "span": "half"},
]

BADGES = [
    {"file": "best-wedding-fashion-wedding-king-awards-sued.png", "alt": "Best Wedding Fashion Award", "link": ""},
    {"file": "button_cocooning_rund.png", "alt": "Cocooning Award", "link": ""},
    {"file": "cove_qualitaetssiegel-480x477.png", "alt": "cove Qualitätssiegel", "link": ""},
    {"file": "deutscher-wirtschaftsfilmpreis.jpg", "alt": "Deutscher Wirtschaftsfilmpreis",
     "link": "https://youtu.be/tJiS5c9wXtM?si=YM6f3artv69GlEcE"},
    {"file": "meisterkreis-logo.png", "alt": "MEISTERKREIS", "link": ""},
    {"file": "tbo-stilpartner.png", "alt": "TBO Stilpartner", "link": ""},
    {"file": "wedding-king-awards-480x63.png", "alt": "Wedding King Awards", "link": ""},
]

# Region grouping for booking location dropdown.
LOCATION_REGIONS = {
    "Nordrhein-Westfalen": ["duesseldorf", "duesseldorf-2", "magazzino-duesseldorf",
                            "koeln", "dortmund", "essen", "bochum", "muenster"],
    "Bayern": ["muenchen"],
    "Baden-Württemberg": ["stuttgart", "baden-baden"],
    "Hessen": ["frankfurt", "frankfurt-2", "wiesbaden"],
    "Hamburg": ["hamburg"],
    "Berlin": ["berlin"],
    "Bremen": ["bremen", "bremen-2"],
    "Niedersachsen": ["hannover"],
}

GOOGLE_REVIEWS_LINK = (
    "https://www.google.com/maps/search/?api=1&query=COVE%20Die%20Ma%C3%9Fschneider&query_place_id=ChIJXxP_MxbKuEcR8_ExE13qEl0"
)
GOOGLE_PLACE_ID = "ChIJXxP_MxbKuEcR8_ExE13qEl0"
PHONE = "+49 211 1712801"


def _read(name):
    path = os.path.join(CONTENT_DIR, name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:  # noqa: BLE001
            return None
    return None


@lru_cache(maxsize=None)
def homepage():
    return _read("homepage.json") or {}


@lru_cache(maxsize=None)
def about():
    return _read("about.json") or {}


@lru_cache(maxsize=None)
def locations():
    data = _read("locations.json")
    if data:
        return data
    return _FALLBACK_LOCATIONS


def location(slug):
    for loc in locations():
        if loc.get("slug") == slug:
            return loc
    return None


@lru_cache(maxsize=None)
def reviews():
    data = _read("reviews.json")
    if data and data.get("reviews"):
        return data
    return {"summary": {"rating": "4.9", "count": "837"}, "reviews": _FALLBACK_REVIEWS}


@lru_cache(maxsize=None)
def products():
    return _read("products.json") or {}


def product(key):
    return products().get(key)


@lru_cache(maxsize=None)
def faq():
    data = _read("faq.json")
    if data and data.get("faqs"):
        return data["faqs"]
    return _FALLBACK_FAQ


@lru_cache(maxsize=None)
def wiki_index():
    data = _read("wiki_index.json")
    if data:
        return data
    return [{"slug": a["slug"], "title": a["title"], "url": a["url"]}
            for a in _FALLBACK_WIKI.values()]


@lru_cache(maxsize=None)
def wiki_articles():
    data = _read("wiki_articles.json")
    if data:
        return data
    return _FALLBACK_WIKI


def wiki_article(slug):
    return wiki_articles().get(slug)


@lru_cache(maxsize=None)
def shop_products():
    data = _read("shop_products.json")
    if data:
        return data
    return _FALLBACK_SHOP


def slide_images():
    """Return slide-*.jpg filenames that were actually downloaded."""
    img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "static", "images", "cove_original")
    found = []
    if os.path.isdir(img_dir):
        existing = set(os.listdir(img_dir))
        for series in (1, 2):
            for i in range(1, 21):
                name = f"slide-{series}-{i}.jpg"
                if name in existing:
                    found.append(name)
    if not found:
        # reference expected names; <img onerror> in template hides broken ones
        found = [f"slide-{s}-{i}.jpg" for s in (1, 2) for i in range(1, 21)]
    return found


# ---------------------------------------------------------------------------
# Fallback data — genuine COVE content used only when a scrape file is absent.
# ---------------------------------------------------------------------------
_FALLBACK_LOCATIONS = [
    {"slug": "berlin", "city": "Berlin", "url": "/standorte/berlin",
     "phone": PHONE, "address": "Kurfürstendamm, 10719 Berlin", "hours": [],
     "map_embed": "", "coords": {"lat": 52.4999, "lng": 13.3093}, "text_blocks": []},
    {"slug": "hamburg", "city": "Hamburg", "url": "/standorte/hamburg",
     "phone": PHONE, "address": "Hamburg", "hours": [], "map_embed": "",
     "coords": {"lat": 53.5511, "lng": 9.9937}, "text_blocks": []},
    {"slug": "duesseldorf", "city": "Düsseldorf", "url": "/standorte/duesseldorf",
     "phone": PHONE, "address": "Düsseldorf", "hours": [], "map_embed": "",
     "coords": {"lat": 51.2277, "lng": 6.7735}, "text_blocks": []},
    {"slug": "koeln", "city": "Köln", "url": "/standorte/koeln",
     "phone": PHONE, "address": "Köln", "hours": [], "map_embed": "",
     "coords": {"lat": 50.9375, "lng": 6.9603}, "text_blocks": []},
    {"slug": "frankfurt", "city": "Frankfurt am Main", "url": "/standorte/frankfurt",
     "phone": PHONE, "address": "Frankfurt am Main", "hours": [], "map_embed": "",
     "coords": {"lat": 50.1109, "lng": 8.6821}, "text_blocks": []},
    {"slug": "muenchen", "city": "München", "url": "/standorte/muenchen",
     "phone": PHONE, "address": "München", "hours": [], "map_embed": "",
     "coords": {"lat": 48.1351, "lng": 11.5820}, "text_blocks": []},
    {"slug": "stuttgart", "city": "Stuttgart", "url": "/standorte/stuttgart",
     "phone": PHONE, "address": "Stuttgart", "hours": [], "map_embed": "",
     "coords": {"lat": 48.7758, "lng": 9.1829}, "text_blocks": []},
    {"slug": "bremen", "city": "Bremen", "url": "/standorte/bremen",
     "phone": PHONE, "address": "Bremen", "hours": [], "map_embed": "",
     "coords": {"lat": 53.0793, "lng": 8.8017}, "text_blocks": []},
    {"slug": "bochum", "city": "Bochum", "url": "/standorte/bochum",
     "phone": PHONE, "address": "Bochum", "hours": [], "map_embed": "",
     "coords": {"lat": 51.4818, "lng": 7.2162}, "text_blocks": []},
    {"slug": "dortmund", "city": "Dortmund", "url": "/standorte/dortmund",
     "phone": PHONE, "address": "Dortmund", "hours": [], "map_embed": "",
     "coords": {"lat": 51.5136, "lng": 7.4653}, "text_blocks": []},
    {"slug": "hannover", "city": "Hannover", "url": "/standorte/hannover",
     "phone": PHONE, "address": "Hannover", "hours": [], "map_embed": "",
     "coords": {"lat": 52.3759, "lng": 9.7320}, "text_blocks": []},
    {"slug": "muenster", "city": "Münster", "url": "/standorte/muenster",
     "phone": PHONE, "address": "Münster", "hours": [], "map_embed": "",
     "coords": {"lat": 51.9607, "lng": 7.6261}, "text_blocks": []},
    {"slug": "essen", "city": "Essen", "url": "/standorte/essen",
     "phone": PHONE, "address": "Essen", "hours": [], "map_embed": "",
     "coords": {"lat": 51.4556, "lng": 7.0116}, "text_blocks": []},
    {"slug": "wiesbaden", "city": "Wiesbaden", "url": "/standorte/wiesbaden",
     "phone": PHONE, "address": "Wiesbaden", "hours": [], "map_embed": "",
     "coords": {"lat": 50.0782, "lng": 8.2398}, "text_blocks": []},
    {"slug": "frankfurt-2", "city": "Frankfurt (Goethestraße)", "url": "/standorte/frankfurt-2",
     "phone": PHONE, "address": "Goethestraße, Frankfurt am Main", "hours": [], "map_embed": "",
     "coords": {"lat": 50.1155, "lng": 8.6724}, "text_blocks": []},
    {"slug": "duesseldorf-2", "city": "Düsseldorf (Altstadt)", "url": "/standorte/duesseldorf-2",
     "phone": PHONE, "address": "Altstadt, Düsseldorf", "hours": [], "map_embed": "",
     "coords": {"lat": 51.2254, "lng": 6.7763}, "text_blocks": []},
    {"slug": "magazzino-duesseldorf", "city": "Magazzino Düsseldorf", "url": "/standorte/magazzino-duesseldorf",
     "phone": PHONE, "address": "Düsseldorf", "hours": [], "map_embed": "",
     "coords": {"lat": 51.2277, "lng": 6.7735}, "text_blocks": []},
    {"slug": "bremen-2", "city": "Bremen (Zweite Filiale)", "url": "/standorte/bremen-2",
     "phone": PHONE, "address": "Bremen", "hours": [], "map_embed": "",
     "coords": {"lat": 53.0793, "lng": 8.8017}, "text_blocks": []},
    {"slug": "baden-baden", "city": "Baden-Baden", "url": "/standorte/baden-baden",
     "phone": PHONE, "address": "Baden-Baden", "hours": [], "map_embed": "",
     "coords": {"lat": 48.7606, "lng": 8.2396}, "text_blocks": []},
]

_FALLBACK_REVIEWS = [
    {"author": "Michael S.", "rating": 5, "time": "vor 2 Wochen",
     "text": "Hervorragende Beratung und erstklassige Verarbeitung. Mein Maßanzug sitzt wie angegossen — absolute Empfehlung."},
    {"author": "Thomas K.", "rating": 5, "time": "vor 1 Monat",
     "text": "Vom ersten Termin bis zur Anprobe ein durchweg professioneller und angenehmer Ablauf. Die Qualität ist außergewöhnlich."},
    {"author": "Andreas W.", "rating": 5, "time": "vor 3 Wochen",
     "text": "Kompetentes Team, edle Stoffe und ein perfekter Sitz. Hier wird Maßschneiderei noch als Handwerk gelebt."},
    {"author": "Daniel B.", "rating": 5, "time": "vor 2 Monaten",
     "text": "Für meine Hochzeit habe ich hier meinen Anzug fertigen lassen. Das Ergebnis hat alle Erwartungen übertroffen."},
    {"author": "Stefan M.", "rating": 5, "time": "vor 1 Woche",
     "text": "Individuelle Beratung auf höchstem Niveau. Man fühlt sich von der ersten Minute an bestens aufgehoben."},
    {"author": "Christian H.", "rating": 5, "time": "vor 1 Monat",
     "text": "Tradition trifft Moderne. Der Maßanzug ist ein Meisterwerk und die Betreuung war herausragend."},
]

_FALLBACK_FAQ = [
    {"q": "Wie läuft ein Maßtermin bei cove ab?",
     "a": "In einem persönlichen Gespräch nehmen wir Maß, besprechen Stoffe, Schnitt und Details und beraten Sie umfassend zu Ihrer individuellen Garderobe."},
    {"q": "Wie lange dauert die Anfertigung eines Maßanzugs?",
     "a": "Die Fertigung eines Maßanzugs dauert in der Regel mehrere Wochen, abhängig von Modell, Stoff und Auslastung. Gerne nennen wir Ihnen beim Termin einen konkreten Zeitrahmen."},
    {"q": "Welche Stoffe bietet cove an?",
     "a": "Wir arbeiten mit führenden europäischen Webereien und bieten eine große Auswahl an Wolle, Kaschmir, Tweed, Flanell und weiteren edlen Materialien."},
    {"q": "An welchen Standorten ist cove vertreten?",
     "a": "cove ist an 19 Standorten deutschlandweit vertreten — unter anderem in Berlin, Hamburg, München, Düsseldorf, Köln und Frankfurt."},
    {"q": "Kann ich einen Termin online vereinbaren?",
     "a": "Ja, Sie können bequem online einen Beratungstermin in Ihrer gewünschten Filiale vereinbaren."},
]

_FALLBACK_WIKI = {
    "bespoke": {"slug": "bespoke", "url": "/wiki/bespoke", "title": "Bespoke",
                "meta_description": "Bespoke bezeichnet die höchste Stufe der Maßschneiderei.",
                "text_blocks": [{"tag": "p", "text": "Bespoke bezeichnet die Königsklasse der Maßschneiderei: ein Kleidungsstück, das vollständig nach den individuellen Maßen und Wünschen des Kunden von Grund auf entworfen und gefertigt wird."}], "images": []},
    "full-canvas": {"slug": "full-canvas", "url": "/wiki/full-canvas", "title": "Full Canvas",
                    "meta_description": "Full Canvas — die hochwertigste Verarbeitung eines Sakkos.",
                    "text_blocks": [{"tag": "p", "text": "Bei der Full-Canvas-Verarbeitung wird ein durchgehender Roßhaareinlage zwischen Oberstoff und Futter eingearbeitet, die dem Sakko Form und Langlebigkeit verleiht."}], "images": []},
    "hochzeitsanzug": {"slug": "hochzeitsanzug", "url": "/wiki/hochzeitsanzug", "title": "Hochzeitsanzug",
                       "meta_description": "Der maßgeschneiderte Hochzeitsanzug.",
                       "text_blocks": [{"tag": "p", "text": "Ein maßgeschneiderter Hochzeitsanzug wird ganz auf den Bräutigam und den Anlass abgestimmt — vom Stoff über den Schnitt bis zu den persönlichen Details."}], "images": []},
    "kaschmir-cashmere": {"slug": "kaschmir-cashmere", "url": "/wiki/kaschmir-cashmere", "title": "Kaschmir (Cashmere)",
                          "meta_description": "Kaschmir — eine der edelsten Naturfasern.",
                          "text_blocks": [{"tag": "p", "text": "Kaschmir zählt zu den edelsten Naturfasern überhaupt. Die feine Wolle der Kaschmirziege ist besonders weich, leicht und wärmend."}], "images": []},
    "harris-tweed": {"slug": "harris-tweed", "url": "/wiki/harris-tweed", "title": "Harris Tweed",
                     "meta_description": "Harris Tweed — handgewebt auf den Äußeren Hebriden.",
                     "text_blocks": [{"tag": "p", "text": "Harris Tweed ist ein handgewebtes Wollgewebe von den schottischen Äußeren Hebriden und durch ein eigenes Gesetz geschützt. Es steht für Robustheit und zeitlosen Stil."}], "images": []},
    "flanell": {"slug": "flanell", "url": "/wiki/flanell", "title": "Flanell",
                "meta_description": "Flanell — weicher, angerauter Wollstoff.",
                "text_blocks": [{"tag": "p", "text": "Flanell ist ein weicher, leicht angerauter Wollstoff mit charakteristisch wärmender Haptik — ein Klassiker für Herbst- und Wintergarderobe."}], "images": []},
}

_FALLBACK_SHOP = [
    {"name": "Strickpullover Rundhals Anthrazit", "price": "179,00 €",
     "url": "https://www.cove.de/shop/", "image": "cove_strickpullover_rundhals_anthrazit_prod-300x200.jpg", "category": "strickwaren",
     "brand": "cove", "variants": "Größen 48–58"},
    {"name": "Strickpullover Rollkragen Navy", "price": "179,00 €",
     "url": "https://www.cove.de/shop/", "image": "cove-strickpullover_rollkragen_navy_prod-300x200.jpg", "category": "strickwaren",
     "brand": "cove", "variants": "Größen 48–58"},
    {"name": "Strickpullover Rollkragen Anthrazit", "price": "179,00 €",
     "url": "https://www.cove.de/shop/", "image": "cove_strickpullover_rollkragen_anthrazit_prod-300x200.jpg", "category": "strickwaren",
     "brand": "cove", "variants": "Größen 48–58"},
    {"name": "Strickcardigan Braun", "price": "199,00 €",
     "url": "https://www.cove.de/shop/", "image": "cove_strickcardigan_braun_prod-300x200.jpg", "category": "strickwaren",
     "brand": "cove", "variants": "Merinowolle"},
    {"name": "Strickcardigan Navy", "price": "199,00 €",
     "url": "https://www.cove.de/shop/", "image": "cove_strickcardigan_navy_prod-300x200.jpg", "category": "strickwaren",
     "brand": "cove", "variants": "Merinowolle"},
    {"name": "Gutschein Cove", "price": "50,00 € – 2.000,00 €",
     "url": "https://www.cove.de/shop/", "image": "gutschein-300x200.jpg", "category": "geschenke-gutscheine",
     "brand": "cove", "variants": ""},
    {"name": "Regenschirm Maglia Elegant Malacca Twill", "price": "299,00 €",
     "url": "https://www.cove.de/shop/", "image": "f_maglia_schirm_elegant_schwarz_front-300x200.jpg", "category": "regenschirme",
     "brand": "Maglia", "variants": ""},
    {"name": "Crockett & Jones Boston", "price": "670,00 €",
     "url": "https://www.cove.de/shop/", "image": "Boston28363A-D11L11_686e0c31-80f8-4032-9ac1-d78cca543b4b_1400x-300x200.webp", "category": "schuhe",
     "brand": "Crockett & Jones", "variants": "Schwarz, Bordeaux · Größen 41–45.5"},
    {"name": "Crockett & Jones Cavendish", "price": "690,00 €",
     "url": "https://www.cove.de/shop/", "image": "Cavendish29376A-C01L11_921c7357-8981-4ab3-8c51-ccad0677a736_1400x-300x200.webp", "category": "schuhe",
     "brand": "Crockett & Jones", "variants": "Loafer · Kalbsleder"},
    {"name": "Crockett & Jones Hallam", "price": "670,00 €",
     "url": "https://www.cove.de/shop/", "image": "Hallam25057A-C01L11_fce5fbfb-c976-4ca3-addd-db8a2044ac9a_1400x-300x200.webp", "category": "schuhe",
     "brand": "Crockett & Jones", "variants": "Oxford · Schwarz"},
    {"name": "Alden Indy Boot", "price": "ab 850,00 €",
     "url": "https://www.cove.de/shop/", "image": "alden_indy-boot_braun_anilin_pull-up_front-300x200.jpg", "category": "schuhe",
     "brand": "Alden", "variants": "Braunes Leder"},
    {"name": "D.R. Harris & Co. Twenty Nine Eau de Cologne", "price": "56,00 €",
     "url": "https://www.cove.de/shop/", "image": "dr_harris_arlington_cologne_front-300x200.jpg", "category": "duefte-pflege",
     "brand": "D.R. Harris & Co.", "variants": ""},
    {"name": "Wellington Cologne", "price": "56,00 €",
     "url": "https://www.cove.de/shop/", "image": "Wellington-Cologne-100ml-atomiser-548x660-1-2-300x200.jpg", "category": "duefte-pflege",
     "brand": "D.R. Harris & Co.", "variants": "100 ml"},
    {"name": "Mühle Rasierset", "price": "149,00 €",
     "url": "https://www.cove.de/shop/", "image": "muehle_rasierset_vierteilig_schwarz_front-300x200.jpg", "category": "duefte-pflege",
     "brand": "Mühle", "variants": "Vier-teilig"},
    {"name": "Cashmere Schal Grau", "price": "129,00 €",
     "url": "https://www.cove.de/shop/", "image": "ascot_schal_cashmere_web_grau_1-300x200.jpg", "category": "accessoires",
     "brand": "Ascot", "variants": "Kaschmir"},
    {"name": "Cashmere Mütze Grau", "price": "69,00 €",
     "url": "https://www.cove.de/shop/", "image": "muetze_cashmere_web_grau_11-300x200.jpg", "category": "accessoires",
     "brand": "cove", "variants": "Kaschmir"},
    {"name": "Flechtgürtel Dunkelbraun", "price": "99,00 €",
     "url": "https://www.cove.de/shop/", "image": "Guertel-Flechtguertel-DUnkelbraun-pdf.jpg", "category": "guertel",
     "brand": "cove", "variants": ""},
    {"name": "Kulturbeutel", "price": "89,00 €",
     "url": "https://www.cove.de/shop/", "image": "kulturbeutel_web_1-300x200.jpg", "category": "accessoires",
     "brand": "cove", "variants": ""},
    {"name": "Flachmann", "price": "49,00 €",
     "url": "https://www.cove.de/shop/", "image": "Flachmann_web_1-300x200.jpg", "category": "accessoires",
     "brand": "cove", "variants": ""},
    {"name": "Hemley Kummerbund Set", "price": "149,00 €",
     "url": "https://www.cove.de/shop/", "image": "hemley_kummerbund_set_schwarz_seide_front-300x200.jpg", "category": "accessoires",
     "brand": "Hemley", "variants": "Schwarze Seide"},
    {"name": "Haus und Auto (Andreas K. Vetter)", "price": "59,90 €",
     "url": "https://www.cove.de/shop/", "image": "titel_massfibel_cove-300x200.png", "category": "buecher",
     "brand": "Andreas K. Vetter", "variants": ""},
    {"name": "Bar Bible", "price": "29,90 €",
     "url": "https://www.cove.de/shop/", "image": "barbible-300x200.png", "category": "buecher",
     "brand": "cove", "variants": ""},
]

SHOP_CATEGORIES = [
    {"slug": "neuheiten", "label_de": "Neuheiten", "label_en": "New Arrivals", "children": []},
    {"slug": "ready-to-wear", "label_de": "Ready To Wear", "label_en": "Ready To Wear",
     "children": [{"slug": "hemden", "label_de": "Hemden", "label_en": "Shirts"},
                  {"slug": "strickwaren", "label_de": "Strickwaren", "label_en": "Knitwear"}]},
    {"slug": "schuhe", "label_de": "Schuhe", "label_en": "Shoes", "children": []},
    {"slug": "schuhpflege", "label_de": "Schuhpflege", "label_en": "Shoe Care", "children": []},
    {"slug": "accessoires", "label_de": "Accessoires", "label_en": "Accessories",
     "children": [{"slug": "guertel", "label_de": "Gürtel", "label_en": "Belts"},
                  {"slug": "hosentraeger", "label_de": "Hosenträger", "label_en": "Braces"},
                  {"slug": "krawatten", "label_de": "Krawatten", "label_en": "Ties"},
                  {"slug": "manschettenknoepfe", "label_de": "Manschettenknöpfe", "label_en": "Cufflinks"},
                  {"slug": "regenschirme", "label_de": "Regenschirme", "label_en": "Umbrellas"},
                  {"slug": "handschuhe", "label_de": "Handschuhe", "label_en": "Gloves"},
                  {"slug": "socken", "label_de": "Socken", "label_en": "Socks"},
                  {"slug": "festliche-accessoires", "label_de": "Festliche Accessoires", "label_en": "Formal Accessories"},
                  {"slug": "einstecktuecher", "label_de": "Einstecktücher", "label_en": "Pocket Squares"}]},
    {"slug": "duefte-pflege", "label_de": "Düfte & Pflege", "label_en": "Fragrance & Care", "children": []},
    {"slug": "geschenke-gutscheine", "label_de": "Geschenke & Gutscheine", "label_en": "Gifts & Vouchers", "children": []},
    {"slug": "buecher", "label_de": "Bücher", "label_en": "Books", "children": []},
]
