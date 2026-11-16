# coding: utf-8
"""147 由已缓存 DataV 数据构建县级行政区身份，不访问网络。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'output/expo/geo-cache'
GEO = ROOT / 'extensions/expo/geo'


def short_name(name):
    return re.sub(r'(自治县|自治旗|林区|特区|地区|省|市|区|县|旗)$', '', name)


def main():
    national = json.loads((CACHE / '100000_full.json').read_text(encoding='utf-8'))
    provinces = {str(f['properties']['adcode'])[:2]: f['properties']['name']
                 for f in national['features'] if len(str(f['properties'].get('adcode', ''))) == 6}
    cities = {}
    for code in provinces:
        path = CACHE / f'{code}0000_full.json'
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            continue
        for feature in data.get('features', []):
            p = feature['properties']
            if p.get('level') == 'city':
                cities[str(p['adcode'])] = p['name']
    counties = json.loads((GEO / 'cn-counties.json').read_text(encoding='utf-8'))
    admin = {}
    for feature in counties['features']:
        p = feature['properties']
        code = str(p['adcode'])
        province = provinces.get(code[:2], '')
        city = cities.get(code[:4] + '00', '')
        label = (city or province) + p['name']
        admin[code] = {'name': p['name'], 'short': short_name(p['name']),
                       'province': province, 'city': city, 'label': label}
    out = GEO / 'admin.json'
    out.write_text(json.dumps(admin, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(json.dumps({'entries': len(admin), 'cities': len(cities), 'hangzhou': admin['330106'],
                      'nanchang': admin['360103'], 'bytes': out.stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    main()
