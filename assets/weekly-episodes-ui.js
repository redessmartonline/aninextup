(function(){
const data=window.ANINEXTUP_WEEKLY_EPISODES;
const todayRoot=document.querySelector('[data-weekly-episodes]');
const weekRoot=document.querySelector('[data-weekly-episodes-week]');
const select=document.querySelector('[data-episode-region]');
if(!data||(!todayRoot&&!weekRoot))return;
const tz=window.ANINEXTUP_DATA&&window.ANINEXTUP_DATA.site&&window.ANINEXTUP_DATA.site.timezone||data.timezone||'America/Santo_Domingo';
const regions=data.regions||[];let selected=select?Number(select.value):2;if(!Number.isInteger(selected)||selected<0||selected>=regions.length)selected=2;
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const today=zone=>{const parts=new Intl.DateTimeFormat('en-US',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());const get=t=>parts.find(p=>p.type===t).value;return get('year')+'-'+get('month')+'-'+get('day');};
const dayLabel=d=>new Date(d+'T12:00:00Z').toLocaleDateString('en-US',{weekday:'long',month:'short',day:'numeric',timeZone:'UTC'});
const timeLabel=t=>{const p=t.split(':'),h=Number(p[0]);return (h%12||12)+':'+p[1]+' '+(h>=12?'PM':'AM');};
const displayDate=e=>{const d=new Date(e.date+'T12:00:00Z');if((e.nextDayRegions||[]).includes(selected))d.setUTCDate(d.getUTCDate()+1);return d.toISOString().slice(0,10);};
const renderCard=(e,date)=>{const next=(e.nextDayRegions||[]).includes(selected),slot=e.times[selected]||e.times[2]||e.times[0];return '<article class="episode-card"><div class="episode-card-title"><h3><a href="'+esc(e.url)+'" target="_blank" rel="noopener noreferrer">'+esc(e.title)+'</a></h3><span>Episode '+esc(e.episode)+'</span></div><p class="episode-meta">'+esc(dayLabel(date||e.date))+' · Crunchyroll</p><p class="episode-time">'+esc(timeLabel(slot)+(next?' (next day)':'')+' · '+regions[selected])+'</p></article>';};
function render(){
 const current=today(tz);
 if(todayRoot){
  const items=data.episodes.filter(e=>e.date===current);
  todayRoot.innerHTML=items.length?items.map(e=>renderCard(e,e.date)).join(''):'<p class="empty">No weekly episode schedule is listed here for today. Check <a href="'+esc(data.sourceUrl)+'" target="_blank" rel="noopener noreferrer">Crunchyroll’s official weekly calendar</a> for the latest regional schedule.</p>';
 }
 if(weekRoot){
  const start=new Date(current+'T12:00:00Z');start.setUTCDate(start.getUTCDate()-((start.getUTCDay()+6)%7));
  const end=new Date(start);end.setUTCDate(start.getUTCDate()+6);
  const iso=d=>d.toISOString().slice(0,10),startIso=iso(start),endIso=iso(end);
  const items=data.episodes.map(e=>({...e,localDate:displayDate(e)})).filter(e=>e.localDate>=startIso&&e.localDate<=endIso).sort((a,b)=>a.localDate.localeCompare(b.localDate)||(a.times[selected]||'').localeCompare(b.times[selected]||''));
  if(items.length){
   const groups=new Map();items.forEach(e=>{if(!groups.has(e.localDate))groups.set(e.localDate,[]);groups.get(e.localDate).push(e);});
   weekRoot.innerHTML=[...groups.entries()].map(([date,eps])=>'<section class="episode-day-group"><h3>'+esc(dayLabel(date))+'</h3><div class="episode-schedule">'+eps.map(e=>renderCard(e,e.localDate)).join('')+'</div></section>').join('');
  }else{
   weekRoot.innerHTML='<p class="empty">No weekly episodes are listed for this week. Check <a href="'+esc(data.sourceUrl)+'" target="_blank" rel="noopener noreferrer">Crunchyroll’s official schedule</a> for the latest regional lineup.</p>';
  }
 }
}
if(select)select.addEventListener('change',()=>{selected=Number(select.value);render();});
render();
})();