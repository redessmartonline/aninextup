const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

const source=fs.readFileSync('assets/app.js','utf8');
const start=source.indexOf('function normalizeRelatedReleaseGrid(section){');
const end=source.indexOf('\nfunction enforceRelatedReleaseRow()',start);
assert(start>=0&&end>start,'related grid normalizer must be present');

class Card {
  constructor(title){this.title=title;this.parent=null;this.style={values:{},setProperty(name,value,priority=''){this.values[name]={value,priority}}};}
  remove(){if(this.parent)this.parent.removeChild(this);}
}
class Grid {
  constructor(section){this.section=section;this.children=[];this.classList={values:new Set(['grid','two']),toggle:(name,on)=>on?this.classList.values.add(name):this.classList.values.delete(name)};this.style={values:{},setProperty(name,value,priority=''){this.values[name]={value,priority}}};}
  querySelectorAll(selector){return selector===':scope > a.mini'?this.children.filter(x=>x instanceof Card):[];}
  append(card){if(card.parent)card.parent.removeChild(card);this.children.push(card);card.parent=this;}
  removeChild(card){this.children=this.children.filter(x=>x!==card);card.parent=null;}
  remove(){this.section.grids=this.section.grids.filter(x=>x!==this);}
}
class Section {
  constructor(groups){this.grids=groups.map(()=>new Grid(this));groups.forEach((cards,i)=>cards.forEach(title=>this.grids[i].append(new Card(title))));}
  querySelectorAll(selector){return selector==='.grid'?this.grids:[];}
}

const context={};
vm.createContext(context);
vm.runInContext(source.slice(start,end)+';this.normalizeRelatedReleaseGrid=normalizeRelatedReleaseGrid;',context);

const section=new Section([['TANK CHAIR','PSYREN'],['Anime release calendar','Where to watch anime']]);
const grid=context.normalizeRelatedReleaseGrid(section);
assert.equal(section.grids.length,1,'split legacy grids should be merged into one');
assert.deepEqual(grid.children.map(card=>card.title),['TANK CHAIR','PSYREN','Anime release calendar']);
assert.equal(grid.style.values['grid-template-columns'].value,'repeat(3,minmax(0,1fr))');
assert.equal(grid.style.values['grid-template-columns'].priority,'important');
assert.equal(grid.classList.values.has('three'),true);

const twoCardSection=new Section([['First','Second'],['Third']]);
const twoCardGrid=context.normalizeRelatedReleaseGrid(twoCardSection);
assert.deepEqual(twoCardGrid.children.map(card=>card.title),['First','Second','Third']);
assert.equal(twoCardSection.grids.length,1);

console.log('PASS: legacy related cards from multiple grids are merged, ordered, capped at three, and forced into one three-column grid.');
