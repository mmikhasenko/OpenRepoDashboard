# OpenRepoDashboard

A quiet, public overview of 31 open-source repositories.

**[Open the dashboard](https://mmikhasenko.github.io/OpenRepoDashboard/)**

JuliaDev covers 18 general Julia packages. DecayModels covers 13 hadron-physics and amplitude-analysis models. The exact collection is in `config/repositories.json`.

## Everyday use

Bookmark the dashboard. Filter by category or search a repository. Failures and incomplete data appear first; cards show workflow health, a CI duration where identifiable, and open PR/issue counts. Expand a card for workflow links and up to ten recently updated items of each kind. Copy agent context to investigate locally.

No npm install or local server is needed for normal use. The site is read-only and uses no browser credentials or third-party scripts.

## Updates and deployment

`.github/workflows/update.yml` collects data and deploys GitHub Pages daily at **06:23 UTC**, on pushes to main, or via Actions → Update dashboard and deploy Pages → Run workflow. GitHub may delay scheduled runs. Repository Settings → Pages must use GitHub Actions as its source. GitHub may disable scheduled workflows after 60 days without repository activity; the dashboard flags snapshots older than 36 hours.

The collector uses the workflow's read-only GITHUB_TOKEN and GitHub REST API. It checks repository visibility, enumerates open issues/PRs and workflows, and retrieves the latest default-branch run per workflow. PR-triggered runs are excluded from repository health. Failed API requests display as incomplete data. Archived/disabled workflows and old/no evidence do not count as healthy. Individual PR checks and review readiness are not assessed yet.

CI duration is an approximation from run start to last update, not billed minutes or summed matrix-job time. CI is identified by its workflow name; all workflow durations are available in details. Runs older than 30 days are treated as old evidence. A green status describes observed workflows, not test coverage.

## Development

Python 3.10+ with no third-party dependencies:

```sh
python3 -m unittest discover -s tests
# Supply GH_TOKEN securely in the environment (never commit it).
python3 scripts/collect.py
python3 scripts/validate.py
python3 -m http.server 8000 --directory site
```

Open http://localhost:8000 for a development preview. The GitHub Action is the normal production collector.

## Private local context

`.local/checkouts.json` maps repository names to local checkouts for agents. It is ignored and never read by the collector. It must not be committed, uploaded or included in copied public prompts. Only `site/` is deployed. Generated `site/data.json` is ignored. See `AGENTS.md` for project requirements and operational guidance.
