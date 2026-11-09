(() => {
  for (const label of document.querySelectorAll('[data-broadcast-at]')) {
    const value = label.dataset.broadcastAt;
    if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$/.test(value)) continue;
    const broadcastAt = Date.parse(value);
    if (!Number.isFinite(broadcastAt)) continue;

    function refresh() {
      const remaining = broadcastAt - Date.now();
      label.textContent = remaining > 0 ? 'Next listed Japanese broadcast' : 'Last listed Japanese broadcast';
      if (remaining > 0) setTimeout(refresh, Math.min(remaining, 2147483647));
    }

    refresh();
  }
})();
