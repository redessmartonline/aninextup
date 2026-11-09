(() => {
  if (document.getElementById('aninextup-google-ads')) return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }

  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
  });
  gtag('consent', 'update', {
    ad_storage: 'granted',
    ad_user_data: 'granted',
    ad_personalization: 'granted',
  });
  window.dataLayer.push({'gtm.start': Date.now(), event: 'gtm.js'});

  const tag = document.createElement('script');
  tag.id = 'aninextup-google-ads';
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-NL276DVG';
  document.head.appendChild(tag);
})();
