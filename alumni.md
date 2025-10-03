---
layout: page
title: Schnable Lab Alumni

googlefonts: ["Monoton", "Lobster"]
---

[Current Lab Members](/people)

{% assign alumni_groups = site.data.alumni %}
{% assign alumni_nav = alumni_groups | map: 'title' %}

**Browse Alumni by Group**

<ul>
{% for title in alumni_nav %}
  <li><a href="#{{ title | slugify }}">{{ title }}</a></li>
{% endfor %}
</ul>

{% assign alumni_records = site.data.people | where: 'status', 'alumni' %}
{% if alumni_records and alumni_records.size > 0 %}
## Recent Alumni
<ul class="people-grid">
{% for person in alumni_records %}
  {% assign person_url = nil %}
  {% if person.page_path %}
    {% assign detail_page = site.pages | where: 'path', person.page_path | first %}
    {% if detail_page %}
      {% assign person_url = detail_page.url %}
    {% endif %}
  {% elsif person.page %}
    {% assign person_url = person.page %}
  {% endif %}
  {% assign detail_url = nil %}
  {% assign portrait = person.image | default: '/images/People_Images/placeholder.jpg' %}
  {% if portrait contains '://' %}
    {% assign portrait_path = portrait %}
  {% else %}
    {% assign portrait_path = portrait | relative_url %}
  {% endif %}
  {% if person_url %}
    {% if person_url contains '://' %}
      {% assign detail_url = person_url %}
    {% else %}
      {% assign detail_url = person_url | relative_url %}
    {% endif %}
  {% endif %}
  <li class="people-card">
    {% if detail_url %}<a class="people-card__image-link" href="{{ detail_url }}">{% endif %}
    <img class="people-card__image" src="{{ portrait_path }}" alt="{{ person.name | escape }}" />
    {% if detail_url %}</a>{% endif %}
    <h3 class="people-card__name">
      {% if detail_url %}<a href="{{ detail_url }}">{{ person.name }}</a>{% else %}{{ person.name }}{% endif %}
    </h3>
    {% if person.role %}<p class="people-card__role">{{ person.role }}</p>{% endif %}
    <ul class="people-card__meta">
      {% if person.tenure %}<li><strong>Years:</strong> {{ person.tenure }}</li>{% endif %}
      {% if person.current %}<li><strong>Now:</strong> {{ person.current }}</li>{% endif %}
      {% if person.orcid %}<li><a href="https://orcid.org/{{ person.orcid }}">ORCID</a></li>{% endif %}
      {% if person.cv %}<li><a href="{{ person.cv | relative_url }}">CV</a></li>{% endif %}
    </ul>
  </li>
{% endfor %}
</ul>
{% endif %}

{% for group in alumni_groups %}
### {{ group.title }}
{: #{{ group.title | slugify }} }

<ul class="people-grid">
{% for person in group.people %}
  {% assign person_url = person.link %}
  {% assign portrait = person.image | default: '/images/People_Images/placeholder.jpg' %}
  {% assign detail_url = nil %}
  {% if portrait contains '://' %}
    {% assign portrait_path = portrait %}
  {% else %}
    {% assign portrait_path = portrait | relative_url %}
  {% endif %}
  {% if person_url %}
    {% if person_url contains '://' %}
      {% assign detail_url = person_url %}
    {% else %}
      {% assign detail_url = person_url | relative_url %}
    {% endif %}
  {% endif %}
  <li class="people-card">
    {% if detail_url %}<a class="people-card__image-link" href="{{ detail_url }}">{% endif %}
    <img class="people-card__image" src="{{ portrait_path }}" alt="{{ person.name | escape }}" />
    {% if detail_url %}</a>{% endif %}
    <h3 class="people-card__name">
      {% if detail_url %}<a href="{{ detail_url }}">{{ person.name }}</a>{% else %}{{ person.name }}{% endif %}
    </h3>
    {% if person.role %}<p class="people-card__role">{{ person.role }}</p>{% endif %}
    <ul class="people-card__meta">
      {% if person.tenure %}<li><strong>Years:</strong> {{ person.tenure }}</li>{% endif %}
      {% if person.current %}<li><strong>Now:</strong> {{ person.current }}</li>{% endif %}
      {% if person.orcid %}<li><a href="https://orcid.org/{{ person.orcid }}">ORCID</a></li>{% endif %}
    </ul>
  </li>
{% endfor %}
</ul>
{% endfor %}
