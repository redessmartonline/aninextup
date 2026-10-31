(function(root){
 const months=['January','February','March','April','May','June','July','August','September','October','November','December'];
 function monthOf(a){if(/^\d{4}-\d{2}-\d{2}$/.test(a.date||''))return a.date.slice(0,7);const label=a.dateLabel||'';const m=months.findIndex(n=>new RegExp('\\b'+n+'\\b','i').test(label));const y=label.match(/\b20\d{2}\b/);return m>=0&&y?y[0]+'-'+String(m+1).padStart(2,'0'):null;}
 function format(a){const v=(a.category||'').toLowerCase();if(/movie|film|theatr/.test(v))return 'Movies';if(/special|ova|ona/.test(v))return 'Specials';if(/season|cour|return|arc/.test(v)||a.newsCategory==='returning-series')return 'Returning series';return 'New series';}
 function precision(a){return /^\d{4}-\d{2}-\d{2}$/.test(a.date||'')?'Exact date':monthOf(a)?'Month confirmed':/\b(?:winter|spring|summer|fall|autumn)\b/i.test(a.dateLabel||'')?'Season announced':/\b20\d{2}\b/.test(a.dateLabel||'')?'Year announced':'Date TBA';}
 function range(now=new Date()){const y=now.getUTCFullYear(),m=now.getUTCMonth();return Array.from({length:12},(_,i)=>new Date(Date.UTC(y,m+i,1)).toISOString().slice(0,7));}
 function matches(a,f={}){return (!f.query||a.title.toLowerCase().includes(f.query.toLowerCase()))&&(!f.platform||(a.platform||'')===f.platform)&&(!f.format||format(a)===f.format)&&(!f.precision||precision(a)===f.precision);}
 const api={months,monthOf,format,precision,range,matches};root.ANINEXTUP_CALENDAR=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
