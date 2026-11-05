// Apply the same policy to links inserted after the HTML is served.
(() => {
  const internalHosts = new Set(['aninextup.com', 'www.aninextup.com', location.hostname]);
  const selector = 'a[href]:not([download])';

  function openExternally(link) {
    if (!link.matches(selector)) return;
    let url;
    try {
      url = new URL(link.getAttribute('href'), document.baseURI);
    } catch {
      return;
    }
    if (!['http:', 'https:'].includes(url.protocol) ||
        internalHosts.has(url.hostname.replace(/\.$/, ''))) return;
    link.target = '_blank';
    link.relList.remove('opener');
    link.relList.add('noopener');
  }

  function visit(root) {
    if (root instanceof Element) openExternally(root);
    root.querySelectorAll?.(selector).forEach(openExternally);
  }

  visit(document);
  new MutationObserver(records => {
    for (const record of records) {
      if (record.type === 'attributes') openExternally(record.target);
      else record.addedNodes.forEach(visit);
    }
  }).observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['href']
  });
})();
