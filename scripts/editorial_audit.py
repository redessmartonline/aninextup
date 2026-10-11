#!/usr/bin/env python3
import json,re,datetime,pathlib,collections,ast
root=pathlib.Path(__file__).resolve().parents[1]
data=(root/'assets/data.js').read_text(encoding='utf8')
rows=[x for x in data.splitlines() if re.search(r'\{id:"',x)]
issues=[];seen=set();found=0
def field(row,k):
 m=re.search(r'\b'+re.escape(k)+r':("(?:\\.|[^"\\])*"|null)',row)
 return (ast.literal_eval(m.group(1)) if m.group(1)!='null' else None) if m else None
def warn(id,code,detail):issues.append(dict(id=id,code=code,detail=detail))
for row in rows:
 e={k:field(row,k) for k in ('id','title','date','dateLabel','platform','article','category','status','image')}
 ident=e['id'] or '(missing id)'
 if ident in seen:warn(ident,'duplicate_id','Repeated ID')
 seen.add(ident)
 if e['status'] not in ('confirmed','month-confirmed','tba'):warn(ident,'invalid_status',str(e['status']))
 if e['status']=='confirmed' and not e['date']:warn(ident,'confirmed_without_date','Exact date missing')
 if e['status']=='month-confirmed' and e['date']:warn(ident,'month_with_exact_date',str(e['date']))
 if e['date']:
  try:datetime.date.fromisoformat(e['date'])
  except (ValueError,TypeError):warn(ident,'invalid_date',str(e['date']))
 for k in ('id','title','platform','article','image'):
  if not e[k]:warn(ident,'missing_field',k)
 if not e['article']:continue
 path=root/(e['article']+'.html')
 if not path.is_file():warn(ident,'missing_article',str(path));continue
 found+=1;html=path.read_text(encoding='utf8')
 for k,pat in [('h1',r'<h1\b'),('description',r'<meta\s+name=["\']description["\']'),('canonical',r'<link\s+rel=["\']canonical["\']')]:
  if not re.search(pat,html,re.I):warn(ident,'missing_'+k,e['article'])
 m=re.search(r'<script\b[^>]*\bid=["\']aninextup-index["\'][^>]*>(.*?)</script>',html,re.I|re.S)
 if not m:continue # Embedded index is optional; validate only when present
 try:embedded=json.loads(m.group(1))
 except json.JSONDecodeError as ex:warn(ident,'invalid_embedded_json',str(ex));continue
 for k in ('id','title','date','dateLabel','platform','category','status','image'):
  if embedded.get(k)!=e[k]:warn(ident,'index_mismatch',k+': central='+repr(e[k])+', article='+repr(embedded.get(k)))
report={'scope':'Structural checks for indexed articles only; no factual verification','entries':len(rows),'articles_found':found,'warning_count':len(issues),'warnings_by_code':dict(collections.Counter(x['code'] for x in issues)),'findings':issues}
out=root/'editorial_report.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
