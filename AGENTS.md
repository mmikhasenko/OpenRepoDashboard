# OpenRepoDashboard context

Build a low-maintenance, public, read-only GitHub Pages dashboard for the 31 explicitly selected repositories in config/repositories.json. Preserve the selection unless the user changes it. JuliaDev means general Julia packages; DecayModels means specific hadron-physics and amplitude-analysis models.

## Product

Keep the interface calm and easy to act on: failures first, open PRs and issues, CI status and one approximate duration. Round corners, restrained colors, macOS-inspired typography. Keep job timings and lists expandable. Avoid scores, crowded metrics and charts. Public GitHub links perform actions; the website has no write credentials. Local agents handle investigation and fixes.

## Privacy

.local/checkouts.json is ignored, private machine context. Never commit it, copy paths from it into public data, or deploy the project root. Only site/ is uploaded. Collect only from the public repository allowlist, checking visibility before collecting. Never persist tokens.

## Operations

Python standard library only. Run python -m unittest discover -s tests, python scripts/collect.py with GH_TOKEN provided via environment, then python scripts/validate.py. The daily workflow builds fresh data and uploads only site/. Data is generated at deployment and not committed. Missing or partial data must never appear healthy. Update README when behavior changes.
