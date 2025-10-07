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
  <p>The Schnable Lab blends field experiments, molecular biology, and computational analytics understand how the genetics of our worlds most important crops.</p>

## What We Study

- **Phenotyping at scale** – pairing field robotics, imaging, and classical agronomy to monitor trait development across environments.
- **Genomics that matters** – linking DNA variation to stress resilience, yield components, and gene regulation in maize and sorghum.
- **Collaborative solutions** – working with breeders, engineers, and data scientists to turn discoveries into deployable tools.

## Recent Highlights

{% assign highlights = site.data.news | sort: 'date' | reverse | slice: 0, 3 %}
<ul class="news-list">
{% for item in highlights %}
  <li class="news-list__item">
    <time datetime="{{ item.date | date: '%Y-%m-%d' }}">{{ item.date | date: '%B %d, %Y' }}</time>
    <strong>{{ item.title }}</strong><br />
    {{ item.summary }}
    {% if item.link %}<br /><a href="{{ item.link }}">Learn more</a>{% endif %}
  </li>
{% endfor %}
</ul>

[See all news]({{ '/news/' | relative_url }})

## Training Across Disciplines

Each lab member gains experience coding, building field equipment, running molecular assays, and communicating results to scientific and public audiences. The cross-training keeps our science grounded in real-world challenges and ensures discoveries translate beyond the lab.

## Join the Lab {#join}

We are always interested in motivated scientists:

- **Undergraduates** can contribute to funded projects or propose UCARE research within our focus areas.
- **Graduate students and postdocs** should reach out with a CV and a short statement of interests; opportunities shift with grant availability.

Check current openings on the [Join the Lab]({{ '/jobs/' | relative_url }}) page, or email Dr. Schnable to start a conversation.

Looking for the Iowa State group led by Dr. Patrick Schnable? [Visit their site](https://schnablelab.plantgenomics.iastate.edu/).
