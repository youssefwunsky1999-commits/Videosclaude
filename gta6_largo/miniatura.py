"""Miniatura de YouTube 1280x720 a juego con el vídeo (neón retro + Lucía y Jason dibujados). Sin logos de Rockstar.

    python3 miniatura.py   -> hf_miniatura/ y, con HyperFrames, miniatura.png"""
import os
import shutil
import subprocess

import dibujos as D

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "hf_miniatura")

PAREJA = f'''<svg viewBox="0 0 640 520" style="width:100%;height:100%;overflow:visible">
  {D.lucia("lu", -10, 40, 1.05)}
  {D.jason("ja", 250, 30, 1.08)}
</svg>'''

HTML = f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1280, height=720"/>
<title>Miniatura GTA VI</title><script src="assets/lib/gsap.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1280px; height: 720px; overflow: hidden; background: #12062a; }}
#root {{ position: relative; width: 1280px; height: 720px; overflow: hidden; font-family: Inter; color: #fff; }}
.cielo {{ position: absolute; inset: 0; background: linear-gradient(180deg, #12062a 0%, #5b1a7a 40%, #ff2e88 64%, #12062a 64.3%, #07020f 100%); }}
.sol {{ position: absolute; left: 560px; top: 70px; width: 420px; height: 420px; border-radius: 50%;
  background: linear-gradient(180deg, #ffd166 0%, #ff8c42 45%, #ff2e88 100%);
  -webkit-mask: linear-gradient(180deg, #000 0 52%, transparent 52%), repeating-linear-gradient(180deg, #000 0 22px, transparent 22px 31px);
  box-shadow: 0 0 120px rgba(255,46,136,.7); }}
.rc {{ position: absolute; inset: 0; perspective: 260px; perspective-origin: 50% 462px; overflow: hidden; }}
.rej {{ position: absolute; left: -900px; right: -900px; top: 462px; height: 900px; transform-origin: 50% 0; transform: rotateX(74deg);
  background-image: linear-gradient(#ff2e88cc 3px, transparent 3px), linear-gradient(90deg, #ff2e88cc 3px, transparent 3px); background-size: 80px 80px; }}
.palm {{ position: absolute; bottom: 0; height: 640px; width: 220px; }}
.palm.izq {{ left: -70px; }} .palm.der {{ right: -70px; height: 560px; }}
.lg {{ position: absolute; left: 40px; top: 18px; font-family: "League Gothic"; font-size: 300px; line-height: .88; letter-spacing: 6px;
  text-shadow: 0 0 24px #ff2e88, 0 0 60px #ff2e88, 0 10px 0 #7b2ff7; }}
.lg b {{ font-weight: 400; color: #ffd166; text-shadow: 0 0 24px #ff8c42, 0 0 60px #ff8c42, 0 10px 0 #7b2ff7; }}
.tx {{ position: absolute; left: 40px; top: 300px; font-family: "League Gothic"; font-size: 112px; line-height: .95; letter-spacing: 2px; }}
.tx span {{ display: inline-block; background: #ffd166; color: #12062a; padding: 2px 22px; border-radius: 12px; box-shadow: 0 10px 0 #ff2e88; }}
.tx span.b {{ background: #fff; margin-top: 18px; }}
.fecha {{ position: absolute; left: 40px; top: 568px; font-family: "League Gothic"; font-size: 104px; letter-spacing: 6px; color: #00e5ff;
  text-shadow: 0 0 18px #00b3ff, 0 0 46px #00b3ff, 0 6px 0 #12062a; }}
.pj {{ position: absolute; left: 640px; top: 200px; width: 660px; height: 540px; filter: drop-shadow(0 14px 0 rgba(0,0,0,.35)); }}
.sello {{ position: absolute; right: 30px; top: 40px; font-family: "League Gothic"; font-size: 64px; letter-spacing: 3px; color: #fff; background: #ff3b4d;
  padding: 4px 22px; border-radius: 12px; transform: rotate(6deg); box-shadow: 0 0 30px rgba(255,59,77,.8), 0 8px 0 #7a0a1a; }}
</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="1" data-width="1280" data-height="720">
  <div class="cielo"></div><div class="sol"></div><div class="rc"><div class="rej"></div></div>
  {{D_PALM_IZQ}}
  {{D_PALM_DER}}
  <div class="pj">{PAREJA}</div>
  <div class="lg">GTA <b>VI</b></div>
  <div class="tx"><span>TODO LO QUE</span><br><span class="b">SABEMOS</span></div>
  <div class="fecha">19 · 11 · 2026</div>
  <div class="sello">¿VERDAD O RUMOR?</div>
</div>
<script>window.__timelines["main"] = gsap.timeline({{ paused: true }}); window.__timelines["main"].to({{}}, {{ duration: 1 }});</script>
</body></html>"""


def main():
    import construir as C
    os.makedirs(os.path.join(OUT, "assets", "lib"), exist_ok=True)
    shutil.copy(os.path.join(AQUI, "hf", "assets", "lib", "gsap.min.js"), os.path.join(OUT, "assets", "lib", "gsap.min.js"))
    for f in ("package.json", "hyperframes.json"):
        shutil.copy(os.path.join(AQUI, "hf", f), os.path.join(OUT, f))
    html = HTML.replace("{D_PALM_IZQ}", C.PALMERA.replace("{cls}", "izq")).replace("{D_PALM_DER}", C.PALMERA.replace("{cls}", "der"))
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)
    tmp = os.path.join(OUT, ".snap")
    subprocess.run(["npx", "--yes", "hyperframes@0.9.26", "snapshot", "--at", "0.5", "--no-end", "-o", tmp], cwd=OUT, check=True,
                   stdout=subprocess.DEVNULL)
    png = [f for f in os.listdir(tmp) if f.startswith("frame-")][0]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(tmp, png), "-vf", "scale=1280:720", os.path.join(AQUI, "miniatura.png")], check=True)
    shutil.rmtree(tmp)
    print("miniatura.png lista")


if __name__ == "__main__":
    main()
