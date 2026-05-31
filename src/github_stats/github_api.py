import requests
from typing import Dict, Any, List, Optional, Set
from .config import (
    GRAPHQL_URL,
    EXCLUDED_LANGUAGES,
    MAX_LANGUAGES,
    MAX_RECENT_REPOS,
    get_github_token,
)


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    if max_len <= 3:
        return text[:max_len]
    return text[:max_len - 3] + "..."


def _build_top_languages(
    repositories: List[Dict[str, Any]],
    excluded_languages: Optional[Set[str]] = None,
    limit: int = 5,
    bar_max_width: int = 190,
) -> List[Dict[str, Any]]:
    excluded = {item.lower() for item in excluded_languages} if excluded_languages else set()
    language_sizes: Dict[str, int] = {}
    language_colors: Dict[str, str] = {}

    for repo in repositories:
        if repo.get("isFork"):
            continue
        languages = repo.get("languages", {}).get("edges", [])
        for edge in languages:
            size = edge.get("size") or 0
            node = edge.get("node") or {}
            name = node.get("name")
            if not name:
                continue
            if name.lower() in excluded:
                continue
            language_sizes[name] = language_sizes.get(name, 0) + size
            if name not in language_colors and node.get("color"):
                language_colors[name] = node["color"]

    total_size = sum(language_sizes.values())
    if total_size == 0:
        return []

    top = sorted(language_sizes.items(), key=lambda item: item[1], reverse=True)[:limit]
    top_languages: List[Dict[str, Any]] = []
    for name, size in top:
        percent = (size / total_size) * 100.0
        bar_width = int(round(bar_max_width * percent / 100.0))
        if bar_width == 0 and percent > 0:
            bar_width = 2
        top_languages.append(
            {
                "name": name,
                "display_name": _truncate(name, 18),
                "percent": round(percent, 1),
                "color": language_colors.get(name, "#8b949e"),
                "bar_width": bar_width,
            }
        )

    return top_languages


def _build_recent_repos(
    contributed_repos: List[Dict[str, Any]],
    owned_repos: List[Dict[str, Any]],
    limit: int = 5,
    excluded_languages: Optional[Set[str]] = None,
    name_max_len: int = 26,
    description_max_len: int = 44,
) -> List[Dict[str, Any]]:
    excluded = {item.lower() for item in excluded_languages} if excluded_languages else set()
    source = contributed_repos or owned_repos
    sorted_repos = sorted(
        source,
        key=lambda repo: repo.get("pushedAt") or repo.get("updatedAt") or "",
        reverse=True,
    )

    recent: List[Dict[str, Any]] = []
    seen = set()
    for repo in sorted_repos:
        name_with_owner = repo.get("nameWithOwner")
        if not name_with_owner or name_with_owner in seen:
            continue
        if repo.get("isFork"):
            continue

        primary = repo.get("primaryLanguage") or {}
        language_name = primary.get("name") or "Other"
        language_color = primary.get("color") or "#8b949e"
        if language_name.lower() in excluded:
            language_name = "Other"
            language_color = "#8b949e"
        description = repo.get("description") or ""
        description_display = _truncate(description, description_max_len) if description else ""
        updated_at = repo.get("pushedAt") or repo.get("updatedAt") or ""
        recent.append(
            {
                "name": name_with_owner,
                "display_name": _truncate(name_with_owner, name_max_len),
                "url": repo.get("url"),
                "description": description_display,
                "language_name": language_name,
                "language_color": language_color,
                "updated_at": updated_at[:10] if updated_at else "",
            }
        )
        seen.add(name_with_owner)
        if len(recent) >= limit:
            break

    return recent


def _merge_unique_repos(*repo_lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen = set()
    for repos in repo_lists:
        for repo in repos:
            name_with_owner = repo.get("nameWithOwner")
            if not name_with_owner or name_with_owner in seen:
                continue
            merged.append(repo)
            seen.add(name_with_owner)
    return merged


def fetch_github_stats(
    username: str,
    excluded_languages: Optional[Set[str]] = None,
    max_languages: Optional[int] = None,
    max_recent_repos: Optional[int] = None,
) -> Dict[str, Any]:
    """Fetches user statistics using the GitHub GraphQL API."""

    query = """
    query($username: String!) {
      user(login: $username) {
        name
        login
        contributionsCollection {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          restrictedContributionsCount
        }
        repositoriesContributedTo(first: 100, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
          totalCount
          nodes {
            nameWithOwner
            url
            description
            isFork
            updatedAt
            pushedAt
            primaryLanguage {
              name
              color
            }
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                  color
                }
              }
            }
          }
        }
        repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: UPDATED_AT, direction: DESC}) {
          totalCount
          nodes {
            nameWithOwner
            url
            description
            updatedAt
            pushedAt
            isFork
            stargazerCount
            primaryLanguage {
              name
              color
            }
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                  color
                }
              }
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {get_github_token()}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": {"username": username}},
        headers=headers,
    )

    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")

    data = response.json()
    if "errors" in data:
        raise Exception(f"GraphQL Error: {data['errors']}")

    user_data = data["data"]["user"]

    owned_repositories = user_data["repositories"]["nodes"]
    total_stars = sum(repo.get("stargazerCount", 0) for repo in owned_repositories)
    owned_repo_count = user_data["repositories"]["totalCount"]

    contributions = user_data["contributionsCollection"]
    total_commits = contributions["totalCommitContributions"] + contributions["restrictedContributionsCount"]

    excluded = excluded_languages if excluded_languages is not None else EXCLUDED_LANGUAGES
    languages_limit = max_languages if max_languages is not None else MAX_LANGUAGES
    recent_limit = max_recent_repos if max_recent_repos is not None else MAX_RECENT_REPOS

    contributed_repos = user_data["repositoriesContributedTo"].get("nodes", [])
    language_sources = _merge_unique_repos(owned_repositories, contributed_repos)
    top_languages = _build_top_languages(
        language_sources,
        excluded,
        limit=languages_limit,
    )

    recent_repos = _build_recent_repos(
        contributed_repos,
        owned_repositories,
        excluded_languages=excluded,
        limit=recent_limit,
    )

    name_display = _truncate(user_data["name"] or user_data["login"], 24)

    return {
        "username": user_data["login"],
        "name": user_data["name"] or user_data["login"],
        "name_display": name_display,
        "total_commits": total_commits,
        "total_prs": contributions["totalPullRequestContributions"],
        "total_issues": contributions["totalIssueContributions"],
        "contributed_to": user_data["repositoriesContributedTo"]["totalCount"],
        "total_stars": total_stars,
        "owned_repo_count": owned_repo_count,
        "top_languages": top_languages,
        "recent_repos": recent_repos,
    }
