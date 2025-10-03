# Repository Guidelines

## Project Structure & Content Organization
- Root markdown pages (`index.md`, `about.md`, `research.md`, `news.md`, `software.md`, `people.md`) render through `_layouts/page.html`.
- `_posts/` supports dated news items, while `News/` stores long-form PDFs; pair new PDFs with a short `_posts` entry so updates surface in the feed.
- `peoplepages/` holds individual bios that `people.md` aggregates; name files `First_Last.md` and store matching headshots in `images/People_Images/`.
- `_data/people.yml` drives both the current roster and alumni listings—set `status: current` (default) or `status: alumni` to move cards between pages without editing markdown.
- `_data/alumni.yml` keeps the historical grad/postdoc lists in sync with the new card layout; edit categories there when you need to add cohorts predating the data file.
- Styling lives in `_sass/` partials with the compiled entry in `style.scss`; shared HTML snippets belong in `_includes/`.

## Build, Test, and Development Commands
- `bundle install` installs the GitHub Pages plug-in set defined in `Gemfile`; rerun when Ruby dependencies change.
- `bundle exec jekyll serve --livereload` watches markdown, HTML, and Sass changes and serves the site at `http://127.0.0.1:4000`.
- `bundle exec jekyll serve --drafts --future` previews embargoed announcements without publishing.
- `bundle exec jekyll build` produces the static `_site/` output and surfaces Liquid or front-matter errors earlier than GitHub Pages.
- `bundle exec jekyll doctor` reports broken links, missing permalinks, and configuration issues before you push.
- `npm install` pulls in tooling for image optimization; rerun only when `package.json` changes.

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

## Assets & Media
- Store new photography in `images/` and keep widths ≤ 1800px to avoid layout shifts; run `npm run optimize:image -- path/to/image.jpg` to recompress heavy assets with `sharp`.
- Reference hero imagery from `images/Front_Page_Images/` and people portraits from `images/People_Images/`; update `_data/people.yml` when you add a new headshot.
- Large data downloads, PDFs, or slide decks belong in `News/` or `Pubs/`; link to them from a short markdown summary so they surface in the news feed.

## Commit & Pull Request Guidelines
- Use concise, imperative commit messages (e.g., `Add Deniz profile` or `Refresh maize phenotyping copy`) and group related edits together.
- Reference the touched page or asset in the first line of the PR description and include a local preview link (`http://127.0.0.1:4000/path/`) plus screenshots when visual changes matter.
- Call out new dependencies (Ruby or Node), data sources, or manual follow-up steps so downstream maintainers know what to expect.
