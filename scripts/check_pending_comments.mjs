import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const config=JSON.parse(readFileSync('wrangler.jsonc','utf8'));
const db=config.d1_databases.find(x=>x.binding==='NEWSLETTER_DB').database_id;
const r=await fetch('https://api.cloudflare.com/client/v4/accounts/'+process.env.CLOUDFLARE_ACCOUNT_ID+'/d1/database/'+db+'/query',{method:'POST',headers:{Authorization:'Bearer '+process.env.CLOUDFLARE_API_TOKEN,'Content-Type':'application/json'},body:JSON.stringify({sql:"SELECT COUNT(*) AS pending_count,COALESCE(MAX(id),0) AS latest_pending_id FROM article_comments WHERE state='pending'"})});
const data=await r.json();assert(r.ok&&data.success,'Pending comment check failed');
const row=data.result[0].results[0];assert(Number.isSafeInteger(row.pending_count)&&Number.isSafeInteger(row.latest_pending_id));
console.log('COMMENT_REVIEW_STATUS '+JSON.stringify(row));
