"""079 evidence-reviewed HH6000 dossier. Quotes are verbatim from frozen source chunks."""
import json
from pathlib import Path
import project_pipeline as pp
import research_workflow as rw

PID = '2019-s19'
ACTOR = '主Agent证据核读'
OUT = pp.ROOT / 'output/research-079/2019-s19'
OUT.mkdir(parents=True, exist_ok=True)
ARCHIVE = 'Se3e240239a2f0916'
PAPER = 'S7e3f4f2b06f63fe8'
MOST = 'S958291324dfd4332'
MEDIA = 'S8ae50c84687b0709'
KCZG = 'S5ca519ed10721899'
COMPANY = 'S349e0fec3fb0debf'
created = []


def add(source, chunk, entity, field, record_id, title, value, quote=None, **extra):
    quote = value if quote is None else quote
    args = dict(entity=entity, field=field, record_id=record_id, title=title, value=value,
                source_id=source, chunk_id=chunk, quote=quote,
                object=extra.pop('object', ''), unit=extra.pop('unit', ''),
                conditions=extra.pop('conditions', ''), limitations=extra.pop('limitations', ''),
                content_nature=extra.pop('content_nature', 'source_statement'), **extra)
    try:
        candidate = rw.propose(pp.LIB, PID, args, ACTOR)
    except ValueError as exc:
        raise ValueError(f'{record_id}.{field}: {exc}') from exc
    if candidate['status'] == 'pending':
        candidate = rw.review(pp.LIB, PID, candidate['id'], 'approved', ACTOR,
                              '已逐字核对指定来源块、项目对象、数值单位与适用边界', reviewer_kind='agent')
    created.append(candidate['id'])
    return candidate['id']


add(ARCHIVE, 'B0001', 'project', 'canonical_name', 'PROJ-001', '6000HP电动压裂泵', '6000HP电动压裂泵', '6000HP电动压裂泵')
add(PAPER, 'B0001', 'project', 'project_type', 'PROJ-001', '6000HP电动压裂泵', '泵组', 'HH6000大功率电动压裂泵组')
add(PAPER, 'B0001', 'project', 'industry', 'PROJ-001', '6000HP电动压裂泵', ['石油钻采装备'], '石油钻采装备')
add(ARCHIVE, 'B0001', 'project', 'summary', 'PROJ-001', '6000HP电动压裂泵', '2011年以来，在国家能源局支持下，四川宏华研发了6000HP超大功率电动压裂泵，解决了非常规油气大规模成片开发的高效、经济和环保问题。', '2011年以来，在国家能源局支持下，四川宏华研发了6000HP超大功率电动压裂泵，解决了非常规油气大规模成片开发的高效、经济和环保问题。')
add(MOST, 'B0001', 'project', 'current_stage', 'PROJ-001', '6000HP电动压裂泵', '实现了产业化', '目前，6000HP页岩气压裂装备已实现了产业化')
add(MOST, 'B0001', 'project', 'status_as_of', 'PROJ-001', '6000HP电动压裂泵', '2021-06-30', '2021年06月30日 15:32')
add(ARCHIVE, 'B0001', 'organization', 'name_original', 'ORG-001', '四川宏华石油设备有限公司', '四川宏华石油设备有限公司', '"unit": "四川宏华石油设备有限公司"')
add(ARCHIVE, 'B0001', 'organization', 'name_canonical', 'ORG-001', '四川宏华石油设备有限公司', '四川宏华石油设备有限公司', '"unit": "四川宏华石油设备有限公司"')
add(PAPER, 'B0001', 'organization', 'project_role', 'ORG-001', '四川宏华石油设备有限公司', '研发设计工作', '现从事石油钻采装备的研发设计工作')
add(ARCHIVE, 'B0001', 'award', 'year', 'AWARD-001', '2019好设计银奖', 2019, '"year": 2019')
add(ARCHIVE, 'B0001', 'award', 'level', 'AWARD-001', '2019好设计银奖', '银奖', '"level": "银奖"')
add(ARCHIVE, 'B0001', 'problem', 'title', 'PROB-001', '超大功率电动压裂装备', '6000HP超大功率电动压裂泵', '6000HP超大功率电动压裂泵')
add(ARCHIVE, 'B0001', 'problem', 'scenario', 'PROB-001', '超大功率电动压裂装备', '非常规油气大规模成片开发', '非常规油气大规模成片开发')
add(ARCHIVE, 'B0001', 'problem', 'original_solution', 'PROB-001', '超大功率电动压裂装备', '柴油机通过液力变矩器或变速箱驱动压裂泵的传统机械方式', '目前的压裂车都采用柴油机通过液力变矩器或变速箱驱动压裂泵的传统机械方式')
add(ARCHIVE, 'B0001', 'problem', 'pain_point', 'PROB-001', '超大功率电动压裂装备', '单机功率小、占地面积大、购置维护费用高、污染大、噪音高、结构复杂、传动效率低、不能实现自动化精准控制', '单机功率小、占地面积大、购置维护费用高、污染大、噪音高、结构复杂、传动效率低、不能实现自动化精准控制')
add(ARCHIVE, 'B0001', 'problem', 'goal', 'PROB-001', '超大功率电动压裂装备', '高效、经济和环保', '解决了非常规油气大规模成片开发的高效、经济和环保问题。', content_nature='ai_interpretation', conditions='依据历史申报中对既有问题的描述与项目主张', limitations='目标方向由平台归纳，未取得项目方原始设计任务书或验收判据')
add(ARCHIVE, 'B0001', 'problem', 'constraints', 'PROB-001', '超大功率电动压裂装备', ['在有限尺寸内大幅提高单机功率'], '在有限尺寸内大幅提高单机功率')
add(ARCHIVE, 'B0001', 'problem', 'success_criteria', 'PROB-001', '超大功率电动压裂装备', '满足在超大功率下的连续运转要求', '满足在超大功率下的连续运转要求')
add(PAPER, 'B0001', 'technology', 'name', 'TECH-001', 'HH6000电动压裂泵组', 'HH6000大功率电动压裂泵组', 'HH6000大功率电动压裂泵组')
add(PAPER, 'B0001', 'technology', 'version_id', 'TECH-001', 'HH6000电动压裂泵组', 'HH6000', 'HH6000')
add(PAPER, 'B0003', 'technology', 'function', 'TECH-001', 'HH6000电动压裂泵组', '交流变频电机作为原动机，为压裂泵提供动力。压裂泵动力端为经过特殊结构设计的曲柄连杆机构，其作用是将电机旋转运动转化为往复直线运动，向液力端提供所需的工作动能', '交流变频电机作为原动机，为压裂泵提供动力。压裂泵动力端为经过特殊结构设计的曲柄连杆机构，其作用是将电机旋转运动转化为往复直线运动，向液力端提供所需的工作动能')
add(PAPER, 'B0003', 'technology', 'principle', 'TECH-001', 'HH6000电动压裂泵组', '网电为电动压裂泵提供电源，交流变频电机通过中压变频控制系统进行调速，实现流量无级调节。', '网电为电动压裂泵提供电源，交流变频电机通过中压变频控制系统进行调速，实现流量无级调节。')
add(PAPER, 'B0003', 'technology', 'components', 'TECH-001', 'HH6000电动压裂泵组', ['变电站', '中压变频房', '电动压裂泵', '动力端总成', '液力端总成'], 'HH6000电动压裂泵组由变电站、中压变频房 (含变频系统和PLC控制系统) 和电动压裂泵组成。电动压裂泵又由动力端总成 (含机架总成、曲轴总成、小齿轮及交流变频电机和十字头总成) 和液力端总成组成。')
add(PAPER, 'B0004', 'technology', 'control_software', 'TECH-001', 'HH6000电动压裂泵组', 'PLC控制系统由中压变频PLC和工业以太网组成。', 'PLC控制系统由中压变频PLC和工业以太网组成。')
add(PAPER, 'B0004', 'technology', 'interfaces', 'TECH-001', 'HH6000电动压裂泵组', '操作人员可通过仪表车工作站、中压变频房触摸式工作站、本地触摸屏和变频器面板对变频器进行操作。选择以太网式远程I/O读取现场传感器的数据', '操作人员可通过仪表车工作站、中压变频房触摸式工作站、本地触摸屏和变频器面板对变频器进行操作。选择以太网式远程I/O读取现场传感器的数据')
add(PAPER, 'B0004', 'technology', 'alternatives', 'TECH-001', 'HH6000电动压裂泵组', [{'name': '柴油机加传动箱的传动结构形式', 'note': '论文用作结构对照的传统方案；原文没有完整方案比选记录'}], '打破了常规压裂泵车柴油机加传动箱的传动结构形式', content_nature='ai_interpretation', conditions='依据2017论文结构对比', limitations='仅列对照方案，不表示项目方曾完成系统比选，也不评价未核实的其他产品')
add(PAPER, 'B0004', 'technology', 'selection_reason', 'TECH-001', 'HH6000电动压裂泵组', '取消了中间机械变速传动机构，总体结构优化、工作可靠，系统传动效率提高2%~3%，泵组移运性得到提高，制造成本下降', '取消了中间机械变速传动机构，总体结构优化、工作可靠，系统传动效率提高2%~3%，泵组移运性得到提高，制造成本下降')
add(PAPER, 'B0004', 'technology', 'tradeoffs', 'TECH-001', 'HH6000电动压裂泵组', '压裂泵曲轴连杆机构负载大、工作条件十分苛刻，设计人员对该曲轴和连杆进行了优化设计，并在结构形式、尺寸、润滑通道和材料选用等方面进行了一系列的研究', '压裂泵曲轴连杆机构负载大、工作条件十分苛刻，设计人员对该曲轴和连杆进行了优化设计，并在结构形式、尺寸、润滑通道和材料选用等方面进行了一系列的研究')
add(PAPER, 'B0004', 'technology', 'failure_modes', 'TECH-001', 'HH6000电动压裂泵组', ['曲轴连杆机构负载大、工作条件十分苛刻'], '压裂泵曲轴连杆机构负载大、工作条件十分苛刻')
add(PAPER, 'B0005', 'technology', 'maintenance', 'TECH-001', 'HH6000电动压裂泵组', '电机可实现3 a免维护', '电机可实现3 a免维护')
add(PAPER, 'B0005', 'innovation', 'title', 'INNO-001', '电机直驱与机电融合一体化', '电机直驱技术', '电机直驱技术')
add(PAPER, 'B0004', 'innovation', 'problem_id', 'INNO-001', '电机直驱与机电融合一体化', 'PROB-001', '压裂泵曲轴连杆机构负载大、工作条件十分苛刻', content_nature='ai_interpretation', conditions='平台将传统机械传动痛点与低速重载结构问题归入同一问题记录', limitations='这是档案内部关联，不是原文给出的问题编号')
add(PAPER, 'B0004', 'innovation', 'measure', 'INNO-001', '电机直驱与机电融合一体化', '将动力机 (电机) 与执行机构 (压裂泵) 纳入一体化设计，打破了常规压裂泵车柴油机加传动箱的传动结构形式，取消了中间机械变速传动机构', '将动力机 (电机) 与执行机构 (压裂泵) 纳入一体化设计，打破了常规压裂泵车柴油机加传动箱的传动结构形式，取消了中间机械变速传动机构')
add(PAPER, 'B0004', 'innovation', 'mechanism', 'INNO-001', '电机直驱与机电融合一体化', '总体结构优化、工作可靠，系统传动效率提高2%~3%，泵组移运性得到提高，制造成本下降', '总体结构优化、工作可靠，系统传动效率提高2%~3%，泵组移运性得到提高，制造成本下降')
add(PAPER, 'B0004', 'innovation', 'baseline', 'INNO-001', '电机直驱与机电融合一体化', '柴油机加传动箱的传动结构形式', '打破了常规压裂泵车柴油机加传动箱的传动结构形式')
add(PAPER, 'B0004', 'innovation', 'tradeoffs', 'INNO-001', '电机直驱与机电融合一体化', '压裂泵曲轴连杆机构负载大、工作条件十分苛刻', '压裂泵曲轴连杆机构负载大、工作条件十分苛刻')
add(PAPER, 'B0004', 'innovation', 'applicable_conditions', 'INNO-001', '电机直驱与机电融合一体化', ['工作时，电机两端轴伸齿轮直接驱动曲轴'], '工作时，电机两端轴伸齿轮直接驱动曲轴，能效比高，操控性能好，具有更高的可靠性和稳定性')
add(KCZG, 'B0001', 'innovation', 'title', 'INNO-002', '双端传动与低速重载承载结构', '双端传动结构斜齿轮结构', '创新研发了双端传动结构斜齿轮结构')
add(PAPER, 'B0004', 'innovation', 'measure', 'INNO-002', '双端传动与低速重载承载结构', 'HH6000电动压裂泵组采用在曲轴两端安装2对斜齿轮，2对斜齿轮旋向相反，这2对斜齿轮组合起来相当于一对人字形齿轮。曲轴采用六支撑结构，齿轮置于曲轴两端', 'HH6000电动压裂泵组采用在曲轴两端安装2对斜齿轮，2对斜齿轮旋向相反，这2对斜齿轮组合起来相当于一对人字形齿轮。曲轴采用六支撑结构，齿轮置于曲轴两端')
add(PAPER, 'B0004', 'innovation', 'mechanism', 'INNO-002', '双端传动与低速重载承载结构', '曲轴两端的大齿轮起飞轮的作用，可以减缓振动。', '由于柱塞泵做往复运动，传动机构各杆件所产生的惯性力 (力矩) 将会引起泵的周期性振动。采用此结构后，曲轴两端的大齿轮起飞轮的作用，可以减缓振动。')
add(PAPER, 'B0004', 'innovation', 'tradeoffs', 'INNO-002', '双端传动与低速重载承载结构', '在低速重载条件下曲轴、连杆、十字头结构和滑动轴承技术方面取得了成功，并在后续测试中得到成功的验证。', '在低速重载条件下曲轴、连杆、十字头结构和滑动轴承技术方面取得了成功，并在后续测试中得到成功的验证。')
add(PAPER, 'B0003', 'innovation', 'title', 'INNO-003', '中压变频与PLC精准控制', '中压变频控制系统', '中压变频控制系统')
add(PAPER, 'B0004', 'innovation', 'measure', 'INNO-003', '中压变频与PLC精准控制', 'PLC控制系统由中压变频PLC和工业以太网组成。', 'PLC控制系统由中压变频PLC和工业以太网组成。')
add(PAPER, 'B0004', 'innovation', 'mechanism', 'INNO-003', '中压变频与PLC精准控制', '通过控制交流变频电机的输出特性，可实现压裂泵的精准控制和排量压力的无级调节。', '通过控制交流变频电机的输出特性，可实现压裂泵的精准控制和排量压力的无级调节。')
add(PAPER, 'B0004', 'innovation', 'tradeoffs', 'INNO-003', '中压变频与PLC精准控制', '通过变频器，电机只需在额定电流下就可启动，电流平滑无冲击，减少了启动电流对电机和电网的冲击，延长了电机的使用寿命。', '通过变频器，电机只需在额定电流下就可启动，电流平滑无冲击，减少了启动电流对电机和电网的冲击，延长了电机的使用寿命。')

PARAMS = '针对这种现状，四川宏华石油设备有限公司研制出了功率大、占地面积小、绿色经济环保的HH6000电动压裂泵组。\n1 技术分析\n1.1 基本参数\n通过参考国内外压裂泵的基本参数，结合页岩气开发特点，新型压裂泵组设计为卧式五缸单作用柱塞泵，额定输入功率4 500 kW，采用ø101.6 mm柱塞时最大压力为105 MPa，采用ø127.0 mm柱塞时最大压力为70 MPa，冲程254 mm，最高冲数为275 min-1，采用速比为4.516 1的人字齿轮副，主机质量约28 t。'
COMPARISON = '宏华公司\n产品型号\nFC-2251-Q\nHQ-2000\nSYL3000-140Q\nApollo4500\nHH6000\n功率/kW\n1 678\n1 490\n2 237\n3 355\n4 500\n型式\n车载式\n车载式\n车载式\n车载式\n橇装式\n最高压力/MPa\n140\n105\n140\n140\n105\n105 MPa时排量/(m3·min-1)\n0.95\n0.82\n1.28\n1.92\n2.32\n70 MPa时排量/(m3·min-1)\n1.45\n1.14\n1.92\n2.88\n3.22\n外形尺寸/(m×m×m)\n10.7×2.5×4.1\n10.8×2.5×4.0\n12.0×2.8×4.1\n10.5×2.5×4.2\n6.3×3.0×3.0'
H9_FIELD = '000电动压裂泵组完成了四川长宁H9平台的页岩气压裂施工，施工现场如图 3所示。平台上一共分布有6口丛式井，每口井按照平均20段进行压裂作业。每段液量1 800~2 000 m3，每段加砂80~150 t，作业施工压力70~85 MPa。在此期间，1号电动压裂泵组累计运行132.2 h (66段)，2号电动泵组累计运行107.2h (48段)，2套泵组供液能力3.0~4.5 m3/min，约占总施工液量的1/4，砂的质量浓度100~200 kg/m3，设备运行情况良好，得到了用户的高度评价。'
ARCHIVE_COSTS = '该项目取得了9项国家专利，6000HP电动压裂泵系统为客户节省设备购置费用30%～40%，节省燃料成本46%，节省易损件40%'
metrics = [
    ('MET-001', '额定输入功率', 4500, 'kW', PAPER, 'B0003', PARAMS, 'HH6000电动压裂泵组', '卧式五缸单作用柱塞泵', ''),
    ('MET-002', '采用ø101.6 mm柱塞时最大压力', 105, 'MPa', PAPER, 'B0003', PARAMS, 'HH6000电动压裂泵组', '采用ø101.6 mm柱塞', ''),
    ('MET-003', '采用ø127.0 mm柱塞时最大压力', 70, 'MPa', PAPER, 'B0003', PARAMS, 'HH6000电动压裂泵组', '采用ø127.0 mm柱塞', ''),
    ('MET-004', '最高冲数', 275, 'min-1', PAPER, 'B0003', PARAMS, 'HH6000电动压裂泵组', '卧式五缸单作用柱塞泵', ''),
    ('MET-005', '主机质量', 28, 't', PAPER, 'B0003', PARAMS, 'HH6000电动压裂泵组', '卧式五缸单作用柱塞泵', '约'),
    ('MET-006', '井场内噪音', 85, '分贝', MEDIA, 'B0001', '全电动钻井及压裂装备实现井场内噪音85分贝以下，井场边缘区域在60分贝以下', '全电动钻井及压裂装备', '井场内', '以下'),
    ('MET-007', '105 MPa时排量', 2.32, 'm3·min-1', PAPER, 'B0005', COMPARISON, 'HH6000', '105 MPa时排量/(m3·min-1)', ''),
    ('MET-008', '70 MPa时排量', 3.22, 'm3·min-1', PAPER, 'B0005', COMPARISON, 'HH6000', '70 MPa时排量/(m3·min-1)', ''),
    ('MET-009', '1号电动压裂泵组累计运行', 132.2, 'h', PAPER, 'B0006', H9_FIELD, '1号电动压裂泵组', '四川长宁H9平台的页岩气压裂施工', ''),
    ('MET-010', '2号电动泵组累计运行', 107.2, 'h', PAPER, 'B0006', H9_FIELD, '2号电动泵组', '四川长宁H9平台的页岩气压裂施工', ''),
    ('MET-011', '燃料费用', 40, '%', PAPER, 'B0005', '按照当前油价和电价的差别，采用电动压裂泵比常规压裂车可节省40%以上的燃料费用。', '电动压裂泵', '按照当前油价和电价的差别', '以上'),
    ('MET-012', '节省燃料成本', 46, '%', ARCHIVE, 'B0001', ARCHIVE_COSTS, '6000HP电动压裂泵系统', '节省燃料成本46%', ''),
    ('MET-013', '节省易损件', 40, '%', ARCHIVE, 'B0001', ARCHIVE_COSTS, '6000HP电动压裂泵系统', '节省易损件40%', ''),
    ('MET-014', '国家专利', 9, '项', ARCHIVE, 'B0001', ARCHIVE_COSTS, '6000HP电动压裂泵', '该项目取得了9项国家专利', '')
]
for rid, title, value, unit, source, chunk, quote, subject, conditions, qualifier in metrics:
    value_quote = f'{value}\n' if rid in {'MET-007', 'MET-008'} else quote
    add(source, chunk, 'metric', 'name', rid, title, title, quote)
    add(source, chunk, 'metric', 'subject', rid, title, subject, quote)
    add(source, chunk, 'metric', 'value', rid, title, value, value_quote, object=subject, unit=unit, conditions=conditions)
    add(source, chunk, 'metric', 'unit', rid, title, unit, quote)
    add(source, chunk, 'metric', 'conditions', rid, title, conditions, quote)
    if qualifier:
        add(source, chunk, 'metric', 'qualifier', rid, title, qualifier, quote)

add(PAPER, 'B0005', 'metric', 'name', 'MET-015', '外形尺寸', '外形尺寸', COMPARISON)
add(PAPER, 'B0005', 'metric', 'original_statement', 'MET-015', '外形尺寸', '6.3×3.0×3.0', COMPARISON, object='HH6000', unit='m×m×m', conditions='外形尺寸/(m×m×m)')
add(PAPER, 'B0006', 'metric', 'name', 'MET-016', '长宁H9供液能力', '2套泵组供液能力', H9_FIELD)
add(PAPER, 'B0006', 'metric', 'original_statement', 'MET-016', '长宁H9供液能力', '3.0~4.5 m3/min，约占总施工液量的1/4', H9_FIELD, object='2套泵组', unit='m3/min', conditions='四川长宁H9平台的页岩气压裂施工')
add(PAPER, 'B0006', 'metric', 'name', 'MET-017', '长宁H9施工压力', '作业施工压力', H9_FIELD)
add(PAPER, 'B0006', 'metric', 'original_statement', 'MET-017', '长宁H9施工压力', '70~85 MPa', H9_FIELD, object='长宁H9平台', unit='MPa', conditions='四川长宁H9平台的页岩气压裂施工')
add(PAPER, 'B0006', 'metric', 'name', 'MET-018', '单台等效常规压裂车', '单台6000HP压裂泵功率', '单台6000HP压裂泵功率相当于3辆2000型常规压裂车的总和')
add(PAPER, 'B0006', 'metric', 'original_statement', 'MET-018', '单台等效常规压裂车', '相当于3辆2000型常规压裂车的总和', '单台6000HP压裂泵功率相当于3辆2000型常规压裂车的总和', object='单台6000HP压裂泵', unit='辆2000型常规压裂车', conditions='单台6000HP压裂泵功率相当于3辆2000型常规压裂车的总和')
add(PAPER, 'B0006', 'metric', 'name', 'MET-019', '六台等效常规压裂车', '6台HH6000电动压裂泵组', '以构建1套36000HP压裂泵组为例，仅用6台HH6000电动压裂泵组就可以实现18台2000型压裂车才能进行的大型工厂化压裂作业')
add(PAPER, 'B0006', 'metric', 'original_statement', 'MET-019', '六台等效常规压裂车', '实现18台2000型压裂车才能进行的大型工厂化压裂作业', '以构建1套36000HP压裂泵组为例，仅用6台HH6000电动压裂泵组就可以实现18台2000型压裂车才能进行的大型工厂化压裂作业', object='36000HP压裂泵组', unit='辆2000型压裂车', conditions='以构建1套36000HP压裂泵组为例')
add(MEDIA, 'B0001', 'metric', 'name', 'MET-020', '媒体所述八台等效关系', '8台6000马力压裂泵', '8台6000马力压裂泵至少等同于20台以上传统柴油机压裂设备的性能')
add(MEDIA, 'B0001', 'metric', 'original_statement', 'MET-020', '媒体所述八台等效关系', '至少等同于20台以上传统柴油机压裂设备的性能', '8台6000马力压裂泵至少等同于20台以上传统柴油机压裂设备的性能', object='8台6000马力压裂泵', unit='台传统柴油机压裂设备', conditions='8台6000马力压裂泵至少等同于20台以上传统柴油机压裂设备的性能')
add(PAPER, 'B0004', 'metric', 'name', 'MET-021', '系统传动效率改善', '系统传动效率', '系统传动效率提高2%~3%')
add(PAPER, 'B0004', 'metric', 'original_statement', 'MET-021', '系统传动效率改善', '提高2%~3%', '系统传动效率提高2%~3%', object='压裂泵', unit='%', conditions='取消了中间机械变速传动机构')
add(ARCHIVE, 'B0001', 'metric', 'name', 'MET-022', '设备购置费用节省（申报披露）', '设备购置费用', ARCHIVE_COSTS)
add(ARCHIVE, 'B0001', 'metric', 'original_statement', 'MET-022', '设备购置费用节省（申报披露）', '30%～40%', ARCHIVE_COSTS, object='6000HP电动压裂泵系统', unit='%', conditions='为客户节省设备购置费用30%～40%')

add(PAPER, 'B0001', 'paper', 'title', 'PAPER-001', '新型大功率电动压裂泵组的研制', '新型大功率电动压裂泵组的研制', '新型大功率电动压裂泵组的研制')
add(PAPER, 'B0001', 'paper', 'authors', 'PAPER-001', '新型大功率电动压裂泵组的研制', ['田雨', '谢梅英'], '田雨, 谢梅英')
add(PAPER, 'B0001', 'paper', 'affiliations', 'PAPER-001', '新型大功率电动压裂泵组的研制', ['四川宏华石油设备有限公司成都研发部'], '四川宏华石油设备有限公司成都研发部')
add(PAPER, 'B0001', 'paper', 'year', 'PAPER-001', '新型大功率电动压裂泵组的研制', 2017, '石油机械, 2017, 45(4): 94-97')
add(PAPER, 'B0001', 'paper', 'venue', 'PAPER-001', '新型大功率电动压裂泵组的研制', '石油机械', '石油机械, 2017, 45(4): 94-97')
add(PAPER, 'B0001', 'paper', 'volume', 'PAPER-001', '新型大功率电动压裂泵组的研制', '45', '2017, 45(4)')
add(PAPER, 'B0001', 'paper', 'issue', 'PAPER-001', '新型大功率电动压裂泵组的研制', '4', '45(4)')
add(PAPER, 'B0001', 'paper', 'pages', 'PAPER-001', '新型大功率电动压裂泵组的研制', '94-97', '45(4): 94-97')
add(PAPER, 'B0001', 'paper', 'doi', 'PAPER-001', '新型大功率电动压裂泵组的研制', '10.16082/j.cnki.issn.1001-4578.2017.04.021', 'DOI: 10.16082/j.cnki.issn.1001-4578.2017.04.021.')
add(PAPER, 'B0001', 'paper', 'reading_scope', 'PAPER-001', '新型大功率电动压裂泵组的研制', '全文', 'Download PDF', content_nature='ai_interpretation', conditions='本轮已核读网页正文B0001—B0007，含中英文摘要、技术正文、表格文本和参考文献', limitations='网页中的Download PDF入口未单独下载核验；“全文”指本轮网页正文核读范围')
add(PAPER, 'B0001', 'paper', 'project_relation', 'PAPER-001', '新型大功率电动压裂泵组的研制', '任务相关', 'HH6000大功率电动压裂泵组', content_nature='ai_interpretation', conditions='论文题名、摘要和作者单位均指向宏华HH6000电动压裂泵组', limitations='这是论文与装备对象的研究关联，不等于获奖成果清单确认')
add(ARCHIVE, 'B0001', 'achievement', 'kind', 'PAT-ACH-001', '国家专利（申报披露）', '专利', '该项目取得了9项国家专利')
add(ARCHIVE, 'B0001', 'achievement', 'count', 'PAT-ACH-001', '国家专利（申报披露）', 9, '该项目取得了9项国家专利')
add(ARCHIVE, 'B0001', 'achievement', 'count_unit', 'PAT-ACH-001', '国家专利（申报披露）', '项', '该项目取得了9项国家专利')
add(ARCHIVE, 'B0001', 'achievement', 'count_basis', 'PAT-ACH-001', '国家专利（申报披露）', '历史申报披露数量，未展开逐项清单', '该项目取得了9项国家专利', content_nature='ai_interpretation', conditions='历史申报仅给出9项国家专利总数', limitations='未据此推定申请、授权、有效专利或项目实际采用情况')
add(ARCHIVE, 'B0001', 'achievement', 'item_list_obtained', 'PAT-ACH-001', '国家专利（申报披露）', False, '该项目取得了9项国家专利', content_nature='ai_interpretation', conditions='本轮已核读来源没有逐项专利编号清单', limitations='表示本轮未取得清单，不表示项目不存在相关专利')
add(ARCHIVE, 'B0001', 'achievement', 'review_status', 'PAT-ACH-001', '国家专利（申报披露）', '待逐项核验', '该项目取得了9项国家专利', content_nature='ai_interpretation', conditions='只有历史申报总数可供核对', limitations='需取得逐项清单并核原件，未完成项目方或专家确认')

add(COMPANY, 'B0001', 'event', 'title', 'EVT-001', 'OTC展出全球首台6000HP电动压裂橇', '于2012年OTC 展出全球首台6000HP 电动压裂橇')
add(COMPANY, 'B0001', 'event', 'date', 'EVT-001', 'OTC展出全球首台6000HP电动压裂橇', '2012', '于2012年OTC 展出全球首台6000HP 电动压裂橇')
add(PAPER, 'B0005', 'event', 'title', 'EVT-002', '美国加州首次现场压裂作业', '2015年3—5月，2套HH6000电动压裂泵组在美国加利福利亚州完成了12口井45个阶段的丛式井压裂作业，这也是HH6000电动压裂泵组的第1次现场作业')
add(PAPER, 'B0005', 'event', 'date', 'EVT-002', '美国加州首次现场压裂作业', '2015年3—5月', '2015年3—5月')
add(PAPER, 'B0005', 'event', 'stage', 'EVT-002', '美国加州首次现场压裂作业', '现场作业', '2015年3—5月，2套HH6000电动压裂泵组在美国加利福利亚州完成了12口井45个阶段的丛式井压裂作业，这也是HH6000电动压裂泵组的第1次现场作业')
add(PAPER, 'B0006', 'event', 'title', 'EVT-003', '四川长宁H9平台压裂施工', '四川长宁H9平台的页岩气压裂施工', H9_FIELD)
add(PAPER, 'B0005', 'event', 'date', 'EVT-003', '四川长宁H9平台压裂施工', '2015年11月15日至12月31日', '2015年11月15日至12月31日')
add(PAPER, 'B0006', 'event', 'stage', 'EVT-003', '四川长宁H9平台压裂施工', '页岩气压裂施工', H9_FIELD)
add(PAPER, 'B0001', 'event', 'title', 'EVT-004', '论文正式发表', '石油机械, 2017, 45(4): 94-97')
add(PAPER, 'B0001', 'event', 'date', 'EVT-004', '论文正式发表', '2017', '石油机械, 2017, 45(4): 94-97')
add(COMPANY, 'B0001', 'event', 'title', 'EVT-005', '推出电驱压裂解决方案与配套产品', '2018年国内率先推出电驱压裂解决方案和全套电驱配套产品')
add(COMPANY, 'B0001', 'event', 'date', 'EVT-005', '推出电驱压裂解决方案与配套产品', '2018', '2018年国内率先推出电驱压裂解决方案和全套电驱配套产品')
add(ARCHIVE, 'B0001', 'event', 'title', 'EVT-006', '获得好设计银奖', '6000HP电动压裂泵', '"year": 2019,\n"level": "银奖",\n"name": "6000HP电动压裂泵"')
add(ARCHIVE, 'B0001', 'event', 'date', 'EVT-006', '获得好设计银奖', '2019', '"year": 2019')
add(MOST, 'B0001', 'event', 'title', 'EVT-007', '实现产业化并形成多地应用', '目前，6000HP页岩气压裂装备已实现了产业化，形成产值上亿元，已在新疆、川渝等多地完成了多个页岩气区块压裂任务')
add(MOST, 'B0001', 'event', 'date', 'EVT-007', '实现产业化并形成多地应用', '2021年06月30日', '2021年06月30日 15:32')

add(PAPER, 'B0005', 'validation', 'title', 'VAL-001', '美国加州首次现场压裂作业', '第1次现场作业', '这也是HH6000电动压裂泵组的第1次现场作业')
add(PAPER, 'B0005', 'validation', 'version_id', 'VAL-001', '美国加州首次现场压裂作业', 'HH6000', 'HH6000')
add(PAPER, 'B0005', 'validation', 'performed_at', 'VAL-001', '美国加州首次现场压裂作业', '2015年3—5月', '2015年3—5月')
add(PAPER, 'B0005', 'validation', 'environment', 'VAL-001', '美国加州首次现场压裂作业', '美国加利福利亚州完成了12口井45个阶段的丛式井压裂作业', '美国加利福利亚州完成了12口井45个阶段的丛式井压裂作业')
add(PAPER, 'B0005', 'validation', 'result', 'VAL-001', '美国加州首次现场压裂作业', '整个作业过程安全、平稳', '整个作业过程安全、平稳')
add(PAPER, 'B0005', 'validation', 'limitations', 'VAL-001', '美国加州首次现场压裂作业', '论文报告首次现场作业，未提供原始施工日志、完整测试方法与长期可靠性统计', '整个作业过程安全、平稳', content_nature='ai_interpretation', conditions='本轮只核读论文对现场作业的概述', limitations='不将报道性结果升级为独立工程验证或全工况可靠性结论')
add(PAPER, 'B0006', 'validation', 'title', 'VAL-002', '四川长宁H9平台压裂施工', '四川长宁H9平台的页岩气压裂施工', H9_FIELD)
add(PAPER, 'B0006', 'validation', 'environment', 'VAL-002', '四川长宁H9平台压裂施工', '每段液量1 800~2 000 m3，每段加砂80~150 t，作业施工压力70~85 MPa', H9_FIELD)
add(PAPER, 'B0006', 'validation', 'metric_ids', 'VAL-002', '四川长宁H9平台压裂施工', ['MET-009', 'MET-010', 'MET-016', 'MET-017'], H9_FIELD, content_nature='ai_interpretation', conditions='指标均来自同一2017论文长宁H9现场段落', limitations='是档案内部证据关联，不是原始试验报告中的指标编号')
add(PAPER, 'B0006', 'validation', 'result', 'VAL-002', '四川长宁H9平台压裂施工', '设备运行情况良好，得到了用户的高度评价。', H9_FIELD)
add(PAPER, 'B0006', 'validation', 'limitations', 'VAL-002', '四川长宁H9平台压裂施工', '未取得原始施工日志、逐段完整记录、测量不确定度和对照组数据', H9_FIELD, content_nature='ai_interpretation', conditions='论文提供两台泵组累计运行时间与施工概况', limitations='不能由累计运行时间推导全生命周期可靠性或普遍节能率')

add(PAPER, 'B0005', 'application', 'scenario', 'APP-001', '美国加州丛式井压裂', '美国加利福利亚州完成了12口井45个阶段的丛式井压裂作业')
add(PAPER, 'B0005', 'application', 'version_id', 'APP-001', '美国加州丛式井压裂', 'HH6000', 'HH6000')
add(PAPER, 'B0005', 'application', 'start_date', 'APP-001', '美国加州丛式井压裂', '2015年3—5月', '2015年3—5月')
add(PAPER, 'B0005', 'application', 'scale', 'APP-001', '美国加州丛式井压裂', '2套HH6000电动压裂泵组在美国加利福利亚州完成了12口井45个阶段的丛式井压裂作业', '2套HH6000电动压裂泵组在美国加利福利亚州完成了12口井45个阶段的丛式井压裂作业')
add(PAPER, 'B0006', 'application', 'scenario', 'APP-002', '四川长宁H9平台页岩气压裂', '四川长宁H9平台的页岩气压裂施工')
add(PAPER, 'B0005', 'application', 'start_date', 'APP-002', '四川长宁H9平台页岩气压裂', '2015年11月15日至12月31日', '2015年11月15日至12月31日')
add(PAPER, 'B0006', 'application', 'scale', 'APP-002', '四川长宁H9平台页岩气压裂', '平台上一共分布有6口丛式井，每口井按照平均20段进行压裂作业。', '平台上一共分布有6口丛式井，每口井按照平均20段进行压裂作业。')
add(PAPER, 'B0006', 'application', 'feedback', 'APP-002', '四川长宁H9平台页岩气压裂', '设备运行情况良好，得到了用户的高度评价。', '设备运行情况良好，得到了用户的高度评价。')
add(MOST, 'B0001', 'application', 'scenario', 'APP-003', '新疆、川渝等页岩气区块', '已在新疆、川渝等多地完成了多个页岩气区块压裂任务')
add(MOST, 'B0001', 'application', 'status', 'APP-003', '新疆、川渝等页岩气区块', '已应用', '已在新疆、川渝等多地完成了多个页岩气区块压裂任务', content_nature='ai_interpretation', conditions='科技部2021报道明确称多个区块已完成压裂任务', limitations='只描述该报道时点，不代表2026年仍在运行或全部市场部署状态')
add(MOST, 'B0001', 'application', 'scale', 'APP-003', '新疆、川渝等页岩气区块', '形成产值上亿元', '形成产值上亿元')
add(MOST, 'B0001', 'application', 'benefit_basis', 'APP-003', '新疆、川渝等页岩气区块', '科技部2021报道，产值不等于项目利润或用户节省', '形成产值上亿元', content_nature='ai_interpretation', conditions='科技部报道只给出“形成产值上亿元”', limitations='没有审计口径、统计区间、利润或用户节省明细，不转换成精确效益金额')
add(COMPANY, 'B0001', 'application', 'scenario', 'APP-004', '煤层气勘探开发电动压裂设备服务', '煤层气勘探开发电动压裂设备服务项目')
add(COMPANY, 'B0001', 'application', 'status', 'APP-004', '煤层气勘探开发电动压裂设备服务', '成功中标', '东方宏华成功中标一国内客户为期两年的煤层气勘探开发电动压裂设备服务项目')
add(COMPANY, 'B0001', 'application', 'scale', 'APP-004', '煤层气勘探开发电动压裂设备服务', '为期两年的煤层气勘探开发电动压裂设备服务项目,中标金额约3.7亿元', '为期两年的煤层气勘探开发电动压裂设备服务项目,中标金额约3.7亿元')
add(COMPANY, 'B0001', 'application', 'benefit_basis', 'APP-004', '煤层气勘探开发电动压裂设备服务', '公开资料提取件，非合同原件，未披露客户名称', '中标金额约3.7亿元', content_nature='ai_interpretation', conditions='宏华相关公开资料提取件披露服务期和中标金额', limitations='尚未取得PDF原件、合同、客户名称与执行结果；不认定6000HP型号实际用于该服务')

add(PAPER, 'B0004', 'innovation', 'title', 'ANA-001', '直驱不是简单换电机，而是结构、控制与承载共同重构', '电机直驱的结构形式', '将动力机 (电机) 与执行机构 (压裂泵) 纳入一体化设计，打破了常规压裂泵车柴油机加传动箱的传动结构形式，取消了中间机械变速传动机构', content_nature='ai_interpretation', conditions='依据2017论文的电机直驱、双端斜齿轮、变频与PLC结构', limitations='属于机制分析，不是新增实验结论')
add(PAPER, 'B0004', 'innovation', 'mechanism', 'ANA-001', '直驱不是简单换电机，而是结构、控制与承载共同重构', '电机直驱取消中间机械变速传动机构；双端斜齿轮与六支撑曲轴处理低速重载和周期振动；中压变频与PLC负责排量压力调节，因此大功率、精确控制和结构紧凑是共同作用的结果，不能只归因于电机替换。', '将动力机 (电机) 与执行机构 (压裂泵) 纳入一体化设计，打破了常规压裂泵车柴油机加传动箱的传动结构形式，取消了中间机械变速传动机构', content_nature='ai_interpretation', conditions='依据2017论文结构描述整合', limitations='机制整合分析，不提升为工程验证等级')
add(PAPER, 'B0005', 'metric', 'name', 'ANA-002', '成本数据只能按各自测算条件理解', '成本数据只能按各自测算条件理解', '按照当前油价和电价的差别，采用电动压裂泵比常规压裂车可节省40%以上的燃料费用。', content_nature='ai_interpretation', conditions='依据论文效益模型、申报披露和媒体引述', limitations='不是统一测量口径或普适节省率')
add(PAPER, 'B0005', 'metric', 'original_statement', 'ANA-002', '成本数据只能按各自测算条件理解', '论文的燃料节省建立在当前油价和电价差别、36000HP组态及18台对6台比较上；申报中的购置费、燃料和易损件节省缺原始测算表；媒体等效关系未披露独立测量方法，不能相互替代或合并成统一比例。', '按照当前油价和电价的差别，采用电动压裂泵比常规压裂车可节省40%以上的燃料费用。', content_nature='ai_interpretation', conditions='区分论文、申报与媒体三类证据', limitations='成本判断边界，不是财务审计结论')

for rid, title, quote, source, chunk in [
    ('TASK-001', '取得9项国家专利逐项清单', '该项目取得了9项国家专利', ARCHIVE, 'B0001'),
    ('TASK-002', '取得长宁H9原始施工与运行记录', '1号电动压裂泵组累计运行132.2 h (66段)', PAPER, 'B0006'),
    ('TASK-003', '核对成本测算表与适用边界', '以构建1套36000HP的压裂车组工作1 h为例', PAPER, 'B0006'),
    ('TASK-004', '补宏华原始PDF与奖项官方名单', '于2012年OTC 展出全球首台6000HP 电动压裂橇', COMPANY, 'B0001')]:
    add(source, chunk, 'task', 'title', rid, title, title, quote, content_nature='ai_interpretation', conditions='当前证据缺口已明确', limitations='待外部原件或项目方补证，未完成不升质量状态')
    add(source, chunk, 'task', 'task_type', rid, title, '核验', quote, content_nature='ai_interpretation', conditions='需要逐项核验来源与原件', limitations='不是已完成')
    add(source, chunk, 'task', 'priority', rid, title, 'P0', quote, content_nature='ai_interpretation', conditions='影响工程判断或成果归属', limitations='优先补证')
    add(source, chunk, 'task', 'owner', rid, title, '待指定', quote, content_nature='ai_interpretation', conditions='需项目方或资料负责人接手', limitations='未指派，不冒称已联系')
    add(source, chunk, 'task', 'status', rid, title, '待补证', quote, content_nature='ai_interpretation', conditions='原件或审核尚未取得', limitations='不是已完成任务')
    add(source, chunk, 'task', 'acceptance', rid, title, '取得可定位原件并逐条核读，保留来源、对象、日期与范围', quote, content_nature='ai_interpretation', conditions='按证据契约验收', limitations='不凭文件数量验收')

p = pp.project(pp.LIB, PID)
w = rw.current(p)
applied = set(rw.dataset(p, w).get('applied_candidate_ids', [])) if w['revision'] else set()
compare_keys = ('operation', 'entity', 'field', 'record_id', 'value', 'content_nature', 'source_id', 'source_sha256', 'chunks_path', 'chunks_sha256', 'chunk_id', 'quote', 'quote_sha256', 'object', 'unit', 'conditions', 'limitations')
published_candidates = [c for c in w['candidates'] if c['id'] in applied]
def already_published(cid):
    candidate = next(c for c in w['candidates'] if c['id'] == cid)
    return any(all(candidate.get(k) == old.get(k) for k in compare_keys) for old in published_candidates)
if w['revision'] and all(already_published(cid) for cid in created):
    result = {'status': 'no_changes', 'revision': 'research-%06d' % w['revision']}
else:
    selected = [cid for cid in created if cid not in applied]
    result = rw.publish(pp.LIB, PID, ACTOR, '079核读发布：事实、指标、机制、现场与缺口均有逐字证据', expected_candidate_ids=selected, selected_candidate_ids=selected)
revision = result['revision']
folder, _ = rw.check_version(p, revision)
data = rw.dataset(p, revision=revision)
dataset_sha256 = pp.sha((folder / '档案.json').read_bytes())

import research_reader_notes as notes
import research_assessment as assessment

guide = {
    'schema': notes.SCHEMA,
    'version': '0.1.0',
    'project_id': PID,
    'research_revision': revision,
    'dataset_sha256': dataset_sha256,
    'content_nature': 'ai_reading_guide',
    'overview': '这份档案以历史申报、2017论文、科技部报道和有限核读的企业/媒体资料为依据。先确认宏华HH6000泵组，再读直驱、承载和控制机制，最后核对现场、成本与专利缺口；AI解读不等于工程结论。',
    'modules': [
        {'module_id': 1, 'summary': '项目对象是四川宏华石油设备有限公司的6000HP电动压裂泵组，历史条目为2019银奖。科技部2021材料说明当时已产业化，不代表2026年的最新经营状态。', 'record_ids': ['PROJ-001', 'ORG-001', 'AWARD-001'], 'gaps': ['官方获奖名单、完成人和完整项目编号仍待核验', '2021之后的版本和产业化状态未持续追踪']},
        {'module_id': 2, 'summary': '传统机械传动的小功率、占地、维护和精准控制问题，对应大功率直驱、网电变频与PLC控制方案。技术结构按变电站、中压变频房、动力端和液力端阅读。', 'record_ids': ['PROB-001', 'TECH-001'], 'gaps': ['项目方原始设计任务书、备选方案和完整设计取舍未取得', '材料、制造工艺和具体控制参数仍不完整']},
        {'module_id': 3, 'summary': '三条机制分别是电机直驱与机电融合、双端斜齿轮与六支撑曲轴承载、以及中压变频与PLC调节。它们共同作用，不能把性能只归因于换用电机。', 'record_ids': ['INNO-001', 'INNO-002', 'INNO-003'], 'gaps': ['双端传动等结构缺少原始图纸、试验记录与失效数据', '科创中国所述TRIZ过程尚缺项目方方法记录佐证']},
        {'module_id': 4, 'summary': '额定输入功率、压力、排量和质量来自2017论文；长宁H9记录包含两台泵组132.2h与107.2h。三种等效台数及成本披露各有口径，不能合并或外推。', 'record_ids': ['MET-001', 'MET-002', 'MET-003', 'MET-007', 'MET-009', 'MET-010', 'MET-016', 'MET-017'], 'gaps': ['原始施工日志、逐段数据、测量方法与不确定度未取得', '申报成本比例和媒体报道缺独立测算或测量报告']},
        {'module_id': 5, 'summary': '2017《石油机械》论文网页正文已核读，可回溯参数和现场描述。9项国家专利仅为历史申报总数，尚无逐项编号清单，未推定法律状态或型号采用。', 'record_ids': ['PAPER-001', 'PAT-ACH-001'], 'gaps': ['取得9项专利的名称、编号、申请人及与项目的逐项关系', '论文PDF入口未单独下载核验，原网页图表图片未做工程复算']},
        {'module_id': 6, 'summary': '时间线从2012展出、2015两次现场作业、2017论文、2018方案、2019获奖，到2021产业化报道。企业后续煤层气服务资料与获奖型号应用不能直接画等号。', 'record_ids': ['EVT-001', 'EVT-002', 'EVT-003', 'EVT-005', 'EVT-006', 'EVT-007'], 'gaps': ['早期展出的原始企业PDF和完整事件日期仍缺', '后续产业化节点需企业材料与时间口径交叉核验']},
        {'module_id': 7, 'summary': '应用证据覆盖美国加州、四川长宁H9及2021新疆川渝报道。东方宏华煤层气服务中标只作为后续企业业务线索，不认定6000HP型号已实际用于该合同。', 'record_ids': ['APP-001', 'APP-002', 'APP-003', 'APP-004'], 'gaps': ['具体客户、型号清单、合同执行与长期运行效果未披露', '产值和中标金额不是利润或用户节省，不作财务审计结论']},
        {'module_id': 8, 'summary': '当前优先补专利清单、现场原始记录、成本测算和企业PDF/官方名单。四项任务均待指定负责人，没有自动下派，也没有因入档而提高质量分或专家状态。', 'record_ids': [], 'gaps': ['四项P0补证任务均未完成，负责人和时间表待指定', '部分动态页与PDF获取失败，保留提取边界和pending来源']}
    ]
}
notes_result = notes.freeze(pp.LIB, PID, guide, ACTOR)

review = {
    'schema': assessment.SCHEMA,
    'version': '0.1.0',
    'project_id': PID,
    'research_revision': revision,
    'dataset_sha256': dataset_sha256,
    'content_nature': 'ai_research_review',
    'summary': '已形成可追溯的研究档案，覆盖身份、技术机制、指标、现场、应用和补证任务。论文与申报支持“说了什么”，但原始工程记录、专利清单和独立测算尚缺，因此不评质量总分，不作专家或工程认证。',
    'dimensions': [
        {'key': 'identity', 'stage': 'usable_with_limits', 'basis': '历史条目、论文作者单位和科技部材料共同指向四川宏华6000HP/HH6000泵组；后续东方宏华业务单独标范围。', 'record_ids': ['PROJ-001', 'ORG-001', 'AWARD-001'], 'gaps': ['官方获奖名单与完整完成人未核', '2021后的产品版本和企业主体变化未系统核读']},
        {'key': 'evidence', 'stage': 'usable_with_limits', 'basis': '核心参数与现场描述可回溯2017论文，历史和产业化分别有申报与科技部来源；媒体和提取件只作有限证据。', 'record_ids': ['PAPER-001', 'PROJ-001', 'MET-020'], 'gaps': ['科创中国直接页面404，环球网普通抓取无正文', '宏华PDF下载失败，提取件不能替代原件', '其他企业装备和工信部资料不用于宏华参数证明']},
        {'key': 'technical', 'stage': 'partial', 'basis': '结构、控制、基本参数及两次现场作业已有来源，长宁H9运行时间与施工条件可定位，但原始验证资料未入档。', 'record_ids': ['TECH-001', 'VAL-001', 'VAL-002', 'MET-009', 'MET-010'], 'gaps': ['原始施工日志、逐段数据、测量方法与不确定度', '结构试验、失效记录、长期可靠性与全工况边界']},
        {'key': 'transfer', 'stage': 'partial', 'basis': '可把直驱、承载和控制作为机制组合阅读，并明确组态、工况和成本口径，尚不能形成无条件迁移规则。', 'record_ids': ['INNO-001', 'INNO-002', 'INNO-003', 'MET-018', 'MET-019', 'MET-020'], 'gaps': ['原始备选方案、设计决策和失败迭代记录', 'TRIZ实际应用过程、目标工况适配及独立迁移验证']},
        {'key': 'rights', 'stage': 'unconfirmed', 'basis': '论文题录与网页正文可追溯；9项国家专利只有历史申报总数，未生成编号或权利状态。', 'record_ids': ['PAPER-001', 'PAT-ACH-001'], 'gaps': ['专利逐项清单、申请人、法律状态和项目采用关系', '原始图纸、企业PDF及公开再利用权限边界']},
        {'key': 'maintenance', 'stage': 'usable_with_limits', 'basis': '研究版本、导读和评估按数据指纹冻结，四项补证任务明确；历史草稿和未核来源不自动进入事实。', 'record_ids': ['PROJ-001'], 'gaps': ['任务负责人、期限、外部补证和项目方复核未落实', '后续来源变化需重新核读并建立新版本，不沿用本评估']}
    ],
    'priorities': [
        {'priority': 'P0', 'title': '取得9项国家专利逐项清单', 'why': '当前只有申报总数，无法判断专利身份、权属或项目采用关系。', 'next_step': '取得项目方清单及公开文本，逐项核对申请、公开、授权与项目关联。', 'record_ids': ['PAT-ACH-001']},
        {'priority': 'P0', 'title': '补齐长宁H9原始施工与运行记录', 'why': '论文给出两台累计运行时间与施工概况，但不足以支持完整可靠性或普遍效益判断。', 'next_step': '取得逐段日志、测量方法、异常记录和对照工况，保留原始时间与设备编号。', 'record_ids': ['VAL-002', 'MET-009', 'MET-010']},
        {'priority': 'P0', 'title': '核对成本测算与三种等效口径', 'why': '论文、历史申报和媒体引述的组态及测算边界不同，不能合并成统一比例。', 'next_step': '取得能源价格、传动效率、人员管汇和设备购置的原始测算表及适用范围。', 'record_ids': ['MET-011', 'MET-018', 'MET-019', 'MET-020', 'MET-022']},
        {'priority': 'P0', 'title': '补企业原始PDF与官方获奖名单', 'why': '部分网页/PDF只有提取件或失败记录，正式身份与企业历史仍需原件支撑。', 'next_step': '重新取得可定位原件，核对奖项、展出时间、主体和后续业务型号。', 'record_ids': ['EVT-001', 'EVT-006', 'APP-004']}
    ]
}
assessment_result = assessment.freeze(pp.LIB, PID, review, ACTOR)
report = {
    'project_id': PID,
    'candidate_count': len(created),
    'publish': result,
    'records': len(data['records']),
    'known_fact_cells': sum(c.get('value_state') == 'known' for r in data['records'] for c in r['cells'].values()),
    'ai_items': len(data.get('interpretations', [])),
    'reader_notes': {'version': '0.1.0', 'status': notes_result['status']},
    'assessment': {'version': '0.1.0', 'status': assessment_result['status'], 'evidence_audit': assessment_result['report']['evidence_audit']},
    'quality_score': None,
    'expert_reviewed': False
}
(OUT / 'publish-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
