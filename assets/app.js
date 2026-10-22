// Accessible mobile navigation: one toggle state, keyboard dismissal, and responsive reset.
document.querySelectorAll('.site-header').forEach(header=>{
  const button=header.querySelector('.menu');
  const nav=header.querySelector('nav');
  if(!button||!nav)return;
  // Keep a direct route back to the AniNextUp homepage on every page.
  if(!nav.querySelector('a[href="/"]')){
    const home=document.createElement('a');
    home.href='/';
    home.textContent='HOME';
    nav.insertBefore(home,nav.querySelector('a[href="today"],a[href="/today"]')||nav.firstChild);
  }
  const newsLink=nav.querySelector('a[href="news"],a[href="/news"]');
  if(newsLink&&!newsLink.parentElement.classList.contains('nav-news-item')){
    const item=document.createElement('div');item.className='nav-news-item';
    newsLink.parentNode.insertBefore(item,newsLink);item.append(newsLink);
    const submenu=document.createElement('div');submenu.className='nav-news-menu';
    submenu.setAttribute('role','group');submenu.setAttribute('aria-label','News subcategories');
    [['New Anime','new-anime'],['Returning Series','returning-series'],['Trailers & Cast','trailers-cast'],['Release News','release-news']].forEach(([label,category])=>{
      const link=document.createElement('a');link.href='/news?category='+category;link.textContent=label;submenu.append(link);
    });
    item.append(submenu);
  }
  const close=(restoreFocus=false)=>{
    nav.classList.remove('open');
    button.setAttribute('aria-expanded','false');
    button.setAttribute('aria-label','Open menu');
    if(restoreFocus)button.focus();
  };
  button.setAttribute('aria-controls',nav.id||(nav.id='site-primary-navigation'));
  button.addEventListener('click',()=>{
    const isOpen=nav.classList.toggle('open');
    button.setAttribute('aria-expanded',String(isOpen));
    button.setAttribute('aria-label',isOpen?'Close menu':'Open menu');
  });
  nav.addEventListener('click',event=>{
    if(event.target.closest('a'))close();
  });
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&nav.classList.contains('open'))close(true);
  });
  document.addEventListener('pointerdown',event=>{
    if(nav.classList.contains('open')&&!header.contains(event.target))close();
  });
  const desktop=window.matchMedia('(min-width: 781px)');
  const reset=()=>{if(desktop.matches)close()};
  if(desktop.addEventListener)desktop.addEventListener('change',reset);
  else if(desktop.addListener)desktop.addListener(reset);
});
const cardImageFallback='/assets/images/anime-image-fallback.svg';
const cardImageSelector='.visual-card > img, .news-featured > img, .news-side-card img, .week-release img, .calendar-day-items img, .related-releases img';
function useCardImageFallback(image){
  if(!(image instanceof HTMLImageElement))return;
  // Only stop when the current request already is the fallback.
  // A later external request must still be able to recover.
  if(image.src===new URL(cardImageFallback,location.origin).href)return;
  image.dataset.fallbackApplied='true';
  image.classList.add('image-fallback');
  image.src=image.src==="https://images.microcms-assets.io/assets/c44392189a8b469a9081892cfb643293/748b8a300806461a98622f11dad150f1/kv_photo.jpg"?"https://hirayasumi-anime.jp/img/top/kv_main.jpg":cardImageFallback;
}
// Keep cards composed when an external artwork host is unavailable.
document.addEventListener('error',event=>{
  if(event.target instanceof HTMLImageElement&&event.target.matches(cardImageSelector))useCardImageFallback(event.target);
},true);
document.querySelectorAll(cardImageSelector).forEach(image=>{
  if(image.complete&&!image.naturalWidth)useCardImageFallback(image);
});
const D=window.ANINEXTUP_DATA||{anime:[],guides:[]};
// Keep the pre-rendered lists when the central index fails to load.
const discoveryNodes=selector=>window.ANINEXTUP_DATA?document.querySelectorAll(selector):[];
const TZ=D.site?.timezone||'America/Santo_Domingo';
const releaseContext=window.ANINEXTUP_RELEASES?.context(new Date(),TZ);
const prettyDate=(s,label)=>{if(!s)return (label||'DATE TBA').toUpperCase();const d=new Date(s+'T12:00:00');return d.toLocaleDateString('en-US',{month:'short',day:'2-digit'}).toUpperCase()};
const releaseState=a=>a.status==='month-confirmed'?'MONTH CONFIRMED':a.status==='tba'?'DATE TBA':'CONFIRMED';
const animeCard=(a,showMore=false)=>'<a class="mini data-card visual-card" href="'+a.article+'">'+(a.image?'<img src="'+a.image+'" alt="'+a.title+'" loading="lazy">':'')+'<div class="visual-body"><b>'+prettyDate(a.date,a.dateLabel)+'</b>'+(showMore?'':'<small class="status">'+releaseState(a)+'</small>')+'<h3>'+a.title+'</h3><span>'+a.platform+'</span>'+(showMore?'<span class="more">VIEW RELEASE →</span>':'')+'</div></a>';
const fullCard=a=>'<a class="card story data-card visual-card" href="'+a.article+'">'+(a.image?'<img src="'+a.image+'" alt="'+a.title+'" loading="lazy">':'')+'<div class="visual-body"><span class="tag">'+a.platform.toUpperCase()+'</span><span class="status">'+releaseState(a)+'</span><div class="date">'+prettyDate(a.date,a.dateLabel)+'</div><h3>'+a.title+'</h3><p>'+a.category+' · '+a.platform+'</p><span class="more">READ GUIDE →</span></div></a>';
discoveryNodes('[data-anime-list]').forEach(el=>{let items=[...D.anime];const mode=el.dataset.animeList;if(mode==='today'){const day=el.dataset.date||(()=>{const parts=new Intl.DateTimeFormat('en-US',{timeZone:TZ,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());const value=t=>parts.find(p=>p.type===t)?.value;return value('year')+'-'+value('month')+'-'+value('day')})();items=items.filter(a=>a.date===day)}if(mode==='week'){const now=new Date(),day=new Date(now.toLocaleString('en-US',{timeZone:TZ})),dow=(day.getDay()+6)%7,start=new Date(day);start.setDate(day.getDate()-dow);const end=new Date(start);end.setDate(start.getDate()+6);const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');items=items.filter(a=>a.date&&a.date>=iso(start)&&a.date<=iso(end)).sort((a,b)=>a.date.localeCompare(b.date))}if(mode==='upcoming-week'){const now=new Date(),day=new Date(now.toLocaleString('en-US',{timeZone:TZ})),dow=(day.getDay()+6)%7,end=new Date(day);end.setDate(day.getDate()+(6-dow));const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'),today=iso(day);items=items.filter(a=>a.date&&a.date>today&&a.date<=iso(end)).sort((a,b)=>a.date.localeCompare(b.date))}if(mode==='calendar')items=items.filter(a=>a.date).sort((a,b)=>a.date.localeCompare(b.date));if(mode==='netflix')items=items.filter(a=>a.platform==='Netflix');if(mode==='crunchyroll')items=items.filter(a=>a.platform==='Crunchyroll');const emptyCopy=mode==='today'?'No new anime premieres today. Weekly episodes are listed above.':mode==='upcoming-week'?'No more first premieres this week. <a href="/calendar">Browse upcoming dates →</a>':'No first premieres confirmed for this date. Explore the upcoming releases below.';el.innerHTML=items.map(a=>el.hasAttribute('data-home-schedule')?animeCard(a,true):el.hasAttribute('data-compact-cards')?animeCard(a):mode==='today'?fullCard(a):animeCard(a)).join('')||'<p class="empty">'+emptyCopy+'</p>'});
discoveryNodes('[data-anime-month]').forEach(el=>{const month=el.dataset.animeMonth;const items=(D.anime||[]).filter(a=>a.date&&a.date.startsWith(month)).sort((a,b)=>a.date.localeCompare(b.date));el.innerHTML=items.map(animeCard).join('')||'<p class="empty">No confirmed releases yet.</p>'});
discoveryNodes('[data-month-count]').forEach(el=>{const month=el.dataset.monthCount;const n=(D.anime||[]).filter(a=>a.date&&a.date.startsWith(month)).length;el.textContent=n?'· '+n+' CONFIRMED':''});
const NEWS_CATEGORY_KEYS=new Set(['new-anime','returning-series','trailers-cast','release-news']);
const NEWS_ARTICLE_CATEGORY=Object.freeze(Object.fromEntries([...(D.anime||[]),...(D.guides||[])].filter(item=>item.article&&NEWS_CATEGORY_KEYS.has(item.newsCategory)).map(item=>[item.article,item.newsCategory])));
const NEWS_CATEGORY_COUNTS=Object.freeze({'new-anime':20,'returning-series':7,'trailers-cast':4,'release-news':6});
function setupNewsCategoryFilters(){
 const nav=document.querySelector('[data-news-category-filters]');if(!nav)return;
 const grid=document.querySelector('[data-guides]');if(!grid)return;
 const categoryCards=[];
 [...grid.querySelectorAll('a[href^="articles/"]')].forEach(card=>{
  const article=card.getAttribute('href').split('?')[0].replace(/\\.html$/,'');
  const category=NEWS_ARTICLE_CATEGORY[article];
  if(!category){card.hidden=true;return;}
  card.dataset.newsCategory=category;categoryCards.push(card);
 });
 if(!categoryCards.length)return;
 const status=document.querySelector('[data-news-filter-status]');
 const lead=document.querySelector('.news-lead');
 const intro=document.querySelector('.news-intro');
 const guideSection=grid.closest('section');
 const sections=[...document.querySelectorAll('.news-redesign > section')];
 const counts=categoryCards.reduce((all,card)=>(all[card.dataset.newsCategory]=(all[card.dataset.newsCategory]||0)+1,all),{});
 nav.querySelectorAll('[data-news-filter]').forEach(button=>{
  const key=button.dataset.newsFilter;
  const badge=button.querySelector('span');
  if(badge)badge.textContent=String(key==='all'?categoryCards.length:(counts[key]||0));
 });
 function applyNewsFilter(key){
  const active=key!=='all';
  let shown=0;
  categoryCards.forEach(card=>{const match=!active||card.dataset.newsCategory===key;card.hidden=!match;if(match)shown++;});
  nav.querySelectorAll('[data-news-filter]').forEach(button=>{
   const selected=button.dataset.newsFilter===key;
   button.classList.toggle('is-active',selected);button.setAttribute('aria-pressed',String(selected));
  });
  if(lead)lead.hidden=active;
  sections.forEach(section=>{if(section!==intro&&section!==guideSection)section.hidden=active;});
  if(status){status.hidden=!active;status.textContent=active?shown+' '+(shown===1?'article':'articles')+' shown':'';}
  try{const url=new URL(location.href);if(active)url.searchParams.set('category',key);else url.searchParams.delete('category');history.replaceState({},'',url);}catch(_){}
 }
 nav.addEventListener('click',event=>{const button=event.target.closest('[data-news-filter]');if(button)applyNewsFilter(button.dataset.newsFilter);});
 nav.hidden=false;
 const requested=new URLSearchParams(location.search).get('category');
 applyNewsFilter(NEWS_CATEGORY_KEYS.has(requested)?requested:'all');
}
discoveryNodes('[data-guides]').forEach(el=>{
 const seen=new Set();
 const stories=[...(D.anime||[]).filter(a=>a.article&&NEWS_ARTICLE_CATEGORY[a.article]),...(D.guides||[])].filter(g=>{
  if(!g.article||seen.has(g.article)||!NEWS_ARTICLE_CATEGORY[g.article])return false;
  seen.add(g.article);return true;
 });
 const ordered=window.ANINEXTUP_RELEASES?.sortNews(stories,window.ANINEXTUP_NEWS_DATES||{})||stories;
 el.innerHTML=ordered.map(g=>'<a class="card story visual-card" data-news-category="'+NEWS_ARTICLE_CATEGORY[g.article]+'" href="'+g.article+'">'+(g.image?'<img src="'+g.image+'" alt="'+g.title+'" loading="lazy">':'')+'<div class="visual-body"><span class="tag">'+(g.tag||'OFFICIAL NEWS')+'</span><h3>'+g.title+'</h3>'+(typeof g.description==='string'&&g.description.trim()?'<p>'+g.description+'</p>':'')+'<span class="more">READ MORE →</span></div></a>').join('');
});
setupNewsCategoryFilters();
// Search every indexed public page, including articles not featured on the homepage.
let siteSearchIndexPromise=null,siteSearchRequest=0;
const normalizeSiteSearch=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();
function prepareSiteSearchEntry(entry){
 if(!entry||typeof entry.title!=='string'||!entry.title.trim())return null;
 let url;try{url=new URL(entry.url||entry.article,location.origin)}catch{return null}
 if(url.origin!==location.origin||!url.pathname.startsWith('/articles/'))return null;
 const aliases=Array.isArray(entry.aliases)?entry.aliases.filter(a=>typeof a==='string'):[];
 const description=typeof entry.description==='string'?entry.description:'';
 return {title:entry.title,description,url:url.pathname,aliases,search:normalizeSiteSearch([entry.title,...aliases,description,entry.content,entry.tag,entry.platform].filter(x=>typeof x==='string').join(' '))};
}
function loadSiteSearchIndex(){
 if(siteSearchIndexPromise)return siteSearchIndexPromise;
 siteSearchIndexPromise=(async()=>{
  // One generated index replaces a separate network request for every article.
  try{
   const response=await fetch('/assets/search-index.json',{cache:'no-cache'});
   if(response.ok){
    const payload=await response.json();
    if(payload.version===1&&Array.isArray(payload.entries)){
     const entries=payload.entries.map(prepareSiteSearchEntry).filter(Boolean);
     if(entries.length)return entries;
    }
   }
  }catch(e){/* Older deployments can still use the public sitemap fallback. */}
  const response=await fetch('/sitemap.xml');
  if(!response.ok)throw new Error('Sitemap unavailable');
  const xml=new DOMParser().parseFromString(await response.text(),'application/xml');
  const urls=[...xml.getElementsByTagName('loc')].map(el=>el.textContent.trim()).filter(url=>{try{const parsed=new URL(url);return parsed.origin===location.origin&&parsed.pathname.startsWith('/articles/')&&parsed.pathname.length>'/articles/'.length}catch{return false}});
  const entries=[];let cursor=0;
  async function worker(){
   while(cursor<urls.length){
    const url=urls[cursor++];
    try{
     const res=await fetch(url);if(!res.ok)continue;
     const doc=new DOMParser().parseFromString(await res.text(),'text/html');
     doc.querySelectorAll('script,style,nav,footer,header.site-header').forEach(n=>n.remove());
     const title=doc.querySelector('h1')?.textContent?.trim()||doc.title.replace(/ — AniNextUp$/,'');
     const description=doc.querySelector('meta[name="description"]')?.content||'';
     const content=(doc.querySelector('article')||doc.querySelector('main')||doc.body)?.textContent||'';
     entries.push({title,description,url:new URL(url).pathname,search:normalizeSiteSearch(title+' '+description+' '+content)});
    }catch(e){/* Ignore an individual unavailable page. */}
   }
  }
  await Promise.all(Array.from({length:8},()=>worker()));
  return entries;
 })().catch(e=>{siteSearchIndexPromise=null;throw e});
 return siteSearchIndexPromise;
}
function rankSiteSearchEntries(entries,words){
 if(!words.length)return [];
 const phrase=words.join(' ');
 return entries.map(x=>{
  const title=normalizeSiteSearch(x.title),aliases=(x.aliases||[]).map(normalizeSiteSearch);
  const score=words.every(w=>x.search.includes(w))?words.reduce((n,w)=>n+(title.includes(w)?5:1),0):-1;
  return {...x,score:score<0?-1:score+(title===phrase?100:aliases.includes(phrase)?90:title.includes(phrase)?30:0)};
 }).filter(x=>x.score>=0).sort((a,b)=>b.score-a.score||a.title.localeCompare(b.title)).slice(0,40);
}
function renderSiteSearchResults(box,results){
 if(!box)return;
 box.innerHTML=results.length?results.map(x=>{
  const a=document.createElement('a');a.href=x.url;
  const strong=document.createElement('strong');strong.textContent=x.title;
  const span=document.createElement('span');span.textContent=x.description||'AniNextUp article';
  a.append(strong,span);return a.outerHTML
 }).join(''):'<div class="no-result">No matching articles found.</div>';
 box.hidden=false;
}
// Make the same article search available from every page, including articles.
document.querySelectorAll('.site-header').forEach((header,index)=>{
 const toggle=document.createElement('button');
 toggle.className='global-search-toggle';
 toggle.type='button';
 toggle.setAttribute('aria-label','Search AniNextUp');
 toggle.setAttribute('aria-expanded','false');
 toggle.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.8"></circle><path d="m16 16 5 5"></path></svg><span class="sr-only">Search</span>';
 const panel=document.createElement('div');
 panel.className='site-search-panel';
 panel.id='site-search-panel-'+index;
 panel.hidden=true;
 panel.innerHTML='<form class="site-search-form" role="search"><label class="sr-only" for="site-search-input-'+index+'">Search anime, platforms and guides</label><div class="search"><input id="site-search-input-'+index+'" class="site-search-input" type="search" placeholder="Search anime, platform or guide..."><button type="submit">SEARCH</button></div><div class="search-results site-search-results" aria-live="polite" hidden></div></form>';
 toggle.setAttribute('aria-controls',panel.id);
 const nav=header.querySelector('nav');
 if(nav)nav.after(toggle);else header.append(toggle);
 header.append(panel);
 const input=panel.querySelector('.site-search-input');
 const results=panel.querySelector('.site-search-results');
 toggle.addEventListener('click',()=>{
  const open=panel.hidden;
  panel.hidden=!open;
  toggle.setAttribute('aria-expanded',String(open));
  if(open)input.focus();
 });
 panel.querySelector('form').addEventListener('submit',event=>{
  event.preventDefault();
  searchSite(input,results);
 });
 input.addEventListener('input',()=>{
  if(input.value.trim())return;
  results.hidden=true;
  siteSearchRequest++;
 });
 document.addEventListener('keydown',event=>{
  if(event.key==='Escape'&&!panel.hidden){panel.hidden=true;toggle.setAttribute('aria-expanded','false');toggle.focus()}
 });
 document.addEventListener('pointerdown',event=>{
  if(!panel.hidden&&!header.contains(event.target)){panel.hidden=true;toggle.setAttribute('aria-expanded','false')}
 });
});
async function searchSite(input=document.getElementById('search'),box=document.getElementById('searchResults')){
 const raw=(input?.value||'').trim(),request=++siteSearchRequest;
 if(!raw){if(box)box.hidden=true;return}
 const words=normalizeSiteSearch(raw).split(/\s+/).filter(Boolean);
 if(!words.length){renderSiteSearchResults(box,[]);return;}
 // Show matches already present in the homepage data before loading the full sitemap index.
 const localEntries=[...(window.ANINEXTUP_DATA?.anime||[]),...(window.ANINEXTUP_DATA?.guides||[])].map(prepareSiteSearchEntry).filter(Boolean);
 const immediate=rankSiteSearchEntries(localEntries,words);
 if(immediate.length)renderSiteSearchResults(box,immediate);
 else if(box){box.innerHTML='<div class="no-result">Searching all articles…</div>';box.hidden=false}
 try{
  const entries=await loadSiteSearchIndex();
  if(request!==siteSearchRequest)return;
  const unique=new Map([...localEntries,...entries].map(x=>[x.url,x]));
  const results=rankSiteSearchEntries([...unique.values()],words);
  if(box)renderSiteSearchResults(box,results);
  else if(results[0])location.href=results[0].url;
 }catch(e){
  if(request===siteSearchRequest&&box&&!immediate.length){
   box.innerHTML='<div class="no-result">Search is temporarily unavailable. Please try again.</div>';
   box.hidden=false;
  }
 }
}
document.getElementById('search')?.addEventListener('keydown',e=>{if(e.key==='Enter')searchSite()});document.getElementById('search')?.addEventListener('input',e=>{if(!e.target.value.trim()){const b=document.getElementById('searchResults');if(b)b.hidden=true;siteSearchRequest++}});

const siteToday=new Date(new Date().toLocaleString('en-US',{timeZone:TZ}));discoveryNodes('[data-today-label]').forEach(el=>el.textContent='TODAY · '+siteToday.toLocaleDateString('en-US',{month:'long',day:'numeric'}).toUpperCase());

// Dynamic Today and This Week context
const isoLocal=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const localToday=new Date(new Date().toLocaleString('en-US',{timeZone:TZ}));
const localTodayIso=isoLocal(localToday);
const fmtLong=d=>d.toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'});
discoveryNodes('[data-today-heading]').forEach(el=>el.textContent='New Anime Premieres on '+fmtLong(localToday));
discoveryNodes('[data-today-description]').forEach(el=>el.textContent='See weekly anime episodes scheduled for '+fmtLong(localToday)+', with regional release times, streaming platforms and official series links. Confirmed first premieres are listed separately; timing and availability can vary by region.');
if(document.querySelector('[data-today-heading]')){document.title='Anime Releasing Today ('+fmtLong(localToday)+') | AniNextUp';const m=document.querySelector('meta[name="description"]');if(m)m.content='See weekly anime episodes scheduled for '+fmtLong(localToday)+', with regional release times, platforms and official links. Browse confirmed first premieres and upcoming releases too; timing and availability can vary by region.';}
discoveryNodes('[data-today-next]').forEach(el=>{const items=[...(D.anime||[])].filter(a=>a.date&&a.date>localTodayIso).sort((a,b)=>a.date.localeCompare(b.date)).slice(0,6);el.innerHTML=items.map(animeCard).join('')||'<p class="empty">No upcoming confirmed releases listed yet.</p>'});
const weekDow=(localToday.getDay()+6)%7,weekStart=new Date(localToday),weekEnd=new Date(localToday);weekStart.setDate(localToday.getDate()-weekDow);weekEnd.setDate(weekStart.getDate()+6);
const weekRange=weekStart.getMonth()===weekEnd.getMonth()?weekStart.toLocaleDateString('en-US',{month:'long'})+' '+weekStart.getDate()+'–'+weekEnd.getDate()+', '+weekEnd.getFullYear():weekStart.toLocaleDateString('en-US',{month:'short',day:'numeric'})+'–'+weekEnd.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
discoveryNodes('[data-week-range]').forEach(el=>el.textContent=weekRange.toUpperCase());
discoveryNodes('[data-week-title]').forEach(el=>el.textContent='Anime Episodes & First Premieres This Week — '+weekRange);
discoveryNodes('[data-week-heading]').forEach(el=>el.textContent=weekRange+' First Premieres');
discoveryNodes('[data-week-description]').forEach(el=>el.textContent='Browse weekly episodes above, then see confirmed first premieres and season openings scheduled for '+weekRange+'.');
if(document.querySelector('[data-week-heading]')){document.title='Anime Episodes & Premieres This Week: '+weekRange+' — AniNextUp';const m=document.querySelector('meta[name="description"]');if(m)m.content='Find weekly anime episodes and confirmed first premieres this week, '+weekRange+', with regional times and viewing guides.';}
discoveryNodes('[data-after-week]').forEach(el=>{const endIso=isoLocal(weekEnd);const items=[...(D.anime||[])].filter(a=>a.date&&a.date>endIso).sort((a,b)=>a.date.localeCompare(b.date)).slice(0,6);el.innerHTML=items.map(animeCard).join('')||'<p class="empty">No later confirmed releases listed yet.</p>'});

// Homepage discovery sections
const homeIso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const homeToday=homeIso(new Date(new Date().toLocaleString('en-US',{timeZone:TZ})));
// Latest news is generated from articles/*.html on each article publication.
// The static HTML cards remain a no-JavaScript / network-error fallback.
const latestNewsNodes=discoveryNodes('[data-home-latest]');
if(latestNewsNodes.length){
  fetch('/assets/latest-news.json?v='+Date.now(),{cache:'no-store'})
    .then(response=>{if(!response.ok)throw new Error('Latest news feed unavailable');return response.json()})
    .then(feed=>{
      const seen=new Set();
      const items=(Array.isArray(feed.items)?feed.items:[]).filter(g=>{
        if(!g.article||!g.title||seen.has(g.article))return false;
        seen.add(g.article);return true;
      }).slice(0,7);
      if(!items.length)return;
      const escapeHTML=s=>String(s||'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
      const validImage=s=>{const url=/^(https?:\/\/|\/)/.test(s||'')?s:'/assets/images/anime-image-fallback.svg';return url;};
      const markup=items.map((g,i)=>'<a class="card story visual-card" href="/'+escapeHTML(g.article)+'"><img src="'+escapeHTML(validImage(g.image))+'" alt="'+escapeHTML(g.title)+'" loading="'+(i===0?'eager':'lazy')+'" decoding="async"'+(i===0?' fetchpriority="high"':' fetchpriority="low"')+'><div class="visual-body"><span class="tag">'+escapeHTML(g.tag||'ANIME NEWS')+'</span><h3>'+escapeHTML(g.title)+'</h3><p>'+escapeHTML(g.description)+'</p><span class="more">READ UPDATE →</span></div></a>').join('');
      // Defer off-screen image downloads, but preserve ordinary links and native lazy-loading.
      latestNewsNodes.forEach(el=>{el.innerHTML=markup});
    }).catch(()=>{/* Keep pre-rendered news cards intact. */});
}

discoveryNodes('[data-home-next]').forEach(el=>{const items=window.ANINEXTUP_RELEASES.select(D.anime||[],'after-week',releaseContext).slice(0,6);el.innerHTML=items.map(animeCard).join('')||'<p class="empty">No upcoming releases listed yet.</p>'});

// Platform-specific release hubs
for(const el of discoveryNodes('[data-anime-platform]')){
 const p=el.dataset.animePlatform;
 const match=x=>window.ANINEXTUP_RELEASES.matchesPlatform(x,p);
 const list=(D.anime||[]).filter(match).sort((x,y)=>(x.date||'9999').localeCompare(y.date||'9999'));
 el.innerHTML=list.map(animeCard).join('')||'<p class="empty">No confirmed releases yet.</p>';
}

discoveryNodes('[data-platform-count]').forEach(el=>{const p=el.dataset.platformCount;const n=(D.anime||[]).filter(x=>window.ANINEXTUP_RELEASES.matchesPlatform(x,p)).length;el.textContent=n?'· '+n+' TRACKED':''});

// Keep exactly three related anime releases on every article, including legacy and future pages.
const renderRelatedReleases=data=>{
  const article=document.querySelector('article.article');
  if(!article)return;
  const slug=location.pathname.split('/').pop().replace(/\.html$/,'');
  const items=(data?.anime||[]).filter(a=>a.article&&a.title&&a.image);
  const current=items.find(a=>a.article.split('/').pop().replace(/\.html$/,'')===slug);
  let section=article.querySelector('.related-releases');
  if(!section){
    section=document.createElement('section');
    section.className='related-releases';
    section.setAttribute('aria-labelledby','related-releases-heading');
    const head=document.createElement('div');head.className='section-head';
    const title=document.createElement('div');
    const kicker=document.createElement('span');kicker.className='kicker';kicker.textContent='KEEP WATCHING';
    const heading=document.createElement('h2');heading.id='related-releases-heading';heading.textContent='Related releases';
    title.append(kicker,heading);
    const calendar=document.createElement('a');calendar.href='../calendar';calendar.textContent='FULL CALENDAR →';
    head.append(title,calendar);section.append(head);article.append(section);
  }
  let grid=section.querySelector('.grid');
  if(!grid){grid=document.createElement('div');grid.className='grid three';section.append(grid);}
  const existing=Array.from(section.querySelectorAll('.grid > a.mini'));
  const slugOf=value=>{try{return new URL(value,location.href).pathname.split('/').pop().replace(/\.html$/,'')}catch{return String(value||'').split('/').pop().replace(/\.html$/,'')}};
  const used=new Set(existing.map(card=>slugOf(card.href)));
  used.add(slug);
  const refDate=current?.date||(new Date()).toISOString().slice(0,10);
  const distance=value=>{
    const target=Date.parse((value||'')+'T00:00:00Z'),reference=Date.parse(refDate+'T00:00:00Z');
    return Number.isFinite(target)&&Number.isFinite(reference)?Math.abs(target-reference):999999999;
  };
  const score=x=>(current&&x.category===current.category?4:0)+(current&&x.platform===current.platform?2:0)+(current&&x.date&&x.date===current.date?1:0);
  const ranked=items.filter(x=>!used.has(slugOf(x.article))).sort((a,b)=>{
    const relevance=score(b)-score(a);
    return relevance||distance(a.date)-distance(b.date);
  }).slice(0,Math.max(0,3-existing.length));
  ranked.forEach(a=>{
    const link=document.createElement('a');link.className='mini data-card related-card';link.href='../'+a.article.replace(/^\//,'');
    const source=new URL(a.image,location.origin+'/');
    if((source.protocol==='https:'||source.origin===location.origin)&&source.pathname!=='/assets/images/covers/aoashi-season-2.jpg'&&!/(?:favicon|\.svg(?:$|\?))/i.test(source.href)){
      const media=document.createElement('span');media.className='related-card-media';
      const image=document.createElement('img');image.className='related-card-image';image.alt=a.title;image.width=160;image.height=90;image.loading='lazy';image.decoding='async';image.src=source.href;media.append(image);link.append(media);
    }
    const copy=document.createElement('div');copy.className='related-card-copy';
    const label=document.createElement('b');label.textContent=a.dateLabel||a.date||'ANIME RELEASE';
    const heading=document.createElement('h3');heading.textContent=a.title;
    const detail=document.createElement('span');detail.textContent=(a.platform||'Release updates')+' · Read the release guide →';
    copy.append(label,heading,detail);link.append(copy);grid.append(link);
  });
  normalizeRelatedReleaseGrid(section);
};
if(document.querySelector('article.article')){
  if(D.anime?.length)renderRelatedReleases(D);
  else{const script=document.createElement('script');script.src='../assets/data.js';script.onload=()=>renderRelatedReleases(window.ANINEXTUP_DATA);document.head.appendChild(script);}
}

function updateCuratedRelatedHeadings(){
  const curatedSlugs=['one-piece-elbaph-arc-english-dub-october-2026','reincarnated-as-a-sword-season-2-english-dub-release-date'];
  const slug=location.pathname.split('/').pop().replace(/\\.html$/,'');
  if(!curatedSlugs.includes(slug))return;
  const section=document.querySelector('article.article .related-releases');
  if(!section)return;
  const kicker=section.querySelector('.kicker');
  if(kicker)kicker.textContent='MORE ANIME NEWS';
  const heading=section.querySelector('h2');
  if(heading){heading.textContent='Related stories';heading.id='related-releases-heading';section.setAttribute('aria-labelledby','related-releases-heading');}
}
updateCuratedRelatedHeadings();
document.addEventListener('DOMContentLoaded',updateCuratedRelatedHeadings,{once:true});


// Enforce the three-column layout even when a page retains cached legacy CSS.
// Run immediately, independently of image fetching or editorial data loading.
function normalizeRelatedReleaseGrid(section){
  const grids=Array.from(section.querySelectorAll('.grid'));
  if(!grids.length)return null;

  // Older editorial markup sometimes split one related list across several grids.
  // Move the first three cards, in document order, into one shared grid.
  const cards=grids.flatMap(grid=>Array.from(grid.querySelectorAll(':scope > a.mini')));
  cards.slice(3).forEach(card=>card.remove());
  const visibleCards=cards.slice(0,3);
  const grid=grids[0];
  visibleCards.forEach(card=>grid.append(card));
  grids.slice(1).forEach(extra=>extra.remove());

  grid.classList.toggle('three',visibleCards.length===3);
  grid.style.setProperty('display','grid','important');
  grid.style.setProperty('gap','12px','important');
  grid.style.setProperty('align-items','stretch','important');
  visibleCards.forEach(card=>{
    card.style.setProperty('min-width','0');
    card.style.setProperty('width','100%');
  });
  return grid;
}
function enforceRelatedReleaseRow(){
  document.querySelectorAll('article.article .related-releases').forEach(section=>{
    normalizeRelatedReleaseGrid(section);
  });
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',enforceRelatedReleaseRow,{once:true});
else enforceRelatedReleaseRow();

// Every KEEP WATCHING card gets artwork, including legacy hand-authored sections.
// Prefer the destination article's cover, never reuse the current article's image.
async function ensureRelatedReleaseCovers(){
  const sections=document.querySelectorAll('article.article .related-releases');
  if(!sections.length)return;
  // Show at most three related articles on every article page, including legacy sections.
  for(const section of sections){
    normalizeRelatedReleaseGrid(section);
  }
  const entries=(window.ANINEXTUP_DATA?.anime||[]).concat(window.ANINEXTUP_DATA?.guides||[]);
  const coverBySlug=new Map(entries.filter(x=>x.article&&x.image).map(x=>[x.article.split('/').pop().replace(/\.html$/,''),x.image]));
  for(const section of sections){
    for(const link of section.querySelectorAll('a.mini')){
      // Normalize legacy editorial cards to the shared full-width cover layout.
      // Keep their original links, labels and descriptions intact.
      if(!link.classList.contains('related-card')){
        const media=document.createElement('span');
        media.className='related-card-media';
        const copy=document.createElement('span');
        copy.className='related-card-copy';
        for(const child of Array.from(link.childNodes)){
          if(child.nodeType===1&&child.matches('img,.related-card-media'))media.append(child);
          else copy.append(child);
        }
        link.append(media,copy);
        link.classList.add('related-card');
      }
      const destination=new URL(link.getAttribute('href'),location.href);
      const slug=destination.pathname.split('/').pop().replace(/\.html$/,'');
      let img=link.querySelector('img');
      if(img?.dataset.verifiedArtwork==='true'&&img.getAttribute('src'))continue;
      if(!img){
        img=document.createElement('img');
        img.className='related-card-image';
        img.alt='';
        img.width=160;img.height=90;
        img.loading='lazy';img.decoding='async';
        const media=link.querySelector('.related-card-media');
        if(media)media.append(img);else link.prepend(img);
        img.src=cardImageFallback;
      }
      img.removeAttribute('onerror');
      if(img.complete&&!img.naturalWidth)useCardImageFallback(img);
      const known=coverBySlug.get(slug);
      if(known){
        try{const expected=new URL(known,location.origin+'/').href;if(img.src!==expected)img.src=expected;}catch{useCardImageFallback(img);}
      }
      if(!known&&destination.origin===location.origin&&destination.pathname.startsWith('/articles/')){
        try{
          const response=await fetch(destination.href,{credentials:'omit'});
          if(!response.ok)continue;
          const html=await response.text();
          const parsed=new DOMParser().parseFromString(html,'text/html');
          const cover=parsed.querySelector('meta[property="og:image"]')?.content;
          if(cover&&/^https?:\/\//.test(cover)&&img.src!==cover)img.src=cover;
        }catch{/* Keep the branded fallback when destination metadata is unavailable. */}
      }
    }
  }
}
if(document.querySelector('article.article')){
  const startRelatedCovers=()=>ensureRelatedReleaseCovers().catch(()=>{});
  if(window.ANINEXTUP_DATA)startRelatedCovers();
  else window.addEventListener('load',startRelatedCovers,{once:true});
}

// News hub: upcoming confirmed releases
discoveryNodes('[data-news-upcoming]').forEach(el=>{const items=[...(D.anime||[])].filter(a=>a.date&&a.date>=homeToday).sort((a,b)=>a.date.localeCompare(b.date)).slice(0,9);el.innerHTML=items.map(fullCard).join('')||'<p class="empty">No upcoming confirmed releases listed yet.</p>'});

// Lightweight official trailers: YouTube loads only after a visitor clicks play.
document.querySelectorAll('.lite-trailer[data-youtube]').forEach(box=>{const btn=box.querySelector('.trailer-play');if(!btn)return;btn.addEventListener('click',()=>{const id=box.dataset.youtube,title=box.dataset.title||'Official trailer';const iframe=document.createElement('iframe');iframe.src='https://www.youtube-nocookie.com/embed/'+encodeURIComponent(id)+'?autoplay=1';iframe.title=title;iframe.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';iframe.referrerPolicy='strict-origin-when-cross-origin';iframe.allowFullscreen=true;box.replaceChildren(iframe)},{once:true})});


// Lead cover artwork is illustrative, not a navigation link.
// Keep caption/source links, related article cards and trailer play controls working.
if(document.querySelector('article.article')){
 const article=document.querySelector('article.article');
 const head=article.querySelector(':scope > .article-head');
 const cover=head?.nextElementSibling;
 if(cover&&(cover.matches('figure,.article-hero,.official-hero,img'))){
  const image=cover.matches('img')?cover:cover.querySelector('img');
  const anchor=image?.closest('a');
  if(anchor&&cover.contains(anchor)&&anchor.querySelector('img')===image){
   anchor.replaceWith(...anchor.childNodes);
  }
 }
}


// Keep article recommendations last, with one complete footer after them.
function normalizeArticleFooter(){
  const article=document.querySelector('article.article');
  if(!article)return;
  const footers=[...document.querySelectorAll('footer')];
  const footer=footers.shift()||document.createElement('footer');
  footer.innerHTML='<b>ANINEXTUP</b><p>Anime releases, streaming guides, calendars and news.</p><small>Release dates and availability can vary by region.</small><p><a href="/about">About</a> · <a href="/contact">Contact</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a></p>';
  footers.forEach(extra=>extra.remove());
  if(!footer.isConnected)document.body.append(footer);
  const related=article.querySelector('.related-releases');
  if(related)article.append(related);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',normalizeArticleFooter,{once:true});
else normalizeArticleFooter();


// Classify platform destinations before counting outbound clicks in GA4.
function classifyPlatformLink(destination){
  if(!['https:','http:'].includes(destination.protocol))return null;
  const platforms=[
    {host:"crunchyroll.com",name:"Crunchyroll"},{host:"netflix.com",name:"Netflix"},
    {host:"hidive.com",name:"HIDIVE"},{host:"disneyplus.com",name:"Disney+"},
    {host:"primevideo.com",name:"Prime Video"},{host:"hulu.com",name:"Hulu"},
    {host:"tv.apple.com",name:"Apple TV"},{host:"max.com",name:"Max"},
    {host:"peacocktv.com",name:"Peacock"},{host:"tubitv.com",name:"Tubi"}
  ];
  const hostname=destination.hostname.toLowerCase();
  const platform=platforms.find(p=>hostname===p.host||hostname.endsWith('.'+p.host));
  if(!platform)return null;
  // Match editorial sections across localized routes, e.g. /es/news/ and /en-US/news/.
  const editorialPath=/(?:^|\/)(?:news|tudum|media|newsroom|press|press-releases|blog|only-on-netflix)(?:\/|$)/i.test(destination.pathname);
  const editorialHost=/^(?:about|media|news|press)\./i.test(hostname);
  const kind=editorialPath||editorialHost?'source':'streaming';
  const slug=platform.name.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'');
  return {platform:platform.name,kind,event:kind+'_click_'+slug};
}
(function setupStreamingLinkAnalytics(){
  document.addEventListener('click',event=>{
    if(event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
    const link=event.target instanceof Element?event.target.closest('a[href]'):null;
    if(!link)return;
    let destination;
    try{destination=new URL(link.href,location.href)}catch{return}
    if(destination.origin===location.origin)return;
    const metric=classifyPlatformLink(destination);
    if(!metric||typeof window.gtag!=='function')return;
    window.gtag('event',metric.event,{
      platform_name:metric.platform,
      destination_type:metric.kind,
      link_url:destination.href,
      link_domain:destination.hostname,
      link_text:(link.innerText||link.getAttribute('aria-label')||'').trim().slice(0,120),
      page_path:location.pathname,
      transport_type:'beacon'
    });
  },true);
})();
