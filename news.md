---
layout: page
title: Schnable Lab News
googlefonts: ["Monoton", "Lobster"]
---

## Recent Highlights

{% assign sorted_news = site.data.news | sort: 'date' | reverse %}
{% assign recent_news = sorted_news | slice: 0, 6 %}
{% assign recent_months = '' %}
{% for item in recent_news %}
  {% assign month_label = item.date | date: '%B %Y' %}
  {% unless recent_months contains month_label %}
    {% assign recent_months = recent_months | append: month_label | append: '||' %}
  {% endunless %}
{% endfor %}
<ul class="news-list">
{% for item in recent_news %}
  <li class="news-list__item">
    <time datetime="{{ item.date | date: '%Y-%m-%d' }}">{{ item.date | date: '%B %d, %Y' }}</time>
    <strong>{{ item.title }}</strong><br />
    {{ item.summary }}
  </li>
{% endfor %}
</ul>

## Archive

<div class="news-archive">
{% assign grouped = sorted_news | group_by_exp: 'entry', "entry.date | date: '%B %Y'" %}
{% for group in grouped %}
  {% if recent_months contains group.name %}
    {% continue %}
  {% endif %}
  {% if forloop.index0 < 3 %}
### {{ group.name }}
  <ul class="news-list">
  {% for entry in group.items %}
    <li class="news-list__item">
      <strong>{{ entry.title }}</strong><br />
      {{ entry.summary }}
    </li>
  {% endfor %}
  </ul>
  {% else %}
  <details>
    <summary>{{ group.name }}</summary>
    <ul class="news-list">
    {% for entry in group.items %}
      <li class="news-list__item">
        <strong>{{ entry.title }}</strong><br />
        {{ entry.summary }}
      </li>
    {% endfor %}
    </ul>
  </details>
  {% endif %}
{% endfor %}
</div>

Looking for earlier stories? Browse the [full archive]({{ '/news-archive/' | relative_url }}).
