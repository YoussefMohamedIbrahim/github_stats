# GitHub Stats SVGs

Generate modern, themed GitHub profile SVG cards for stats, languages, and recent work.

## Setup

1. Create a GitHub token with `read:user` access.
2. Add it to a `.env` file:

```text
GITHUB_TOKEN=your_token_here
```

## Usage

Run from source:

```bash
python -m github_stats torvalds
```

Or install locally:

```bash
pip install -e .
github-stats torvalds
```

Generated files (in `output/` by default):

- `github-stats-dark.svg`
- `github-stats-light.svg`
- `github-languages-dark.svg`
- `github-languages-light.svg`
- `github-recent-dark.svg`
- `github-recent-light.svg`

## Options

- `username` positional argument, e.g. `torvalds`.
- `--output-dir` where SVGs are written.
- `--themes` comma-separated list, e.g. `dark,light`.
- `--exclude-languages` comma-separated list, e.g. `HTML,CSS`.
- `--max-languages` limit number of language rows.
- `--max-recent` limit number of recent repos.

## Environment Variables

- `EXCLUDED_LANGUAGES` comma-separated list, e.g. `HTML,CSS`.
- `MAX_LANGUAGES` default 5.
- `MAX_RECENT_REPOS` default 5.

## GitHub README embedding

Use GitHub theme selectors for the light/dark variants:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="github-stats-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="github-stats-light.svg">
  <img alt="GitHub stats" src="github-stats-light.svg">
</picture>
```
