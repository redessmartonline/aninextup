(()=>{'use strict';
const root=document.querySelector('.calendar-expanded'),data=document.getElementById('calendar-catalog');if(!root||!data)return;
const model=window.ANINEXTUP_CALENDAR,catalog=JSON.parse(data.textContent);if(!model)return;
const byId=id=>document.getElementById(id),month=byId('cal-month'),query=byId('cal-query'),format=byId('cal-format'),platform=byId('cal-platform'),precision=byId('cal-precision'),results=byId('cal-results'),count=byId('cal-count');
let selectedDay=null;const picker=document.createElement('section');picker.className='calendar-month-box calendar-picker';picker.setAttribute('aria-label','Choose a premiere day');results.before(picker);
const el=(tag,text,cls)=>{const x=document.createElement(tag);if(text)x.textContent=text;if(cls)x.className=cls;return x;};
const label=m=>new Date(m+'-01T12:00:00Z').toLocaleDateString('en-US',{month:'long',year:'numeric',timeZone:'UTC'});
function card(a){const x=el('a',null,'calendar-release');x.href='/'+a.article.replace(/^\//,'');x.append(el('span',(a.date||a.dateLabel||'Date TBA')+' · '+model.precision(a),'calendar-release-date'),el('h3',a.title),el('p',model.format(a)+' · '+a.platform),el('small','Read guide for territories, language options and official sources →'));return x;}
function matches(a){return model.matches(a,{query:query.value.trim(),format:format.value,platform:platform.value,precision:precision.value})&&(!month.value||(month.value==='announced'?!model.monthOf(a):model.monthOf(a)===month.value))&&(!selectedDay||a.date===selectedDay);}
function drawPicker(){picker.replaceChildren();picker.hidden=!catalog.months.includes(month.value);if(picker.hidden)return;
picker.append(el('h2',label(month.value)));const clear=el('button','Show entire month','calendar-view-toggle');clear.type='button';clear.onclick=()=>{selectedDay=null;render();};picker.append(clear);
const week=el('div',null,'calendar-weekdays');for(const day of ['SU','MO','TU','WE','TH','FR','SA'])week.append(el('span',day));picker.append(week);
const grid=el('div',null,'calendar-days'),[y,m]=month.value.split('-').map(Number),first=new Date(Date.UTC(y,m-1,1)).getUTCDay(),length=new Date(Date.UTC(y,m,0)).getUTCDate();
for(let i=0;i<first;i++){const blank=el('span',null,'calendar-empty');blank.setAttribute('aria-hidden','true');grid.append(blank);}
for(let d=1;d<=length;d++){const iso=month.value+'-'+String(d).padStart(2,'0'),n=catalog.items.filter(a=>a.date===iso&&model.matches(a,{query:query.value.trim(),format:format.value,platform:platform.value,precision:precision.value})).length;const b=el('button',String(d),'calendar-day'+(n?' has-releases':''));b.type='button';b.setAttribute('aria-label',label(month.value)+' '+d+': '+n+' tracked releases');b.setAttribute('aria-pressed',String(selectedDay===iso));b.onclick=()=>{selectedDay=selectedDay===iso?null:iso;render();picker.querySelector('[aria-label="'+b.getAttribute('aria-label')+'"]')?.focus();};grid.append(b);}picker.append(grid,el('p','Dots mark exact premiere dates. Month-only announcements appear below the grid.','calendar-legend'));
}
function render(){const items=catalog.items.filter(matches);results.replaceChildren();drawPicker();count.textContent=items.length+' matching '+(items.length===1?'release':'releases')+(selectedDay?' · '+selectedDay:'');
for(const m of [...catalog.months,'announced']){if(month.value&&month.value!==m)continue;const list=items.filter(a=>m==='announced'?!model.monthOf(a):model.monthOf(a)===m).sort((a,b)=>(a.date||'9999').localeCompare(b.date||'9999')||a.title.localeCompare(b.title));if(!list.length&&!month.value)continue;const section=el('section',null,'calendar-release-group');section.append(el('h2',m==='announced'?'Season, year & date to be announced':label(m)));const grid=el('div',null,'calendar-release-grid');for(const a of list)grid.append(card(a));if(!list.length)grid.append(el('p','No tracked releases match these filters. Try clearing the filters or choosing another month.','empty'));section.append(grid);results.append(section);}
if(!results.children.length)results.append(el('p','No tracked releases match these filters.','empty'));
}
for(const input of [month,format,platform,precision])input.addEventListener('change',()=>{selectedDay=null;render();});query.addEventListener('input',()=>{selectedDay=null;render();});byId('cal-clear').onclick=()=>{for(const x of [month,query,format,platform,precision])x.value='';selectedDay=null;render();query.focus();};
render();
})();
