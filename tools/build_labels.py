# QR 작품 캡션 카드 (인쇄용) 생성기
# tools/works.json 을 읽어 A4 한 장에 90×55mm 카드 10장씩 배치한 HTML 을 만든다.
# 카드의 QR 은 artselah.com/works/<slug>/ 로 연결된다.
# 사용: python3 tools/build_works.py 다음에  python3 tools/build_labels.py <출력.html>
# (qrcode 패키지 필요: pip install qrcode)
import html
import io
import json
import sys

import qrcode
import qrcode.image.svg

e = html.escape
works = [w for w in json.load(open('tools/works.json', encoding='utf-8')) if w['slug'] != 'oh-jiyoon-blue-gold']


def qr_svg(url):
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=0,
                      error_correction=qrcode.constants.ERROR_CORRECT_M)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode()
    return svg[svg.index('<svg'):]


def card(w):
    parts = [p.strip() for p in w['meta'].split('·')]
    year = next((p for p in parts if p.isdigit()), '')
    size = ' '.join(p for p in parts if not p.isdigit())
    url = f"https://artselah.com/works/{w['slug']}/"
    return f'''<div class="card">
  <div class="top"><span class="brand">ARTSELAH</span></div>
  <div class="body">
    <div class="info">
      <h2>{e(w['title'])}</h2>
      <p class="artist">오지윤 Oh Jiyoon</p>
      <p class="spec">{e(w['mat'] or '캔버스에 혼합재료')}<br>{e(size)}{('<br>' + year) if year else ''}</p>
    </div>
    <div class="qr">{qr_svg(url)}</div>
  </div>
  <p class="foot">작품 이야기 · 소장 문의 <span>artselah.com</span></p>
</div>'''


pages = [works[i:i + 10] for i in range(0, len(works), 10)]
doc = '''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>아트셀라 작품 캡션 카드</title>
<style>
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Pretendard", "Noto Sans CJK KR", "Apple SD Gothic Neo", sans-serif; color: #141414; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.sheet { width: 210mm; height: 297mm; padding: 10mm 15mm; display: grid; grid-template-columns: 90mm 90mm; grid-auto-rows: 55mm; justify-content: center; align-content: center; page-break-after: always; }
.sheet:last-child { page-break-after: auto; }
.card { position: relative; border: 0.2mm dashed #c9c6c0; padding: 6mm 6.5mm 5mm; display: flex; flex-direction: column; background: #fff; }
.top { display: flex; justify-content: flex-end; }
.brand { font-family: "Cormorant Garamond", "Noto Serif CJK KR", serif; font-weight: 600; font-size: 7.5pt; letter-spacing: .28em; }
.body { flex: 1; display: flex; justify-content: space-between; gap: 4mm; margin-top: 1.5mm; }
.info { min-width: 0; }
h2 { margin: 0 0 1.2mm; font-size: 11.5pt; font-weight: 600; letter-spacing: .01em; line-height: 1.25; }
.artist { margin: 0 0 3.2mm; font-size: 8.5pt; }
.spec { margin: 0; font-size: 7pt; line-height: 1.55; color: #555350; }
.qr { flex: none; width: 19mm; align-self: flex-end; }
.qr svg { width: 19mm; height: 19mm; display: block; }
.foot { margin: 2mm 0 0; padding-top: 1.6mm; border-top: 0.2mm solid #e4e2dd; font-size: 6.2pt; color: #8a8782; display: flex; justify-content: space-between; letter-spacing: .02em; }
</style></head><body>
''' + ''.join('<section class="sheet">' + ''.join(card(w) for w in p) + '</section>' for p in pages) + '\n</body></html>\n'

open(sys.argv[1], 'w', encoding='utf-8').write(doc)
print(len(works), 'cards,', len(pages), 'pages')
