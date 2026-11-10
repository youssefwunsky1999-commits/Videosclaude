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
BPM = 96


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
    total = round(t - HUECO + COLA, 2)
    # cada escena ocupa desde un poco antes de su voz hasta un poco antes de la siguiente
    for i, e in enumerate(escenas):
        ini = 0.0 if i == 0 else round(e["t0"] - HUECO / 2, 3)
        fin = total if i == len(escenas) - 1 else round(escenas[i + 1]["t0"] - HUECO / 2, 3)
        e["ini"], e["dur"] = ini, round(fin - ini, 3)

    n = int(total * SR) + SR
    voz = np.zeros(n, np.float32)
    for e, v in zip(escenas, voces):
        colocar(voz, v, e["t0"])
    voz *= 0.92 / (np.abs(voz).max() + 1e-6)

    # música tensa: Dm – B♭ – Gm – A a 96 BPM, bombo a negras, pulso de bajo en corcheas, pad oscuro
    mus = np.zeros(n, np.float32)
    beat = 60 / BPM
    acordes = [[50, 53, 57], [46, 50, 53], [43, 46, 50], [45, 49, 52]]
    k = 0
    while k * beat / 2 < total:
        t0 = k * beat / 2
        ac = acordes[int(t0 / (4 * beat)) % 4]
        if k % 8 == 0:
            colocar(mus, pad([nf(m + 12) for m in ac], 4 * beat + 0.3), t0, 0.15)
        colocar(mus, pluck(nf(ac[0] - 12), 0.25), t0, 0.16 if k % 2 == 0 else 0.09)
        if k % 2 == 0 and t0 > 0.2:
            colocar(mus, bombo(), t0, 0.34)
        if k % 8 == 6:
            colocar(mus, palmada(k), t0, 0.1)
        colocar(mus, hat(k), t0, 0.05 if k % 2 else 0.03)
        k += 1
    voz_env = np.convolve(np.abs(voz), np.ones(int(0.15 * SR)) / (0.15 * SR), mode="same")
    mus *= 1 - 0.55 * np.clip(voz_env / 0.05, 0, 1)
    fin = int((total - 0.8) * SR)
    mus[fin:] *= np.linspace(1, 0, n - fin)

    # efectos: whoosh en cada cambio de escena y golpe en cada tarjeta (la palabra que la trae)
    from guion import SEGMENTOS
    sfx = np.zeros(n, np.float32)
    for i, e in enumerate(escenas[1:], 1):
        colocar(sfx, whoosh(i), e["t0"] - 0.38, 0.35)
    for e, seg in zip(escenas, SEGMENTOS):
        for tj in seg["tarjetas"]:
            palabra, nn = (tj["en"].split("#") + ["1"])[:2]
            hits = [w for w in e["palabras"] if w["w"] == palabra]
            t = hits[int(nn) - 1]["t"]
            colocar(sfx, bombo(), t - 0.03, 0.45 if tj.get("grande") else 0.25)
            colocar(sfx, pop(600 if tj.get("grande") else 1000), t - 0.03, 0.15)

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
