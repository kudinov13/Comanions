"""Перекачивает превью из manifest.json в максимальном размере через as= + &cs=WxH.
Использование: python vk_upscale.py <manifest.json> <out_dir>"""
import sys, io, json, re, os, urllib.request, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

def fetch(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://vk.com/'}), timeout=30).read()
    except Exception:
        proxy = 'https://images.weserv.nl/?url=' + urllib.parse.quote(url.replace('https://', '').replace('http://', ''), safe='')
        return urllib.request.urlopen(urllib.request.Request(proxy, headers={'User-Agent': UA}), timeout=40).read()

def main():
    mf_path, out_dir = sys.argv[1], sys.argv[2]
    m = json.load(open(mf_path, encoding='utf-8'))
    updated = 0
    for fname, meta in m.items():
        u = meta['url']
        am = re.search(r'[?&]as=([0-9x,]+)', u)
        if not am:
            continue
        sizes = am.group(1).split(',')
        biggest = sizes[-1]  # последний = самый большой
        base = u.split('?')[0]
        # оставляем quality если был
        q = re.search(r'quality=\d+', u)
        big = f"{base}?{'quality=95&' if not q else q.group(0) + '&'}cs={biggest}"
        path = os.path.join(out_dir, fname)
        try:
            data = fetch(big)
            if len(data) > 4000:
                with open(path, 'wb') as f:
                    f.write(data)
                meta['url_big'] = big
                updated += 1
                print(fname, len(data)//1024, 'kb')
        except Exception as e:
            print(fname, 'fail', str(e)[:60])
    json.dump(m, open(mf_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('updated', updated)

main()
