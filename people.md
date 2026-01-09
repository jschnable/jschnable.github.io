---
layout: page
title: Schnable Lab Members

googlefonts: ["Monoton", "Lobster"]
---

[Lab Alumni 2014-Present](/alumni)

{% assign category_labels = 'Faculty|Research Staff|Professional Staff|Graduate Students|Undergraduate Researchers|High-school intern' | split: '|' %}
{% for label in category_labels %}
  {% assign singles = site.data.people | where: 'category', label %}
  {% assign multi_candidates = site.data.people | where_exp: 'person', 'person.categories' %}
  {% assign multi = multi_candidates | where_exp: 'person', 'person.categories contains label' %}
  {% assign combined = singles | concat: multi %}
  {% assign filtered = combined | where_exp: 'person', 'person.status != "alumni"' %}
  {% assign group = filtered | uniq %}
  {% if group.size > 0 %}
### {{ label }}
  <ul class="people-grid">
  {% for person in group %}
    {% assign person_url = nil %}
    {% if person.page_path %}
      {% assign detail_page = site.pages | where: 'path', person.page_path | first %}
      {% if detail_page %}
        {% assign person_url = detail_page.url %}
      {% endif %}
    {% elsif person.page %}
      {% assign person_url = person.page %}
    {% endif %}
    {% assign portrait = person.image | default: '/images/optimized/People_Images/placeholder.jpg' %}
    {% assign safe_name = person.name | escape %}
    <li class="people-card">
      {% if person_url %}<a class="people-card__image-link" href="{{ person_url | relative_url }}" aria-label="View profile for {{ safe_name }}">{% endif %}
      <img class="people-card__image" src="{{ portrait | relative_url }}" alt="{{ safe_name }}" loading="lazy" decoding="async" />
      {% if person_url %}</a>{% endif %}
      <h3 class="people-card__name">
        {% if person_url %}<a href="{{ person_url | relative_url }}">{{ safe_name }}</a>{% else %}{{ safe_name }}{% endif %}
      </h3>
      <p class="people-card__role">{{ person.role | escape }}</p>
      {% if person_url %}
        <a class="people-card__cta" href="{{ person_url | relative_url }}">View profile →</a>
      {% endif %}
      {% assign link_count = 0 %}
      {% if person.cv %}{% assign link_count = link_count | plus: 1 %}{% endif %}
      {% if person.orcid %}{% assign link_count = link_count | plus: 1 %}{% endif %}
      {% if person.scholar %}{% assign link_count = link_count | plus: 1 %}{% endif %}
      {% if person.github %}{% assign link_count = link_count | plus: 1 %}{% endif %}
      {% if person.socials %}{% assign link_count = link_count | plus: person.socials.size %}{% endif %}
      {% if link_count > 0 %}
      <ul class="people-card__links">
        {% if person.cv %}<li><a href="{{ person.cv | relative_url }}">CV</a></li>{% endif %}
        {% if person.orcid %}<li><a href="https://orcid.org/{{ person.orcid }}">ORCID</a></li>{% endif %}
        {% if person.scholar %}
          {% assign scholar_url = person.scholar %}
          {% unless scholar_url contains '://' %}
            {% assign scholar_url = 'https://scholar.google.com/citations?user=' | append: person.scholar %}
          {% endunless %}
          <li><a href="{{ scholar_url }}">Google Scholar</a></li>
        {% endif %}
        {% if person.github %}    
          {% assign github_url = person.github %}    
          {% unless github_url contains '://' %}      
            {% assign github_url = 'https://github.com/' | append: person.github %}    
          {% endunless %}    
          <li><a href="{{ github_url }}">GitHub</a></li>
        {% endif %}
        {% if person.socials %}
          {% for social in person.socials %}
            <li><a href="{{ social.url }}">{{ social.label }}</a></li>
          {% endfor %}
        {% endif %}
      </ul>
      {% endif %}
    </li>
  {% endfor %}
  </ul>
  {% endif %}
{% endfor %}
