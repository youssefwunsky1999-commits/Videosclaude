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


COLORES = {"BRONCANO": "#ffd23f", "ABASCAL": "#7fd4ff"}
FONDOS = {  # grain gradient de Paper Shaders por escena: (fondo, colores, forma)
    "gancho": ("#07070c", ["#e63946", "#2b2d42", "#7a1020"], "corners"),
    "m1": ("#07070c", ["#1d3557", "#e63946", "#10131f"], "wave"),
    "m2": ("#07070c", ["#3a2a12", "#b8651f", "#10131f"], "blob"),
    "m3": ("#0a0205", ["#e63946", "#7a1020", "#2b0a10"], "sphere"),
    "m4": ("#07070c", ["#123a8a", "#2a7fff", "#10131f"], "ripple"),
    "m5": ("#0a0205", ["#e63946", "#7a1020", "#2b0a10"], "sphere"),
    "final": ("#07070c", ["#5a3cff", "#e63946", "#10131f"], "corners"),
}


def t_palabra(escena, clave):
    palabra, n = (clave.split("#") + ["1"])[:2]
    hits = [w for w in escena["palabras"] if w["w"] == palabra]
    if len(hits) < int(n):
        raise SystemExit(f"[{escena['escena']}] la voz no dice «{palabra}»")
    return hits[int(n) - 1]["t"] - escena["ini"]


TELETIPO = ("VOX SUSPENDE LA ENTREVISTA CON JORDI WILD · ACUSA A LA REVUELTA DE «GRAVES INCUMPLIMIENTOS» · "
            "DENUNCIA 40 MINUTOS SIN EMITIR · ABASCAL SOLO IRÁ A PROGRAMAS DONDE CONTROLE SUS RESPUESTAS")
TK_PX = 2600


def escena_html(e, seg):
    eid, D = e["escena"], e["dur"]
    back, cols, forma = FONDOS.get(eid, ("#07070c", ["#e63946", "#2b2d42", "#7a1020"], "corners"))
    tarjetas, tws = [], []
    gancho = eid == "gancho"
    for k, tj in enumerate(seg["tarjetas"]):
        t = max(0.05, t_palabra(e, tj["en"]) - 0.12)
        i = f"{eid}-t{k}"
        if tj.get("grande"):
            tarjetas.append(f'<div id="{i}" class="tj-g"><span>{html.escape(tj["texto"])}</span></div>')
            tws.append(f'tl.fromTo("#{i} span", {{ scale: 3, opacity: 0, rotation: -14 }}, {{ scale: 1, opacity: 1, rotation: {-5 if k % 2 else 4}, duration: 0.18, ease: "power4.in" }}, {t:.3f});')
        else:
            col = COLORES.get(tj["quien"], "#ffffff")
            chip = f'<span class="tj-q" style="background:{col}">{tj["quien"]}</span>' if tj["quien"] else ""
            tarjetas.append(f'<div id="{i}" class="tj" style="--rot:{-1.2 if k % 2 else 1.2}deg">{chip}'
                            f'<span class="tj-x"><span class="tj-m" id="{i}-m">{html.escape(tj["texto"])}</span></span></div>')
            tws.append(f'tl.fromTo("#{i}-m", {{ backgroundSize: "0% 100%" }}, {{ backgroundSize: "100% 100%", duration: 0.6, ease: "power2.inOut" }}, {t + 0.3:.3f});')
            tws.append(f'tl.fromTo("#{i}", {{ y: 60, rotation: {-6 if k % 2 else 6}, opacity: 0 }}, {{ y: 0, rotation: {-1.2 if k % 2 else 1.2}, opacity: 1, duration: 0.28, ease: "back.out(1.8)" }}, {t:.3f});')
        # la tarjeta anterior se apaga un poco cuando llega la siguiente
        if k and eid != "final":
            tws.append(f'tl.to("#{eid}-t{k - 1}", {{ opacity: 0.45, duration: 0.2 }}, {t:.3f});')
    cab = ('<div id="{0}-vs" class="vs"><span class="vs-b">ABASCAL</span><span class="vs-v">PLANTA A</span><span class="vs-a">JORDI WILD</span></div>'.format(eid)
           if gancho else f'<div id="{eid}-cab" class="cab"><span class="cab-mini">VOX <b>vs</b> LA REVUELTA</span><span class="cab-et">{html.escape(seg["etiqueta"])}</span></div>')
    if gancho:
        tws.insert(0, f'tl.fromTo("#{eid}-vs .vs-v", {{ scale: 1 }}, {{ scale: 1.25, duration: 0.18, yoyo: true, repeat: 3, ease: "power2.out" }}, 0.0);')
        tws.insert(0, f'tl.fromTo("#{eid}-et", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, 0.0);')
    else:
        tws.insert(0, f'tl.fromTo("#{eid}-cab .cab-et", {{ scale: 0.3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.4)" }}, 0.0);')
    et = f'<div id="{eid}-et" class="et-live"><i></i>{html.escape(seg["etiqueta"])}</div>' if gancho else ""
    top = 700 if gancho else 470
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {back}; }}
    #{eid}-fondo {{ position: absolute; inset: 0; }}
    #{eid}-velo {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.25), rgba(0,0,0,.05) 40%, rgba(0,0,0,.45)); }}
    .vs {{ position: absolute; left: 0; right: 0; top: 280px; display: flex; flex-direction: column; align-items: center; }}
    .vs span {{ display: block; font-family: "Archivo Black"; line-height: .95; text-shadow: 0 10px 40px rgba(0,0,0,.6); }}
    .vs-b {{ font-size: 138px; color: #ffd23f; }}
    .vs-v {{ font-size: 96px; color: #fff; background: #e63946; padding: 0 26px; border-radius: 16px; margin: 10px 0; }}
    .vs-a {{ font-size: 138px; color: #7fd4ff; }}
    .et-live {{ display: none; position: absolute; left: 0; right: 0; top: 190px; text-align: center; font-family: Inter; font-weight: 900; font-size: 34px; color: #fff; letter-spacing: 3px; }}
    .et-live i {{ display: inline-block; width: 22px; height: 22px; border-radius: 50%; background: #e63946; margin-right: 14px; vertical-align: 1px; }}
    .cab {{ position: absolute; left: 0; right: 0; top: 262px; display: flex; flex-direction: column; align-items: center; gap: 22px; }}
    .cab-mini {{ display: block; font-family: "Archivo Black"; font-size: 44px; color: #fff; letter-spacing: 1px; }}
    .cab-mini b {{ color: #e63946; font-weight: 400; }}
    .cab-et {{ display: block; font-family: "Archivo Black"; font-size: 62px; color: #fff; background: #111; border-left: 22px solid #e63946; padding: 8px 32px; border-radius: 0; text-align: left; max-width: 980px; }}
    .pila {{ position: absolute; left: 60px; right: 60px; top: {top}px; display: flex; flex-direction: column; gap: 26px; }}
    .tj {{ background: #f3efe6; border-radius: 3px; padding: 20px 30px 24px; box-shadow: 0 18px 50px rgba(0,0,0,.6); }}
    .tj-q {{ display: inline-block; font-family: "Archivo Black"; font-size: 28px; color: #fff !important; background: #111 !important; padding: 4px 16px; border-radius: 2px; margin-bottom: 12px; letter-spacing: 2px; }}
    .tj-x {{ display: block; font-family: "Archivo Black"; font-size: 50px; line-height: 1.18; color: #121212; }}
    .tj-m {{ background-image: linear-gradient(transparent 55%, #ffe14d 55%, #ffe14d 92%, transparent 92%); background-repeat: no-repeat; background-size: 0% 100%; -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
    .tj-g {{ text-align: center; }}
    .tj-g span {{ display: inline-block; font-family: "Archivo Black"; font-size: 68px; line-height: 1.05; letter-spacing: 2px; color: #ff3b47; background: rgba(10,10,14,.88); border: 9px solid #ff3b47; padding: 10px 32px; border-radius: 6px; box-shadow: 0 0 0 4px rgba(10,10,14,.88), 0 20px 60px rgba(0,0,0,.5); max-width: 960px; }}
    .foto {{ position: absolute; left: -30px; right: -30px; top: 640px; height: 2250px; background-size: cover; background-position: 50% 8%; transform-origin: 50% 30%; }}
    .foto-velo {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(7,7,12,0) 0%, rgba(7,7,12,0) 30%, rgba(7,7,12,.85) 36%, rgba(7,7,12,.8) 44%, rgba(7,7,12,.05) 50%, rgba(7,7,12,.05) 78%, rgba(7,7,12,.6) 100%); }}
    .foto-cred {{ position: absolute; right: 24px; top: 1880px; font-family: Inter; font-weight: 700; font-size: 22px; color: rgba(255,255,255,.7); text-shadow: 0 2px 6px #000; }}
    .bh {{ position: absolute; left: 0; right: 0; top: 176px; height: 62px; display: flex; align-items: stretch; z-index: 30; box-shadow: 0 8px 30px rgba(0,0,0,.45); }}
    .bh-r {{ display: flex; align-items: center; gap: 14px; background: #e63946; color: #fff; font-family: "Archivo Black"; font-size: 32px; letter-spacing: 2px; padding: 0 26px; }}
    .bh-r i {{ display: block; width: 18px; height: 18px; border-radius: 50%; background: #fff; }}
    .bh-t {{ flex: 1; display: flex; align-items: center; background: #111; color: #fff; font-family: Inter; font-weight: 800; font-size: 26px; letter-spacing: 1px; padding: 0 22px; }}
    .tk {{ position: absolute; left: 0; right: 0; top: 1136px; height: 58px; display: flex; z-index: 25; }}
    .tk-l {{ display: flex; align-items: center; background: #ffe14d; color: #111; font-family: "Archivo Black"; font-size: 26px; padding: 0 20px; white-space: nowrap; }}
    .tk-v {{ position: relative; flex: 1; overflow: hidden; background: rgba(10,10,14,.92); }}
    .tk-s {{ position: absolute; left: 0; top: 0; line-height: 58px; white-space: nowrap; font-family: Inter; font-weight: 800; font-size: 28px; color: #fff; }}
    .flash {{ position: absolute; inset: 0; background: #fff; z-index: 40; pointer-events: none; }}
    .fuente {{ position: absolute; left: 0; right: 0; top: 1400px; text-align: center; font-family: Inter; font-size: 22px; color: rgba(255,255,255,.55); }}
  </style>
  <div id="root" data-composition-id="{eid}" data-width="1080" data-height="1920">
    <div id="{eid}-fondo"></div>
    {f'<div id="{eid}-foto" class="foto" style="background-image:url(assets/fotos/{seg["foto"]}.jpg)"></div><div class="foto-velo"></div><div class="foto-cred">Imágenes: RTVE / La Revuelta · EFE · Cadena SER · VOX</div>' if seg.get("foto") else ""}
    <div id="{eid}-velo"></div>
    <div class="bh"><span class="bh-r"><i id="{eid}-dot"></i>ÚLTIMA HORA</span><span class="bh-t">VOX · LA REVUELTA · THE WILD PROJECT</span></div>
    {et}
    {cab}
    <div class="pila">
      {chr(10).join("      " + x for x in tarjetas).strip()}
    </div>
    <div class="tk"><span class="tk-l">EN DIRECTO</span><div class="tk-v"><span class="tk-s" id="{eid}-tk">{TELETIPO} &nbsp;·&nbsp; {TELETIPO}</span></div></div>
    <div class="fuente">Fuentes: comunicado de VOX · Cadena SER (11 nov 2026)</div>
    <div class="flash" id="{eid}-flash"></div>
  </div>
  <script>
    (function () {{
      const C = hfPaperColor;
      const fondo = hfPaper("{eid}", document.getElementById("{eid}-fondo"), PaperShaders.grainGradientFragmentShader, hfPaperSizing("cover", {{
        u_colorBack: C("{back}"), u_colors: {json.dumps(cols)}.map(C), u_colorsCount: {len(cols)},
        u_softness: 0.6, u_intensity: 0.45, u_noise: 0.5, u_shape: PaperShaders.GrainGradientShapes.{forma}, u_noiseTexture: hfNoise(),
      }}), {{ speed: 1.1, offset: {3 + 2 * len(eid)} }});
      const tl = gsap.timeline({{ paused: true }});
      tl.to({{}}, {{ duration: {D} }}, 0);
      {(chr(10) + "      ").join(tws)}
      tl.fromTo("#{eid}-flash", {{ opacity: {0 if eid == "gancho" else 0.85} }}, {{ opacity: 0, duration: 0.3, ease: "power2.out" }}, 0);
      tl.fromTo("#{eid}-tk", {{ x: 0 }}, {{ x: -{TK_PX}, duration: {D}, ease: "none" }}, 0);
      tl.fromTo("#{eid}-dot", {{ opacity: 1 }}, {{ opacity: 0.2, duration: 0.5, yoyo: true, repeat: Math.max(1, Math.floor({D} / 0.5) - 1), ease: "none" }}, 0);
      if (document.getElementById("{eid}-foto") && "{eid}" !== "gancho") tl.fromTo("#{eid}-foto", {{ x: -24 }}, {{ x: 0, duration: 0.18, ease: "steps(3)" }}, 0);
      tl.fromTo("#{eid}-fondo", {{ scale: 1.08 }}, {{ scale: 1, duration: {D}, ease: "none" }}, 0);
      if (document.getElementById("{eid}-foto")) tl.fromTo("#{eid}-foto", {{ scale: 1.0, x: -15 }}, {{ scale: 1.12, x: 15, duration: {D}, ease: "none" }}, 0);
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
    <title>Abascal planta a Jordi Wild</title>
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
