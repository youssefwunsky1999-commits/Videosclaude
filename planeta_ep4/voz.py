"""Paso 1: genera la narración frase a frase (recortando los silencios del TTS) y los tiempos de cada palabra."""
import asyncio
import json
import os
import re
import subprocess

import certifi

if os.path.exists("/root/.ccr/ca-bundle.crt"):
    certifi.where = lambda: "/root/.ccr/ca-bundle.crt"

import edge_tts  # noqa: E402

from guion import PAUSA, SEGMENTOS, TONO, VELOCIDAD, VOZ  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")
os.makedirs(OUT, exist_ok=True)
SR = 24000


async def frase(texto, ruta, seg=None):
    seg = seg or {}
    com = edge_tts.Communicate(texto, seg.get("voz", VOZ), rate=seg.get("velocidad", VELOCIDAD),
                               pitch=seg.get("tono", TONO), boundary="WordBoundary")
    palabras = []
    with open(ruta, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                palabras.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "w": ch["text"]})
    return palabras


def pcm(ruta):
    return subprocess.check_output(["ffmpeg", "-v", "error", "-i", ruta, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])


def recorta(raw, umbral=400, margen=0.04):
    """Quita el silencio que edge-tts deja al principio y al final de cada frase (ritmo sin huecos)."""
    import numpy as np
    x = np.frombuffer(raw, np.int16)
    idx = np.nonzero(np.abs(x) > umbral)[0]
    if len(idx) == 0:
        return raw, 0.0
    m = int(margen * SR)
    a, b = max(0, idx[0] - m), min(len(x), idx[-1] + m)
    return x[a:b].tobytes(), a / SR


async def main():
    datos = []
    for i, seg in enumerate(SEGMENTOS):
        frases = [f for f in re.split(r"(?<=[.!?…:])\s+", seg["texto"]) if f.strip()]
        audio = b""
        palabras = []
        for j, fr in enumerate(frases):
            tmp = os.path.join(OUT, f"tmp_{i}_{j}.mp3")
            ws = await frase(fr, tmp, seg)
            off = len(audio) / 2 / SR
            crudo, lead = recorta(pcm(tmp))
            for w in ws:
                w["t"] += off - lead
                palabras.append(w)
            audio += crudo
            os.remove(tmp)
            if j < len(frases) - 1:
                pausa = PAUSA * (0.6 if fr.endswith(":") else 1.0)
                audio += b"\0\0" * int(pausa * SR)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-b:a", "128k", os.path.join(OUT, f"voz_{i}.mp3")], input=audio, check=True)
        datos.append({"escena": seg["escena"], "texto": seg["texto"], "palabras": palabras})
        print(f"[{i}] {len(frases)} frases, {len(palabras)} palabras, {len(audio) / 2 / SR:.2f}s")
    with open(os.path.join(OUT, "palabras.json"), "w") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)


asyncio.run(main())
