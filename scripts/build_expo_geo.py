# coding: utf-8
"""129 expo 首页县级中国地图数据构建。

从阿里云 DataV GeoJSON（areas_v3）取省级与地级边界，合并为全国县级单元：
- 省文件 {adcode}_full.json 只到地级；地级文件才含区县；
- 直辖市/港澳的区在省级文件里；省直辖县级单位（如仙桃、石河子）无地级文件，
  几何回退取省级文件中的对应要素；台湾用省级轮廓补齐；
- 九段线（adcode 100000_JD）保留在省级文件，供南海诸岛插图使用。

产物（ extensions/expo/geo/ ）：
- cn-counties.json   全国县级单元（保留 centroid，坐标 3 位小数）
- cn-provinces.json  省级轮廓 + 九段线（坐标 3 位小数）

缓存：output/expo/geo-cache（gitignore，可从 DataV 重新下载）。
用法：python scripts/build_expo_geo.py [--refresh]
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'output/expo/geo-cache'
OUT = ROOT / 'extensions/expo/geo'
SRC = 'https://geo.datav.aliyun.com/areas_v3/bound/{}_full.json'

MUNI = ['110000', '120000', '310000', '500000', '810000', '820000']


def fetch(code):
    """返回 (data, definitive_empty)。

    definitive_empty=True 表示数据源明确返回"无此编码下级数据"（可解析的响应但无 features），
    调用方应回退省级几何；网络层异常才重试。
    """
    sub = CACHE if code in PROVINCE_CODES or code == '100000' else CACHE / 'city'
    path = sub / f'{code}_full.json'
    if path.exists():
        try:
            d = json.loads(path.read_text(encoding='utf-8'))
            if d.get('features'):
                return d, False
            return None, True
        except Exception:
            pass
    path.parent.mkdir(parents=True, exist_ok=True)
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(SRC.format(code), headers={'User-Agent': 'curl/8'}), timeout=15) as r:
                body = r.read().decode('utf-8', 'replace')
            try:
                d = json.loads(body)
            except ValueError:
                return None, True
            if d.get('features'):
                path.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')
                return d, False
            return None, True
        except Exception as exc:
            last = exc
        time.sleep(0.5)
    raise RuntimeError(f'下载失败 {code}: {last}')


def load_cache(name):
    return json.loads((CACHE / name).read_text(encoding='utf-8'))


def round_coords(o, n=3):
    if isinstance(o, list):
        if o and isinstance(o[0], (int, float)):
            return [round(x, n) for x in o]
        return [round_coords(x, n) for x in o]
    return o


def keep(f, level):
    p = f['properties']
    return {'type': 'Feature',
            'properties': {'adcode': p['adcode'], 'name': p.get('name', ''), 'level': level,
                           'centroid': p.get('centroid') or p.get('center')},
            'geometry': {'type': f['geometry']['type'],
                         'coordinates': round_coords(f['geometry']['coordinates'])}}


def main():
    refresh = '--refresh' in sys.argv
    if refresh:
        import shutil
        shutil.rmtree(CACHE, ignore_errors=True)
    (CACHE / 'city').mkdir(parents=True, exist_ok=True)

    national, _ = fetch('100000')
    province_codes = [str(f['properties']['adcode']) for f in national['features']
                      if len(str(f['properties']['adcode'])) == 6]
    global PROVINCE_CODES
    PROVINCE_CODES = set(province_codes)

    provinces = [keep(f, 'province') for f in national['features']
                 if len(str(f['properties']['adcode'])) == 6]
    jd = [keep(f, 'nine-dash') for f in national['features'] if str(f['properties'].get('adcode')) == '100000_JD']
    provinces += jd

    counties = []
    fallback_needed = []
    city_children = {}
    city_codes = []
    for code in province_codes:
        if code == '710000':
            continue
        d, _ = fetch(code)
        for f in d['features']:
            p = f['properties']
            if p.get('level') == 'district':
                counties.append(keep(f, 'district'))
            elif p.get('level') == 'city':
                city_codes.append(str(p['adcode']))
                city_children[str(p['adcode'])] = int(p.get('childrenNum') or 0)
    for code in city_codes:
        if city_children.get(code, 1) == 0 and not (CACHE / 'city' / f'{code}_full.json').exists():
            # 数据源声明无下级单位：直接回退省级几何，不访问网络
            fallback_needed.append(code)
            continue
        try:
            d, definitive = fetch(code)
        except RuntimeError:
            if city_children.get(code, 1) == 0:
                fallback_needed.append(code)
                continue
            raise
        if d is None:
            if definitive:
                fallback_needed.append(code)
                continue
            raise RuntimeError(f'{code} 网络层失败，中止构建（不得用省级几何冒充县级）')
        for f in d['features']:
            counties.append(keep(f, 'district'))
    # 省直辖县级单位：几何在省级文件
    hit = 0
    for code in province_codes:
        if code == '710000':
            continue
        d = load_cache(f'{code}_full.json')
        for f in d['features']:
            if str(f['properties'].get('adcode')) in fallback_needed:
                counties.append(keep(f, 'district'))
                hit += 1
    # 台湾：省级轮廓补齐
    for f in national['features']:
        if str(f['properties'].get('adcode')) == '710000':
            counties.append(keep(f, 'district'))

    OUT.mkdir(parents=True, exist_ok=True)
    cpath = OUT / 'cn-counties.json'
    ppath = OUT / 'cn-provinces.json'
    cpath.write_text(json.dumps({'type': 'FeatureCollection', 'features': counties},
                                ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    ppath.write_text(json.dumps({'type': 'FeatureCollection', 'features': provinces},
                                ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(json.dumps({
        'counties': len(counties), 'provinces': len(provinces),
        'city_files': len(city_codes), 'fallback_county_units': hit,
        'counties_bytes': cpath.stat().st_size, 'provinces_bytes': ppath.stat().st_size,
    }, ensure_ascii=False))


PROVINCE_CODES = set()

if __name__ == '__main__':
    main()
