"""Скачивает фото из карточки 2GIS (если рендерится).
Использование: python twogis_photos.py <firm_url> <out_dir> <max>"""
import sys, io, json, re, os, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
url, out_dir = sys.argv[1], sys.argv[2]
maxn = int(sys.argv[3]) if len(sys.argv) > 3 else 12
os.makedirs(out_dir, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(user_agent=UA)
    try:
        pg.goto(url, timeout=35000, wait_until='domcontentloaded')
        pg.wait_for_timeout(6000)
        for _ in range(4):
            pg.mouse.wheel(0, 3000)
            pg.wait_for_timeout(900)
        html = pg.content()
        open(out_dir + '/_page.html', 'w', encoding='utf-8').write(html)
        urls = sorted(set(re.findall(r'https?://[^"\'\s<>\\)]*\.(?:jpg|jpeg|png|webp)[^"\'\s<>\\)]*', html, re.I)))
        # фильтруем CDN 2gis (static.*.2gis.com, disk.2gis.com и подобные)
        cdn = [u.replace('&amp;', '&') for u in urls if '2gis' in u or 'ams3' in u or 'digitaloceanspaces' in u]
        print('img urls total', len(urls), 'cdn', len(cdn))
        for i, u in enumerate(cdn[:maxn]):
            try:
                d = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=30).read()
                if len(d) < 5000:
                    continue
                open(os.path.join(out_dir, f'2gis_{i:02d}.jpg'), 'wb').write(d)
                print('saved', i, len(d)//1024, 'kb')
            except Exception as e:
                print('fail', i, str(e)[:60])
    except Exception as e:
        print('page fail', str(e)[:120])
    b.close()
