---
---
(function () {
  const searchInput = document.getElementById('search-input');
  const resultsList = document.getElementById('search-results');
  if (!searchInput || !resultsList) return;

  let documents = [];
  let index;

  const renderResults = (results) => {
    resultsList.innerHTML = '';
    if (!results.length) {
      const li = document.createElement('li');
      li.className = 'news-list__item';
      li.textContent = 'No matching pages found yet. Try another keyword or search by topic.';
      resultsList.appendChild(li);
      return;
    }

    results.slice(0, 20).forEach((result) => {
      const doc = documents.find((entry) => entry.url === result.ref);
      if (!doc) return;

      const li = document.createElement('li');
      li.className = 'news-list__item';

      const link = document.createElement('a');
      link.href = doc.url;
      link.textContent = doc.title;

      const excerpt = document.createElement('p');
      excerpt.textContent = doc.excerpt;

      li.appendChild(link);
      li.appendChild(excerpt);
      resultsList.appendChild(li);
    });
  };

  const buildIndex = () => {
    index = lunr(function () {
      this.ref('url');
      this.field('title', { boost: 10 });
      this.field('content');

      documents.forEach((doc) => this.add(doc));
    });
  };

  const hydrateDocuments = (rawDocs) => {
    documents = rawDocs.map((doc) => {
      const normalizedContent = doc.content.replace(/\s+/g, ' ').trim();
      const excerpt = normalizedContent.slice(0, 220) + (normalizedContent.length > 220 ? '…' : '');
      return {
        title: doc.title,
        url: doc.url,
        content: normalizedContent,
        excerpt,
      };
    });
  };

  fetch('{{ '/search.json' | relative_url }}')
    .then((response) => response.json())
    .then((data) => {
      hydrateDocuments(data);
      buildIndex();
    })
    .catch((error) => {
      console.error('Search index failed to load', error);
    });

  const performSearch = (term) => {
    if (!index || !term) {
      resultsList.innerHTML = '';
      return;
    }
    const results = index.search(term + '*');
    renderResults(results);
  };

  searchInput.addEventListener('input', (event) => {
    const query = event.target.value.trim();
    if (query.length < 2) {
      resultsList.innerHTML = '';
      return;
    }
    performSearch(query);
  });
})();
