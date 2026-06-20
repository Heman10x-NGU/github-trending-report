#!/usr/bin/env python3
"""
build.py -- GitHub Trending Report generator.

Scans upstream bonfy/github-trending .md files, parses repos,
deduplicates, categorizes, and writes an HTML report.

Usage:
    python scripts/build.py --upstream <path> --output docs/index.html

Only stdlib deps: json, re, os, glob, html, datetime, argparse, tempfile.
"""

import argparse
import glob
import html
import json
import os
import re
import tempfile
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CATEGORIES_PATH = os.path.join(SCRIPT_DIR, "categories.json")
TEMPLATE_PATH = os.path.join(
    os.path.dirname(SCRIPT_DIR), "templates", "report.html"
)

# Regex: matches lines like:
#   * [owner / repo-name](https://github.com/owner/repo-name):Description here
#   * [owner / repo-name](https://github.com/owner/repo-name):
REPO_RE = re.compile(
    r"^\*\s*\[(?P<owner>[^\s]+)\s*/\s*(?P<repo>[^\]]+)]"
    r"\(https://github\.com/(?P<path>[^)]+)\):(?P<desc>.*)"
)

# Date header: ## YYYY-MM-DD
DATE_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})")

# Language section: #### language
LANG_RE = re.compile(r"^####\s+(.+)")


# ---------------------------------------------------------------------------
# Category matching
# ---------------------------------------------------------------------------

def load_categories(path: str) -> dict:
    """Load categories.json. Returns empty dict on missing file."""
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("categories", {})


def categorize(name: str, description: str, categories: dict) -> str:
    """Return the first matching category name, or 'Other'."""
    if not categories:
        return "Other"
    # Build searchable text: repo name + description, lowered
    text = f"{name} {description}".lower()
    # Check subcategories first (they are more specific), then top-level.
    # Sort so that subcategories (non-null subcategory_of) come first.
    sorted_cats = sorted(
        categories.items(),
        key=lambda kv: (0 if kv[1].get("subcategory_of") else 1),
    )
    for cat_name, cat_info in sorted_cats:
        for kw in cat_info.get("keywords", []):
            if kw.lower() in text:
                return cat_name
    return "Other"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_upstream_files(upstream_dir: str) -> list[dict]:
    """
    Scan upstream_dir for .md files (flat YYYY-MM-DD.md and nested
    YYYY/YYYY-MM-DD.md).  Parse repo entries.  Returns a flat list of
    dicts with keys: full_name, url, description, language, date.
    """
    patterns = [
        os.path.join(upstream_dir, "*.md"),
        os.path.join(upstream_dir, "*", "*.md"),
    ]
    files: list[str] = []
    for pat in patterns:
        files.extend(glob.glob(pat))

    # De-dup just in case a file matches both patterns
    files = sorted(set(files))

    entries: list[dict] = []
    for fpath in files:
        # Extract date from filename
        basename = os.path.basename(fpath)
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})\.md$", basename)
        if not date_match:
            continue
        file_date = date_match.group(1)

        current_language = "unknown"
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.rstrip("\n")

                    # Check for date header (use as fallback date)
                    dm = DATE_RE.match(line)
                    if dm:
                        file_date = dm.group(1)
                        continue

                    # Check for language section
                    lm = LANG_RE.match(line)
                    if lm:
                        current_language = lm.group(1).strip()
                        continue

                    # Check for repo line
                    rm = REPO_RE.match(line)
                    if rm:
                        owner = rm.group("owner").strip()
                        repo = rm.group("repo").strip()
                        url_path = rm.group("path").strip()
                        desc = rm.group("desc").strip()
                        # Normalize URL
                        url = f"https://github.com/{url_path}"
                        entries.append({
                            "full_name": f"{owner}/{repo}",
                            "url": url,
                            "description": desc,
                            "language": current_language,
                            "date": file_date,
                        })
        except OSError:
            continue  # skip unreadable files

    return entries


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate(entries: list[dict]) -> list[dict]:
    """
    Deduplicate by lowercase full_name.  Tracks appearance_count,
    first_seen, last_seen.  Keeps the latest description.
    """
    seen: dict[str, dict] = {}
    for e in entries:
        key = e["full_name"].lower()
        if key in seen:
            seen[key]["appearance_count"] += 1
            # Update last_seen if this date is newer
            if e["date"] > seen[key]["last_seen"]:
                seen[key]["last_seen"] = e["date"]
                seen[key]["description"] = e["description"]
            # Update first_seen if older
            if e["date"] < seen[key]["first_seen"]:
                seen[key]["first_seen"] = e["date"]
            # Track languages
            lang = e["language"]
            if lang and lang not in seen[key]["languages"]:
                seen[key]["languages"].append(lang)
        else:
            seen[key] = {
                "full_name": e["full_name"],
                "url": e["url"],
                "description": e["description"],
                "language": e["language"],
                "languages": [e["language"]] if e["language"] else [],
                "first_seen": e["date"],
                "last_seen": e["date"],
                "appearance_count": 1,
            }
    return list(seen.values())


# ---------------------------------------------------------------------------
# Significance
# ---------------------------------------------------------------------------

def compute_significance(count: int, thresholds: dict) -> str:
    """Map appearance_count to a significance label."""
    # thresholds sorted descending by value
    sorted_t = sorted(thresholds.items(), key=lambda kv: kv[1], reverse=True)
    for label, min_count in sorted_t:
        if count >= min_count:
            return label
    return "new"


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def compute_stats(repos: list[dict]) -> dict:
    """Compute aggregate statistics for the report."""
    total = len(repos)
    category_counts: dict[str, int] = {}
    significance_counts: dict[str, int] = {}
    language_counts: dict[str, int] = {}

    for r in repos:
        cat = r.get("primary_category", "Other")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        sig = r.get("significance", "new")
        significance_counts[sig] = significance_counts.get(sig, 0) + 1
        for lang in r.get("languages", []):
            if lang:
                language_counts[lang] = language_counts.get(lang, 0) + 1

    # Sort categories by count descending
    sorted_cats = sorted(
        category_counts.items(), key=lambda kv: kv[1], reverse=True
    )
    sorted_langs = sorted(
        language_counts.items(), key=lambda kv: kv[1], reverse=True
    )[:15]  # top 15

    return {
        "total_repos": total,
        "category_counts": sorted_cats,
        "significance_counts": significance_counts,
        "language_counts": sorted_langs,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def significance_badge(sig: str) -> str:
    """Return an HTML badge span for a significance level."""
    colors = {
        "legendary": "#b8860b",
        "hot": "#d4380d",
        "rising": "#096dd9",
        "notable": "#389e0d",
        "new": "#8c8c8c",
    }
    color = colors.get(sig, "#8c8c8c")
    esc = html.escape(sig.title())
    return (
        f'<span style="background:{color};color:#fff;'
        f'padding:1px 6px;border-radius:3px;font-size:0.75em;'
        f'font-weight:600;">{esc}</span>'
    )


def build_repo_row(r: dict) -> str:
    """Build a single <tr> for a repo."""
    name = html.escape(r["full_name"])
    url = html.escape(r["url"])
    desc = html.escape(r["description"] or "No description available")
    cat = html.escape(r.get("primary_category", "Other"))
    sig = significance_badge(r.get("significance", "new"))
    count = r["appearance_count"]
    first = html.escape(r.get("first_seen", ""))
    last = html.escape(r.get("last_seen", ""))
    langs = ", ".join(html.escape(l) for l in r.get("languages", []) if l) or "-"

    return (
        "<tr>"
        f'<td><a href="{url}" target="_blank" rel="noopener">{name}</a></td>'
        f"<td>{desc}</td>"
        f"<td>{cat}</td>"
        f"<td>{sig}</td>"
        f"<td style=\"text-align:center\">{count}</td>"
        f"<td>{first}</td>"
        f"<td>{last}</td>"
        f"<td>{langs}</td>"
        "</tr>\n"
    )


def build_category_section(cat_name: str, repos: list[dict]) -> str:
    """Build an HTML section for a single category."""
    esc_name = html.escape(cat_name)
    count = len(repos)
    rows = "".join(build_repo_row(r) for r in repos)
    return (
        f'<details open>\n<summary><h3 style="display:inline">'
        f"{esc_name} ({count})</h3></summary>\n"
        "<table>\n<thead><tr>"
        "<th>Repo</th><th>Description</th><th>Category</th>"
        "<th>Significance</th><th>Days</th>"
        "<th>First Seen</th><th>Last Seen</th><th>Languages</th>"
        "</tr></thead>\n<tbody>\n"
        f"{rows}"
        "</tbody>\n</table>\n</details>\n"
    )


def generate_html(
    repos: list[dict], stats: dict, build_time: str
) -> str:
    """Generate the full HTML report as a string."""

    # ---- Top 30 by appearance_count ----
    top30 = sorted(
        repos, key=lambda r: r["appearance_count"], reverse=True
    )[:30]
    top30_rows = "".join(build_repo_row(r) for r in top30)

    # ---- Group by category ----
    by_cat: dict[str, list[dict]] = {}
    for r in repos:
        cat = r.get("primary_category", "Other")
        by_cat.setdefault(cat, []).append(r)

    # Sort categories by repo count descending
    sorted_cats = sorted(by_cat.items(), key=lambda kv: len(kv[1]), reverse=True)
    category_sections = "".join(
        build_category_section(name, cat_repos)
        for name, cat_repos in sorted_cats
    )

    # ---- Stats ----
    total = stats["total_repos"]
    generated = html.escape(stats["generated_at"])
    build_ts = html.escape(build_time)

    # Significance summary
    sig = stats.get("significance_counts", {})
    sig_html = " | ".join(
        f"<strong>{html.escape(k.title())}:</strong> {v}"
        for k, v in sorted(sig.items(), key=lambda kv: kv[1], reverse=True)
    )

    # Category summary (top 10)
    cat_summary = "".join(
        f'<span style="margin-right:12px;">{html.escape(name)}: <strong>{count}</strong></span>'
        for name, count in stats.get("category_counts", [])[:10]
    )

    # Language summary
    lang_summary = "".join(
        f'<span style="margin-right:10px;">{html.escape(name)}: {count}</span>'
        for name, count in stats.get("language_counts", [])
    )

    # ---- Try loading external template ----
    template = None
    if os.path.isfile(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = f.read()

    if template:
        # Build JSON data for the template's embedded <script> block
        # Categories grouped by name -> list of repo objects
        categories_json_data: dict[str, list[dict]] = {}
        for name, cat_repos in sorted_cats:
            categories_json_data[name] = [
                {
                    "full_name": r["full_name"],
                    "url": r["url"],
                    "description": r.get("description", ""),
                    "primary_category": r.get("primary_category", "Other"),
                    "significance": r.get("significance", "new"),
                    "appearance_count": r["appearance_count"],
                    "first_seen": r.get("first_seen", ""),
                    "last_seen": r.get("last_seen", ""),
                    "languages": r.get("languages", []),
                }
                for r in cat_repos
            ]

        top30_json_data = [
            {
                "full_name": r["full_name"],
                "url": r["url"],
                "description": r.get("description", ""),
                "primary_category": r.get("primary_category", "Other"),
                "significance": r.get("significance", "new"),
                "appearance_count": r["appearance_count"],
                "first_seen": r.get("first_seen", ""),
                "last_seen": r.get("last_seen", ""),
                "languages": r.get("languages", []),
            }
            for r in top30
        ]

        repos_json_data = [
            {
                "full_name": r["full_name"],
                "url": r["url"],
                "description": r.get("description", ""),
                "primary_category": r.get("primary_category", "Other"),
                "significance": r.get("significance", "new"),
                "appearance_count": r["appearance_count"],
                "first_seen": r.get("first_seen", ""),
                "last_seen": r.get("last_seen", ""),
                "languages": r.get("languages", []),
            }
            for r in repos
        ]

        stats_json_data = {
            "total_repos": total,
            "category_counts": stats.get("category_counts", []),
            "significance_counts": stats.get("significance_counts", {}),
            "language_counts": stats.get("language_counts", []),
        }

        replacements = {
            "{{STATS_JSON}}": json.dumps(stats_json_data),
            "{{REPOS_JSON}}": json.dumps(repos_json_data),
            "{{CATEGORIES_JSON}}": json.dumps(categories_json_data),
            "{{TOP30_JSON}}": json.dumps(top30_json_data),
            "{{GENERATED_DATE}}": generated,
        }
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        return result

    # ---- Fallback: self-contained HTML ----
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub Trending Report</title>
<style>
  :root {{
    --bg: #0d1117;
    --fg: #c9d1d9;
    --card: #161b22;
    --border: #30363d;
    --link: #58a6ff;
    --accent: #1f6feb;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    background: var(--bg); color: var(--fg);
    line-height: 1.6; padding: 24px; max-width: 1400px; margin: 0 auto;
  }}
  h1 {{ color: #f0f6fc; margin-bottom: 8px; font-size: 1.8em; }}
  h2 {{ color: #f0f6fc; margin: 24px 0 12px; font-size: 1.4em; border-bottom: 1px solid var(--border); padding-bottom: 6px; }}
  h3 {{ color: var(--link); margin: 0; font-size: 1.1em; }}
  a {{ color: var(--link); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .stats {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin: 16px 0; }}
  .stats p {{ margin: 4px 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0 24px; font-size: 0.9em; }}
  th {{ background: var(--card); color: var(--fg); text-align: left; padding: 8px 10px; border-bottom: 2px solid var(--border); position: sticky; top: 0; }}
  td {{ padding: 6px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }}
  tr:hover {{ background: rgba(88,166,255,0.04); }}
  details {{ margin: 16px 0; }}
  summary {{ cursor: pointer; padding: 8px 0; }}
  summary:hover {{ color: var(--link); }}
  .meta {{ color: #8b949e; font-size: 0.85em; margin-top: 16px; }}
  @media (max-width: 768px) {{
    body {{ padding: 12px; }}
    table {{ font-size: 0.8em; }}
    td, th {{ padding: 4px 6px; }}
  }}
</style>
</head>
<body>
<h1>GitHub Trending Report</h1>
<p class="meta">Generated: {generated} &nbsp;|&nbsp; Build: {build_ts}</p>

<div class="stats">
  <p><strong>Total unique repos:</strong> {total}</p>
  <p><strong>Significance:</strong> {sig_html}</p>
  <p><strong>Top categories:</strong> {cat_summary}</p>
  <p><strong>Languages:</strong> {lang_summary}</p>
</div>

<h2>Top 30 by Appearances</h2>
<table>
<thead><tr>
  <th>Repo</th><th>Description</th><th>Category</th>
  <th>Significance</th><th>Days</th>
  <th>First Seen</th><th>Last Seen</th><th>Languages</th>
</tr></thead>
<tbody>
{top30_rows}
</tbody>
</table>

<h2>By Category</h2>
{category_sections}

<p class="meta">Data sourced from <a href="https://github.com/bonfy/github-trending">bonfy/github-trending</a>.
Built with Python stdlib only.</p>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------------

def atomic_write(path: str, content: str) -> None:
    """Write content to path atomically (tmp file + rename)."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    dir_name = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(
        suffix=".tmp", prefix=".build_", dir=dir_name
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, os.path.abspath(path))
    except BaseException:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build GitHub Trending HTML report from upstream .md files."
    )
    parser.add_argument(
        "--upstream",
        required=True,
        help="Path to upstream directory containing date .md files.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output HTML file path (e.g. docs/index.html).",
    )
    parser.add_argument(
        "--categories",
        default=CATEGORIES_PATH,
        help=f"Path to categories.json (default: {CATEGORIES_PATH}).",
    )
    args = parser.parse_args()

    upstream = os.path.abspath(args.upstream)
    output = os.path.abspath(args.output)

    if not os.path.isdir(upstream):
        print(f"Error: upstream directory not found: {upstream}")
        raise SystemExit(1)

    # 1. Load categories
    categories = load_categories(args.categories)

    # 2. Parse upstream files
    print(f"Scanning {upstream} ...")
    entries = parse_upstream_files(upstream)
    print(f"  Parsed {len(entries)} repo entries from .md files.")

    # 3. Deduplicate
    repos = deduplicate(entries)
    print(f"  {len(repos)} unique repos after deduplication.")

    # 4. Categorize + significance
    significance_thresholds = {}
    if os.path.isfile(args.categories):
        with open(args.categories, "r", encoding="utf-8") as f:
            cat_data = json.load(f)
        significance_thresholds = cat_data.get("significance", {})

    for r in repos:
        r["primary_category"] = categorize(
            r["full_name"], r["description"], categories
        )
        r["significance"] = compute_significance(
            r["appearance_count"], significance_thresholds
        )

    # 5. Compute stats
    stats = compute_stats(repos)
    build_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # 6. Generate HTML
    report = generate_html(repos, stats, build_time)

    # 7. Atomic write
    atomic_write(output, report)
    print(f"  Wrote {output} ({len(report):,} bytes).")
    print(f"  Total repos: {stats['total_repos']}")
    print("Done.")


if __name__ == "__main__":
    main()
