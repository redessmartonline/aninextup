// Build Where to Watch from catalog records and explicit article metadata.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),box={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(root,'assets/data.js'),'utf8'),box);
const platforms=['Crunchyroll','Netflix','Disney+','Prime Video','HIDIVE'];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const entries=new Map();
function add(item){
 if(!item||!item.article||!item.title||!item.platform)return;
 if(/not announced|unconfirmed|\\bTBA\\b|rumou?r/i.test(item.platform))return;
 const article=item.article.replace(/^https:\/\/aninextup.com\//,'').replace(/^\//,'').replace(/\.html$/,'');
 if(!/^articles\/[a-z0-9-]+$/.test(article)||!fs.existsSync(path.join(root,article+'.html')))return;
 entries.set(article,{...item,article});
}
for(const a of box.window.ANINEXTUP_DATA.anime||[])add(a);
for(const file of fs.readdirSync(path.join(root,'articles')).filter(f=>f.endsWith('.html'))){
 const html=fs.readFileSync(path.join(root,'articles',file),'utf8');
 for(const match of html.matchAll(/<script\b[^>]*\bid=["']aninextup-index["'][^>]*>([\s\S]*?)<\/script>/gi)){
  let a;try{a=JSON.parse(match[1]);}catch(e){throw new Error('Invalid editorial index in '+file);}
  // Only explicit, confirmed editorial platform fields may add a new listing.
  if(!['confirmed','month-confirmed'].includes(a.status))continue;
  add({...a,article:'articles/'+file.replace(/\.html$/,'')});
 }
}
function replaceContents(html,attr,render){
 const regex=new RegExp('<([a-z][a-z0-9]*)\\b[^>]*\\s'+attr+'="([^"]*)"[^>]*>','gi');
 const edits=[];let m;
 while((m=regex.exec(html))){
  const tags=new RegExp('<\\/?'+m[1]+'\\b[^>]*>','gi');tags.lastIndex=regex.lastIndex;
  let depth=1,t;while((t=tags.exec(html))){depth+=t[0].startsWith('</')?-1:1;if(!depth)break;}
  if(depth)throw new Error('Unclosed '+attr);
  edits.push([regex.lastIndex,t.index,render(m[2])]);
 }
 for(const [start,end,value] of edits.reverse())html=html.slice(0,start)+value+html.slice(end);
 return html;
}
let html=fs.readFileSync(path.join(root,'where-to-watch.html'),'utf8');
// Preserve this server-rendered catalog instead of replacing it from an older browser index.
html=html.replaceAll('data-anime-platform','data-watch-catalog-platform').replaceAll('data-platform-count','data-watch-catalog-count');
const lists={};
for(const p of platforms){
 lists[p]=[...entries.values()].filter(a=>a.platform===p||a.platform.startsWith(p+' ')||a.platform.startsWith(p+'/')).sort((a,b)=>(a.date||'9999').localeCompare(b.date||'9999')||a.title.localeCompare(b.title));
}
html=replaceContents(html,'data-watch-catalog-platform',p=>(lists[p]||[]).map(a=>{
 const label=a.dateLabel||(a.date&&/^\d{4}-\d{2}-\d{2}$/.test(a.date)?a.date:'DATE TBA');
 return '<a class="mini data-card visual-card" href="'+esc(a.article)+'">'+(a.image?'<img src="'+esc(a.image)+'" alt="'+esc(a.title)+'" loading="lazy">':'')+'<div class="visual-body"><b>'+esc(label)+'</b><h3>'+esc(a.title)+'</h3><span>'+esc(a.platform)+'</span></div></a>';
}).join('')||'<p class="empty">No confirmed releases listed yet.</p>');
html=replaceContents(html,'data-watch-catalog-count',p=>'· '+(lists[p]||[]).length+' TRACKED');
html=replaceContents(html,'data-watch-total',p=>String((lists[p]||[]).length));
fs.writeFileSync(path.join(root,'where-to-watch.html'),html);
console.log('Where to Watch: '+platforms.map(p=>p+' '+lists[p].length).join(', '));
