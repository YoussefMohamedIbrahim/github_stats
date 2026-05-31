import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("Critical: GITHUB_TOKEN environment variable is missing.")

GRAPHQL_URL = "https://api.github.com/graphql"

# Comma-separated list of language names to exclude from the language card.
EXCLUDED_LANGUAGES = {
    item.strip().lower()
    for item in os.getenv("EXCLUDED_LANGUAGES", "").split(",")
    if item.strip()
}


def _read_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


# Display limits to prevent text overflow inside the SVG cards.
MAX_LANGUAGES = _read_int_env("MAX_LANGUAGES", 5)
MAX_RECENT_REPOS = _read_int_env("MAX_RECENT_REPOS", 5)