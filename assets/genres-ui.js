/* Native anchor links and static guide content remain usable without JavaScript. */
(()=>{
  const page=document.querySelector('.genres-page');
  if(!page)return;
  const sections=[...page.querySelectorAll('.genre-section[id]')];
  const links=[...page.querySelectorAll('.genre-index a,.genre-starter-link a')];
  const pageSize = 9;
  for (const section of sections) {
    const button = section.querySelector('.genre-load-more');
    if (!button) continue;
    const cards = [...section.querySelectorAll('.genre-visual-card')];
    let visible = pageSize;
    cards.slice(visible).forEach(card => { card.hidden = true; });
    button.hidden = false;
    button.addEventListener('click', () => {
      const next = cards.slice(visible, visible + pageSize);
      next.forEach(card => { card.hidden = false; });
      visible += next.length;
      next[0]?.focus();
      button.hidden = visible >= cards.length;
    });
  }
  function select(){
    const key=location.hash.slice(1);
    const selected=sections.find(section=>section.id===key)||sections[0];
    sections.forEach(section=>{section.hidden=section!==selected});
    links.forEach(link=>{
      if(link.hash==='#'+selected.id)link.setAttribute('aria-current','true');
      else link.removeAttribute('aria-current');
    });
  }
  links.forEach(link=>link.addEventListener('click',event=>{
    if(event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
    event.preventDefault();
    history.pushState(null,'',link.hash);
    select();
  }));
  window.addEventListener('hashchange',select);
  window.addEventListener('popstate',select);
  select();
})();
