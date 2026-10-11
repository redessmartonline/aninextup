#!/usr/bin/env python3
"""Check external images from assets/data.js with HTTP GET (HEAD often blocked)."""
import json,re,urllib.request,urllib.error,collections,pathlib,time,ast
root=pathlib.Path(__file__).resolve().parents[1]
data=(root/'assets/data.js').read_text(encoding='utf8')
rows=[x for x in data.splitlines() if re.search(r'\{id:"',x)]
results=[]
for row in rows:
 def field(k):
  m=re.search(r'\b'+re.escape(k)+r':("(?:\\.|[^"\\])*"|null)',row)
  return (ast.literal_eval(m.group(1)) if m.group(1)!='null' else None) if m else None
 ident,url=field('id'),field('image')
 item={'id':ident,'url':url,'result':'unverified'}
 if not url:item['result']='invalid_url'
 elif not url.startswith(('https://','http://')):
  local=(root/url.lstrip('/')).resolve()
  if not local.is_relative_to(root):item['result']='invalid_url'
  elif not local.is_file():item['result']='missing_local_file'
  else:
   suffix=local.suffix.lower()
   item['result']='ok_local' if suffix in ('.jpg','.jpeg','.png','.webp','.gif','.avif','.svg') else 'invalid_local_type'
   item['size_bytes']=local.stat().st_size
 else:
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; AniNextUpLinkAudit/1.0)','Accept':'image/avif,image/webp,image/*,*/*;q=0.8','Range':'bytes=0-2047'})
   with urllib.request.urlopen(req,timeout=12) as resp:
    typ=resp.headers.get('Content-Type','').split(';')[0].lower()
    item.update(http_status=resp.status,content_type=typ,result='ok' if typ.startswith('image/') else 'not_image')
  except urllib.error.HTTPError as e:item.update(http_status=e.code,result='http_error')
  except Exception as e:item.update(result='network_error',detail=str(e)[:180])
 results.append(item)
 time.sleep(0.15)
report={'scope':'External images referenced by the central anime index; HTTP checks from GitHub Actions runner','total':len(results),'summary':dict(collections.Counter(x['result'] for x in results)),'images':results}
out=root/'image_url_report.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report['summary'],ensure_ascii=False))
