"""Parte una narración completa (p. ej. generada con ElevenLabs) en los segmentos de guion.py y estima el tiempo de
cada palabra, para que audio.py y construir.py funcionen igual que con voz.py.

    python3 ../comun/alinear.py build/narracion.mp3     -> build/voz_<i>.mp3 + build/palabras.json

Método: cada frontera (entre segmentos y entre frases) es el silencio más cercano a donde caería según la longitud del
texto; dentro de cada frase, las palabras se reparten según su longitud. Los subtítulos quedan a pocas décimas."""
import json
import os
import re
import subprocess
import sys

import numpy as np

SR = 22050


def leer(ruta):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", ruta, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def silencios(x, umbral=0.02, minimo=0.12):
    """Tramos (ini, fin) en segundos con energía por debajo del umbral."""
    v = int(0.01 * SR)
    e = np.sqrt(np.convolve(x ** 2, np.ones(v) / v, mode="same"))[::v]
    bajo = e < umbral
    out, i = [], 0
    while i < len(bajo):
        if bajo[i]:
            j = i
            while j < len(bajo) and bajo[j]:
                j += 1
            if (j - i) * 0.01 >= minimo:
                out.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return out


def elegir_cortes(sil, a, b, pesos):
    """Para cada frontera esperada (repartiendo [a, b] según los pesos del texto) toma el silencio más cercano que no
    se haya usado; así no se confunde una respiración larga con un cambio de párrafo."""
    total = sum(pesos)
    cortes, acum = [], 0.0
    libres = [s for s in sil if a < s[0] and s[1] < b]
    for w in pesos[:-1]:
        acum += w
        esperado = a + (b - a) * acum / total
        cand = [s for s in libres if not cortes or s[0] > cortes[-1][1]]
        if not cand:
            cortes.append((esperado, esperado))
            continue
        mejor = min(cand, key=lambda s: abs((s[0] + s[1]) / 2 - esperado) - 0.6 * (s[1] - s[0]))
        cortes.append(mejor)
    return cortes


def frases(texto):
    return [f for f in re.split(r"(?<=[.!?…:])\s+", texto) if f.strip()]


def palabras(texto):
    return re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ'-]+", texto)


def main(ruta):
    sys.path.insert(0, os.getcwd())
    from guion import SEGMENTOS
    x = leer(ruta)
    dur = len(x) / SR
    sil = silencios(x)
    voz_ini = sil[0][1] if sil and sil[0][0] == 0 else 0.0
    voz_fin = sil[-1][0] if sil and sil[-1][1] >= dur - 0.02 else dur
    internos = [s for s in sil if s[0] > voz_ini and s[1] < voz_fin]
    n = len(SEGMENTOS)
    cortes = elegir_cortes(internos, voz_ini, voz_fin, [len(seg["texto"]) for seg in SEGMENTOS])
    limites = [voz_ini] + [c for s in cortes for c in s] + [voz_fin]
    tramos = [(limites[2 * i], limites[2 * i + 1]) for i in range(n)]
    out = os.path.dirname(os.path.abspath(ruta))
    datos = []
    for i, (seg, (a, b)) in enumerate(zip(SEGMENTOS, tramos)):
        fs = frases(seg["texto"])
        cs = elegir_cortes(internos, a, b, [len(f) for f in fs])
        lim = [a] + [c for s in cs for c in s] + [b]
        ws = []
        for k, f in enumerate(fs):
            fa, fb = lim[2 * k], lim[2 * k + 1]
            ps = palabras(f)
            pesos = np.array([len(p) + 1.5 for p in ps], float)
            t = fa
            for p, w in zip(ps, pesos):
                d = (fb - fa) * w / pesos.sum()
                ws.append({"t": round(t - a + 0.05, 3), "d": round(d, 3), "w": p})
                t += d
        # cada segmento empieza 0,05 s antes de su primera palabra, como hace voz.py
        ini, fin = max(0.0, a - 0.05), min(dur, b + 0.1)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", ruta, "-ss", f"{ini:.3f}", "-to", f"{fin:.3f}",
                        "-b:a", "192k", os.path.join(out, f"voz_{i}.mp3")], check=True)
        datos.append({"escena": seg["escena"], "texto": seg["texto"], "palabras": ws})
        print(f"[{i}] {seg['escena']:8s} {a:6.2f}–{b:6.2f}s  {len(fs)} frases ({len(cs)} cortes encontrados)")
    json.dump(datos, open(os.path.join(out, "palabras.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
