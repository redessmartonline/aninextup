const genreMenuItem = document.querySelector('.nav-genres-item');
const genreMenu = genreMenuItem?.querySelector('.nav-genres-disclosure');

if (genreMenu) {
  const toggle = genreMenu.querySelector('summary');
  const desktop = window.matchMedia('(min-width: 781px) and (hover: hover)');
  genreMenuItem.addEventListener('pointerenter', event => {
    if (desktop.matches && event.pointerType === 'mouse') genreMenu.open = true;
  });
  genreMenuItem.addEventListener('pointerleave', event => {
    if (desktop.matches && event.pointerType === 'mouse' &&
        !genreMenu.contains(document.activeElement)) genreMenu.open = false;
  });
  genreMenuItem.addEventListener('focusout', event => {
    if (desktop.matches && !genreMenuItem.contains(event.relatedTarget)) genreMenu.open = false;
  });
  genreMenuItem.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !genreMenu.open) return;
    event.stopPropagation();
    genreMenu.open = false;
    toggle.focus();
  });
  document.addEventListener('pointerdown', event => {
    if (!genreMenuItem.contains(event.target)) genreMenu.open = false;
  });
  genreMenu.addEventListener('click', event => {
    if (event.target.closest('a')) genreMenu.open = false;
  });
}
