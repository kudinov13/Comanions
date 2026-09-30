import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
h = open(sys.argv[1], encoding='utf-8').read()
for pat in [r'/org/[^"\'<>\s\\]+', r'"businessId"\s*:\s*"?(\d+)', r'oid[=:"]+(\d+)', r'Matury?m', 'Матурым', r'avatars\.mds\.yandex\.net[^"\'<>\s\\]+', r'firms\?[^"\'<>\s\\]*']:
    m = re.findall(pat, h)
    print(repr(pat), '->', m[:8], 'total', len(m))
