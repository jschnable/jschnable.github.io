---
layout: page
title: Search the Schnable Lab Site
permalink: /search/
search_exclude: true
---

<input type="search" id="search-input" placeholder="Search pages, news, and people" aria-label="Search the Schnable Lab site" />
<ul id="search-results" class="news-list" aria-live="polite"></ul>

<script src="https://cdn.jsdelivr.net/npm/lunr/lunr.min.js"></script>
<script src="{{ '/assets/js/search.js' | relative_url }}"></script>
