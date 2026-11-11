"""Gera YouTube Shorts (1080x1920) a partir dos posts: 3 estados + crossfade via ffmpeg."""
import base64, sys, pathlib, subprocess
from playwright.sync_api import sync_playwright
D = pathlib.Path(__file__).parent
sys.path.insert(0, str(D))
from posts import POSTS, POSTS_EXTRA
ALL = {p["id"]: p for p in POSTS + POSTS_EXTRA}
OUT = D / "shorts"; OUT.mkdir(exist_ok=True)
def b64(p): return "data:image/png;base64," + base64.b64encode((D/"assets"/p).read_bytes()).decode()
LOGO = {"cq": b64("logo-conceitoq.png"), "radar": b64("logo-radar.png")}
ACC = {"cq": "#2EC4C9", "radar": "#E8A13C"}

def html(p, stage):
    a = ACC[p["brand"]]; radar = p["brand"] == "radar"
    logo_h = 104 if p["brand"] == "cq" else 84
    show_t = 1 if stage >= 2 else 0
    show_s = 1 if stage >= 3 else 0
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#19232D;font-family:'Inter',sans-serif;color:#fff;position:relative;overflow:hidden}}
.rings{{position:absolute;left:330px;top:-60px;width:1000px;height:1000px}}
.wrap{{position:absolute;inset:0;padding:200px 88px 300px;display:flex;flex-direction:column}}
.tag{{display:inline-flex;align-items:center;gap:18px;font-weight:600;font-size:30px;letter-spacing:.18em;text-transform:uppercase;color:{a}}}
.tag i{{width:18px;height:18px;border-radius:50%;background:{a};display:block}}
.badge{{margin-left:18px;font-size:22px;letter-spacing:.14em;padding:8px 18px;border:2px solid {a};border-radius:40px}}
h1{{font-family:'Inter Display','Inter',sans-serif;font-weight:700;font-size:100px;line-height:1.06;letter-spacing:-.02em;margin-top:auto;opacity:{show_t}}}
h1 em{{font-style:normal;color:{a}}}
.bar{{width:140px;height:10px;background:{a};border-radius:5px;margin:64px 0 48px;opacity:{show_t}}}
p.sub{{font-size:42px;line-height:1.4;color:#C8CBD3;opacity:{show_s}}}
.foot{{margin-top:auto;padding-top:52px;border-top:2px solid rgba(255,255,255,.12);display:flex;flex-direction:column;gap:28px}}
.foot img{{height:{logo_h}px;align-self:flex-start}}
.cta{{font-size:32px;font-weight:600;color:{a}}}
.handle{{color:#81868D;font-weight:500;font-size:28px}}
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
 <div class="foot"><img src="{LOGO[p['brand']]}"><div class="cta">conceitoq.com</div><div class="handle">YouTube · Boas Práticas PodCast</div></div>
</div></body></html>"""

ids = sys.argv[1:]
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = br.new_page(viewport={"width":1080,"height":1920})
    for i in ids:
        p = ALL[i]
        for s in (1,2,3):
            pg.set_content(html(p, s)); pg.wait_for_timeout(120)
            pg.screenshot(path=str(OUT/f"{i}_s{s}.png"))
        # 0-1s estado1 -> fade 0.8s -> estado2 até 3.5s -> fade 0.8s -> estado3 até 14s
        cmd = ["ffmpeg","-y","-loglevel","error",
          "-loop","1","-t","1.8","-i",str(OUT/f"{i}_s1.png"),
          "-loop","1","-t","3.3","-i",str(OUT/f"{i}_s2.png"),
          "-loop","1","-t","10.5","-i",str(OUT/f"{i}_s3.png"),
          "-f","lavfi","-t","14","-i","anullsrc=r=44100:cl=stereo",
          "-filter_complex","[0][1]xfade=transition=fade:duration=0.8:offset=1.0[a];[a][2]xfade=transition=fade:duration=0.8:offset=3.5,format=yuv420p,fps=30[v]",
          "-map","[v]","-map","3:a","-c:v","libx264","-preset","veryfast","-crf","20","-c:a","aac","-shortest","-movflags","+faststart",
          str(OUT/f"{i}.mp4")]
        subprocess.run(cmd, check=True)
        print("ok", i)
    br.close()
