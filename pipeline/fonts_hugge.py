import re, urllib.request, pathlib, time

BASE = pathlib.Path(r"C:\Проекты WEB\Subagents\pipeline\2026-09-29\hugge\site\fonts")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}
FAMS = {
    "Vollkorn": [(0,400),(0,500),(0,600),(0,700),(1,400),(1,500)],
    "IBM Plex Mono": [(0,400),(0,500)],
    "Fira Sans": [(0,400),(0,500),(0,600)],
    "Caveat": [(0,400),(0,600)],
}
BASE.mkdir(parents=True, exist_ok=True)

def get(url, tries=4):
    for t in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except Exception as e:
            if t == tries - 1:
                raise
            time.sleep(2 + t * 2)

parts = []
for fam, tuples in FAMS.items():
    t = ";".join(f"{i},{w}" for i, w in sorted(tuples))
    parts.append(f"family={fam.replace(' ', '+')}:ital,wght@{t}")
url = "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"
css = get(url).decode("utf-8")

i = 0
def repl(m):
    global i
    i += 1
    data = get(m.group(1))
    (BASE / f"f{i:02d}.woff2").write_bytes(data)
    return f"url(f{i:02d}.woff2)"

css_new = re.sub(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", repl, css)
(BASE / "fonts.css").write_text(css_new, encoding="utf-8")
print("hugge ->", i, "woff2,", css_new.count("@font-face"), "faces")
