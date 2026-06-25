# COVE Website Rebuild — models/location.py — location helper
"""
Locations are sourced from scraped_content/locations.json (see content.py) rather
than the database, since they are static editorial content. This module exposes a
lightweight dataclass-style wrapper for any code that prefers an object API.
"""

from dataclasses import dataclass, field


@dataclass
class Location:
    slug: str
    city: str
    url: str = ""
    phone: str = ""
    address: str = ""
    hours: list = field(default_factory=list)
    map_embed: str = ""
    coords: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data):
        return cls(
            slug=data.get("slug", ""),
            city=data.get("city", ""),
            url=data.get("url", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            hours=data.get("hours", []),
            map_embed=data.get("map_embed", ""),
            coords=data.get("coords") or {},
        )
