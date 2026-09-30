import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
url = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(user_agent=UA)
    pg.goto(url, timeout=30000, wait_until='domcontentloaded')
    pg.wait_for_timeout(5000)
    for _ in range(3):
        pg.mouse.wheel(0, 3000)
        pg.wait_for_timeout(800)
    html = pg.content()
    out = sys.argv[2]
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('len', len(html), '->', out)
    print('album refs:', len(re.findall(r'album-\d+_\d+', html)))
    print('photo refs:', len(re.findall(r'photo-\d+_\d+', html)))
    print('userapi:', len(re.findall(r'userapi\.com', html)))
    b.close()
