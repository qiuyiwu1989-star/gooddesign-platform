from pathlib import Path
import csv,json,hashlib
ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent
if (BASE/'任务台账.json').exists():
 existing=json.loads((BASE/'任务台账.json').read_text())
 if any(t['status']not in ('planned','ready_to_start')for t in existing['tasks']):
  raise SystemExit('已有执行进度，禁止初始化脚本覆盖；请显式更新任务状态。')
research=ROOT/'02-研究/ML-017-方法深化第二轮'
rows={x['id']:x for x in csv.DictReader((research/'逐法研究判断.tsv').open(),delimiter='\t')}
names={x['research_id']:x['name']for x in json.loads((research/'研究清单.json').read_text())['methods_index']}
batches=[('关键链贯通',['R48','R08','R14','R17','R36','R44','R42']),('需求与功能补全',['R02','R03','R09','R10','R11','R12','R13','R15','R16']),('创新原理生成',['R19','R20','R21','R22','R23','R24','R25','R26','R27','R28','R29','R18','R49']),('工程架构与实现',['R30','R31','R32','R33','R34','R35','R05','R47']),('权衡风险与验证',['R37','R38','R39','R40','R41','R43','R45','R46','R50','R51','R52','R07']),('全流程编排',['R01','R04','R06']),('闻邦椿体系专项',[f'WB{i:02d}'for i in range(1,13)])]
assert len([i for _,ids in batches for i in ids])==64
assert {i for _,ids in batches for i in ids}==set(rows)
anchors={'R48':[],'R08':['R48'],'R14':['R48','R08'],'R17':['R14'],'R36':['R17'],'R44':['R36'],'R42':['R48','R44']}
teaching={'R01','R02','R03','R04','R14','R17','R36','R42','R44','R48'}
existing_math={'R33','R38'}
ledger=[];lines=[]
for batch,(label,ids) in enumerate(batches,1):
 lines.append(f'\n## 第{batch}批 · {label}（{len(ids)}项）\n\n|顺序|任务|本项交付重点|状态|\n|---|---|---|---|')
 for rid in ids:
  n=len(ledger)+1;tid=f'MD-{n:03d}';d=rows[rid];fn=f'{tid}-{rid}.md';status='待启动（首项）' if n==1 else '待启动';deps=anchors.get(rid,[])
  base_note='已有固定教学包，先核现有版本和审核边界，补缺与迁移，不重建已完成内容。'if rid in teaching else ('已有ML-017数学复算，先复核其输入、模型及适用范围，不能转称工程验证。'if rid in existing_math else '承接ML-017研究稿，补成完整教学产物；研究稿存在不等于本任务完成。')
  text=f'''# {tid} · {rid} {names[rid]}

- 排期：第{n}/64项；第{batch}批「{label}」。
- 状态：{status}。本卡仅为已安排任务，尚未分配给外部人员或独立审核者。
- 主责：当前好设计方法库Agent；执行由本会话逐项推进。
- 复核：另行安排具备相应方法背景的独立复核者；未安排前不写已审核。
- 上游材料：{('、'.join(deps)+'的相应产物；若缺失需先补或保留待确认。') if deps else '本项研究稿、所选版本原典和目标任务；不把排期前项当强制算法依赖。'}
- 启动底稿：[ML-017逐法研究](../../../02-研究/ML-017-方法深化第二轮/逐法档案/{rid}.md)。

## 本项研究目标

{d['focus']}

优先解决的判断：{d['decision']}

## 已有基础

{base_note}

## 执行清单

- [ ] 01 原典补证：锁定版本、核对来源身份与可读范围；将支持关键规则的原文定位和未决资料分开保存。
- [ ] 02 机制拆解：解释输入如何变化为输出，写清本项关键判断与返回/停止条件，不把方法族或体系专题强写成求解器。
- [ ] 03 完整示范：{d['artifact']}
- [ ] 04 反例检查：至少覆盖正常、缺材料、不适用、边界和冲突五类；区分实际执行结果与未执行的测试设计。
- [ ] 05 迁移交接：{d['handoff']}
- [ ] 06 独立复核：核原文支持范围、计算/规则、推演和反例结论；保留分歧、修订记录与仍未覆盖的专业事项。
- [ ] 07 入库验收：分别检查正文、结构图、教学附件与调用说明是否一致；只有真实已实现并验证的接口才称可执行。通过后版本化发布。

## 必须检查的具体反例

{d['negative_case']}

## 固定交付结构

后续成果保存到同一外置盘项目下`02-研究/方法深化执行/{tid}-{rid}/`，本次不预建空成果冒充完成：

1. `研究说明.md`：版本、原理、适用/禁用、关键判断、与邻近方法区别。
2. `来源与主张.json`：来源身份、定位、支持主张、核读范围及缺口。
3. `教学包/`：输入、中间产物、输出及运行/手工操作记录；构造与真实材料分开。
4. `反例与迁移.md`：五类检查、其他情境的适用性、尚需验证的差异。
5. `调用说明.json`：触发条件、输入输出、依赖、未知处理和交接；注明建议契约或实际接口。
6. `审核与版本.json`：复核者身份/角色、意见、修订、产物指纹、发布范围和日期。

## 完成条件

- 原典规则和平台适配分开；缺原典时可完成受限研究，但不能标完整原法复刻。
- 他人可据材料跟随操作；数值方法能复算，研究框架有可回查的判断与产物。
- 重要未知不被填成默认通过；上述具体反例得到明确处置并保留证据。
- 至少一个不同情境的迁移检查；仅做桌面推演时如实标注，不能冒称现场验证。
- 技术检查、专业复核、客户确认和工程验证分别记录；没有独立复核不标最终审核完成。

## 受阻时的处理

将缺失原典、客户材料或专业复核列为独立缺口。能做的原创解释、教学及取证继续推进；不能取得的证据不编造。主攻顺序可让后续可做任务前移，原任务保留状态与下一动作。
'''
  (BASE/'任务卡'/fn).write_text(text)
  entry={'task_id':tid,'sequence':n,'method_id':rid,'name':names[rid],'batch':batch,'batch_name':label,'status':'ready_to_start'if n==1 else'planned','owner':'current_method_library_agent','independent_reviewer':None,'source_material_dependencies':deps,'planned_task_card':'任务卡/'+fn,'target_artifact':d['artifact'],'progress':{'source_review':False,'mechanism':False,'worked_example':False,'negative_cases':False,'transfer':False,'independent_review':False,'published':False}}
  ledger.append(entry);lines.append(f"|{n:02d}|[{tid} · {rid} {names[rid]}](任务卡/{fn})|{d['artifact']}|{status}|")
summary='''# 64项方法深化任务总表 · ML-018

2026-10-27。用户要求将逐法深化计划逐项安排。本表落实排期及验收，不代表任务已经被外部人员接单或已完成研究。

## 执行规则

- 当前Agent主责，按顺序一次主攻一项；各项取证、教学、反例、迁移、审核与发布分开勾选。
- 首项MD-001/R48可启动；其余为待启动。没有可靠输入不算完成，没有独立复核不标最终审核通过。
- 排期顺序不是方法因果或固定调用顺序。R48初稿之后R08补证，再返回修订R48，允许迭代；后续方法是否调用由问题与材料决定。
- 第3、5、7项后分别检查需求→功能、功能→候选→筛选、假设→验证三段交接；其余各批每完成3—5项检查一次组合。检查只是证据和字段衔接，不强行串联所有方法。
- 受阻项保留缺口并前移可做任务，不为了顺序耗尽等待；闻邦椿专著取得单独排队，不用一般设计知识冒充作者原法。
- 割胶机器人作为贯穿研究题，另加不同领域情境做迁移检查。构造教学、文献研究、现场调查和工程试验分别标识。
- 每项完成后交付可读说明、来源定位、教学产物、反例、调用说明及审核版本；若要公开，先确认取证权利与现有发布流程。
- 不安排未经依据的日历截止或承诺固定完成时长：原典、现场输入和复核资源尚未全到位。以产物和验收推进，每批回报实际进度。

## 验收状态

`待启动 → 原典与机制研究 → 教学与反例 → 迁移检查 → 待独立复核 → 通过后发布`。

受限研究可以单独交付并保留缺口；不能因此勾选最终完整入库。已有ML-017分析和055教学包不自动勾成本轮完成，也不重新覆盖已有审核记录。
'''
(BASE/'任务总表.md').write_text(summary+'\n'.join(lines)+'\n')
(BASE/'任务台账.json').write_text(json.dumps({'created_date':'2026-10-27','scope':'planned_64_deepening_tasks_not_dispatched_or_completed_research','primary_owner':'current_method_library_agent','active_task':None,'next_task':'MD-001','tasks':ledger},ensure_ascii=False,indent=2))
files=[p for p in BASE.rglob('*')if p.is_file()and p.name!='manifest.json']
(BASE/'manifest.json').write_text(json.dumps({'tasks':64,'files':[{'path':str(p.relative_to(BASE)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(files)]},ensure_ascii=False,indent=2))
print('Created 64 individual task cards, seven batches and explicit acceptance ledger.')
