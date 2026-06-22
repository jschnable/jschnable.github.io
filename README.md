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
The `/tools/maize-gene-syntheses/` page is a static browser tool backed by generated maize JSON in `assets/data/maize-gene-syntheses/`. Do not edit those JSON files by hand; rebuild them from the current GeneAnnotation SQLite databases.

Default rebuild, assuming sibling checkouts under `/Users/jschnable/Projects/`:

```bash
python3 scripts/generate_maize_gene_syntheses.py
bundle exec jekyll build
```

Rebuild from alternate or newly produced databases:

```bash
python3 scripts/generate_maize_gene_syntheses.py \
  --synthesis-db /path/to/direct_synthesis.sqlite \
  --evidence-db /path/to/evidence.sqlite \
  --output-dir assets/data/maize-gene-syntheses
bundle exec jekyll build
```

Required source tables:

- `direct_synthesis.sqlite`: table `direct_gene_syntheses`, using `species`, `gene_id`, `function_phrase`, `function_sentence`, and `annotation_abstract`; only `species = 'zea_mays'` rows are exported.
- `evidence.sqlite`: table `maize_gene_synonyms`, using `synonym_norm`, `synonym`, `gene_id`, `synonym_type`, `query_priority`, `is_ambiguous`, `is_gene_model_id`, and `include_in_pubmed_query`; exported lookup terms must have `is_ambiguous = 0` and either `is_gene_model_id = 1` or `include_in_pubmed_query = 1`.

After rebuilding, spot-check the tool locally with one v5 ID, one v4 ID, one v3 ID, and one PubMed-query synonym, for example `Zm00001eb237930`, `Zm00001d016066`, `GRMZM2G120408`, and `ZmDFR1`.

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
- `scripts/generate_maize_gene_syntheses.py` rebuilds the static lookup index and synthesis shards for `/tools/maize-gene-syntheses/` from GeneAnnotation SQLite databases.
- `scripts/migrate_publications.py` was used for the initial markdown→YAML migration and serves as a reference for future bulk conversions.

## Contributing
- Follow the practices outlined in `AGENTS.md` for project structure expectations, testing, and review checklists.
- Group related edits into a single branch, keep commit messages short and imperative, and include screenshots or local URLs for visual changes.
- The site deploys through GitHub Pages; pushing to `master` (or merging a PR targeting `master`) triggers a rebuild.
