const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('assets/app.js','utf8');
const start=source.indexOf('let siteSearchIndexPromise=null,siteSearchRequest=0;');
const coreEnd=source.indexOf('// Make the same article search available',start);
const searchStart=source.indexOf('async function searchSite(');
const searchEnd=source.indexOf("\ndocument.getElementById('search')?.addEventListener",searchStart);
assert(start>=0&&coreEnd>start&&searchEnd>searchStart);
const code=source.slice(start,coreEnd)+source.slice(searchStart,searchEnd)+';this.searchSite=searchSite;this.normalizeSiteSearch=normalizeSiteSearch;';
function setup(fetch,anime=[]){
 const input={value:'Berserk'},box={hidden:true,innerHTML:''};
 const document={getElementById:id=>id==='search'?input:id==='searchResults'?box:null,createElement(tag){const el={tag,children:[],append(...xs){this.children.push(...xs)}};Object.defineProperty(el,'outerHTML',{get(){return this.tag==='a'?'<a href="'+this.href+'">'+this.children.map(x=>x.textContent).join('')+'</a>':'<'+this.tag+'>'+this.textContent+'</'+this.tag+'>'}});return el}};
 const context={document,window:{ANINEXTUP_DATA:{anime}},location:{origin:'https://aninextup.com'},URL,fetch};vm.createContext(context);vm.runInContext(code,context);return {context,input,box};
}
async function main(){
 const pending=setup(()=>new Promise(()=>{}),[{title:'Berserk of Gluttony Season 2',description:'Official trailer',article:'articles/berserk-of-gluttony-season-2'}]);
 pending.context.searchSite();assert.match(pending.box.innerHTML,/Berserk of Gluttony Season 2/);assert.equal(pending.box.hidden,false);
 const payload=JSON.parse(fs.readFileSync('assets/search-index.json','utf8'));let requests=0;
 const live=setup(async url=>{requests++;assert.equal(url,'/assets/search-index.json');return{ok:true,json:async()=>payload}});
 for(const [query,expected] of [['Kinioto','kinioto-january-2027'],['ShanFro','shangri-la-frontier-season-3-release-date'],['Watashi no Shiawase na Kekkon','my-happy-marriage-special-episodes'],['わたしの幸せな結婚','my-happy-marriage-special-episodes'],['Murciélago','murcielago-anime-january-2027'],['January 2027 anime','anime-releasing-january-2027']]){
  live.input.value=query;await live.context.searchSite();assert(live.box.innerHTML.includes('/articles/'+expected),query+': article missing');
 }
 for(const entry of payload.entries){live.input.value=entry.title;await live.context.searchSite();assert(live.box.innerHTML.includes(entry.url),'full-title search misses '+entry.url);}
 assert.equal(requests,1,'all subsequent queries reuse the generated index');
 live.input.value='!!!';await live.context.searchSite();assert.match(live.box.innerHTML,/No matching articles/);
 live.input.value='nothingmatcheszzzz';await live.context.searchSite();assert.match(live.box.innerHTML,/No matching articles/);
 live.input.value='';await live.context.searchSite();assert.equal(live.box.hidden,true);
 let resolveFirst;
 const delayed=setup(()=>new Promise(resolve=>{resolveFirst=resolve}));delayed.input.value='ShanFro';const first=delayed.context.searchSite();delayed.input.value='Kinioto';const second=delayed.context.searchSite();resolveFirst({ok:true,json:async()=>payload});await Promise.all([first,second]);assert.match(delayed.box.innerHTML,/kinioto-january-2027/);assert.doesNotMatch(delayed.box.innerHTML,/shangri-la-frontier-season-3-release-date/);
 const failure=setup(async()=>{throw Error('offline')},[{title:'Berserk of Gluttony Season 2',article:'articles/berserk-of-gluttony-season-2'}]);await failure.context.searchSite();assert.match(failure.box.innerHTML,/Berserk of Gluttony/,'known results survive a network failure');
 console.log('PASS: immediate results, one index request, romanized/Japanese aliases, accents, empty queries, stale requests and offline results.');
}
main().catch(e=>{console.error(e);process.exitCode=1});
