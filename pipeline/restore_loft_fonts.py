# -*- coding: utf-8 -*-
"""Восстановление шрифтов LOFT: перекачать все woff2 по исходному Google Fonts URL,
перезаписав css2_N.woff2 в порядке @font-face из fonts.css. Плюс добавить IBM Plex Sans."""
import re, io, urllib.request, pathlib

LOFT = pathlib.Path(r"C:\Проекты WEB\Subagents\pipeline\2026-09-29\loft-proletarskaya\site\fonts")
DELO = pathlib.Path(r"C:\Проекты WEB\Subagents\pipeline\2026-09-29\delo-levina\site\fonts")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}

# 1. собрать состав из fonts.css
t = (LOFT / "fonts.css").read_text(encoding="utf-8")
faces = re.findall(r"@font-face \{(.*?)\}", t, re.S)
combos = []
for f in faces:
    fam = re.search(r"font-family: '([^']+)'", f).group(1)
    style = re.search(r"font-style: (\w+)", f).group(1)
    weight = re.search(r"font-weight: (\d+)", f).group(1)
    combos.append((fam, style, weight))
uniq = sorted(set(combos))
print("faces:", len(faces), "unique fam/style/weight:", uniq)

# 2. построить URL: корректные кортежи "ital,weight" для каждого семейства
fams = {}
for fam, style, weight in uniq:
    fams.setdefault(fam, set()).add((0 if style == "normal" else 1, int(weight)))
parts = []
for fam in sorted(fams):
    tuples = ";".join(f"{i},{w}" for i, w in sorted(fams[fam]))
    parts.append(f"family={fam.replace(' ', '+')}:ital,wght@{tuples}")
url = "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"
print("URL:", url)

# 3. скачать css и все woff2 в порядке появления, перезаписать css2_N.woff2
css = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8")
i = 0
def repl(m):
    global i
    i += 1
    data = urllib.request.urlopen(urllib.request.Request(m.group(1), headers=UA), timeout=30).read()
    (LOFT / f"css2_{i}.woff2").write_bytes(data)
    return f"url(css2_{i}.woff2)"
css_new = re.sub(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", repl, css)
print("downloaded:", i, "woff2 files; faces in css:", css_new.count("@font-face"), "was:", len(faces))

# 4. доклеить IBM Plex Sans (кириллица/латиница, 400+500) из делевинских файлов под уникальными именами
extra = []
for src, name in [("css2_11.woff2", "plex_400_cyr_ext.woff2"), ("css2_12.woff2", "plex_400_cyr.woff2"),
                  ("css2_15.woff2", "plex_400_lat_ext.woff2"), ("css2_16.woff2", "plex_400_lat.woff2"),
                  ("css2_17.woff2", "plex_500_cyr_ext.woff2"), ("css2_18.woff2", "plex_500_cyr.woff2"),
                  ("css2_21.woff2", "plex_500_lat_ext.woff2"), ("css2_22.woff2", "plex_500_lat.woff2")]:
    (LOFT / name).write_bytes((DELO / src).read_bytes())
CYR = "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116"
CYR_EXT = "U+0460-052F, U+1C80-1C8A, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F"
LAT_EXT = "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF"
LAT = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
for w in (400, 500):
    for rng, name in [("cyr_ext", f"plex_{w}_cyr_ext.woff2"), ("cyr", f"plex_{w}_cyr.woff2"), ("lat_ext", f"plex_{w}_lat_ext.woff2"), ("lat", f"plex_{w}_lat.woff2")]:
        r = CYR_EXT if rng == "cyr_ext" else CYR if rng == "cyr" else LAT_EXT if rng == "lat_ext" else LAT
        extra.append(f"\n@font-face {{\n  font-family: 'IBM Plex Sans';\n  font-style: normal;\n  font-weight: {w};\n  font-display: swap;\n  src: url({name}) format('woff2');\n  unicode-range: {r};\n}}")
(LOFT / "fonts.css").write_text(css_new + "".join(extra), encoding="utf-8")
print("plex added; fonts.css updated")
