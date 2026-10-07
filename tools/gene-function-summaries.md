---
layout: page
title: "Gene Function Summaries"
permalink: /tools/gene-function-summaries/
search_exclude: true
sitemap: false
---

<div class="maize-synth-tool" data-baseurl="{{ site.baseurl }}">
  <p class="maize-synth-subtitle">
    Known and inferred phenotypes and functions of genes searchable by gene name or gene model ID.
  </p>

  <section class="maize-synth-search">
    <div class="maize-synth-tabs" role="tablist" aria-label="Search type">
      <button type="button" id="maize-synth-tab-gene" class="maize-synth-tab" role="tab" aria-selected="true" aria-controls="maize-synth-panel-gene">Gene lookup</button>
      <button type="button" id="maize-synth-tab-region" class="maize-synth-tab" role="tab" aria-selected="false" aria-controls="maize-synth-panel-region" tabindex="-1">Region search</button>
    </div>

    <div id="maize-synth-panel-gene" class="maize-synth-panel" role="tabpanel" aria-labelledby="maize-synth-tab-gene">
      <form id="maize-synth-form" class="maize-synth-form">
        <label for="maize-synth-species">Species</label>
        <select id="maize-synth-species" name="species">
          <option value="maize" selected>Maize</option>
          <option value="rice">Rice</option>
          <option value="sorghum">Sorghum</option>
        </select>

        <label for="maize-synth-query">Gene model ID or gene name</label>
        <div class="maize-synth-input-row">
          <input id="maize-synth-query" name="query" type="search" autocomplete="off" spellcheck="false" placeholder="Zm00001eb237930, GRMZM2G120408, Sobic.001G000100, Os01g0100100">
          <button type="submit">Search</button>
        </div>
      </form>
      <div id="maize-synth-status" class="maize-synth-status" role="status" aria-live="polite">Loading...</div>
    </div>

    <div id="maize-synth-panel-region" class="maize-synth-panel" role="tabpanel" aria-labelledby="maize-synth-tab-region" hidden>
      <form id="maize-synth-region-form" class="maize-synth-form maize-synth-region-form">
        <div>
          <label for="maize-synth-region-species">Species</label>
          <select id="maize-synth-region-species" name="species">
            <option value="maize" selected>Maize</option>
            <option value="sorghum">Sorghum</option>
            <option value="rice">Rice</option>
          </select>
        </div>
        <div>
          <label for="maize-synth-region-chr">Chromosome</label>
          <select id="maize-synth-region-chr" name="chr"></select>
        </div>
        <div>
          <label for="maize-synth-region-start">Start (bp)</label>
          <input id="maize-synth-region-start" name="start" type="text" inputmode="numeric" autocomplete="off" placeholder="1,000,000">
        </div>
        <div>
          <label for="maize-synth-region-end">End (bp)</label>
          <input id="maize-synth-region-end" name="end" type="text" inputmode="numeric" autocomplete="off" placeholder="2,000,000">
        </div>
        <button type="submit">Find genes</button>
      </form>
      <p id="maize-synth-region-assembly" class="maize-synth-region-assembly"></p>
      <div id="maize-synth-region-status" class="maize-synth-status" role="status" aria-live="polite"></div>
    </div>
  </section>

  <section id="maize-synth-region-result" class="maize-synth-region-result" hidden>
    <div class="maize-synth-result__header">
      <h2 id="maize-synth-region-heading"></h2>
      <a id="maize-synth-region-download" class="maize-synth-share" href="#">Download TSV</a>
    </div>
    <ul id="maize-synth-region-list" class="maize-synth-region-list"></ul>
  </section>

  <section id="maize-synth-choices" class="maize-synth-choices" hidden>
    <ul id="maize-synth-choice-list"></ul>
  </section>

  <section id="maize-synth-result" class="maize-synth-result" hidden>
    <div class="maize-synth-result__header">
      <div>
        <h2 id="maize-synth-gene-title"></h2>
        <p id="maize-synth-gene-meta" class="maize-synth-gene-meta"></p>
      </div>
      <a id="maize-synth-share" class="maize-synth-share" href="#">Copy link</a>
    </div>
    <h3>Function phrase</h3>
    <p id="maize-synth-phrase"></p>
    <h3>Function sentence</h3>
    <p id="maize-synth-sentence"></p>
    <h3>Annotation abstract</h3>
    <p id="maize-synth-abstract"></p>
    <div id="maize-synth-orthologs-section" hidden>
      <h3>Function of orthologs</h3>
      <ul id="maize-synth-orthologs" class="maize-synth-orthologs"></ul>
    </div>
    <div id="maize-synth-papers-section" hidden>
      <h3>Relevant papers</h3>
      <ol id="maize-synth-papers" class="maize-synth-papers"></ol>
    </div>
  </section>
  <p id="maize-synth-version" class="maize-synth-version"></p>
</div>

<script src="{{ site.baseurl }}/assets/js/gene-function-summaries.js?v={{ site.time | date: "%s" }}" defer></script>
