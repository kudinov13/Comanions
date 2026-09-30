import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

urls = sys.argv[1:]
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36')
    for u in urls:
        try:
            pg.goto(u, timeout=30000, wait_until='domcontentloaded')
            pg.wait_for_timeout(4500)
            txt = pg.inner_text('body')
            links = pg.eval_on_selector_all(
                'a[href]',
                'els => els.map(e => e.href).filter(h => h && h.startsWith("http") && !h.includes("vk.com") && !h.includes("vk.ru") && !h.includes("vkvideo") && !h.includes("vk.me"))'
            )
            out[u] = {'text': txt[:7000], 'ext_links': sorted(set(links))[:40]}
        except Exception as e:
            out[u] = {'error': str(e)}
    b.close()

with open(r'C:\Проекты WEB\Subagents\pipeline\vk_check.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('done')
