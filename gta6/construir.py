"""Paso 3: genera el proyecto de HyperFrames en hf/ (una escena por momento, tarjetas sincronizadas con la voz).

    python3 construir.py  -> hf/index.html, hf/compositions/*.html, hf/assets/mezcla.wav"""
import html
import json
import os
import re
import shutil
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(AQUI, "build")
HF = os.path.join(AQUI, "hf")


FONDOS = {  # mesh gradient de Paper Shaders: atardecer de neón por escena
    "gancho": ["#1a0b2e", "#ff2e88", "#7b2ff7", "#ff8c42"],
    "fecha": ["#12062a", "#7b2ff7", "#00b3ff", "#ff2e88"],
    "mundo": ["#1a0b2e", "#ff8c42", "#ff2e88", "#ffd166"],
    "hype": ["#07021a", "#00b3ff", "#7b2ff7", "#00e5c0"],
    "fomo": ["#1a0410", "#ff2e4d", "#7a0a3a", "#ff8c42"],
    "sorteo": ["#1a0b2e", "#ffd166", "#ff2e88", "#7b2ff7"],
}

PALMERA = """<svg viewBox="0 0 300 900" class="palm {cls}" preserveAspectRatio="xMidYMax meet"><g fill="#0b0414">
<path d="M150 900 C 140 700, 170 520, 150 300 L 162 300 C 184 520, 156 700, 168 900 Z"/>
<path d="M156 300 C 90 240, 30 260, 0 320 C 50 270, 100 270, 156 312 Z"/>
<path d="M156 300 C 230 230, 280 250, 300 310 C 250 265, 210 268, 156 314 Z"/>
<path d="M156 298 C 110 200, 60 170, 20 180 C 80 200, 120 240, 150 310 Z"/>
<path d="M156 298 C 200 190, 250 170, 290 190 C 230 205, 190 245, 162 312 Z"/>
<path d="M156 300 C 150 220, 160 160, 190 120 C 175 180, 168 240, 162 306 Z"/>
<path d="M156 300 C 120 300, 80 340, 60 400 C 100 350, 130 330, 156 316 Z"/>
<path d="M156 300 C 200 305, 240 345, 255 405 C 220 355, 190 335, 158 318 Z"/>
</g></svg>"""


def t_palabra(escena, clave):
    palabra, n = (clave.split("#") + ["1"])[:2]
    hits = [w for w in escena["palabras"] if w["w"] == palabra]
    if len(hits) < int(n):
        raise SystemExit(f"[{escena['escena']}] la voz no dice «{palabra}»")
    return hits[int(n) - 1]["t"] - escena["ini"]


def escena_html(e, seg):
    eid, D = e["escena"], e["dur"]
    cols = FONDOS[eid]
    tarjetas, tws = [], []
    for k, tj in enumerate(seg["tarjetas"]):
        t = max(0.05, t_palabra(e, tj["en"]) - 0.12)
        i = f"{eid}-t{k}"
        if tj.get("grande"):
            tarjetas.append(f'<div id="{i}" class="tj-g"><span>{html.escape(tj["texto"])}</span></div>')
            tws.append(f'tl.fromTo("#{i} span", {{ scale: 2.6, opacity: 0, rotation: {-8 if k % 2 else 8} }}, {{ scale: 1, opacity: 1, rotation: {-2 if k % 2 else 2}, duration: 0.2, ease: "power4.in" }}, {t:.3f});')
        elif tj.get("dato"):
            tarjetas.append(f'<div id="{i}" class="tj-d"><span class="tj-n" id="{i}-n">0</span><span class="tj-p">{html.escape(tj["pie"])}</span></div>')
            tws.append(f'tl.fromTo("#{i}", {{ y: 80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "power3.out" }}, {t:.3f});')
            tws.append(f'(() => {{ const o = {{ v: 0 }}, el = document.getElementById("{i}-n"); tl.fromTo(o, {{ v: 0 }}, {{ v: {tj["dato"]}, duration: 1.4, ease: "power3.out", onUpdate: () => {{ el.textContent = Math.round(o.v).toLocaleString("es-ES"); }} }}, {t:.3f}); }})();')
        else:
            cls = "tj tj-x" if tj.get("tachado") else "tj"
            tarjetas.append(f'<div id="{i}" class="{cls}"><span>{html.escape(tj["texto"])}</span>{"<i></i>" if tj.get("tachado") else ""}</div>')
            tws.append(f'tl.fromTo("#{i}", {{ x: {-900 if k % 2 else 900}, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.28, ease: "power3.out" }}, {t:.3f});')
            if tj.get("tachado"):
                tws.append(f'tl.fromTo("#{i} i", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power2.out" }}, {t + 0.45:.3f});')
        if k and eid != "sorteo":
            tws.append(f'tl.to("#{eid}-t{k - 1}", {{ opacity: 0.5, duration: 0.2 }}, {t:.3f});')
    gancho = eid == "gancho"
    if gancho:
        cab = (f'<div id="{eid}-cab" class="cab cab-g"><span class="logo">GTA <b>VI</b></span>'
               f'<span class="fecha">19 · 11 · 2026</span></div>')
        tws.insert(0, f'tl.fromTo("#{eid}-cab .logo", {{ scale: 1.06 }}, {{ scale: 1, duration: 0.6, ease: "power2.out" }}, 0);')
    else:
        cab = (f'<div id="{eid}-cab" class="cab"><span class="logo logo-s">GTA <b>VI</b></span>'
               f'<span class="et">{html.escape(seg["etiqueta"])}</span></div>')
        tws.insert(0, f'tl.fromTo("#{eid}-cab .et", {{ scale: 0.3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.4)" }}, 0);')
    top = 720 if gancho else 520
    sorteo = eid == "sorteo"
    pie = ('<div class="pie">Sorteo del autor de la cuenta, no de Rockstar. Solo si el vídeo llega a 10.000 likes.</div>' if sorteo
           else '<div class="pie">Datos: Infobae, Guinness World Records, Rockstar Games · nov 2026</div>')
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {cols[0]}; }}
    #{eid}-fondo {{ position: absolute; inset: 0; }}
    .sol {{ position: absolute; left: 190px; top: 1020px; width: 700px; height: 700px; border-radius: 50%;
           background: linear-gradient(180deg, #ffd166 0%, #ff8c42 45%, #ff2e88 100%);
           -webkit-mask: repeating-linear-gradient(180deg, #000 0 34px, transparent 34px 46px);
           mask: repeating-linear-gradient(180deg, #000 0 34px, transparent 34px 46px); box-shadow: 0 0 120px rgba(255,46,136,.6); }}
    .horizonte {{ position: absolute; left: 0; right: 0; top: 1380px; bottom: 0; background: linear-gradient(180deg, #1a0b2e, #07020f); }}
    .rejilla {{ position: absolute; left: -540px; right: -540px; top: 1380px; height: 1200px; transform-origin: 50% 0;
               background-image: linear-gradient(rgba(255,46,136,.85) 3px, transparent 3px), linear-gradient(90deg, rgba(255,46,136,.85) 3px, transparent 3px);
               background-size: 90px 90px; transform: rotateX(72deg); }}
    .rejilla-cont {{ position: absolute; left: 0; right: 0; top: 0; bottom: 0; perspective: 420px; perspective-origin: 50% 1380px; overflow: hidden; }}
    .palm {{ position: absolute; bottom: 0; height: 1000px; width: 340px; }}
    .palm.izq {{ left: -70px; }}
    .palm.der {{ right: -90px; height: 860px; }}
    .cab {{ position: absolute; left: 0; right: 0; top: 190px; display: flex; flex-direction: column; align-items: center; gap: 14px; }}
    .logo {{ display: block; font-family: "League Gothic"; font-size: 120px; line-height: .9; color: #fff; letter-spacing: 4px;
            text-shadow: 0 0 18px #ff2e88, 0 0 46px #ff2e88, 0 6px 0 #7b2ff7; }}
    .logo b {{ font-weight: 400; color: #ffd166; text-shadow: 0 0 18px #ff8c42, 0 0 46px #ff8c42, 0 6px 0 #7b2ff7; }}
    .cab-g .logo {{ font-size: 300px; }}
    .fecha {{ display: block; font-family: "League Gothic"; font-size: 96px; color: #00e5ff; letter-spacing: 8px; text-shadow: 0 0 20px #00b3ff, 0 0 50px #00b3ff; }}
    .et {{ display: block; font-family: "League Gothic"; font-size: 84px; letter-spacing: 3px; color: #1a0b2e; background: #00e5ff; padding: 4px 34px; border-radius: 12px;
          box-shadow: 0 0 30px rgba(0,229,255,.7); }}
    .pila {{ position: absolute; left: 70px; right: 70px; top: {top}px; display: flex; flex-direction: column; align-items: center; gap: 24px; }}
    .tj {{ position: relative; align-self: stretch; text-align: center; background: rgba(10,4,24,.78); border: 4px solid #00e5ff; border-radius: 18px; padding: 14px 24px;
          box-shadow: 0 0 26px rgba(0,229,255,.55), inset 0 0 20px rgba(0,229,255,.25); }}
    .tj span {{ font-family: "League Gothic"; font-size: 78px; line-height: 1; letter-spacing: 2px; color: #fff; }}
    .tj-x i {{ position: absolute; left: 30px; right: 30px; top: 50%; height: 10px; margin-top: -5px; background: #ff2e4d; border-radius: 5px; transform-origin: 0 50%; box-shadow: 0 0 16px #ff2e4d; }}
    .tj-g span {{ display: inline-block; font-family: "League Gothic"; font-size: 132px; line-height: 1; letter-spacing: 3px; color: #fff; background: #ff2e88; padding: 6px 40px; border-radius: 18px;
                 box-shadow: 0 0 40px rgba(255,46,136,.8), 0 14px 0 #7b2ff7; }}
    .tj-d {{ display: flex; flex-direction: column; align-items: center; }}
    .tj-n {{ display: block; font-family: "League Gothic"; font-size: 170px; line-height: 1; color: #ffd166; text-shadow: 0 0 24px #ff8c42, 0 0 60px #ff8c42; }}
    .tj-p {{ display: block; font-family: Inter; font-weight: 900; font-size: 32px; color: #fff; text-align: center; text-shadow: 0 2px 10px rgba(0,0,0,.8); }}
    .pie {{ position: absolute; left: 40px; right: 40px; top: 1395px; text-align: center; font-family: Inter; font-weight: 700; font-size: 22px; color: rgba(255,255,255,.75); text-shadow: 0 2px 8px #000; }}
  </style>
  <div id="root" data-composition-id="{eid}" data-width="1080" data-height="1920">
    <div id="{eid}-fondo"></div>
    <div class="sol" id="{eid}-sol"></div>
    <div class="horizonte"></div>
    <div class="rejilla-cont"><div class="rejilla" id="{eid}-rej"></div></div>
    {PALMERA.replace("{cls}", "izq")}
    {PALMERA.replace("{cls}", "der")}
    {cab}
    <div class="pila">
      {chr(10).join("      " + x for x in tarjetas).strip()}
    </div>
    {pie}
  </div>
  <script>
    (function () {{
      const C = hfPaperColor;
      const fondo = hfPaper("{eid}", document.getElementById("{eid}-fondo"), PaperShaders.meshGradientFragmentShader, hfPaperSizing("cover", {{
        u_colors: {json.dumps(cols)}.map(C), u_colorsCount: {len(cols)},
        u_distortion: 0.9, u_swirl: 0.4, u_grainMixer: 0, u_grainOverlay: 0.06,
      }}), {{ speed: 1.0, offset: {3 + 2 * len(eid)} }});
      const tl = gsap.timeline({{ paused: true }});
      tl.to({{}}, {{ duration: {D} }}, 0);
      // la carretera de neón avanza sin parar y el sol sube un poco
      tl.fromTo("#{eid}-rej", {{ backgroundPosition: "0px 0px" }}, {{ backgroundPosition: "0px " + (90 * Math.round({D} * 3)) + "px", duration: {D}, ease: "none" }}, 0);
      tl.fromTo("#{eid}-sol", {{ y: 40 }}, {{ y: -20, duration: {D}, ease: "none" }}, 0);
      {(chr(10) + "      ").join(tws)}
      tl.eventCallback("onUpdate", () => fondo.draw(tl.time()));
      fondo.draw(0);
      window.__timelines["{eid}"] = tl;
    }})();
  </script>
</template>
"""


def grupos(escena):
    """Subtítulos de 1–3 palabras; un signo de puntuación cierra el grupo."""
    tokens = escena["texto"].split()
    palabras, j = [], 0
    for w in escena["palabras"]:
        limpio = lambda s: re.sub(r"[^\wáéíóúñü-]", "", s.lower())
        while j < len(tokens) and not limpio(tokens[j]).startswith(limpio(w["w"])[:3]):
            j += 1
        fin = j < len(tokens) and bool(re.search(r"[.,:;…!?]$", tokens[j]))
        palabras.append(dict(w, fin=fin))
        j += 1
    out, g = [], []
    for w in palabras:
        g.append(w)
        if w["fin"] or len(g) == 3:
            out.append(g)
            g = []
    if g:
        out.append(g)
    return out


def subtitulos(datos):
    total = datos["total"]
    gs = [g for e in datos["escenas"] for g in grupos(e)]
    filas, tw = [], []
    for i, g in enumerate(gs):
        t0 = g[0]["t"] - 0.05
        fin = gs[i + 1][0]["t"] - 0.05 if i + 1 < len(gs) else total
        fin = min(fin, g[-1]["t"] + g[-1]["d"] + 0.6)
        spans = " ".join(f'<span id="sb-{i}-{k}" class="sb-w">{html.escape(w["w"])}</span>' for k, w in enumerate(g))
        filas.append(f'    <div id="sb-{i}" class="sb-g clip" data-start="{t0:.3f}" data-duration="{fin - t0:.3f}">{spans}</div>')
        tw.append(f'      tl.fromTo("#sb-{i}", {{ scale: 0.82, y: 16 }}, {{ scale: 1, y: 0, duration: 0.14, ease: "back.out(2.5)" }}, {t0:.3f});')
        for k, w in enumerate(g):
            tw.append(f'      tl.fromTo("#sb-{i}-{k}", {{ color: "#ffffff" }}, {{ color: "#ffd23f", duration: 0.01 }}, {w["t"]:.3f});')
            if k + 1 < len(g):
                tw.append(f'      tl.to("#sb-{i}-{k}", {{ color: "#ffffff", duration: 0.01 }}, {g[k + 1]["t"]:.3f});')
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .sb-g {{ position: absolute; left: 60px; right: 60px; top: 1215px; text-align: center; }}
    .sb-w {{ display: inline-block; margin: 0 10px; font-family: "Archivo Black"; font-size: 68px; line-height: 1.1; color: #fff;
            -webkit-text-stroke: 12px #0b0712; paint-order: stroke fill; text-shadow: 0 6px 18px rgba(0,0,0,.45); }}
  </style>
  <div id="root" data-composition-id="subtitulos" data-width="1080" data-height="1920">
{chr(10).join(filas)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.to({{}}, {{ duration: {total} }}, 0);
{chr(10).join(tw)}
      window.__timelines["subtitulos"] = tl;
    }})();
  </script>
</template>
"""


def index(datos):
    total = datos["total"]
    hosts = []
    for k, e in enumerate(datos["escenas"]):
        hosts.append(f'''      <div id="{e['escena']}" data-composition-id="{e['escena']}" data-composition-src="compositions/{e['escena']}.html"
        data-start="{e['ini']:.3f}" data-duration="{e['dur']:.3f}" data-track-index="{k + 1}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 1"></div>''')
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>GTA VI sale en menos de 10 días</title>
    <script src="assets/lib/gsap.min.js"></script>
    <script src="assets/lib/paper-shaders.js"></script>
    <script src="assets/lib/hf-paper.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0d0d12; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
{chr(10).join(hosts)}
      <div id="subtitulos" data-composition-id="subtitulos" data-composition-src="compositions/subtitulos.html"
        data-start="0" data-duration="{total}" data-track-index="10" data-track-kind="captions"
        data-width="1080" data-height="1920" style="z-index: 20"></div>
      <audio id="mezcla" class="clip" src="assets/mezcla.wav" data-start="0" data-duration="{total}" data-track-index="20" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def main():
    from guion import SEGMENTOS
    datos = json.load(open(os.path.join(BUILD, "tiempos.json"), encoding="utf-8"))
    os.makedirs(os.path.join(HF, "compositions"), exist_ok=True)
    for e, seg in zip(datos["escenas"], SEGMENTOS):
        with open(os.path.join(HF, "compositions", e["escena"] + ".html"), "w", encoding="utf-8") as f:
            f.write(escena_html(e, seg))
    with open(os.path.join(HF, "compositions", "subtitulos.html"), "w", encoding="utf-8") as f:
        f.write(subtitulos(datos))
    with open(os.path.join(HF, "index.html"), "w", encoding="utf-8") as f:
        f.write(index(datos))
    shutil.copy(os.path.join(BUILD, "mezcla.wav"), os.path.join(HF, "assets", "mezcla.wav"))
    print("hf/ listo:", len(datos["escenas"]), "escenas,", datos["total"], "s")


if __name__ == "__main__":
    main()
