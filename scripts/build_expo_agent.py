# coding: utf-8
"""121v3 产业创新 Agent（Deep Research 演示版）生成器：单文件离线 HTML。

数据纪律：
- 项目事实（名称/奖项/单位/摘要）生成时从项目库 catalog 读取，不手抄。
- 地方产业画像/企业/画像/需求/机会为策展数据包，页面逐处标注"公开资料整理/策展整理/研究假设"。
- 需求行沿用引擎语言：hard=null、status=proposed，不升格。
- 迁移点写"一种解/可类比"，差异与不可迁移部分必须同列。

用法：PYTHONPATH=scripts python build_expo_agent.py [--out output/expo/agent/index.html]
"""
import argparse
import base64
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import project_pipeline as pp  # noqa: E402
import project_portal  # noqa: E402

BASE_URL = 'https://haoshejiguan.com'

PLACES = {
    'yuhuan': {
        'label': '玉环',
        'headline': '浙东南制造业强市：从零部件到成套装备。',
        'intro': '阀门水暖、汽摩配、机床装备是基本盘；多家上市公司集中在精密传动、流体控制与自动化设备。',
        'sectors': ['齿轮传动', '阀门管件', '汽车减震器', '水暖阀门', '医用耗材自动化设备', '高端数控车床'],
        'drivers': ['装备国产替代与精度升级', '出口合规与海外渠道深耕', '自动化换人降本增效'],
        'summary_points': ['玉环制造业呈"精密传动+流体控制+自动化装备"三足结构，零部件强、整机弱',
                           '上市公司集中在精度与可靠性敏感环节，升级需求真实且可验证',
                           '跨域获奖机制可引入，但必须经载荷、成本、工况的差异校核'],
        'theses': [
            {'id': 'H1', 'text': '玉环升级约束集中在精度一致性与工艺数据沉淀，而非产能', 'angle': '约束识别', 'status': 'partial', 'note': '六家样本企业的痛点表述一致指向精度与工艺资产；待企业访谈确认'},
            {'id': 'H2', 'text': '获奖装备与密封类项目的机制可迁移到玉环的传动与流体控制场景', 'angle': '机制迁移', 'status': 'unknown', 'note': '跨域类比，载荷与成本差异未校核'},
        ],
        'boundary': '本研究不含金融、文旅与农业板块，聚焦制造业六个板块',
        'sources': [
            {'title': '玉环市上市公司公开资料（策展整理）', 'url': ''},
            {'title': '好设计获奖项目库（560 项，平台自有）', 'url': 'https://haoshejiguan.com/projects/'},
        ],
        'companies': [
            {'name': '双环传动', 'field': '齿轮与精密传动', 'reads': ['大规模齿轮制造，精度与寿命是生命线', '关注产线柔性与材料利用率']},
            {'name': '永和流体', 'field': '阀门管件', 'reads': ['流体控制件，密封与耐压是底线', '关注标准迭代与海外合规']},
            {'name': '正裕工业', 'field': '汽车减震器', 'reads': ['悬架减振部件，舒适与耐久兼顾', '关注阻尼一致性与疲劳寿命']},
            {'name': '万得凯', 'field': '水暖阀门', 'reads': ['水暖管路出口为主', '关注漏率、表面处理与交付稳定']},
            {'name': '迈得医疗', 'field': '医用耗材自动化设备', 'reads': ['输液器、注射器组装设备（沙门镇）', '关注洁净、视觉检测与柔性换型']},
            {'name': '浙海德曼', 'field': '高端数控车床', 'reads': ['工业母机（沙门镇）', '关注精度保持性与工艺数据沉淀']},
        ],
        'note': '公开资料整理：全市上市公司共 9 家，此处列 6 家示例；表述为策展整理，未经企业确认。',
        'chain': [
            {'tier': '上游', 'links': ['特种钢材与铜材等原材料', '铸造锻压毛坯', '密封件、轴承等功能部件', '数控系统与伺服电机']},
            {'tier': '中游', 'links': ['齿轮与传动件制造（双环传动）', '阀门管件与水暖件（永和、万得凯）', '汽车减震器（正裕工业）', '高端数控车床（浙海德曼）']},
            {'tier': '下游', 'links': ['整车厂与一级供应商', '海外水暖建材渠道', '医用耗材生产企业（迈得设备客户）', '装备使用方与技改市场']},
        ],
        'risks': ['企业信息为公开资料整理，未经企业确认', '机制关联为跨域类比，需载荷与成本差异校核', '9 家上市公司此处仅列 6 家示例，覆盖不全'],
        'personas': [
            {'name': '精密传动制造商', 'from': '以双环传动为代表', 'profile': '以齿轮为核心件，批量大、客户审厂严。',
             'pains': ['精度一致性与寿命怎么同时保', '换型频繁的产线柔性', '材料利用率与成本']},
            {'name': '阀门水暖出口商', 'from': '以永和流体、万得凯为代表', 'profile': '管路件出口为主，标准与合规密集。',
             'pains': ['密封可靠性与漏率', '海外标准快速响应', '表面处理一致性']},
            {'name': '装备与设备集成商', 'from': '以迈得医疗、浙海德曼为代表', 'profile': '卖设备也卖产线能力。',
             'pains': ['洁净/精度等硬约束', '检测误判率', '多规格柔性换型']},
        ],
        'requirements': [
            {'id': 'N1', 'text': '齿轮副精度一致性提升，同时不牺牲疲劳寿命', 'from': '精密传动画像'},
            {'id': 'N2', 'text': '小批量多规格下的快速换型与产线柔性', 'from': '精密传动画像'},
            {'id': 'N3', 'text': '高压工况下阀门密封可靠性与漏率控制', 'from': '阀门水暖画像'},
            {'id': 'N4', 'text': '出口水暖件的表面处理一致性与耐蚀', 'from': '阀门水暖画像'},
            {'id': 'N5', 'text': '减震器阻尼一致性与长寿命的平衡', 'from': '汽配画像'},
            {'id': 'N6', 'text': '耗材组装设备的视觉检测误判率下降', 'from': '装备设备画像'},
            {'id': 'N7', 'text': '数控车床精度保持与工艺数据沉淀', 'from': '装备设备画像'},
        ],
        'matches': [
            {'question': '齿轮与传动：精度和寿命怎么一起上去',
             'projects': [{'id': '2023-02', 'link': '高效率长寿命变速器的系统设计方法，可类比齿轮副精度与寿命协同',
                           'diff': '商用车工况与小型齿轮差异大，载荷谱须重新标定'}]},
            {'question': '阀门与水暖：密封可靠性怎么再进一步',
             'projects': [{'id': '2023-04', 'link': '高耐压低摩擦动密封，是密封可靠性的一种新路径',
                           'diff': '磁性液体方案成本高，民用阀门的成本边界要先算'}]},
            {'question': '减震器：阻尼一致性靠什么',
             'projects': [{'id': '2025-s02', 'link': '金属橡胶减振材料设计，为阻尼一致性提供材料级思路',
                           'diff': '特种工况材料体系，汽车量产成本与工艺须验证'}]},
            {'question': '自动化设备：多规格还要快换型',
             'projects': [{'id': '2024-s04', 'link': '一次装夹完成多工序，小批量高精的柔性范式',
                           'diff': '零件形态差异大，夹具体系不可照搬'},
                          {'id': '2025-s16', 'link': '多品种定制化智能制造，产线数据沉淀为工艺资产',
                           'diff': '压缩机品类与耗材品类节拍差异，需重新建模'}]},
        ],
        'opportunities': [
            {'title': '齿轮传动的精度跃迁', 'text': '参照金奖变速器的效率与寿命协同方法，校准本地齿轮产品的精度路线。',
             'basis': '关联：2023-02 重型商用车变速器（金奖）', 'verify': '先做载荷谱对标与样件台架对比'},
            {'title': '阀门水暖的密封升级', 'text': '评估磁性液体动密封等机制在高端管路件的适用边界。',
             'basis': '关联：2023-04 磁性液体动密封（金奖）', 'verify': '成本边界核算与台架小样'},
            {'title': '耗材设备的柔性换型', 'text': '把定制化智能制造的产线数据方法引入耗材组装设备。',
             'basis': '关联：2025-s16 定制化智能制造（银奖）', 'verify': '一条产线试点换型计时'},
        ],
    },
    'jiashan': {
        'label': '嘉善',
        'headline': '长三角接轨上海第一站：木业家居、装备制造、电子信息。',
        'intro': '从板材到成品家具的制造链，精密零部件与成套装备，电子器件与模组配套。',
        'sectors': ['智能家居与木业家居', '装备制造与精密机械', '电子信息与半导体'],
        'drivers': ['长三角一体化与上海产业外溢', '传统产业智能化改造'],
        'summary_points': ['嘉善呈"家居+装备+电子"三元结构，承接上海外溢与本地升级双重需求'],
        'theses': [
            {'id': 'H1', 'text': '嘉善的升级机会在上海外溢订单的精度门槛，而非土地与人力', 'angle': '约束识别', 'status': 'unknown', 'note': '演示示例，待真实数据核证'},
        ],
        'boundary': '演示示例：企业群表述待按嘉善实际产业数据替换',
        'sources': [{'title': '好设计获奖项目库（560 项，平台自有）', 'url': 'https://haoshejiguan.com/projects/'}],
        'chain': [
            {'tier': '上游', 'links': ['板材与木皮原料', '电子元器件与模组', '特种金属材料']},
            {'tier': '中游', 'links': ['木业家居制造', '精密零部件与成套装备', '电子器件配套']},
            {'tier': '下游', 'links': ['家居品牌与出口渠道', '装备使用方', '智能终端品牌']},
        ],
        'risks': ['画像为演示示例，待按嘉善实际产业数据替换', '机制关联为跨域类比，需差异校核'],
        'companies': [
            {'name': '木业家居企业群', 'field': '板材与成品家具', 'reads': ['从板材到成品家具的完整链条', '关注表面处理与定制化']},
            {'name': '精密机械企业群', 'field': '零部件与装备', 'reads': ['精密零部件与成套装备', '关注精度与电驱化']},
            {'name': '电子配套企业群', 'field': '器件与模组', 'reads': ['电子器件、模组与智能终端配套', '关注散热与良率']},
        ],
        'note': '演示示例画像：企业群表述待按嘉善实际产业数据替换。',
        'personas': [
            {'name': '家居制造商', 'from': '木业家居企业群', 'profile': '从板材到成品家具，向智能化与定制化升级。',
             'pains': ['表面处理与触感品质', '小批量定制柔性产线', '连接与装配工艺']},
            {'name': '精密装备商', 'from': '精密机械企业群', 'profile': '精密零部件与成套装备。',
             'pains': ['精度再上一级靠什么', '电驱化改造值不值', '产线数据变工艺资产']},
            {'name': '电子配套商', 'from': '电子配套企业群', 'profile': '电子器件、模组与智能终端配套。',
             'pains': ['芯片散热卡点', '超薄脆性材料加工', '良率背后的工艺窗口']},
        ],
        'requirements': [
            {'id': 'N1', 'text': '曲面与异型面的表面处理品质稳定', 'from': '家居画像'},
            {'id': 'N2', 'text': '小批量定制下的柔性产线与快速换型', 'from': '家居画像'},
            {'id': 'N3', 'text': '精密装备精度等级再上一级', 'from': '装备画像'},
            {'id': 'N4', 'text': '电驱化改造的效率与成本平衡', 'from': '装备画像'},
            {'id': 'N5', 'text': '高功率模组的散热能力提升', 'from': '电子画像'},
            {'id': 'N6', 'text': '超薄脆性材料的稳定加工', 'from': '电子画像'},
        ],
        'matches': [
            {'question': '家居：难加工面也要有稳定表面',
             'projects': [{'id': '2025-04', 'link': '磨料介质抛光复杂内腔，是"难加工面也有稳定表面"的一种解',
                           'diff': '金属内腔与木质曲面介质不同，磨料体系须重做'}]},
            {'question': '装备：电驱化改造的真实账本',
             'projects': [{'id': '2019-s19', 'link': '柴油驱动改电驱：效率、噪声与自动化的实测路径',
                           'diff': '压裂工况与通用装备不同，功率等级须重新匹配'}]},
            {'question': '电子：芯片散热卡在材料',
             'projects': [{'id': '2025-08', 'link': '金刚石散热材料，把芯片热问题变成材料与装备问题',
                           'diff': '雷达组件与消费级模组成本结构差异大'}]},
        ],
        'opportunities': [
            {'title': '家居表面处理的品质跃迁', 'text': '把磨料介质抛光类机制引入高端家居曲面与异型面处理。',
             'basis': '关联：2025-04 磨料介质与装备（金奖）', 'verify': '先做小样对比试验'},
            {'title': '精密机械的"电驱账"', 'text': '参照电动压裂泵的电驱替代路径，核算本地装备产品电驱化收益。',
             'basis': '关联：2019-s19 电动压裂泵（银奖）', 'verify': '选一款产品做全生命周期成本测算'},
            {'title': '电子散热的材料级答案', 'text': '高功率模组热管理，评估金刚石/复合散热路径。',
             'basis': '关联：2025-08 半导体金刚石散热（金奖）', 'verify': '热仿真与样品热阻测试'},
        ],
    },
    '_generic': {
        'label': '这个地方',
        'headline': '地方产业画像待补充，先用通用制造业结构演示。',
        'intro': '任何地方产业都可以按"板块、样本企业、典型问题"三步展开。',
        'sectors': ['基础零部件', '成套装备', '终端产品'],
        'drivers': ['产业升级需求'],
        'summary_points': ['通用演示结构，地方事实待补充'],
        'theses': [{'id': 'H1', 'text': '该地方升级约束待识别，先用通用结构演示流程', 'angle': '演示', 'status': 'unknown', 'note': '通用结构，非研究结论'}],
        'boundary': '该地方画像待补充，以上为通用演示结构',
        'sources': [],
        'chain': [
            {'tier': '上游', 'links': ['原材料与功能部件']},
            {'tier': '中游', 'links': ['零部件与装备制造']},
            {'tier': '下游', 'links': ['整机品牌与使用方']},
        ],
        'risks': ['该地方画像待补充，以上为通用演示结构'],
        'companies': [
            {'name': '零部件企业', 'field': '基础件制造', 'reads': ['关注精度与成本']},
            {'name': '装备企业', 'field': '成套设备', 'reads': ['关注可靠性与交付']},
            {'name': '终端品牌', 'field': '整机与产品', 'reads': ['关注差异化与供应链']},
        ],
        'note': '该地方画像待补充：以上为通用演示结构，产业事实不编造。',
        'personas': [
            {'name': '制造企业负责人', 'from': '通用画像', 'profile': '有订单有产线，想升级但怕走错方向。',
             'pains': ['升级方向怎么选', '投入产出怎么算', '技术从哪里来']},
        ],
        'requirements': [
            {'id': 'N1', 'text': '在成本约束下找到可验证的升级路径', 'from': '通用画像'},
        ],
        'matches': [
            {'question': '制造业通用：精度、效率、可靠性的平衡',
             'projects': [{'id': '2024-s04', 'link': '一次装夹完成多工序的柔性范式', 'diff': '需按本地零件形态重做夹具与工艺'},
                          {'id': '2025-06', 'link': '异种材料高可靠连接的系统方法', 'diff': '材料体系差异，需小样验证'}]},
        ],
        'opportunities': [
            {'title': '先跑一遍真实研究流程', 'text': '把地方产业问题带进需求研究工作台，用真实获奖项目做机制检索与验证规划。',
             'basis': '关联：好设计需求研究与创新设计大模型', 'verify': '一次完整的需求研究简报'},
        ],
    },
}

REQUIRED_IDS = {pid for place in PLACES.values() for g in place['matches'] for ref in g['projects'] for pid in [ref['id']]}


def image_data(source, max_px):
    from PIL import Image
    image = Image.open(source)
    image.thumbnail((max_px, max_px))
    buf = io.BytesIO()
    image.save(buf, format='WEBP', quality=80, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()


def cover_data(path):
    if not path:
        return ''
    source = ROOT / 'extensions/project-portal' / path
    return image_data(source, 480) if source.is_file() else ''


def ip_logo():
    png = ROOT / 'extensions/design-system/xiaohao-bot-20261115.png'
    if png.is_file():
        return image_data(png, 256)
    path = ROOT / 'extensions/design-system/ip-xiaohao.svg'
    return 'data:image/svg+xml;base64,' + base64.b64encode(path.read_bytes()).decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=str(ROOT / 'output/expo/agent/index.html'))
    args = parser.parse_args()

    catalog = {p['id']: p for p in project_portal.catalog(pp.LIB)}
    projects = {}
    for pid in sorted(REQUIRED_IDS):
        p = catalog[pid]
        projects[pid] = {'name': p['name'], 'award': p['award'], 'unit': p['unit'],
                         'summary': p['summary'], 'research': bool(p['research']),
                         'cover': cover_data(p.get('cover'))}
    team_avatars = {}
    for key in ('coordinator', 'poti', 'scout', 'chain', 'verify', 'seeker', 'synth', 'writer'):
        path = ROOT / 'extensions/design-system/team-20261115' / f'{key}.png'
        if path.is_file():
            team_avatars[key] = image_data(path, 192)
    data = {
        'places': PLACES,
        'projects': projects,
        'team_avatars': team_avatars,
        'stats': {'projects': len(catalog), 'research': sum(1 for p in catalog.values() if p['research'])},
        'ip_logo': ip_logo(),
        'admin': json.loads((ROOT / 'extensions/expo/geo/admin.json').read_text(encoding='utf-8')),
        'engine_sample': {'requirements': 15, 'functions': 7, 'options': 28, 'combinations': 4, 'judgments': 60},
    }
    template = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
    qr_lib = (ROOT / 'original-app/public/vendor/qrcode.min.js').read_text(encoding='utf-8')
    html = template.replace('/*__EXPO_QR_LIB__*/', qr_lib)
    html = html.replace('/*__EXPO_AGENT_DATA__*/', json.dumps(data, ensure_ascii=False))
    from immersive_chrome import wrap
    html = wrap(html, 'expo')
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError(f'演示应用不可覆盖: {out}')
    out.write_text(html, encoding='utf-8')
    geo = []
    geo_src = ROOT / 'extensions/expo/geo'
    geo_dst = out.parent / 'geo'
    if geo_src.is_dir():
        import shutil
        if geo_dst.exists():
            shutil.rmtree(geo_dst)
        shutil.copytree(geo_src, geo_dst)
        geo = sorted(p.name for p in geo_dst.iterdir())
    print(json.dumps({'out': str(out), 'bytes': out.stat().st_size, 'geo': geo,
                      'places': sorted(PLACES), 'projects_used': sorted(projects)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
