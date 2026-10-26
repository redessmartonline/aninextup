/* Keep original citations in the article while gathering reference lists at the end. */
(function () {
  const article = document.querySelector('main article');
  if (!article) return;
  const sourceHeading = /^(?:official sources(?: and (?:verification|further reading|remaining details|updates|related anime news|what to watch next|more upcoming anime))?|official release sources|official source|official streaming source|release information source|release sources?|sources(?: and (?:updates|verification|release references))?)$/i;
  const videoWords = /\b(?:trailer|teaser|video|watch|play|youtube)\b/i;
  const sourceWords = /\b(?:official|source|announcement|report|news|website|site|lineup|update|reference)\b/i;
  const isExternal = a => {
    try { const u = new URL(a.getAttribute('href'), location.href); return /^https?:$/.test(u.protocol) && u.origin !== location.origin; }
    catch (_) { return false; }
  };
  const blocks = [];
  const claimed = new Set();
  function take(node) {
    if (!node || claimed.has(node) || [...claimed].some(parent => parent.contains(node))) return;
    blocks.push(node); claimed.add(node);
  }
  // Explicitly marked reference sections contain attribution and explanatory context.
  article.querySelectorAll('.editorial-sources, p.editorial-reference').forEach(take);
  // Collect only named reference lists, not paragraphs discussing source material.
  article.querySelectorAll('.prose h2, .prose h3').forEach(heading => {
    if (!sourceHeading.test(heading.textContent.trim())) return;
    let next = heading.nextElementSibling;
    const group = [];
    while (next && /^(P|UL|OL)$/.test(next.tagName)) {
      const links = [...next.querySelectorAll('a[href]')];
      if (!links.some(isExternal) || links.some(a => !isExternal(a))) break;
      group.push(next); next = next.nextElementSibling;
    }
    if (group.length) { take(heading); group.forEach(take); }
  });
  // Move references from the release box, leaving video and viewing links in place.
  const summaryReferences = [];
  article.querySelectorAll('.release-summary p').forEach(p => {
    const links = [...p.querySelectorAll('a[href]')].filter(a =>
      isExternal(a) && sourceWords.test(a.textContent) && !videoWords.test(a.textContent));
    links.forEach((a, i) => {
      summaryReferences.push(a.cloneNode(true));
      if (i === 0) {
        const jump = document.createElement('a');
        jump.href = '#article-sources'; jump.textContent = 'Sources';
        a.replaceWith(jump);
      } else {
        const before = a.previousSibling;
        if (before && before.nodeType === Node.TEXT_NODE) before.textContent = before.textContent.replace(/\s*[·|;,]\s*$/, '');
        a.remove();
      }
    });
  });
  if (!blocks.length && !summaryReferences.length) return;
  const details = document.createElement('details');
  details.className = 'article-sources';
  details.id = 'article-sources';
  const label = document.createElement('summary');
  label.textContent = 'Sources and verification';
  details.append(label);
  const body = document.createElement('div');
  body.className = 'article-sources-body';
  if (summaryReferences.length) {
    const p = document.createElement('p');
    p.append(document.createTextNode('Release references: '));
    summaryReferences.forEach((link, i) => { if (i) p.append(document.createTextNode(' · ')); p.append(link); });
    body.append(p);
  }
  blocks.forEach(node => body.append(node));
  // Preserve attribution text while linking a repeated source only once in this section.
  const seen = new Set();
  body.querySelectorAll('a[href]').forEach(a => {
    if (!isExternal(a)) return;
    const key = new URL(a.getAttribute('href'), location.href).href;
    if (seen.has(key)) a.replaceWith(document.createTextNode(a.textContent));
    else seen.add(key);
  });
  details.append(body);
  article.querySelectorAll('a[href="#article-sources"]').forEach(a => a.addEventListener('click', () => { details.open = true; }));
  const related = article.querySelector('.related-releases');
  if (related && related.parentElement === article) article.insertBefore(details, related);
  else article.append(details);
})();
