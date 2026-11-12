"""Paso 2: coloca las frases en la línea de tiempo, sintetiza la música y los efectos con NumPy y lo mezcla todo.

    python3 audio.py      -> build/mezcla.wav + build/tiempos.json (lo que lee construir.py)"""
import json
import os
import subprocess

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(AQUI, "build")
SR = 44100
INICIO = 0.25      # la voz arranca casi en el fotograma 0: el gancho no espera
HUECO = 0.42       # respiro entre escenas (aquí suena el whoosh)
COLA = 2.0         # el cierre se queda en pantalla tras la última palabra
BPM = 140


def leer(ruta):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", ruta, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def colocar(buf, x, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += x * g


def nf(m):
    return 440 * 2 ** ((m - 69) / 12)


def env(m, a=0.005, r=0.3):
    u = np.arange(m) / SR
    return np.minimum(1, u / a) * np.exp(-u / r)


def ruido(m, seed, lp=None):
    r = np.random.default_rng(seed).standard_normal(m).astype(np.float32)
    if lp:
        k = int(lp)
        r = np.convolve(r, np.ones(k) / k, mode="same")
    return r


def bombo():
    m = int(0.35 * SR)
    u = np.arange(m) / SR
    f = 50 + 90 * np.exp(-u * 30)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-u * 9)).astype(np.float32)


def hat(seed):
    m = int(0.06 * SR)
    r = ruido(m, seed)
    r = r - np.convolve(r, np.ones(6) / 6, mode="same")
    return (r * env(m, 0.001, 0.015)).astype(np.float32)


def palmada(seed):
    m = int(0.2 * SR)
    return (ruido(m, seed, 3) * env(m, 0.002, 0.05)).astype(np.float32)


def pluck(f, dur=0.5):
    m = int(dur * SR)
    u = np.arange(m) / SR
    s = sum(np.sin(2 * np.pi * f * h * u) / h ** 1.6 for h in range(1, 6))
    return (s * env(m, 0.003, 0.18)).astype(np.float32)


def pad(fs, dur):
    m = int(dur * SR)
    u = np.arange(m) / SR
    s = np.zeros(m, np.float32)
    for f in fs:
        for d in (-0.15, 0.15):
            ff = f * 2 ** (d / 12)
            s += np.sin(2 * np.pi * ff * u + np.sin(2 * np.pi * 0.3 * u)) * 0.5
    fade = np.minimum(1, np.minimum(u / 0.25, (dur - u) / 0.4))
    return (s * np.clip(fade, 0, 1) / len(fs)).astype(np.float32)


def whoosh(seed, dur=0.55):
    m = int(dur * SR)
    u = np.arange(m) / SR
    r = ruido(m, seed)
    out = np.zeros(m, np.float32)
    # barrido de filtro: media móvil cada vez más corta (de grave a agudo) y vuelta
    for k, w in enumerate((40, 24, 14, 8, 5, 8, 14)):
        a, b = int(k * m / 7), int((k + 1) * m / 7)
        out[a:b] = np.convolve(r, np.ones(w) / w, mode="same")[a:b]
    return (out * np.sin(np.pi * u / dur) ** 2 * 1.6).astype(np.float32)


def pop(f=880):
    m = int(0.12 * SR)
    u = np.arange(m) / SR
    return (np.sin(2 * np.pi * (f + 900 * np.exp(-u * 40)) * u) * env(m, 0.001, 0.04)).astype(np.float32)


def teclas(n, seed):
    out = np.zeros(int(n * 0.075 * SR + SR * 0.1), np.float32)
    rng = np.random.default_rng(seed)
    for k in range(n):
        m = int(0.03 * SR)
        colocar(out, (ruido(m, seed + k, 2) * env(m, 0.001, 0.008)).astype(np.float32), k * 0.075 + rng.uniform(0, 0.02), 0.5)
    return out


def brillo():
    m = int(1.2 * SR)
    out = np.zeros(m, np.float32)
    for k, n in enumerate((84, 88, 91, 96)):
        colocar(out, pluck(nf(n), 0.8) * 0.5, k * 0.07)
    return out


def b808(f, dur, glide=None):
    m = int(dur * SR)
    u = np.arange(m) / SR
    ff = f if glide is None else f + (glide - f) * np.clip((u - dur * 0.5) / (dur * 0.4), 0, 1)
    s = np.sin(2 * np.pi * np.cumsum(ff) / SR + 2 * np.exp(-u * 40))
    s = np.tanh(s * 1.8) * np.minimum(1, u / 0.004) * np.exp(-u * 1.6)
    return s.astype(np.float32)


def snare(seed):
    m = int(0.25 * SR)
    u = np.arange(m) / SR
    r = ruido(m, seed + 99)
    r = r - np.convolve(r, np.ones(4) / 4, mode="same")
    tono = np.sin(2 * np.pi * 190 * u) * np.exp(-u * 30)
    return ((r * np.exp(-u * 18) * 0.8 + tono * 0.6)).astype(np.float32)


def campana(f):
    m = int(0.9 * SR)
    u = np.arange(m) / SR
    s = np.sin(2 * np.pi * f * u + 1.5 * np.sin(2 * np.pi * f * 1.41 * u) * np.exp(-u * 4))
    return (s * np.exp(-u * 5) * np.minimum(1, u / 0.002)).astype(np.float32)


def tic(f):
    m = int(0.05 * SR)
    u = np.arange(m) / SR
    return (np.sin(2 * np.pi * f * u) * np.exp(-u * 160)).astype(np.float32)


def subida(dur):
    m = int(dur * SR)
    u = np.arange(m) / SR
    r = ruido(m, 5)
    out = np.zeros(m, np.float32)
    for k, w in enumerate((60, 40, 26, 16, 10, 6, 4, 3)):
        a, b = int(k * m / 8), int((k + 1) * m / 8)
        out[a:b] = np.convolve(r, np.ones(w) / w, mode="same")[a:b]
    f = 200 * 2 ** (u / dur * 3)
    tono = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    return ((out * 1.5 + tono) * (u / dur) ** 2).astype(np.float32)


def braam(dur=1.6):
    m = int(dur * SR)
    u = np.arange(m) / SR
    s = np.zeros(m, np.float32)
    for f, g in ((36.7, 1), (73.4, .6), (55, .5), (110, .3), (146.8, .2)):
        ph = 2 * np.pi * f * u
        s += g * (2 * ((ph / (2 * np.pi)) % 1) - 1)   # diente de sierra
    s = np.convolve(s, np.ones(12) / 12, mode="same")
    return (np.tanh(s * 1.2) * np.minimum(1, u / 0.01) * np.exp(-u * 2.2)).astype(np.float32)


def golpe_seco():
    m = int(0.3 * SR)
    u = np.arange(m) / SR
    s = np.sin(2 * np.pi * (60 + 120 * np.exp(-u * 50)) * u) * np.exp(-u * 14)
    return (s + ruido(m, 3, 6) * np.exp(-u * 40) * 0.4).astype(np.float32)


def main():
    datos = json.load(open(os.path.join(BUILD, "palabras.json")))
    voces = [leer(os.path.join(BUILD, f"voz_{i}.mp3")) for i in range(len(datos))]
    t = INICIO
    escenas = []
    for d, v in zip(datos, voces):
        dur = len(v) / SR
        escenas.append({"escena": d["escena"], "t0": round(t, 3), "dur_voz": round(dur, 3), "texto": d["texto"],
                        "palabras": [{"t": round(max(0.0, w["t"]) + t, 3), "d": round(w["d"], 3), "w": w["w"]} for w in d["palabras"]]})
        t += dur + HUECO
    # TikTok solo paga vídeos de más de 1 minuto: el cierre se alarga hasta 61,5 s si hace falta
    total = max(round(t - HUECO + COLA, 2), 61.5)
    # cada escena ocupa desde un poco antes de su voz hasta un poco antes de la siguiente
    for i, e in enumerate(escenas):
        ini = 0.0 if i == 0 else round(e["t0"] - HUECO / 2, 3)
        fin = total if i == len(escenas) - 1 else round(escenas[i + 1]["t0"] - HUECO / 2, 3)
        e["ini"], e["dur"] = ini, round(fin - ini, 3)

    n = int(total * SR) + SR
    voz = np.zeros(n, np.float32)
    for e, v in zip(escenas, voces):
        colocar(voz, v, e["t0"])
    voz *= 1.0 / (np.abs(voz).max() + 1e-6)
    voz = np.tanh(voz * 2.4) / np.tanh(2.4) * 0.92   # compresión suave: voz más presente y directa

    # música: beat oscuro tipo trap a 140 BPM (medio tiempo). 808 con glide siguiendo Dm–B♭–Gm–A, hi-hats con
    # ráfagas de semicorcheas/tresillos, palmada en el 3, campana oscura en arpegio y pad grave. En el momento
    # más tenso (m3) el beat se corta y queda un tic-tac de reloj con el 808; vuelve con fuerza en m4.
    from guion import SEGMENTOS
    mus = np.zeros(n, np.float32)
    beat = 60 / BPM
    sem = beat / 4
    ac_raiz = [38, 34, 31, 33]
    ac = [[50, 53, 57], [46, 50, 53], [43, 46, 50], [45, 49, 52]]
    rango = {e["escena"]: (e["ini"], e["ini"] + e["dur"]) for e in escenas}
    tenso = rango["escandalos"]
    patron_808 = [0, 10]            # semicorcheas del compás donde entra el 808
    patron_kick = [0, 10]
    k = 0
    while k * sem < total:
        t0 = k * sem
        pos, compas = k % 16, int(k // 16)
        i = compas % 4
        en_tension = tenso[0] <= t0 < tenso[1]
        intro = t0 < 0.9
        if pos == 0:
            colocar(mus, pad([nf(m) for m in ac[i]], 16 * sem + 0.3), t0, 0.10)
        if pos in patron_808:
            colocar(mus, b808(nf(ac_raiz[i]), 1.4 if pos == 0 else 0.7, glide=nf(ac_raiz[(i + 1) % 4]) if pos == 10 else None), t0, 0.42)
        if en_tension:
            if pos % 4 == 0:
                colocar(mus, tic(1800 if (pos // 4) % 2 == 0 else 1400), t0, 0.22)
            k += 1
            continue
        if intro:
            k += 1
            continue
        if pos in patron_kick:
            colocar(mus, bombo(), t0, 0.40)
        if pos == 8:
            colocar(mus, palmada(k), t0, 0.18)
            colocar(mus, snare(k), t0, 0.2)
        # hi-hats: corcheas, con una ráfaga al final de cada dos compases
        if compas % 2 == 1 and pos >= 12:
            for r in range(3):
                colocar(mus, hat(k * 3 + r), t0 + r * sem / 3, 0.05)
        elif pos % 2 == 0:
            colocar(mus, hat(k), t0, 0.06 if pos % 4 == 2 else 0.04)
        if pos in (0, 3, 6, 10, 13):
            colocar(mus, campana(nf(ac[i][(pos // 3) % 3] + 24)), t0, 0.05)
        k += 1
    voz_env = np.convolve(np.abs(voz), np.ones(int(0.15 * SR)) / (0.15 * SR), mode="same")
    mus *= 1 - 0.5 * np.clip(voz_env / 0.05, 0, 1)
    fin = int((total - 0.8) * SR)
    mus[fin:] *= np.linspace(1, 0, n - fin)

    # efectos: subida + whoosh antes de cada momento, golpe grave en cada tarjeta, impacto doble en las «grandes»
    sfx = np.zeros(n, np.float32)
    for i, e in enumerate(escenas[1:], 1):
        colocar(sfx, subida(1.1), e["t0"] - 1.15, 0.22)
        colocar(sfx, whoosh(i), e["t0"] - 0.38, 0.35)
    for e, seg in zip(escenas, SEGMENTOS):
        for tj in seg.get("tarjetas", []):
            palabra, nn = (tj["en"].split("#") + ["1"])[:2]
            hits = [w for w in e["palabras"] if w["w"] == palabra]
            t = hits[int(nn) - 1]["t"] - 0.03
            if tj.get("grande"):
                colocar(sfx, braam(), t, 0.32)
                colocar(sfx, bombo(), t, 0.5)
            else:
                colocar(sfx, golpe_seco(), t, 0.3)
                colocar(sfx, pop(1000), t, 0.1)

    mezcla = voz + mus + sfx
    mezcla *= 0.95 / np.abs(mezcla).max()
    pcm = (np.clip(mezcla, -1, 1) * 32767).astype(np.int16)
    est = np.stack([pcm, pcm], 1).tobytes()
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-t", str(total), os.path.join(BUILD, "mezcla.wav")], input=est, check=True)
    json.dump({"total": total, "escenas": escenas}, open(os.path.join(BUILD, "tiempos.json"), "w"), ensure_ascii=False, indent=1)
    for e in escenas:
        print(f"{e['escena']:12s} host {e['ini']:6.2f} +{e['dur']:5.2f}   voz {e['t0']:6.2f} +{e['dur_voz']:.2f}")
    print("total", total)


if __name__ == "__main__":
    main()
