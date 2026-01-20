---
layout: page
title: Schnable Lab Papers
---

{% assign preprints = site.data.publications | where: "status", "preprint" | sort: "year" | reverse %}
{% assign published = site.data.publications | where_exp: "pub", "pub.status != 'preprint'" %}
{% assign grouped = published | group_by: "year" | sort: "name" | reverse %}

{% comment %} Filter Buttons in collapsible menu {% endcomment %}
<details class="pub-filters-wrapper">
  <summary>Filter Papers by Topic</summary>
  <div class="pub-filters">
    <div class="pub-filter-group">
      <span class="pub-filter-label">Special:</span>
      <button class="pub-filter-btn" data-filter="lab-first-author">Lab First Author</button>
    </div>
    <div class="pub-filter-group">
      <span class="pub-filter-label">Crops:</span>
      {% for tag in site.data.publication_tags %}{% if tag.category == "crop" %}
      <button class="pub-filter-btn" data-filter="{{ tag.id }}" style="--tag-color: {{ tag.color }}">{{ tag.label }}</button>
      {% endif %}{% endfor %}
    </div>
    <div class="pub-filter-group">
      <span class="pub-filter-label">Methods:</span>
      {% for tag in site.data.publication_tags %}{% if tag.category == "method" %}
      <button class="pub-filter-btn" data-filter="{{ tag.id }}" style="--tag-color: {{ tag.color }}">{{ tag.label }}</button>
      {% endif %}{% endfor %}
    </div>
    <div class="pub-filter-group">
      <span class="pub-filter-label">Topics:</span>
      {% for tag in site.data.publication_tags %}{% if tag.category == "topic" %}
      <button class="pub-filter-btn" data-filter="{{ tag.id }}" style="--tag-color: {{ tag.color }}">{{ tag.label }}</button>
      {% endif %}{% endfor %}
    </div>
    <div class="pub-filter-group">
      <span class="pub-filter-label">Types:</span>
      {% for tag in site.data.publication_tags %}{% if tag.category == "type" %}
      <button class="pub-filter-btn" data-filter="{{ tag.id }}" style="--tag-color: {{ tag.color }}">{{ tag.label }}</button>
      {% endif %}{% endfor %}
    </div>
    <div class="pub-filter-actions">
      <button class="pub-filter-clear" id="clear-filters">Clear All Filters</button>
    </div>
  </div>
</details>

<p class="pub-filter-status" id="filter-status"></p>

{% comment %} Year Navigation Bar {% endcomment %}
<nav class="year-nav">
  {% if preprints.size > 0 %}<a href="#preprints">Preprints</a>{% endif %}
  {% for group in grouped %}<a href="#year-{{ group.name }}">{{ group.name }}</a>{% endfor %}
</nav>

{% comment %} Preprints section {% endcomment %}
{% if preprints.size > 0 %}
<section id="preprints" class="pub-year-section">
  <h2>Preprints</h2>
  <ul class="pub-list">
{% for pub in preprints %}<li class="pub-item" data-tags="{{ pub.tags | join: ' ' }}"{% if pub.first_author_is_lab_member %} data-lab-first="true"{% endif %}>{% include publication-card.html pub=pub %}</li>
{% endfor %}</ul>
</section>
{% endif %}

{% comment %} Published papers grouped by year {% endcomment %}
{% for group in grouped %}
<section id="year-{{ group.name }}" class="pub-year-section">
  <h2>{{ group.name }}</h2>
  <ul class="pub-list">
{% for pub in group.items %}<li class="pub-item" data-tags="{{ pub.tags | join: ' ' }}"{% if pub.first_author_is_lab_member %} data-lab-first="true"{% endif %}>{% include publication-card.html pub=pub %}</li>
{% endfor %}</ul>
</section>
{% endfor %}

<script>
(function() {
  var activeFilters = [];
  var filterBtns = document.querySelectorAll('.pub-filter-btn');
  var clearBtn = document.getElementById('clear-filters');
  var statusEl = document.getElementById('filter-status');
  var allPubs = document.querySelectorAll('.pub-item');
  var sections = document.querySelectorAll('.pub-year-section');

  function applyFilters() {
    if (activeFilters.length === 0) {
      clearFilters();
      return;
    }

    var visibleCount = 0;

    allPubs.forEach(function(pub) {
      var dominated = true;
      var pubTags = (pub.dataset.tags || '').split(' ').filter(function(t) { return t; });
      var isLabFirst = pub.dataset.labFirst === 'true';

      // Check if paper matches ALL active filters (AND logic)
      for (var i = 0; i < activeFilters.length; i++) {
        var filter = activeFilters[i];
        if (filter === 'lab-first-author') {
          if (!isLabFirst) {
            dominated = false;
            break;
          }
        } else {
          if (pubTags.indexOf(filter) === -1) {
            dominated = false;
            break;
          }
        }
      }

      pub.style.display = dominated ? '' : 'none';
      if (dominated) visibleCount++;
    });

    // Hide empty sections
    sections.forEach(function(section) {
      var hasVisible = Array.from(section.querySelectorAll('.pub-item')).some(function(p) {
        return p.style.display !== 'none';
      });
      section.style.display = hasVisible ? '' : 'none';
    });

    // Update status message
    var filterLabels = activeFilters.map(function(f) {
      if (f === 'lab-first-author') return 'Lab First Author';
      var btn = document.querySelector('[data-filter="' + f + '"]');
      return btn ? btn.textContent : f;
    });
    statusEl.textContent = 'Showing ' + visibleCount + ' paper' + (visibleCount !== 1 ? 's' : '') +
      ' matching: ' + filterLabels.join(' + ');
  }

  function clearFilters() {
    activeFilters = [];
    allPubs.forEach(function(pub) {
      pub.style.display = '';
    });
    sections.forEach(function(section) {
      section.style.display = '';
    });
    filterBtns.forEach(function(btn) {
      btn.classList.remove('active');
    });
    statusEl.textContent = '';
  }

  filterBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var filter = this.dataset.filter;
      var index = activeFilters.indexOf(filter);

      if (index === -1) {
        // Add filter
        activeFilters.push(filter);
        this.classList.add('active');
      } else {
        // Remove filter
        activeFilters.splice(index, 1);
        this.classList.remove('active');
      }

      applyFilters();
    });
  });

  clearBtn.addEventListener('click', clearFilters);
})();
</script>
