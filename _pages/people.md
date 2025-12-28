---
layout: page
title: people
permalink: /labmembers/
# description: Lab Members
nav: true
nav_order: 3
display_categories: [Faculty Members, Postdoctoral Fellows, PhD Students, MSc Students, Research Associates, Undergraduate Students, Alumni]
horizontal: false
---



# AI2Lab Members

<!-- pages/people.md -->
<div class="people">
  <!-- Display categorized people -->
  {%- for category in page.display_categories %}
  <h2 class="category">{{ category }}</h2>
  {%- assign categorized_people = site.people | where: "category", category -%}
  {%- assign sorted_people = categorized_people | sort: "lastname" %}
  <!-- Generate cards for each person -->
  <div class="grid">
    {%- for person in sorted_people -%}
      {%- if person.show -%}
        {% include people.liquid %}
      {%- endif -%}
    {%- endfor %}
  </div>
  {% endfor %}
</div>
