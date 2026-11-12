"""Paso 1b: parte la narración de cada capítulo (build/cap_<id>.mp3, una toma de ElevenLabs por capítulo) en sus
escenas y estima el tiempo de cada palabra con ../comun/alinear.py (silencios + longitud del texto).

    python3 alinear_caps.py   -> build/voz_<i>.mp3 (una por escena) + build/palabras.json"""
import importlib.util
import json
import os
import subprocess

import numpy as np

from guion import CAPITULOS

AQUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(AQUI, "build")
_spec = importlib.util.spec_from_file_location("alinear", os.path.join(AQUI, "..", "comun", "alinear.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def main():
    datos, n = [], 0
    for cap in CAPITULOS:
        ruta = os.path.join(BUILD, f"cap_{cap['id']}.mp3")
        x = A.leer(ruta)
        dur = len(x) / A.SR
        sil = A.silencios(x)
        ini = sil[0][1] if sil and sil[0][0] == 0 else 0.0
        fin = sil[-1][0] if sil and sil[-1][1] >= dur - 0.02 else dur
        internos = [s for s in sil if s[0] > ini and s[1] < fin]
        escenas = cap["escenas"]
        cortes = A.elegir_cortes(internos, ini, fin, [len(e["texto"]) for e in escenas])
        lim = [ini] + [c for s in cortes for c in s] + [fin]
        for k, e in enumerate(escenas):
            a, b = lim[2 * k], lim[2 * k + 1]
            fs = A.frases(e["texto"])
            cs = A.elegir_cortes(internos, a, b, [len(f) for f in fs])
            lf = [a] + [c for s in cs for c in s] + [b]
            ws = []
            for j, f in enumerate(fs):
                fa, fb = lf[2 * j], lf[2 * j + 1]
                ps = A.palabras(f)
                pesos = np.array([len(p) + 1.5 for p in ps], float)
                t = fa
                for p, w in zip(ps, pesos):
                    d = (fb - fa) * w / pesos.sum()
                    ws.append({"t": round(t - a + 0.05, 3), "d": round(d, 3), "w": p})
                    t += d
            s0, s1 = max(0.0, a - 0.05), min(dur, b + 0.12)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", ruta, "-ss", f"{s0:.3f}", "-to", f"{s1:.3f}",
                            "-c:a", "pcm_s16le", "-ar", "44100", os.path.join(BUILD, f"voz_{n}.wav")], check=True)
            datos.append({"escena": e["id"], "texto": e["texto"], "palabras": ws})
            print(f"[{n:2d}] {cap['id']:6s} {e['id']:7s} {a:6.2f}–{b:6.2f}s  {len(fs)} frases ({len(cs)} cortes)")
            n += 1
    json.dump(datos, open(os.path.join(BUILD, "palabras.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
