# COVE Website Rebuild — blueprints/main/routes.py — homepage, about, locations, products, faq
from flask import render_template, abort, redirect

import content
from . import main

# Map of clean product routes -> scraped product key + display metadata.
PRODUCT_ROUTE_MAP = {
    "massanzug": {"key": "massanzug", "title_de": "Maßanzug", "title_en": "Bespoke Suit"},
    "masshemd": {"key": "masshemd", "title_de": "Maßhemd", "title_en": "Bespoke Shirt"},
    "hochzeit": {"key": "hochzeit", "title_de": "Hochzeit", "title_en": "Wedding"},
    "sakko": {"key": "sakko", "title_de": "Maßsakko", "title_en": "Bespoke Jacket"},
    "mantel": {"key": "mantel", "title_de": "Maßmantel", "title_en": "Bespoke Coat"},
    "schuhe": {"key": "schuhe", "title_de": "Schuhwerk", "title_en": "Shoes"},
    "cove-custom-shirt": {"key": "cove-custom-shirt", "title_de": "Hemden Konfigurator", "title_en": "Shirt Configurator"},
    "herrenschuh-selber-designen": {"key": "herrenschuh-designen", "title_de": "Schuh Konfigurator", "title_en": "Shoe Configurator"},
}


@main.route("/")
def index():
    return render_template(
        "main/index.html",
        homepage=content.homepage(),
        services=content.SERVICES,
        badges=content.BADGES,
        slides=content.slide_images(),
        reviews=content.reviews(),
        about=content.about(),
        locations=content.locations(),
        wiki_featured=[content.wiki_article(s) for s in
                       ("bespoke", "full-canvas", "hochzeitsanzug",
                        "kaschmir-cashmere", "harris-tweed", "flanell")
                       if content.wiki_article(s)],
        google_reviews_link=content.GOOGLE_REVIEWS_LINK,
        phone=content.PHONE,
    )


@main.route("/ueber-uns")
def about_page():
    return render_template(
        "main/about.html",
        about=content.about(),
        badges=content.BADGES,
        phone=content.PHONE,
    )


@main.route("/faq")
@main.route("/f-a-q")
def faq_page():
    return render_template("main/faq.html", faqs=content.faq())


@main.route("/standorte")
def locations_page():
    return render_template(
        "main/locations.html",
        locations=content.locations(),
        phone=content.PHONE,
    )


@main.route("/standorte/<slug>")
def location_detail(slug):
    loc = content.location(slug)
    if not loc:
        abort(404)
    return render_template(
        "main/location_detail.html",
        loc=loc,
        locations=content.locations(),
        phone=content.PHONE,
    )


@main.route("/<route>")
def product_page(route):
    meta = PRODUCT_ROUTE_MAP.get(route)
    if not meta:
        abort(404)
    prod = content.product(meta["key"]) or {}
    return render_template(
        "main/product.html",
        route=route,
        meta=meta,
        product=prod,
        phone=content.PHONE,
    )
