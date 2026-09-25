"""Apply an exact HTML-only migration to the assembled Pages artifact.

Keep original source HTML as a fallback. Data endpoints and terms are untouched.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OLD = 'https://modbus-monitor.github.io/modbus-device-maps/'
NEW = 'https://docs.quantumbitsolutions.com/'


def portable_sha256(path: Path) -> str:
    """Hash text content with platform-independent LF line endings."""
    content = path.read_bytes().replace(b'\r\n', b'\n')
    return hashlib.sha256(content).hexdigest()


class TargetPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals, self.links, self.robots, self.refresh = [], [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag == 'meta' and attrs.get('name', '').lower() == 'robots':
            self.robots.append(attrs.get('content', ''))
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            self.refresh.append(attrs.get('content'))


def verify_live_target(mapping):
    target = mapping['target']
    with urlopen(Request(target, headers={'User-Agent': 'ModbusMonitor-Migration-Check/1.0'}), timeout=30) as response:
        page = TargetPage()
        page.feed(response.read().decode('utf-8'))
        if response.status != 200 or response.url != target or page.canonicals != [target] or page.refresh or any('noindex' in v for v in page.robots):
            raise ValueError(f'Docs target is not ready: {target}')
        identifier = mapping.get('id')
        if identifier and not any(f'maps/{identifier}.json' in link for link in page.links):
            raise ValueError(f'Docs target lacks matching model JSON: {target}')


def apply(site: Path, verify_live: bool = False) -> None:
    manifest = json.loads((ROOT / 'html-redirects.json').read_text(encoding='utf-8'))
    for relative, digest in manifest['source_sha256'].items():
        if portable_sha256(site / relative) != digest:
            raise ValueError(f'Public data changed; regenerate and review migration: {relative}')
    mappings = manifest['redirects']
    catalog = json.loads((site / 'catalog.json').read_text(encoding='utf-8'))
    expected = {OLD} | {OLD + e['preview_url'] for e in catalog['maps']}
    if len(mappings) != len(expected) or {m['source'] for m in mappings} != expected:
        raise ValueError('Redirect manifest must cover the exact catalog HTML URLs once each')
    if verify_live:
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(verify_live_target, mappings))
    for mapping in mappings:
        source, target = mapping['source'], mapping['target']
        relative = source.removeprefix(OLD)
        if not source.startswith(OLD) or '..' in relative or not target.startswith(NEW) or urlsplit(target).query:
            raise ValueError(f'Unsafe redirect: {mapping}')
        path = site / relative / 'index.html'
        if not path.is_file():
            raise ValueError(f'Missing source HTML: {path}')
        target = html.escape(target, quote=True)
        path.write_text(f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
                        f'<title>Modbus device preview moved</title>\n'
                        f'<meta http-equiv="refresh" content="0; url={target}">\n'
                        f'<link rel="canonical" href="{target}"></head>\n'
                        f'<body><h1>Modbus device preview moved</h1><p><a href="{target}">Continue to the device preview</a></p></body></html>\n', encoding='utf-8')
    tree = ET.parse(site / 'sitemap.xml')
    for node in list(tree.getroot()):
        if node.findtext('{*}loc') in expected:
            tree.getroot().remove(node)
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    tree.write(site / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    print(f'Applied {len(mappings)} exact HTML redirects; public JSON hashes unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-dir', type=Path, required=True)
    parser.add_argument('--verify-live-targets', action='store_true')
    args = parser.parse_args()
    apply(args.site_dir, args.verify_live_targets)
