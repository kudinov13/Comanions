"""VK-фото публичной группы -> локальные файлы.

Использование:
  python vk_photos.py <group_url> <out_dir> [max_total]

Логика:
  1) открываем группу, из HTML берём gid (wall-<gid>_) и id альбомов/фото;
  2) скроллим стену, собираем vkuserphoto.ru URL'ы (превью постов);
  3) открываем каждый альбом, собираем photo-id и img URL'ы;
  4) по каждому photo-id открываем страницу фото и берём самый большой вариант;
  5) качаем напрямую, при сбое через images.weserv.nl.
"""
import sys, io, json, re, os, urllib.request, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
IMG_RE = re.compile(r'https?://[^"\'\s<>\\)]+(?:vkuserphoto\.ru|userapi\.com)[^"\'\s<>\\)]*\.(?:jpg|jpeg|png|webp)[^"\'\s<>\\)]*', re.I)


def fetch_url(url, timeout=40):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://vk.com/'})
    return urllib.request.urlopen(req, timeout=timeout).read()


def download(url, path):
    try:
        data = fetch_url(url)
    except Exception:
        proxy = 'https://images.weserv.nl/?url=' + urllib.parse.quote(
            url.replace('https://', '').replace('http://', ''), safe='')
        data = fetch_url(proxy)
    if len(data) < 4000:
        raise ValueError(f'too small {len(data)}')
    with open(path, 'wb') as f:
        f.write(data)


def img_urls(html):
    urls = [u.replace('&amp;', '&') for u in IMG_RE.findall(html)]
    # прямой размер в query: size=WxH
    def score(u):
        m = re.search(r'size=(\d+)x(\d+)', u)
        if m:
            return int(m.group(1)) * int(m.group(2))
        m = re.search(r'cs=(\d+)x(\d+)', u)
        return int(m.group(1)) * int(m.group(2)) if m else 0
    return sorted(set(urls), key=score, reverse=True)


def scroll(pg, n=6):
    for _ in range(n):
        pg.mouse.wheel(0, 3500)
        pg.wait_for_timeout(900)


def main():
    group = sys.argv[1]
    out_dir = sys.argv[2]
    max_total = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    os.makedirs(out_dir, exist_ok=True)

    manifest = {}
    direct_urls = []   # url -> source
    photo_ids = []     # photo-<gid>_<id>

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(user_agent=UA)
        pg.goto(group if group.startswith('http') else 'https://vk.com/' + group,
                timeout=35000, wait_until='domcontentloaded')
        pg.wait_for_timeout(5000)
        scroll(pg, 14)
        html = pg.content()

        from collections import Counter
        counts = Counter(re.findall(r'wall-(\d+)_\d+', html) + re.findall(r'photo-(\d+)_\d+', html))
        gid = counts.most_common(1)[0][0]
        print('gid:', gid)

        albums = sorted(set(re.findall(r'album-' + gid + r'_(\d+)', html)))
        print('albums:', albums)
        for u in img_urls(html):
            direct_urls.append((u, 'wall'))
        photo_ids += re.findall(r'photo-' + gid + r'_(\d+)', html)

        # альбомы
        for alb in albums:
            try:
                pg.goto(f'https://vk.com/album-{gid}_{alb}', timeout=30000, wait_until='domcontentloaded')
                pg.wait_for_timeout(4000)
                scroll(pg, 4)
                ah = pg.content()
                pids = re.findall(r'photo-' + gid + r'_(\d+)', ah)
                iu = img_urls(ah)
                print(f'  album {alb}: {len(pids)} photo-ids, {len(iu)} img urls')
                photo_ids += pids
                for u in iu:
                    direct_urls.append((u, f'album{alb}'))
            except Exception as e:
                print('  album fail', alb, str(e)[:90])

        # страницы отдельных фото — там полный размер
        big = []
        seen = set()
        for pid in dict.fromkeys(photo_ids):
            if len(big) >= max_total:
                break
            if pid in seen:
                continue
            seen.add(pid)
            try:
                pg.goto(f'https://vk.com/photo-{gid}_{pid}', timeout=25000, wait_until='domcontentloaded')
                pg.wait_for_timeout(2200)
                ph = pg.content()
                us = img_urls(ph)
                if us:
                    big.append((us[0], f'photo{pid}'))
            except Exception as e:
                print('  photo fail', pid, str(e)[:80])
        b.close()

    # скачиваем: сначала большие со страниц фото, потом прямые url со стены/альбомов
    queue = big + [u for u in direct_urls if u[0] not in {x[0] for x in big}]
    got = 0
    for i, (u, src) in enumerate(queue):
        if got >= max_total:
            break
        fname = f'{got+1:02d}_{src}.jpg'
        try:
            download(u, os.path.join(out_dir, fname))
            manifest[fname] = {'source': src, 'url': u}
            got += 1
        except Exception as e:
            print('  dl fail', src, str(e)[:80])

    with open(os.path.join(out_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print('saved', got, '->', out_dir)


if __name__ == '__main__':
    main()
