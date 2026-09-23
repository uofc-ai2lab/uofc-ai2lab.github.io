---
layout: page
title: Alumni
permalink: /alumni/
nav: true
nav_order: 4
---

<div class="alumni-page">

  <aside class="alumni-sidebar">
    <button class="alumni-tab active" data-category="postdocs">Former Postdoctoral Fellows</button>
    <button class="alumni-tab" data-category="phd">Former PhD Students</button>
    <button class="alumni-tab" data-category="msc">Former MSc Students</button>
    <button class="alumni-tab" data-category="interns">Former Summer Interns</button>
  </aside>


 
  <div class="alumni-content">
    
    <!-- Former Postdoctoral Fellows -->
    <section class="alumni-category-panel active" data-category="postdocs">
      <h2>Former Postdoctoral Fellows</h2>

      <div class="alumni-list">

        <!-- Alumni: Mumu Aktar -->
        <div class="alumni-member">
          <div class="alumni-photo"><img src="{{ '/assets/img/alumni/Mumu_Aktar.jpg' | relative_url }}" alt="Mumu Aktar"></div>

          <div class="alumni-info">
            <h3 class="alumni-name">Mumu Aktar</h3>
            <div class="alumni-dept">Electrical and Software Engineering (University of Calgary)</div>

            <div class="alumni-links">
              <a href="https://scholar.google.com/citations?hl=en&user=EBFetcQAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar</a>
              <a href="https://ca.linkedin.com/in/mumu-aktar" target="_blank" rel="noopener noreferrer">LinkedIn</a>
            </div>
          </div>
        </div>


        <!-- Alumni: Kaue Duarte -->
        <div class="alumni-member">
          <div class="alumni-photo"><img src="{{ '/assets/img/alumni/Kaue_Duarte.jpg' | relative_url }}" alt="Kaue Duarte"></div>

          <div class="alumni-info">
            <h3 class="alumni-name">Kaue Duarte</h3>
            <div class="alumni-dept">Biomedical Engineering (University of Calgary)</div>

            <div class="alumni-links">
              <a href="https://scholar.google.com/citations?hl=en&user=Fr7gWkkAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar</a>
              <a href="https://ca.linkedin.com/in/kauetnduarte" target="_blank" rel="noopener noreferrer">LinkedIn</a>
            </div>
          </div>
        </div>


        <!-- Alumni: Amir Shamaei -->
        <div class="alumni-member">
          <div class="alumni-photo"><img src="{{ '/assets/img/alumni/Amir_Shamaei.jpg' | relative_url }}" alt="Amir Shamaei"></div>

          <div class="alumni-info">
            <h3 class="alumni-name">Amir Shamaei</h3>
            <div class="alumni-dept">Electrical and Software Engineering (University of Calgary)</div>

            <div class="alumni-links">
              <a href="https://scholar.google.com/citations?user=irO6ttAAAAAJ&hl=en" target="_blank" rel="noopener noreferrer">Google Scholar</a>
              <a href="https://ca.linkedin.com/in/amshamaei" target="_blank" rel="noopener noreferrer">LinkedIn</a>
            </div>
          </div>
        </div>

      </div>
    </section>






    <!-- Former PhD Students -->
    <section class="alumni-category-panel" data-category="phd">
      <h2>Former PhD Students</h2>

      <div class="alumni-list">
      
        <!-- Alumni: Hanna Bugler -->
        <div class="alumni-member">
          <div class="alumni-photo"><img src="{{ '/assets/img/alumni/Hanna_Bugler.png' | relative_url }}" alt="Hanna Bugler"></div>

          <div class="alumni-info">
            <h3 class="alumni-name">Hanna Bugler</h3>
            <div class="alumni-dept">Biomedical Engineering (University of Calgary)</div>

            <div class="alumni-links">
              <a href="" target="_blank" rel="noopener noreferrer">Google Scholar</a>
              <a href="https://www.linkedin.com/in/hanna-b-4b013414a/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
            </div>
          </div>
        </div>


        <!-- Alumni: Mohammad Sahnoon -->
        <div class="alumni-member">
          <div class="alumni-photo"><img src="{{ '/assets/img/alumni/Mohammad_Sahnoon.jpg' | relative_url }}" alt="Mohammad Sahnoon"></div>

          <div class="alumni-info">
            <h3 class="alumni-name">Mohammad Sahnoon</h3>
            <div class="alumni-dept">Electrical and Software Engineering (University of Calgary)</div>

            <div class="alumni-links">
              <a href="https://scholar.google.com/citations?user=GykKBo4AAAAJ&hl=en" target="_blank" rel="noopener noreferrer">Google Scholar</a>
              <a href="https://www.linkedin.com/in/mohammadsahnoon/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
            </div>
          </div>
        </div>


        <!-- Alumni: Alexandre Lopes -->
        <div class="alumni-member">
          <div class="alumni-photo"><img src="{{ '/assets/img/alumni/Alexandre_Lopes.png' | relative_url }}" alt="Alexandre Lopes"></div>

          <div class="alumni-info">
            <h3 class="alumni-name">Alexandre Lopes</h3>
            <div class="alumni-dept">Computer Science (University of Campinas)</div>

            <div class="alumni-links">
              <a href="https://scholar.google.com/citations?user=KeHisO8AAAAJ&hl=en" target="_blank" rel="noopener noreferrer">Google Scholar</a>
              <a href="https://www.linkedin.com/in/alexandreribeirolopes/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
            </div>
          </div>
        </div>


      </div>
    </section>





    <!-- Former MSc Students -->
    <section class="alumni-category-panel" data-category="msc">
      <h2>Former MSc Students</h2>

      <div class="alumni-list">



      </div>
    </section>


    <!-- Former Summer Interns -->

    <section class="alumni-category-panel" data-category="interns">
      <h2>Former Summer Interns</h2>

      <div class="alumni-list">

        

      </div>
    </section>

    
  </div>
</div>






<script>
  document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll(".alumni-tab");
    const panels = document.querySelectorAll(".alumni-category-panel");

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {

        const category = this.dataset.category;

        tabs.forEach(function (item) {
          item.classList.remove("active");
        });

        panels.forEach(function (panel) {
          panel.classList.remove("active");
        });

        this.classList.add("active");

        const selectedPanel = document.querySelector(
          '.alumni-category-panel[data-category="' + category + '"]'
        );

        if (selectedPanel) {
          selectedPanel.classList.add("active");
        }
        
      });
    });
  });
</script>
