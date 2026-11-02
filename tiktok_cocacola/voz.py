"""Paso 1: genera la narración (voz neuronal) y los tiempos de cada palabra."""
import asyncio
import json
import os

import certifi

# El contenedor sale a internet por un proxy con su propia CA.
if os.path.exists("/root/.ccr/ca-bundle.crt"):
    certifi.where = lambda: "/root/.ccr/ca-bundle.crt"

import edge_tts  # noqa: E402

from guion import SEGMENTOS, TONO, VELOCIDAD, VOZ  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "build")
os.makedirs(OUT, exist_ok=True)


async def generar(i, texto):
    com = edge_tts.Communicate(texto, VOZ, rate=VELOCIDAD, pitch=TONO, boundary="WordBoundary")
    palabras = []
    with open(f"{OUT}/voz_{i}.mp3", "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                palabras.append({
                    "t": chunk["offset"] / 1e7,
                    "d": chunk["duration"] / 1e7,
                    "w": chunk["text"],
                })
    return palabras


async def main():
    datos = []
    for i, seg in enumerate(SEGMENTOS):
        palabras = await generar(i, seg["texto"])
        datos.append({"escena": seg["escena"], "texto": seg["texto"], "palabras": palabras})
        print(f"[{i}] {len(palabras)} palabras")
    with open(f"{OUT}/palabras.json", "w") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)


asyncio.run(main())
