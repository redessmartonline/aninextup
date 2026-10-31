const ORIGIN='https://aninextup.com';
const json=(body,status=200)=>Response.json(body,{status,headers:{'cache-control':'no-store','x-robots-tag':'noindex','x-content-type-options':'nosniff'}});
const hash=async value=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value))),n=>n.toString(16).padStart(2,'0')).join('');

// Conservative local spam rules; retained comments remain available for manual review.
export function needsReview(name,body){
 const text=(name+' '+body).normalize('NFKC').replace(/[\u200b-\u200f\u2060\ufeff]/g,'').toLowerCase();
 return /https?:|www\.|[a-z0-9-]+\.(?:com|net|org|io|xyz|top|ru|click|info|shop)\b|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|<\/?[a-z][^>]*>|\[url\b/i.test(text)
 || /\b(?:buy now|promo code|earn money|make money|free crypto|crypto giveaway|casino bonus|whatsapp me|telegram me|contact me on|comprar ahora|gana dinero|dinero facil)\b/i.test(text)
 || /(.)\1{14,}/u.test(text);
}

async function validArticle(env,slug){
 if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)||slug.length>180)return false;
 const response=await env.ASSETS.fetch(new Request(ORIGIN+'/articles/'+slug));
 if(!response.ok)return false;const html=await response.text();
 return html.includes('href="'+ORIGIN+'/articles/'+slug+'"')&&!/<meta\s+name=["']robots["'][^>]*noindex/i.test(html);
}
export async function comments(request,env){
 try{return await handle(request,env);}catch(error){console.error('Comment request failed',{name:error.name});return json({error:'Comments are temporarily unavailable. Please try again later.'},503);}
}
async function handle(request,env){
 const url=new URL(request.url),db=env.NEWSLETTER_DB;
 if(url.pathname!=='/api/comments')return json({error:'Not found'},404);
 if(!['GET','POST'].includes(request.method))return json({error:'Method not allowed'},405);
 if(!db)return json({error:'Comments are temporarily unavailable.'},503);
 if(request.method==='GET'){
  const slug=url.searchParams.get('article')||'';if(!await validArticle(env,slug))return json({error:'Article not found'},404);
  const before=Number(url.searchParams.get('before')||Number.MAX_SAFE_INTEGER);if(!Number.isSafeInteger(before)||before<1)return json({error:'Invalid page'},400);
  const rows=await db.prepare("SELECT id,display_name,body,parent_id,created_at FROM article_comments WHERE article=? AND state='approved' AND id<? ORDER BY id DESC LIMIT 21").bind(slug,before).all();
  const count=await db.prepare("SELECT COUNT(*) AS total FROM article_comments WHERE article=? AND state='approved'").bind(slug).first();
  const items=rows.results.slice(0,20);return json({items,total:count.total,nextBefore:rows.results.length>20?items.at(-1).id:null});
 }
 if(![ORIGIN,'https://www.aninextup.com'].includes(request.headers.get('origin')))return json({error:'Invalid origin'},403);
 if(!request.headers.get('content-type')?.startsWith('application/json'))return json({error:'JSON required'},415);
 if(Number(request.headers.get('content-length')||0)>10000)return json({error:'Comment too large'},413);
 const reader=request.body?.getReader();if(!reader)return json({error:'Invalid submission'},400);let size=0,chunks=[];
 while(true){const part=await reader.read();if(part.done)break;size+=part.value.length;if(size>10000){await reader.cancel();return json({error:'Comment too large'},413);}chunks.push(part.value);}
 let form;try{const bytes=new Uint8Array(size);let offset=0;for(const c of chunks){bytes.set(c,offset);offset+=c.length;}form=JSON.parse(new TextDecoder().decode(bytes));}catch{return json({error:'Invalid submission'},400);}
 if(!form||typeof form!=='object')return json({error:'Invalid submission'},400);
 if(form.website)return json({ok:true,message:'Comment submitted for review.'},202);
 const slug=typeof form.article==='string'?form.article:'',name=typeof form.name==='string'?form.name.trim():'',body=typeof form.body==='string'?form.body.trim():'';
 if(name.length<2||name.length>60||body.length<3||body.length>2000||/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(name+body))return json({error:'Use a name of 2–60 characters and a comment of 3–2,000 characters.'},400);
 if(!await validArticle(env,slug))return json({error:'Article not found'},404);
 const parent=form.parentId??null;
 if(parent!==null){if(!Number.isSafeInteger(parent)||parent<1)return json({error:'Invalid reply'},400);const found=await db.prepare("SELECT id FROM article_comments WHERE id=? AND article=? AND state='approved'").bind(parent,slug).first();if(!found)return json({error:'The comment you are replying to is unavailable.'},400);}
 const now=Date.now(),hour=Math.floor(now/3600000),ip=request.headers.get('cf-connecting-ip');if(!ip)return json({error:'Please try again later.'},503);
 await db.prepare('DELETE FROM comment_limits WHERE period<=?').bind(hour-24).run();
 for(const [key,limit] of [['ip:'+ip,3],['global',100]]){const row=await db.prepare('INSERT INTO comment_limits(key,period,count) VALUES(?,?,1) ON CONFLICT(key,period) DO UPDATE SET count=count+1 RETURNING count').bind(await hash(hour+':'+key),hour).first();if(row.count>limit)return json({error:'Too many comments. Please try again later.'},429);}
 const fingerprint=await hash(slug+'\n'+name+'\n'+body+'\n'+parent);
 const state=needsReview(name,body)?'pending':'approved';
 await db.prepare("INSERT OR IGNORE INTO article_comments(article,display_name,body,parent_id,state,created_at,fingerprint) VALUES(?,?,?,?,?,?,?)").bind(slug,name,body,parent,state,new Date(now).toISOString(),fingerprint).run();
 return json({ok:true,state,message:state==='approved'?'Thanks! Your comment is now published.':'Thanks! Your comment is awaiting review.'},202);
}
