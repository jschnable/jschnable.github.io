(function () {
  const root = document.querySelector(".maize-synth-tool");
  if (!root) return;

  const baseUrl = root.dataset.baseurl || "";
  const dataBase = `${baseUrl}/assets/data/maize-gene-syntheses`;
  const form = document.getElementById("maize-synth-form");
  const speciesSelect = document.getElementById("maize-synth-species");
  const queryInput = document.getElementById("maize-synth-query");
  const statusEl = document.getElementById("maize-synth-status");
  const resultEl = document.getElementById("maize-synth-result");
  const shareEl = document.getElementById("maize-synth-share");
  const fields = {
    geneId: document.getElementById("maize-synth-gene-id"),
    matchLabel: document.getElementById("maize-synth-match-label"),
    matchType: document.getElementById("maize-synth-match-type"),
    phrase: document.getElementById("maize-synth-phrase"),
    sentence: document.getElementById("maize-synth-sentence"),
    abstract: document.getElementById("maize-synth-abstract"),
  };

  let lookupIndex = null;
  const shardCache = new Map();

  function normalizeQuery(value) {
    return (value || "").trim().toLowerCase().replace(/\s+/g, " ");
  }

  function setStatus(message, kind) {
    statusEl.textContent = message;
    statusEl.dataset.kind = kind || "info";
  }

  function setText(node, value) {
    node.textContent = value || "No statement available.";
  }

  function updateUrl(query) {
    const url = new URL(window.location.href);
    url.searchParams.set("q", query);
    window.history.replaceState({}, "", url);
  }

  async function fetchJson(url) {
    const response = await fetch(url, { cache: "force-cache" });
    if (!response.ok) {
      throw new Error(`Unable to load ${url}`);
    }
    return response.json();
  }

  async function loadLookup() {
    if (lookupIndex) return lookupIndex;
    lookupIndex = await fetchJson(`${dataBase}/lookup.json`);
    setStatus("Ready.", "ready");
    return lookupIndex;
  }

  async function loadShard(shard) {
    if (shardCache.has(shard)) return shardCache.get(shard);
    const shardData = await fetchJson(`${dataBase}/shards/${encodeURIComponent(shard)}.json`);
    shardCache.set(shard, shardData);
    return shardData;
  }

  async function search(rawQuery, options) {
    const normalized = normalizeQuery(rawQuery);
    if (!normalized) {
      resultEl.hidden = true;
      setStatus("Enter a gene model ID or gene name.", "warn");
      return;
    }

    if (speciesSelect && speciesSelect.value !== "maize") {
      resultEl.hidden = true;
      setStatus("This species is not available yet.", "warn");
      return;
    }

    setStatus("Searching...", "info");
    const lookup = await loadLookup();
    const match = lookup[normalized];
    if (!match) {
      resultEl.hidden = true;
      setStatus(`No gene match found for "${rawQuery}".`, "warn");
      return;
    }

    const geneId = match[0];
    const label = match[1];
    const type = match[2];
    const shardName = match[3];
    const shard = await loadShard(shardName);
    const record = shard[geneId];
    if (!record) {
      resultEl.hidden = true;
      setStatus(`Matched ${geneId}, but its synthesis record was not found.`, "warn");
      return;
    }

    fields.geneId.textContent = geneId;
    fields.matchLabel.textContent = label || rawQuery;
    fields.matchType.textContent = (type || "synonym").replace(/_/g, " ");
    setText(fields.phrase, record[0]);
    setText(fields.sentence, record[1]);
    setText(fields.abstract, record[2]);
    resultEl.hidden = false;
    setStatus(`Showing synthesis for ${geneId}.`, "ready");

    if (!options || options.updateUrl !== false) {
      updateUrl(rawQuery);
    }
  }

  async function copyShareLink(event) {
    event.preventDefault();
    const url = new URL(window.location.href);
    const link = url.toString();
    try {
      await navigator.clipboard.writeText(link);
      setStatus("Link copied to clipboard.", "ready");
    } catch (error) {
      setStatus(link, "info");
    }
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    search(queryInput.value).catch(function (error) {
      resultEl.hidden = true;
      setStatus(error.message, "error");
    });
  });

  shareEl.addEventListener("click", copyShareLink);

  loadLookup()
    .then(function () {
      const params = new URLSearchParams(window.location.search);
      const initialQuery = params.get("q");
      if (initialQuery) {
        queryInput.value = initialQuery;
        return search(initialQuery, { updateUrl: false });
      }
      return null;
    })
    .catch(function (error) {
      setStatus(error.message, "error");
    });
})();
