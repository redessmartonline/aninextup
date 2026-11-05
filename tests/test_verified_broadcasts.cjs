const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const api=require('../assets/verified-broadcasts.js');
const now=new Date('2026-11-05T16:00:00Z');
assert.equal(api.state(now,'UTC').items.length,4);
assert.deepEqual(api.state(now,'UTC').items.map(x=>x.id),['ramparts-20','heavy-knight-19','iceblade-5','fx-kurumi-6-ktv']);
const knight=api.data.episodes.find(x=>x.id==='heavy-knight-19');
assert.equal(api.day(knight.scheduledAt,'UTC'),'2026-11-05');
assert.equal(api.day(knight.scheduledAt,'Asia/Tokyo'),'2026-11-06');
assert.equal(api.time(knight.scheduledAt,'America/New_York'),'10:26 AM');
assert.equal(api.time(knight.scheduledAt,'Europe/London'),'3:26 PM');
assert.equal(api.state(new Date('2026-11-05T12:00:00Z'),'Asia/Tokyo').items.length,1);
assert.equal(api.state(now,'Asia/Tokyo').items.length,3);
for(const later of ['2026-11-07T12:00:00Z','2026-11-12T12:00:00Z']){
 assert.equal(api.state(new Date(later),'UTC').covered,false);
 assert.ok(!api.render(new Date(later),'UTC').includes('class="episode-card"'));
}
const current=api.render(now,'UTC');
assert.equal((current.match(/class="episode-card"/g)||[]).length,4);
for(const e of api.data.episodes){assert.ok(current.includes(e.sourceUrl));assert.ok(e.sourceUrl.startsWith('https://'));}
assert.ok(current.includes('series numbering'));
assert.ok(!current.includes('· Crunchyroll'));
// Exercise the actual browser picker handler with a fixed clock and minimal DOM.
const nodes={};for(const id of ['broadcast-timezone','broadcast-date','today-count','today-platforms'])nodes[id]={value:'UTC',textContent:'',addEventListener(name,fn){this[name]=fn;}};
const list={innerHTML:'',dataset:{}};
class FixedDate extends Date{constructor(...a){super(...(a.length?a:['2026-11-05T16:00:00Z']));}}
const context={window:{},document:{querySelector:selector=>selector==='[data-verified-broadcasts]'?list:{content:''},getElementById:id=>nodes[id],addEventListener(){},hidden:false},Date:FixedDate,Intl,setInterval(){}};
vm.runInNewContext(fs.readFileSync(require.resolve('../assets/verified-broadcasts.js'),'utf8'),context);
assert.equal(nodes['today-count'].textContent,'4');
nodes['broadcast-timezone'].value='Asia/Tokyo';nodes['broadcast-timezone'].change();
assert.equal(nodes['today-count'].textContent,'3');
assert.ok(nodes['broadcast-date'].textContent.includes('November 6, 2026'));
assert.ok(list.innerHTML.includes('12:26 AM'));
console.log('PASS: verified source links, UTC/Japan date rollover, US/UK offsets, expiry, no weekly extrapolation and timezone picker.');
