import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
html = open(sys.argv[1], encoding='utf-8').read()
pats = {
    'photo': r'photo-\d+_\d+',
    'album': r'album-\d+_\d+',
    'clubN': r'club(\d+)',
    'group_id': r'group_id.{0,5}(-?\d+)',
    'data-group': r'data-group-id="(\d+)"',
    'oid': r'oid.{0,3}(-?\d{5,})',
    'wall': r'wall-\d+_\d+',
}
for k, pat in pats.items():
    m = re.findall(pat, html)
    print(k, '->', m[:15], 'total', len(m))
urls = re.findall(r'https://[^"\'\s<>\\]+userapi\.com[^"\'\s<>\\]+', html)
print('userapi count:', len(urls))
for u in urls[:8]:
    print('  ', u[:160])
