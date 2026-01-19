# Repository Guidelines

## Project Structure & Content Organization
- Root markdown pages (`index.md`, `about.md`, `research.md`, `news.md`, `software.md`, `people.md`) render through `_layouts/page.html`.
- `_posts/` supports dated news items, while `News/` stores long-form PDFs; pair new PDFs with a short `_posts` entry so updates surface in the feed.
- `peoplepages/` holds individual bios that `people.md` aggregates; name files `First_Last.md` and store matching headshots in `images/People_Images/`.
- `_data/people.yml` drives both the current roster and alumni listings—set `status: current` (default) or `status: alumni` to move cards between pages without editing markdown.
- `_data/alumni.yml` keeps the historical grad/postdoc lists in sync with the new card layout; edit categories there when you need to add cohorts predating the data file.
- `_data/publications.yml` and `_data/lab_authors.yml` are the single source for publications and lab-member aliases; never hand-edit `papers.md` directly.
- Styling lives in `_sass/` partials with the compiled entry in `style.scss`; shared HTML snippets belong in `_includes/`.

## Build, Test, and Development Commands
- `bundle install` installs the GitHub Pages plug-in set defined in `Gemfile`; rerun when Ruby dependencies change.
- `bundle exec jekyll serve --livereload` watches markdown, HTML, and Sass changes and serves the site at `http://127.0.0.1:4000`.
- `bundle exec jekyll serve --drafts --future` previews embargoed announcements without publishing.
- `bundle exec jekyll build` produces the static `_site/` output and surfaces Liquid or front-matter errors earlier than GitHub Pages.
- `bundle exec jekyll doctor` reports broken links, missing permalinks, and configuration issues before you push.
- `npm install` pulls in tooling for image optimization; rerun only when `package.json` changes.
- `python scripts/review_lab_authors.py > docs/lab_authors_review.txt` audits alias coverage and flags unmatched bolded authors before shipping publication updates.

## Coding Style & Naming Conventions
- Markdown and HTML use two-space indentation; replace tabs when you encounter them and wrap lines at ~100 characters for readability.
- Keep YAML front matter minimal and ordered as `layout`, `title`, `permalink`, `categories`, `tags`; example:
  ```yaml
  ---
  layout: page
  title: "Lab Members"
  permalink: /people/
  ---
  ```
- Posts follow `YYYY-MM-DD-slug.md`; prefer lowercase slugs with hyphens (`2024-05-15-field-day.md`).
- Use descriptive alt text for images and compress photos below ~500 KB before committing.

## Testing & Review Practices
- After content edits, load the affected page via `jekyll serve` and check navigation links, anchors, and image paths.
- When adding assets, verify they load under `_site/` and that relative URLs match the deployed permalink structure.
- Run `jekyll build` before opening a pull request; resolve Liquid warnings so GitHub Pages builds remain green.
- For larger structural changes, capture a quick screenshot or screen recording to demonstrate the rendered result.
- Whenever you touch publication data, commit the regenerated `docs/lab_authors_review.txt` so reviewers can see the before/after diff, and mention any helper scripts used.

## Assets & Media
- Store new photography in `images/` and keep widths ≤ 1800px to avoid layout shifts; run `npm run optimize:image -- path/to/image.jpg` to recompress heavy assets with `sharp`.
- Reference hero imagery from `images/Front_Page_Images/` and people portraits from `images/People_Images/`; update `_data/people.yml` when you add a new headshot.
- Optimized derivatives that ship with the site live under `images/optimized/`; regenerate them with `python scripts/build_optimized_images.py` after adding or updating source photos.
- Large data downloads, PDFs, or slide decks belong in `News/` or `Pubs/`; link to them from a short markdown summary so they surface in the news feed.

## Publications Workflow
- Follow the schema in `docs/publications-data-spec.md` when editing `_data/publications.yml`; keep entries sorted by year and ensure each lab author carries the correct `member_id` from `_data/lab_authors.yml`.
- Add or update aliases in `_data/lab_authors.yml` whenever a new spelling appears; the optional `scripts/build_lab_authors.py` helper can reseed from roster data, but expected edits should be manual and reviewed.
- Use the planned helper page at `/tools/bibtex-to-yaml` (or the spec’s examples until that page lands) to convert BibTeX into the required YAML structure.
- After making changes, run `python scripts/review_lab_authors.py` for alias validation and `bundle exec jekyll build` to confirm the Liquid templates still render.

### Adding a new publication (quick recipe)
- Copy the BibTeX for the paper from the journal or preprint server.
- In your browser, open `/tools/bibtex-to-yaml` (once available) and paste the BibTeX to generate a YAML block; until then, follow the examples in `docs/publications-data-spec.md` and existing entries in `_data/publications.yml`.
- Append the YAML block to `_data/publications.yml` under the correct year, keeping IDs unique and consistent with the existing `YYYY-key-phrase` pattern.
- Only edit `_data/lab_authors.yml` if the paper introduces a new lab-affiliated person or a new spelling/initials variant for an existing lab member; external collaborators do not need `member_id`s.
- After updating the data files, run `python3 scripts/review_lab_authors.py > docs/lab_authors_review.txt` and then `bundle exec jekyll build`; fix any reported issues before committing.

## News Items Workflow

News items are stored in `_data/news.yml` and displayed on the homepage (3 most recent), the news page (6 recent + grouped archive), and the full archive.

### News item schema
```yaml
- date: '2025-11-24'           # Required: ISO date format
  title: Short Descriptive Title  # Required: keep concise
  image: /images/News_Images/photo.jpg  # Optional: thumbnail image
  summary: "Description text."  # Required: supports Markdown links
  people:                      # Optional: lab member page paths
    - /peoplepages/PersonA/
    - /peoplepages/PersonB/
```

### Linking conventions

**Lab members**: Always link lab member names to their people pages using Markdown syntax:
```yaml
summary: "[James Schnable](/peoplepages/jschnable/) presented new research..."
```

**External links**: Embed links directly in the summary text rather than using a separate `link` field:
```yaml
# Correct - link embedded in text
summary: "Read the [full paper](https://doi.org/10.1234/example) in Nature."

# Incorrect - don't use separate link field
link: https://example.com  # Avoid this pattern
```

**Example with both**:
```yaml
summary: "[Vladimir Torres-Rodríguez](/peoplepages/Vlad/)'s paper [*Population-level gene expression*](https://doi.org/10.1111/tpj.16801) won the TPJ award."
```

### Adding a news item

**Option 1: Interactive script**
```bash
./scripts/add-news.sh
```
The script prompts for date, title, summary, image, and people links, then prepends the entry to `_data/news.yml`.

**Option 2: Manual entry**
- Reference `scripts/news-template.yml` for example formats
- Add the new entry to `_data/news.yml` (order doesn't matter; items are sorted by date)

### Adding and optimizing news images

1. **Prepare the image**: Resize to ~400px width for thumbnails. Use macOS `sips` or ImageMagick:
   ```bash
   sips -Z 400 original.jpg --out images/News_Images/optimized.jpg
   ```

2. **Target file size**: Aim for 30–60KB per image. The display size is 120×90px on desktop (with 2× retina support) and full-width on mobile at 180px height.

3. **Save location**: Place optimized images in `images/News_Images/`.

4. **Reference in YAML**: Use the path `/images/News_Images/filename.jpg` in the `image` field.

5. **Naming convention**: Use descriptive names matching the news item (e.g., `Hackathon.jpg`, `GradAwards.jpg`).

### WebP thumbnails (required for news images)

The homepage template uses `<picture>` elements that reference WebP thumbnails at `_240.webp` paths. **When adding a news item with an image, you must also create the corresponding WebP thumbnail**, or the image will show as broken (404 error).

For example, if your news entry has:
```yaml
image: /images/News_Images/PAG2026Reunion.jpg
```

You must also create `images/News_Images/PAG2026Reunion_240.webp`.

**Generate a single thumbnail:**
```bash
python3 -c "
from PIL import Image, ImageOps
from pathlib import Path

src = Path('images/News_Images/YourImage.jpg')  # Change to your image
dest = src.parent / (src.stem + '_240.webp')

with Image.open(src) as img:
    img = ImageOps.exif_transpose(img)
    ratio = 240 / img.width
    resized = img.resize((240, int(img.height * ratio)), Image.LANCZOS)
    if resized.mode in ('RGBA', 'P'):
        resized = resized.convert('RGB')
    resized.save(dest, 'WEBP', quality=85)
    print(f'Created: {dest}')
"
```

**Generate all missing thumbnails:**
```bash
# Find news images missing WebP versions and list them
grep -o 'image: /images/News_Images/[^[:space:]]*' _data/news.yml | \
  sed 's/image: //' | while read img; do
    base=$(echo "$img" | sed 's/\.[^.]*$//')
    webp="${base}_240.webp"
    [ ! -f ".$webp" ] && echo "Missing: $webp"
  done
```

### General image optimization (optional)

For bulk optimization of all site images (not the `_240.webp` thumbnails), run:
```bash
python scripts/build_optimized_images.py
```
This creates resized copies under `images/optimized/` for faster page loads.

## Commit & Pull Request Guidelines
- Use concise, imperative commit messages (e.g., `Add Deniz profile` or `Refresh maize phenotyping copy`) and group related edits together.
- Reference the touched page or asset in the first line of the PR description and include a local preview link (`http://127.0.0.1:4000/path/`) plus screenshots when visual changes matter.
- Call out new dependencies (Ruby or Node), data sources, or manual follow-up steps so downstream maintainers know what to expect.
