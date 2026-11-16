# coding: utf-8
"""121 嘉善展厅演示应用生成器：单文件离线 HTML（内联样式/脚本/数据）。

数据纪律：
- 项目事实（名称/奖项/单位/摘要/封面）全部来自项目库 catalog，生成时读取，不手抄。
- 嘉善产业画像为演示示例，可换数据文件复用到其他场地。
- 机会方向卡一律标注"研究假设 · 未经验证"。
- 引擎数字来自 098/108 割胶固定样例（15/7/28/4/60），与规格一致。

用法：PYTHONPATH=scripts python build_expo_jiashan.py [--out output/expo/jiashan/index.html]
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

# 产业画像（演示示例，可按场地替换）。机制关联点为策展表述，项目事实以库内为准。
INDUSTRIES = [
    {
        'id': 'furniture',
        'name': '智能家居与木业家居',
        'scene': '从板材到成品家具的制造链，向智能化、定制化升级',
        'questions': ['表面处理与触感品质如何稳定', '小批量定制的柔性产线怎么建', '连接与装配工艺如何简化'],
        'projects': [
            {'id': '2025-04', 'link': '复杂内腔的磨料介质抛光，是"难加工面也有稳定表面"的一种解'},
            {'id': '2024-s04', 'link': '一次装夹完成多工序，是小批量高精零件的柔性范式'},
            {'id': '2025-06', 'link': '异种材料的高可靠连接思路，可类比板材与五金的结合'},
        ],
    },
    {
        'id': 'machinery',
        'name': '装备制造与精密机械',
        'scene': '精密零部件、成套装备与自动化产线',
        'questions': ['精度再往上走一级靠什么', '电驱化改造值不值', '产线数据怎么变成工艺资产'],
        'projects': [
            {'id': '2025-e02', 'link': '纳米级精度的工业母机，回答"精度再上一级靠什么"'},
            {'id': '2019-s19', 'link': '柴油驱动改电驱的真实账本：效率、噪声与自动化'},
            {'id': '2024-s05', 'link': '复杂构件的高精高效加工，把工艺沉淀进机床'},
        ],
    },
    {
        'id': 'electronics',
        'name': '电子信息与半导体',
        'scene': '电子器件、模组与智能终端配套',
        'questions': ['芯片散热卡在哪里', '超薄脆性材料怎么加工', '良率背后的工艺窗口怎么找'],
        'projects': [
            {'id': '2025-08', 'link': '金刚石散热材料，把芯片热问题变成材料与装备问题'},
            {'id': '2025-02', 'link': '减薄到 10μm 以下还要全局均匀，是三维集成的硬功夫'},
            {'id': '2025-01', 'link': '光热力协同加工超薄玻璃，脆性材料也能稳定成形的思路'},
        ],
    },
]

OPPORTUNITIES = [
    {'title': '家居表面处理的品质跃迁', 'text': '把磨料介质抛光类机制引入高端家居的曲面与异型面处理，先做小样验证。',
     'basis': '关联：2025-04 磨料介质与装备（金奖）'},
    {'title': '精密机械的"电驱账"', 'text': '参照电动压裂泵的电驱替代路径，核算本地装备产品的电驱化收益与自动化空间。',
     'basis': '关联：2019-s19 6000HP 电动压裂泵（银奖，有研究整理版）'},
    {'title': '电子散热的材料级答案', 'text': '高功率模组的热管理，评估金刚石/复合散热路径与本地配套可能。',
     'basis': '关联：2025-08 半导体金刚石散热（金奖，有研究整理版）'},
]

PIPELINE = [
    ('S1', '把问题说准', '15 项真实需求，硬软属性和未知原样保留'),
    ('S2', '拆成功能', '7 个动词加对象的功能与接口'),
    ('S3', '找相似案例', '从 560 个获奖项目里检索，命中不等于可迁移'),
    ('S5', '双侧映射', '能说清差异和不可迁移部分才算类比'),
    ('S6', '长概念', '28 个功能选项，基线方案必须在内'),
    ('S7', '组合与修剪', '4 个组合方案，理论空间不等于已研究'),
    ('S8', '验证才下结论', '60 格判断全是未知时，推荐就是空集'),
]

ATTRACT_PROJECTS = ['2025-00', '2017-01', '2021-00']
HERO = '2025-00'


def cover_data_url(name):
    if not name:
        return ''
    path = ROOT / 'extensions/project-portal/covers' / name
    if not path.is_file():
        return ''
    return 'data:image/jpeg;base64,' + base64.b64encode(path.read_bytes()).decode()


def qr_data_url(text, box=6):
    import qrcode
    img = qrcode.make(text, box_size=box, border=2)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=str(ROOT / 'output/expo/jiashan/index.html'))
    args = parser.parse_args()

    catalog = {p['id']: p for p in project_portal.catalog(pp.LIB)}
    for ind in INDUSTRIES:
        for ref in ind['projects']:
            p = catalog[ref['id']]
            ref['name'] = p['name']
            ref['award'] = p['award']
            ref['unit'] = p['unit']
            ref['summary'] = p['summary']
            ref['cover'] = p['cover'].rsplit('/', 1)[-1] if p['cover'] else ''
            ref['research'] = bool(p['research'])
    attract = []
    for pid in ATTRACT_PROJECTS:
        p = catalog[pid]
        attract.append({'id': pid, 'name': p['name'], 'award': p['award'], 'summary': p['summary'], 'cover': p['cover'].rsplit('/', 1)[-1] if p['cover'] else ''})
    stats = {
        'projects': len(catalog),
        'covers': sum(1 for p in catalog.values() if p['cover']),
        'research': sum(1 for p in catalog.values() if p['research']),
        'awards': len({p['award'] for p in catalog.values()}),
    }
    hero = catalog[HERO]
    for ind in INDUSTRIES:
        for ref in ind['projects']:
            ref['cover_url'] = cover_data_url(ref['cover'])
    for item in attract:
        item['cover_url'] = cover_data_url(item['cover'])
    data = {
        'base_url': BASE_URL,
        'venue': '嘉善展厅 · 测试场',
        'stats': stats,
        'hero': {'id': hero['id'], 'name': hero['name'], 'award': hero['award'], 'summary': hero['summary'], 'cover': hero['cover'], 'unit': hero['unit']},
        'attract': attract,
        'industries': INDUSTRIES,
        'opportunities': OPPORTUNITIES,
        'pipeline': PIPELINE,
        'engine_sample': {'requirements': 15, 'functions': 7, 'options': 28, 'combinations': 4, 'judgments': 60, 'recommendations': 0,
                           'case': '割胶机器人末端与作业流程创新研究（GD-CRE-0.1 固定样例）'},
        'qr_home': qr_data_url(BASE_URL + '/'),
        'qr_projects': qr_data_url(BASE_URL + '/projects/'),
        'qr_museum': qr_data_url(BASE_URL + '/museum/'),
    }
    html = render(data)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError(f'演示应用不可覆盖: {out}')
    out.write_text(html, encoding='utf-8')
    print(json.dumps({'out': str(out), 'bytes': out.stat().st_size,
                      'industries': len(INDUSTRIES), 'opportunities': len(OPPORTUNITIES)}, ensure_ascii=False))


def render(data):
    template = (ROOT / 'extensions/expo/expo-template.html').read_text(encoding='utf-8')
    return template.replace('/*__EXPO_DATA__*/', json.dumps(data, ensure_ascii=False))


if __name__ == '__main__':
    main()
