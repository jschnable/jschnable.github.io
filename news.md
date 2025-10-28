---
layout: page
title: Schnable Lab News
googlefonts: ["Monoton", "Lobster"]
---

## Recent Highlights

{% assign sorted_news = site.data.news | sort: 'date' | reverse %}
{% assign recent_news = sorted_news | slice: 0, 6 %}
{% assign recent_month_keys = '' %}
{% for item in recent_news %}
  {% assign month_key = item.date | date: '%Y-%m' %}
  {% unless recent_month_keys contains month_key %}
    {% assign recent_month_keys = recent_month_keys | append: month_key | append: ',' %}
  {% endunless %}
{% endfor %}
{% assign recent_month_count = recent_month_keys | split: ',' | size | minus: 1 %}
<ul class="news-list">
{% for item in recent_news %}
  <li class="news-list__item">
    <time datetime="{{ item.date | date: '%Y-%m-%d' }}">{{ item.date | date: '%B %d, %Y' }}</time>
    <strong>{{ item.title }}</strong><br />
    {% assign summary_html = item.summary | markdownify | strip_newlines | replace: '<p>', '' | replace: '</p>', '' %}
    {{ summary_html }}
  </li>
{% endfor %}
</ul>

## Archive

<div class="news-archive">
{% assign grouped = sorted_news | group_by_exp: 'entry', "entry.date | date: '%B %Y'" %}
{% assign archive_headings_displayed = 0 %}
{% assign skip_counter = 0 %}
{% for group in grouped %}
  {% if skip_counter < recent_month_count %}
    {% assign skip_counter = skip_counter | plus: 1 %}
    {% continue %}
  {% endif %}
  {% if archive_headings_displayed < 3 %}
### {{ group.name }}
  <ul class="news-list">
  {% for entry in group.items %}
      <li class="news-list__item">
        <strong>{{ entry.title }}</strong><br />
        {% assign entry_summary = entry.summary | markdownify | strip_newlines | replace: '<p>', '' | replace: '</p>', '' %}
        {{ entry_summary }}
      </li>
    {% endfor %}
    </ul>
  {% assign archive_headings_displayed = archive_headings_displayed | plus: 1 %}
  {% else %}
  <details>
    <summary>{{ group.name }}</summary>
    <ul class="news-list">
    {% for entry in group.items %}
      <li class="news-list__item">
        <strong>{{ entry.title }}</strong><br />
        {% assign entry_summary = entry.summary | markdownify | strip_newlines | replace: '<p>', '' | replace: '</p>', '' %}
        {{ entry_summary }}
      </li>
    {% endfor %}
    </ul>
  </details>
  {% endif %}
{% endfor %}
</div>

Looking for earlier stories? Browse the [full archive]({{ '/news-archive/' | relative_url }}).
