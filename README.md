# GitHub Trending Report

A searchable, categorized daily report of repositories appearing on GitHub Trending.

**Live report:** https://heman10x-ngu.github.io/github-trending-report/  
**Source data:** https://github.com/bonfy/github-trending

GitHub Trending is useful, but it is noisy when you want to spot durable themes. This project turns raw trending snapshots into a static report with categories, significance labels, appearance counts, first/last seen dates, language filters, and search.

## What You Get

- Daily GitHub Actions refresh at 11:30 PM IST
- Searchable static site served by GitHub Pages
- Category grouping for AI agents, LLM infrastructure, developer tools, security, data, DevOps, frontend, finance, and more
- Significance labels based on repeat appearances: `new`, `notable`, `rising`, `hot`, `legendary`
- Top 30 repositories by appearance count
- No backend, no database, no paid API dependency

## How It Works

1. GitHub Actions runs on a daily cron and can also be triggered manually.
2. The workflow checks out this repo and the upstream [`bonfy/github-trending`](https://github.com/bonfy/github-trending) data repo.
3. [`scripts/build.py`](scripts/build.py) parses 2026 trending markdown files.
4. Repositories are deduplicated, categorized, scored by appearance count, and rendered into [`docs/index.html`](docs/index.html).
5. GitHub Pages serves the generated report from the `docs/` directory.

## Categories

Category rules live in [`scripts/categories.json`](scripts/categories.json). Current top-level groups include:

| Category | What it catches |
|---|---|
| Agent Frameworks & Orchestration | Multi-agent systems, agent runtimes, orchestration frameworks |
| Agent Memory & RAG | Retrieval, memory, embeddings, knowledge graphs, long-context tooling |
| Coding Agents | AI coding tools, IDE agents, code assistants |
| LLM Infrastructure | Inference, serving, model routing, local LLM tooling |
| Developer Tools & CLI | Terminals, shells, package managers, editors, build tools |
| Security & Privacy | Scanners, auth, proxies, privacy/security utilities |
| Data & Databases | Databases, analytics, ETL, document/data tooling |
| DevOps & Cloud | Containers, CI/CD, infrastructure, deployment, self-hosting |
| Web Frameworks & Frontend | Frontend frameworks, web tooling, UI libraries |
| Finance & Trading | Trading, crypto, payments, finance, billing |

## Local Usage

```bash
git clone https://github.com/Heman10x-NGU/github-trending-report.git
cd github-trending-report

git clone https://github.com/bonfy/github-trending.git upstream
python scripts/build.py --upstream upstream --output docs/index.html
python -m http.server -d docs 8000
```

Open http://localhost:8000.

## Project Structure

```text
github-trending-report/
├── .github/workflows/update.yml   # Daily cron job
├── scripts/
│   ├── build.py                   # Report generator
│   └── categories.json            # Category and significance rules
├── templates/report.html          # Static site template
├── docs/index.html                # Generated GitHub Pages output
├── design-tokens.json             # Visual system tokens
├── LAUNCH.md                      # Suggested places to share the project
└── README.md
```

## Good Launch Angles

- "I built a searchable daily report of GitHub Trending so it is easier to spot durable developer trends."
- "GitHub Trending is noisy, so I grouped repos by category and repeat appearances."
- "No backend: GitHub Actions plus GitHub Pages turns public trending data into a daily static report."

See [`LAUNCH.md`](LAUNCH.md) for posting targets and suggested titles.

## Credits

Trending data is sourced from [`bonfy/github-trending`](https://github.com/bonfy/github-trending).

## License

MIT
