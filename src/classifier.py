from __future__ import annotations

import json
import re

from openai import AsyncOpenAI
from trafilatura import extract as extract_text
from trafilatura import extract_metadata, fetch_url

from config import Settings
from models import LinkData

CATEGORIES = [
    "code",
    "documentation",
    "video",
    "article",
    "social",
    "news",
    "tool",
    "design",
    "learning",
    "research",
    "reference",
    "other",
]

SYSTEM_PROMPT = """You are an expert web content classifier and metadata extractor. Your task is to analyze webpage data and produce structured, accurate categorization.

# Your Role
You analyze URLs and their content to:
1. Determine the most accurate category from a predefined list
2. Generate clean, human-readable metadata
3. Provide useful context about why the resource is valuable

# Categories (in order of specificity - choose the MOST specific match)

## Primary Content Types
- **code**: Source code repositories, code snippets, GitHub/GitLab projects, programming libraries, SDKs, frameworks, open-source projects
- **documentation**: Official API docs, technical references, specification docs, man pages, SDK documentation, library references
- **video**: YouTube, Vimeo, video tutorials, recorded talks, screencasts, video courses
- **article**: Blog posts, opinion pieces, written tutorials, how-to guides, technical write-ups, medium posts
- **news**: Breaking news, current events, press releases, announcements, changelogs, release notes

## Resource Types
- **tool**: Web applications, SaaS products, utilities, online calculators, converters, generators, productivity apps, developer tools
- **design**: UI kits, design systems, Figma/Sketch resources, icon packs, color palettes, typography, mockups, visual assets
- **learning**: Courses, educational platforms, interactive tutorials, bootcamps, certifications, structured learning paths
- **research**: Academic papers, whitepapers, case studies, technical reports, empirical studies, data analysis
- **reference**: Cheatsheets, quick references, comparison tables, awesome lists, curated collections, glossaries

## Social & Other
- **social**: Social media profiles, Reddit threads, Twitter/X posts, Discord servers, community forums, discussions
- **other**: Content that genuinely doesn't fit any above category

# Classification Rules
1. Prioritize the PRIMARY purpose of the page, not secondary elements
2. GitHub repos with code → "code", not "documentation" even if they have READMEs
3. Tutorial videos → "video", not "learning" (video format takes precedence)
4. Interactive coding tutorials → "learning" (learning takes precedence over tool)
5. News about tech/code → "news", not "code"
6. API reference pages → "documentation", not "reference"
7. Curated "awesome" lists → "reference"

# Output Requirements
Respond with ONLY a valid JSON object (no markdown, no explanation):
{
  "title": "Clean title, max 100 chars, no site name suffix",
  "description": "Concise summary of value proposition, max 200 chars",
  "site_name": "Publisher, product, or platform name",
  "category": "exactly one category from the list above",
  "context": "1-2 sentences: who benefits and why this is useful"
}"""

USER_PROMPT = """Analyze this webpage and categorize it:

URL: {url}
Domain: {domain}
Title: {raw_title}
Meta Description: {raw_desc}
Site Name: {raw_site}

--- Page Content (excerpt) ---
{content}
---

Return the JSON classification."""


class Classifier:
    def __init__(self, settings: Settings):
        self._client = AsyncOpenAI(
            api_key=settings.openrouter_api_key, base_url=settings.openrouter_base_url
        )
        self._model = settings.openrouter_model

    async def analyze(self, url: str, domain: str) -> LinkData:
        raw_title, raw_desc, raw_site, image_url, content = self._fetch_and_extract(url)

        try:
            data = await self._call_llm(
                url, domain, raw_title, raw_desc, raw_site, content
            )
        except Exception:
            data = {}

        return LinkData(
            url=url,
            title=data.get("title") or raw_title,
            description=data.get("description") or raw_desc,
            site_name=data.get("site_name") or raw_site,
            image_url=image_url,
            category=data.get("category")
            if data.get("category") in CATEGORIES
            else "other",
            context=data.get("context"),
        )

    def _fetch_and_extract(
        self, url: str
    ) -> tuple[str | None, str | None, str | None, str | None, str | None]:
        html = fetch_url(url)
        if not html:
            return None, None, None, None, None

        meta = extract_metadata(html, default_url=url)
        content = extract_text(
            html,
            url=url,
            include_comments=False,
            include_links=False,
            include_images=False,
        )

        title = getattr(meta, "title", None) if meta else None
        desc = getattr(meta, "description", None) if meta else None
        site = getattr(meta, "sitename", None) if meta else None
        image = getattr(meta, "image", None) if meta else None

        return title, desc, site, image, content

    async def _call_llm(
        self,
        url: str,
        domain: str,
        raw_title: str | None,
        raw_desc: str | None,
        raw_site: str | None,
        content: str | None,
    ) -> dict:
        user_message = USER_PROMPT.format(
            url=url,
            domain=domain,
            raw_title=raw_title or "(not available)",
            raw_desc=raw_desc or "(not available)",
            raw_site=raw_site or "(not available)",
            content=(content[:2500] + "\n... [truncated]")
            if content and len(content) > 2500
            else (content or "(no content extracted)"),
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=400,
            temperature=0.1,
        )

        return self._parse_json(response.choices[0].message.content or "")

    def _parse_json(self, content: str) -> dict:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        return {}
