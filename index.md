---
layout: page
title: Schnable Lab
subtitle: Hypothesis Driven Research in Plant Genomics and Phenomics

googlefonts: ["Monoton", "Lobster"]
bigimg:
  - "/images/optimized/Front_Page_Images/header.png" : ""
---

<script type="application/ld+json">{% include schema-organization.json %}</script>

![The Schnable Lab](/images/optimized/lab2022_v2.jpg){:width="900" align="middle" }

<div class="hero-banner">
  <h2>Hypothesis-driven research in plant genomics and phenomics</h2>
  <p>The Schnable Lab blends field experiments, molecular biology, and computational analytics to understand how the genetics of our world's most important crops drives performance in the field.</p>
</div>

## What We Study

- **Phenotyping** – developing and testing new approaches to measure plants, from greenhouses to fields to satellites.
- **Quantitative genetics** – collecting genetic, molecular, and trait data from large populations in multiple environments to understand how genes and environment shape plant phenotypes.
- **Genomics** – using comparative genomics to figure out how to engineer more stress-tolerant and resource-use-efficient plants.

Each lab member gains experience coding, building field equipment, running molecular assays, and communicating results to scientific and public audiences. The cross-training keeps our science grounded in real-world challenges and ensures discoveries translate beyond the lab.

## Recent Lab News

{% assign highlights = site.data.news | sort: 'date' | reverse | slice: 0, 3 %}
<ul class="news-list">
{% for item in highlights %}
  <li class="news-list__item">
    <time datetime="{{ item.date | date: '%Y-%m-%d' }}">{{ item.date | date: '%B %d, %Y' }}</time>
    <strong>{{ item.title }}</strong><br />
    {% assign summary_html = item.summary | markdownify | strip_newlines | replace: '<p>', '' | replace: '</p>', '' %}
    {{ summary_html }}
    {% if item.link %}<br /><a href="{{ item.link }}">Learn more</a>{% endif %}
  </li>
{% endfor %}
</ul>

[See all news]({{ '/news/' | relative_url }})

Looking for the Iowa State group led by Dr. Patrick Schnable? [Visit their site](https://schnablelab.plantgenomics.iastate.edu/).
