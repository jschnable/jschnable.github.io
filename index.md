---
layout: page
title: Schnable Lab
subtitle: Hypothesis Driven Research in Plant Genomics and Phenomics

googlefonts: ["Monoton", "Lobster"]
bigimg:
  - "/images/optimized/Front_Page_Images/header.png" : ""
---

<script type="application/ld+json">{% include schema-organization.json %}</script>

<picture>
  <source srcset="/images/optimized/lab2022_v2_800.webp" type="image/webp">
  <img src="/images/optimized/lab2022_v2.jpg" alt="The Schnable Lab" width="800" loading="eager">
</picture>

<div class="hero-banner">
  <h2>Hypothesis-driven research in plant genomics and phenomics</h2>
  <p>The Schnable Lab blends field experiments, molecular biology, and computational analytics to understand how the genetics of our world's most important crops drives performance in the field.</p>
</div>

## What We Study

- **Phenotyping** – developing and testing new approaches to measure plants, from greenhouses to fields to satellites.
- **Quantitative genetics** – collecting genetic, molecular, and trait data from large populations in multiple environments to understand how genes and environment shape plant phenotypes.
- **Genomics** – using comparative genomics to figure out how to engineer more stress-tolerant and resource-use-efficient plants.

Each lab member gains experience coding, building field equipment, running molecular assays, and communicating results to scientific and public audiences. The cross-training keeps our science grounded in real-world challenges and ensures discoveries translate beyond the lab.

## Where Our Trainees Go

Our alumni are employed as professors at eleven universities across four countries, as research scientists at all three of the major seed companies, and at multiple plant biotechnology startups.

<picture>
  <source srcset="/images/optimized/alumni_map_800.webp" type="image/webp">
  <img src="/images/Alumnitrimmed.png" alt="Alumni map" width="600" loading="lazy">
</picture>

## Recent Lab News

{% assign highlights = site.data.news | sort: 'date' | reverse | slice: 0, 3 %}
<ul class="news-list">
{% for item in highlights %}
  <li class="news-list__item{% if item.image %} news-list__item--has-image{% endif %}">
    {% if item.image %}
      {% assign img_webp = item.image | replace: '.jpg', '_240.webp' | replace: '.jpeg', '_240.webp' | replace: '.png', '_240.webp' %}
      <picture>
        <source srcset="{{ img_webp }}" type="image/webp">
        <img src="{{ item.image }}" alt="{{ item.title }}" class="news-list__image" width="120" height="90" loading="lazy" />
      </picture>
    {% endif %}
    <div class="news-list__content">
      <time datetime="{{ item.date | date: '%Y-%m-%d' }}">{{ item.date | date: '%B %d, %Y' }}</time>
      <strong>{{ item.title }}</strong><br />
      {% assign summary_html = item.summary | markdownify | strip_newlines | replace: '<p>', '' | replace: '</p>', '' %}
      {{ summary_html }}
      {% if item.link %}<br /><a href="{{ item.link }}">Learn more</a>{% endif %}
    </div>
  </li>
{% endfor %}
</ul>

[See all news]({{ '/news/' | relative_url }})

Looking for the Iowa State group led by Dr. Patrick Schnable? [Visit their site](https://schnablelab.plantgenomics.iastate.edu/).
