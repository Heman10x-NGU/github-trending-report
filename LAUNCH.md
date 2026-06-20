# Launch Notes

A short distribution plan for sharing GitHub Trending Report without sounding like spam.

## Primary Links

- Live report: https://heman10x-ngu.github.io/github-trending-report/
- GitHub repo: https://github.com/Heman10x-NGU/github-trending-report
- Upstream data source: https://github.com/bonfy/github-trending

## Best Places To Post

| Channel | Link | Suggested title | Notes |
|---|---|---|---|
| Hacker News | https://news.ycombinator.com/submit | `Show HN: Searchable daily report of GitHub Trending repos by category` | Best single launch target. HN's Show HN guidance says the thing should be personally made, non-trivial, and easy to try without signups. This qualifies because the live report is usable immediately. |
| r/github | https://www.reddit.com/r/github/ | `I built a searchable daily report for GitHub Trending repos` | Directly relevant. Lead with the GitHub Pages link, then repo link. Ask for feedback on categories. |
| r/opensource | https://www.reddit.com/r/opensource/ | `Open-source GitHub Trending report: categories, search, repeat-appearance scoring` | Works if framed as an open-source utility, not a personal promo blast. |
| r/SideProject | https://www.reddit.com/r/SideProject/ | `I made a daily GitHub Trending report to spot durable developer trends` | Good maker audience. Include why you built it and what feedback you want. |
| r/webdev | https://www.reddit.com/r/webdev/ | `Static GitHub Pages report generated daily by GitHub Actions` | Post only if emphasizing the static architecture and frontend, not just the dataset. |
| r/Python | https://www.reddit.com/r/Python/ | `Python stdlib script that turns GitHub Trending snapshots into a static report` | Use only if you write a technical post around the parser/generator. Avoid if it is just a link drop. |
| Product Hunt | https://www.producthunt.com/posts/new | `GitHub Trending Report` | Lower priority than HN/Reddit, but useful as a product-discovery backlink. Use the live site as the product URL. |
| X / Twitter | https://x.com/compose/post | `I built a searchable daily GitHub Trending report...` | Post a short thread with screenshots, categories, and live link. |
| LinkedIn | https://www.linkedin.com/feed/ | `I built a static report that tracks what repeatedly trends on GitHub` | Use a more professional angle: trend discovery, automation, and data product. |
| DEV Community | https://dev.to/new | `Building a daily GitHub Trending report with GitHub Actions and Pages` | Best as a build-note article, not just a project announcement. |

## Channels To Avoid Or Treat Carefully

- `r/programming`: only post if you write a strong technical article. A plain project link is likely too self-promotional.
- `r/MachineLearning`: avoid. The project tracks AI repos, but it is not ML research.
- `r/datasets`: avoid unless you publish a downloadable dataset/API beyond the generated HTML.
- Broad startup communities: avoid for now. This is a developer utility, not a startup launch.

## First HN Comment Draft

I built this because GitHub Trending is useful but hard to scan historically. The report groups trending repos by category, tracks repeat appearances, and labels projects as new/notable/rising/hot/legendary based on how often they appear.

It is intentionally simple: GitHub Actions pulls public trending snapshots from bonfy/github-trending, a Python stdlib script parses/categorizes them, and GitHub Pages serves the generated static report.

I would especially like feedback on the category rules and whether repeat appearances are a useful signal for developer trend discovery.

## Reddit Post Body Draft

I built a small static site that turns GitHub Trending snapshots into a searchable categorized report.

Live: https://heman10x-ngu.github.io/github-trending-report/  
Repo: https://github.com/Heman10x-NGU/github-trending-report

It tracks repeat appearances, first/last seen dates, language labels, and groups repos into categories like AI agents, LLM infrastructure, developer tools, security, data, DevOps, and frontend.

The stack is deliberately boring: GitHub Actions, Python stdlib, and GitHub Pages. No backend or database.

Would love feedback on the category rules and whether the repeat-appearance scoring is useful.

## Source Notes

- HN Show HN guidelines: https://news.ycombinator.com/showhn.html
- HN general guidelines: https://news.ycombinator.com/newsguidelines.html
- Product Hunt new product page: https://www.producthunt.com/posts/new
