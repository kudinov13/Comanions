"""Скриншоты сайта-концепта для Visual QA.
Использование: python qa_shots.py <slug>
Пишет в <slug>/qa/shots/: 1440-fold/full, 1024-fold/full, 375-fold/full + 1440-nojs."""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

slug = sys.argv[1]
base = rf"C:\Проекты WEB\Subagents\pipeline\2026-09-29\{slug}"
url = "file:///" + os.path.join(base, "site", "index.html").replace("\\", "/")
outdir = os.path.join(base, "qa", "shots")
os.makedirs(outdir, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for w, h, name in [(1440, 900, "1440"), (1024, 768, "1024"), (375, 812, "375")]:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(url, timeout=30000, wait_until='load')
        pg.wait_for_timeout(2500)
        pg.screenshot(path=os.path.join(outdir, f"{name}-fold.png"))
        # полная страница — ленивый контент: прокрутить вниз и обратно
        pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        pg.wait_for_timeout(1500)
        pg.evaluate("window.scrollTo(0,0)")
        pg.wait_for_timeout(800)
        pg.screenshot(path=os.path.join(outdir, f"{name}-full.png"), full_page=True)
        pg.close()
        print(name, "ok")
    # no-JS variant
    ctx = b.new_context(viewport={"width":1440,"height":900}, java_script_enabled=False)
    pg = ctx.new_page()
    pg.goto(url, timeout=30000)
    pg.wait_for_timeout(1500)
    pg.screenshot(path=os.path.join(outdir, "1440-nojs.png"), full_page=True)
    ctx.close()
    b.close()
print("done ->", outdir)
