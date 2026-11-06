(() => {
  const popup = document.getElementById('newsletter-popup');
  const sessionKey = 'aninextup-newsletter-shown';
  let showPopup = Boolean(popup?.showModal);
  if (showPopup) {
    try {
      showPopup = !sessionStorage.getItem(sessionKey);
    } catch {
      // The signup still works when the browser blocks storage.
    }
  }

  const forms = [
    document.getElementById('newsletter-signup'),
    showPopup ? document.getElementById('newsletter-popup-signup') : null,
  ].filter(Boolean);
  if (!forms.length) return;

  if (showPopup) {
    popup.querySelector('[data-newsletter-dismiss]').addEventListener('click', () => popup.close());
    popup.showModal();
    try {
      sessionStorage.setItem(sessionKey, '1');
    } catch {
      // A blocked storage write does not interrupt signup.
    }
  }

  const availability = fetch('/api/newsletter/status', {cache: 'no-store'}).then(response => {
    if (!response.ok) throw new Error('Newsletter status unavailable');
    return response.json();
  });

  for (const form of forms) {
    const status = document.getElementById(form.getAttribute('aria-describedby'));
    const email = form.querySelector('input[type="email"]');
    const button = form.querySelector('button[type="submit"]');

    availability.then(data => {
      if (data.available) {
        email.disabled = false;
        button.disabled = false;
        status.textContent = 'Subscribe for free. No email confirmation required.';
      } else {
        status.textContent = 'Coming soon — email subscriptions are not open yet.';
      }
    }).catch(() => {
      status.textContent = 'Subscriptions are temporarily unavailable. Please try again later.';
    });

    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (button.disabled || !form.reportValidity()) return;
      button.disabled = true;
      status.textContent = 'Subscribing…';
      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: new URLSearchParams(new FormData(form)),
          headers: {'Content-Type': 'application/x-www-form-urlencoded'},
          credentials: 'same-origin',
        });
        const data = await response.json();
        if (!response.ok || !data.ok) throw new Error(data.error || 'Please try again later.');
        status.textContent = data.message;
        form.reset();
      } catch (error) {
        status.textContent = error.message || 'Unable to subscribe. Please try again later.';
      } finally {
        button.disabled = false;
      }
    });
  }
})();
