(function(root){
  const iso=d=>d.toISOString().slice(0,10);
  function context(now=new Date(),timezone='America/Santo_Domingo'){
    const parts=new Intl.DateTimeFormat('en-US',{timeZone:timezone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
    const value=k=>parts.find(p=>p.type===k).value;
    const today=value('year')+'-'+value('month')+'-'+value('day');
    const start=new Date(today+'T12:00:00Z');
    start.setUTCDate(start.getUTCDate()-(start.getUTCDay()+6)%7);
    const end=new Date(start);end.setUTCDate(start.getUTCDate()+6);
    return {today,weekStart:iso(start),weekEnd:iso(end)};
  }
  const matchesPlatform=(item,platform)=>new RegExp('^'+platform.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'(?:$|[ /\\(])','i').test(item.platform||'');
  function select(items,mode,ctx){
    return items.filter(a=>{
      if(mode==='today')return a.date===ctx.today;
      if(mode==='week')return a.date&&a.date>=ctx.weekStart&&a.date<=ctx.weekEnd;
      if(mode==='upcoming-week')return a.date&&a.date>=ctx.today&&a.date<=ctx.weekEnd;
      if(mode==='after-week')return a.date&&a.date>ctx.weekEnd;
      if(mode==='next')return a.date&&a.date>ctx.today;
      if(mode==='upcoming')return a.date&&a.date>=ctx.today;
      if(mode==='calendar')return !!a.date;
      return true;
    }).sort((a,b)=>(a.date||'9999').localeCompare(b.date||'9999'));
  }
  root.ANINEXTUP_RELEASES={context,matchesPlatform,select};
  if(typeof module!=='undefined')module.exports=root.ANINEXTUP_RELEASES;
})(typeof window!=='undefined'?window:globalThis);
