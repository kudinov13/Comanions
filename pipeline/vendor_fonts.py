# -*- coding: utf-8 -*-
"""Вендоринг шрифтов Google Fonts -> site/fonts/<family_slug>/ + fonts.css."""
import re, urllib.request, pathlib, sys

BASE = pathlib.Path(r"C:\Проекты WEB\Subagents\pipeline\2026-09-29")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}

JOBS = {
    "chompi": {
        "Unbounded": [(0, 700), (0, 900)],
        "Manrope": [(0, 400), (0, 600)],
        "JetBrains Mono": [(0, 400), (0, 500)],
    },
    "elki-palki": {
        "Cormorant": [(0, 500), (0, 600), (0, 700), (1, 500)],
        "Golos Text": [(0, 400), (0, 500)],
        "JetBrains Mono": [(0, 400)],
    },
}

for slug, fams in JOBS.items():
    parts = []
    for fam, tuples in fams.items():
        t = ";".join(f"{i},{w}" for i, w in sorted(tuples))
        parts.append(f"family={fam.replace(' ', '+')}:ital,wght@{t}")
    url = "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"
    css = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8")
    fdir = BASE / slug / "site" / "fonts"
    fdir.mkdir(parents=True, exist_ok=True)
    i = 0
    def repl(m):
        global i
        i += 1
        data = urllib.request.urlopen(urllib.request.Request(m.group(1), headers=UA), timeout=30).read()
        (fdir / f"f{i:02d}.woff2").write_bytes(data)
        return f"url(f{i:02d}.woff2)"
    css_new = re.sub(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", repl, css)
    (fdir / "fonts.css").write_text(css_new, encoding="utf-8")
    print(slug, "->", i, "woff2,", css_new.count("@font-face"), "faces")
