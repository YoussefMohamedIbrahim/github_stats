# GitHub Stats SVGs

Generate modern, themed GitHub profile SVG cards for your overall stats, top languages, and recent work. 

**✨ What makes this different?** This generator uses advanced GraphQL queries to track your **personal commit timestamps**. Your "Recent Work" card will strictly surface repositories based on when *you* last committed to them, preventing highly active open-source projects from hijacking your recent list!

## Usage: GitHub Actions (Recommended)

The easiest way to generate and automatically update your stats is by using the built-in GitHub Action. 

1. Create a Personal Access Token (PAT) with `read:user` access.
2. Add the token as a Repository Secret in your profile README repository (e.g., `STATS_TOKEN`).
3. Create a workflow file in your repository at `.github/workflows/update-stats.yml`:

```yaml
name: Update GitHub Stats

on:
  schedule:
    - cron: "0 0 * * *" # Runs daily at midnight UTC
  workflow_dispatch:    # Allows manual triggering

jobs:
  generate-stats:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate SVGs
        uses: youssefmohamedibrahim/github_stats@main
        with:
          token: ${{ secrets.STATS_TOKEN }}
          username: torvalds # Replace with your GitHub username
          
          # Optional configurations (showing defaults):
          # output_dir: 'images'
          # themes: 'dark,light'
          # exclude_languages: ''

      - name: Commit and push changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add images/
          git commit -m "chore: update GitHub stats SVGs" || echo "No changes to commit"
          git push
```

By default, the Action will save the SVGs into an `images/` directory in your repository.

## Generated Files

Depending on the themes you select, the action will generate the following files:

- `github-stats-dark.svg` / `github-stats-light.svg`
- `github-languages-dark.svg` / `github-languages-light.svg`
- `github-recent-dark.svg` / `github-recent-light.svg`

## Embedding in your README

You can use GitHub's native HTML picture tags to automatically switch between light and dark themes based on the viewer's system preferences.

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/github-stats-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="images/github-stats-light.svg">
  <img alt="GitHub stats" src="images/github-stats-light.svg">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/github-languages-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="images/github-languages-light.svg">
  <img alt="GitHub Top Languages" src="images/github-languages-light.svg">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/github-recent-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="images/github-recent-light.svg">
  <img alt="GitHub Recent Work" src="images/github-recent-light.svg">
</picture>
```

---

## Local Development / Manual Usage

If you prefer to run the script manually or want to test changes locally:

### Setup
1. Create a `.env` file in the root directory:
```text
GITHUB_TOKEN=your_personal_access_token_here
```

### Installation & Execution
Run from source:
```bash
python -m github_stats torvalds
```

Or install locally:
```bash
pip install -e .
github-stats torvalds
```

### CLI Options
- `username` positional argument, e.g. `torvalds`.
- `--output-dir` where SVGs are written (default: `output`).
- `--themes` comma-separated list, e.g. `dark,light`.
- `--exclude-languages` comma-separated list, e.g. `HTML,CSS`.
- `--max-languages` limit number of language rows (default: `5`).
- `--max-recent` limit number of recent repos (default: `5`).

### Local Environment Variables
- `EXCLUDED_LANGUAGES` comma-separated list, e.g. `HTML,CSS`.
- `MAX_LANGUAGES` default 5.
- `MAX_RECENT_REPOS` default 5.
