# 작품별 페이지 생성기
# index.html / en/index.html 안의 window.WORKS 데이터를 읽어
#   works/<slug>/index.html, en/works/<slug>/index.html 을 만들고
#   작품 카드를 각 페이지 링크로 바꾸고, sitemap.xml 을 다시 쓴다.
# 사용: 저장소 맨 위에서  python3 tools/build_works.py
import html
import json
import os
import re
from urllib.parse import quote
from datetime import date

SITE = 'https://artselah.com'
VERIFY = '3aa5bbc0698c7ac166d1279722ea5893b389d147'
e = html.escape

SERIES = {
    'ko': {'BLUE OCEAN': '바다 위, 바다 아래, 그리고 어제와 오늘. 시시각각 달라지는 바다의 소리와 빛깔을 인간 삶의 감정으로 다시 읽습니다.',
           'DIGNITY': '반복된 붓질로 쌓인 깊은 질감은 삶의 시련과 시간을, 그 안에서 빛나는 사각형은 인간의 고유한 존엄을 상징합니다.'},
    'en': {'BLUE OCEAN': 'Above the sea and beneath it, yesterday and today — the sea changes its voice and colour by the moment, and she reads those changes as the emotions of human life.',
           'DIGNITY': 'Deep textures built from repeated strokes speak of life\'s trials and time; the square that glows within them stands for the dignity inherent in every person.'},
}

T = {
    'ko': dict(lang='ko', artist='오지윤', artist_alt='Oh Jiyoon', site='아트셀라 Artselah', all='전체 작품', ask='이 작품 문의하기',
               series='연작', prev='이전 작품', next='다음 작품', locale='ko_KR', back='← 작품 목록',
               note='작품가와 소장 가능 여부, 액자 · 운송 · 공간에 맞는 크기는 문의 시 안내해 드립니다.',
               about='작가 소개', home_link='아트셀라 홈', other='EN'),
    'en': dict(lang='en', artist='Oh Jiyoon', artist_alt='오지윤', site='Artselah 아트셀라', all='All works', ask='Enquire about this work',
               series='Series', prev='Previous', next='Next', locale='en_US', back='← All works',
               note='Price, availability, framing, shipping and sizing for your space are provided on request.',
               about='About the artist', home_link='Artselah home', other='KO'),
}


def slug_of(w):
    s = os.path.basename(w['img'])[:-4]
    if s == 'ojy-untitled-blue-gold':
        return 'oh-jiyoon-blue-gold'
    return s.replace('-red', '')


def load(path):
    s = open(path, encoding='utf-8').read()
    m = re.search(r'window\.WORKS = (.*?);</script>', s)
    return s, json.loads(m.group(1))


def save_index(path, s, works, prefix):
    # 카드(button 또는 이전에 만든 a)를 작품 페이지 링크로
    def card(m):
        i = int(m.group(1))
        return f'<li><a class="card" href="{prefix}works/{works[i]["slug"]}/" data-work="{i}">'
    s = re.sub(r'<li><(?:button|a) class="card"[^>]*?data-work="(\d+)">', card, s)
    s = re.sub(r'(<li><a class="card"[^>]*>(?:(?!</li>).)*?)</button></li>', r'\1</a></li>', s, flags=re.S)
    s = re.sub(r'window\.WORKS = .*?;</script>',
               lambda _: 'window.WORKS = ' + json.dumps(works, ensure_ascii=False) + ';</script>', s)
    open(path, 'w', encoding='utf-8').write(s)


def page(L, works, i):
    t = T[L]
    w = works[i]
    up = '../../' if L == 'ko' else '../../../'
    home = up if L == 'ko' else '../../'
    asset = lambda p: up + p
    series = next((k for k in SERIES[L] if w['title'].upper().startswith(k)), None)
    url = f"{SITE}/{'' if L == 'ko' else 'en/'}works/{w['slug']}/"
    other = f"{SITE}/{'en/' if L == 'ko' else ''}works/{w['slug']}/"
    title = f"{w['title']} — {t['artist']} | {t['site']}"
    desc = f"{t['artist']}, {w['title']}. {w['meta']}. {w['desc']}"
    prv, nxt = works[(i - 1) % len(works)], works[(i + 1) % len(works)]
    ask_href = f"{home}?work={quote(w['title'] + ' (' + w['meta'] + ')' if w['ask'] else w['title'])}#contact"
    ld = {"@context": "https://schema.org", "@type": "VisualArtwork", "name": w['title'],
          "creator": {"@type": "Person", "name": "오지윤", "alternateName": "Oh Jiyoon", "url": "https://www.ohjiyoon.com/"},
          "image": f"{SITE}/{w['img']}", "url": url, "description": w['desc'],
          "artMedium": w['mat'] or None, "provider": {"@type": "Organization", "name": "아트셀라", "url": SITE + '/'}}
    ld = {k: v for k, v in ld.items() if v}
    other_lang_href = (f"../../en/works/{w['slug']}/" if L == 'ko' else f"../../../works/{w['slug']}/")
    return f'''<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="{'en' if L == 'ko' else 'ko'}" href="{other}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{e(t['site'])}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(w['title'])} — {e(t['artist'])}">
<meta property="og:description" content="{e(w['desc'])}">
<meta property="og:image" content="{SITE}/{w['img']}">
<meta property="og:locale" content="{t['locale']}">
<meta name="naver-site-verification" content="{VERIFY}" />
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="icon" type="image/png" href="{asset('assets/favicon.png')}?v=20261004e">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="{asset('style.css')}?v=20261024a">
</head>
<body class="work-page">
<header class="nav solid">
  <div class="wrap nav-in">
    <a class="brand" href="{home}" aria-label="{e(t['home_link'])}"><b>ARTSELAH</b><span>{'아트셀라' if L == 'ko' else 'Art Agency'}</span></a>
    <nav class="wp-links"><a href="{home}#works">{t['back']}</a><a class="wp-lang" href="{other_lang_href}">{t['other']}</a></nav>
  </div>
</header>
<main class="wrap wp">
  <figure class="wp-img"><img src="{asset(w['img'])}" alt="{e(t['artist'])}, {e(w['title'])}" width="1100" height="1100"></figure>
  <div class="wp-text">
    <p class="kicker"><a href="{home}#artist">{t['artist']} · {t['artist_alt']}</a></p>
    <h1>{e(w['title'])}</h1>
    <p class="wp-meta">{e(w['meta'])}</p>
    {f'<p class="wp-mat">{e(w["mat"])}</p>' if w['mat'] else ''}
    <p class="wp-desc">{e(w['desc'])}</p>
    {f'<div class="wp-series"><h2>{t["series"]} · {series}</h2><p>{e(SERIES[L][series])}</p></div>' if series else ''}
    <p class="wp-note">{e(t['note'])}</p>
    <p class="wp-cta"><a class="btn" href="{e(ask_href)}">{t['ask']}</a><a class="txt" href="{home}#works">{t['all']}</a></p>
  </div>
</main>
<nav class="wrap wp-pager" aria-label="{t['all']}">
  <a href="../{prv['slug']}/"><span>{t['prev']}</span><b>{e(prv['title'])}</b></a>
  <a href="../{nxt['slug']}/"><span>{t['next']}</span><b>{e(nxt['title'])}</b></a>
</nav>
<footer class="foot">
  <div class="wrap foot-in">
    <span><b>ARTSELAH</b> 아트셀라 · <a href="{home}#contact">estherp@artselah.com</a></span>
    <span>© 2026 Artselah · Esther Park. Artworks © Oh Jiyoon.</span>
  </div>
</footer>
</body>
</html>
'''


def main():
    out = {}
    for L, path, prefix in (('ko', 'index.html', ''), ('en', 'en/index.html', '')):
        s, works = load(path)
        for w in works:
            w['img'] = re.sub(r'^(\.\./)+', '', w['img'])
            w['slug'] = slug_of(w)
        out[L] = works
        # 홈의 WORKS 는 그 페이지 기준 상대경로를 유지
        home_works = [dict(w, img=('../' if L == 'en' else '') + w['img']) for w in works]
        save_index(path, s, home_works, prefix)
        for i, w in enumerate(works):
            d = ('' if L == 'ko' else 'en/') + f"works/{w['slug']}"
            os.makedirs(d, exist_ok=True)
            open(f'{d}/index.html', 'w', encoding='utf-8').write(page(L, works, i))
    today = date.today().isoformat()
    urls = [(f'{SITE}/', '1.0'), (f'{SITE}/en/', '0.8')]
    urls += [(f"{SITE}/works/{w['slug']}/", '0.7') for w in out['ko']]
    urls += [(f"{SITE}/en/works/{w['slug']}/", '0.5') for w in out['en']]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += ''.join(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{p}</priority></url>\n' for u, p in urls)
    xml += '</urlset>\n'
    open('sitemap.xml', 'w', encoding='utf-8').write(xml)
    json.dump([{k: w[k] for k in ('slug', 'title', 'meta', 'mat')} for w in out['ko']],
              open('tools/works.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(out['ko']), 'works ×', len(out), 'languages')


if __name__ == '__main__':
    main()
