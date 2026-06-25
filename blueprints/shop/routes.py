# COVE Website Rebuild — blueprints/shop/routes.py — shop index, category, product
#
# NOTE: This rebuild does not reimplement a full e-commerce / checkout backend.
# Product "buy" actions redirect to the original cove.de shop URLs.
# TODO: Integrate a real checkout (cart, payment, inventory) for production.

from flask import render_template, abort

import content
from . import shop


def _products_for(category=None):
    items = content.shop_products()
    if category and category != "neuheiten":
        allowed = {category}
        parent = next((c for c in content.SHOP_CATEGORIES if c["slug"] == category), None)
        if parent:
            allowed.update(child["slug"] for child in parent.get("children", []))
        items = [p for p in items if p.get("category") in allowed]
    return items


@shop.route("/")
def index():
    return render_template(
        "shop/index.html",
        categories=content.SHOP_CATEGORIES,
        products=_products_for(),
        active_category=None,
    )


@shop.route("/produkt-kategorie/<slug>")
def category(slug):
    cat = next((c for c in content.SHOP_CATEGORIES if c["slug"] == slug), None)
    if not cat:
        # also allow child category slugs
        for c in content.SHOP_CATEGORIES:
            child = next((ch for ch in c["children"] if ch["slug"] == slug), None)
            if child:
                cat = child
                break
    if not cat:
        abort(404)
    return render_template(
        "shop/category.html",
        categories=content.SHOP_CATEGORIES,
        products=_products_for(slug),
        active_category=slug,
        category=cat,
    )


@shop.route("/produkt/<path:name>")
def product(name):
    items = content.shop_products()
    prod = next((p for p in items if p.get("name") == name), None)
    if not prod:
        abort(404)
    return render_template(
        "shop/product.html",
        categories=content.SHOP_CATEGORIES,
        product=prod,
    )
