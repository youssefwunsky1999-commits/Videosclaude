"""Paso 4: monta el proyecto de HyperFrames en hf/ a partir de los tiempos de la voz.

    python3 construir.py      -> hf/index.html, hf/compositions/*.html, hf/assets/{mezcla.wav, clawd_arcoiris.mp4, ...}

Las escenas de escenas/*.html son plantillas: {{dur}} es la duración de la escena y {{w:palabra}} el segundo (local a la
escena) en que la voz dice esa palabra. Se pueden sumar o restar términos con «|»: {{w:Y|-w:Lo}}, {{dur|-0.3}}."""
import html
import json
import os
import random
import re
import shutil
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(AQUI, "build")
HF = os.path.join(AQUI, "hf")
ESC = os.path.join(AQUI, "escenas")
CLAWD = os.path.join(AQUI, "clawd")


def valor(term, escena):
    term = term.strip()
    signo = 1
    if term[:1] in "+-":
        signo = -1 if term[0] == "-" else 1
        term = term[1:]
    if term == "dur":
        return signo * escena["dur"]
    if term.startswith("w:"):
        palabra, n = term[2:], 1
        if "#" in palabra:
            palabra, n = palabra.split("#")
            n = int(n)
        hits = [w for w in escena["palabras"] if w["w"] == palabra]
        if len(hits) < n:
            raise SystemExit(f"[{escena['escena']}] la voz no dice «{palabra}» ({n}ª vez)")
        return signo * (hits[n - 1]["t"] - escena["ini"])
    return signo * float(term)


def plantilla(nombre, escena, extra):
    src = open(os.path.join(ESC, nombre + ".html"), encoding="utf-8").read()

    def sub(m):
        clave = m.group(1)
        if clave in extra:
            return extra[clave]
        return f"{sum(valor(t, escena) for t in clave.split('|')):.3f}"

    return re.sub(r"\{\{([^}]+)\}\}", sub, src)


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
    <title>4 herramientas gratis para hacer vídeos con código</title>
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


def clawd_assets():
    """El clip de Clawd (renderizado con Claude Animation Base a 12 dibujos/s, «a dos») pasa a 24 fps y se recorta al
    cuadrado central; un fotograma suelto alimenta el shader de semitono."""
    frames = os.path.join(CLAWD, "frames")
    mp4 = os.path.join(HF, "assets", "clawd_arcoiris.mp4")
    if os.path.isdir(frames) and len(os.listdir(frames)) >= 84:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", "12", "-i", os.path.join(frames, "f%05d.png"),
                        "-vf", "crop=1080:1080:420:0,scale=720:720:flags=lanczos,fps=24", "-c:v", "libx264", "-crf", "16",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4], check=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(frames, "f00044.png"),
                        "-vf", "crop=1080:1080:420:0,scale=900:900", os.path.join(HF, "assets", "clawd_still.png")], check=True)
    elif not os.path.exists(mp4):
        raise SystemExit("Falta el clip de Clawd: renderiza clawd/ primero (ver README)")


def main():
    datos = json.load(open(os.path.join(BUILD, "tiempos.json"), encoding="utf-8"))
    os.makedirs(os.path.join(HF, "compositions"), exist_ok=True)
    lemo = sorted(f for f in os.listdir(os.path.join(HF, "assets", "lemo")) if f.endswith(".jpg"))
    random.Random(7).shuffle(lemo)
    extra = {"lemo_mosaico": "".join(f'<img class="l-m" src="assets/lemo/{f}" alt="">' for f in lemo)}
    for e in datos["escenas"]:
        with open(os.path.join(HF, "compositions", e["escena"] + ".html"), "w", encoding="utf-8") as f:
            f.write(plantilla(e["escena"], e, extra))
    with open(os.path.join(HF, "compositions", "subtitulos.html"), "w", encoding="utf-8") as f:
        f.write(subtitulos(datos))
    with open(os.path.join(HF, "index.html"), "w", encoding="utf-8") as f:
        f.write(index(datos))
    shutil.copy(os.path.join(BUILD, "mezcla.wav"), os.path.join(HF, "assets", "mezcla.wav"))
    clawd_assets()
    print("hf/ listo:", len(datos["escenas"]), "escenas,", datos["total"], "s")


if __name__ == "__main__":
    main()
