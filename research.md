---
layout: page
title: Schnable Lab Research Interests
---

Research in the Schnable Lab@UNL is an interdisciplinary endeavor. Here are our main focus areas:

<nav class="research-nav" aria-label="Research topics">
  <a href="#Phenotyping" class="research-nav__btn">Phenotyping</a>
  <a href="#QuantGen" class="research-nav__btn">Quantitative Genetics</a>
  <a href="#Genomics" class="research-nav__btn">Genomics</a>
  <a href="#AIML" class="research-nav__btn">AI/ML</a>
</nav>

{% comment %} in-review papers are tracked in publications.yml but never rendered on the site {% endcomment %}
{% assign all_pubs = site.data.publications | where_exp: "pub", "pub.status != 'in-review'" | sort: "year" | reverse %}
{% assign lab_first_pubs = all_pubs | where: "first_author_is_lab_member", true %}

<section id="Phenotyping" class="research-section">
<div class="research-section__inner">
<div class="research-section__content">
<h2>Phenotyping</h2>

<p>Developing and testing new approaches to measure plants, from greenhouses to fields to satellites. We collaborate closely with engineers and statisticians both here at UNL and at other universities around the world to develop and deploy new algorithms, tools, and datasets for high throughput plant phenotyping.</p>

<details class="research-details">
<summary>Recent Lab Publications on Phenotyping</summary>
<ul>
{% assign pheno1 = lab_first_pubs | where_exp: "pub", "pub.tags contains 'phenomics'" %}
{% assign pheno2 = lab_first_pubs | where_exp: "pub", "pub.tags contains 'image-analysis'" %}
{% assign phenotyping_pubs = pheno1 | concat: pheno2 | uniq | sort: "year" | reverse %}
{% for pub in phenotyping_pubs limit: 8 %}
<li>{% for author in pub.authors %}{% if author.truncated %}...{% elsif author.member_id %}<strong>{{ author.name }}</strong>{% else %}{{ author.name }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %} ({{ pub.year }}) "<a href="{{ pub.url }}">{{ pub.title }}</a>" <em>{{ pub.journal }}</em>{% if pub.doi %} doi: <a href="https://doi.org/{{ pub.doi }}">{{ pub.doi }}</a>{% endif %}</li>
{% endfor %}
</ul>
</details>

</div>
<div class="research-section__image">
<img src="/images/optimized/Science_Images/HTPMerged.jpg" alt="Plant imaging, a robotic sensor system, aerial field plots, and a soil electrical conductivity map" width="400" height="300" loading="lazy" decoding="async" />
</div>
</div>
</section>

<section id="QuantGen" class="research-section research-section--alt">
<div class="research-section__inner research-section__inner--reverse">
<div class="research-section__content">
<h2>Quantitative Genetics</h2>

<p>Collecting genetic, molecular, and trait data from large populations to understand how genes and environment shape phenotypes. We develop and apply statistical approaches that leverage unique features of new phenotypic datasets, including time-series data from whole mapping populations collected using high throughput phenotyping technologies.</p>

<details class="research-details">
<summary>Recent Lab Publications on Quantitative Genetics</summary>
<ul>
{% assign qg1 = lab_first_pubs | where_exp: "pub", "pub.tags contains 'association-studies'" %}
{% assign qg2 = lab_first_pubs | where_exp: "pub", "pub.tags contains 'quantitative-genetics'" %}
{% assign quantgen_pubs = qg1 | concat: qg2 | uniq | sort: "year" | reverse %}
{% for pub in quantgen_pubs limit: 8 %}
<li>{% for author in pub.authors %}{% if author.truncated %}...{% elsif author.member_id %}<strong>{{ author.name }}</strong>{% else %}{{ author.name }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %} ({{ pub.year }}) "<a href="{{ pub.url }}">{{ pub.title }}</a>" <em>{{ pub.journal }}</em>{% if pub.doi %} doi: <a href="https://doi.org/{{ pub.doi }}">{{ pub.doi }}</a>{% endif %}</li>
{% endfor %}
</ul>
</details>

</div>
<div class="research-section__image">
<img src="/images/optimized/Science_Images/QGMerged.jpg" alt="Trait association and correlation plots, allele frequencies, linkage decay, and population structure in four grass crops" width="400" height="300" loading="lazy" decoding="async" />
</div>
</div>
</section>

<section id="Genomics" class="research-section">
<div class="research-section__inner">
<div class="research-section__content">
<h2>Genomics</h2>

<p>Using comparative genomics to engineer more stress-tolerant and resource-use-efficient plants. We utilize cross-species comparisons to separate functional from non-functional portions of plant genomes and predict the functions of conserved sequences.</p>

<details class="research-details">
<summary>Recent Lab Publications on Genomics</summary>
<ul>
{% assign genomics_pubs = lab_first_pubs | where_exp: "pub", "pub.tags contains 'genomics'" %}
{% for pub in genomics_pubs limit: 8 %}
<li>{% for author in pub.authors %}{% if author.truncated %}...{% elsif author.member_id %}<strong>{{ author.name }}</strong>{% else %}{{ author.name }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %} ({{ pub.year }}) "<a href="{{ pub.url }}">{{ pub.title }}</a>" <em>{{ pub.journal }}</em>{% if pub.doi %} doi: <a href="https://doi.org/{{ pub.doi }}">{{ pub.doi }}</a>{% endif %}</li>
{% endfor %}
</ul>
</details>

</div>
<div class="research-section__image">
<img src="/images/optimized/Science_Images/CompGenMerged.jpg" alt="Grass evolutionary relationships, conserved gene order, maize and sorghum stems, and chromosome synteny" width="400" height="300" loading="lazy" decoding="async" />
</div>
</div>
</section>

<section id="AIML" class="research-section research-section--alt">
<div class="research-section__inner research-section__inner--reverse">
<div class="research-section__content">
<h2>AI/ML</h2>

<p>Applying artificial intelligence and machine learning approaches across our research areas. From deep learning models for image-based phenotyping to neural networks for genomic prediction, we leverage modern computational methods to extract insights from large biological datasets.</p>

<details class="research-details">
<summary>Recent Lab Publications on AI/ML</summary>
<ul>
{% assign aiml_pubs = all_pubs | where_exp: "pub", "pub.tags contains 'ai-ml'" %}
{% for pub in aiml_pubs limit: 8 %}
<li>{% for author in pub.authors %}{% if author.truncated %}...{% elsif author.member_id %}<strong>{{ author.name }}</strong>{% else %}{{ author.name }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %} ({{ pub.year }}) "<a href="{{ pub.url }}">{{ pub.title }}</a>" <em>{{ pub.journal }}</em>{% if pub.doi %} doi: <a href="https://doi.org/{{ pub.doi }}">{{ pub.doi }}</a>{% endif %}</li>
{% endfor %}
</ul>
</details>

</div>
</div>
</section>
