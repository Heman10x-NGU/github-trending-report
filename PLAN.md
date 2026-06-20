# GitHub Trending Report — Implementation Plan

## JTBD (Jobs to Be Done)

**When I** want to understand what's trending on GitHub in 2026
**I want to** see a categorized, searchable, auto-updating report
**So I can** spot trends, find repos, and share insights on Twitter

**Job performers:** AI developers, indie hackers, tech Twitter accounts
**Frequency:** Weekly check, daily share
**Competing solutions:** GitHub Trending page (raw, uncategorized), HN front page, Reddit

---

## Architecture

```
Data:   bonfy/github-trending (upstream, daily .md files)
Tools:  your/repo/scripts (categorizer + HTML generator)
Output: your/repo/docs/index.html (GitHub Pages)
```

**Two repos, one job.** Upstream scrapes. We present.

---

## Repo Structure

```
github-trending-report/
├── .github/
│   └── workflows/
│       └── update.yml           # Mon/Wed/Fri at 11:30 PM IST
├── scripts/
│   ├── ingest.py                # Read new .md → merge into state.json
│   └── generate_html.py         # state.json → docs/index.html
├── data/
│   ├── state.json               # Accumulated repo data (single source of truth)
│   └── last_processed.txt       # "2026-06-20" (tracks ingestion)
├── docs/
│   └── index.html               # Generated HTML (GitHub Pages serves this)
├── templates/
│   └── report.html              # HTML template with CSS/JS
├── requirements.txt             # pyquery, requests
├── README.md
└── PLAN.md
```

---

## Scripts

### ingest.py

```
Input: upstream/*.md files, data/state.json (existing state), data/last_processed.txt
Output: Updated state.json, updated last_processed.txt

Logic:
1. Read last_processed.txt → last_date
2. Find upstream/*.md files with date > last_date
3. For each new file:
   a. Parse: regex extract (owner, repo, url, description, language_section)
   b. For each repo:
      - If full_name in state.json repos → increment appearance_count, update last_seen
      - If new → add with appearance_count=1, first_seen=today, last_seen=today
4. Re-categorize ALL repos (keyword matching, fast)
5. Write state.json
6. Write last_processed.txt = latest date processed
7. Print summary: N new repos, M updated, total now T
```

### generate_html.py

```
Input: data/state.json, templates/report.html
Output: docs/index.html

Logic:
1. Load state.json
2. Compute stats: category_counts, significance_counts, monthly_unique
3. Sort repos by appearance_count desc
4. Top 30 = top 30 by count
5. Categories = repos grouped by primary_category, sorted by count
6. Fill HTML template with data
7. Write docs/index.html
```

---

## Categorization Rules (keyword-based, no AI)

**Main categories:**
1. AI Agents & Frameworks → subcategories: Frameworks, Skills & Plugins, Memory & RAG, Coding Agents, Browser Agents, Research Agents
2. LLM Infrastructure
3. AI/ML Models & Research
4. Developer Tools & CLI
5. Observability & Monitoring
6. Web Frameworks & Frontend
7. DevOps & Cloud
8. Security & Privacy
9. Data & Databases
10. Mobile & Desktop
11. API & Backend
12. Content & Media
13. Finance & Trading
14. Education & Learning
15. Other (target: <200 repos)

**Significance:**
- legendary: 50+ days
- hot: 20-49 days
- rising: 10-19 days
- notable: 4-9 days
- new: 1-3 days

---

## GitHub Actions Workflow

```yaml
name: Update Report
on:
  schedule:
    - cron: '30 18 * * 1,3,5'  # Mon/Wed/Fri at 11:30 PM IST
  workflow_dispatch:
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - checkout (self)
      - checkout bonfy/github-trending → upstream/
      - setup python 3.12
      - pip install pyquery requests
      - python scripts/ingest.py
      - python scripts/generate_html.py
      - git add + commit + push
```

---

## Edge Cases (Pre-Mortem + Inversion)

| Failure Mode | Cause | Mitigation |
|--------------|-------|------------|
| Upstream format changes | bonfy changes .md structure | Script fails gracefully, logs error, doesn't corrupt state |
| Duplicate repos across days | Same repo, different casing | Normalize full_name to lowercase |
| Empty descriptions | Some repos have no description | Template shows "No description available" |
| state.json grows unbounded | 2000+ repos after a year | Compress old data, keep last 180 days only |
| GitHub Actions minutes exhausted | Free tier = 2000 min/month | Mon/Wed/Fri schedule = ~13 runs/month, well under limit |
| bonfy repo goes offline | Upstream deleted or private | Workflow fails gracefully, keeps existing state |
| New language categories appear | bonfy adds Rust, TypeScript | Ingest.py handles any language section dynamically |
| Rate limiting on checkout | Too many workflow runs | schedule is 3x/week, no risk |

---

## What We're NOT Building

- ❌ Our own scraper (bonfy does it)
- ❌ AI-powered categorization (keywords work, free)
- ❌ Database (JSON file is enough for 2000 repos)
- ❌ Backend server (GitHub Pages is static)
- ❌ User auth / accounts (public data, public site)

---

## Verification Checklist

- [ ] Repo created on GitHub
- [ ] ingest.py processes bonfy's existing 170 .md files into state.json
- [ ] generate_html.py produces valid HTML from state.json
- [ ] HTML renders correctly in browser
- [ ] GitHub Pages enabled and serving
- [ ] Workflow runs successfully
- [ ] Tweet the live link

---

## Implementation Order

1. Create repo structure
2. Write ingest.py + test locally
3. Write generate_html.py + test locally
4. Write HTML template (from polished design)
5. Write README.md
6. Create GitHub repo, push
7. Enable GitHub Pages
8. Set up workflow
9. Run initial ingest (170 files)
10. Verify live site
11. Tweet
