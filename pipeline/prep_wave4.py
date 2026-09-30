"""Подготовка к билду: копия ledger-approved фото в site/img/ + вендоринг шрифтов."""
import re, shutil, urllib.request, pathlib, sys

BASE = pathlib.Path(r"C:\Проекты WEB\Subagents\pipeline\2026-09-29")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}

# drop-списки из ledgers
DROP = {
    "yantarny-ruchey": {"03_wall.jpg","04_wall.jpg","05_wall.jpg","06_wall.jpg","07_wall.jpg","14_wall.jpg","18_wall.jpg"},
    "maturym": {"06_wall.jpg","10_wall.jpg","11_wall.jpg","12_wall.jpg","2gis_00.jpg","2gis_02.jpg","2gis_04.jpg"},
    "hugge": {"05_wall.jpg","06_wall.jpg","07_wall.jpg","16_wall.jpg"},
}

FONTS = {
    "yantarny-ruchey": {
        "EB Garamond": [(0,400),(0,500),(0,600),(1,400),(1,500)],
        "PT Mono": [(0,400)],
        "Caveat": [(0,400),(0,600)],
    },
    "maturym": {
        "Oranienbaum": [(0,400)],
        "Bebas Neue": [(0,400)],
        "Golos Text": [(0,400),(0,500),(0,600)],
        "Caveat": [(0,400),(0,600)],
    },
    "hugge": {
        "Vollkorn": [(0,400),(0,500),(0,600),(0,700),(1,400),(1,500)],
        "IBM Plex Mono": [(0,400),(0,500)],
        "Fira Sans": [(0,400),(0,500),(0,600)],
        "Caveat": [(0,400),(0,600)],
    },
}

# 1) фото
for slug, drops in DROP.items():
    src = BASE / slug / "research" / "assets"
    dst = BASE / slug / "site" / "img"
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(src.glob("*.jpg")):
        if f.name in drops:
            continue
        shutil.copy2(f, dst / f.name)
        n += 1
    print(slug, "photos ->", n)

# 2) шрифты
for slug, fams in FONTS.items():
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
    print(slug, "fonts ->", i, "woff2,", css_new.count("@font-face"), "faces")
