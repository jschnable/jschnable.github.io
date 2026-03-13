# Publications Reference (Current Implementation)

This page documents how publications are currently stored and rendered on this site.
Use this file as the primary reference when editing publication content.

## Source of Truth

- Canonical dataset: `_data/publications.yml`
- Lab author identity + aliases: `_data/lab_authors.yml`
- Tag/filter vocabulary: `_data/publication_tags.yml`

Do not hand-edit citation prose in `papers.md`; that page renders from YAML data.

## Current Publication Entry Shape

Each publication is one YAML object in `_data/publications.yml`.

```yaml
- id: 2026-example-publication
  year: 2026
  title: Example publication title
  authors:
  - name: Example A
    member_id: example-author
  - name: Example B
  # optional abbreviation for very long author lists:
  # - truncated: true
  status: published        # e.g. published | accepted | in-press | preprint
  type: article            # e.g. article | review | preprint | conference | chapter
  journal: Example Journal
  doi: 10.1000/example-doi # optional but preferred when known
  url: https://doi.org/10.1000/example-doi # optional if no landing page exists
  notes:                   # optional list of key/value maps
  - bioRxiv: 10.1101/2026.01.01.123456
  author_note: Example note for abbreviated author list context # optional
  first_author_is_lab_member: true
  lab_author_count: 1
  tags:
  - maize
  - genomics
```

### Field Notes

- `authors[].member_id` must match an `id` in `_data/lab_authors.yml`.
- `authors[].truncated: true` is used when an author list is intentionally abbreviated with `...`.
- `status: preprint` drives the preprint section in the publications page.
- `tags` should use IDs defined in `_data/publication_tags.yml`.

## Rendering Flow

- Main publications page:
  - Source page: `papers.md`
  - Renders all preprints first (`status: preprint`), sorted by `lab_author_count` descending
  - Groups non-preprints by year (descending)
  - Within each year, display order is:
    1. Papers without `doi` and without `url` (treated as not-yet-linked/accepted/in-press)
    2. Papers with `doi` or `url`, sorted by `lab_author_count` descending
  - Adds filter UI using `tags` and `first_author_is_lab_member`
- Citation rendering:
  - Include: `_includes/publication-card.html`
  - Bolds lab authors when `member_id` is present
  - Renders `...` for `truncated: true`
  - Links title via `url`, renders DOI link when `doi` exists
  - Shows non-published status badge
- Person-specific publication lists:
  - Include: `_includes/person-publications.html`
  - Called from `_layouts/person.html` after mapping a person page to a `lab_authors` entry by `people_page`

## Author Alias Workflow

- Maintain author aliases in `_data/lab_authors.yml`.
- Use `python scripts/review_lab_authors.py > docs/lab_authors_review.txt` after publication updates.
- Commit the refreshed `docs/lab_authors_review.txt` with publication data changes.

## BibTeX Conversion

- Helper page: `/tools/bibtex-to-yaml` (`tools/bibtex-to-yaml.md`).
- The helper parses one BibTeX entry, maps author aliases to `member_id`, and outputs a YAML block for `_data/publications.yml`.

## Legacy / Historical Files

- `docs/publications-data-spec.md` is migration/design documentation and may not always reflect every live field.
- `papers_original.md`, `papers.md.backup`, and `papers2.md` are legacy snapshots and not the canonical publications source.
