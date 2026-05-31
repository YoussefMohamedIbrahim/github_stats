import argparse
import os
from typing import List, Optional, Set
from .github_api import fetch_github_stats
from .svg_generator import render_svgs


def _parse_csv(value: Optional[str]) -> Optional[Set[str]]:
    if value is None:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        return set()
    return {item.lower() for item in items}


def _parse_themes(value: Optional[str]) -> List[str]:
    if not value:
        return ["dark", "light"]
    return [item.strip() for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate GitHub stats SVG cards.")
    parser.add_argument(
        "username",
        nargs="?",
        default=os.getenv("GITHUB_USERNAME", "torvalds"),
        help="GitHub username to fetch",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to write SVGs to",
    )
    parser.add_argument(
        "--themes",
        default="dark,light",
        help="Comma-separated list of themes to render",
    )
    parser.add_argument(
        "--exclude-languages",
        default=None,
        help="Comma-separated list of languages to exclude",
    )
    parser.add_argument(
        "--max-languages",
        type=int,
        default=None,
        help="Maximum number of languages to display",
    )
    parser.add_argument(
        "--max-recent",
        type=int,
        default=None,
        help="Maximum number of recent repositories to display",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    excluded = _parse_csv(args.exclude_languages)
    themes = _parse_themes(args.themes)

    print(f"Fetching GitHub data for {args.username}...")
    try:
        stats = fetch_github_stats(
            args.username,
            excluded_languages=excluded,
            max_languages=args.max_languages,
            max_recent_repos=args.max_recent,
        )
        print("Data fetched successfully. Generating SVGs...")
        outputs = render_svgs(stats, output_dir=args.output_dir, themes=themes)
        for output_path in outputs:
            print(f"Generated: {output_path}")
        return 0
    except Exception as exc:
        print(f"Error occurred: {exc}")
        return 1
