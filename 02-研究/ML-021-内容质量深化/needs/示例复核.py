# -*- coding: utf-8 -*-
from pathlib import Path
import json,math,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2]
rows=[]
def record(method,calculation,input,output,scope):rows.append({'method':method,'calculation':calculation,'input':input,'actual_output':output,'scope':scope})
def area(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
a=[area(v,[40,0,60,80])for v in [[0,20,30,60],[20,30,80,50],[-35,30,-5,50]]];assert a==[0,400,0];record('R01','rectangle intersection',{'unit':'mm','scope':'constructed rectangles'},a,'teaching geometry not collision/engineering validation')
assert 40+60==100;record('R02','phase arithmetic',[40,60],{'total':100,'recovery_share':.6},'synthetic ticks not real seconds')
record('R05','coordinate and age arithmetic',{'mechanical':2,'software_command':-1,'times':[80,100],'teaching_limit_ms':30},{'software':-2,'mechanical_command':1,'age':20,'at_limit_stale':110-80>=30},'fixed arithmetic only')
P=R/'02-研究/方法深化执行/MD-012-R11/教学包';inp=json.loads((P/'02-全回答对夹具.json').read_text());out=json.loads((P/'03-完整分类输出.json').read_text());table={z['id']:z['category']for z in out['mappings']};chosen=[(z['functional'],z['dysfunctional'],table[z['id']])for z in inp['pairs']if(z['functional'],z['dysfunctional'])in[('like','neutral'),('like','dislike'),('must_be','dislike')]];assert chosen==[('like','neutral','A'),('like','dislike','O'),('must_be','dislike','M')];record('R11','source-table mapping cross-check','existing table2 JSON',chosen,'three constructed answer pairs not participants')
M=[[1,1.8,1.25],[1/1.8,1,1/1.8],[.8,1.8,1]];ss=[sum(r[j]for r in M)for j in range(3)];weights=[sum(r[j]/ss[j]for j in range(3))/3 for r in M];assert max(abs(v-w)for v,w in zip(weights,[.4204590680561083,.21708672097726592,.36245421096662583]))<1e-12;record('R12','column normalization row means',M,weights,'public display-value slice not survey replication')
record('R13','representation distinction',{'A':['green','green'],'B':['current','stale']},{'A_collision':True,'B_collision':False},'encoding only not human comprehension')
pairmax=max(a+b for a in[5,20]for b in[0,25]);assert pairmax<=50 and 20+25+20==65;record('R17','higher-order constraint',[20,25,20],{'total':65,'limit':50,'exceeded':True},'synthetic watt values not device ratings')
remaining=500-sum([120,80,100]);assert remaining==200;record('R48','new illustrative TBR budget',{'total_ms':500,'other_serial_segments_ms':[120,80,100]},remaining,'all authored coordination estimate not measured or approved timing')
(D/'示例复核记录.json').write_text(json.dumps({'date':'2026-10-28','actual_activity':'local arithmetic/source-table crosschecks','field_or_user_experiments':0,'records':rows},ensure_ascii=False,indent=2));print('verified calculations',len(rows))
