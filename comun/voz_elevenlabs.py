"""Narración con ElevenLabs (voz «Marcos» por defecto): sustituye a edge-tts en voz.py.

Genera lo mismo que los voz.py de cada vídeo: build/voz_<i>.mp3 por segmento y build/palabras.json con el tiempo de
cada palabra (sacado de los tiempos por carácter que devuelve /with-timestamps). Así audio.py y construir.py no cambian.

Uso desde la carpeta de un vídeo:
    python3 ../comun/voz_elevenlabs.py            # lee SEGMENTOS de guion.py

La clave se lee de ELEVENLABS_API_KEY. En los entornos en la nube de Claude Code la inyecta el proxy, así que basta
con un valor cualquiera; en local, exporta la clave real."""
import base64
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

API = "https://api.elevenlabs.io/v1"
NOMBRE_VOZ = os.environ.get("ELEVENLABS_VOZ", "wfwG5A1z7UhZfYQ68gAv")   # MARCOS PROFESIONAL
MODELO = os.environ.get("ELEVENLABS_MODELO", "eleven_multilingual_v2")
CLAVE = os.environ.get("ELEVENLABS_API_KEY", "proxy")
SR = 44100
CA = "/root/.ccr/ca-bundle.crt"


def pedir(ruta, datos=None):
    req = urllib.request.Request(API + ruta, data=json.dumps(datos).encode() if datos else None,
                                 headers={"xi-api-key": CLAVE, "Content-Type": "application/json"})
    import ssl
    ctx = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else None
    with urllib.request.urlopen(req, context=ctx, timeout=120) as r:
        return json.loads(r.read())


def id_voz(nombre):
    """Busca la voz por nombre: primero en la cuenta, luego en la biblioteca compartida (español)."""
    if re.fullmatch(r"[A-Za-z0-9]{20}", nombre):
        return nombre
    for v in pedir("/voices")["voices"]:
        if v["name"].split(" ")[0].lower() == nombre.lower():
            return v["voice_id"]
    q = urllib.parse.urlencode({"search": nombre, "language": "es", "page_size": 20})
    voces = pedir("/shared-voices?" + q).get("voices", [])
    for v in voces:
        if v["name"].lower().startswith(nombre.lower()):
            print(f"voz de la biblioteca: {v['name']} ({v['voice_id']}) — añádela a tu cuenta si la API la rechaza")
            return v["voice_id"]
    raise SystemExit(f"No encuentro la voz «{nombre}» en ElevenLabs: pon su voice_id en ELEVENLABS_VOZ")


def frase(voice_id, texto, ajustes):
    r = pedir(f"/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128",
              {"text": texto, "model_id": MODELO, "voice_settings": ajustes})
    al = r["alignment"]
    palabras, actual, t0, t1 = [], "", None, None
    for ch, a, b in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if re.match(r"[\wáéíóúüñÁÉÍÓÚÜÑ'-]", ch):
            if not actual:
                t0 = a
            actual += ch
            t1 = b
        elif actual:
            palabras.append({"t": t0, "d": t1 - t0, "w": actual})
            actual = ""
    if actual:
        palabras.append({"t": t0, "d": t1 - t0, "w": actual})
    return base64.b64decode(r["audio_base64"]), palabras


def main():
    sys.path.insert(0, os.getcwd())
    from guion import SEGMENTOS
    ajustes = {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}
    out = os.path.join(os.getcwd(), "build")
    os.makedirs(out, exist_ok=True)
    vid = id_voz(NOMBRE_VOZ)
    datos = []
    for i, seg in enumerate(SEGMENTOS):
        mp3, palabras = frase(vid, seg["texto"], dict(ajustes, **seg.get("ajustes", {})))
        ruta = os.path.join(out, f"voz_{i}.mp3")
        open(ruta, "wb").write(mp3)
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta]))
        datos.append({"escena": seg["escena"], "texto": seg["texto"], "palabras": palabras})
        print(f"[{i}] {len(palabras)} palabras, {dur:.2f}s")
    json.dump(datos, open(os.path.join(out, "palabras.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
