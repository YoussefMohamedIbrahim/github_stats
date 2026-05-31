import os
from typing import Set
from dotenv import load_dotenv

load_dotenv()

GRAPHQL_URL = "https://api.github.com/graphql"


def get_github_token() -> str:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("Critical: GITHUB_TOKEN environment variable is missing.")
    return token


def _read_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _read_csv_env(name: str) -> Set[str]:
    raw = os.getenv(name, "")
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


EXCLUDED_LANGUAGES = _read_csv_env("EXCLUDED_LANGUAGES")
MAX_LANGUAGES = _read_int_env("MAX_LANGUAGES", 5)
MAX_RECENT_REPOS = _read_int_env("MAX_RECENT_REPOS", 5)
