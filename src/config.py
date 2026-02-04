from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    data_path: str = "data/links.json"
    timeout_s: int = 12
    max_concurrency: int = 8
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            data_path=os.getenv("LINKREC_DATA_PATH", "data/links.json"),
            timeout_s=int(os.getenv("LINKREC_TIMEOUT", "12")),
            max_concurrency=int(os.getenv("LINKREC_MAX_CONCURRENCY", "8")),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            openrouter_base_url=os.getenv(
                "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
            ),
            openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        )
