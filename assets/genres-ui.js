/* Native anchor links and static guide content remain usable without JavaScript. */
(()=>{
  const page=document.querySelector('.genres-page');
  if(!page)return;
  const sections=[...page.querySelectorAll('.genre-section[id]')];
  const links=[...page.querySelectorAll('.genre-index a,.genre-starter-link a')];
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
