"""TikTok vertical «META404»: la ciudad de los seguidores. Personajes de bloques en 3D, pueblo de día y de
noche, un misterio (apagón y cartel robado: «Volveré cuando seáis 1.000») y llamada a seguir, compartir y
comentar qué puesto quieres en la ciudad para el vídeo de los 1.000.

    python3 voz.py && python3 video.py        -> meta404_tiktok.mp4"""
import json
import math
import os
import random
import subprocess
import sys
import wave
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(AQUI, "build")
SALIDA = os.path.join(AQUI, "meta404_tiktok.mp4")

W, H = 540, 960            # unidades de diseño (9:16)
K = 3                      # resolución interna = 1620x2880
IW, IH = W * K, H * K
OW, OH = 1080, 1920
FPS = 30
SR = 44100
VOZ_OFF = 0.12
COLA = 0.22

# paleta
PIEL = (240, 196, 160)
PIEL_S = (214, 166, 130)
NARANJA = (235, 128, 70)
NARANJA_S = (205, 104, 52)
AZUL = (62, 86, 150)
AZUL_S = (48, 68, 122)
PELO = (40, 30, 26)
NEGRO = (32, 34, 42)
NEGRO_S = (24, 25, 32)
MADERA = (176, 112, 60)
MADERA_S = (140, 86, 44)
BLANCO = (250, 248, 242)
AMARILLO = (255, 214, 64)
ROJO = (235, 64, 64)
VERDE = (90, 210, 120)
POLI = (40, 52, 78)

FUENTES = {
    "black": "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "xbold": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "semi": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "sym": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


@lru_cache(maxsize=512)
def F(n, px):
    return ImageFont.truetype(FUENTES[n], max(1, int(px)))


def cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, d):
    return cl((t - t0) / d) if d > 0 else float(t >= t0)


def eo3(x):
    x = cl(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = cl(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eob(x, s=1.8):
    x = cl(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def lerp(a, b, k):
    return a + (b - a) * k


def mezcla(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


# ------------------------------------------------------------------ timeline
with open(os.path.join(BUILD, "palabras.json")) as f:
    DATOS = json.load(f)
for _seg in DATOS:
    _nuevas = []
    for _w in _seg["palabras"]:
        _partes = _w["w"].split()
        for _k, _p in enumerate(_partes):
            _nuevas.append({"t": _w["t"] + _w["d"] * _k / len(_partes), "d": _w["d"] / len(_partes), "w": _p})
    _seg["palabras"] = _nuevas


def dur_mp3(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", p]))


EXTRA = {"apagon": 0.6, "robo": 0.4, "nota": 1.0, "final": 1.6}
ESC = []
_t = 0.0
for i, seg in enumerate(DATOS):
    dv = dur_mp3(os.path.join(BUILD, f"voz_{i}.mp3"))
    d = VOZ_OFF + dv + COLA + EXTRA.get(seg["escena"], 0)
    ESC.append({"i": i, "nombre": seg["escena"], "t0": _t, "dur": d, "voz_t0": _t + (0.05 if i == 0 else VOZ_OFF),
                "palabras": seg["palabras"], "texto": seg["texto"]})
    _t += d
TOTAL = _t
NFRAMES = int(TOTAL * FPS)


def wt(e, palabra, n=0):
    k = 0
    for w in e["palabras"]:
        if w["w"].lower().strip("¿?¡!.,:").startswith(palabra.lower()):
            if k == n:
                return e["voz_t0"] - e["t0"] + w["t"]
            k += 1
    raise KeyError(palabra)


# ------------------------------------------------------------------ subtítulos
CLAVE = {"230", "anoche…", "todo.", "META404.", "META404", "seguidor", "tres", "apagaron", "luz…", "desaparecido.",
         "policía.", "problema:", "bomberos.", "médicos.", "alcalde.", "huella…", "nota:", "1.000.", "vecinos.",
         "síguenos,", "comparte", "comenta", "ladrón.", "puesto.", "robó", "necesita.", "tú?"}


def construir_subs():
    bloques = []
    for e in ESC:
        toks = e["texto"].split()
        ws = e["palabras"]
        if len(toks) != len(ws):
            toks = [w["w"] for w in ws]
        pares = list(zip(toks, ws))
        fus = []
        j = 0
        while j < len(pares):
            hecho = False
            for seq, num in ((["meta", "cuatro", "cero", "cuatro"], "META404"), (["uno", "uno", "dos"], "112")):
                n = len(seq)
                if j + n <= len(pares) and [p[0].lower().strip(".,") for p in pares[j:j + n]] == seq:
                    w0 = dict(pares[j][1])
                    w0["d"] = pares[j + n - 1][1]["t"] + pares[j + n - 1][1]["d"] - w0["t"]
                    ult = pares[j + n - 1][0]
                    fus.append((num + ult[len(ult.rstrip(".,:?!")):], w0))
                    j += n
                    hecho = True
                    break
            if hecho:
                continue
            tok, w = pares[j]
            limpio = tok.lower().rstrip(".,:?!")
            if limpio == "mil":
                tok = "1.000" + tok[3:]
            fus.append((tok, w))
            j += 1
        chunk = []
        for tok, w in fus:
            chunk.append((tok, e["voz_t0"] + w["t"], e["voz_t0"] + w["t"] + w["d"]))
            largo = sum(len(c[0]) + 1 for c in chunk)
            if tok[-1] in ".,:?!" or largo > 15 or len(chunk) >= 3:
                bloques.append(chunk)
                chunk = []
        if chunk:
            bloques.append(chunk)
    res = []
    for k, b in enumerate(bloques):
        ini = b[0][1] - 0.05
        fin = b[-1][2] + 0.35
        if k + 1 < len(bloques):
            fin = min(fin, bloques[k + 1][0][1] - 0.05)
        res.append((ini, fin, b))
    return res


SUBS = construir_subs()


# ------------------------------------------------------------------ lienzo
class Capa:
    """Superficie de dibujo en unidades de diseño."""

    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img, "RGBA")
        self.A = 1.0

    def c(self, col, a=1.0):
        return tuple(col[:3]) + (int(255 * cl(a * self.A)),)


def P(*v):
    return [x * K for x in v]


def circ(L, x, y, r, fill=None, outline=None, w=2, a=1.0):
    if r <= 0:
        return
    L.d.ellipse(P(x - r, y - r, x + r, y + r), fill=L.c(fill, a) if fill else None,
                outline=L.c(outline, a) if outline else None, width=max(1, int(w * K)))


def rect(L, x0, y0, x1, y1, fill, a=1.0, r=0, outline=None, w=2):
    if r:
        L.d.rounded_rectangle(P(x0, y0, x1, y1), radius=r * K, fill=L.c(fill, a) if fill else None,
                              outline=L.c(outline, a) if outline else None, width=int(w * K))
    else:
        L.d.rectangle(P(x0, y0, x1, y1), fill=L.c(fill, a) if fill else None,
                      outline=L.c(outline, a) if outline else None, width=int(w * K))


def poly(L, pts, fill, a=1.0):
    L.d.polygon([(x * K, y * K) for x, y in pts], fill=L.c(fill, a))


def linea(L, pts, col, w=2, a=1.0):
    L.d.line([(x * K, y * K) for x, y in pts], fill=L.c(col, a), width=max(1, int(w * K)), joint="curve")


def capsula(L, p1, p2, w, col, a=1.0):
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1
    px, py = -dy / n * w / 2, dx / n * w / 2
    poly(L, [(x1 + px, y1 + py), (x2 + px, y2 + py), (x2 - px, y2 - py), (x1 - px, y1 - py)], col, a)
    circ(L, x1, y1, w / 2, fill=col, a=a)
    circ(L, x2, y2, w / 2, fill=col, a=a)


def texto(L, s, x, y, size, col=BLANCO, a=1.0, fuente="black", anchor="mm", sombra=True):
    if a * L.A <= 0.003:
        return
    f = F(fuente, size * K)
    if sombra:
        L.d.text((x * K + 2 * K, y * K + 3 * K), s, font=f, fill=(0, 0, 0, int(160 * cl(a * L.A))), anchor=anchor)
    L.d.text((x * K, y * K), s, font=f, fill=L.c(col, a), anchor=anchor,
             stroke_width=int(size * K * 0.06) if sombra else 0, stroke_fill=(0, 0, 0, int(200 * cl(a * L.A))))


def ancho(s, size, fuente="black"):
    return F(fuente, size * K).getlength(s) / K


# ------------------------------------------------------------------ personajes
POSES = {
    # cadera en (0,0); mirando a la derecha
    "sentado": dict(rodilla=(70, 0), pie=(72, 85), cuello=(-6, -118), cabeza=(-2, -158), codo=(26, -58), mano=(70, -44)),
    "sentado_habla": dict(rodilla=(70, 0), pie=(72, 85), cuello=(-2, -118), cabeza=(4, -158), codo=(34, -62), mano=(66, -96)),
    "sentado_come": dict(rodilla=(70, 0), pie=(72, 85), cuello=(-2, -118), cabeza=(4, -156), codo=(36, -70), mano=(26, -136)),
    "sentado_duerme": dict(rodilla=(70, 0), pie=(72, 85), cuello=(4, -112), cabeza=(26, -140), codo=(24, -52), mano=(66, -40)),
    "sentado_respira": dict(rodilla=(70, 0), pie=(72, 85), cuello=(-8, -122), cabeza=(-6, -162), codo=(24, -56), mano=(62, -18)),
    "suelo": dict(rodilla=(-72, 4), pie=(-142, 8), cuello=(108, -4), cabeza=(150, -10), codo=(164, 2), mano=(214, 6)),
    "agachado": dict(rodilla=(56, -6), pie=(48, 72), cuello=(60, -86), cabeza=(98, -110), codo=(96, -30), mano=(134, -6)),
    "de_pie": dict(rodilla=(4, 95), pie=(2, 190), cuello=(0, -150), cabeza=(0, -196), codo=(-6, -74), mano=(-4, -8)),
    "de_pie_brazos": dict(rodilla=(4, 95), pie=(2, 190), cuello=(0, -150), cabeza=(-2, -196), codo=(-30, -96), mano=(-16, -60)),
    "de_pie_inclina": dict(rodilla=(4, 95), pie=(2, 190), cuello=(-8, -148), cabeza=(-18, -190), codo=(-12, -74), mano=(-8, -8)),
    "apunta": dict(rodilla=(10, 95), pie=(14, 190), cuello=(-4, -150), cabeza=(-6, -196), codo=(-56, -126), mano=(-104, -128)),
}


def _completa(p):
    p = dict(POSES[p] if isinstance(p, str) else p)
    p.setdefault("codo2", (p["codo"][0] - 6, p["codo"][1] + 2))
    p.setdefault("mano2", (p["mano"][0] - 8, p["mano"][1] + 4))
    return p


def pose_mix(a, b, k):
    pa, pb = _completa(a), _completa(b)
    return {n: (lerp(pa[n][0], pb[n][0], k), lerp(pa[n][1], pb[n][1], k)) for n in pa}


def persona(L, x, y, pose, esc=1.0, flip=False, tipo="victima", sombra=None, a=1.0, ojos=1.0, boca=0.0,
            ropa=None, barba=False, bigote=False, pelo=None):
    """Dibuja un personaje plano. tipo: victima | captor | policia."""
    if isinstance(pose, str):
        pose = POSES[pose]
    s = -esc if flip else esc

    def T(p):
        return (x + p[0] * s, y + p[1] * esc)

    cad = (x, y)
    rod, pie, cue, cab, cod, man = (T(pose[n]) for n in ("rodilla", "pie", "cuello", "cabeza", "codo", "mano"))
    cod2 = T(pose["codo2"]) if "codo2" in pose else None
    man2 = T(pose["mano2"]) if "mano2" in pose else None
    hombro = (lerp(cue[0], cad[0], 0.12), lerp(cue[1], cad[1], 0.12))
    if tipo == "victima":
        cuerpo, cuerpo_s, pierna, pierna_s, piel = NARANJA, NARANJA_S, AZUL, AZUL_S, PIEL
    elif tipo == "captor":
        cuerpo, cuerpo_s, pierna, pierna_s, piel = NEGRO, NEGRO_S, NEGRO, NEGRO_S, NEGRO
    else:
        cuerpo, cuerpo_s, pierna, pierna_s, piel = POLI, (30, 40, 62), (34, 40, 58), (26, 30, 46), (30, 34, 44)
    if ropa:
        cuerpo, cuerpo_s, pierna, pierna_s = ropa
        piel = PIEL
        tipo = "victima"
    PELO_ = pelo or PELO
    if sombra:
        cuerpo = cuerpo_s = pierna = pierna_s = piel = sombra
    e = esc
    # brazo y pierna del fondo
    capsula(L, cad, rod, 36 * e, pierna_s, a)
    capsula(L, rod, (pie[0] - 6 * s, pie[1]), 32 * e, pierna_s, a)
    cb = cod2 or cod
    mb = man2 or (man[0] - 8 * s, man[1] + 4 * e)
    capsula(L, hombro, cb, 22 * e, cuerpo_s, a)
    capsula(L, cb, mb, 20 * e, cuerpo_s, a)
    if man2:
        circ(L, mb[0], mb[1], 11 * e, fill=sombra or (PIEL_S if tipo == "victima" else (36, 36, 44)), a=a)
    # torso
    capsula(L, cad, cue, 56 * e, cuerpo, a)
    if ropa and not sombra:   # cuello de camisa y pajarita
        poly(L, [(cue[0] - 10 * e, cue[1] + 2 * e), (cue[0] + 12 * e, cue[1] + 2 * e), (cue[0] + 2 * e * s / e, cue[1] + 30 * e)],
             BLANCO, a)
        circ(L, cue[0] + 1 * e, cue[1] + 8 * e, 5 * e, fill=(120, 30, 30), a=a)
    # pierna delante
    capsula(L, cad, rod, 36 * e, pierna, a)
    capsula(L, rod, pie, 32 * e, pierna, a)
    zap = sombra or ((20, 20, 24) if tipo != "policia" else (16, 18, 24))
    poly(L, [(pie[0] - 14 * e * abs(s) / e, pie[1] - 6 * e), (pie[0] + 26 * s, pie[1] - 4 * e),
             (pie[0] + 26 * s, pie[1] + 12 * e), (pie[0] - 14 * s, pie[1] + 12 * e)], zap, a)
    # cabeza
    r = 34 * e
    circ(L, cab[0], cab[1], r, fill=piel, a=a)
    if sombra:
        pass
    elif tipo == "victima":
        L.d.pieslice(P(cab[0] - r * 1.04, cab[1] - r * 1.08, cab[0] + r * 1.04, cab[1] + r),
                     185 if s > 0 else 175, 355 if s > 0 else 365, fill=L.c(PELO_, a))
        poly(L, [(cab[0] - r * s, cab[1] - r * .3), (cab[0] - r * .3 * s, cab[1] - r), (cab[0] - r * 1.02 * s, cab[1] + r * .25)],
             PELO_, a)
        if barba:
            L.d.chord(P(cab[0] - r * 1.02, cab[1] - r * 0.9, cab[0] + r * 1.02, cab[1] + r * 1.12), 15, 165,
                      fill=L.c(PELO_, a))
        if barba or bigote:
            rect(L, min(cab[0] + r * .25 * s, cab[0] + r * .85 * s), cab[1] + r * .22,
                 max(cab[0] + r * .25 * s, cab[0] + r * .85 * s), cab[1] + r * .38, PELO_, a=a, r=3 * e)
        circ(L, cab[0] - r * .05 * s, cab[1] + r * .25, r * .22, fill=(232, 150, 130), a=a * .5)  # mejilla
        ex = cab[0] + r * .45 * s
        ey = cab[1] - r * .05
        if ojos > 0.15:
            circ(L, ex, ey, 3.6 * e * ojos + 1, fill=(28, 24, 22), a=a)
        else:
            linea(L, [(ex - 5 * e, ey), (ex + 5 * e, ey)], (28, 24, 22), w=2 * e, a=a)
        linea(L, [(ex - 7 * e, ey - 10 * e), (ex + 7 * e, ey - 11 * e)], PELO_, w=2.6 * e, a=a)
        if boca > 0:
            circ(L, cab[0] + r * .55 * s, cab[1] + r * .45, 3 * e + 4 * e * boca, fill=(120, 50, 46), a=a)
    elif tipo == "captor":
        bx0, bx1 = sorted([cab[0] - r * .1 * s, cab[0] + r * 1.0 * s])
        rect(L, bx0, cab[1] - r * .35, bx1, cab[1] + r * .05, PIEL, a=a, r=6 * e)
        ex = cab[0] + r * .55 * s
        circ(L, ex, cab[1] - r * .15, 5 * e, fill=BLANCO, a=a)
        circ(L, ex + 1.5 * s, cab[1] - r * .15, 2.6 * e, fill=(20, 20, 20), a=a)
    else:  # policía con casco y visera
        L.d.pieslice(P(cab[0] - r * 1.1, cab[1] - r * 1.2, cab[0] + r * 1.1, cab[1] + r * .9), 180, 360,
                     fill=L.c((22, 26, 36), a))
        rect(L, min(cab[0], cab[0] + r * 1.05 * s), cab[1] - r * .2, max(cab[0], cab[0] + r * 1.05 * s), cab[1] + r * .25,
             (70, 110, 150), a=a, r=4 * e)
    # brazo delante y mano
    capsula(L, hombro, cod, 22 * e, cuerpo, a)
    capsula(L, cod, man, 20 * e, cuerpo, a)
    circ(L, man[0], man[1], 12 * e, fill=sombra or (PIEL if tipo == "victima" else (40, 40, 48)), a=a)
    return dict(cabeza=cab, mano=man, cadera=cad)


def silla(L, x, y, a=1.0, sombra=None, flip=False):
    """Silla de madera; (x, y) = punto del asiento bajo la cadera."""
    m, ms = (sombra, sombra) if sombra else (MADERA, MADERA_S)
    s = -1 if flip else 1
    rect(L, x - 30, y + 14, x + 70, y + 26, m, a=a)
    for lx in (x - 26, x + 62):
        rect(L, lx, y + 26, lx + 9, y + 100, ms, a=a)
    bx = x - 34 if s > 0 else x + 66
    rect(L, bx, y - 110, bx + 10, y + 100, m, a=a, r=4)
    rect(L, bx - 2, y - 116, bx + 12, y - 104, ms, a=a, r=3)


# --- Escenas del TikTok «META404» (se insertan en video.py al montarlo) ---

CIUDAD = "META404"
VECINOS = 230
META = 1000
CABECERA = f"{CIUDAD} · {VECINOS} VECINOS"

CIELO_D = (130, 190, 240)
CIELO_D2 = (200, 230, 250)
CIELO_N = (10, 14, 40)
CIELO_N2 = (34, 40, 90)
ASFALTO = (70, 74, 84)
ACERA = (200, 200, 205)
CESPED_B = (100, 180, 90)
AMAR = (255, 210, 70)
TXT = (245, 245, 250)

VECINOS_LOOK = [
    dict(camisa=(170, 225, 190), pantalon=(90, 140, 220), pelo=(120, 80, 50), gorra=(90, 180, 110)),
    dict(camisa=(250, 220, 150), pantalon=(250, 220, 150), pelo=(180, 100, 50), rizos=True),
    dict(camisa=(220, 70, 70), pantalon=(60, 60, 80), pelo=(220, 120, 40)),
    dict(camisa=(80, 120, 220), pantalon=(40, 40, 60), pelo=(30, 30, 30)),
    dict(camisa=(250, 250, 250), pantalon=(80, 160, 120), pelo=(240, 210, 120)),
    dict(camisa=(160, 100, 220), pantalon=(60, 60, 70), pelo=(40, 30, 20), gorra=(220, 70, 70)),
    dict(camisa=(255, 170, 60), pantalon=(70, 90, 160), pelo=(90, 60, 40)),
]


def sombra_c(c, k=0.75):
    return tuple(int(v * k) for v in c)


def cubo(L, x, y, w, h, col, prof=8, a=1.0):
    """Bloque con cara frontal, lateral (derecha) y superior para dar volumen."""
    poly(L, [(x + w, y), (x + w + prof, y - prof * 0.7), (x + w + prof, y + h - prof * 0.7), (x + w, y + h)],
         sombra_c(col, 0.72), a=a)
    poly(L, [(x, y), (x + prof, y - prof * 0.7), (x + w + prof, y - prof * 0.7), (x + w, y)], mezcla(col, BLANCO, 0.18), a=a)
    rect(L, x, y, x + w, y + h, col, a=a)


def bloque(L, x, y, s=1.0, look=None, brazo=0.0, brazo2=0.0, paso=0.0, cara="feliz", a=1.0, luz=1.0, silueta=None):
    """Personaje de bloques visto de frente. (x, y) = pies."""
    look = look or VECINOS_LOOK[0]
    piel = (250, 214, 170)

    def C(c):
        if silueta:
            return silueta
        return tuple(int(v * luz) for v in c)
    pr = 7 * s
    # piernas
    lh = 64 * s
    for k, dx in enumerate((-17 * s, 1 * s)):
        dy = paso * 8 * s * (1 if k == 0 else -1)
        cubo(L, x + dx, y - lh + dy, 16 * s, lh - dy, C(look["pantalon"]), pr, a)
    # torso
    ty = y - lh - 62 * s
    cubo(L, x - 26 * s, ty, 52 * s, 64 * s, C(look["camisa"]), pr, a)
    # brazos (rotación sencilla desde el hombro)
    for lado, ang in ((-1, brazo), (1, brazo2)):
        hx = x + lado * 34 * s
        hy = ty + 6 * s
        largo = 58 * s
        ca, sa = math.cos(ang), math.sin(ang)
        wv = 15 * s
        pts = [(-wv / 2, 0), (wv / 2, 0), (wv / 2, largo), (-wv / 2, largo)]
        rot = [(hx + px * ca - py * sa * lado * -1, hy + px * sa * lado + py * ca) for px, py in pts]
        poly(L, rot, C(look["camisa"]), a=a)
        mx, my = rot[2][0] / 2 + rot[3][0] / 2, rot[2][1] / 2 + rot[3][1] / 2
        rect(L, mx - 8 * s, my - 2 * s, mx + 8 * s, my + 12 * s, C(piel), a=a, r=2 * s)
    # cabeza
    hs = 46 * s
    hx0, hy0 = x - hs / 2, ty - hs - 4 * s
    cubo(L, hx0, hy0, hs, hs, C(piel), pr, a)
    if not silueta:
        if look.get("rizos"):
            for k in range(7):
                circ(L, hx0 + 4 * s + k * 7 * s, hy0 + 2 * s, 9 * s, fill=C(look["pelo"]), a=a)
            circ(L, hx0 + hs, hy0 + 14 * s, 10 * s, fill=C(look["pelo"]), a=a)
        else:
            rect(L, hx0 - 1, hy0 - 6 * s, hx0 + hs + pr, hy0 + 10 * s, C(look["pelo"]), a=a)
        if look.get("gorra"):
            rect(L, hx0 - 2, hy0 - 16 * s, hx0 + hs + pr, hy0 + 2 * s, C(look["gorra"]), a=a, r=6 * s)
            rect(L, hx0 + hs * 0.4, hy0 - 2 * s, hx0 + hs + 16 * s, hy0 + 4 * s, C(look["gorra"]), a=a, r=2 * s)
        if look.get("casco"):
            rect(L, hx0 - 2, hy0 - 14 * s, hx0 + hs + pr, hy0 + 4 * s, C(look["casco"]), a=a, r=4 * s)
        ojos_y = hy0 + 22 * s
        tinta = (40, 34, 30)
        if cara == "feliz":
            for ex in (hx0 + 14 * s, hx0 + 32 * s):
                L.d.arc(P(ex - 4 * s, ojos_y - 4 * s, ex + 4 * s, ojos_y + 4 * s), 200, 340, fill=L.c(tinta, a),
                        width=max(1, int(2.2 * s * K)))
            L.d.arc(P(hx0 + 14 * s, hy0 + 24 * s, hx0 + 32 * s, hy0 + 38 * s), 20, 160, fill=L.c(tinta, a),
                    width=max(1, int(2.4 * s * K)))
        else:   # sorpresa / miedo
            for ex in (hx0 + 14 * s, hx0 + 32 * s):
                circ(L, ex, ojos_y, 3.2 * s, fill=tinta, a=a)
            circ(L, hx0 + 23 * s, hy0 + 35 * s, 4 * s, fill=tinta, a=a)


def casa(L, x, y, w, h, pared, tejado, noche=0.0, luz_on=1.0, letrero=None, letrero_col=None, cerrada=False):
    cubo(L, x, y - h, w, h, mezcla(pared, (30, 34, 60), noche * 0.6), 14)
    poly(L, [(x - 14, y - h), (x + w / 2 + 7, y - h - h * 0.45), (x + w + 28, y - h), (x + w + 14, y - h - 4)],
         mezcla(tejado, (20, 20, 40), noche * 0.6))
    # puerta y ventanas
    rect(L, x + w / 2 - 18, y - 60, x + w / 2 + 18, y, (90, 60, 40))
    for wx in (x + 14, x + w - 50):
        on = noche > 0.3 and luz_on > 0.5
        rect(L, wx, y - h + 30, wx + 36, y - h + 70, (255, 220, 120) if on else mezcla((140, 190, 230), (40, 50, 80), noche))
        linea(L, [(wx + 18, y - h + 30), (wx + 18, y - h + 70)], BLANCO, w=2)
    if letrero:
        rect(L, x + 6, y - h - 4, x + w - 6, y - h + 22, letrero_col or (220, 60, 60), r=3)
        texto(L, letrero, x + w / 2, y - h + 9, 14, BLANCO, fuente="black", sombra=False)
    if cerrada:
        linea(L, [(x + w / 2 - 22, y - 56), (x + w / 2 + 22, y - 6)], (200, 160, 60), w=5)
        linea(L, [(x + w / 2 + 22, y - 56), (x + w / 2 - 22, y - 6)], (200, 160, 60), w=5)


def arbol(L, x, y, s=1.0, noche=0.0):
    rect(L, x - 7 * s, y - 50 * s, x + 7 * s, y, mezcla((120, 80, 50), (30, 26, 40), noche * 0.6))
    for k, (dy, w) in enumerate(((-90, 60), (-125, 46), (-152, 30))):
        cubo(L, x - w * s / 2, y + dy * s, w * s, 38 * s, mezcla((60, 150, 70), (20, 40, 50), noche * 0.7), 8 * s)


def farola(L, x, y, on=1.0, noche=0.0):
    rect(L, x - 3, y - 160, x + 3, y, (60, 60, 70))
    rect(L, x - 14, y - 172, x + 14, y - 158, (60, 60, 70), r=3)
    if noche > 0.2 and on > 0:
        poly(L, [(x - 12, y - 158), (x + 12, y - 158), (x + 70, y), (x - 70, y)], (255, 230, 150), a=0.16 * on * noche)
        circ(L, x, y - 160, 9, fill=(255, 240, 180), a=on)
    else:
        circ(L, x, y - 160, 7, fill=(200, 200, 190))


def cielo(L, T, noche):
    for i in range(0, 700, 8):
        k = i / 700
        rect(L, 0, i, W, i + 8, mezcla(mezcla(CIELO_D, CIELO_D2, k), mezcla(CIELO_N, CIELO_N2, k), noche))
    if noche > 0.3:
        rs = random.Random(4)
        for _ in range(50):
            circ(L, rs.uniform(0, W), rs.uniform(0, 520), rs.uniform(0.6, 1.6), fill=BLANCO,
                 a=(noche - 0.3) * (0.5 + 0.5 * math.sin(T * 2 + rs.random() * 6)))
        circ(L, 440, 360, 34, fill=(240, 240, 220), a=noche)
        circ(L, 452, 352, 30, fill=mezcla(CIELO_N, CIELO_N2, 0.5), a=noche)
    else:
        circ(L, 450, 360, 36, fill=(255, 230, 120), a=1 - noche)
    # nubes de bloques
    for j in range(3):
        cx = (j * 220 + T * 12) % (W + 200) - 100
        for k in range(3):
            cubo(L, cx + k * 30, 420 - (k % 2) * 16 + j * 30, 40, 26, mezcla((250, 250, 255), (60, 66, 110), noche), 8, a=0.9)


def pueblo(L, T, noche=0.0, farolas=1.0, cartel=1.0, gente=True, pasos=False, caras="feliz", sin_luces=False,
           robado=False):
    cielo(L, T, noche)
    rect(L, 0, 700, W, 760, mezcla(CESPED_B, (20, 40, 40), noche * 0.7))
    luz_casas = 0 if sin_luces else 1
    casa(L, 20, 720, 140, 130, (230, 200, 160), (150, 80, 50), noche, luz_casas)
    casa(L, 200, 720, 150, 150, (200, 220, 240), (90, 70, 60), noche, luz_casas)
    casa(L, 390, 720, 130, 120, (240, 210, 210), (120, 60, 60), noche, luz_casas)
    arbol(L, 175, 724, 0.8, noche)
    arbol(L, 370, 724, 0.7, noche)
    rect(L, 0, 720, W, 770, mezcla(ACERA, (50, 54, 70), noche * 0.7))
    rect(L, 0, 770, W, H, mezcla(ASFALTO, (20, 22, 30), noche * 0.6))
    for x in range(0, W, 80):
        rect(L, x + 10, 856, x + 50, 864, mezcla(AMAR, (90, 80, 40), noche * 0.6))
    for x in (110, 430):
        farola(L, x, 770, on=farolas, noche=noche)
    # cartel de la ciudad
    cx = 270
    if cartel > 0:
        rect(L, cx - 6, 580, cx + 6, 722, (90, 90, 100), a=cartel)
        cubo(L, cx - 110, 540, 220, 70, mezcla((40, 120, 200), (20, 40, 90), noche * 0.5), 10, a=cartel)
        texto(L, CIUDAD, cx, 568, 40, BLANCO, a=cartel, fuente="black", sombra=False)
        texto(L, f"{VECINOS} habitantes", cx, 598, 14, (220, 235, 250), a=cartel, fuente="bold", sombra=False)
    elif robado:
        rect(L, cx - 6, 590, cx + 6, 722, (90, 90, 100))
        linea(L, [(cx - 30, 600), (cx + 26, 586)], (90, 90, 100), w=3)
    if gente:
        luz = 1.0 - 0.45 * noche
        for j, (x, look) in enumerate(zip((60, 150, 250, 350, 450), VECINOS_LOOK)):
            br = 0.4 * math.sin(T * 6 + j) if not pasos else 0
            bloque(L, x, 900, 0.95, look, brazo=0.1, brazo2=-0.2 - (0.6 + br if j % 2 == 0 and noche < 0.5 else 0),
                   paso=math.sin(T * 8 + j) if pasos else 0, cara=caras, luz=luz)


def oscuridad(L, k):
    if k > 0:
        rect(L, 0, 0, W, H, (0, 0, 8), a=k)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    tn = wt(e, "anoche") - 0.2
    noche = eio(prog(t, tn, 1.4))
    pueblo(L, T, noche=noche, caras="feliz" if t < tn + 1.0 else "susto")
    st["overlay"].append(("titular", t, e, noche))


def esc_presentacion(L, e, t, D, T, st):
    pueblo(L, T, noche=0.0)
    q = prog(t, wt(e, "seguidor") - 0.2, 0.4)
    if q > 0:
        st["overlay"].append(("etiquetas", q, t))


def esc_apagon(L, e, t, D, T, st):
    ta = wt(e, "apagaron") - 0.3
    apaga = prog(t, ta, 0.25)
    parpadeo = 1.0 if t < ta else (0 if apaga >= 1 else (0.5 + 0.5 * math.sin(t * 60)) * (1 - apaga))
    pueblo(L, T, noche=1.0, farolas=parpadeo, gente=False, sin_luces=apaga > 0.5)
    oscuridad(L, 0.55 * apaga)
    st["overlay"].append(("reloj", prog(t, wt(e, "tres") - 0.2, 0.3)))


def esc_robo(L, e, t, D, T, st):
    tl = wt(e, "luz") - 0.3
    vuelve = prog(t, tl, 0.4)
    pueblo(L, T, noche=1.0, farolas=vuelve, cartel=0.0, gente=vuelve > 0.5, caras="susto", sin_luces=vuelve < 0.5)
    oscuridad(L, 0.55 * (1 - vuelve))
    if vuelve > 0.5:
        # postes vacíos donde estaba el cartel
        rect(L, 264, 590, 276, 722, (90, 90, 100))
        st["overlay"].append(("vacio", prog(t, wt(e, "desaparecido") - 0.3, 0.4), t))


def esc_llamada(L, e, t, D, T, st):
    pueblo(L, T, noche=1.0, caras="susto", cartel=0.0, robado=True)
    tp = wt(e, "problema") - 0.2
    st["overlay"].append(("telefono", t, prog(t, tp, 0.3)))
    tn = wt(e, "policía", 1) - 0.4
    if t > tn:
        st["overlay"].append(("sin_policia", prog(t, tn, 0.35)))


def esc_vacios(L, e, t, D, T, st):
    cielo(L, T, 1.0)
    rect(L, 0, 720, W, H, (40, 44, 60))
    edificios = [("POLICÍA", (40, 80, 180), None), ("bomberos", (200, 50, 50), "BOMBEROS"),
                 ("médicos", (240, 240, 245), "HOSPITAL"), ("alcalde", (230, 200, 120), "AYUNTAMIENTO")]
    for j, (pal, col, rot) in enumerate(edificios):
        x = 18 + j * 130
        q = 1.0 if j == 0 else prog(t, wt(e, pal) - 0.25, 0.35)
        if q <= 0:
            continue
        casa(L, x, 760, 104, 140 * eob(q) + 1, col, (60, 60, 80), noche=0.7, luz_on=0, letrero=rot or "POLICÍA",
             letrero_col=(30, 30, 40), cerrada=True)
        st["overlay"].append(("se_busca", x + 52, 840, q))


def esc_nota(L, e, t, D, T, st):
    th = wt(e, "huella") - 0.3
    tn = wt(e, "nota") - 0.3
    if t < tn:
        rect(L, 0, 0, W, H, (24, 26, 40))
        rect(L, 0, 600, W, H, (60, 62, 76))
        q = prog(t, th, 0.4)
        # huella de bloque iluminada por una linterna
        circ(L, 270, 760, 150, fill=(255, 240, 190), a=0.18)
        for k in range(2):
            x = 230 + k * 70
            y = 740 - k * 40
            rect(L, x - 20, y - 34, x + 20, y + 34, (30, 30, 40), a=q, r=4)
            for j in range(3):
                rect(L, x - 16 + j * 12, y - 52, x - 8 + j * 12, y - 40, (30, 30, 40), a=q, r=2)
        # silueta misteriosa en el tejado
        cubo(L, 340, 560, 200, 40, (34, 36, 52), 12)
        bloque(L, 450, 560, 0.7, silueta=(6, 6, 14), brazo=0.2, brazo2=-0.2)
        circ(L, 440, 470, 3, fill=(255, 60, 60), a=0.6 + 0.4 * math.sin(t * 5))
        circ(L, 456, 470, 3, fill=(255, 60, 60), a=0.6 + 0.4 * math.sin(t * 5))
    else:
        rect(L, 0, 0, W, H, (24, 26, 40))
        st["overlay"].append(("papel", prog(t, tn, 0.4), t - tn))


def esc_cta(L, e, t, D, T, st):
    pueblo(L, T, noche=0.7, gente=True, cartel=0.0, robado=True)
    oscuridad(L, 0.35)
    roles = [("policía", "POLICÍA", (40, 80, 200)), ("bombero", "BOMBERO", (210, 50, 50)),
             ("médico", "MÉDICO", (60, 180, 120)), ("alcalde", "ALCALDE", (220, 170, 40)), ("ladrón", "¿EL LADRÓN?", (20, 20, 30))]
    for j, (pal, txt, col) in enumerate(roles):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("rol", txt, col, j, q))
    for k, pal in enumerate(("Síguenos", "comparte", "comenta")):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("boton", k, q, t))


def esc_promesa(L, e, t, D, T, st):
    tp = wt(e, "puesto") - 0.2
    pueblo(L, T, noche=0.0, gente=t < tp, cartel=0.0, robado=True)
    if t >= tp:
        uniformes = [dict(camisa=(40, 80, 200), pantalon=(30, 40, 80), pelo=(40, 30, 20), gorra=(30, 50, 140)),
                     dict(camisa=(220, 60, 40), pantalon=(60, 50, 40), pelo=(40, 30, 20), casco=(250, 200, 40)),
                     dict(camisa=(245, 245, 250), pantalon=(120, 200, 190), pelo=(90, 60, 40))]
        for j, (x, look) in enumerate(zip((110, 270, 430), uniformes)):
            q = prog(t, tp + j * 0.15, 0.35)
            bloque(L, x, 900 + 30 * (1 - eob(q)), 1.0, look, brazo=0.1, brazo2=-0.9 + 0.3 * math.sin(T * 6 + j))
    # vecinos con uniformes futuros (adelanto del siguiente vídeo)
    st["overlay"].append(("progreso", prog(t, wt(e, "mil") - 0.3, 1.2)))
    q = prog(t, wt(e, "puesto") - 0.2, 0.4)
    if q > 0:
        st["overlay"].append(("tags_tu", q))
    qr = prog(t, wt(e, "robó") - 0.3, 0.4)
    if qr > 0:
        st["overlay"].append(("quien", qr))


def esc_final(L, e, t, D, T, st):
    pueblo(L, T, noche=1.0, gente=True, cartel=0.0, robado=True)
    st["overlay"].append(("final", t))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "presentacion": esc_presentacion, "apagon": esc_apagon, "robo": esc_robo,
         "llamada": esc_llamada, "vacios": esc_vacios, "nota": esc_nota, "cta": esc_cta, "promesa": esc_promesa,
         "final": esc_final}


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "titular":
            _, t, e, noche = it
            s = 1 + 0.4 * math.exp(-t * 9)
            texto(O, f"{VECINOS}", 270, 345, 90 * s, AMAR, fuente="black")
            texto(O, "VECINOS EN ESTE PUEBLO", 270, 405, 22 * s, TXT, fuente="black")
            if noche > 0.5:
                q = prog(noche, 0.5, 0.5)
                texto(O, "…y anoche pasó algo", 270, 600, 26, (255, 120, 120), a=q, fuente="black")
        elif tipo == "etiquetas":
            _, q, t = it
            for j, x in enumerate((60, 150, 250, 350, 450)):
                qq = prog(q, j * 0.12, 0.4)
                w = 70
                rect(O, x - w / 2, 690, x + w / 2, 712, (0, 0, 0), a=0.6 * qq, r=11)
                texto(O, "@seguidor", x, 701, 10, BLANCO, a=qq, fuente="bold", sombra=False)
        elif tipo == "reloj":
            q = it[1]
            if q > 0:
                rect(O, 170, 330, 370, 410, (0, 0, 0), a=0.75 * q, r=14)
                texto(O, "03:00", 270, 370, 48, (255, 80, 80), a=q, fuente="mono", sombra=False)
        elif tipo == "vacio":
            _, q, t = it
            if q > 0:
                texto(O, "?", 270, 520, 110 * (0.7 + 0.3 * eob(q)), (255, 80, 80), a=q, fuente="black")
                texto(O, "EL CARTEL HA DESAPARECIDO", 270, 400, 22, TXT, a=q, fuente="black")
        elif tipo == "telefono":
            _, t, qp = it
            x, y = 270, 470
            rect(O, x - 50, y - 90, x + 50, y + 90, (20, 20, 24), r=14)
            rect(O, x - 42, y - 78, x + 42, y + 70, (40, 60, 90), r=6)
            texto(O, "112", x, y - 40, 26, BLANCO, fuente="black", sombra=False)
            puntos = "." * (1 + int(t * 3) % 3)
            texto(O, "llamando" + puntos if qp < 1 else "sin respuesta", x, y, 12, BLANCO, fuente="bold", sombra=False)
            for k in range(3):
                u = (t * 1.2 + k / 3) % 1
                O.d.arc(P(x + 40 - 20 * u, y - 100 - 20 * u, x + 100 + 20 * u, y - 40 + 20 * u), 270, 360,
                        fill=O.c(BLANCO, 1 - u), width=2 * K)
        elif tipo == "sin_policia":
            q = it[1]
            s = 1 + 1.3 * (1 - eo3(q))
            w = ancho("NO HAY POLICÍA", 30 * s) + 30 * s
            rect(O, 270 - w / 2, 640 - 26 * s, 270 + w / 2, 640 + 26 * s, (200, 40, 40), a=q, r=10)
            texto(O, "NO HAY POLICÍA", 270, 640, 30 * s, BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "se_busca":
            _, x, y, q = it
            rect(O, x - 48, y - 30, x + 48, y + 30, (240, 230, 200), a=q, r=4)
            texto(O, "SE BUSCA", x, y - 12, 13, (160, 40, 40), a=q, fuente="black", sombra=False)
            texto(O, "¿TÚ?", x, y + 10, 18, (40, 40, 40), a=q, fuente="black", sombra=False)
        elif tipo == "papel":
            _, q, dt = it
            ang = 0
            rect(O, 70, 380, 470, 720, (240, 236, 220), a=q, r=4)
            txt = "Volveré cuando seáis"
            n = int(len(txt) * cl(dt / 1.2))
            texto(O, txt[:n], 270, 480, 30, (40, 40, 60), a=q, fuente="semi", sombra=False)
            q2 = prog(dt, 1.2, 0.4)
            texto(O, "1.000", 270, 570, 80 * (0.7 + 0.3 * eob(q2)), (200, 40, 40), a=q2, fuente="black", sombra=False)
            texto(O, "— ?", 420, 670, 22, (80, 80, 90), a=q2, fuente="semi", anchor="rm", sombra=False)
            _ = ang
        elif tipo == "rol":
            _, txt, col, j, q = it
            y = 330 + j * 56
            w = ancho(txt, 24) + 40
            x = 270
            s = eob(q)
            rect(O, x - w / 2 * s, y - 22, x + w / 2 * s, y + 22, col, a=q, r=22)
            texto(O, txt, x, y, 24 * (0.7 + 0.3 * s), BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "boton":
            _, k, q, t = it
            etiquetas = [("+ SEGUIR", (254, 44, 85)), ("↗ COMPARTIR", (40, 160, 230)), ("💬 COMENTA", (255, 190, 40))]
            txt, col = etiquetas[k]
            txt = txt.replace("💬 ", "✎ ")
            x, y = 270, 650 + k * 56
            s = eob(q) * (1 + 0.04 * math.sin(t * 6 + k))
            rect(O, x - 120 * s, y - 22 * s, x + 120 * s, y + 22 * s, col, a=q, r=22 * s)
            texto(O, txt, x, y, 20 * s, BLANCO, a=q, fuente="sym", sombra=False)
        elif tipo == "progreso":
            q = it[1]
            rect(O, 60, 340, 480, 376, (0, 0, 0), a=0.65, r=18)
            frac = VECINOS / META
            rect(O, 64, 344, 64 + 412 * frac * eo3(q), 372, AMAR, r=14)
            texto(O, f"{VECINOS} / {META:,}".replace(",", "."), 270, 358, 16, (20, 20, 20) if q > 0.5 else BLANCO,
                  fuente="black", sombra=False)
            texto(O, "OBJETIVO: 1.000 VECINOS", 270, 400, 20, TXT, fuente="black")
        elif tipo == "tags_tu":
            q = it[1]
            for j, (x, rol) in enumerate(((110, "POLICÍA"), (270, "BOMBERO"), (430, "MÉDICO"))):
                qq = prog(q, j * 0.15, 0.5)
                rect(O, x - 56, 690, x + 56, 736, (0, 0, 0), a=0.7 * qq, r=12)
                texto(O, "@¿tú?", x, 704, 14, AMAR, a=qq, fuente="black", sombra=False)
                texto(O, rol, x, 724, 11, BLANCO, a=qq, fuente="bold", sombra=False)
        elif tipo == "quien":
            q = it[1]
            texto(O, "¿QUIÉN FUE?", 270, 610, 44 * (0.8 + 0.2 * eob(q)), (255, 90, 90), a=q, fuente="black")
        elif tipo == "final":
            t = it[1]
            s = 1 + 0.04 * math.sin(t * 4)
            texto(O, CIUDAD, 270, 360, 70 * s, AMAR, fuente="black")
            texto(O, "TE NECESITA", 270, 420, 30, TXT, fuente="black")
            tt = (t % 2.0)
            toque = prog(tt, 0.8, 0.3)
            r = 26 * (1 - 0.15 * math.sin(toque * math.pi))
            circ(O, 270, 540, 56, fill=(40, 120, 200))
            texto(O, "M", 270, 540, 50, BLANCO, fuente="black", sombra=False)
            circ(O, 270, 600, r, fill=(254, 44, 85) if toque < 0.5 else BLANCO)
            texto(O, "+" if toque < 0.5 else "✓", 270, 600, 28, BLANCO if toque < 0.5 else (254, 44, 85), fuente="sym",
                  sombra=False)
            if 0 < toque < 1:
                circ(O, 270, 600, 26 + 40 * toque, outline=(254, 44, 85), w=3, a=1 - toque)


def cabecera(O, st):
    if st.get("sin_cabecera"):
        return
    w = ancho(CABECERA, 15) + 30
    rect(O, 270 - w / 2, 148, 270 + w / 2, 180, (40, 120, 200), a=0.95, r=16)
    texto(O, CABECERA, 270, 164, 15, BLANCO, fuente="black", sombra=False)


def fecha(O, e, t):
    return


def paso(O, st, t):
    if not st.get("paso") or st.get("sin_paso"):
        return
    n, txt = st["paso"]
    q = eo3(prog(t, 0.05, 0.4))
    s = f"{n}"
    w = ancho(txt, 19, "black") + 74
    x0 = 270 - w / 2 + 30 * (1 - q)
    rect(O, x0, 128, x0 + w, 172, (0, 0, 0), a=0.55 * q, r=22)
    circ(O, x0 + 24, 150, 16, fill=AMARILLO, a=q)
    texto(O, s, x0 + 24, 150, 18, (20, 20, 20), a=q, fuente="black" if s.isdigit() else "sym", sombra=False)
    texto(O, txt, x0 + 48, 150, 19, BLANCO, a=q, fuente="black", anchor="lm", sombra=False)


def subtitulos(O, T):
    for ini, fin, bloque in SUBS:
        if ini <= T < fin:
            size = 44
            f_w = [ancho(w[0], size) for w in bloque]
            esp = ancho(" ", size)
            total = sum(f_w) + esp * (len(f_w) - 1)
            lineas = [list(range(len(bloque)))]
            if total > 470:
                lineas = [list(range(len(bloque) - 1)), [len(bloque) - 1]]
            y0 = 250 - (len(lineas) - 1) * 26
            for li, idxs in enumerate(lineas):
                tw = sum(f_w[i] for i in idxs) + esp * (len(idxs) - 1)
                x = 270 - tw / 2
                for i in idxs:
                    w, t0, t1 = bloque[i]
                    dicha = T >= t0
                    pop = eob(prog(T, t0, 0.18)) if dicha else 0
                    limpio = w.lower().strip("¿?¡!.,:")
                    col = AMARILLO if limpio in CLAVE and dicha else BLANCO
                    a = 1.0 if dicha else 0.0
                    s = size * (0.85 + 0.15 * pop) if dicha else size
                    texto(O, w, x + f_w[i] / 2, y0 + li * 54 + 4 * (1 - pop), s, col, a=a, fuente="black")
                    x += f_w[i] + esp
            break












# ------------------------------------------------------------------ render
def escena_en(T):
    for e in ESC:
        if e["t0"] <= T < e["t0"] + e["dur"]:
            return e
    return ESC[-1]


# instantes en que se pronuncia una palabra clave (para el «zoom punch»)
GOLPES = []
for _e in ESC:
    for _w in _e["palabras"]:
        if _w["w"].lower().strip("¿?¡!.,:…") in CLAVE:
            GOLPES.append(_e["voz_t0"] + _w["t"])
GOLPES.sort()


def golpe_zoom(T):
    import bisect
    k = bisect.bisect_right(GOLPES, T) - 1
    if k < 0:
        return 0.0
    return 0.045 * math.exp(-(T - GOLPES[k]) * 9)


_VIN = None


def VINETA():
    global _VIN
    if _VIN is None:
        sw, sh = IW // 8, IH // 8
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        r = np.sqrt(((xx - sw / 2) / sw) ** 2 + ((yy - sh / 2) / sh) ** 2 * 0.8)
        v = np.clip(1.3 - r * 1.0, 0.55, 1)
        _VIN = Image.fromarray((v * 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR).convert("RGB")
    return _VIN


def render_frame(fr):
    T = fr / FPS
    e = escena_en(T)
    t = T - e["t0"]
    D = e["dur"]
    img = Image.new("RGB", (IW, IH), (0, 0, 0))
    L = Capa(img)
    st = {"overlay": []}
    FUNCS[e["nombre"]](L, e, t, D, T, st)
    z = 1.03 + 0.05 * eio(t / D) + golpe_zoom(T)
    cw, ch = IW / z, IH / z
    sh = st.get("shake", 0)
    x0 = (IW - cw) / 2 + sh * K * math.sin(T * 61)
    y0 = (IH - ch) / 2 + 10 * K + sh * K * math.cos(T * 47)
    img = L.img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    if st.get("oscuro"):
        img = Image.blend(img, Image.new("RGB", (IW, IH), (0, 0, 0)), st["oscuro"])
    if st.get("flash"):
        img = Image.blend(img, Image.new("RGB", (IW, IH), (255, 255, 250)), cl(st["flash"]))
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    overlays(O, st, T)
    cabecera(O, st)
    fecha(O, e, t)
    subtitulos(O, T)
    out = O.img
    if T > TOTAL - 0.5:
        out = Image.blend(out, Image.new("RGB", (IW, IH), (0, 0, 8)), cl((T - (TOTAL - 0.5)) / 0.5))
    return out.resize((OW, OH), Image.LANCZOS).tobytes()


# ------------------------------------------------------------------ audio
def leer(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def colocar(buf, x, t0, g=1.0):
    a0 = int(t0 * SR)
    if a0 >= len(buf) or a0 < 0:
        return
    n = min(len(x), len(buf) - a0)
    buf[a0:a0 + n] += x[:n] * g


def latido():
    n = int(0.5 * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for t0, amp in ((0, 1.0), (0.17, 0.7)):
        u = np.clip(tt - t0, 0, None)
        s += amp * np.sin(2 * np.pi * 52 * u) * np.exp(-u * 18) * (tt >= t0)
    return s


def whoosh(seed, dur=0.5):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32)
    y = np.zeros(n, np.float32)
    lp = bp = 0.0
    for i in range(n):
        c = 0.02 + 0.3 * math.sin(i / n * math.pi)
        lp += c * (x[i] - lp)
        bp += c * (lp - bp)
        y[i] = lp - bp
    return y * np.sin(np.linspace(0, np.pi, n)) ** 2


def golpe():
    n = int(1.0 * SR)
    tt = np.arange(n) / SR
    rng = np.random.default_rng(9)
    s = np.sin(2 * np.pi * (40 + 70 * np.exp(-tt * 10)) * tt) * np.exp(-tt * 4)
    s += 0.6 * rng.standard_normal(n) * np.exp(-tt * 14)
    return s.astype(np.float32)


def sirena(dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 750 + 350 * np.sin(2 * np.pi * 0.9 * tt)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * 0.5 + 0.2 * np.sin(2 * ph)
    env = np.clip(tt / 0.5, 0, 1) * np.clip((dur - tt) / 0.8, 0, 1)
    return (s * env).astype(np.float32)




def splash():
    n = int(1.6 * SR)
    tt = np.arange(n) / SR
    rng = np.random.default_rng(3)
    ruido = rng.standard_normal(n).astype(np.float32)
    y = np.zeros(n, np.float32)
    lp = 0.0
    for i in range(n):
        c = 0.5 * math.exp(-i / SR * 3) + 0.03
        lp += c * (ruido[i] - lp)
        y[i] = lp
    s = y * np.exp(-tt * 2.2) * 1.4 + np.sin(2 * np.pi * (50 + 60 * np.exp(-tt * 8)) * tt) * np.exp(-tt * 5)
    return s.astype(np.float32)


def cristal():
    n = int(1.2 * SR)
    tt = np.arange(n) / SR
    rng = np.random.default_rng(8)
    s = np.diff(rng.standard_normal(n + 1)).astype(np.float32) * np.exp(-tt * 9) * 0.5
    for j in range(14):
        t0 = rng.uniform(0.02, 0.7)
        f = rng.uniform(2500, 6500)
        u = np.clip(tt - t0, 0, None)
        s += 0.12 * np.sin(2 * np.pi * f * u) * np.exp(-u * 30) * (tt >= t0)
    return s


def burbuja(seed):
    rng = np.random.default_rng(seed)
    n = int(0.09 * SR)
    tt = np.arange(n) / SR
    f0 = rng.uniform(400, 900)
    return (np.sin(2 * np.pi * (f0 + 3000 * tt) * tt) * np.exp(-tt * 40)).astype(np.float32)


def tic():
    n = int(0.05 * SR)
    tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2000 * tt) * np.exp(-tt * 120)).astype(np.float32)






def nota(m):
    return 440 * 2 ** ((m - 69) / 12)




def nota(m):
    return 440 * 2 ** ((m - 69) / 12)


def piano(f, dur, vol):
    n = int(dur * SR)
    u = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * u) + 0.4 * np.sin(4 * np.pi * f * u) + 0.15 * np.sin(6 * np.pi * f * u)
    return (vol * s * np.exp(-u * 3.5) * np.clip(u / 0.005, 0, 1)).astype(np.float32)




def ruido_filtrado(n, ancho_lp, seed, hp=None):
    rng = np.random.default_rng(seed)
    r = rng.standard_normal(n).astype(np.float32)
    r = np.convolve(r, np.ones(ancho_lp) / ancho_lp, mode="same")
    if hp:
        r = r - np.convolve(r, np.ones(hp) / hp, mode="same")
    return r / (np.abs(r).max() + 1e-6)




def ruido(n, lp, seed, hp=None):
    rng = np.random.default_rng(seed)
    r = rng.standard_normal(n).astype(np.float32)
    if lp > 1:
        r = np.convolve(r, np.ones(lp) / lp, mode="same")
    if hp:
        r = r - np.convolve(r, np.ones(hp) / hp, mode="same")
    return r / (np.abs(r).max() + 1e-6)


def saw(f, tt, armonicos=8):
    s = np.zeros_like(tt)
    for k in range(1, armonicos + 1):
        s += np.sin(2 * np.pi * f * k * tt) / k
    return s


def braam(dur=3.0):
    """Impacto grave de tráiler."""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = 0.5 * saw(36.7, tt, 12) + 0.4 * saw(55, tt, 10) + 0.3 * saw(73.4, tt, 8)
    s = np.convolve(s, np.ones(40) / 40, mode="same")
    env = np.clip(tt / 0.04, 0, 1) * np.exp(-tt * 0.9)
    sub = np.sin(2 * np.pi * (30 + 30 * np.exp(-tt * 4)) * tt) * np.exp(-tt * 1.5)
    return ((s * 0.5 + sub) * env * 0.5).astype(np.float32)


def braam(dur=3.0):
    """Impacto grave de tráiler."""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = 0.5 * saw(36.7, tt, 12) + 0.4 * saw(55, tt, 10) + 0.3 * saw(73.4, tt, 8)
    s = np.convolve(s, np.ones(40) / 40, mode="same")
    env = np.clip(tt / 0.04, 0, 1) * np.exp(-tt * 0.9)
    sub = np.sin(2 * np.pi * (30 + 30 * np.exp(-tt * 4)) * tt) * np.exp(-tt * 1.5)
    return ((s * 0.5 + sub) * env * 0.5).astype(np.float32)


def procesar_voz(x):
    """EQ con más graves, compresión y una reverberación sutil (con ffmpeg)."""
    ent = os.path.join(BUILD, "voz_cruda.wav")
    sal = os.path.join(BUILD, "voz_proc.wav")
    with wave.open(ent, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    filtro = ("highpass=f=60,equalizer=f=140:t=q:w=1.2:g=5,equalizer=f=350:t=q:w=1:g=-2,"
              "equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-22dB:ratio=3.5:attack=4:release=90:makeup=3,"
              "aecho=0.85:0.5:55|95:0.14|0.09")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", ent, "-af", filtro, "-ar", str(SR), "-ac", "1", sal])
    return leer(sal)[:len(x)]




def pop():
    n = int(0.25 * SR)
    u = np.arange(n) / SR
    return (np.sin(2 * np.pi * (500 + 900 * u * 4) * u) * np.exp(-u * 18) * 0.6).astype(np.float32)


def caja():
    n = int(0.9 * SR)
    u = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 2100 * u) + np.sin(2 * np.pi * 2650 * u)) * np.exp(-u * 6) * 0.3
    s[:int(0.05 * SR)] += np.random.default_rng(1).standard_normal(int(0.05 * SR)) * 0.2
    return s.astype(np.float32)


def piano(f, dur, vol):
    n = int(dur * SR)
    u = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * u) + 0.4 * np.sin(4 * np.pi * f * u) + 0.15 * np.sin(6 * np.pi * f * u)
    return (vol * s * np.exp(-u * 3.5) * np.clip(u / 0.005, 0, 1)).astype(np.float32)


def ping():
    n = int(0.35 * SR)
    u = np.arange(n) / SR
    return ((np.sin(2 * np.pi * 1760 * u) + 0.5 * np.sin(2 * np.pi * 2640 * u)) * np.exp(-u * 12) * 0.35).astype(np.float32)


def mazo():
    n = int(0.6 * SR)
    u = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 220 * u) + 0.6 * np.sin(2 * np.pi * 540 * u)) * np.exp(-u * 25)
    s += np.random.default_rng(3).standard_normal(n) * np.exp(-u * 60) * 0.5
    return (s * 0.7).astype(np.float32)


def monedas(dur=1.5):
    out = np.zeros(int(dur * SR), np.float32)
    rng = np.random.default_rng(6)
    for _ in range(14):
        t0 = rng.uniform(0, dur - 0.2)
        m = int(0.15 * SR)
        u = np.arange(m) / SR
        f = rng.uniform(3000, 5200)
        colocar(out, (np.sin(2 * np.pi * f * u) * np.exp(-u * 35) * 0.25).astype(np.float32), t0)
    return out


def subida(dur=1.2):
    n = int(dur * SR)
    u = np.arange(n) / SR
    r = np.random.default_rng(9).standard_normal(n).astype(np.float32)
    f = 200 + 1800 * (u / dur) ** 2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + np.diff(r, prepend=0) * 0.1
    return (s * (u / dur) ** 2).astype(np.float32)




def cuadrada(f, dur, vol, duty=0.5):
    n = int(dur * SR)
    u = np.arange(n) / SR
    s = np.where((u * f) % 1 < duty, 1.0, -1.0)
    s = np.convolve(s, np.ones(6) / 6, mode="same")
    return (s * vol * np.exp(-u * 3) * np.clip(u / 0.005, 0, 1)).astype(np.float32)


def es_noche(T):
    n = escena_en(T)["nombre"]
    return n in ("apagon", "robo", "llamada", "vacios", "nota", "final") or (n == "gancho" and T > 3.5)


def musica(n):
    """Chiptune alegre de día; caja de música misteriosa de noche."""
    out = np.zeros(n, np.float32)
    beat = 60 / 126
    dia_mel = [72, 76, 79, 76, 77, 81, 79, 77, 76, 79, 84, 79, 77, 74, 72, 74]
    noche_mel = [69, 72, 76, 75, 69, 72, 71, 68]
    bajo = [48, 48, 53, 55]
    k = 0
    while k * beat / 2 < TOTAL:
        t0 = k * beat / 2
        nf = lambda m: 440 * 2 ** ((m - 69) / 12)
        if not es_noche(t0):
            colocar(out, cuadrada(nf(dia_mel[k % 16]), 0.22, 0.035, 0.25), t0)
            if k % 2 == 0:
                colocar(out, cuadrada(nf(bajo[(k // 8) % 4] - 12), 0.3, 0.05, 0.5), t0)
            if k % 4 == 2:
                m2 = int(0.05 * SR)
                r = np.random.default_rng(k).standard_normal(m2).astype(np.float32)
                colocar(out, r * 0.05 * np.exp(-np.arange(m2) / SR * 80), t0)
        else:
            if k % 2 == 0:
                f = nf(noche_mel[(k // 2) % 8] + 12)
                m = int(1.2 * SR)
                u = np.arange(m) / SR
                colocar(out, ((np.sin(2 * np.pi * f * u) + 0.3 * np.sin(2 * np.pi * 3 * f * u)) * np.exp(-u * 3) * 0.035)
                        .astype(np.float32), t0)
            if k % 8 == 0:
                m = int(2.0 * SR)
                u = np.arange(m) / SR
                colocar(out, (np.sin(2 * np.pi * 55 * u) * np.exp(-u * 1.2) * 0.07).astype(np.float32), t0)
        k += 1
    return out


def grillos(n):
    tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * 4300 * tt) * (np.sin(2 * np.pi * 30 * tt) > 0.6) * ((tt * 1.7) % 1 < 0.35)
    return (s * 0.02).astype(np.float32)


def apagon_s():
    m = int(1.4 * SR)
    u = np.arange(m) / SR
    f = 120 * np.exp(-u * 2.2) + 30
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-u * 1.5) * 0.5
    return s.astype(np.float32)


def tono_llamada(veces=2):
    out = np.zeros(int(veces * 1.5 * SR), np.float32)
    for k in range(veces):
        m = int(0.9 * SR)
        u = np.arange(m) / SR
        colocar(out, ((np.sin(2 * np.pi * 425 * u)) * 0.12).astype(np.float32), k * 1.5)
    return out


def buho():
    m = int(1.2 * SR)
    u = np.arange(m) / SR
    s = np.zeros(m, np.float32)
    for t0, d in ((0.0, 0.35), (0.5, 0.6)):
        uu = np.clip(u - t0, 0, None)
        env = np.sin(np.pi * np.clip(uu / d, 0, 1)) * (u >= t0) * (u <= t0 + d)
        s += np.sin(2 * np.pi * (380 - 40 * uu) * uu) * env * 0.2
    return s


def mezclar():
    n = int((TOTAL + 0.3) * SR)
    voz = np.zeros(n, np.float32)
    for e in ESC:
        colocar(voz, leer(os.path.join(BUILD, f"voz_{e['i']}.mp3")), e["voz_t0"])
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    voz = procesar_voz(voz)
    voz = np.pad(voz, (0, max(0, n - len(voz))))[:n]
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    tt = np.arange(n) / SR
    mus = musica(n) * 0.9
    noche = np.array([1.0 if es_noche(min(x, TOTAL - 0.01)) else 0.0 for x in np.arange(0, TOTAL + 0.3, 0.05)])
    noche = np.interp(tt, np.arange(0, TOTAL + 0.3, 0.05)[:len(noche)], np.convolve(noche, np.ones(10) / 10, mode="same"))
    fx = grillos(n) * noche.astype(np.float32)
    E = {e["nombre"]: e for e in ESC}
    colocar(fx, pop(), 0.0, 0.6)
    colocar(fx, braam(), E["gancho"]["t0"] + wt(E["gancho"], "anoche") - 0.2, 0.7)
    a = E["apagon"]
    colocar(fx, apagon_s(), a["t0"] + wt(a, "apagaron") - 0.3, 0.8)
    colocar(fx, ping(), a["t0"] + wt(a, "tres") - 0.2, 0.4)
    r = E["robo"]
    colocar(fx, braam(), r["t0"] + wt(r, "desaparecido") - 0.3, 0.8)
    colocar(fx, buho(), r["t0"] + 0.6, 0.5)
    ll = E["llamada"]
    colocar(fx, tono_llamada(2), ll["t0"] + 0.3, 0.6)
    colocar(fx, golpe(), ll["t0"] + wt(ll, "policía", 1) - 0.4, 0.6)
    v = E["vacios"]
    for pal in ("bomberos", "médicos", "alcalde"):
        colocar(fx, golpe() * 0.6, v["t0"] + wt(v, pal) - 0.25, 0.5)
    nt = E["nota"]
    colocar(fx, subida(1.2), nt["t0"] + wt(nt, "nota") - 1.2, 0.5)
    colocar(fx, braam(), nt["t0"] + wt(nt, "mil") - 0.2, 0.9)
    c = E["cta"]
    for pal in ("Síguenos", "comparte", "comenta", "policía", "bombero", "médico", "alcalde", "ladrón"):
        colocar(fx, pop(), c["t0"] + wt(c, pal) - 0.2, 0.4)
    p = E["promesa"]
    colocar(fx, ping(), p["t0"] + wt(p, "mil") - 0.3, 0.5)
    colocar(fx, braam(), p["t0"] + wt(p, "robó") - 0.3, 0.6)
    fi = E["final"]
    for k in range(3):
        colocar(fx, pop(), fi["t0"] + 0.8 + k * 2.0, 0.5)
    for k, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(k, 0.4), e["t0"] - 0.2, 0.3)
    envv = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.55 * np.clip(envv * 12, 0, 1)
    total = voz + (mus + fx) * duck
    total *= np.clip((TOTAL - tt) / 0.5, 0, 1)
    total = np.tanh(total * 1.1) * 0.95
    ruta = os.path.join(BUILD, "mezcla.wav")
    with wave.open(ruta, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((total * 32767).astype(np.int16).tobytes())
    return ruta


def main():
    if sys.argv[1:2] == ["--preview"]:
        for s in sys.argv[2:]:
            Image.frombytes("RGB", (OW, OH), render_frame(int(float(s) * FPS))).save(os.path.join(BUILD, f"prev_{s}.png"))
        return
    print(f"Duración {TOTAL:.1f}s · {NFRAMES} fotogramas")
    audio = mezclar()
    vid = os.path.join(BUILD, "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for k, buf in enumerate(pool.imap(render_frame, range(NFRAMES), chunksize=4)):
            ff.stdin.write(buf)
            if k % 200 == 0:
                print(f"  {k}/{NFRAMES}", flush=True)
    ff.stdin.close()
    ff.wait()
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", vid, "-i", audio, "-map", "0:v", "-map", "1:a",
                           "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000",
                           "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000", "-shortest",
                           "-movflags", "+faststart", SALIDA])
    print("listo:", SALIDA)


if __name__ == "__main__":
    main()
