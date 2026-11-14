(function(root,factory){
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.ANINEXTUP_VERIFIED_BROADCASTS=api;
 if(typeof document==='undefined')return;
 const list=document.querySelector('[data-verified-broadcasts]');if(!list)return;
 const picker=document.getElementById('broadcast-timezone');
 function update(){
  const zone=picker?.value||'UTC',now=new Date(),state=api.state(now,zone);
  list.innerHTML=api.render(now,zone);
  list.dataset.scheduleState=state.covered?'verified-selection':'awaiting-verification';
  const heading=document.getElementById('broadcast-date');if(heading)heading.textContent=api.dayLabel(state.day)+' · '+api.zoneLabel(zone);
  const count=document.getElementById('today-count');if(count)count.textContent=state.covered?String(state.items.length):'Update pending';
  const networks=document.getElementById('today-platforms');if(networks)networks.textContent=state.covered?[...new Set(state.items.map(e=>e.network))].join(' · '):'Japan TV sources';
  const meta=document.querySelector('meta[name="description"]');if(meta)meta.content=state.covered?'Anime airing today: verified Japan TV episodes, broadcaster sources and UTC, US and UK time conversions. First premieres and streaming guides listed separately.':'Anime airing today: check current schedule coverage and official release calendars. New verified broadcaster listings are awaiting review.';
 }
 picker?.addEventListener('change',update);update();
 // Re-check the date when a reader returns to a tab or leaves it open overnight.
 setInterval(update,60000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)update();});
})(typeof window!=='undefined'?window:null,function(){
 const data={
  verifiedOn:'2026-11-14',defaultZone:'UTC',
  scope:'Selected Japanese television broadcasts verified against date-specific broadcaster listings. This is not a complete anime schedule or an international streaming timetable.',
  zones:[['UTC','UTC'],['America/New_York','US Eastern'],['America/Los_Angeles','US Pacific'],['Europe/London','United Kingdom'],['Asia/Tokyo','Japan · JST'],['America/Sao_Paulo','Brazil · Brasília']],
  episodes:[
   {id:'ramparts-20',title:'The Ramparts of Ice',episode:'Episode 20 · series numbering',scheduledAt:'2026-11-05T23:56:00+09:00',network:'TBS',url:'/articles/ramparts-of-ice-season-2',sourceUrl:'https://www.tbs.co.jp/tv/20261105_C3F4.html',sourceLabel:'TBS · November 5 program listing'},
   {id:'heavy-knight-19',title:'The Exiled Heavy Knight Knows How to Game the System',episode:'Episode 19',scheduledAt:'2026-11-06T00:26:00+09:00',network:'TBS',url:null,sourceUrl:'https://www.tbs.co.jp/tv/20261105_C3F5.html',sourceLabel:'TBS · November 5 late-night program listing'},
   {id:'iceblade-5',title:'The Iceblade Sorcerer Shall Rule the World II',episode:'Episode 5',scheduledAt:'2026-11-06T01:28:00+09:00',network:'TBS',url:'/articles/iceblade-sorcerer-ii',sourceUrl:'https://www.tbs.co.jp/tv/20261105_C3F8.html',sourceLabel:'TBS · November 5 late-night program listing'},
   {id:'fx-kurumi-6-ktv',title:'FX Fighter Kurumi-chan',episode:'Episode 6 · Kansai TV airing',scheduledAt:'2026-11-06T01:45:00+09:00',network:'Kansai TV',url:null,sourceUrl:'https://www.ktv.jp/fxkurumi/',sourceLabel:'Kansai TV · November 5 late-night program listing'},
   {id:'blue-box-s2-5',title:'Blue Box Season 2',episode:'Episode 5',scheduledAt:'2026-11-08T16:30:00+09:00',network:'TBS',url:'/articles/blue-box-season-2',sourceUrl:'https://www.tbs.co.jp/tv/20261108_C454.html',sourceLabel:'TBS · November 8 program listing'},
   {id:'aoashi-s2-6',title:'Aoashi Season 2',episode:'Episode 6',scheduledAt:'2026-11-08T17:00:00+09:00',network:'NHK E Tele',url:'/articles/aoashi-season-2',sourceUrl:'https://aoashi-pr.com/story/',sourceLabel:'Official Aoashi · Episode 6'},
   {id:'yozakura-44',title:'Mission: Yozakura Family Season 2',episode:'Episode 44 · series numbering',scheduledAt:'2026-11-08T17:00:00+09:00',network:'TBS',url:null,sourceUrl:'https://www.tbs.co.jp/tv/20261108_C455.html',sourceLabel:'TBS · November 8 program listing'},
   {id:'ace-of-diamond-act-ii-s2-18',title:'Ace of the Diamond act II -Second Season-',episode:'Episode 18',scheduledAt:'2026-11-08T17:30:00+09:00',network:'TV Tokyo',url:'/articles/ace-of-diamond-second-season',sourceUrl:'https://www.tv-tokyo.co.jp/broad_tvtokyo/program/detail/202611/29059_202611081730.html',sourceLabel:'TV Tokyo · November 8 program listing'},
   {id:'appraisal-skill-31',title:"As a Reincarnated Aristocrat, I'll Use My Appraisal Skill to Rise in the World Season 3",episode:'Episode 31 · series numbering',scheduledAt:'2026-11-08T23:40:00+09:00',network:'TBS',url:null,sourceUrl:'https://www.tbs.co.jp/tv/20261108_C462.html',sourceLabel:'TBS · November 8 program listing'},
   {id:'dark-summoner-6',title:"I'm Dating a Dark Summoner!",episode:'Episode 6',scheduledAt:'2026-11-09T01:20:00+09:00',network:'TOKYO MX',url:null,sourceUrl:'https://darksummoner.deregula.com/onair/',sourceLabel:'Official Dark Summoner · Sunday late-night TV slot'},
   {id:'vanguard-divinez-14',title:'Cardfight!! Vanguard Divinez',episode:'Episode 14 · current arc',scheduledAt:'2026-11-14T08:00:00+09:00',network:'TV Tokyo',url:null,sourceUrl:'https://www.tv-tokyo.co.jp/broad_tvtokyo/program/detail/202611/26481_202611140800.html',sourceLabel:'TV Tokyo · November 14 program listing'},
   {id:'detective-conan-1220',title:'Detective Conan',episode:'Episode 1220',scheduledAt:'2026-11-14T18:00:00+09:00',network:'Yomiuri TV / Nippon TV',url:null,sourceUrl:'https://www.ytv.co.jp/webmagazine/anime/940_tbpyg75p8watavcr.html',sourceLabel:'Yomiuri TV · November 14 broadcast notice'}
  ]
 };
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const validZone=zone=>data.zones.some(z=>z[0]===zone)?zone:data.defaultZone;
 const day=(instant,zone)=>{const p=new Intl.DateTimeFormat('en-US',{timeZone:validZone(zone),year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date(instant));const get=t=>p.find(x=>x.type===t).value;return get('year')+'-'+get('month')+'-'+get('day');};
 const time=(instant,zone)=>new Intl.DateTimeFormat('en-US',{timeZone:validZone(zone),hour:'numeric',minute:'2-digit',hour12:true}).format(new Date(instant));
 const dayLabel=date=>new Date(date+'T12:00:00Z').toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric',timeZone:'UTC'});
 const zoneLabel=zone=>data.zones.find(z=>z[0]===zone)?.[1]||'UTC';
 function state(now,zone='UTC'){
  zone=validZone(zone);const current=day(now,zone);
  const items=data.episodes.filter(e=>day(e.scheduledAt,zone)===current).sort((a,b)=>Date.parse(a.scheduledAt)-Date.parse(b.scheduledAt));
  return {day:current,covered:items.length>0,items};
 }
 function render(now,zone='UTC'){
  zone=validZone(zone);const current=state(now,zone);
  if(!current.covered)return '<p class="empty" role="status">No current verified selection is available for '+esc(dayLabel(current.day))+'. The last source check was '+data.verifiedOn+'. This does not mean nothing is airing. Check the <a href="https://www.crunchyroll.com/releasecalendar" target="_blank" rel="noopener noreferrer">official streaming calendar</a> or the broadcaster links in our <a href="/calendar">release guides</a>.</p>';
  return current.items.map(e=>'<article class="episode-card"><div class="episode-card-title"><h3>'+(e.url?'<a href="'+esc(e.url)+'">'+esc(e.title)+'</a>':esc(e.title))+'</h3><span>'+esc(e.episode)+'</span></div><p class="episode-meta">'+esc(e.network)+' · Japan television</p><p class="episode-time"><time datetime="'+esc(e.scheduledAt)+'">'+esc(time(e.scheduledAt,zone))+'</time> · '+esc(zoneLabel(zone))+'</p><p class="episode-language">Japan airing: '+esc(dayLabel(day(e.scheduledAt,'Asia/Tokyo')))+' · '+esc(time(e.scheduledAt,'Asia/Tokyo'))+' JST. Streaming unlocks and English-language versions are not verified here.</p><p class="episode-source"><a href="'+esc(e.sourceUrl)+'" target="_blank" rel="noopener noreferrer">'+esc(e.sourceLabel)+'</a></p></article>').join('');
 }
 return {data,day,time,dayLabel,zoneLabel,state,render};
});
