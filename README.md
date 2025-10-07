# Schnable Lab Website

This repository hosts the Schnable Lab group website built with Jekyll. Content is written in Markdown and rendered with `_layouts/page.html` plus reusable includes in `_includes/`. Data-heavy sections—people, news, and publications—are sourced from YAML under `_data/` so that pages stay lightweight to edit.

## Local setup
- Install Ruby (3.x) and Bundler; install Node.js if you plan to run the image optimization script.
- Install gems: `bundle install`
- Install JavaScript tooling when `package.json` changes: `npm install`

## Development workflow
- Preview changes: `bundle exec jekyll serve --livereload`
- Build for verification: `bundle exec jekyll build`
- Doctor the site when debugging links or configuration: `bundle exec jekyll doctor`
- Publications QA: `python scripts/review_lab_authors.py > docs/lab_authors_review.txt`

## Publications data
- `_data/publications.yml` is the canonical list of papers. Follow the schema in `docs/publications-data-spec.md`, keep entries grouped by `year`, and ensure every lab author includes a `member_id` that matches `_data/lab_authors.yml`.
- `_data/lab_authors.yml` stores lab-affiliated authors and alias spellings. Extend it whenever a new variation appears in a citation; `scripts/build_lab_authors.py` can regenerate a draft list from the roster, but changes should be manually reviewed.
- `papers.md` renders from the YAML dataset via `_includes/publication-card.html` and `_includes/person-publications.html` (used for per-member listings on people pages). Do not edit publication prose directly in `papers.md`.
- A client-side BibTeX→YAML helper page will live at `/tools/bibtex-to-yaml`; until it lands, convert fields manually using the examples in the spec.

## Scripts
- `scripts/review_lab_authors.py` audits alias coverage and unmatched authors; commit the refreshed `docs/lab_authors_review.txt` alongside publication edits.
- `scripts/build_lab_authors.py` bootstraps `lab_authors.yml` from `_data/people.yml`, `_data/alumni.yml`, and `peoplepages/`; run it when rosters change significantly, then reconcile aliases by hand.
- `scripts/migrate_publications.py` was used for the initial markdown→YAML migration and serves as a reference for future bulk conversions.

## Contributing
- Follow the practices outlined in `AGENTS.md` for project structure expectations, testing, and review checklists.
- Group related edits into a single branch, keep commit messages short and imperative, and include screenshots or local URLs for visual changes.
- The site deploys through GitHub Pages; pushing to `master` (or merging a PR targeting `master`) triggers a rebuild.
