"""Paso 1: genera la narración frase a frase y los tiempos de cada palabra (edge-tts)."""
import asyncio
import json
import os
import re
import subprocess

import certifi
import numpy as np

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


def recorta(raw, margen=0.06):
    """Quita el silencio de entrada y salida de una frase; devuelve (pcm, segundos quitados al principio)."""
    x = np.frombuffer(raw, np.int16)
    voz = np.flatnonzero(np.abs(x) > 600)
    if not len(voz):
        return raw, 0.0
    a = max(0, voz[0] - int(margen * SR))
    b = min(len(x), voz[-1] + int(margen * 2 * SR))
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
            crudo, ini = recorta(pcm(tmp))
            off = len(audio) / 2 / SR - ini
            for w in ws:
                w["t"] += off
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
