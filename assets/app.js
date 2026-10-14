document.querySelectorAll('.menu').forEach(b=>b.addEventListener('click',()=>{const n=b.closest('.site-header')?.querySelector('nav');if(!n)return;n.classList.toggle('open');b.setAttribute('aria-expanded',n.classList.contains('open')?'true':'false')}));
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
const animeCard=a=>'<a class="mini data-card visual-card" href="'+a.article+'">'+(a.image?'<img src="'+a.image+'" alt="'+a.title+'" loading="lazy">':'')+'<div class="visual-body"><b>'+prettyDate(a.date,a.dateLabel)+'</b><small class="status">'+releaseState(a)+'</small><h3>'+a.title+'</h3><span>'+a.platform+'</span></div></a>';
const fullCard=a=>'<a class="card story data-card visual-card" href="'+a.article+'">'+(a.image?'<img src="'+a.image+'" alt="'+a.title+'" loading="lazy">':'')+'<div class="visual-body"><span class="tag">'+a.platform.toUpperCase()+'</span><span class="status">'+releaseState(a)+'</span><div class="date">'+prettyDate(a.date,a.dateLabel)+'</div><h3>'+a.title+'</h3><p>'+a.category+' · '+a.platform+'</p><span class="more">READ GUIDE →</span></div></a>';
discoveryNodes('[data-anime-list]').forEach(el=>{let items=[...D.anime];const mode=el.dataset.animeList;if(mode==='today'){const day=el.dataset.date||(()=>{const parts=new Intl.DateTimeFormat('en-US',{timeZone:TZ,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());const value=t=>parts.find(p=>p.type===t)?.value;return value('year')+'-'+value('month')+'-'+value('day')})();items=items.filter(a=>a.date===day)}if(mode==='week'){const now=new Date(),day=new Date(now.toLocaleString('en-US',{timeZone:TZ})),dow=(day.getDay()+6)%7,start=new Date(day);start.setDate(day.getDate()-dow);const end=new Date(start);end.setDate(start.getDate()+6);const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');items=items.filter(a=>a.date&&a.date>=iso(start)&&a.date<=iso(end)).sort((a,b)=>a.date.localeCompare(b.date))}if(mode==='upcoming-week'){const now=new Date(),day=new Date(now.toLocaleString('en-US',{timeZone:TZ})),dow=(day.getDay()+6)%7,end=new Date(day);end.setDate(day.getDate()+(6-dow));const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'),today=iso(day);items=items.filter(a=>a.date&&a.date>=today&&a.date<=iso(end)).sort((a,b)=>a.date.localeCompare(b.date))}if(mode==='calendar')items=items.filter(a=>a.date).sort((a,b)=>a.date.localeCompare(b.date));if(mode==='netflix')items=items.filter(a=>a.platform==='Netflix');if(mode==='crunchyroll')items=items.filter(a=>a.platform==='Crunchyroll');el.innerHTML=items.map(mode==='today'?fullCard:animeCard).join('')||'<p class="empty">No premieres confirmed for this date. Explore the upcoming releases below.</p>'});
discoveryNodes('[data-anime-month]').forEach(el=>{const month=el.dataset.animeMonth;const items=(D.anime||[]).filter(a=>a.date&&a.date.startsWith(month)).sort((a,b)=>a.date.localeCompare(b.date));el.innerHTML=items.map(animeCard).join('')||'<p class="empty">No confirmed releases yet.</p>'});
discoveryNodes('[data-month-count]').forEach(el=>{const month=el.dataset.monthCount;const n=(D.anime||[]).filter(a=>a.date&&a.date.startsWith(month)).length;el.textContent=n?'· '+n+' CONFIRMED':''});
discoveryNodes('[data-guides]').forEach(el=>{const seen=new Set();const stories=[...(D.anime||[]).filter(a=>a.tag&&a.article),...(D.guides||[])].filter(g=>{if(!g.article||seen.has(g.article))return false;seen.add(g.article);return true});el.innerHTML=stories.map(g=>'<a class="card story visual-card" href="'+g.article+'">'+(g.image?'<img src="'+g.image+'" alt="'+g.title+'" loading="lazy">':'')+'<div class="visual-body"><span class="tag">'+g.tag+'</span><h3>'+g.title+'</h3><p>'+g.description+'</p><span class="more">READ MORE →</span></div></a>').join('');});
function searchSite(){const input=document.getElementById('search'),q=(input?.value||'').trim().toLowerCase();if(!q)return;const results=[...D.anime.map(a=>({title:a.title,meta:a.platform,url:a.article})),...D.guides.map(g=>({title:g.title,meta:g.tag,url:g.article}))].filter(x=>(x.title+' '+x.meta).toLowerCase().includes(q));const box=document.getElementById('searchResults');if(box){box.innerHTML=results.length?results.map(x=>'<a href="'+x.url+'"><strong>'+x.title+'</strong><span>'+x.meta+'</span></a>').join(''):'<div class="no-result">No matching anime or guide found.</div>';box.hidden=false}else if(results[0])location.href=results[0].url}
document.getElementById('search')?.addEventListener('keydown',e=>{if(e.key==='Enter')searchSite()});document.getElementById('search')?.addEventListener('input',e=>{if(!e.target.value.trim()){const b=document.getElementById('searchResults');if(b)b.hidden=true}});

const siteToday=new Date(new Date().toLocaleString('en-US',{timeZone:TZ}));discoveryNodes('[data-today-label]').forEach(el=>el.textContent='TODAY · '+siteToday.toLocaleDateString('en-US',{month:'long',day:'numeric'}).toUpperCase());

// Dynamic Today and This Week context
const isoLocal=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const localToday=new Date(new Date().toLocaleString('en-US',{timeZone:TZ}));
const localTodayIso=isoLocal(localToday);
const fmtLong=d=>d.toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'});
discoveryNodes('[data-today-heading]').forEach(el=>el.textContent=fmtLong(localToday)+' Anime Releases');
discoveryNodes('[data-today-description]').forEach(el=>el.textContent='Confirmed anime premieres and important releases for '+fmtLong(localToday)+'.');
if(document.querySelector('[data-today-heading]')){document.title='Anime Releasing Today: '+fmtLong(localToday)+' — AniNextUp';const m=document.querySelector('meta[name="description"]');if(m)m.content='See anime releasing today, '+fmtLong(localToday)+', plus the next confirmed premieres and where to watch them.';}
discoveryNodes('[data-today-next]').forEach(el=>{const items=[...(D.anime||[])].filter(a=>a.date&&a.date>localTodayIso).sort((a,b)=>a.date.localeCompare(b.date)).slice(0,6);el.innerHTML=items.map(animeCard).join('')||'<p class="empty">No upcoming confirmed releases listed yet.</p>'});
const weekDow=(localToday.getDay()+6)%7,weekStart=new Date(localToday),weekEnd=new Date(localToday);weekStart.setDate(localToday.getDate()-weekDow);weekEnd.setDate(weekStart.getDate()+6);
const weekRange=weekStart.getMonth()===weekEnd.getMonth()?weekStart.toLocaleDateString('en-US',{month:'long'})+' '+weekStart.getDate()+'–'+weekEnd.getDate()+', '+weekEnd.getFullYear():weekStart.toLocaleDateString('en-US',{month:'short',day:'numeric'})+'–'+weekEnd.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
discoveryNodes('[data-week-range]').forEach(el=>el.textContent=weekRange.toUpperCase());
discoveryNodes('[data-week-title]').forEach(el=>el.textContent='This Week’s Anime Releases — '+weekRange);
discoveryNodes('[data-week-heading]').forEach(el=>el.textContent=weekRange+' Anime Releases');
discoveryNodes('[data-week-description]').forEach(el=>el.textContent='Track confirmed anime premieres, season returns and streaming releases scheduled for '+weekRange+'.');
if(document.querySelector('[data-week-heading]')){document.title='Anime Releasing This Week: '+weekRange+' — AniNextUp';const m=document.querySelector('meta[name="description"]');if(m)m.content='Track confirmed anime releasing this week, '+weekRange+', with premiere dates, streaming platforms and detailed viewing guides.';}
discoveryNodes('[data-after-week]').forEach(el=>{const endIso=isoLocal(weekEnd);const items=[...(D.anime||[])].filter(a=>a.date&&a.date>endIso).sort((a,b)=>a.date.localeCompare(b.date)).slice(0,6);el.innerHTML=items.map(animeCard).join('')||'<p class="empty">No later confirmed releases listed yet.</p>'});

// Homepage discovery sections
const homeIso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const homeToday=homeIso(new Date(new Date().toLocaleString('en-US',{timeZone:TZ})));
discoveryNodes('[data-home-latest]').forEach(el=>{const seen=new Set();const items=[...(D.anime||[]).filter(a=>a.tag&&a.article),...(D.guides||[])].filter(g=>{if(!g.article||seen.has(g.article))return false;seen.add(g.article);return true}).slice(0,6);el.innerHTML=items.map(g=>'<a class="card story visual-card" href="'+g.article+'">'+(g.image?'<img src="'+g.image+'" alt="'+g.title+'" loading="lazy">':'')+'<div class="visual-body"><span class="tag">'+g.tag+'</span><h3>'+g.title+'</h3><p>'+g.description+'</p><span class="more">READ UPDATE →</span></div></a>').join('')||'<p class="empty">No updates listed yet.</p>'});
discoveryNodes('[data-home-next]').forEach(el=>{const items=window.ANINEXTUP_RELEASES.select(D.anime||[],'after-week',releaseContext).slice(0,6);el.innerHTML=items.map(animeCard).join('')||'<p class="empty">No upcoming releases listed yet.</p>'});

// Platform-specific release hubs
for(const el of discoveryNodes('[data-anime-platform]')){
 const p=el.dataset.animePlatform;
 const match=x=>window.ANINEXTUP_RELEASES.matchesPlatform(x,p);
 const list=(D.anime||[]).filter(match).sort((x,y)=>(x.date||'9999').localeCompare(y.date||'9999'));
 el.innerHTML=list.map(animeCard).join('')||'<p class="empty">No confirmed releases yet.</p>';
}

discoveryNodes('[data-platform-count]').forEach(el=>{const p=el.dataset.platformCount;const n=(D.anime||[]).filter(x=>window.ANINEXTUP_RELEASES.matchesPlatform(x,p)).length;el.textContent=n?'· '+n+' TRACKED':''});

// Consistent, accessible related releases for every article page.
const renderRelatedReleases=data=>{
  const article=document.querySelector('article.article');
  if(!article)return;
  // Keep the editor's related links; fill only pages without a section.
  if(article.querySelector('.related-releases'))return;
  const slug=location.pathname.split('/').pop().replace(/\.html$/,'');
  const items=(data?.anime||[]).filter(a=>a.article&&a.title);
  const current=items.find(a=>a.article.split('/').pop().replace(/\.html$/,'')===slug);
  const ranked=items.filter(a=>a!==current).sort((a,b)=>{
    const score=x=>(current&&x.category===current.category?4:0)+(current&&x.platform===current.platform?2:0)+(current&&x.date&&x.date===current.date?1:0);
    return score(b)-score(a);
  }).slice(0,3);
  if(!ranked.length)return;
  const section=article.querySelector('.related-releases')||document.createElement('section');
  section.className='related-releases';
  section.dataset.autoRelated='true';
  const head=document.createElement('div');head.className='section-head';
  const title=document.createElement('div');
  const kicker=document.createElement('span');kicker.className='kicker';kicker.textContent='KEEP WATCHING';
  const h=document.createElement('h2');h.textContent='Related releases';
  title.append(kicker,h);
  const calendar=document.createElement('a');calendar.href='../calendar';calendar.textContent='FULL CALENDAR →';
  head.append(title,calendar);
  const grid=document.createElement('div');grid.className='grid three';
  ranked.forEach(a=>{
    const link=document.createElement('a');link.className='mini data-card related-card';link.href='../'+a.article.replace(/^\//,'');
    if(a.image){
      try{
        const source=new URL(a.image,location.origin+'/');
        // This cached Aoashi asset was visually confirmed to contain another work.
        if((source.protocol==='https:'||source.origin===location.origin)&&source.pathname!=='/assets/images/covers/aoashi-season-2.jpg'&&!/(?:favicon|\.svg(?:$|\?))/i.test(source.href)){
          const media=document.createElement('span');media.className='related-card-media';
          const image=document.createElement('img');image.className='related-card-image';image.alt='';image.width=160;image.height=90;image.loading='lazy';image.decoding='async';
          image.src=source.href;media.append(image);link.append(media);
        }
      }catch{/* An invalid cover must not prevent the related link from rendering. */}
    }
    const copy=document.createElement('div');copy.className='related-card-copy';
    const label=document.createElement('b');label.textContent=a.category||'ANIME RELEASE';
    const heading=document.createElement('h3');heading.textContent=a.title;
    const detail=document.createElement('span');detail.textContent=(a.dateLabel||a.date||'DATE TBA')+' · '+(a.platform||'Release updates')+' →';
    copy.append(label,heading,detail);link.append(copy);grid.append(link);
  });
  section.replaceChildren(head,grid);
  article.appendChild(section);
};
if(document.querySelector('article.article')){
  if(D.anime?.length)renderRelatedReleases(D);
  else{const script=document.createElement('script');script.src='../assets/data.js';script.onload=()=>renderRelatedReleases(window.ANINEXTUP_DATA);document.head.appendChild(script);}
}


// Every KEEP WATCHING card gets artwork, including legacy hand-authored sections.
// Prefer the destination article's cover, never reuse the current article's image.
async function ensureRelatedReleaseCovers(){
  const sections=document.querySelectorAll('article.article .related-releases');
  if(!sections.length)return;
  const entries=(window.ANINEXTUP_DATA?.anime||[]).concat(window.ANINEXTUP_DATA?.guides||[]);
  const coverBySlug=new Map(entries.filter(x=>x.article&&x.image).map(x=>[x.article.split('/').pop().replace(/\.html$/,''),x.image]));
  for(const section of sections){
    for(const link of section.querySelectorAll('a.mini')){
      const destination=new URL(link.getAttribute('href'),location.href);
      const slug=destination.pathname.split('/').pop().replace(/\.html$/,'');
      let img=link.querySelector('img');
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

