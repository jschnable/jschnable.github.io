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

## Gene function summaries tool data
The `/tools/gene-function-summaries/` page is a static browser tool. Its data (gzipped JSON) are **not** in this
repository: they live in [jschnable/gene-function-data](https://github.com/jschnable/gene-function-data), a GitHub
Pages project site served on the same domain at `https://schnablelab.org/gene-function-data/`. That repository keeps
a single commit, replaced on each publish, so data updates never grow this repository's history. Do not commit
generated data here and do not edit the data files by hand.

Update, assuming sibling checkouts `GeneAnnotation_v2/` and `gene-function-data/` under `/Users/jschnable/Projects/`:

```bash
python3 scripts/generate_gene_function_summaries.py   # read-only on the GeneAnnotation_v2 database
scripts/publish_gene_function_data.sh                 # force-pushes one fresh commit to gene-function-data
```

The generator reads the live `GeneAnnotation_v2` SQLite database (active summaries, names, key papers, Dias et al.
2025 syntenic orthologs) and `data/processed/paper_authors/key_paper_authors.tsv` there; it documents the file
layout in its docstring. After publishing, spot-check the tool with, for example, `tb1`, `Zm00001eb054440`,
`Sobic.001G000100`, `Os03g0215400` and a region search.

## Publications data
- `docs/publications-reference.md` is the best starting point for the current publication storage, schema, and rendering flow.
- `_data/publications.yml` is the canonical list of papers. Keep entries grouped newest year first and preserve the live field schema used by templates.
- Keep publication titles in sentence case with a trailing period.
- For published papers, provide both `doi` and `url` (typically `https://doi.org/<doi>`) so paper titles are clickable on the publications page.
- `_data/lab_authors.yml` stores lab-affiliated authors and alias spellings. Extend it whenever a new variation appears in a citation; `scripts/build_lab_authors.py` can regenerate a draft list from the roster, but changes should be manually reviewed.
- `papers.md` renders from the YAML dataset via `_includes/publication-card.html` and `_includes/person-publications.html` (used for per-member listings on people pages). Do not edit publication prose directly in `papers.md`.
- `/tools/bibtex-to-yaml` converts a single BibTeX entry into a publication YAML block and highlights unmatched author aliases.
- `docs/publications-data-spec.md` captures migration/design history; treat it as background context rather than the source of truth for current fields.

## Scripts
- `scripts/review_lab_authors.py` audits alias coverage and unmatched authors; commit the refreshed `docs/lab_authors_review.txt` alongside publication edits.
- `scripts/build_lab_authors.py` bootstraps `lab_authors.yml` from `_data/people.yml`, `_data/alumni.yml`, and `peoplepages/`; run it when rosters change significantly, then reconcile aliases by hand.
- `scripts/generate_gene_function_summaries.py` rebuilds the data for `/tools/gene-function-summaries/` from the GeneAnnotation v2 database into the `gene-function-data` checkout; `scripts/publish_gene_function_data.sh` publishes it.
- `scripts/migrate_publications.py` was used for the initial markdown→YAML migration and serves as a reference for future bulk conversions.

## Contributing
- Follow the practices outlined in `AGENTS.md` for project structure expectations, testing, and review checklists.
- Group related edits into a single branch, keep commit messages short and imperative, and include screenshots or local URLs for visual changes.
- The site deploys through GitHub Pages; pushing to `master` (or merging a PR targeting `master`) triggers a rebuild.
