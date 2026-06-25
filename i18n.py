# COVE Website Rebuild — i18n.py — server-side DE/EN translation helpers
import json
from functools import lru_cache
from pathlib import Path

from flask import g, request

SUPPORTED_LANGUAGES = ("de", "en")
DEFAULT_LANGUAGE = "de"

TRANSLATION_DIR = Path(__file__).resolve().parent / "static" / "translations"


@lru_cache(maxsize=None)
def load_translations(lang):
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    path = TRANSLATION_DIR / f"{lang}.json"
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve_language():
    query_lang = (request.args.get("lang") or "").lower()
    cookie_lang = (request.cookies.get("cove_lang") or "").lower()
    if query_lang in SUPPORTED_LANGUAGES:
        return query_lang
    if cookie_lang in SUPPORTED_LANGUAGES:
        return cookie_lang
    return DEFAULT_LANGUAGE


def get_nested(mapping, dotted_key):
    current = mapping
    for part in dotted_key.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        if isinstance(current, list) and part.isdigit():
            idx = int(part)
            if 0 <= idx < len(current):
                current = current[idx]
                continue
        return None
    return current


def translate(key, default=None, **kwargs):
    lang = getattr(g, "lang", DEFAULT_LANGUAGE)
    value = get_nested(load_translations(lang), key)
    if value is None and lang != DEFAULT_LANGUAGE:
        value = get_nested(load_translations(DEFAULT_LANGUAGE), key)
    if value is None:
        value = default if default is not None else key
    if kwargs and isinstance(value, str):
        try:
            value = value.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return value


def with_lang_cookie(response):
    lang = getattr(g, "lang", DEFAULT_LANGUAGE)
    response.set_cookie("cove_lang", lang, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return response
