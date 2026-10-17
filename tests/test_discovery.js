const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const path=require('node:path');process.chdir(path.join(__dirname,'..'));
const model=require('../assets/release-model.js');
const box={window:{}};vm.runInNewContext(fs.readFileSync('assets/data.js','utf8'),box);
const data=box.window.ANINEXTUP_DATA;
// Sunday midnight in UTC is still Saturday in the site's timezone.
assert.equal(model.context(new Date('2026-10-19T02:00:00Z')).weekEnd,'2026-10-18');
assert.equal(model.context(new Date('2026-10-19T05:00:00Z')).weekEnd,'2026-10-25');
const ctx=model.context(new Date('2026-10-12T21:00:00Z'));
const weekly=model.select(data.anime,'upcoming-week',ctx);
const upcoming=model.select(data.anime,'after-week',ctx);
assert(weekly.length);assert(upcoming.length);
assert(!weekly.some(a=>upcoming.some(b=>a.id===b.id)));
assert.equal(upcoming[0].date,'2026-10-20');
assert(model.matchesPlatform({platform:'Disney+ / Hulu (U.S.)'},'Disney+'));
assert(model.matchesPlatform({platform:'Netflix (U.S.)'},'Netflix'));
assert(model.matchesPlatform({platform:'Crunchyroll (supported territories)'},'Crunchyroll'));
assert(!model.matchesPlatform({platform:'NetflixOther'},'Netflix'));
for(const name of ['calendar.html','where-to-watch.html','today.html','this-week.html']){
  const html=fs.readFileSync(name,'utf8');
  assert(html.includes('data-card'),`${name}: no prerendered cards`);
  assert(html.includes('assets/release-model.js'),`${name}: missing shared date rules`);
}
for(const name of fs.readdirSync('articles').filter(n=>n.endsWith('.html'))){
  const html=fs.readFileSync('articles/'+name,'utf8');
  assert.equal((html.match(/class="related-releases"/g)||[]).length,1,`${name}: related releases count`);
  const curated = ['one-piece-elbaph-arc-english-dub-october-2026.html','reincarnated-as-a-sword-season-2-english-dub-release-date.html'].includes(name);
  if(curated){
    assert(html.includes('MORE ANIME NEWS')&&html.includes('Related stories'),`${name}: missing curated related heading`);
    assert.equal((html.match(/class="mini related-card"/g)||[]).length,3,`${name}: expected three curated story cards`);
    assert(!html.includes('KEEP WATCHING'),`${name}: legacy related kicker remains`);
  }else{
    assert(html.includes('KEEP WATCHING')&&html.includes('Related releases'),`${name}: missing related headings`);
  }
  assert(html.includes('class="editorial-details"'),`${name}: missing editorial details`);
  const sections=html.match(/<section class="related-releases"[\s\S]*?<\/section>/g)||[];
  for(const section of sections)for(const link of section.matchAll(/href="([^"]+)"/g)){
    if(/^https?:/.test(link[1]))continue;
    const target=path.resolve('articles',link[1].split('#')[0]);
    assert(fs.existsSync(target)||fs.existsSync(target+'.html'),`${name}: broken related link ${link[1]}`);
  }
}
console.log('PASS: date boundaries, non-overlapping sections, regional platforms, crawlable hubs and article navigation.');
