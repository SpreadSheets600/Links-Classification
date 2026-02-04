from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from models import LinkData
from utils import get_domain, normalize_url


class LinkStore:
    def __init__(self, path: str = "data/links.json"):
        self.path = path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.path):
            self._save({"links": [], "next_id": 1})

    def _load(self) -> dict[str, Any]:
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict[str, Any]):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def exists(self, url: str) -> bool:
        normalized = normalize_url(url)
        data = self._load()
        return any(link.get("normalized_url") == normalized for link in data["links"])

    def save(self, link: LinkData) -> dict[str, Any] | None:
        normalized = normalize_url(link.url)
        if self.exists(link.url):
            return None

        data = self._load()
        record = {
            "id": data["next_id"],
            "url": link.url,
            "normalized_url": normalized,
            "domain": get_domain(link.url),
            "title": link.title,
            "description": link.description,
            "site_name": link.site_name,
            "image_url": link.image_url,
            "category": link.category,
            "context": link.context,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data["links"].append(record)
        data["next_id"] += 1
        self._save(data)
        return record

    def get_all(self) -> list[dict[str, Any]]:
        return self._load()["links"]
