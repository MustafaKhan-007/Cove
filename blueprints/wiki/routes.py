# COVE Website Rebuild — blueprints/wiki/routes.py — wiki index + article pages
#
# HOW TO ADD MORE WIKI ARTICLES
# -----------------------------
# The wiki is a first draft. The full A–Z index is loaded from
# scraped_content/wiki_index.json, but only the 6 seed articles in
# scraped_content/wiki_articles.json have full body content.
#
# To fully populate another entry:
#   1. Add its slug to WIKI_SEEDS in scripts/scrape_cove.py and re-run the scraper
#      (or manually add an object to scraped_content/wiki_articles.json with keys:
#       slug, url, title, meta_description, text_blocks[{tag,text}], images[]).
#   2. It will then render at /wiki/<slug> automatically.
# Entries without a full article fall back to a link to the original cove.de page.

import string

from flask import render_template, abort, redirect

import content
from . import wiki


@wiki.route("/")
def index():
    entries = content.wiki_index()
    # group alphabetically by first letter
    groups = {}
    for e in sorted(entries, key=lambda x: x.get("title", "").upper()):
        title = e.get("title", "")
        if not title:
            continue
        letter = title[0].upper()
        if letter not in string.ascii_uppercase:
            letter = "#"
        groups.setdefault(letter, []).append(e)
    available_letters = sorted(groups.keys())
    seeded = set(content.wiki_articles().keys())
    return render_template(
        "wiki/index.html",
        groups=groups,
        letters=available_letters,
        seeded=seeded,
    )


@wiki.route("/<slug>")
def article(slug):
    art = content.wiki_article(slug)
    if not art:
        # not seeded -> send the visitor to the original page
        entry = next((e for e in content.wiki_index() if e.get("slug") == slug), None)
        if entry and entry.get("url"):
            return redirect(entry["url"])
        abort(404)
    # related = three other seeded articles
    related = [a for s, a in content.wiki_articles().items() if s != slug][:3]
    return render_template("wiki/article.html", article=art, related=related)
