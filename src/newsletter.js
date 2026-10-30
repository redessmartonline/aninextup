const ORIGIN='https://aninextup.com';
const headers={'cache-control':'no-store','x-robots-tag':'noindex, nofollow','referrer-policy':'no-referrer'};
const json=(data,status=200)=>Response.json(data,{status,headers});
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const hash=async s=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s))),v=>v.toString(16).padStart(2,'0')).join('');
const token=()=>crypto.randomUUID()+crypto.randomUUID();
const day=ms=>new Intl.DateTimeFormat('en-CA',{timeZone:'America/Santo_Domingo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(ms));
const page=(title,body,status=200)=>new Response(`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} | AniNextUp</title><style>body{margin:0;background:#080b19;color:#f8fafc;font:16px/1.7 system-ui}main{max-width:560px;margin:12vh auto;padding:28px}a{color:#c4b5fd}button{background:#8b5cf6;color:white;border:0;border-radius:8px;padding:14px 24px;font-weight:700;cursor:pointer}h1{line-height:1.2}</style><main><a href="/">ANINEXTUP</a><h1>${esc(title)}</h1>${body}</main></html>`,{status,headers:{...headers,'content-type':'text/html;charset=utf-8','content-security-policy':"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"}});
async function send(env,to,subject,html,key,unsubscribe){
 const response=await fetch('https://api.resend.com/emails',{method:'POST',headers:{Authorization:'Bearer '+env.RESEND_API_KEY,'Content-Type':'application/json','Idempotency-Key':key},body:JSON.stringify({from:env.CONTACT_FROM_EMAIL,to:[to],subject,html,...(unsubscribe?{headers:{'List-Unsubscribe':`<${unsubscribe}>`,'List-Unsubscribe-Post':'List-Unsubscribe=One-Click'}}:{})})});
 if(!response.ok){console.error('Newsletter delivery rejected',{status:response.status});throw Error('Email delivery unavailable');}return response.json();
}
async function limited(db,key,max){const hour=Math.floor(Date.now()/3600000);const row=await db.prepare('INSERT INTO newsletter_limits (key,period,count) VALUES(?,?,1) ON CONFLICT(key,period) DO UPDATE SET count=count+1 RETURNING count').bind(await hash(key),hour).first();return row.count>max;}
export async function newsletter(request,env){
 const u=new URL(request.url),db=env.NEWSLETTER_DB;
 if(u.pathname==='/api/newsletter/status')return json({available:!!(db&&env.RESEND_API_KEY&&env.CONTACT_FROM_EMAIL),configured:{storage:!!db,delivery:!!env.RESEND_API_KEY,sender:!!env.CONTACT_FROM_EMAIL}});
 if(!db||!env.RESEND_API_KEY||!env.CONTACT_FROM_EMAIL)return json({error:'Subscriptions are temporarily unavailable. Please try again later.'},503);
 if(!['GET','POST'].includes(request.method))return json({error:'Method not allowed'},405);
 if(request.method==='POST'&&request.headers.get('origin')&&request.headers.get('origin')!==ORIGIN&&request.headers.get('origin')!==u.origin)return json({error:'Invalid origin'},403);
 if(u.pathname==='/api/newsletter/subscribe'){
  if(request.method!=='POST')return json({error:'Method not allowed'},405);
  if(Number(request.headers.get('content-length')||0)>2048)return json({error:'Submission too large'},413);
  let form;try{const text=await request.text();if(text.length>2048)return json({error:'Submission too large'},413);form=new URLSearchParams(text);}catch{return json({error:'Invalid form'},400);}
  if(form.get('website'))return json({ok:true,message:'Subscription received.'});
  const email=String(form.get('email')||'').trim().toLowerCase();
  if(email.length>254||!/^\S+@[^\s@]+\.[^\s@]+$/.test(email)||form.get('consent')!=='yes')return json({error:'Enter a valid email and agree to receive the newsletter.'},400);
  if(await limited(db,'ip:'+request.headers.get('cf-connecting-ip'),5)||await limited(db,'email:'+email,2)||await limited(db,'global-subscriptions',80))return json({error:'Too many attempts. Please try again later.'},429);
  const now=Date.now();
  await db.prepare(`INSERT INTO newsletter_subscribers(email,state,confirm_hash,confirm_expires,unsubscribe_token,created_at,confirmed_at,cursor) VALUES(?,'active',NULL,NULL,?,?,?,?) ON CONFLICT(email) DO UPDATE SET state='active',confirm_hash=NULL,confirm_expires=NULL,confirmed_at=CASE WHEN newsletter_subscribers.state='active' THEN newsletter_subscribers.confirmed_at ELSE excluded.confirmed_at END,cursor=CASE WHEN newsletter_subscribers.state='active' THEN newsletter_subscribers.cursor ELSE excluded.cursor END`).bind(email,token(),now,now,day(now-86400000)).run();
  return json({ok:true,message:'You’re subscribed! You’ll receive our daily digest when new articles or updates are published. Unsubscribe anytime.'});
 }
 if(u.pathname==='/api/newsletter/confirm')return page('No confirmation required','<p>Subscriptions now start immediately when you submit your email on the <a href="/">homepage</a>. If you subscribed using the older form, submit your email again to activate it.</p>');
 if(u.pathname==='/api/newsletter/unsubscribe'){
  const raw=u.searchParams.get('token')||'';if(raw.length!==72)return page('Invalid unsubscribe link','<p>Use the link in your AniNextUp email.</p>',400);
  const row=await db.prepare('SELECT state FROM newsletter_subscribers WHERE unsubscribe_token=?').bind(raw).first();if(!row)return page('Link unavailable','<p>This subscription link is no longer valid.</p>',400);
  if(request.method==='GET')return page('Unsubscribe from AniNextUp','<p>Stop receiving the AniNextUp newsletter.</p><form method="POST"><button>Unsubscribe</button></form>');
  await db.prepare("UPDATE newsletter_subscribers SET state='unsubscribed',confirm_hash=NULL,confirm_expires=NULL WHERE unsubscribe_token=?").bind(raw).run();return page('You’re unsubscribed','<p>You will no longer receive the AniNextUp newsletter.</p><a href="/">Back to AniNextUp</a>');
 }
 return json({error:'Not found'},404);
}
export async function digest(env){
 if(!env.NEWSLETTER_DB||!env.RESEND_API_KEY||!env.CONTACT_FROM_EMAIL)return;
 const db=env.NEWSLETTER_DB,now=Date.now(),cutoff=day(now-86400000);
 const response=await env.ASSETS.fetch(new Request(ORIGIN+'/assets/latest-news.json'));if(!response.ok)throw Error('News feed unavailable');
 const feed=await response.json();if(!Array.isArray(feed.items))throw Error('Invalid news feed');
 const rows=await db.prepare("SELECT email,cursor,unsubscribe_token FROM newsletter_subscribers WHERE state='active' AND cursor<? LIMIT 80").bind(cutoff).all();
 for(const subscriber of rows.results){
  const items=feed.items.filter(i=>/^articles\/[a-z0-9-]+$/.test(i.article)&&/^\d{4}-\d{2}-\d{2}$/.test(i.published)&&(i.updated||i.published)>subscriber.cursor&&(i.updated||i.published)<=cutoff);
  if(items.length){
   const unsub=ORIGIN+'/api/newsletter/unsubscribe?token='+subscriber.unsubscribe_token;
   const html='<h1>Your AniNextUp update</h1>'+items.map(i=>`<h2><a href="${ORIGIN+'/'+i.article}">${esc(i.title)}</a></h2><p>${esc(i.description||'')}</p>`).join('')+`<hr><p>You subscribed to the AniNextUp newsletter.</p><p><a href="${unsub}">Unsubscribe</a> · <a href="${ORIGIN}/privacy">Privacy</a> · <a href="${ORIGIN}/contact">Contact AniNextUp</a></p>`;
   try{await send(env,subscriber.email,'Your AniNextUp anime news digest',html,'newsletter-digest/'+await hash(subscriber.email+':'+subscriber.cursor+':'+cutoff),unsub);}catch{continue;}
  }
  await db.prepare("UPDATE newsletter_subscribers SET cursor=? WHERE email=? AND state='active'").bind(cutoff,subscriber.email).run();
 }
 await db.prepare('DELETE FROM newsletter_limits WHERE period<?').bind(Math.floor(now/3600000)-48).run();
 await db.prepare("DELETE FROM newsletter_subscribers WHERE state='pending' AND confirm_expires<?").bind(now-7*86400000).run();
}
