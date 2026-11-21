"""Settings read from the environment, optionally seeded by a local .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_BASE_URL = "http://127.0.0.1:11434/v1"
DEFAULT_MODEL = "qwen3:14b"

# OpenAI-compatible clients reject an empty key; local servers never look at it.
PLACEHOLDER_API_KEY = "ollama"

ENV_BASE_URL = "SCISCITOR_BASE_URL"
ENV_API_KEY = "SCISCITOR_API_KEY"
ENV_MODEL = "SCISCITOR_MODEL"


@dataclass(frozen=True)
class Config:
    """Everything needed to talk to one chat endpoint."""

    base_url: str
    api_key: str
    model: str


def load_config(env_file: Path | None = None) -> Config:
    """Build a Config from the environment.

    Variables already present in the environment win over the .env file, so a
    shell override never requires editing the file.
    """
    load_dotenv(env_file)

    base_url = os.environ.get(ENV_BASE_URL, "").strip() or DEFAULT_BASE_URL
    api_key = os.environ.get(ENV_API_KEY, "").strip() or PLACEHOLDER_API_KEY
    model = os.environ.get(ENV_MODEL, "").strip() or DEFAULT_MODEL
    return Config(base_url=base_url, api_key=api_key, model=model)
