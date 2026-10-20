// Build crawlable discovery lists from the same index and date rules as the UI.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const model=require('../assets/release-model.js');
const dataSource=fs.readFileSync(path.join(root,'assets/data.js'),'utf8');
const dataVersion=crypto.createHash('sha256').update(dataSource).digest('hex').slice(0,16);
const sandbox={window:{}};vm.runInNewContext(dataSource,sandbox);
const data=sandbox.window.ANINEXTUP_DATA;
const now=process.env.ANINEXTUP_NOW?new Date(process.env.ANINEXTUP_NOW):new Date();
const ctx=model.context(now,data.site.timezone);
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const state=a=>a.status==='month-confirmed'?'MONTH CONFIRMED':a.status==='tba'?'DATE TBA':'CONFIRMED';
const date=a=>a.date?new Date(a.date+'T12:00:00Z').toLocaleDateString('en-US',{timeZone:'UTC',month:'short',day:'2-digit'}).toUpperCase():(a.dateLabel||'DATE TBA').toUpperCase();
function card(a,full=false){
  return `<a class="${full?'card story':'mini'} data-card visual-card" href="${escape(a.article)}">${a.image?`<img src="${escape(a.image)}" alt="${escape(a.title)}" loading="lazy">`:''}<div class="visual-body"><b>${escape(date(a))}</b><small class="status">${state(a)}</small><h3>${escape(a.title)}</h3><span>${escape(a.platform)}</span>${full?'<span class="more">READ GUIDE →</span>':''}</div></a>`;
}
function guide(g){return `<a class="card story visual-card" href="${escape(g.article)}">${g.image?`<img src="${escape(g.image)}" alt="${escape(g.title)}" loading="lazy">`:''}<div class="visual-body"><span class="tag">${escape(g.tag||'OFFICIAL NEWS')}</span><h3>${escape(g.title)}</h3>${g.description?`<p>${escape(g.description)}</p>`:''}<span class="more">READ UPDATE →</span></div></a>`;}
// Find matching closing tags, including nested divs, without rewriting the page.
function fill(html,attribute,render){
  const pattern=new RegExp(`<([a-z][a-z0-9]*)\\b[^>]*\\s${attribute}(?:="([^"]*)")?(?=[\\s>])[^>]*>`,'gi');
  const edits=[];let match;
  while((match=pattern.exec(html))){
    const tags=new RegExp(`</?${match[1]}\\b[^>]*>`,'gi');tags.lastIndex=pattern.lastIndex;
    let depth=1,tag;while((tag=tags.exec(html))){depth+=tag[0].startsWith('</')?-1:1;if(!depth)break;}
    if(depth)throw new Error('Unclosed '+attribute);
    edits.push([pattern.lastIndex,tag.index,render(match[2])]);
  }
  for(const [start,end,value] of edits.reverse())html=html.slice(0,start)+value+html.slice(end);
  return html;
}
const editorialStories=()=>{const seen=new Set();return [...data.anime.filter(a=>a.tag&&a.article),...data.guides].filter(g=>{if(!g.article||seen.has(g.article))return false;seen.add(g.article);return true;});};
// Match the browser's category rules, including releases without a guide tag.
const newsCategories=new Set(['new-anime','returning-series','trailers-cast','release-news']);
const newsStories=()=>{const seen=new Set();return [...data.anime,...data.guides].filter(g=>{if(!g.article||seen.has(g.article)||!newsCategories.has(g.newsCategory))return false;seen.add(g.article);return true;});};
const list=(items,full=false,empty='No confirmed releases yet.')=>items.map(a=>card(a,full)).join('')||`<p class="empty">${escape(empty)}</p>`;
let changed=0;
for(const name of fs.readdirSync(root).filter(n=>n.endsWith('.html'))){
  const file=path.join(root,name),original=fs.readFileSync(file,'utf8');let html=original;
  html=fill(html,'data-anime-list',mode=>list(model.select(data.anime,mode,ctx),mode==='today','No premieres confirmed for this date. Explore the upcoming releases below.'));
  for(const [hook,mode,limit] of [['data-home-next','after-week',6],['data-today-next','next',6],['data-after-week','after-week',6],['data-news-upcoming','upcoming',9]])html=fill(html,hook,()=>list(model.select(data.anime,mode,ctx).slice(0,limit),hook==='data-news-upcoming'));
  html=fill(html,'data-anime-month',month=>list(model.select(data.anime,'calendar',ctx).filter(a=>a.date.startsWith(month))));
  html=fill(html,'data-month-count',month=>{const n=data.anime.filter(a=>a.date?.startsWith(month)).length;return n?'· '+n+' CONFIRMED':'';});
  html=fill(html,'data-anime-platform',platform=>list(model.select(data.anime.filter(a=>model.matchesPlatform(a,platform)),'all',ctx)));
  html=fill(html,'data-platform-count',platform=>{const n=data.anime.filter(a=>model.matchesPlatform(a,platform)).length;return n?'· '+n+' TRACKED':'';});
  html=fill(html,'data-home-latest',()=>editorialStories().slice(0,6).map(guide).join(''));
  html=fill(html,'data-guides',()=>newsStories().map(guide).join(''));
  // A new release index must not be replaced by a day-old cached script.
  html=html.replace(/(<script\b[^>]*\bsrc=")assets\/data\.js(?:\?[^"\s]*)?"/g,(_,prefix)=>prefix+'assets/data.js?v='+dataVersion+'"');
  // All discovery pages load shared selectors before client-side refresh.
  if(html.includes('assets/data.js')&&!html.includes('src="assets/release-model.js'))html=html.replace(/<script src="assets\/app\.js[^\"]*"><\/script>/,'<script src="assets/release-model.js?v=discovery1"></script><script src="assets/app.js?v=discovery1"></script>');
  if(html!==original){fs.writeFileSync(file,html);changed++;}
}
console.log(`Discovery HTML updated: ${changed} pages; ${ctx.today}, week ending ${ctx.weekEnd}.`);

