(function () {
  const root = document.querySelector(".maize-synth-tool");
  if (!root) return;

  const baseUrl = root.dataset.baseurl || "";
  // Data live in the separate jschnable/gene-function-data repository (GitHub Pages project site on
  // the same domain), so regenerated data never enter this repository's history.
  const dataBase = (root.dataset.dataurl || "/gene-function-data").replace(/\/$/, "");
  // Show the model-written one-line reason under each key paper (preview: decide before publishing).
  const SHOW_PAPER_REASONS = true;
  const speciesConfig = {
    maize: {
      label: "Maize",
      database: "MaizeGDB",
      url: function (id) { return `https://www.maizegdb.org/gene_center/gene/${encodeURIComponent(id)}`; },
    },
    sorghum: {
      label: "Sorghum",
      database: "Phytozome",
      url: function (id) { return `https://phytozome-next.jgi.doe.gov/report/gene/Sbicolor_v5_1/${encodeURIComponent(id)}`; },
    },
    rice: {
      label: "Rice",
      database: "RAP-DB",
      url: function (id) { return `https://rapdb.dna.affrc.go.jp/locus/?name=${encodeURIComponent(id)}`; },
    },
  };
  const evidenceText = {
    lit: "Based on published studies of this gene",
    inferred: "No published studies of this gene; inferred from protein domains, expression and related genes",
    none: "No functional evidence available; standard summary",
    te: "Annotated as a transposable element; standard summary",
    npc: "Non-protein-coding gene without functional evidence; standard summary",
  };
  const pageTitle = document.title;
  const MAX_REGION_ROWS = 2000;
  const orthologOrder = ["maize", "sorghum", "rice"];

  const form = document.getElementById("maize-synth-form");
  const speciesSelect = document.getElementById("maize-synth-species");
  const queryInput = document.getElementById("maize-synth-query");
  const statusEl = document.getElementById("maize-synth-status");
  const resultEl = document.getElementById("maize-synth-result");
  const choicesEl = document.getElementById("maize-synth-choices");
  const choiceListEl = document.getElementById("maize-synth-choice-list");
  const shareEl = document.getElementById("maize-synth-share");
  const versionEl = document.getElementById("maize-synth-version");
  const fields = {
    geneTitle: document.getElementById("maize-synth-gene-title"),
    geneMeta: document.getElementById("maize-synth-gene-meta"),
    phrase: document.getElementById("maize-synth-phrase"),
    sentence: document.getElementById("maize-synth-sentence"),
    abstract: document.getElementById("maize-synth-abstract"),
    papersSection: document.getElementById("maize-synth-papers-section"),
    papers: document.getElementById("maize-synth-papers"),
    orthologsSection: document.getElementById("maize-synth-orthologs-section"),
    orthologs: document.getElementById("maize-synth-orthologs"),
  };

  const region = {
    form: document.getElementById("maize-synth-region-form"),
    species: document.getElementById("maize-synth-region-species"),
    chr: document.getElementById("maize-synth-region-chr"),
    start: document.getElementById("maize-synth-region-start"),
    end: document.getElementById("maize-synth-region-end"),
    assembly: document.getElementById("maize-synth-region-assembly"),
    status: document.getElementById("maize-synth-region-status"),
    result: document.getElementById("maize-synth-region-result"),
    heading: document.getElementById("maize-synth-region-heading"),
    list: document.getElementById("maize-synth-region-list"),
    download: document.getElementById("maize-synth-region-download"),
  };
  let regionRows = [];

  // Tabs: each tab keeps its own last result; only the active tab's result is visible.
  const tabs = {
    gene: { tab: document.getElementById("maize-synth-tab-gene"), panel: document.getElementById("maize-synth-panel-gene") },
    region: { tab: document.getElementById("maize-synth-tab-region"), panel: document.getElementById("maize-synth-panel-region") },
  };
  let activeTab = "gene";
  let geneView = null; // "result" | "choices" | null
  let regionShown = false;
  // Each tab's own URL query and page title, restored when switching tabs by hand.
  const tabState = { gene: { search: "", title: "" }, region: { search: "", title: "" } };

  function remember(tab) {
    tabState[tab] = { search: window.location.search, title: document.title };
  }

  function render() {
    resultEl.hidden = !(activeTab === "gene" && geneView === "result");
    choicesEl.hidden = !(activeTab === "gene" && geneView === "choices");
    region.result.hidden = !(activeTab === "region" && regionShown);
  }

  function switchTab(name, focus) {
    if (name === activeTab) return;
    setTab(name, focus);
    const saved = tabState[name];
    window.history.replaceState({}, "", saved.search ? saved.search : window.location.pathname);
    document.title = saved.title || pageTitle;
  }

  function setTab(name, focus) {
    activeTab = name;
    Object.entries(tabs).forEach(function ([key, t]) {
      const selected = key === name;
      t.tab.setAttribute("aria-selected", selected ? "true" : "false");
      t.tab.tabIndex = selected ? 0 : -1;
      t.panel.hidden = !selected;
    });
    if (focus) tabs[name].tab.focus();
    render();
  }

  let metadata = null;
  let dataVersion = "";
  const fileCache = new Map();

  function normalizeQuery(value) {
    return (value || "").trim().toLowerCase().replace(/\s+/g, " ");
  }

  function compactKey(value) {
    return value.replace(/[^a-z0-9]/g, "");
  }

  // 32-bit FNV-1a over UTF-8 bytes; must match scripts/generate_gene_function_summaries.py.
  function fnv1a(value) {
    let hash = 0x811c9dc5;
    for (const byte of new TextEncoder().encode(value)) {
      hash ^= byte;
      hash = Math.imul(hash, 0x01000193) >>> 0;
    }
    return hash >>> 0;
  }

  function pad(number, width) {
    return String(number).padStart(width, "0");
  }

  function setStatus(message, kind) {
    statusEl.textContent = message;
    statusEl.dataset.kind = kind || "info";
  }

  function setText(node, value) {
    node.textContent = value || "No statement available.";
  }

  function getSpecies() {
    return speciesSelect ? speciesSelect.value : "maize";
  }

  // Data files are immutable per data release: their URLs carry the release timestamp, so the
  // browser cache can be used freely; metadata.json is always revalidated to pick up new releases.
  async function fetchJson(path, options) {
    const opts = options || {};
    const url = opts.versioned === false ? path : `${path}?v=${encodeURIComponent(dataVersion)}`;
    if (fileCache.has(url)) return fileCache.get(url);
    const promise = (async function () {
      const response = await fetch(url, { cache: opts.versioned === false ? "no-cache" : "force-cache" });
      if (!response.ok) throw new Error(`Unable to load ${url}`);
      const bytes = new Uint8Array(await response.arrayBuffer());
      // Files are stored gzipped; a server may already have decoded them, so check the magic bytes.
      let text;
      if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
        const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
        text = await new Response(stream).text();
      } else {
        text = new TextDecoder().decode(bytes);
      }
      return JSON.parse(text);
    })();
    fileCache.set(url, promise);
    promise.catch(function () { fileCache.delete(url); });
    return promise;
  }

  async function loadMetadata() {
    if (!metadata) {
      metadata = await fetchJson(`${dataBase}/metadata.json`, { versioned: false });
      dataVersion = metadata.generated_at || "";
    }
    return metadata;
  }

  async function lookupName(species, normalized) {
    const meta = await loadMetadata();
    const compact = compactKey(normalized);
    if (!compact) return null;
    const bucket = pad(fnv1a(compact) % meta.lookup_buckets, 2);
    const data = await fetchJson(`${dataBase}/${species}/lookup/${bucket}.json.gz`);
    return data.n[normalized] || data.c[compact] || null;
  }

  // Exact name first; then transcript/isoform accessions reduced to their gene model.
  async function resolveName(species, normalized) {
    const candidates = [normalized];
    const dotted = normalized.match(/^(.*)\.(\d+)$/); // Sobic.001G195100.1
    if (dotted) candidates.push(dotted[1]);
    const underscored = normalized.match(/^(.*)_[tp]\d+$/); // Zm00001eb000010_T001
    if (underscored) candidates.push(underscored[1]);
    const riceTranscript = normalized.match(/^(os\d\dg\d{7})-\d+$/); // Os01g0100100-01
    if (riceTranscript) candidates.push(riceTranscript[1]);
    for (const value of candidates) {
      const hits = await lookupName(species, value);
      if (hits) return hits;
    }
    return null;
  }

  async function loadGene(species, geneId) {
    const meta = await loadMetadata();
    const shard = pad(fnv1a(geneId.toLowerCase()) % meta.gene_shards, 3);
    const data = await fetchJson(`${dataBase}/${species}/genes/${shard}.json.gz`);
    return data[geneId] || null;
  }

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(function ([key, value]) {
      if (key === "text") node.textContent = value;
      else node.setAttribute(key, value);
    });
    (children || []).forEach(function (child) {
      node.append(child);
    });
    return node;
  }

  function geneHref(species, geneId) {
    const url = new URL(window.location.href);
    url.search = "";
    url.searchParams.set("species", species);
    url.searchParams.set("q", geneId);
    return url.toString();
  }

  function geneLink(species, geneId) {
    const link = el("a", { href: geneHref(species, geneId), text: geneId });
    link.addEventListener("click", function (event) {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.button !== 0) return;
      event.preventDefault();
      navigate(species, geneId);
    });
    return link;
  }

  function renderPapers(papers) {
    fields.papers.replaceChildren();
    if (!papers || !papers.length) {
      fields.papersSection.hidden = true;
      return;
    }
    papers.forEach(function (paper) {
      const [authors, year, title, journal, doi, pmid, , reason] = paper;
      const item = el("li");
      const lead = [authors, year ? `(${year})` : ""].filter(Boolean).join(" ");
      if (lead) item.append(`${lead} `);
      if (title) item.append(el("span", { class: "maize-synth-paper-title", text: `${title}.` }), " ");
      if (journal) item.append(el("em", { text: `${journal}.` }), " ");
      if (doi) {
        item.append("doi: ", el("a", { href: `https://doi.org/${doi}`, rel: "noopener", text: doi }));
      } else if (pmid) {
        item.append("PMID: ", el("a", { href: `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`, rel: "noopener", text: pmid }));
      }
      if (SHOW_PAPER_REASONS && reason) {
        item.append(el("span", { class: "maize-synth-paper-reason", text: reason }));
      }
      fields.papers.append(item);
    });
    fields.papersSection.hidden = false;
  }

  function renderOrthologs(species, orthologs) {
    fields.orthologs.replaceChildren();
    orthologOrder.forEach(function (key) {
      if (key === species || !orthologs || !orthologs[key]) return;
      orthologs[key].forEach(function ([geneId, , phrase]) {
        const item = el("li", {}, [`${speciesConfig[key].label}: `, geneLink(key, geneId)]);
        if (phrase) item.append(` - ${phrase.replace(/\.$/, "")}.`);
        fields.orthologs.append(item);
      });
    });
    fields.orthologsSection.hidden = !fields.orthologs.childElementCount;
  }

  function formatBp(value) {
    return Number(value).toLocaleString("en-US");
  }

  function chromosomeLabel(species, name) {
    const meta = metadata && metadata.species.find(function (s) { return s.key === species; });
    const entry = meta && (meta.chromosomes || []).find(function (c) { return c.name === name; });
    return entry ? entry.label : name;
  }

  function renderGeneMeta(species, geneId) {
    const config = speciesConfig[species];
    fields.geneMeta.replaceChildren(el("a", { href: config.url(geneId), rel: "noopener", text: `View in ${config.database}` }));
  }

  async function showChoices(species, rawQuery, hits) {
    choiceListEl.replaceChildren();
    const records = await Promise.all(hits.map(function (hit) { return loadGene(species, hit[0]); }));
    hits.forEach(function ([geneId], index) {
      const record = records[index] || {};
      const item = el("li", {}, [geneLink(species, geneId)]);
      if (record.n) item.append(` (${record.n})`);
      if (record.p) item.append(` - ${record.p}`);
      choiceListEl.append(item);
    });
    geneView = "choices";
    setTab("gene");
    document.title = `${rawQuery} | ${pageTitle}`;
    remember("gene");
    setStatus(`"${rawQuery}" matches ${hits.length} ${speciesConfig[species].label.toLowerCase()} genes. Choose one.`, "warn");
  }

  async function search(rawQuery, options) {
    const opts = options || {};
    const normalized = normalizeQuery(rawQuery);
    const species = getSpecies();
    geneView = null;
    setTab("gene");
    if (!normalized) {
      setStatus("Enter a gene model ID or gene name.", "warn");
      return;
    }
    setStatus("Searching...", "info");
    const hits = await resolveName(species, normalized);
    if (!hits) {
      setStatus(`No ${speciesConfig[species].label.toLowerCase()} gene match found for "${rawQuery}".`, "warn");
      return;
    }
    if (opts.history) writeHistory(rawQuery, opts.history);
    if (hits.length > 1) {
      await showChoices(species, rawQuery, hits);
      return;
    }
    const geneId = hits[0][0];
    const record = await loadGene(species, geneId);
    if (!record) {
      setStatus(`Matched ${geneId}, but its summary record was not found.`, "warn");
      return;
    }
    const title = record.n ? `${record.n} - ${geneId}` : geneId;
    fields.geneTitle.replaceChildren(title);
    if (evidenceText[record.e]) {
      fields.geneTitle.append(" ", el("span", { class: "maize-synth-evidence", text: `(${evidenceText[record.e]})` }));
    }
    document.title = `${title} | ${pageTitle}`;
    renderGeneMeta(species, geneId);
    setText(fields.phrase, record.p);
    setText(fields.sentence, record.s);
    setText(fields.abstract, record.a);
    renderPapers(record.k);
    renderOrthologs(species, record.o);
    geneView = "result";
    render();
    remember("gene");
    setStatus("", "ready");
  }

  function writeHistory(query, mode) {
    const url = new URL(window.location.href);
    url.search = "";
    url.searchParams.set("q", query);
    url.searchParams.set("species", getSpecies());
    if (mode === "push") window.history.pushState({}, "", url);
    else window.history.replaceState({}, "", url);
  }

  function reportError(error) {
    geneView = null;
    render();
    setStatus(error.message, "error");
  }

  function navigate(species, geneId) {
    speciesSelect.value = species;
    queryInput.value = geneId;
    search(geneId, { history: "push" })
      .then(function () { window.scrollTo({ top: root.offsetTop, behavior: "smooth" }); })
      .catch(reportError);
  }

  // ---------------------------------------------------------------- region search
  function parsePosition(value) {
    const text = (value || "").trim().toLowerCase().replace(/[,\s_]/g, "");
    const match = text.match(/^(\d+(?:\.\d+)?)(kb|mb|k|m)?(bp)?$/);
    if (!match) return null;
    const scale = { kb: 1e3, k: 1e3, mb: 1e6, m: 1e6 }[match[2]] || 1;
    return Math.round(parseFloat(match[1]) * scale);
  }

  function setRegionStatus(message, kind) {
    region.status.textContent = message;
    region.status.dataset.kind = kind || "info";
  }

  function fillChromosomes(selected) {
    const meta = metadata.species.find(function (s) { return s.key === region.species.value; });
    region.chr.replaceChildren();
    if (!meta || !Array.isArray(meta.chromosomes)) {
      setRegionStatus("Region search is not available for this data release.", "warn");
      return;
    }
    meta.chromosomes.forEach(function (c) {
      const option = el("option", { value: c.name, text: c.label, title: `${formatBp(c.max_end)} bp` });
      region.chr.append(option);
    });
    if (selected && meta.chromosomes.some(function (c) { return c.name === selected; })) region.chr.value = selected;
    region.assembly.textContent = `Coordinates: ${meta.assembly}.`;
  }

  async function regionSearch(options) {
    const opts = options || {};
    const species = region.species.value;
    const chrom = region.chr.value;
    const start = parsePosition(region.start.value);
    const end = parsePosition(region.end.value);
    if (start === null || end === null) {
      setRegionStatus("Enter start and end positions in bp (for example 1,000,000 or 1.5 Mb).", "warn");
      return;
    }
    if (end < start) {
      setRegionStatus("The end position must be greater than the start position.", "warn");
      return;
    }
    setRegionStatus("Searching...", "info");
    const rows = await fetchJson(`${dataBase}/${species}/region/${encodeURIComponent(chrom)}.json.gz`);
    regionRows = rows.filter(function (row) { return row[2] >= start && row[1] <= end; });
    if (opts.history) {
      const url = new URL(window.location.href);
      url.search = "";
      url.searchParams.set("species", species);
      url.searchParams.set("chr", chrom);
      url.searchParams.set("start", String(start));
      url.searchParams.set("end", String(end));
      if (opts.history === "push") window.history.pushState({}, "", url);
      else window.history.replaceState({}, "", url);
    }
    const label = `${speciesConfig[species].label} ${chromosomeLabel(species, chrom)}: ${formatBp(start)}–${formatBp(end)}`;
    region.heading.textContent = `${formatBp(regionRows.length)} gene${regionRows.length === 1 ? "" : "s"} in ${label}`;
    document.title = `${label} | ${pageTitle}`;
    region.list.replaceChildren();
    regionRows.slice(0, MAX_REGION_ROWS).forEach(function ([geneId, gStart, gEnd, name, phrase]) {
      const item = el("li", {}, [geneLink(species, geneId)]);
      if (name) item.append(` (${name})`);
      item.append(el("span", { class: "maize-synth-region-pos", text: ` ${formatBp(gStart)}–${formatBp(gEnd)}` }));
      if (phrase) item.append(` - ${phrase}`);
      region.list.append(item);
    });
    regionShown = true;
    setTab("region");
    remember("region");
    region.download.hidden = !regionRows.length;
    const speciesMeta = metadata.species.find(function (s) { return s.key === species; });
    const chromMeta = speciesMeta && (speciesMeta.chromosomes || []).find(function (c) { return c.name === chrom; });
    if (!regionRows.length && chromMeta && start > chromMeta.max_end) {
      setRegionStatus(`${chromMeta.label} genes end at ${formatBp(chromMeta.max_end)} bp; this region lies beyond them.`, "warn");
      return;
    }
    setRegionStatus(regionRows.length > MAX_REGION_ROWS
      ? `Showing the first ${formatBp(MAX_REGION_ROWS)} genes; the TSV download has all ${formatBp(regionRows.length)}.`
      : "", regionRows.length > MAX_REGION_ROWS ? "warn" : "ready");
  }

  function downloadRegion(event) {
    event.preventDefault();
    const species = region.species.value;
    const header = ["gene_id", "preferred_name", "chromosome", "start", "end", "function_phrase"];
    const chrom = region.chr.value;
    const clean = function (v) { return String(v == null ? "" : v).replace(/[\t\n\r]+/g, " "); };
    const lines = [header.join("\t")].concat(regionRows.map(function ([geneId, start, end, name, phrase]) {
      return [geneId, name, chrom, start, end, phrase].map(clean).join("\t");
    }));
    const blob = new Blob([lines.join("\n") + "\n"], { type: "text/tab-separated-values" });
    const link = el("a", {
      href: URL.createObjectURL(blob),
      download: `${species}_chr${chrom}_${parsePosition(region.start.value)}-${parsePosition(region.end.value)}_genes.tsv`,
    });
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(link.href); }, 1000);
  }

  function runFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const species = params.get("species");
    if (species && speciesConfig[species]) speciesSelect.value = species;
    if (params.get("chr") && species && speciesConfig[species]) {
      setStatus("", "ready");
      region.species.value = species;
      fillChromosomes(params.get("chr"));
      const urlStart = parsePosition(params.get("start"));
      const urlEnd = parsePosition(params.get("end"));
      region.start.value = urlStart === null ? params.get("start") || "" : formatBp(urlStart);
      region.end.value = urlEnd === null ? params.get("end") || "" : formatBp(urlEnd);
      return regionSearch().catch(function (error) { setRegionStatus(error.message, "error"); });
    }
    const query = params.get("q");
    if (query) {
      queryInput.value = query;
      return search(query);
    }
    geneView = null;
    setTab("gene");
    document.title = pageTitle;
    setStatus("", "ready");
    return null;
  }

  async function copyShareLink(event) {
    event.preventDefault();
    const link = window.location.href;
    try {
      await navigator.clipboard.writeText(link);
      setStatus("Link copied to clipboard.", "ready");
    } catch (error) {
      setStatus(link, "info");
    }
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    search(queryInput.value, { history: "push" }).catch(reportError);
  });

  speciesSelect.addEventListener("change", function () {
    geneView = null;
    render();
  });

  Object.entries(tabs).forEach(function ([key, t]) {
    t.tab.addEventListener("click", function () { switchTab(key); });
    t.tab.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      switchTab(key === "gene" ? "region" : "gene", true);
    });
  });

  window.addEventListener("popstate", function () {
    Promise.resolve(runFromUrl()).catch(reportError);
  });

  shareEl.addEventListener("click", copyShareLink);

  region.species.addEventListener("change", function () { fillChromosomes(); });
  region.form.addEventListener("submit", function (event) {
    event.preventDefault();
    regionSearch({ history: "push" }).catch(function (error) { setRegionStatus(error.message, "error"); });
  });
  region.download.addEventListener("click", downloadRegion);

  loadMetadata()
    .then(function (meta) {
      if (versionEl) {
        const date = (meta.generated_at || "").slice(0, 10);
        versionEl.textContent = `Data: ${meta.source}, generated ${date}.`;
      }
      fillChromosomes();
      return runFromUrl();
    })
    .catch(reportError);
})();
