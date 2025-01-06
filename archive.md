---
layout: default
title: Archive
permalink: /archive/
---

# Poetry Archive

{% assign postsByYear = site.posts | group_by_exp:"post", "post.date | date: '%Y'" %}
{% for year in postsByYear %}
## {{ year.name }}

{% for post in year.items %}
- [{{ post.title }}]({{ post.url | relative_url }}) - {{ post.date | date: "%B %d" }}
{% endfor %}

{% endfor %}