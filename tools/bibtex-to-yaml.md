---
layout: page
title: "BibTeX to Publications YAML"
permalink: /tools/bibtex-to-yaml/
---

Paste a single BibTeX entry below and use this helper to generate a YAML block compatible with `_data/publications.yml`.

<div class="bibtex-tool">
  <h2>Input</h2>
  <label for="bibtex-input"><strong>BibTeX entry</strong></label><br>
  <textarea id="bibtex-input" rows="12" style="width: 100%;" placeholder="@article{...}"></textarea>

  <div style="margin-top: 1rem;">
    <label for="status-select"><strong>Status</strong></label>
    <select id="status-select">
      <option value="preprint" selected>preprint</option>
      <option value="published">published</option>
      <option value="in-press">in-press</option>
      <option value="accepted">accepted</option>
    </select>

    <label for="type-select" style="margin-left: 1rem;"><strong>Type</strong></label>
    <select id="type-select">
      <option value="article" selected>article</option>
      <option value="review">review</option>
      <option value="preprint">preprint</option>
      <option value="conference">conference</option>
      <option value="chapter">chapter</option>
    </select>

    <label for="schnable-last" style="margin-left: 1rem;">
      <input type="checkbox" id="schnable-last">
      Schnable JC last author?
    </label>
  </div>

  <div style="margin-top: 1rem;">
    <button id="convert-button">Convert BibTeX → YAML</button>
  </div>

  <h2 style="margin-top: 2rem;">Output YAML</h2>
  <textarea id="yaml-output" rows="14" style="width: 100%;" readonly placeholder="Generated YAML will appear here..."></textarea>
  <div style="margin-top: 0.5rem;">
    <button id="copy-yaml-button">Copy YAML to clipboard</button>
  </div>

  <h2 style="margin-top: 2rem;">Author Matching Summary</h2>
  <div id="author-summary">
    <p>No conversion run yet.</p>
  </div>
</div>

<h2>Usage</h2>
<ul>
  <li>Paste a single BibTeX record into the input box.</li>
  <li>Select the appropriate publication <code>status</code> and <code>type</code>.</li>
  <li>Check “Schnable JC last author?” when applicable to get a warning if that is not true in the parsed authors list.</li>
  <li>Click <strong>Convert BibTeX → YAML</strong>, review the generated YAML and author matching summary, then copy the YAML into <code>_data/publications.yml</code>.</li>
  <li>If any lab member names appear under “Unmatched authors”, add or update aliases in <code>_data/lab_authors.yml</code> and re-run the conversion.</li>
</ul>

<script src="https://cdn.jsdelivr.net/npm/@orcid/bibtex-parse-js@2/dist/bibtexParse.min.js"></script>
<script>
  (function() {
    const labAuthors = {{ site.data.lab_authors | jsonify }};

    function normalizeName(str) {
      if (!str) return '';
      return str
        .toUpperCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^A-Z]/g, '');
    }

    function buildAliasIndex(authors) {
      const index = {};
      authors.forEach(author => {
        const aliases = author.aliases || [];
        const allNames = [author.name].concat(aliases);
        allNames.forEach(raw => {
          const key = normalizeName(raw);
          if (!key) return;
          if (!index[key]) {
            index[key] = author.id;
          }
        });
      });
      return index;
    }

    const aliasIndex = buildAliasIndex(labAuthors || []);

    function parseBibtex(raw) {
      const trimmed = (raw || '').trim();
      if (!trimmed) {
        throw new Error('BibTeX input is empty.');
      }
      const parsed = bibtexParse.toJSON(trimmed);
      if (!parsed || !parsed.length) {
        throw new Error('Unable to parse BibTeX. Please check the entry.');
      }
      const entry = parsed[0].entryTags || parsed[0].entrytags || {};
      return entry;
    }

    function cleanTitle(title) {
      if (!title) return '';
      return title
        .replace(/[{}]/g, '')
        .replace(/\s+/g, ' ')
        .trim();
    }

    function determineJournal(entry) {
      return (entry.journal || entry.booktitle || entry.note || '').trim();
    }

    function normalizeDoi(doi) {
      if (!doi) return '';
      let d = doi.trim();
      d = d.replace(/^https?:\/\/(dx\.)?doi\.org\//i, '');
      return d.toLowerCase();
    }

    function buildUrl(doi, entryUrl) {
      const url = (entryUrl || '').trim();
      if (url) return url;
      if (doi) return 'https://doi.org/' + doi;
      return '';
    }

    function formatAuthorName(authorObj) {
      const first = (authorObj.first || '').trim();
      const last = (authorObj.last || '').trim();
      if (!last && !first) return '';
      if (!first) return last;
      const initials = first
        .split(/\s+/)
        .filter(Boolean)
        .map(p => p[0].toUpperCase())
        .join('');
      return initials ? (initials + ' ' + last) : last;
    }

    function extractAuthors(entry) {
      const rawAuthors = entry.AUTHOR || entry.author || '';
      if (!rawAuthors) return [];
      const parsedList = bibtexParse.parseAuthor
        ? bibtexParse.parseAuthor(rawAuthors)
        : [];
      if (!parsedList || !parsedList.length) {
        return rawAuthors.split(/\s+and\s+/i).map(name => ({ name: name.trim() })).filter(a => a.name);
      }
      return parsedList.map(a => ({ name: formatAuthorName(a) })).filter(a => a.name);
    }

    function attachMemberIds(authors) {
      return authors.map(author => {
        const key = normalizeName(author.name);
        const memberId = aliasIndex[key] || null;
        return memberId ? { name: author.name, member_id: memberId } : { name: author.name };
      });
    }

    function yamlEscape(str) {
      if (str == null) return '';
      const s = String(str);
      if (s === '' || /[:{}\[\],&*#?|\-<>=!%@`]/.test(s)) {
        return '"' + s.replace(/"/g, '\\"') + '"';
      }
      return s;
    }

    function buildId(year, title) {
      const safeYear = year || 'xxxx';
      const base = (title || '')
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim()
        .split(' ')
        .slice(0, 4)
        .join('-');
      return safeYear + '-' + (base || 'untitled');
    }

    function buildYaml(entry, options) {
      const status = options.status || 'published';
      const type = options.type || 'article';
      const year = entry.year ? parseInt(entry.year, 10) : null;
      const title = cleanTitle(entry.title || '');
      const journal = determineJournal(entry);
      const doi = normalizeDoi(entry.doi || entry.DOI || '');
      const url = buildUrl(doi, entry.url || entry.URL);
      const rawAuthors = extractAuthors(entry);
      const authors = attachMemberIds(rawAuthors);
      const id = buildId(year, title);

      const yamlLines = [];
      yamlLines.push('- id: ' + yamlEscape(id));
      if (year) yamlLines.push('  year: ' + year);
      if (title) yamlLines.push('  title: ' + yamlEscape(title));
      if (authors.length) {
        yamlLines.push('  authors:');
        authors.forEach(a => {
          yamlLines.push('  - name: ' + yamlEscape(a.name));
          if (a.member_id) {
            yamlLines.push('    member_id: ' + yamlEscape(a.member_id));
          }
        });
      }
      yamlLines.push('  status: ' + yamlEscape(status));
      yamlLines.push('  type: ' + yamlEscape(type));
      if (journal) yamlLines.push('  journal: ' + yamlEscape(journal));
      if (doi) yamlLines.push('  doi: ' + yamlEscape(doi));
      if (url) yamlLines.push('  url: ' + yamlEscape(url));

      if (status === 'preprint' && /biorxiv/i.test(journal) && doi) {
        yamlLines.push('  notes:');
        yamlLines.push('  - bioRxiv: ' + yamlEscape(doi));
      }

      let labAuthorCount = 0;
      authors.forEach(a => {
        if (a.member_id) labAuthorCount += 1;
      });
      yamlLines.push('  first_author_is_lab_member: ' + (authors[0] && authors[0].member_id ? 'true' : 'false'));
      yamlLines.push('  lab_author_count: ' + labAuthorCount);

      return { yaml: yamlLines.join('\\n'), authors };
    }

    function renderAuthorSummary(authors, schnableLastChecked) {
      if (!authors.length) {
        return '<p>No authors parsed from BibTeX.</p>';
      }

      const matched = [];
      const unmatched = [];

      authors.forEach(a => {
        if (a.member_id) {
          matched.push(a);
        } else {
          unmatched.push(a);
        }
      });

      let html = '';
      html += '<p><strong>Matched lab authors (' + matched.length + '):</strong></p>';
      if (matched.length) {
        html += '<ul>';
        matched.forEach(a => {
          html += '<li><span style="color: #0a0; font-weight: bold;">' +
            a.name + '</span> (' + a.member_id + ')</li>';
        });
        html += '</ul>';
      } else {
        html += '<p>None.</p>';
      }

      html += '<p><strong>Unmatched authors (' + unmatched.length + '):</strong></p>';
      if (unmatched.length) {
        html += '<ul>';
        unmatched.forEach(a => {
          html += '<li><span style="color: #555;">' + a.name + '</span></li>';
        });
        html += '</ul>';
      } else {
        html += '<p>None.</p>';
      }

      if (schnableLastChecked) {
        const last = authors[authors.length - 1];
        const ok = last && /schnable/i.test(last.name);
        if (!ok) {
          html += '<p style="color: #b00; font-weight: bold;">Warning: “Schnable JC last author?” is checked but the last parsed author is <em>' +
            (last ? last.name : 'N/A') + '</em>.</p>';
        }
      }

      return html;
    }

    function onConvert() {
      const inputEl = document.getElementById('bibtex-input');
      const outputEl = document.getElementById('yaml-output');
      const summaryEl = document.getElementById('author-summary');
      const statusEl = document.getElementById('status-select');
      const typeEl = document.getElementById('type-select');
      const schnableLastEl = document.getElementById('schnable-last');

      try {
        const entry = parseBibtex(inputEl.value);
        const result = buildYaml(entry, {
          status: statusEl.value,
          type: typeEl.value
        });
        outputEl.value = result.yaml;
        summaryEl.innerHTML = renderAuthorSummary(result.authors, schnableLastEl.checked);
      } catch (err) {
        outputEl.value = '';
        summaryEl.innerHTML = '<p style="color: #b00;">' + err.message + '</p>';
      }
    }

    function onCopyYaml() {
      const outputEl = document.getElementById('yaml-output');
      const text = outputEl.value || '';
      if (!text) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text);
      } else {
        outputEl.select();
        document.execCommand('copy');
      }
    }

    document.addEventListener('DOMContentLoaded', function() {
      var convertBtn = document.getElementById('convert-button');
      var copyBtn = document.getElementById('copy-yaml-button');
      if (convertBtn) {
        convertBtn.addEventListener('click', onConvert);
      }
      if (copyBtn) {
        copyBtn.addEventListener('click', onCopyYaml);
      }
    });
  })();
</script>

