---
layout: page
title: Schnable Lab Papers
---
<script type='text/javascript' src='https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js'></script>
<script async src="https://badge.dimensions.ai/badge.js" charset="utf-8"></script>

{% assign preprints = site.data.publications | where: "status", "preprint" | sort: "year" | reverse %}
{% assign published = site.data.publications | where: "status", "published" %}
{% assign grouped = published | group_by: "year" | sort: "name" | reverse %}

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
{% for pub in preprints %}<li class="pub-item"><div data-badge-type="2" data-doi="{{ pub.doi }}" data-hide-no-mentions="true" data-hide-less-than="2" class="altmetric-embed" style="float:right;"></div>{% include publication-card.html pub=pub %}</li>
{% endfor %}</ul>
</section>
{% endif %}

{% comment %} Published papers grouped by year {% endcomment %}
{% for group in grouped %}
<section id="year-{{ group.name }}" class="pub-year-section">
  <h2>{{ group.name }}</h2>
  <ul class="pub-list">
{% for pub in group.items %}<li class="pub-item"><div data-badge-type="2" data-doi="{{ pub.doi }}" data-hide-no-mentions="true" data-hide-less-than="2" class="altmetric-embed" style="float:right;"></div>{% include publication-card.html pub=pub %}</li>
{% endfor %}</ul>
</section>
{% endfor %}
