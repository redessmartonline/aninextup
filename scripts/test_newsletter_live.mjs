// Ephemeral first-party address; this check never sends email and always removes its test record.
import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const origin='https://aninextup.com';const config=JSON.parse(readFileSync('wrangler.jsonc','utf8'));const id=config.d1_databases.find(x=>x.binding==='NEWSLETTER_DB').database_id;
const email='newsletter-check-'+crypto.randomUUID()+'@aninextup.com';
async function sql(query,params=[]){const r=await fetch('https://api.cloudflare.com/client/v4/accounts/'+process.env.CLOUDFLARE_ACCOUNT_ID+'/d1/database/'+id+'/query',{method:'POST',headers:{Authorization:'Bearer '+process.env.CLOUDFLARE_API_TOKEN,'Content-Type':'application/json'},body:JSON.stringify({sql:query,params})});const j=await r.json();assert(r.ok&&j.success,'D1 verification request failed');return j.result[0].results;}
let ready=false;for(let i=0;i<8;i++){const r=await fetch(origin+'/api/newsletter/status',{cache:'no-store'});const j=await r.json();if(j.available&&j.signupMode==='immediate'){ready=true;break;}await new Promise(resolve=>setTimeout(resolve,2000));}assert(ready,'Immediate newsletter mode not ready');
try{
 const register=()=>fetch(origin+'/api/newsletter/subscribe',{method:'POST',headers:{Origin:origin,'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({email,consent:'yes'})});
 let r=await register();assert.equal(r.status,200);assert((await r.json()).ok);let rows=await sql('SELECT state,confirm_hash,unsubscribe_token FROM newsletter_subscribers WHERE email=?',[email]);assert.equal(rows.length,1);assert.equal(rows[0].state,'active');assert.equal(rows[0].confirm_hash,null);
 r=await register();assert.equal(r.status,200);assert.equal((await sql('SELECT state FROM newsletter_subscribers WHERE email=?',[email])).length,1);
 const url=origin+'/api/newsletter/unsubscribe?token='+encodeURIComponent(rows[0].unsubscribe_token);r=await fetch(url);assert.equal(r.status,200);assert.equal((await sql('SELECT state FROM newsletter_subscribers WHERE email=?',[email]))[0].state,'active');
 r=await fetch(url,{method:'POST',body:'List-Unsubscribe=One-Click'});assert.equal(r.status,200);assert.equal((await sql('SELECT state FROM newsletter_subscribers WHERE email=?',[email]))[0].state,'unsubscribed');
 console.log('PASS: live immediate signup persisted as active; no confirmation token; duplicate prevented; GET does not unsubscribe; POST unsubscribe persisted.');
}finally{await sql('DELETE FROM newsletter_subscribers WHERE email=?',[email]);console.log('Ephemeral newsletter test record removed.');}
