#!/usr/bin/env python3
"""Render the 1200x630 share cards, one per language, with headless Chrome: web/assets/og-<lang>.png"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as B

CHROME = os.environ.get("CHROME_BIN", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
ROOT = B.DEFAULT_OUT
LOGO = open(os.path.join(ROOT, "assets", "logo.svg"), encoding="utf-8").read()
CARD = """<!doctype html><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;width:1200px;height:630px;background:#faf8f4;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;color:#16181d;display:flex;flex-direction:column;justify-content:space-between;padding:64px 72px}
.top{display:flex;align-items:center;gap:18px;font-size:30px;font-weight:700;letter-spacing:-.02em}.top svg{width:64px;height:64px}.top span{color:#5d6470;font-weight:500}
h1{font-size:96px;line-height:1.02;letter-spacing:-.045em;margin:0;font-weight:800}h1 em{font-style:normal;color:#d1262b}
.sub{font-size:30px;color:#5d6470;max-width:980px;line-height:1.3}
.bar{display:flex;justify-content:space-between;align-items:center;font-size:26px;color:#5d6470}.bar b{color:#1e2a5a}
.dots i{display:inline-block;width:18px;height:18px;border-radius:50%;margin-left:10px}
</style><div class="top">@@logo@@<div>ask·your·ai<span>.me</span></div></div>
<div><h1>@@a@@<br><em>@@b@@</em></h1></div>
<div class="bar"><div class="sub" style="font-size:28px;max-width:900px">@@sub@@</div><div class="dots"><i style="background:#1e2a5a"></i><i style="background:#fff;border:3px solid #1e2a5a"></i><i style="background:#d1262b"></i></div></div>"""
SUB = {"en": "Your visitors' own AI learns your facts and sends the right people to you.",
       "fr": "L'IA de vos visiteurs connaît vos faits et vous envoie les bonnes personnes.",
       "es": "La IA de tus visitantes conoce tus datos y te envía a las personas adecuadas.",
       "it": "L'IA dei tuoi visitatori conosce i tuoi fatti e ti manda le persone giuste.",
       "nl": "De AI van je bezoekers kent je feiten en stuurt de juiste mensen naar je toe.",
       "de": "Die KI Ihrer Besucher kennt Ihre Fakten und schickt Ihnen die richtigen Leute."}
table, _ = B.load()
out = os.path.join(ROOT, "assets"); os.makedirs(out, exist_ok=True)
for code in B.CODES:
    a = B.tr(table, code, "Make your website"); b = B.tr(table, code, "conversational.")
    html = CARD.replace("@@logo@@", LOGO).replace("@@a@@", a).replace("@@b@@", b).replace("@@sub@@", SUB[code])
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html); path = f.name
    png = os.path.join(out, "og-%s.png" % code)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,630", "--screenshot=" + png, "file://" + path],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.unlink(path); print("wrote", os.path.relpath(png), os.path.getsize(png), "bytes")
