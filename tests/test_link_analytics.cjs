const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../assets/app.js'),'utf8');
const code=source.slice(source.indexOf('// Classify platform destinations'));
const sent=[];let listener;
class Link{constructor(href){this.href=href;this.innerText='Official source';}closest(){return this;}getAttribute(){return null;}}
const sandbox={URL,Element:Link,location:{origin:'https://aninextup.com',href:'https://aninextup.com/articles/test',pathname:'/articles/test'},window:{gtag:(...args)=>sent.push(args)},document:{addEventListener:(type,fn)=>{if(type==='click')listener=fn;}}};
vm.runInNewContext(code,sandbox);
function click(url){listener({target:new Link(url),button:0});}
click('https://www.crunchyroll.com/es/news/latest/2026/10/21/test');
click('https://www.crunchyroll.com/en-US/news/announcements/test');
click('https://www.crunchyroll.com/series/EXAMPLE');
click('https://about.netflix.com/en/news/test');
click('https://www.netflix.com/tudum/articles/test');
click('https://www.netflix.com/title/81054853');
click('https://www.hidive.com/news/2026/test');
click('https://aninextup.com/news');
click('https://crunchyroll.com.attacker.example/series/test');
assert.deepEqual(sent.map(x=>x[1]),['source_click_crunchyroll','source_click_crunchyroll','streaming_click_crunchyroll','source_click_netflix','source_click_netflix','streaming_click_netflix','source_click_hidive']);
assert.equal(sent[2][2].destination_type,'streaming');
assert.equal(sent[0][2].destination_type,'source');
assert.equal(sent[0][2].page_path,'/articles/test');
console.log('PASS: localized editorial URLs, watch URLs, event delivery and unrelated/spoofed domains.');
