"""Genera la narración por segmentos (edge-tts) + tiempos de cada palabra -> public/voz/ y src/voz.json."""
import array
import asyncio
import json
import os
import re
import subprocess

import certifi

if os.path.exists("/root/.ccr/ca-bundle.crt"):
    certifi.where = lambda: "/root/.ccr/ca-bundle.crt"

import edge_tts  # noqa: E402

from guion import HUECO, PAUSA, SEGMENTOS, TONO, VELOCIDAD, VOZ  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RAIZ, "public", "voz")
os.makedirs(OUT, exist_ok=True)
SR = 24000


async def frase(texto, ruta):
    com = edge_tts.Communicate(texto, VOZ, rate=VELOCIDAD, pitch=TONO, boundary="WordBoundary")
    palabras = []
    with open(ruta, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                palabras.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "w": ch["text"]})
    return palabras


def pcm(ruta):
    """PCM mono 16 bits sin el silencio que edge-tts deja al final de cada frase."""
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", ruta, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    a = array.array("h", raw)
    fin = len(a)
    while fin > 0 and abs(a[fin - 1]) < 300:
        fin -= 1
    fin = min(len(a), fin + int(0.06 * SR))
    return a[:fin].tobytes()


async def main():
    datos = []
    for i, seg in enumerate(SEGMENTOS):
        frases = [f for f in re.split(r"(?<=[.!?…:])\s+", seg["texto"]) if f.strip()]
        audio, palabras = b"", []
        for j, fr in enumerate(frases):
            tmp = os.path.join(OUT, f"tmp_{i}_{j}.mp3")
            ws = await frase(fr, tmp)
            off = len(audio) / 2 / SR
            for w in ws:
                w["t"] = round(w["t"] + off, 3)
                w["d"] = round(w["d"], 3)
                palabras.append(w)
            audio += pcm(tmp)
            os.remove(tmp)
            if j < len(frases) - 1:
                audio += b"\0\0" * int(seg.get("pausa", PAUSA) * SR)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-c:a", "pcm_s16le", os.path.join(OUT, f"voz_{i}.wav")], input=audio, check=True)
        dur = len(audio) / 2 / SR
        datos.append({"escena": seg["escena"], "audio": f"voz/voz_{i}.wav", "dur": round(dur, 3), "palabras": palabras})
        print(f"[{i}] {seg['escena']}: {len(palabras)} palabras, {dur:.2f}s")
    with open(os.path.join(RAIZ, "src", "voz.json"), "w") as f:
        json.dump({"hueco": HUECO, "segmentos": datos}, f, ensure_ascii=False, indent=1)


asyncio.run(main())
