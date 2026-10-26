"""Read-only SVG presentation helpers; no library or filesystem mutation.

ICON_SEMANTICS is an editorial mapping from the actual method title/operations,
not a historical assertion that these symbols belong to the method's authors.
"""
from html import escape

# Each tuple: method-specific visual metaphor, its connection to operations, geometry.
ICON_SEMANTICS = {
'R01':('工程设计蓝图','要求到实体再到冻结','<path d="M8 10h32v30H8zM13 17h15m-15 7h9m7 2 11 7-11 7zM11 46h37M44 11v12"/>'),
'R02':('双钻','发现定义与开发交付的两次发散收敛','<path d="m3 28 12-17 12 17-12 17zM27 28l12-17 12 17-12 17z"/>'),
'R03':('人本原型循环','理解人并以原型测试返回','<circle cx="19" cy="18" r="5"/><path d="M9 34q0-11 20-11M33 13q18 2 15 20m0 0-6-5m6 5 4-7M43 42q-14 9-25-1"/><rect x="30" y="29" width="12" height="13" rx="2"/>'),
'R04':('系统接口架构','系统分配及集成追溯','<rect x="4" y="8" width="46" height="40" rx="4"/><path d="M27 14v10M14 24h26M14 24v10m26-10v10"/><rect x="9" y="34" width="10" height="8"/><rect x="35" y="34" width="10" height="8"/>'),
'R05':('V模型','分解设计与分层集成相对应','<path d="m5 9 22 39L49 9M10 18h34M16 29h22M22 39h10"/>'),
'R06':('阶段门','证据活动后的关口决定','<path d="M4 28h46m-7-5 7 5-7 5M12 12v32m15-32v32m15-32v32M9 12h6m9 0h6m9 0h6"/>'),
'R07':('质量目标分布','将需求变成可测特性及稳健参数','<path d="M5 44h44M7 41c10 0 8-28 20-28s10 28 20 28M17 9v36m20-36v36M27 7v39"/>'),
'R08':('观察取证','观察事件并保留证据位置','<path d="M4 25q23-26 46 0-23 26-46 0z"/><circle cx="27" cy="25" r="7"/><path d="M14 44h26m-20 5h14"/>'),
'R09':('情境中的进步','从当前情境走向期望进步','<path d="M6 40h12V30h12V20h17m-6-5 6 5-6 5"/><circle cx="12" cy="16" r="4"/><path d="m12 20 7 8m-7-8-5 9"/>'),
'R10':('领先用户','沿趋势寻找前沿用户','<path d="M5 43 45 12m-9 0h9v9"/><circle cx="15" cy="34" r="4"/><circle cx="29" cy="23" r="4"/><path d="m43 30 2 5 6 1-4 4 1 6-5-3-5 3 1-6-4-4 6-1z"/>'),
'R11':('Kano曲线','满意度对不同特性的不同响应','<path d="M7 44h42M10 49V6M13 39q24 0 32-29M13 39l32-29M13 25q7-14 32-15"/>'),
'R12':('质量屋','需求与技术响应关系及冲突','<path d="m7 19 20-14 20 14H7v29h40V19M17 19v29m10-29v29m10-29v29M7 29h40M7 39h40"/>'),
'R13':('人与工作台','人机任务与工作系统匹配','<circle cx="17" cy="12" r="5"/><path d="m17 18-3 15h17m-17 0-5 14m8-14 7 14M17 23l13 3M29 17h20v7H29zM40 24v23"/>'),
'R14':('功能分解接口','功能分解与输入输出交接','<rect x="20" y="5" width="14" height="10"/><path d="M27 15v9M10 24h34M10 24v9m17-9v9m17-9v9"/><rect x="4" y="33" width="12" height="12"/><rect x="21" y="33" width="12" height="12"/><rect x="38" y="33" width="12" height="12"/>'),
'R15':('HOW WHY链','功能逻辑双向反读','<path d="M4 27h46m-6-5 6 5-6 5M10 22l-6 5 6 5"/><rect x="18" y="17" width="18" height="20"/><path d="M22 10h10m-10 34h10"/>'),
'R16':('因果鱼骨','多原因假设与反证','<path d="M5 28h45m-7-5 7 5-7 5M12 11l13 17-13 17M27 11l13 17-13 17"/>'),
'R17':('形态组合矩阵','按功能组合不同候选原理','<path d="M6 8h42v39H6zM20 8v39m14-39v39M6 21h42M6 34h42m-35-19 14 13 14 13"/><circle cx="13" cy="15" r="3"/><circle cx="27" cy="28" r="3"/><circle cx="41" cy="41" r="3"/>'),
'R18':('叶脉到工程','从自然策略抽象工程机制','<path d="M7 37Q5 7 31 7q1 23-24 30zm0 0L26 13m-12 13h9M33 26h14v20H33zM23 38h10m-4-4 4 4-4 4"/>'),
'R19':('概念变换卡','用提示打破既有概念固着','<rect x="6" y="13" width="23" height="31" rx="3"/><path d="m31 7 17 5-6 21M12 23h11m-6-5v10M12 36h11m13 3 4 4 8-10"/>'),
'R20':('概念知识双空间','概念分支与知识扩展往返','<path d="M5 8h17v39H5zM32 8h17v39H32zM22 20h10m-4-4 4 4-4 4M32 36H22m4-4-4 4 4 4M10 17l7 9-7 10M37 17h7m-7 10h7m-7 10h7"/>'),
'R21':('TRIZ路由','问题模型引向不同子方法','<circle cx="27" cy="12" r="6"/><path d="M27 18v9M10 27h34M10 27v14m17-14v14m17-14v14"/><circle cx="10" cy="45" r="4"/><path d="m27 40 5 9H22zM40 41h8v8h-8z"/>'),
'R22':('技术矛盾权衡','改善一项引起另一项恶化','<path d="M7 27h40M27 12v33M12 18l-7 18h14zM42 18l-7 18h14zM12 18l15-6 15 6M18 47h18"/>'),
'R23':('条件分离','相反属性按条件分开','<path d="M27 5v44M6 15h15m-5-5 5 5-5 5M48 39H33m5-5-5 5 5 5"/><circle cx="13" cy="36" r="7"/><path d="M36 9h12v12H36z"/>'),
'R24':('资源走向理想','盘点资源以实现所需作用','<path d="m27 6 7 14 15 2-11 11 3 16-14-8-14 8 3-16L5 22l15-2zM21 27h12m-6-6v12"/>'),
'R25':('物场三角','两个物质与作用场的最小模型','<circle cx="11" cy="40" r="7"/><circle cx="43" cy="40" r="7"/><path d="m27 6-6 12h9l-4 10 9-15h-9zM15 33l8-10m9 0 7 10M18 40h18"/>'),
'R26':('裁剪接替','去除载体并转移其功能','<rect x="5" y="10" width="12" height="12"/><rect x="37" y="10" width="12" height="12"/><path d="M17 16h20M27 22v24M20 27l14 14m0-14L20 41M11 22v22h32V22"/>'),
'R27':('跨域检索','一般化功能后检索与迁移','<circle cx="17" cy="19" r="11"/><path d="m25 27 9 9M32 9h15v15M38 41h12m-5-5 5 5-5 5M8 44h17"/>'),
'R28':('ARIZ回溯路径','带返回检查的问题求解','<path d="M6 9h41v10H17v10h24v11H17m0-6-7 6 7 6M6 9v15M47 19v27"/>'),
'R29':('进化分支','从发展证据生成多条路线','<path d="M7 46V9M7 40q20 0 20-15T48 8M7 40q27 0 41-17M27 25q0 15 21 15"/>'),
'R30':('独立性设计矩阵','四域映射与耦合诊断','<path d="M6 8h42v40H6zM20 8v40m14-40v40M6 21h42M6 34h42M10 13l6 5m8 8 6 5m8 8 6 5M10 27h6m22-13h6"/>'),
'R31':('DSM聚类','依赖矩阵中的模块分组','<path d="M6 6h42v42H6zM6 27h42M27 6v42M10 10h13v13H10zM31 31h13v13H31zM35 14h5m-26 26h5"/>'),
'R32':('连杆机构','拓扑自由度与连续运动','<path d="m9 41 7-26 23-4 7 30H9zM16 15l18 19 12 7"/><circle cx="9" cy="41" r="3"/><circle cx="16" cy="15" r="3"/><circle cx="39" cy="11" r="3"/><circle cx="34" cy="34" r="3"/>'),
'R33':('材料性能图','约束筛选与性能指数排序','<path d="M8 45h41M8 45V6M12 39l32-27"/><ellipse cx="19" cy="29" rx="8" ry="4" transform="rotate(-30 19 29)"/><ellipse cx="36" cy="19" rx="10" ry="5" transform="rotate(-30 36 19)"/>'),
'R34':('装配分解','零件与装配动作的合并简化','<path d="m10 11 17-6 17 6-17 6zM10 22l17 6 17-6M10 34l17 6 17-6M27 17v11m0 12v10m-5-5 5 5 5-5"/>'),
'R35':('拓扑留材','设计域内去除不必要材料','<path d="M6 8h42v39H6zM11 13l16 12 16-12M11 42l16-17 16 17M11 13v29m32-29v29"/><circle cx="27" cy="25" r="5"/>'),
'R36':('基准比较表','相对共同基准逐格比较','<path d="M6 9h42v38H6zM20 9v38m14-38v38M6 22h42M6 35h42M11 28h5m11-3v6m-3-3h6M38 39l5 5m0-5-5 5"/>'),
'R37':('多准则权重','偏好权重与候选排序敏感性','<path d="M9 9v38m18-38v38m18-38v38M5 19h8m10 15h8m10-9h8M7 50h40"/><circle cx="9" cy="19" r="4"/><circle cx="27" cy="34" r="4"/><circle cx="45" cy="25" r="4"/>'),
'R38':('响应面试验','因素组合与响应曲面','<path d="M6 40 27 49l22-12-21-9zM6 40V16m21 33V25m22 12V13M8 30q20-27 39-4M8 22q20-16 39-5M17 13q-6 15 1 31m12-31q-4 15 8 30"/>'),
'R39':('公差窗口','控制变异与允许边界','<path d="M5 44h45M13 8v36m28-36v36M7 39q8 0 12-19t9 0q5 19 19 19M18 49h18"/>'),
'R40':('失效传播','模式到影响与控制','<path d="M6 10h14v12H6zM34 32h14v12H34zM20 16h21v16M27 11l-5 12h8l-4 9 11-17h-8zM8 38l4 4 9-10"/>'),
'R41':('风险降低防护','危险识别后分层降低','<path d="m27 5 21 8v16q0 13-21 22Q6 42 6 29V13zM27 15l-10 20h20zM27 23v5m0 4v1"/>'),
'R42':('双向验证追溯','要求与证据对应及确认','<path d="M5 9h17v35H5zM33 9h17v35H33zM22 19h11m-4-4 4 4-4 4M33 35H22m4-4-4 4 4 4M9 17l3 3 6-7M37 32l3 3 6-7"/>'),
'R43':('生命周期循环','全生命周期清单与影响热点','<path d="M10 18q16-20 33 0m-1-8 1 8-8-1M45 30q-3 22-25 17m7 5-7-5 5-6M10 41Q-2 26 10 18m-8 1 8-1 1 8"/><path d="M21 26q14-12 14 3-3 10-14 5zm0 8 11-9"/>'),
'R44':('假设原型实验','用最小原型检验学习假设','<path d="M17 6h20M21 6v17L9 43q-2 5 4 5h28q6 0 4-5L33 23V6M15 35h24M23 40l3 3 7-8"/>'),
'R45':('功能成本价值','同功能替代与全寿命成本','<path d="M7 14h25l16 14-16 14H7z"/><circle cx="15" cy="28" r="3"/><path d="M24 20v16m-5-12h10m-10 8h10M4 48h43"/>'),
'R46':('专利技术景观','检索归一后建立技术路线','<path d="M7 7h27v34H7zM13 15h15m-15 7h10m-10 7h10"/><circle cx="37" cy="36" r="10"/><path d="m44 43 7 7M15 45h8"/>'),
'R47':('集合收缩','并行候选经证据逐步收缩','<ellipse cx="20" cy="26" rx="15" ry="19"/><ellipse cx="34" cy="26" rx="15" ry="19"/><path d="M25 13h4v26h-4M7 49h40"/>'),
'R48':('要求基线','原话证据到可验证要求与变更','<path d="M8 7h31v40H8zM14 16h18m-18 9h12m-12 9h12M34 32l6 6 11-14M14 42h9"/>'),
'WB01':('综合设计总览','成功条件与跨专业协调闭环','<circle cx="27" cy="27" r="9"/><rect x="21" y="3" width="12" height="9"/><rect x="3" y="36" width="12" height="9"/><rect x="39" y="36" width="12" height="9"/><path d="M27 12v6M20 32l-9 6m23-6 9 6M15 44q12 10 24 0"/>'),
'WB02':('三类调研证据','用户需求环境风险三路汇集','<circle cx="10" cy="13" r="6"/><rect x="21" y="7" width="12" height="12"/><path d="m44 7 7 12H37zM10 21v10h34V21M27 31v10"/><circle cx="27" cy="46" r="5"/>'),
'WB03':('七域总体规划','七个规划域连回总体目标','<path d="m27 5 17 8 6 18-13 17H17L4 31l6-18zM27 5v22m17-14L27 27m23 4-23-4m10 21L27 27M17 48l10-21M4 31l23-4M10 13l17 14"/>'),
'WB04':('一三X综合','功能核心三类设计及任务方法','<circle cx="27" cy="27" r="7"/><path d="M27 20V7M20 31 8 42m26-11 12 11M6 7h10v10H6zM39 6l8 8m0-8-8 8M22 44h10"/>'),
'WB05':('主辅功能','主路径与支撑作用的相容','<path d="M4 26h46m-6-5 6 5-6 5M14 10v16m13 0v19m13-35v16M9 10h10m3 35h10m3-35h10"/>'),
'WB06':('结构动态响应','运动动力模型与试验辨识','<path d="M5 37h44M6 26q5-28 10 0t10 0 10 0 10 0M11 43v6m12-6v6m12-6v6m12-6v6"/>'),
'WB07':('测量控制闭环','使用状态测量与作用链','<rect x="18" y="7" width="20" height="12"/><circle cx="28" cy="39" r="8"/><path d="M28 19v12M38 13h11v26H36M20 39H7V13h11m-5-5 5 5-5 5"/>'),
'WB08':('制造过程可视化','版本过程模型模拟到实物检查','<path d="M5 7h44v31H5zM10 31l10-13 10 9 12-15M20 38v10m14-10v10M15 48h24"/>'),
'WB09':('非线性动态分岔','深层模型参数与状态变化','<path d="M6 46h43M6 46V7M8 39h15m0 0 12-13 12-3M23 39l12 5 12 2M35 26l12-14m-12 14 12 8"/>'),
'WB10':('分层设计评价','指标证据层次与薄弱项复评','<path d="m27 5 21 40H6zM15 28h24M20 18h14M10 37h34M24 39l3 3 5-6"/>'),
'WB11':('规则解释推理','条件结论与边界冲突测试','<rect x="5" y="7" width="18" height="13"/><rect x="31" y="34" width="18" height="13"/><path d="M23 13h17v21M9 12h10m-10 4h6M10 30l9 13m0-13-9 13M36 39l3 3 6-7"/>'),
'WB12':('出处分类去重','同义层级与可撤销归并','<path d="M5 6h18v28H5zM31 6h18v28H31zM10 13h8m18 0h8M14 34v8h26v-8M27 42v8M22 46l5 4 5-4"/>'),
}

def semantic_icon(d):
    """Method-specific icon; fail closed for unmapped future methods."""
    rid=d['research_id']
    metaphor,reason,geometry=ICON_SEMANTICS[rid]
    title=escape(f"{d['name']}：{metaphor}")
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 56" '
            'role="img" aria-labelledby="icon-title icon-desc" style="max-width:100%;height:auto">'
            f'<title id="icon-title">{title}</title><desc id="icon-desc">{escape(reason)}；平台编辑视觉隐喻，非原典标识。</desc>'
            '<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            +geometry+'</g></svg>')


def dependency_svg(d):
    """Draw exactly declared dependencies. No implicit edge between display neighbors.

    Acyclic graph nodes share a rank when independent. Cycles/dangling references
    are explicitly flagged, never silently rewritten as a linear procedure.
    """
    steps=d.get('steps',[])
    ids=[s['step_id'] for s in steps]
    if len(ids)!=len(set(ids)):
        raise ValueError('Duplicate step_id cannot be drawn unambiguously')
    byid={s['step_id']:s for s in steps};ranks={};pending=set(ids)
    edges=[(dep,s['step_id']) for s in steps for dep in s.get('depends_on',[]) if dep in byid]
    unknown=[(dep,s['step_id']) for s in steps for dep in s.get('depends_on',[]) if dep not in byid]
    while pending:
        ready=[i for i in ids if i in pending and all(dep in ranks for dep in byid[i].get('depends_on',[]) if dep in byid)]
        if not ready:break
        for i in ready:
            ranks[i]=max([ranks[dep]+1 for dep in byid[i].get('depends_on',[]) if dep in ranks] or [0])
            pending.remove(i)
    cyclic=sorted(pending)
    if pending:
        rank=max(ranks.values(),default=-1)+1
        for i in ids:
            if i in pending:ranks[i]=rank;rank+=1
    groups={}
    for i in ids:groups.setdefault(ranks[i],[]).append(i)
    cols=max([len(v) for v in groups.values()]or[1]);width=max(300,cols*270+30);height=max(130,(max(ranks.values(),default=0)+1)*126+80)
    positions={i:(30+j*270,32+rank*126)for rank,g in groups.items()for j,i in enumerate(g)}
    warnings=[]
    if unknown:warnings.append('存在未找到的依赖：'+ '、'.join(a+'→'+b for a,b in unknown))
    if cyclic:warnings.append('存在环或受环阻塞的节点；布局不代表可执行次序：'+'、'.join(cyclic))
    description='仅连出档案显式depends_on；无依赖的节点为起点或独立准备。'+(' '.join(warnings))
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="dep-title dep-desc" style="width:100%;max-width:{width}px;height:auto;min-width:0"><title id="dep-title">{escape(d.get("name","方法"))}：步骤依赖图</title><desc id="dep-desc">{escape(description)}</desc><defs><marker id="dependency-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="currentColor"/></marker></defs>']
    for a,b in edges:
        x,y=positions[a];tx,ty=positions[b];x+=120;y+=86;tx+=120
        bend=(y+ty)/2
        out.append(f'<path data-from="{escape(a)}" data-to="{escape(b)}" d="M{x} {y} C{x} {bend} {tx} {bend} {tx} {ty}" fill="none" stroke="currentColor" stroke-width="1.8" marker-end="url(#dependency-arrow)"/>')
    for n,s in enumerate(steps,1):
        i=s['step_id'];x,y=positions[i];label=str(s['title']);lines=[label[k:k+12]for k in range(0,len(label),12)]
        if len(lines)>2:lines=lines[:2];lines[-1]=lines[-1][:-1]+'…'
        out.append(f'<g data-step="{escape(i)}"><title>{escape(label)}</title><rect x="{x}" y="{y}" width="240" height="86" rx="12" fill="var(--bg-surface, #fff)" stroke="currentColor" stroke-width="1.5"/><text x="{x+14}" y="{y+23}" fill="currentColor" font-size="12">{n:02} · {"独立准备 / 起点" if not s.get("depends_on") else "依赖见连线 / 说明"}</text>')
        out.append(f'<text x="{x+14}" y="{y+46}" fill="currentColor" font-size="14">'+''.join(f'<tspan x="{x+14}" dy="{0 if k==0 else 19}">{escape(t)}</tspan>'for k,t in enumerate(lines))+'</text></g>')
    if not steps:out.append('<text x="20" y="50" fill="currentColor" font-size="14">尚未记录步骤；未构造依赖。</text>')
    if warnings:out.append(f'<text x="20" y="{height-15}" fill="currentColor" font-size="11">依赖数据需检查；详情见图形说明。</text>')
    out.append('</svg>');return ''.join(out)
