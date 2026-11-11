import base64, sys, pathlib
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from posts import POSTS

D = pathlib.Path(__file__).parent
OUT = D / "out"; OUT.mkdir(exist_ok=True)
def b64(p): return "data:image/png;base64," + base64.b64encode((D/"assets"/p).read_bytes()).decode()
LOGO = {"cq": b64("logo-conceitoq.png"), "radar": b64("logo-radar.png")}
ACC = {"cq": "#2EC4C9", "radar": "#E8A13C"}
WEEKDAY = ["SEG","TER","QUA","QUI","SEX","SÁB","DOM"]

def html(p):
    a = ACC[p["brand"]]
    logo_h = 92 if p["brand"] == "cq" else 74
    radar = p["brand"] == "radar"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:#19232D;font-family:'Inter',sans-serif;color:#fff;position:relative;overflow:hidden}}
.rings{{position:absolute;left:430px;top:-130px;width:820px;height:820px}}
.wrap{{position:absolute;inset:0;padding:96px 88px 80px;display:flex;flex-direction:column}}
.tag{{display:inline-flex;align-items:center;gap:16px;font-weight:600;font-size:26px;letter-spacing:.18em;text-transform:uppercase;color:{a}}}
.tag i{{width:16px;height:16px;border-radius:50%;background:{a};display:block}}
.badge{{margin-left:18px;font-size:20px;letter-spacing:.14em;padding:8px 16px;border:2px solid {a};border-radius:40px}}
h1{{font-family:'Inter Display','Inter',sans-serif;font-weight:700;font-size:{p.get('fs',88)}px;line-height:1.06;letter-spacing:-.02em;margin-top:auto;max-width:900px}}
h1 em{{font-style:normal;color:{a}}}
.bar{{width:120px;height:8px;background:{a};border-radius:4px;margin:56px 0 40px}}
p.sub{{font-size:36px;line-height:1.4;color:#C8CBD3;max-width:860px;font-weight:400}}
.foot{{margin-top:auto;padding-top:44px;border-top:2px solid rgba(255,255,255,.12);display:flex;align-items:center;justify-content:space-between}}
.foot img{{height:{logo_h}px}}
.cta{{font-size:24px;font-weight:600;color:{a};text-align:right;max-width:380px;line-height:1.3}}
.handle{{display:block;color:#81868D;font-weight:500;margin-top:6px}}
</style></head><body>
<svg class="rings" viewBox="0 0 820 820">
 <g fill="none" stroke="#fff" stroke-opacity=".06" stroke-width="3">
  <circle cx="410" cy="410" r="400"/><circle cx="410" cy="410" r="300"/><circle cx="410" cy="410" r="200"/><circle cx="410" cy="410" r="100"/></g>
 <path d="M410 410 L410 190 A220 220 0 0 1 630 410 Z" fill="{a}" fill-opacity=".10"/>
 <circle cx="525" cy="300" r="20" fill="#2EC4C9" fill-opacity=".55"/>
</svg>
<div class="wrap">
 <div class="tag"><i></i>{p['tag']}{'<span class="badge">Em piloto</span>' if radar else ''}</div>
 <h1>{p['title']}</h1>
 <div class="bar"></div>
 <p class="sub">{p['sub']}</p>
 <div class="foot"><img src="{LOGO[p['brand']]}"><div class="cta">{p['cta']}<span class="handle">@conceitoqconsultoria</span></div></div>
</div></body></html>"""

only = sys.argv[1:]
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = br.new_page(viewport={"width":1080,"height":1350})
    for p in POSTS:
        if only and p["id"] not in only: continue
        pg.set_content(html(p)); pg.wait_for_timeout(150)
        pg.screenshot(path=str(OUT/f"{p['id']}.png"))
        print("ok", p["id"])
    br.close()
