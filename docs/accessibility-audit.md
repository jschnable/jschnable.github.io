# Accessibility and crawler audit — 2026-10-20

## Git synchronization

Fetched origin and merged `origin/master` at `8a06e37` into the local branch in merge commit
`d7148f6`. Seven conflicted files contained older versions of roster/publication data and the
GeneAnnotation tool. Resolved them using the newer upstream implementations and data.
The pre-existing uncommitted changes to AGENTS.md, publication filtering, research, and the
publication reference document were stashed and restored successfully.

## Checklist decisions

| Requested item | Implementation or disposition |
| --- | --- |
| Accessible controls and images | Added five missing form labels, named city-removal buttons, made city suggestions native buttons, labeled five video frames, improved research figure and alumni map alternatives, and added optional escaped `image_alt` values for news. Existing social icons already had names. |
| Important information in raw HTML | Lab description, research, people, publications, and news render in HTML. Added a clear lab introduction, text describing the alumni map, and a gene-tool introduction with a dataset link and no-JavaScript explanation. |
| Question as every first H2 | Not applied mechanically: this is not a product-comparison site; existing topic headings remain useful. |
| “It depends” product comparisons | Not applicable. |
| Clear definitions | Added a plain-language lab definition and replaced TimeVenn's slogan with a description of its purpose. |
| Plain-text testimonials | Not applicable; no customer testimonials were found. |
| Date factual claims | The site owner confirmed the admissions, hiring, and alumni claims on October 20, 2026. Added visible “as of” dates to those statements without changing their substance. |
| robots.txt | Explicitly included `meta-webindexer` in the same group as other crawlers, preserving development-path exclusions. Removed the blanket `/tools/` exclusion. Enabled the public gene tool in sitemap and search. |
| Broken links | Fixed all 10 broken local-reference occurrences detected in the original build. Repaired 15 external URL targets and removed 16 confirmed-dead hyperlinks while keeping historical text. |
| Semantic HTML | Native main landmarks, named research navigation, and city-choice buttons. Inline links are underlined so color is not their only distinguishing feature. |
| Publication/update dates | Shared date include supports `published_on` and `last_modified_at` on pages, people, and homepage. Posts use their actual `date`. Dates are shown below titles only when supplied; no build-time freshness stamps. |

Use `published_on: YYYY-MM-DD` for the original publication date and
`last_modified_at: YYYY-MM-DD` only after a meaningful content revision. Do not infer publication
dates from the beginning of the repository's history or update dates from every build.

News entries can optionally supply `image_alt` describing an image; existing titles remain the
fallback. Research figures have surrounding HTML explanations and publication links; their alt
text describes the visual content without claiming to reproduce all underlying numerical data.

## Validation

- Jekyll build and doctor run with the installed Homebrew Ruby 3.3 environment.
- Parsed all 81 generated HTML files: local links, fragment anchors, image/source assets, image
  alt attributes, labels, and names for links/buttons. No findings after fixes.
- Checked 505 distinct external link URLs with redirected GET requests. Initially: 305 returned
  HTTP 200, 31 returned 404, and 169 were blocked, rate-limited, timed out, or otherwise inconclusive.
  Two of the inconclusive failures were malformed/obsolete hostnames and were repaired.
- Preserved Twitter and Google Scholar links that returned 404 because those services can give
  unreliable responses to automated clients. No 403, 429, 999, or timeout was treated as proof
  that a link should be deleted. See [the full link ledger](accessibility/external-links.csv).
- Ran axe-core 4.10.3 WCAG A/AA checks in Chrome across all 81 pages with third-party requests
  blocked. The only remaining finding was five unnamed video frames, subsequently corrected.
  Rechecked the changed media, research, and TimeVenn pages with live browser loading.
  Also checked ten representative pages with live loading; no remaining automated violations.
- Tested keyboard activation of TimeVenn city suggestions and named removal buttons.
- Gene-tool browser checks covered its page and controls. The separate `/gene-function-data/`
  service is not served by this local Jekyll checkout, so gene searches were not tested end to end.
- Checked 390px mobile layouts on home, research, TimeVenn, and gene-tool pages for horizontal
  overflow. Desktop previews: [research](accessibility/research-desktop.png) and
  [TimeVenn](accessibility/timevenn-desktop.png).
- Regenerated `docs/lab_authors_review.txt` with `scripts/review_lab_authors.py` after repairing
  publication URLs. Its 25 initial-variant notices describe the existing aliases, which were
  not changed in this audit.

Automated checks are not a full accessibility certification. Embedded video captions, scientific
figure data equivalence, and TimeVenn's drag-based interval selection need separate manual review.

## Site owner decisions — 2026-10-20

1. **Gene results:** Keep individual results interactive; do not generate static per-gene pages.
   The HTML explanation and dataset link remain available without JavaScript.
2. **Older facts:** The site owner confirmed that the admissions, hiring, and alumni claims are
   correct. Keep them as current guidance rather than archiving them. Added October 20, 2026
   “as of” statements to the homepage alumni paragraph, admissions guide, and jobs page.
   This records owner confirmation, not independent verification of institutional policies.

## Optional follow-up

TimeVenn city choice and time slider are keyboard-accessible, but its graphical interval
selection still uses dragging. A keyboard-operated interval form and tabular overlap summary
would be a useful follow-up feature.

The implementation follows the W3C guidance on [form labels](https://www.w3.org/WAI/tutorials/forms/labels/)
and [image alternatives](https://www.w3.org/WAI/tutorials/images/). None of these changes guarantees
recommendations or citations by an AI service.
