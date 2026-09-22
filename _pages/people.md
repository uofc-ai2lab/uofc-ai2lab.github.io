---
layout: page
title: People
permalink: /people/
nav: true
nav_order: 3
display_categories:
  - Research Assistant
  - Postdoctoral Fellows
  - PhD Students
  - MSc Students
horizontal: false
---

<div class="people">

  {%- for category in page.display_categories %}

    <h2 class="category">{{ category }}</h2>

    {%- assign categorized_people = site.people | where: "category", category -%}
    {%- assign sorted_people = categorized_people | sort: "lastname" %}

    <div class="grid">

      {%- for person in sorted_people -%}
        {%- if person.show -%}
          {% include people.liquid %}
        {%- endif -%}
      {%- endfor %}

    </div>

  {%- endfor %}

</div>
