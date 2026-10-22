(function(){
const data=window.ANINEXTUP_WEEKLY_EPISODES,root=document.querySelector('[data-weekly-episodes]'),select=document.querySelector('[data-episode-region]');
if(!data||!root)return;
const tz=window.ANINEXTUP_DATA&&window.ANINEXTUP_DATA.site&&window.ANINEXTUP_DATA.site.timezone||data.timezone||'America/Santo_Domingo';
const regions=data.regions||[];let selected=select?Number(select.value):2;if(!Number.isInteger(selected)||selected<0||selected>=regions.length)selected=2;
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const today=zone=>{const parts=new Intl.DateTimeFormat('en-US',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());const get=t=>parts.find(p=>p.type===t).value;return get('year')+'-'+get('month')+'-'+get('day');};
const dayLabel=d=>new Date(d+'T12:00:00Z').toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric',timeZone:'UTC'});
const timeLabel=t=>{const p=t.split(':'),h=Number(p[0]);return (h%12||12)+':'+p[1]+' '+(h>=12?'PM':'AM');};
const renderCard=e=>{const next=(e.nextDayRegions||[]).includes(selected),slot=e.times[selected]||e.times[2]||e.times[0];return '<article class="episode-card"><div class="episode-card-title"><h3><a href="'+esc(e.url)+'" target="_blank" rel="noopener noreferrer">'+esc(e.title)+'</a></h3><span>Episode '+esc(e.episode)+'</span></div><p class="episode-meta">'+esc(dayLabel(e.date))+' · Crunchyroll</p><p class="episode-time" data-regional-times="'+esc(e.times.join('|'))+'" data-next-day-regions="'+esc((e.nextDayRegions||[]).join(','))+'">'+esc(timeLabel(slot)+(next?' (next day)':'')+' · '+regions[selected])+'</p></article>';};
function render(){const date=today(tz),items=data.episodes.filter(e=>e.date===date);root.innerHTML=items.length?items.map(renderCard).join(''):'<p class="empty">No weekly episode schedule is listed here for today. Check <a href="'+esc(data.sourceUrl)+'" target="_blank" rel="noopener noreferrer">Crunchyroll’s official weekly calendar</a> for the latest regional schedule.</p>';}
if(select)select.addEventListener('change',()=>{selected=Number(select.value);render();});
render();
})();
