# GitHub Trending Report

A searchable, categorized daily report for repositories appearing on GitHub Trending.

[Live report](https://heman10x-ngu.github.io/github-trending-report/) · [Repository](https://github.com/Heman10x-NGU/github-trending-report)

## Overview

GitHub Trending is useful for discovery, but the raw feed is hard to scan once you want patterns instead of individual links. This project generates a static report that groups trending repositories by category, tracks repeat appearances, and makes the result searchable from a GitHub Pages site.

The site is rebuilt automatically with GitHub Actions and published from the `docs/` directory. There is no backend service, database, or paid API dependency.

## Features

- Search across repository names, descriptions, and languages
- Category filters for AI agents, LLM infrastructure, developer tools, security, data, DevOps, frontend, finance, and more
- Significance labels based on repeat appearances: `new`, `notable`, `rising`, `hot`, `legendary`
- First seen and last seen dates for each repository
- Top repositories ranked by appearance count
- Fully static GitHub Pages deployment
- Daily scheduled refresh via GitHub Actions

## How It Works

1. A GitHub Actions workflow runs daily or manually.
2. The workflow collects the latest trending snapshot data.
3. [`scripts/build.py`](scripts/build.py) parses, deduplicates, categorizes, and scores repositories.
4. The HTML report is rendered from [`templates/report.html`](templates/report.html).
5. The generated output is committed to [`docs/index.html`](docs/index.html), which GitHub Pages serves.

## Local Development

```bash
git clone https://github.com/Heman10x-NGU/github-trending-report.git
cd github-trending-report

# Prepare a local directory containing GitHub Trending markdown snapshots.
# The build script expects date-named .md files such as 2026-06-20.md.
python scripts/build.py --upstream ./upstream --output docs/index.html

python -m http.server -d docs 8000
```

Open http://localhost:8000.

## Configuration

Category and significance rules live in [`scripts/categories.json`](scripts/categories.json).

Significance thresholds:

| Label | Appearance count |
|---|---:|
| `legendary` | 50+ |
| `hot` | 20-49 |
| `rising` | 10-19 |
| `notable` | 4-9 |
| `new` | 1-3 |

To change categorization, edit the keyword lists in `scripts/categories.json` and rerun the build script.

## Project Structure

```text
github-trending-report/
├── .github/workflows/update.yml   # Scheduled report refresh
├── docs/index.html                # Generated GitHub Pages output
├── scripts/
│   ├── build.py                   # Report generator
│   └── categories.json            # Category and significance rules
├── templates/report.html          # HTML/CSS/JS template
├── design-tokens.json             # Visual design tokens
├── requirements.txt               # Python dependency file
└── README.md
```

## License

MIT
