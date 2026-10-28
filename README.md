# Repository Dashboard

A public, read-only overview of 31 open-source repositories, grouped into JuliaDev and DecayModels.

## Interface

Attention items first: failed workflows, issues and pull requests. Show CI status and one duration. Keep job details expandable. Use a calm macOS-inspired design with rounded corners and direct GitHub links.

## Data boundaries

- `config/repositories.json`: public repository names and categories.
- `.local/checkouts.json`: private local checkout paths; ignored by Git.
- `site/`: the only directory intended for publication on GitHub Pages.
- `scripts/`: future collector and validation tools.

The collector must use the public repository configuration, never the checkout map. Publish only `site/`, never the project root. Local agents may read the checkout map, but must not copy it into public artifacts or prompts displayed by the website.

## Status

Project structure and confirmed collection are prepared. Dashboard implementation and deployment are pending.
