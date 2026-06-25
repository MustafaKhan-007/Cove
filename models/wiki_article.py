# COVE Website Rebuild — models/wiki_article.py — wiki article helper
"""
Wiki articles are stored as scraped JSON (scraped_content/wiki_articles.json) and
served via content.py. This wrapper documents the expected shape and offers a
convenience constructor; persisting articles to the DB is left as a future TODO.
"""

from dataclasses import dataclass, field


@dataclass
class WikiArticle:
    slug: str
    title: str
    url: str = ""
    meta_description: str = ""
    text_blocks: list = field(default_factory=list)
    images: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, data):
        return cls(
            slug=data.get("slug", ""),
            title=data.get("title", ""),
            url=data.get("url", ""),
            meta_description=data.get("meta_description", ""),
            text_blocks=data.get("text_blocks", []),
            images=data.get("images", []),
        )
