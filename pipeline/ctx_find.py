import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
h = open(sys.argv[1], encoding='utf-8').read()
needle = sys.argv[2]
for m in re.finditer(re.escape(needle), h):
    s = max(0, m.start()-400)
    print('----')
    print(h[s:m.end()+400].replace('\\n', ' ')[:900])
