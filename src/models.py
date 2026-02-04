from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LinkData:
    url: str
    title: str | None = None
    description: str | None = None
    site_name: str | None = None
    image_url: str | None = None
    category: str = "other"
    context: str | None = None
