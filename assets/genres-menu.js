for (const item of document.querySelectorAll('[data-category-menu]')) {
  const menu = item.querySelector('details');
  const toggle = menu.querySelector('summary');
  const desktop = window.matchMedia('(min-width: 781px) and (hover: hover)');
  item.addEventListener('pointerenter', event => {
    if (desktop.matches && event.pointerType === 'mouse') menu.open = true;
  });
  item.addEventListener('pointerleave', event => {
    if (desktop.matches && event.pointerType === 'mouse' &&
        !menu.contains(document.activeElement)) menu.open = false;
  });
  item.addEventListener('focusout', event => {
    if (desktop.matches && !item.contains(event.relatedTarget)) menu.open = false;
  });
  item.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !menu.open) return;
    event.stopPropagation();
    menu.open = false;
    toggle.focus();
  });
  document.addEventListener('pointerdown', event => {
    if (!item.contains(event.target)) menu.open = false;
  });
  menu.addEventListener('click', event => {
    if (event.target.closest('a')) menu.open = false;
  });
}
