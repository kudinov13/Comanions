import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
html = open(sys.argv[1], encoding='utf-8').read()
# все url с расширением картинки или известными cdn
urls = re.findall(r'https?://[^"\'\s<>\\)]+', html)
img = [u for u in urls if re.search(r'\.(jpg|jpeg|png|webp)', u, re.I)]
cdns = {}
for u in img:
    host = re.sub(r'https?://', '', u).split('/')[0]
    cdns.setdefault(host, []).append(u)
for h, us in sorted(cdns.items(), key=lambda x: -len(x[1])):
    print(h, len(us))
    for u in us[:3]:
        print('   ', u[:150])
