const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),model=require('../assets/calendar-model.js');
const context={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,'assets/data.js'),'utf8'),context);
const catalog=new Map(),slug=a=>String(a.article||'').replace(/^\//,'').replace(/\.html$/,'');
for(const a of context.window.ANINEXTUP_DATA.anime||[])if(a.category||a.date||a.dateLabel)catalog.set(slug(a),{...a});
for(const name of fs.readdirSync(path.join(root,'articles')).filter(x=>x.endsWith('.html'))){
 const html=fs.readFileSync(path.join(root,'articles',name),'utf8'),raw=html.match(/<script type="application\/json" id="aninextup-index">([\s\S]*?)<\/script>/)?.[1];if(!raw)continue;
 let meta;try{meta=JSON.parse(raw);}catch{throw Error('Invalid article index: '+name);}
 const article='articles/'+name.replace(/\.html$/,'');
 const summary=html.match(/<section class="release-summary"[\s\S]*?<\/section>/)?.[0]||'';
 const clean=s=>s.replace(/<[^>]*>/g,' ').replace(/&amp;/g,'&').replace(/\s+/g,' ').trim();
 const rows=[...summary.matchAll(/<dt[^>]*>([\s\S]*?)<\/dt>\s*<dd[^>]*>([\s\S]*?)<\/dd>/g)].map(m=>[clean(m[1]),clean(m[2])]);
 const release=rows.find(([k])=>/^(?:release|premiere|japan premiere|japanese premiere|premiere window|release window)$/i.test(k))?.[1];
 if(!meta.date&&!meta.dateLabel&&release){
  const monthNames=model.months.join('|'),exact=release.match(new RegExp('('+monthNames+')\\s+(\\d{1,2}),?\\s+(20\\d{2})','i'));
  if(exact){const m=model.months.findIndex(x=>x.toLowerCase()===exact[1].toLowerCase());let d=new Date(Date.UTC(Number(exact[3]),m,Number(exact[2])));if(/\b2[4-9]:\d{2}/.test(release))d.setUTCDate(d.getUTCDate()+1);meta.date=d.toISOString().slice(0,10);meta.dateLabel=release;meta.status='confirmed';}
  else if(/\b20\d{2}\b/.test(release)){meta.dateLabel=release;meta.status=model.monthOf({dateLabel:release})?'month-confirmed':'tba';}
 }
 if(!meta.platform){meta.platform=rows.find(([k])=>/^(?:where to watch|streaming|broadcaster|japanese broadcaster|global streaming)$/i.test(k))?.[1];}
 if(!meta.category&&!meta.date&&!meta.dateLabel&&!['new-anime','returning-series'].includes(meta.newsCategory))continue;
 if(/manga|live-action/.test(article))continue;
 if(/codes|manga|live.action|collection|event/i.test(meta.category||''))continue;
 catalog.set(article,{...catalog.get(article),...meta,article});
}
const items=[...catalog.values()].filter(a=>a.title&&a.article).map(a=>({...a,date:a.date||null,platform:a.platform||'Not announced'}));
const now=new Date(process.env.ANINEXTUP_NOW||Date.now()),months=model.range(now),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const label=m=>new Date(m+'-01T12:00:00Z').toLocaleDateString('en-US',{month:'long',year:'numeric',timeZone:'UTC'});
const card=a=>'<a class="calendar-release" href="/'+esc(a.article)+'"><span class="calendar-release-date">'+esc(a.date||a.dateLabel||'Date TBA')+' · '+esc(model.precision(a))+'</span><h3>'+esc(a.title)+'</h3><p>'+esc(model.format(a))+' · '+esc(a.platform)+'</p><small>Read guide for territories, language options and official sources →</small></a>';
const dated=items.filter(a=>months.includes(model.monthOf(a)));
const pending=items.filter(a=>!model.monthOf(a));
let body='<section class="calendar-expanded" aria-label="Anime release tracker"><div class="calendar-filter-bar"><label>Month<select id="cal-month"><option value="">All 12 months</option>'+months.map(m=>'<option value="'+m+'">'+label(m)+'</option>').join('')+'<option value="announced">Season, year &amp; date TBA</option></select></label><label>Search title<input type="search" id="cal-query" placeholder="Search anime..."></label><label>Format<select id="cal-format"><option value="">All formats</option>'+['New series','Returning series','Movies','Specials'].map(x=>'<option>'+x+'</option>').join('')+'</select></label><label>Platform / distribution<select id="cal-platform"><option value="">All platforms</option>'+[...new Set(items.map(a=>a.platform))].sort().map(x=>'<option>'+esc(x)+'</option>').join('')+'</select></label><label>Date status<select id="cal-precision"><option value="">All date statuses</option>'+['Exact date','Month confirmed','Season announced','Year announced','Date TBA'].map(x=>'<option>'+x+'</option>').join('')+'</select></label><button type="button" id="cal-clear">Clear filters</button><p id="cal-count" role="status" aria-live="polite">'+dated.length+' releases across the next 12 months; '+pending.length+' announcements without an exact month.</p></div><div id="cal-results">';
for(const m of months){const list=dated.filter(a=>model.monthOf(a)===m).sort((a,b)=>(a.date||'9999').localeCompare(b.date||'9999'));body+='<section class="calendar-release-group" data-calendar-month="'+m+'"><h2>'+label(m)+'</h2><div class="calendar-release-grid">'+(list.map(card).join('')||'<p class="empty">No releases tracked for this month yet. This is not a complete industry schedule.</p>')+'</div></section>';}
body+='<section class="calendar-release-group" data-calendar-month="announced"><h2>Season, year &amp; date to be announced</h2><p>These entries are not assigned to a day or month. A season or year announcement is not an exact premiere date.</p><div class="calendar-release-grid">'+pending.sort((a,b)=>(a.dateLabel||'zzz').localeCompare(b.dateLabel||'zzz')).map(card).join('')+'</div></section></div><noscript>All tracked releases are listed above. Enable JavaScript to use the filters.</noscript></section>';
const payload=JSON.stringify({months,items:items.filter(a=>months.includes(model.monthOf(a))||!model.monthOf(a))}).replace(/</g,'\\u003c');
body+='<script id="calendar-catalog" type="application/json">'+payload+'</script>';
const file=path.join(root,'calendar.html');let html=fs.readFileSync(file,'utf8');html=html.replace(/<!-- calendar-expanded:start -->[\s\S]*?<!-- calendar-expanded:end -->/,'<!-- calendar-expanded:start -->'+body+'<!-- calendar-expanded:end -->');
for(const asset of ['calendar-model.js','calendar-ui.js']){const version=crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'assets',asset))).digest('hex').slice(0,12);html=html.replace(new RegExp('assets/'+asset.replace('.','\\.')+'(?:\\?[^" ]*)?','g'),'assets/'+asset+'?v='+version);}
fs.writeFileSync(file,html);console.log(JSON.stringify({months:months.length,dated:dated.length,announced:pending.length,total:items.length}));
