def write_sheets(out,routes,projects,exhibits):
 for r in routes:
  for edition in ['student','teacher']:
   teacher=edition=='teacher'
   lines=[f"好设计研学｜{r['title']}｜{'教师指导版' if teacher else '学生活动单'}",r['question'],'建议40分钟：导入5分钟、两站各10分钟、对照10分钟、反思5分钟。','教学草案，未试教。目标：解释任务与约束、引用证据、指出证据边界。','']
   if teacher:lines+=['课前准备：预读档案、调整难度、两人一组解释与找证据。','观察标准：区分原文与推测、引用支持结论、能指出证据边界。']
   for stop in r['stops']:
    p=next(p for p in projects if p['id']==stop['id']);ex=exhibits[p['id']];s=ex['external_source']
    lines += ['',p['name'],ex['short'],'阅读资料（历史档案节选，未全部核验）']+[f['quote'] for f in ex['fields']]
    lines += ['任务：'+ex['activity']['prompt']]+[f"{i+1}. {o['label']}" for i,o in enumerate(ex['activity']['options'])]+['我的选择与理由：________________','引用的原文与来源：________________','还需要的证据：________________']
    if teacher:lines+=['讨论提示（教师用）']+[o['feedback'] for o in ex['activity']['options']]+['追问：'+ex['activity']['followup']]
    lines += ['项目：https://gooddesign.qiuyiwu.com'+p['project_url'],'原文：https://gooddesign.qiuyiwu.com'+p['source_url'],'公开来源：'+s['title']+' '+s['url'],s['access'],'支持范围：'+s['supports'],'边界：'+s['boundary']]
   lines+=['','跨作品反思：两件作品的设计要求有哪些相似与不同？引用依据说明。','今天能解释的一件事：________________','仍想追问的一件事：________________']
   if teacher:lines+=['试教反馈：学生卡在哪个环节？实际耗时？是否出现把目标当结果的情况？________________']
   (out/f'worksheet-{r["id"]}-{edition}.txt').write_text('\n'.join(lines))
