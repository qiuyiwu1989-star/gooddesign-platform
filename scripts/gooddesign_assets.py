from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'tokens.css': ROOT / 'extensions/method-workbench/vendor/tokens.css',
    'design-system.css': ROOT / 'extensions/method-workbench/vendor/design-system.css',
    'gooddesign.css': ROOT / 'extensions/design-system/gooddesign.css',
    'site-bridge.css': ROOT / 'extensions/design-system/site-bridge.css',
    'brand-logo.svg': ROOT / 'extensions/design-system/brand-logo.svg',
    'ip-xiaohao.svg': ROOT / 'extensions/design-system/ip-xiaohao.svg',
    'ip-xiaohao-method.svg': ROOT / 'extensions/design-system/ip-xiaohao-method.svg',
    'ip-xiaohao-evidence.svg': ROOT / 'extensions/design-system/ip-xiaohao-evidence.svg',
    'chrome.js': ROOT / 'extensions/design-system/chrome.js',
}
ORDER = ('tokens.css', 'design-system.css', 'gooddesign.css', 'site-bridge.css')


def path(name):
    if name not in FILES:
        raise ValueError('unknown_gooddesign_asset')
    return FILES[name]


def content_type(name):
    return {
        '.css': 'text/css; charset=utf-8',
        '.svg': 'image/svg+xml',
        '.js': 'text/javascript; charset=utf-8',
    }[Path(name).suffix]


_CSS_VERSION = None


def css_version():
    """内容指纹版本：CSS 变更后 URL 自动变化，避免发版后浏览器沿用旧缓存。"""
    global _CSS_VERSION
    if _CSS_VERSION is None:
        import hashlib
        digest = hashlib.sha256()
        for name in ORDER:
            digest.update(name.encode())
            digest.update(FILES[name].read_bytes())
        _CSS_VERSION = digest.hexdigest()[:8]
    return _CSS_VERSION


def links():
    version = css_version()
    return ''.join(f'<link rel="stylesheet" href="/inno/portal/{name}?v={version}">' for name in ORDER)
