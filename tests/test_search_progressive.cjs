const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

const source=fs.readFileSync('assets/app.js','utf8');
const start=source.indexOf('let siteSearchIndexPromise=null,siteSearchRequest=0;');
const end=source.indexOf("\ndocument.getElementById('search')?.addEventListener",start);
assert(start>=0&&end>start,'search implementation must be present');

const input={value:'Berserk',addEventListener(){}};
const box={hidden:true,innerHTML:''};
const document={
  getElementById(id){return id==='search'?input:id==='searchResults'?box:null;},
  createElement(tag){
    const el={tag,children:[],append(...items){this.children.push(...items);}};
    Object.defineProperty(el,'outerHTML',{get(){return this.tag==='a'
      ?'<a href="'+this.href+'">'+this.children.map(x=>x.textContent).join('')+'</a>'
      :'<'+this.tag+'>'+this.textContent+'</'+this.tag+'>'; }});
    return el;
  },
  addEventListener(){}
};
const context={
  document,
  window:{ANINEXTUP_DATA:{anime:[{
    title:'Berserk of Gluttony Season 2',
    description:'Official Season 2 trailer and streaming details.',
    article:'articles/berserk-of-gluttony-season-2'
  }]}},
  location:{origin:'https://aninextup.com'},
  URL,
  fetch(){return new Promise(()=>{});}
};
vm.createContext(context);
vm.runInContext(source.slice(start,end)+';this.searchSite=searchSite;',context);
context.searchSite();
assert.equal(box.hidden,false,'search results should be visible immediately');
assert.match(box.innerHTML,/Berserk of Gluttony Season 2/,'homepage match should render before full sitemap fetch resolves');
assert.match(box.innerHTML,/articles\/berserk-of-gluttony-season-2/,'immediate result should link to the article');
assert.doesNotMatch(box.innerHTML,/Searching all articles/,'an available match should replace the loading state');
console.log('PASS: homepage search results render while the full sitemap index is still pending.');
