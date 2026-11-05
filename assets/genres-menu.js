for (const item of document.querySelectorAll('[data-category-menu]')) {
  const menu = item.querySelector('details');
  const toggle = menu.querySelector('summary');
  const desktop = window.matchMedia('(min-width: 781px) and (hover: hover)');
  let openedByHover = false;

  function close() {
    openedByHover = false;
    menu.open = false;
  }

  toggle.addEventListener('click', event => {
    if (!openedByHover) return;
    // The pointer may have already opened the menu on its way to the arrow.
    event.preventDefault();
    openedByHover = false;
  });

  item.addEventListener('pointerenter', event => {
    if (desktop.matches && event.pointerType === 'mouse' && !menu.open) {
      openedByHover = true;
      menu.open = true;
    }
  });
  item.addEventListener('pointerleave', event => {
    if (desktop.matches && event.pointerType === 'mouse' &&
        !menu.contains(document.activeElement)) close();
  });
  item.addEventListener('focusout', event => {
    if (desktop.matches && !item.contains(event.relatedTarget)) close();
  });
  item.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !menu.open) return;
    event.stopPropagation();
    close();
    toggle.focus();
  });
  document.addEventListener('pointerdown', event => {
    if (!item.contains(event.target)) close();
  });
  menu.addEventListener('click', event => {
    if (event.target.closest('a')) close();
  });
}
