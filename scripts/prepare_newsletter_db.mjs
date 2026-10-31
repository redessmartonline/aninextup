import {readFileSync,writeFileSync} from 'node:fs';
const base='https://api.cloudflare.com/client/v4/accounts/'+process.env.CLOUDFLARE_ACCOUNT_ID+'/d1/database';
const headers={Authorization:'Bearer '+process.env.CLOUDFLARE_API_TOKEN,'Content-Type':'application/json'};
async function api(url,options={}){const r=await fetch(url,{...options,headers});const j=await r.json();if(!r.ok||!j.success)throw Error('Newsletter database setup failed: HTTP '+r.status+' '+JSON.stringify(j.errors));return j.result;}
let found=(await api(base+'?name=aninextup-newsletter')).filter(x=>x.name==='aninextup-newsletter');if(found.length>1)throw Error('Ambiguous newsletter database');
const db=found[0]||await api(base,{method:'POST',body:JSON.stringify({name:'aninextup-newsletter'})});
const config=JSON.parse(readFileSync('wrangler.jsonc','utf8'));config.d1_databases=[...(config.d1_databases||[]).filter(x=>x.binding!=='NEWSLETTER_DB'),{binding:'NEWSLETTER_DB',database_name:'aninextup-newsletter',database_id:db.uuid}];writeFileSync('wrangler.jsonc',JSON.stringify(config,null,2)+'\n');
await api(base+'/'+db.uuid+'/query',{method:'POST',body:JSON.stringify({sql:readFileSync('db/newsletter.sql','utf8')+'\n'+readFileSync('db/comments.sql','utf8')})});
console.log('Newsletter database ready:',db.uuid);
