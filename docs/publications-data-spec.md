---
published: false
---

# Publications Data Overhaul – Implementation Specification

This document describes the steps required to migrate the Schnable Lab publication workflow to a YAML-based system, introduce a client-side BibTeX→YAML helper page, and prepare the data model for per-person bibliographies. The goal is to provide everything another engineer needs to implement the design end-to-end.

## Objectives

1. **Single source of truth** for publications in `_data/publications.yml`, with machine-readable author metadata.
2. **Consistent rendering** of the publications page (`papers.md`) with automatic lab-member highlighting.
3. **Helper page** that converts pasted BibTeX into the YAML schema and cross-references a lab-author directory.
4. **Future readiness** for per-person bibliographies and automated pipelines.

## Repository Structure Changes

```
assets/
  bibliography/
    lab-publications.bib        # optional legacy export (not used downstream)
_data/
  publications.yml              # canonical publications dataset (new schema)
  lab_authors.yml               # list of lab members + aliases (new file)
docs/
  publications-data-spec.md     # this specification
scripts/
  export_publications.py        # optional helper for bulk conversion (one-off)
  validate_publications.py      # optional lint tool
_tools/
  bibtex-to-yaml.md             # helper page under `/tools/`
```

## Data Model Definitions

### `_data/lab_authors.yml`

Each row represents one lab-affiliated author. This list drives bolding and per-person queries.

```yaml
- id: schnable-jc             # stable identifier (kebab-case)
  name: James C. Schnable     # preferred display name
  aliases:
    - Schnable JC
    - Schnable, James C.
    - Schnable, J.C.
    - J. C. Schnable
  active: true                # optional flag for alumni filtering
  people_page: peoplepages/jschnable.md  # for future linking
```

Guidelines:
- Use kebab-case IDs (`lastname-initials` or `firstname-lastname`).
- Seed the list programmatically from `_data/people.yml` and `_data/alumni.yml` so both current members and alumni are covered, then merge in any individuals who only appear in `peoplepages/` or historical publications.
- List every variant seen in publications (commas, diacritics, initials).
- Include `people_page` if a bio exists; this will ease future includes.

### `_data/publications.yml`

Canonical publication entries, sorted descending by year and alphabetized within year. Example entry:

```yaml
- id: 2025-li-nighttime-fluorescence   # optional unique slug (generated via helper)
  year: 2025
  title: Nighttime fluorescence phenotyping reduces environmental variability for photosynthetic traits in maize
  journal: Frontiers in Plant Science
  doi: 10.3389/fpls.2025.1595339
  url: https://doi.org/10.3389/fpls.2025.1595339
  status: published                    # published | in-press | accepted | preprint
  type: article                        # article | review | preprint | conference | chapter
  authors:
    - name: Li F
      member_id: li-fangyi
    - name: Grzybowski M
    - name: Roston RL
    - name: Schnable JC
      member_id: schnable-jc
  notes:
    - bioRxiv: 10.1101/2024.12.12.628249
    - highlight: Cover article
```

Field requirements:
- `year`: int
- `title`, `journal`: strings with sentence case preserved
- `doi`: canonical DOI string (no URL). Always include when known.
- `url`: best landing page (defaults to `https://doi.org/{doi}` if blank)
- `status`: enumerated string; default “published”
- `type`: enumerated string; used for filtering (preprint, article, review…)
- `authors`: array of objects. `name` holds the citation string. Include `member_id` when the author is in `_data/lab_authors.yml`.
- `notes`: optional array of “key: value” objects. Use for `bioRxiv`, `Altmetric`, `Cover`, etc.

## BibTeX→YAML Helper Page

Create `tools/bibtex-to-yaml.md` with `layout: page`. The page contains:

1. **Input form**
   - Textarea (`id="bibtex-input"`) for pasting a BibTeX entry (single entry per conversion).
   - Status dropdown (`published`, `in-press`, `preprint` default).
   - Type dropdown (`article`, `review`, `conference`, etc.).
   - Checkbox for “Schnable JC last author?” to signal validation warnings.

2. **Processing Script** (`<script>` block)
   - Load lab aliases via inline JSON: `const labAuthors = {{ site.data.lab_authors | jsonify }};` (which itself is derived from `_data/people.yml` + `_data/alumni.yml`).
   - Include `bibtexParse` from CDN: `https://cdn.jsdelivr.net/npm/@orcid/bibtex-parse-js@2/dist/bibtexParse.min.js` (or bundle locally).
   - Parse entry, clean fields:
     - Title: strip braces, condense whitespace.
     - Year: int (`parseInt(entry.year, 10)`).
     - Journal: `entry.journal || entry.booktitle || entry.note` fallback.
     - DOI: `entry.doi` normalized (lowercase, trim).
     - URL: `entry.url` else `https://doi.org/{doi}`.
     - Authors: use `bibtexParse.toJSON()[0].entryTags.AUTHOR` and `bibtexParse.parseAuthor` helpers.
   - For each author, normalize to uppercase letters without punctuation and compare against every alias (precompute alias map `{normalized_string: member_id}` for speed). Add `member_id` when matched.
   - Compose YAML using a template literal; escape strings with `js-yaml` or manual `JSON.stringify` + post-processing to 2-space indentation.

3. **Output**
   - Result textarea (read-only) with generated YAML block.
   - “Copy to clipboard” button using `navigator.clipboard.writeText`.
   - Summary list: show which authors matched lab aliases (green badge) and unmatched ones (grey badge). Flag final author mismatch (if last author isn’t Schnable).

4. **Usage instructions** section on the page: paste BibTeX → review results → copy YAML → update `_data/publications.yml` → add new aliases if needed → run `jekyll build` → commit.

## Liquid Rendering Updates (`papers.md`)

1. Replace hard-coded Markdown with Liquid loops.
2. Group by year descending:
   ```liquid
   {% assign grouped = site.data.publications | group_by: 'year' | sort: 'name' | reverse %}
   {% for group in grouped %}
   ## {{ group.name }}
   <ul class="publication-list">
   {% assign pubs = group.items | sort: 'title' %}
   {% for pub in pubs %}
     <li>
       {% include publication-card.html pub=pub %}
     </li>
   {% endfor %}
   </ul>
   {% endfor %}
   ```
3. Build `_includes/publication-card.html`:
   ```liquid
   {% assign author_strings = '' %}
   {% for author in include.pub.authors %}
     {% capture rendered_author %}
       {% if author.member_id %}<strong>{{ author.name }}</strong>{% else %}{{ author.name }}{% endif %}
     {% endcapture %}
     {% assign author_strings = author_strings | append: rendered_author %}
     {% unless forloop.last %}{% assign author_strings = author_strings | append: ', ' %}{% endunless %}
   {% endfor %}
   <span class="pub-authors">{{ author_strings | raw }}</span>
   ({{ include.pub.year }})
   <em>{{ include.pub.title }}</em>
   {% if include.pub.journal %} *{{ include.pub.journal }}*{% endif %}
   {% if include.pub.doi %} doi: <a href="https://doi.org/{{ include.pub.doi }}">{{ include.pub.doi }}</a>{% endif %}
   {% if include.pub.status and include.pub.status != 'published' %}
     <span class="pub-status pub-status--{{ include.pub.status }}">{{ include.pub.status | capitalize }}</span>
   {% endif %}
   {% if include.pub.notes %}
     <ul class="pub-notes">
     {% for note in include.pub.notes %}
       {% for key in note %}
         <li><strong>{{ key[0] | capitalize }}:</strong> {{ key[1] }}</li>
       {% endfor %}
     {% endfor %}
     </ul>
   {% endif %}
   ```
4. Style using existing CSS (`.pub-authors strong` to bold lab members).

## Future Per-Person Lists

- Create `_includes/person-publications.html` using `where_exp`:
  ```liquid
  {% assign pubs = site.data.publications | where_exp: 'pub', "pub.authors | map: 'member_id' | compact | contains: include.member_id" %}
  {% if pubs.size > 0 %}
    <section class="person-publications">
      <h2>Recent Publications</h2>
      <ul>
      {% for pub in pubs %}
        <li>{% include publication-card.html pub=pub highlight_member=include.member_id %}</li>
      {% endfor %}
      </ul>
    </section>
  {% endif %}
  ```
- Modify `publication-card.html` to optionally wrap the `highlight_member` author with an extra class.

## Migration Steps

1. **Populate `_data/lab_authors.yml`**
   - Extract names from three sources:
     * Front matter of `peoplepages/*.md` (where available).
     * Current roster data in `_data/people.yml` (used by the people list).
     * Alumni listings in `_data/alumni.yml` (captures historical members without pages).
   - Augment this set with existing bold-tag hints in `papers.md` to catch past contributors not present in roster data.
   - For each person, record preferred display name and every alias variant seen in publications (accents, initials, maiden names).

2. **Write `scripts/migrate_publications.py`**
   - Parse `papers.md` line-by-line using regex.
   - Detect year headings (`^\*\*2024\*\*`).
   - For each bullet line, extract authors, title, journal, DOI.
   - Map `<b>Author</b>` tags to `member_id` by alias.
   - Output YAML file using new schema.
   - Manual review of diff.

3. **Replace `papers.md` content** with Liquid loops.
4. **Add helper page** under `/tools/`.
5. **Update docs** (`AGENTS.md`, `README.md`) with new workflow instructions.
6. **Optional scripts**:
   - `scripts/export_publications.py`: convert `.bib` to YAML if bulk updates are needed.
   - `scripts/validate_publications.py`: check required fields, detect duplicates, ensure member IDs exist.

## Testing

- `bundle exec jekyll build` after migration.
- Use helper page to convert sample BibTeX entries; compare output with expected YAML.
- Run validation script (if created) in CI and locally.
- Spot-check `papers.md` for correct bolding/order.

## Task Checklist

- [ ] Add `_data/lab_authors.yml` with complete alias coverage.
- [ ] Implement migration script and generate `_data/publications.yml`.
- [ ] Update `papers.md` to data-driven rendering with new include.
- [ ] Create `/tools/bibtex-to-yaml.md` helper page (HTML/JS).
- [ ] Document workflow in `AGENTS.md`/`README.md`.
- [ ] (Optional) Implement validation script + CI hook.
- [ ] Verify build and visual output before merging.
