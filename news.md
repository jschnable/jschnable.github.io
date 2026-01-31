---
layout: page
title: Schnable Lab News
googlefonts: ["Monoton", "Lobster"]
---

## Recent Highlights

{% assign sorted_news = site.data.news | sort: 'date' | reverse %}
{% assign recent_news = sorted_news | slice: 0, 6 %}
{% assign recent_keys = '' %}
{% for item in recent_news %}
  {% assign key = item.date | append: '|' | append: item.title | append: '||' %}
  {% assign recent_keys = recent_keys | append: key %}
{% endfor %}
{% assign archive_news = '' | split: '' %}
{% for item in sorted_news %}
  {% assign key = item.date | append: '|' | append: item.title | append: '||' %}
  {% unless recent_keys contains key %}
    {% assign archive_news = archive_news | push: item %}
  {% endunless %}
{% endfor %}
<ul class="news-list">
{% for item in recent_news %}
  <li class="news-list__item{% if item.image %} news-list__item--has-image{% endif %}">
    {% if item.image %}<img src="{{ item.image }}" alt="{{ item.title }}" class="news-list__image" width="120" height="90" loading="lazy" decoding="async" />{% endif %}
    <div class="news-list__content">
      <time datetime="{{ item.date | date: '%Y-%m-%d' }}">{{ item.date | date: '%B %d, %Y' }}</time>
      <strong>{{ item.title }}</strong><br />
      {% assign summary_html = item.summary | markdownify | strip_newlines | replace: '<p>', '' | replace: '</p>', '' %}
      {{ summary_html }}
    </div>
  </li>
{% endfor %}
</ul>

## Archive

<div class="news-archive">
{% assign grouped = archive_news | group_by_exp: 'entry', "entry.date | date: '%B %Y'" %}
{% assign archive_headings_displayed = 0 %}
{% for group in grouped %}
  {% if archive_headings_displayed < 3 %}
    <h3>{{ group.name }}</h3>
    <ul class="news-list">
  {% for entry in group.items %}
      <li class="news-list__item{% if entry.image %} news-list__item--has-image{% endif %}">
        {% if entry.image %}<img src="{{ entry.image }}" alt="{{ entry.title }}" class="news-list__image" width="120" height="90" loading="lazy" decoding="async" />{% endif %}
        <div class="news-list__content">
          <strong>{{ entry.title }}</strong><br />
          {% assign entry_summary = entry.summary | markdownify | strip_newlines | replace: '<p>', '' | replace: '</p>', '' %}
          {{ entry_summary }}
        </div>
      </li>
    {% endfor %}
    </ul>
  {% assign archive_headings_displayed = archive_headings_displayed | plus: 1 %}
  {% else %}
  <details>
    <summary>{{ group.name }}</summary>
    <ul class="news-list">
    {% for entry in group.items %}
      <li class="news-list__item{% if entry.image %} news-list__item--has-image{% endif %}">
        {% if entry.image %}<img src="{{ entry.image }}" alt="{{ entry.title }}" class="news-list__image" width="120" height="90" loading="lazy" decoding="async" />{% endif %}
        <div class="news-list__content">
          <strong>{{ entry.title }}</strong><br />
          {% assign entry_summary = entry.summary | markdownify | strip_newlines | replace: '<p>', '' | replace: '</p>', '' %}
          {{ entry_summary }}
        </div>
      </li>
    {% endfor %}
    </ul>
  </details>
  {% endif %}
{% endfor %}
</div>

Looking for earlier stories? Browse the [full archive]({{ '/news-archive/' | relative_url }}).
