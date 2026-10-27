const assert=require('node:assert/strict'),fs=require('node:fs');
const model=require('../assets/release-model.js');
const dates=require('../assets/news-dates.js');
const items=[{article:'old-updated',date:'2030-01-01'},{article:'same-day-first'},{article:'newest'},{article:'same-day-second'}];
const meta={'old-updated':{published:'2026-10-01',updated:'2026-10-30',publishedAt:100},'same-day-first':{published:'2026-10-20',publishedAt:200},'same-day-second':{published:'2026-10-20',publishedAt:201},newest:{published:'2026-10-27',publishedAt:300}};
assert.deepEqual(model.sortNewsByPublication(items,meta).map(x=>x.article),['newest','same-day-second','same-day-first','old-updated']);
assert.deepEqual(items.map(x=>x.article),['old-updated','same-day-first','newest','same-day-second']);
const feed=JSON.parse(fs.readFileSync(require.resolve('../assets/latest-news.json'),'utf8')).items;
assert.deepEqual(feed.map(x=>x.article),model.sortNewsByPublication(feed,dates).map(x=>x.article),'Generated homepage feed must use original publication dates');
const source=fs.readFileSync(require.resolve('../index.html'),'utf8');
assert.match(source,/assets\/news-dates\.js\?v=/,'Homepage must load publication dates before app refresh');
const more=source.split('data-home-more>')[1].split('</section>')[0];
const hrefs=[...more.matchAll(/href="\/(articles\/[^"#]+)"/g)].map(m=>({article:m[1]}));
assert.ok(hrefs.length>20,'Do not truncate the archive');
assert.deepEqual(hrefs.map(x=>x.article),model.sortNewsByPublication(hrefs,dates).map(x=>x.article),'Static More Anime News must remain chronological');
// If the date index cannot load, do not overwrite the chronological fallback
// with the featured archive's HTML order.
const app=fs.readFileSync(require.resolve('../assets/app.js'),'utf8');
const start=app.indexOf('function loadAllHomeMoreNews(){');
const end=app.indexOf("\nif(document.querySelector('.home-page')){",start);
let fetched=false;
const context={document:{querySelector:()=>({})},window:{},fetch:()=>{fetched=true}};
const vm=require('node:vm');vm.createContext(context);
vm.runInContext(app.slice(start,end)+';loadAllHomeMoreNews();',context);
assert.equal(fetched,false,'Missing publication metadata must preserve the static fallback');
console.log('PASS: publication date, same-day time, edits, complete archive, static order and date-index failure fallback.');
