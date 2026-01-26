---
layout: page
title: "Project 1: IMRI - Integrated Magnetic Resonance Imaging"
description: 
img: 
importance: 1
category: work
related_publications: true
---

Magnetic resonance (MR) imaging is an essential tool for diagnostics and health management.  Wait times are long and increasing for MR examinations in Canada, averaging approximately 9.3 weeks in 2019.  Long wait times adversely impact personalized healthcare by delaying subsequent health services, leading to late diagnosis, poorer patient outcomes, and increased cost to both individuals and the health care system.

According to the 2019 “The Value of Radiology report,” the direct annual costs to the Canadian economy related to MR imaging diagnostics is &#36;$700M.  The indirect annual costs incurred due to excessive MR wait times are estimated to be an additional &#36;$700M.

The time required to complete an MR exam often exceeds 45 minutes, but deep-learning-based image reconstruction methods have shown favourable results to reduce MR imaging examination times by reconstructing images from under-sampled acquisitions.  These sophisticated reconstruction methods can increase patient throughput and reduce wait times.  In practice, existing deep-learning models for MR reconstruction do not consider existing redundancies in the data, such as multi-sequence and multi-visit data (i.e., personalized data).  These models often do not generalize well between different scanners. Automated deep learning (AutoDL) provides a framework to develop algorithms capable of fine-tuning image reconstruction models to specific users and use-cases without the intervention of a data scientist. 

This project will develop AutoDL reconstruction methods that incorporate redundancies in the data, such as past subject-specific information, to make MR diagnostics more efficient.  We propose developing a software application called MRIntelligence, which combines these innovations to reduce MR examination times by a factor of ten and to expedite scans' analysis, thus significantly improving personalized healthcare delivery and reducing MR-related expenses.


<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/project_contents/project01_figure.png" title="project 01 figure" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Pilot results of a brain MR imaging exam accelerated by a factor of 20. On the top left, a conventional, deep-learning-based MR image reconstruction approach and its magnified residual map. In the bottom left, the iMRI reconstruction On the right, the fully sampled reconstruction reference. Higher SSIM and pSNR, and lower NRMSE correspond to higher-fidelity reconstructions.
</div>
