# GitHub Trending Report

A static site that aggregates GitHub trending repositories and generates a clean, categorized daily report. Data is refreshed automatically every day via GitHub Actions.

**Live site:** [https://<your-username>.github.io/github-trending-report/](https://<your-username>.github.io/github-trending-report/)

> Replace the URL above with your actual GitHub Pages link after the first deploy.

---

## How It Works

1. **GitHub Actions** runs daily at 11:30 PM IST (`18:30 UTC`).
2. The workflow checks out this repo and the upstream [bonfy/github-trending](https://github.com/bonfy/github-trending) data.
3. `scripts/build.py` parses the trending data, groups repos by category, and renders `docs/index.html`.
4. Updated `data/` and `docs/` files are committed and pushed automatically.
5. GitHub Pages serves `docs/index.html` as the live site.

If the upstream checkout fails (e.g. repo renamed or removed), the workflow continues with whatever data is already present.

---

## Categories

Repos are grouped into these categories:

| Category | Description |
|---|---|
| AI / ML | Machine learning, LLM tooling, agents, inference |
| Web | Frontend frameworks, fullstack, SSR, meta-frameworks |
| Backend | APIs, servers, databases, infrastructure |
| DevOps | CI/CD, containers, IaC, monitoring |
| CLI / Terminal | TUI apps, shells, developer tools |
| Languages & Compilers | New languages, type checkers, runtimes |
| Security | Vulnerability scanners, auth, crypto |
| Other | Everything else |

Categories are configurable in `scripts/build.py`.

---

## Local Usage

```bash
# Clone the repo
git clone https://github.com/<your-username>/github-trending-report.git
cd github-trending-report

# (Optional) Clone upstream data
git clone https://github.com/bonfy/github-trending.git upstream

# Install dependencies
pip install -r requirements.txt

# Build the report
python scripts/build.py --upstream upstream/ --output docs/index.html

# Serve locally
python -m http.server -d docs 8000
# Open http://localhost:8000
```

---

## Project Structure

```
github-trending-report/
├── .github/workflows/update.yml   # Daily cron job
├── scripts/
│   └── build.py                   # Report generator
├── data/                          # Raw trending data (auto-generated)
├── docs/
│   └── index.html                 # Static site output (GitHub Pages)
├── requirements.txt               # Python dependencies
└── README.md
```

---

## License

MIT

---

## Credits

- Trending data sourced from [bonfy/github-trending](https://github.com/bonfy/github-trending)
