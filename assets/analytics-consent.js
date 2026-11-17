(() => {
  const measurementId = 'G-TRV5CF738D';
  const disableKey = 'ga-disable-' + measurementId;
  const preferenceKey = 'aninextup-analytics-consent';
  const panel = document.querySelector('[data-analytics-consent]');
  const settings = document.querySelector('[data-analytics-settings]');
  if (!panel || !settings) return;

  function storedPreference() {
    try { return localStorage.getItem(preferenceKey); }
    catch { return null; }
  }

  function applyPreference(preference) {
    const granted = preference === 'granted';
    const wasGranted = window[disableKey] === false;
    window[disableKey] = !granted;
    if (granted === wasGranted) return;

    window.gtag('consent', 'update', {analytics_storage: preference});
    if (granted && !document.getElementById('aninextup-ga4')) {
      window.gtag('js', new Date());
      window.gtag('config', measurementId, {
        allow_google_signals: false,
        allow_ad_personalization_signals: false,
      });
      const tag = document.createElement('script');
      tag.id = 'aninextup-ga4';
      tag.async = true;
      tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
      document.head.append(tag);
    }
    if (!granted) {
      for (const entry of document.cookie.split(';')) {
        const name = entry.split('=')[0].trim();
        if (name === '_ga' || name.startsWith('_ga_')) {
          document.cookie = name + '=; Max-Age=0; Path=/';
          document.cookie = name + '=; Max-Age=0; Path=/; Domain=aninextup.com';
        }
      }
    }
  }

  function closeSettings() {
    panel.hidden = true;
    settings.setAttribute('aria-expanded', 'false');
  }

  panel.addEventListener('click', event => {
    const button = event.target.closest('[data-analytics-choice]');
    if (!button) return;
    const preference = button.dataset.analyticsChoice;
    try { localStorage.setItem(preferenceKey, preference); } catch {}
    applyPreference(preference);
    const restoreFocus = panel.contains(document.activeElement);
    closeSettings();
    if (restoreFocus) settings.focus();
  });
  settings.addEventListener('click', () => {
    panel.hidden = !panel.hidden;
    settings.setAttribute('aria-expanded', String(!panel.hidden));
    if (!panel.hidden) panel.querySelector('button').focus();
  });
  window.addEventListener('storage', event => {
    if (event.key !== preferenceKey && event.key !== null) return;
    applyPreference(storedPreference() === 'granted' ? 'granted' : 'denied');
    closeSettings();
  });

  const preference = storedPreference();
  applyPreference(preference === 'granted' ? 'granted' : 'denied');
  if (!preference) {
    panel.hidden = false;
    settings.setAttribute('aria-expanded', 'true');
  }
})();
