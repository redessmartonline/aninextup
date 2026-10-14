const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const dataContext={window:{}};
vm.runInNewContext(fs.readFileSync('assets/data.js','utf8'),dataContext);
const entries=[...dataContext.window.ANINEXTUP_DATA.anime,...dataContext.window.ANINEXTUP_DATA.guides];
for(const [parent,destination,cover] of [
  ['naruto-ninku-anime','record-of-a-fallen-vampire-anime','record-of-a-fallen-vampire-teaser.webp'],
  ['kagurabachi-anime-world-tour-finale','nues-exorcist-anime-summer-2027','nues-exorcist-official.png']
]) {
  const html=fs.readFileSync('articles/'+parent+'.html','utf8');
  const section=html.match(/<section class="related-releases"[\s\S]*?<\/section>/)[0];
  assert(section.includes('href="'+destination+'"'));
  assert(section.includes('src="../assets/images/covers/'+cover+'"'));
  assert(!section.includes('this.remove()'));
  assert(html.includes('src="../assets/data.js"'));
  assert(/src="\.\.\/assets\/app\.js(?:\?[^\"]*)?"/.test(html));
  const matches=entries.filter(e=>e.article==='articles/'+destination);
  assert.equal(matches.length,1);
  assert.equal(matches[0].image,'assets/images/covers/'+cover);
  const bytes=fs.readFileSync(matches[0].image);
  assert(bytes.length>2000);
  assert(cover.endsWith('.png')?bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])):bytes.subarray(0,4).toString()==='RIFF'&&bytes.subarray(8,12).toString()==='WEBP');
}
const source=fs.readFileSync('assets/app.js','utf8');
const start=source.indexOf('const cardImageFallback=');
const end=source.indexOf('// Keep cards composed',start);
class Image {
  constructor(){this.dataset={};this.classList={add(){}};this.src='https://external.example/first.jpg';}
  get src(){return this._src;}
  set src(v){this._src=new URL(v,'https://aninextup.com').href;}
}
const context={HTMLImageElement:Image,URL,location:{origin:'https://aninextup.com'}};
vm.createContext(context);
vm.runInContext(source.slice(start,end)+';this.recover=useCardImageFallback;',context);
const image=new Image();
context.recover(image);
assert.equal(image.src,'https://aninextup.com/assets/images/anime-image-fallback.svg');
image.src='https://external.example/second.jpg';
context.recover(image);
assert.equal(image.src,'https://aninextup.com/assets/images/anime-image-fallback.svg');
console.log('PASS: both missing cards use valid local covers, keep their links, load recovery scripts, and recover after repeated external failures.');
