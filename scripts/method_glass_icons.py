"""GoodDesign B / optical frosted glass. Native vector art, no raster wrappers.

Each stable method ID has an editorial visual metaphor. These are interface
illustrations, not original authors' marks or evidence of method validation.
"""
from html import escape

VERSION = 'glass-b-20261116'
DEFS = '''<defs>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#faf8ff" stop-opacity=".96"/><stop offset=".24" stop-color="#d6c4ff" stop-opacity=".88"/><stop offset=".61" stop-color="#b5b8f2" stop-opacity=".82"/><stop offset="1" stop-color="#91e3eb" stop-opacity=".95"/></linearGradient>
<linearGradient id="mint" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f0fffd" stop-opacity=".98"/><stop offset=".37" stop-color="#b1ebe7" stop-opacity=".87"/><stop offset="1" stop-color="#7cc4da" stop-opacity=".98"/></linearGradient>
<linearGradient id="violet" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#cbb6ff"/><stop offset=".5" stop-color="#9574df"/><stop offset="1" stop-color="#6552b3"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff" stop-opacity=".98"/><stop offset=".46" stop-color="#eeeaff" stop-opacity=".8"/><stop offset="1" stop-color="#7dcddb" stop-opacity=".95"/></linearGradient>
<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b7a0e9" stop-opacity=".7"/><stop offset=".55" stop-color="#82bdcb" stop-opacity=".75"/><stop offset="1" stop-color="#c4c0f2"/></linearGradient>
<radialGradient id="lens" cx=".3" cy=".2" r=".95"><stop stop-color="#fff" stop-opacity=".92"/><stop offset=".45" stop-color="#d8d0f6" stop-opacity=".7"/><stop offset="1" stop-color="#a4dce3" stop-opacity=".88"/></radialGradient>
<filter id="shadow" x="-40%" y="-40%" width="190%" height="200%" color-interpolation-filters="sRGB"><feDropShadow dx="0" dy="2.2" stdDeviation="1.8" flood-color="#443965" flood-opacity=".17"/></filter>
</defs>'''


def glass(shape, tone='glass'):
    return ('<g filter="url(#shadow)">'
            '<g transform="translate(.6 1.3)" fill="url(#rim)" stroke="#8e9fc8" stroke-opacity=".38" stroke-width="1.2">'+shape+'</g>'
            '<g fill="url(#'+tone+')" stroke="url(#edge)" stroke-width="1.05" stroke-linejoin="round">'+shape+'</g></g>')


def path(d, tone='glass'):
    return glass('<path d="'+d+'"/>',tone)


def plate(x,y,w,h,r=4,tone='glass'):
    return glass(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>',tone)


def orb(x,y,r,tone='lens'):
    return glass(f'<circle cx="{x}" cy="{y}" r="{r}"/>',tone)


def tube(d,w=3,tone='violet'):
    return (f'<path d="{d}" fill="none" stroke="#859cbf" stroke-opacity=".20" stroke-width="{w+1.5}" stroke-linecap="round" stroke-linejoin="round" transform="translate(.5 1)"/>'
            f'<path d="{d}" fill="none" stroke="url(#{tone})" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width=".65" stroke-linecap="round" stroke-linejoin="round" transform="translate(-.35 -.65)"/>')


def cube(x,y,s=18,tone='glass'):
    d=s*.34
    return path(f'M{x} {y+d}l{s/2} {-d} {s/2} {d}v{s*.72}l{-s/2} {d} {-s/2} {-d}z',tone)+tube(f'M{x} {y+d}l{s/2} {d} {s/2} {-d}m{-s/2} {d}v{s*.72}',.85,'edge')


def sheet(x=13,y=7,w=35,h=46):
    return path(f'M{x+4} {y}h{w-14}l10 10v{h-14}q0 4-4 4h{-w+8}q-4 0-4-4v{-h+8}q0-4 4-4z')+path(f'M{x+w-10} {y}v7q0 3 3 3h7','mint')


def check(x=26,y=36):
    return tube(f'M{x-6} {y}l5 5 11-12',4)


def arrow(d,w=3):
    return tube(d,w)


def matrix(x=9,y=10,n=3,cell=13):
    return ''.join(plate(x+i*cell,y+j*cell,cell-2,cell-2,2.5,'mint' if (i+j)%3==1 else 'glass') for j in range(n) for i in range(n))


def ring(cx,cy,r,width=5):
    return path(f'M{cx-r} {cy}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 {-2*r} 0M{cx-r+width} {cy}a{r-width} {r-width} 0 1 1 {2*(r-width)} 0a{r-width} {r-width} 0 1 1 {-2*(r-width)} 0','glass').replace('<path d=', '<path fill-rule="evenodd" d=')


def bars():
    return plate(12,31,9,21,3)+plate(27,21,9,31,3,'mint')+plate(42,10,9,42,3)


def tree():
    return tube('M32 19v11M13 30h38M13 30v12m19-12v12m19-12v12',2.3)+plate(23,7,18,14,4)+plate(5,42,16,13,4,'mint')+plate(24,42,16,13,4)+plate(43,42,16,13,4,'mint')


def lens():
    return orb(27,26,18)+ring(27,26,18,3.5)+tube('M40 40l14 14',7,'mint')


# New silhouettes, not a restyling of the old line geometry.
ART = {
'R01': ('工程蓝图与实体', lambda: sheet(10,7,35,44)+tube('M17 19h16m-16 7h10',2.3)+cube(32,31,23,'mint')),
'R02': ('两次发散收敛', lambda: path('M3 31 17 10 31 31 17 52z')+path('M31 31 45 10 59 31 45 52z','mint')+tube('M17 19v24M45 19v24',1,'edge')),
'R03': ('人与原型迭代', lambda: ring(32,31,24,5)+orb(24,23,7)+path('M12 45v-4q0-10 12-10t12 10v4z','mint')+plate(39,29,17,22,4)+tube('M47 10l6 8-10 1',3)),
'R04': ('分层系统与接口', lambda: plate(6,7,52,48,9)+tube('M32 25v9M18 34h28M18 34v8m28-8v8',2.2)+plate(24,14,16,12,3,'mint')+plate(12,42,14,9,3,'violet')+plate(39,42,14,9,3,'mint')),
'R05': ('V形对应验证', lambda: path('M6 10h9l17 31L49 10h9L32 57z')+tube('M18 22h28M24 34h16',2,'mint')+orb(11,13,4,'violet')+orb(53,13,4,'mint')),
'R06': ('阶段证据关口', lambda: tube('M5 33h53m-7-6 7 6-7 6',3)+plate(12,12,7,40,3)+plate(28,12,7,40,3,'mint')+plate(44,12,7,40,3)+orb(31.5,33,4,'violet')),
'R07': ('受控质量分布', lambda: path('M7 51C19 51 18 12 32 12S45 51 57 51z')+tube('M7 53h50M20 14v40M45 14v40',2,'mint')+tube('M32 8v44',2.4)),
'R08': ('观察与证据镜头', lambda: path('M3 30Q32 2 61 30Q32 58 3 30z')+orb(32,30,12,'mint')+orb(32,30,6,'violet')+tube('M18 53h28',2.3,'mint')),
'R09': ('情境到期望进步', lambda: path('M7 54V40h14V28h14V16h20v38z')+orb(16,14,6,'mint')+tube('M9 30l9-6 8 5M41 9h13v13',3)),
'R10': ('前沿用户与趋势', lambda: tube('M9 53 48 12m-12 0h12v12',4,'mint')+orb(16,43,6)+orb(33,29,6)+orb(49,12,7,'violet')),
'R11': ('不同满意度响应', lambda: plate(7,7,50,49,7)+tube('M15 46V17m0 29h35',2,'mint')+tube('M19 42q23 0 30-26',3)+tube('M19 42l30-26',2.2,'mint')+tube('M19 29q5-13 30-13',2,'edge')),
'R12': ('需求技术质量屋', lambda: path('M6 24 32 5 58 24v30H6z')+plate(12,27,40,22,3,'mint')+tube('M25 28v20m14-20v20M13 38h38',1.5)+orb(32,19,4,'violet')),
'R13': ('人与操作台匹配', lambda: orb(21,14,7)+path('M14 25q8-7 15 0l5 14H14z')+plate(33,21,24,9,3,'mint')+tube('M45 31v23M17 40l-6 14m15-14 7 14M26 27l12 5',3)),
'R14': ('功能接口树', tree),
'R15': ('双向功能逻辑', lambda: plate(21,16,23,33,6)+tube('M5 24h14m-6-6 6 6-6 6M59 41H46m6-6-6 6 6 6',3,'mint')+tube('M27 27h11m-11 9h7',2)),
'R16': ('因果鱼骨', lambda: tube('M5 34h50m-6-6 6 6-6 6',4,'mint')+tube('M14 12l16 22-16 20M33 12l16 22-16 20',5)+orb(15,12,4)+orb(15,54,4,'mint')),
'R17': ('候选原理组合矩阵', lambda: matrix()+tube('M14.5 15.5l13 13 13 13',2.5)+orb(14.5,15.5,3,'violet')+orb(27.5,28.5,3,'violet')+orb(40.5,41.5,3,'violet')),
'R18': ('叶片策略到工程', lambda: path('M10 39Q5 6 37 7Q39 35 10 39z','mint')+tube('M11 39 31 14m-11 12h9',2.1)+cube(35,35,21)+tube('M13 48h17m-5-4 5 4-5 4',2.4)),
'R19': ('启发与概念变换', lambda: plate(25,7,27,38,5,'mint')+plate(10,17,28,39,5)+tube('M18 31h12m-6-6v12',3)+orb(46,48,8,'violet')+tube('M42 48l3 3 5-6',1.7,'edge')),
'R20': ('概念知识双空间', lambda: plate(5,9,23,45,6)+plate(36,9,23,45,6,'mint')+tube('M16 21v19m0-9 6-7m-6 7 6 7',2.1)+tube('M42 22h10m-10 9h10m-10 9h7',2.1)+tube('M25 25h14m-4-4 4 4-4 4M39 42H25m4-4-4 4 4 4',2.4)),
'R21': ('TRIZ方法路由', lambda: tube('M32 19v13M12 32h40M12 32v10m20-10v10m20-10v10',2.3)+orb(32,12,9)+orb(12,48,7,'mint')+path('M32 41l8 14H24z')+plate(45,41,14,14,3,'mint')),
'R22': ('技术矛盾天平', lambda: tube('M32 13v41M13 22l19-9 19 9M22 55h20',3)+path('M13 22 3 42h20z','mint')+path('M51 22 41 42h20z')+orb(32,13,4,'violet')),
'R23': ('相反属性条件分离', lambda: path('M30 7v50Q7 53 7 32T30 7z')+path('M35 7v50q23-4 23-25T35 7z','mint')+tube('M15 22h7m-3-3 3 3-3 3M50 42h-7m3-3-3 3 3 3',2.4)),
'R24': ('理想目标与可用资源', lambda: ring(32,31,23,6)+orb(32,31,12,'mint')+orb(32,31,5,'violet')+tube('M32 4v7M5 31h7M52 31h7M32 52v7',2)),
'R25': ('物质与作用场', lambda: tube('M16 46 32 16 49 46H16',2.5,'mint')+orb(15,47,10)+orb(49,47,10,'mint')+path('M31 5 22 22h10l-3 12 16-21H34l3-8z','violet')),
'R26': ('裁剪后的功能接替', lambda: tube('M17 17h30M17 17v34h30V17',2.4,'mint')+cube(7,6,18)+cube(39,6,18,'mint')+plate(24,38,16,17,4)+tube('M26 27l12 12m0-12L26 39',3)),
'R27': ('科学效应跨域检索', lambda: cube(38,7,18,'mint')+tube('M40 46h16m-6-5 6 5-6 5',2.8)+lens()+orb(25,24,5,'violet')),
'R28': ('回溯式问题求解', lambda: path('M9 8h46v13H22v11h25v13H22v11L6 40l16-16v9h14v-2H9z')+orb(48,14,4,'mint')),
'R29': ('技术进化多分支', lambda: tube('M8 54V10M9 49q20 0 23-22T56 7M30 32q8-3 25-3M31 30q0 18 24 20',4,'mint')+orb(55,8,6)+orb(55,29,6,'mint')+orb(55,50,6)),
'R30': ('独立性与耦合矩阵', lambda: matrix(9,9,3,15)+orb(15.5,15.5,3,'violet')+orb(30.5,30.5,3,'violet')+orb(45.5,45.5,3,'violet')+tube('M27 15h7',1.8,'violet')),
'R31': ('依赖与模块聚类', lambda: plate(7,7,50,50,7)+plate(12,12,21,21,4)+plate(33,33,19,19,4,'mint')+tube('M39 19h9M18 43h8',2.4)+orb(42,24,3,'violet')),
'R32': ('连杆与运动副', lambda: tube('M11 48 18 14 45 10 54 49H11m7-34 21 27 15 7',6,'mint')+orb(11,48,6)+orb(18,14,6)+orb(45,10,6)+orb(39,41,5,'violet')),
'R33': ('材料性能筛选', lambda: plate(7,8,49,47,7)+tube('M15 16v30h34',2)+glass('<ellipse cx="26" cy="33" rx="10" ry="5.5" transform="rotate(-33 26 33)"/>','mint')+glass('<ellipse cx="42" cy="22" rx="11" ry="6" transform="rotate(-33 42 22)"/>')+tube('M17 43 47 15',1.7)),
'R34': ('装配层次简化', lambda: path('M8 14 32 6 56 14 32 23z')+path('M8 29 32 21 56 29 32 38z','mint')+path('M8 44 32 36 56 44 32 53z')+tube('M32 15v33m-5-5 5 5 5-5',2.1)),
'R35': ('拓扑材料保留', lambda: path('M8 10h48v44H8zM18 19v25l13-13zm28 0L33 31l13 13zM22 46h20L32 35z').replace('<path d=','<path fill-rule="evenodd" d=')+orb(32,31,5,'mint')),
'R36': ('共同基准比较', lambda: plate(7,8,50,48,7)+tube('M24 16v33M13 27h37m-37 12h37',1.6,'mint')+tube('M33 19h9m-5-4v8M13 33h5M34 46l7 7m0-7-7 7',2.2)),
'R37': ('多准则调节权重', lambda: tube('M15 9v46M32 9v46M49 9v46',3,'mint')+plate(8,18,14,9,4)+plate(25,37,14,9,4)+plate(42,25,14,9,4)+orb(15,22.5,2.2,'violet')),
'R38': ('试验设计响应曲面', lambda: path('M7 40 32 54 57 40 32 25z','mint')+path('M8 34Q20 4 34 19T56 20v19L32 51 8 39z')+tube('M15 34q17-22 36-8M18 41q18-19 32-11M24 19l5 27M38 22l4 19',1.2,'edge')),
'R39': ('参数稳健与公差', lambda: plate(7,8,50,47,7)+tube('M18 15v34M46 15v34',2.5,'mint')+path('M13 47q11 0 14-21t10 0q4 21 14 21z')+tube('M23 53h19',2)),
'R40': ('失效传播与控制', lambda: tube('M20 17h25v27',2.7,'mint')+plate(6,6,22,22,6)+plate(35,36,23,23,6,'mint')+path('M31 20 23 34h8l-3 10 14-18h-9l2-6z','violet')+tube('M9 47l5 5 8-9',3)),
'R41': ('分层风险防护', lambda: path('M32 5 56 14v18q0 17-24 27Q8 49 8 32V14z')+path('M32 17 18 43h28z','mint')+tube('M32 25v9m0 5v1',3)),
'R42': ('要求证据双向追溯', lambda: plate(5,9,22,44,5)+plate(37,9,22,44,5,'mint')+tube('M22 24h20m-5-5 5 5-5 5M42 41H22m5-5-5 5 5 5',2.7)+tube('M11 17l3 3 7-8M43 46l3 3 7-8',2.1)),
'R43': ('生命周期循环', lambda: ring(32,32,24,6)+path('M23 40q-9-23 18-22 5 26-18 22z','mint')+tube('M23 40 36 25',2)+path('M46 8 58 10 52 20z','violet')+path('M17 53 5 51 11 41z','violet')),
'R44': ('原型假设实验', lambda: path('M24 7h16v20l15 25q2 5-4 5H13q-6 0-4-5l15-25z')+path('M19 39h26l8 14H11z','mint')+tube('M21 7h22',3)+check(32,45)),
'R45': ('功能与成本价值', lambda: path('M7 15h29l22 17-22 18H7z')+orb(17,32,4,'mint')+tube('M31 23v18m-6-13h13m-13 8h13',2.7)+tube('M10 57h41',2,'mint')),
'R46': ('专利证据景观', lambda: sheet(8,6,34,43)+tube('M15 18h15m-15 8h11m-11 8h8',2.2)+orb(43,42,13,'mint')+tube('M52 51l7 7',5)+tube('M37 42l4 4 8-10',2.3)),
'R47': ('并行候选收敛', lambda: glass('<ellipse cx="24" cy="31" rx="17" ry="24"/>')+glass('<ellipse cx="41" cy="31" rx="17" ry="24"/>','mint')+path('M32 10q17 21 0 43-17-22 0-43z')+tube('M26 32l5 5 8-10',2.3)),
'R48': ('可验证要求基线', lambda: sheet()+tube('M20 18h17m-17 9h11m-11 9h8',2.4)+orb(46,45,12,'mint')+check(46,45)),
'WB01': ('综合设计协调闭环', lambda: ring(32,32,23,4)+orb(32,32,12)+cube(24,2,16,'mint')+cube(3,39,16)+cube(45,39,16,'mint')+orb(32,32,4,'violet')),
'WB02': ('三类调研汇集', lambda: tube('M12 22v12h40V22M32 34v10',2.5)+orb(12,15,8,'mint')+plate(25,7,15,16,4)+path('M52 6 62 23H42z','mint')+orb(32,51,9)),
'WB03': ('七域总体规划', lambda: path('M32 4 51 13 59 34 44 55H20L5 34l8-21z')+tube('M32 4v28m19-19L32 32m27 2-27-2m12 23L32 32M20 55l12-23M5 34l27-2M13 13l19 19',1.7,'mint')+orb(32,32,7,'violet')),
'WB04': ('一核三域多方法', lambda: tube('M32 28V11M25 36 11 49m28-13 14 13',3,'mint')+orb(32,32,11)+cube(24,2,15,'mint')+cube(3,44,15)+cube(46,44,15,'mint')+orb(32,32,3,'violet')),
'WB05': ('主辅功能相容', lambda: tube('M4 31h55m-8-8 8 8-8 8',6)+plate(11,9,14,13,4,'mint')+plate(28,43,14,13,4,'mint')+plate(44,9,14,13,4)+tube('M18 22v9m17 0v12m16-21v9',2.7,'mint')),
'WB06': ('结构动态响应', lambda: plate(6,9,52,44,7)+tube('M13 32q5-27 10 0t10 0 10 0 10 0',3,'mint')+tube('M13 46h38',2)+orb(33,32,4,'violet')),
'WB07': ('测量控制闭环', lambda: tube('M20 15H9v31h16m13 0h17V15H41',3,'mint')+plate(21,5,22,18,5)+orb(32,45,12)+tube('M32 23v10',3)+tube('M32 45l6-6',2.2)+orb(32,45,3,'violet')),
'WB08': ('制造过程可视化', lambda: plate(5,7,54,39,7)+plate(10,12,44,28,4,'mint')+tube('M16 32l10-12 10 8 12-13',3)+tube('M25 47v10m14-10v10M19 58h26',3,'mint')),
'WB09': ('深层动态分岔', lambda: plate(7,7,50,49,7)+tube('M14 15v32h36',2,'mint')+tube('M15 40h14m0 0 10-12 12-4M29 40l10 5 12 3M39 28l12-13m-12 13 12 8',2.8)+orb(29,40,3,'mint')),
'WB10': ('分层设计质量评价', lambda: path('M32 5 59 55H5z')+tube('M15 39h34M21 28h22M27 17h10',2,'mint')+orb(33,47,9,'mint')+tube('M28 47l4 4 7-9',2.2)),
'WB11': ('规则推理与边界', lambda: tube('M23 17h23v24',3,'mint')+plate(5,5,27,24,6)+plate(33,35,27,24,6,'mint')+tube('M12 13h13m-13 7h8M39 47l4 4 10-11',2.4)+tube('M9 41l11 13m0-13L9 54',3)),
'WB12': ('分类与来源去重', lambda: plate(5,6,22,34,5)+plate(37,6,22,34,5,'mint')+tube('M12 16h9m-9 8h7M43 16h9m-9 8h7',2.1)+tube('M16 41v8h32v-8M32 49v10m-5-5 5 5 5-5',2.7)),
'R49': ('功能行为结构映射', lambda: tube('M18 31h30',3,'mint')+plate(3,19,17,25,5)+orb(32,31,11,'mint')+cube(44,18,18)+tube('M50 49q-19 15-36 0',2.1)),
'R50': ('服务前台后台泳道', lambda: plate(6,7,52,49,8)+tube('M12 22h40M12 39h40',2,'mint')+tube('M16 16 32 30 48 47',2.4)+orb(16,16,5,'violet')+orb(32,30,5,'mint')+orb(48,47,5,'violet')),
'R51': ('控制约束与反馈', lambda: plate(19,5,27,17,5)+plate(19,42,27,17,5,'mint')+tube('M26 23v17m-4-5 4 5 4-5M40 42V24m-4 5 4-5 4 5',2.7)+path('M9 22 17 32 9 42 1 32z')),
'R52': ('信息驱动决策分支', lambda: tube('M17 32h13m0 0L48 13M30 32l18 19',3)+orb(11,32,9)+orb(50,13,9,'mint')+orb(50,51,9,'mint')+tube('M32 7v12m-5-6h10',2.7)),
}


def icon(d):
    rid = d['research_id']
    if rid not in ART:
        raise ValueError('Unmapped method icon: '+rid)
    metaphor, draw = ART[rid]
    label = escape(d['name']+'：'+metaphor)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-labelledby="title desc" data-style="'+VERSION+'">'
            '<title id="title">'+label+'</title><desc id="desc">光学磨砂玻璃编辑示意；非原典标识，不表示方法质量或工程认证。</desc>'+DEFS+draw()+'</svg>')
