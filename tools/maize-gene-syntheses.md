---
layout: page
title: "Maize Gene Function Syntheses"
permalink: /tools/maize-gene-syntheses/
search_exclude: true
sitemap: false
---

<div class="maize-synth-tool" data-baseurl="{{ site.baseurl }}">
  <section class="maize-synth-search" aria-labelledby="maize-synth-search-title">
    <div>
      <h2 id="maize-synth-search-title">Gene lookup</h2>
      <p class="maize-synth-intro">
        Search maize direct-evidence synthesis statements by B73 RefGen v3, v4, or v5 gene model ID, or by an unambiguous gene synonym.
      </p>
    </div>
    <form id="maize-synth-form" class="maize-synth-form">
      <label for="maize-synth-query">Gene model ID or synonym</label>
      <div class="maize-synth-input-row">
        <input id="maize-synth-query" name="query" type="search" autocomplete="off" spellcheck="false" placeholder="Zm00001eb237930, GRMZM2G120408, ZmDFR1">
        <button type="submit">Search</button>
      </div>
    </form>
    <div id="maize-synth-status" class="maize-synth-status" role="status" aria-live="polite">Loading lookup index...</div>
  </section>

  <section id="maize-synth-result" class="maize-synth-result" hidden>
    <div class="maize-synth-result__header">
      <div>
        <p class="maize-synth-kicker">Canonical v5 gene model</p>
        <h2 id="maize-synth-gene-id"></h2>
      </div>
      <a id="maize-synth-share" class="maize-synth-share" href="#">Copy link</a>
    </div>
    <dl class="maize-synth-match">
      <div>
        <dt>Matched term</dt>
        <dd id="maize-synth-match-label"></dd>
      </div>
      <div>
        <dt>Identifier type</dt>
        <dd id="maize-synth-match-type"></dd>
      </div>
    </dl>
    <h3>Function phrase</h3>
    <p id="maize-synth-phrase" class="maize-synth-phrase"></p>
    <h3>Function sentence</h3>
    <p id="maize-synth-sentence"></p>
    <h3>Annotation abstract</h3>
    <p id="maize-synth-abstract"></p>
  </section>
</div>

<script src="{{ site.baseurl }}/assets/js/maize-gene-syntheses.js" defer></script>
