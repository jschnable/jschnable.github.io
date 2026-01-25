---
published: false
---

# Publications Page Enhancements – Implementation Plan

This document outlines the implementation plan for three new features on the publications page: topic tags, copy citation buttons, and a featured publications section.

---

## 1. Topic Tags / Keywords

### Overview
Add categorical tags to publications so visitors can quickly identify papers by research area (e.g., phenotyping, GWAS, sorghum, maize, methods).

### Data Model Changes

Add a `tags` field to each publication entry in `_data/publications.yml`:

```yaml
- id: 2025-n-offtheshelf-image-analysis
  year: 2025
  title: Off-the-shelf image analysis models outperform human visual assessment...
  tags:
    - phenotyping
    - sorghum
    - machine-learning
  # ... other fields
```

**Recommended tag vocabulary** (start small, expand as needed):
- **Crops**: `maize`, `sorghum`, `millet`, `other-crops`
- **Methods**: `phenotyping`, `gwas`, `twas`, `genomics`, `machine-learning`, `image-analysis`
- **Traits**: `flowering-time`, `yield`, `stress-tolerance`, `photosynthesis`
- **Other**: `review`, `methods-paper`, `collaboration`

### Implementation Steps

1. **Define tag vocabulary** in `_data/publication_tags.yml`:
   ```yaml
   - id: phenotyping
     label: Phenotyping
     color: "#3b82f6"  # blue
   - id: maize
     label: Maize
     color: "#eab308"  # yellow
   - id: sorghum
     label: Sorghum
     color: "#f97316"  # orange
   # etc.
   ```

2. **Add tags to publications** – Start with recent papers (2023–2026), then backfill older ones as time permits. Many older papers can remain untagged.

3. **Update `publication-card.html`** to display tags:
   ```liquid
   {% if pub.tags %}
   <div class="pub-tags">
     {% for tag_id in pub.tags %}
       {% assign tag_info = site.data.publication_tags | where: "id", tag_id | first %}
       <span class="pub-tag" style="--tag-color: {{ tag_info.color }}">{{ tag_info.label }}</span>
     {% endfor %}
   </div>
   {% endif %}
   ```

4. **Add CSS** for tag badges:
   ```scss
   .pub-tags {
     display: flex;
     flex-wrap: wrap;
     gap: 6px;
     margin-top: 8px;
   }

   .pub-tag {
     background: color-mix(in srgb, var(--tag-color) 15%, white);
     border: 1px solid var(--tag-color);
     color: var(--tag-color);
     font-size: 0.75rem;
     font-weight: 600;
     padding: 2px 8px;
     border-radius: 12px;
     text-transform: uppercase;
     letter-spacing: 0.02em;
   }
   ```

5. **Optional: Add tag filter UI** at the top of the publications page – clickable tag pills that filter the visible publications via JavaScript.

### Level of Effort
- Data entry: ~2-3 hours to tag recent papers
- Code changes: ~1 hour
- Optional filter UI: ~2 hours additional

---

## 2. Copy Citation Button

### Overview
Add a button to each publication that copies a formatted citation to the clipboard. Support multiple formats (APA, BibTeX).

### Implementation Steps

1. **Add citation data to publications** – The current schema already has most needed fields. For BibTeX export, we may want to add:
   ```yaml
   - id: 2025-example
     bibtex_type: article  # article, inproceedings, book, etc.
     pages: "123-145"      # optional
     volume: "12"          # optional
     issue: "3"            # optional
   ```

2. **Create citation formatter JavaScript** in `assets/js/citations.js`:
   ```javascript
   function formatAPA(pub) {
     const authors = pub.authors.map(a => a.name).join(', ');
     return `${authors} (${pub.year}). ${pub.title}. ${pub.journal}. https://doi.org/${pub.doi}`;
   }

   function formatBibTeX(pub) {
     return `@article{${pub.id},
     author = {${pub.authors.map(a => a.name).join(' and ')}},
     title = {${pub.title}},
     journal = {${pub.journal}},
     year = {${pub.year}},
     doi = {${pub.doi}}
   }`;
   }

   async function copyCitation(pubId, format) {
     const pub = window.publicationsData.find(p => p.id === pubId);
     const text = format === 'bibtex' ? formatBibTeX(pub) : formatAPA(pub);
     await navigator.clipboard.writeText(text);
     // Show toast notification
     showToast('Citation copied!');
   }
   ```

3. **Embed publication data as JSON** in `papers.md`:
   ```liquid
   <script>
     window.publicationsData = {{ site.data.publications | jsonify }};
   </script>
   ```

4. **Update `publication-card.html`** to include copy button:
   ```liquid
   <div class="pub-actions">
     <button class="pub-copy-btn" onclick="copyCitation('{{ pub.id }}', 'apa')" title="Copy APA citation">
       <svg><!-- clipboard icon --></svg>
       Cite
     </button>
     <div class="pub-copy-dropdown">
       <button onclick="copyCitation('{{ pub.id }}', 'apa')">APA</button>
       <button onclick="copyCitation('{{ pub.id }}', 'bibtex')">BibTeX</button>
     </div>
   </div>
   ```

5. **Add CSS** for the copy button:
   ```scss
   .pub-copy-btn {
     background: transparent;
     border: 1px solid #ddd;
     border-radius: 4px;
     color: $gray;
     cursor: pointer;
     font-size: 0.8rem;
     padding: 4px 10px;
     transition: all 0.15s ease;

     &:hover {
       border-color: #d00000;
       color: #d00000;
     }
   }

   .pub-toast {
     position: fixed;
     bottom: 24px;
     right: 24px;
     background: #333;
     color: #fff;
     padding: 12px 20px;
     border-radius: 8px;
     opacity: 0;
     transition: opacity 0.2s ease;

     &.visible {
       opacity: 1;
     }
   }
   ```

### Level of Effort
- JavaScript: ~1.5 hours
- HTML/CSS: ~1 hour
- Testing across browsers: ~30 minutes

---

## 3. Featured Publications Section

### Overview
Highlight 3–5 landmark papers at the top of the publications page with larger cards, optional plain-language summaries, and links to press coverage.

### Data Model Changes

Add a `featured` field and optional `summary` and `press` fields:

```yaml
- id: 2022-mural-meta-gwas
  year: 2022
  title: Meta-analysis identifies pleiotropic loci controlling phenotypic trade-offs in sorghum
  featured: true
  featured_order: 1  # controls display order (1 = first)
  summary: "This study combined data from 20+ environments to identify genes that control trade-offs between yield and stress tolerance in sorghum."
  press:
    - title: "UNL News"
      url: "https://news.unl.edu/..."
    - title: "Genetics journal highlight"
      url: "https://..."
  # ... other fields
```

### Implementation Steps

1. **Add featured metadata** to 3–5 key publications in `_data/publications.yml`.

2. **Create featured section** at the top of `papers.md`:
   ```liquid
   {% assign featured = site.data.publications | where: "featured", true | sort: "featured_order" %}
   {% if featured.size > 0 %}
   <section class="featured-publications">
     <h2>Featured Publications</h2>
     <div class="featured-grid">
       {% for pub in featured %}
         <article class="featured-pub-card">
           <h3><a href="{{ pub.url }}">{{ pub.title }}</a></h3>
           <p class="featured-pub-meta">{{ pub.journal }} ({{ pub.year }})</p>
           {% if pub.summary %}
             <p class="featured-pub-summary">{{ pub.summary }}</p>
           {% endif %}
           {% if pub.press %}
             <div class="featured-pub-press">
               <strong>Press:</strong>
               {% for link in pub.press %}
                 <a href="{{ link.url }}">{{ link.title }}</a>{% unless forloop.last %}, {% endunless %}
               {% endfor %}
             </div>
           {% endif %}
           <button class="pub-copy-btn" onclick="copyCitation('{{ pub.id }}', 'apa')">Cite</button>
         </article>
       {% endfor %}
     </div>
   </section>
   {% endif %}
   ```

3. **Add CSS** for featured cards:
   ```scss
   .featured-publications {
     background: #f9f7f3;
     margin: -20px -24px 40px;
     padding: 32px 24px;
     border-radius: 12px;
   }

   .featured-publications h2 {
     margin-top: 0;
   }

   .featured-grid {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
     gap: 24px;
     margin-top: 20px;
   }

   .featured-pub-card {
     background: #fff;
     border: 1px solid #e5e5e5;
     border-radius: 12px;
     padding: 24px;

     h3 {
       font-size: 1.1rem;
       line-height: 1.4;
       margin: 0 0 8px;
     }

     h3 a {
       color: inherit;

       &:hover {
         color: #d00000;
       }
     }
   }

   .featured-pub-meta {
     color: $gray;
     font-size: 0.9rem;
     margin: 0 0 12px;
   }

   .featured-pub-summary {
     font-size: 0.95rem;
     line-height: 1.6;
     margin: 0 0 12px;
   }

   .featured-pub-press {
     font-size: 0.85rem;
     margin-bottom: 12px;
   }
   ```

### Level of Effort
- Data entry (summaries, selecting papers): ~1 hour
- Liquid template: ~30 minutes
- CSS: ~45 minutes

---

## Implementation Priority

**Phase 1 (Quick wins):**
1. Featured Publications section – High visibility, low complexity
2. Copy Citation button – Frequently requested feature

**Phase 2 (Content work):**
3. Topic Tags – Requires data entry but adds significant value

---

## Files to Modify

| File | Changes |
|------|---------|
| `_data/publications.yml` | Add `featured`, `summary`, `press`, `tags` fields |
| `_data/publication_tags.yml` | New file – tag definitions |
| `papers.md` | Add featured section, embed JSON, load JS |
| `_includes/publication-card.html` | Add tags display, copy button |
| `assets/js/citations.js` | New file – citation formatting |
| `style.scss` | Add styles for tags, copy button, featured section |

---

## Open Questions

1. **Tag granularity**: Should we use broad categories (phenotyping, genomics) or allow finer-grained tags (GWAS, TWAS, RNA-seq)?
2. **Featured paper selection criteria**: Impact factor? Citation count? Lab "greatest hits"?
3. **Citation formats**: APA + BibTeX sufficient, or also include Chicago, MLA, RIS?
4. **Backfill strategy**: Tag all papers or just recent ones (e.g., 2020+)?
