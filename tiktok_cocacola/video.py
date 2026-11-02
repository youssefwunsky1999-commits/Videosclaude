"""TikTok vertical «El origen de la Coca-Cola»: historia ilustrada con estética de película antigua
(sepia, grano) para el siglo XIX y color para la era moderna; personajes planos, subtítulos palabra a
palabra, voz neuronal, música y efectos.

    python3 voz.py && python3 video.py        -> cocacola_tiktok.mp4"""
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
SALIDA = os.path.join(AQUI, "cocacola_tiktok.mp4")

W, H = 540, 960            # unidades de diseño (9:16)
K = 3                      # resolución interna = 1620x2880
IW, IH = W * K, H * K
OW, OH = 1080, 1920
FPS = 30
SR = 44100
VOZ_OFF = 0.12
COLA = 0.35

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


def dur_mp3(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", p]))


EXTRA = {"gancho": 0.3, "final": 1.2}
ESC = []
_t = 0.0
for i, seg in enumerate(DATOS):
    dv = dur_mp3(os.path.join(BUILD, f"voz_{i}.mp3"))
    d = VOZ_OFF + dv + COLA + EXTRA.get(seg["escena"], 0)
    ESC.append({"i": i, "nombre": seg["escena"], "t0": _t, "dur": d, "voz_t0": _t + VOZ_OFF + 0,
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
CLAVE = {"famosa", "medicinal", "prohibida", "1886", "morfina", "dolor", "vino", "coca", "alcohol", "azúcar",
         "cola", "gas", "coca-cola.", "centavos", "fracaso", "nueve", "1888", "arruinado", "imperio", "cupones",
         "marketing", "cocaína", "1903", "1915", "botella", "oscuras", "rota", "acorazada", "2.000", "millones",
         "dolor.", "síguenos", "historias", "coca-cola"}


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
            for seq, num in ((["dos", "mil"], "2.000"), (["uno", "uno", "dos"], "112")):
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


# --- Escenas del TikTok «El origen de la Coca-Cola» (se insertan en video.py al montarlo) ---

POSES.update({
    "mezcla": dict(rodilla=(4, 95), pie=(2, 190), cuello=(6, -150), cabeza=(14, -194), codo=(40, -96), mano=(82, -84),
                   codo2=(30, -100), mano2=(70, -100)),
    "pensando": dict(rodilla=(4, 95), pie=(2, 190), cuello=(0, -150), cabeza=(4, -196), codo=(30, -100), mano=(24, -166),
                     codo2=(-10, -80), mano2=(14, -60)),
    "senala": dict(rodilla=(4, 95), pie=(2, 190), cuello=(2, -150), cabeza=(8, -196), codo=(46, -150), mano=(96, -190),
                   codo2=(-8, -74), mano2=(-4, -10)),
    "dolor": dict(rodilla=(10, 92), pie=(4, 190), cuello=(18, -142), cabeza=(30, -184), codo=(30, -80), mano=(10, -40),
                  codo2=(20, -84), mano2=(-6, -50)),
})

SEPIA_ESCENAS = {"pemberton": 0.85, "vino": 0.85, "receta": 0.85, "soda": 0.8, "fracaso": 0.9, "candler": 0.45,
                 "coca": 0.35, "final": 0.7}
ANIO = {"pemberton": "1886", "vino": "1886", "receta": "1886", "soda": "1886", "fracaso": "1887-1888",
        "candler": "1888-1891", "coca": "1903", "botella": "1915", "hoy": "HOY"}

ROJO_CC = (200, 30, 40)
CREMA_V = (238, 226, 200)
MADERA_O = (110, 70, 40)
TRAJE = ((56, 50, 48), (44, 40, 38), (50, 46, 44), (40, 36, 34))
TRAJE_C = ((70, 76, 96), (56, 60, 78), (60, 62, 74), (48, 50, 60))
ORO = (230, 186, 80)


def pemberton(L, x, y, pose="de_pie", esc=0.8, flip=False, a=1.0):
    return persona(L, x, y, pose, esc, flip=flip, ropa=TRAJE, barba=True, pelo=(150, 140, 130), a=a)


def candler(L, x, y, pose="de_pie", esc=0.8, flip=False):
    return persona(L, x, y, pose, esc, flip=flip, ropa=TRAJE_C, bigote=True, pelo=(70, 50, 40))


def frasco(L, x, y, s=1.0, col=(150, 90, 40), etiqueta="", a=1.0, lleno=0.8):
    rect(L, x - 22 * s, y - 50 * s, x + 22 * s, y + 40 * s, col, a=a * 0.9, r=8 * s)
    rect(L, x - 9 * s, y - 70 * s, x + 9 * s, y - 50 * s, col, a=a * 0.9)
    rect(L, x - 11 * s, y - 80 * s, x + 11 * s, y - 70 * s, (120, 90, 60), a=a, r=2 * s)
    rect(L, x - 16 * s, y - 40 * s, x - 10 * s, y + 30 * s, BLANCO, a=a * 0.25, r=3 * s)
    if etiqueta:
        rect(L, x - 20 * s, y - 14 * s, x + 20 * s, y + 18 * s, CREMA_V, a=a)
        size = 9 * s
        while ancho(etiqueta, size, "black") > 36 * s and size > 4:
            size -= 0.5
        texto(L, etiqueta, x, y + 2 * s, size, (60, 30, 20), a=a, fuente="black", sombra=False)


PERFIL = [(0.0, 0.16), (0.12, 0.16), (0.16, 0.19), (0.30, 0.24), (0.45, 0.38), (0.55, 0.40), (0.66, 0.33),
          (0.74, 0.32), (0.86, 0.40), (0.96, 0.38), (1.0, 0.34)]


def perfil_botella(u):
    for (u0, w0), (u1, w1) in zip(PERFIL, PERFIL[1:]):
        if u0 <= u <= u1:
            k = (u - u0) / (u1 - u0)
            k = 0.5 - 0.5 * math.cos(k * math.pi)
            return lerp(w0, w1, k)
    return PERFIL[-1][1]


def contorno_botella(cx, cy, h):
    izq, der = [], []
    for i in range(61):
        u = i / 60
        w = perfil_botella(u) * h * 0.5
        y = cy - h / 2 + u * h
        izq.append((cx - w, y))
        der.append((cx + w, y))
    return der + izq[::-1]


def botella_moderna(L, cx, cy, h, a=1.0, vidrio=(140, 190, 160), liquido=(70, 30, 20), nivel=0.86):
    pts = contorno_botella(cx, cy, h)
    poly(L, pts, vidrio, a=a * 0.55)
    liq = [(x, y) for x, y in pts if y > cy - h / 2 + (1 - nivel) * h]
    if len(liq) > 3:
        poly(L, liq, liquido, a=a * 0.9)
    linea(L, pts + [pts[0]], (210, 240, 220), w=2, a=a * 0.8)
    rect(L, cx - perfil_botella(0) * h * 0.5 - 2, cy - h / 2 - 8, cx + perfil_botella(0) * h * 0.5 + 2, cy - h / 2 + 4,
         (200, 40, 50), a=a, r=2)
    linea(L, [(cx - h * 0.1, cy - h * 0.2), (cx - h * 0.12, cy + h * 0.35)], BLANCO, w=3, a=a * 0.35)


def vaso(L, x, y, s=1.0, nivel=1.0, a=1.0, t=0.0):
    pts = [(x - 26 * s, y - 60 * s), (x + 26 * s, y - 60 * s), (x + 20 * s, y + 30 * s), (x - 20 * s, y + 30 * s)]
    poly(L, pts, (220, 235, 240), a=a * 0.35)
    if nivel > 0:
        top = y + 30 * s - 90 * s * nivel
        wt_ = lerp(20, 26, (y + 30 * s - top) / (90 * s)) * s
        poly(L, [(x - wt_, top), (x + wt_, top), (x + 20 * s, y + 30 * s), (x - 20 * s, y + 30 * s)], (70, 30, 20), a=a)
        rect(L, x - wt_, top - 6 * s, x + wt_, top + 2 * s, (200, 160, 120), a=a * 0.8, r=3 * s)
        rb = random.Random(3)
        for j in range(10):
            u = (t * 0.8 + j / 10) % 1
            bx = x + rb.uniform(-14, 14) * s
            by = y + 25 * s - u * (y + 25 * s - top)
            circ(L, bx, by, 1.6 * s, fill=(230, 210, 180), a=a * 0.7)
    linea(L, pts + [pts[0]], (240, 250, 255), w=1.5, a=a * 0.7)


def hoja(L, x, y, s=1.0, ang=0.0, a=1.0, col=(80, 150, 70)):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for i in range(21):
        u = i / 20
        w = math.sin(u * math.pi) * 16 * s
        pts.append((u * 60 * s - 30 * s, -w))
    for i in range(20, -1, -1):
        u = i / 20
        w = math.sin(u * math.pi) * 16 * s
        pts.append((u * 60 * s - 30 * s, w))
    poly(L, [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts], col, a=a)
    linea(L, [(x - 30 * s * ca, y - 30 * s * sa), (x + 30 * s * ca, y + 30 * s * sa)], (50, 110, 50), w=1.5, a=a)


def nuez(L, x, y, s=1.0, a=1.0):
    circ(L, x, y, 16 * s, fill=(140, 80, 50), a=a)
    circ(L, x + 14 * s, y + 4 * s, 13 * s, fill=(160, 96, 60), a=a)
    linea(L, [(x + 4 * s, y - 12 * s), (x + 6 * s, y + 12 * s)], (100, 56, 34), w=1.5, a=a)


def moneda(L, x, y, s=1.0, a=1.0, txt="5¢"):
    circ(L, x, y, 26 * s, fill=ORO, a=a)
    circ(L, x, y, 20 * s, outline=(190, 140, 50), w=2, a=a)
    texto(L, txt, x, y, 18 * s, (110, 70, 20), a=a, fuente="sym", sombra=False)


def sello(L, txt, x, y, q, col=ROJO, ang_txt=None, size=40):
    if q <= 0:
        return
    s = 1 + 1.4 * (1 - eo3(q))
    w = ancho(txt, size * s) + 34 * s
    rect(L, x - w / 2, y - size * 0.75 * s, x + w / 2, y + size * 0.75 * s, None, a=q, r=10 * s, outline=col, w=5 * s)
    texto(L, txt, x, y, size * s, col, a=q, fuente="black", sombra=False)


def farmacia(L, T):
    """Interior de farmacia de 1886: estanterías de frascos y mostrador."""
    rect(L, 0, 0, W, H, (60, 40, 30))
    rect(L, 0, 330, W, 760, (120, 84, 56))
    for y in (400, 480, 560):
        rect(L, 20, y, 520, y + 8, MADERA_O)
        for j in range(9):
            x = 44 + j * 54
            col = [(150, 90, 40), (60, 110, 90), (90, 60, 110), (170, 60, 50), (60, 90, 140)][(j + y // 80) % 5]
            frasco(L, x, y - 6, 0.42, col)
    texto(L, "FARMACIA", 270, 346, 22, (230, 200, 140), fuente="black", sombra=False)
    rect(L, 0, 760, W, H, (70, 50, 36))


def mostrador(L, y=650):
    rect(L, 0, y, W, y + 18, (90, 56, 32))
    rect(L, 10, y + 18, W - 10, 780, (130, 86, 50))
    for x in range(30, W - 30, 120):
        rect(L, x, y + 34, x + 100, 760, (110, 70, 40), r=4)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (16, 12, 12))
    # cañón de luz
    poly(L, [(250, 0), (290, 0), (420, 760), (120, 760)], (255, 230, 190), a=0.08)
    L.d.ellipse(P(130, 740, 410, 790), fill=L.c((255, 230, 190), 0.12))
    q = eob(prog(t, 0.1, 0.7))
    frasco(L, 270, 640 - 30 * q, 2.4 * q + 0.01, (120, 60, 30), etiqueta="JARABE" if q > 0.5 else "")
    # burbujas que suben
    for j in range(14):
        u = (t * 0.5 + j / 14) % 1
        circ(L, 250 + (j * 37 % 40), 640 - u * 160, 2.5, fill=(240, 220, 180), a=0.6 * (1 - u))
    tp = wt(e, "prohibida") - 0.2
    sello(L, "PROHIBIDA", 270, 470, prog(t, tp, 0.3))
    q2 = prog(t, wt(e, "medicinal") - 0.2, 0.5)
    texto(L, "℞", 120, 470, 60 * eob(q2) + 1, (230, 200, 140), a=q2, fuente="sym")


def esc_pemberton(L, e, t, D, T, st):
    farmacia(L, T)
    k = eio(prog(t, 0.0, 1.2))
    pemberton(L, lerp(80, 220, k), 572, "mezcla" if t > 1.2 else "de_pie")
    mostrador(L)
    frasco(L, 330, 620, 0.6, (120, 60, 30), etiqueta="")
    # mortero
    rect(L, 290, 626, 330, 650, (200, 200, 200), r=10)
    # recuadros: guerra y morfina
    qg = prog(t, wt(e, "herido") - 0.2, 0.4)
    if qg > 0:
        st["overlay"].append(("ficha", 400, 430, "1865", "Herido en la guerra", qg))
    qm = prog(t, wt(e, "morfina") - 0.2, 0.4)
    if qm > 0:
        st["overlay"].append(("frasco_morfina", 110, 640, qm))
    if t > wt(e, "dolor") - 0.3:
        st["overlay"].append(("dolor", prog(t, wt(e, "dolor") - 0.3, 0.4), t))


def esc_vino(L, e, t, D, T, st):
    farmacia(L, T)
    pemberton(L, 140, 572, "senala")
    mostrador(L)
    q = eob(prog(t, 0.2, 0.6))
    # botella de vino
    x, y = 330, 560
    rect(L, x - 26 * q, y - 70 * q, x + 26 * q, y + 80 * q, (80, 20, 40), r=10 * q)
    rect(L, x - 10 * q, y - 120 * q, x + 10 * q, y - 70 * q, (80, 20, 40))
    rect(L, x - 24 * q, y - 10 * q, x + 24 * q, y + 40 * q, CREMA_V)
    texto(L, "VINO", x, y + 6 * q, 13 * q + 1, (80, 20, 40), fuente="black", sombra=False)
    texto(L, "de coca", x, y + 24 * q, 9 * q + 1, (80, 20, 40), fuente="bold", sombra=False)
    if q > 0.3:
        hoja(L, x + 44, y - 40, 0.8, -0.5, a=prog(t, wt(e, "hoja") - 0.2, 0.4))
    tp = wt(e, "prohibió") - 0.4
    qn = prog(t, tp, 0.35)
    if qn > 0:
        st["overlay"].append(("periodico", qn, t))


def esc_receta(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (70, 48, 34))
    rect(L, 0, 330, W, 760, (120, 84, 56))
    # caldero
    cx, cy = 270, 620
    for j in range(6):
        fx = cx - 60 + j * 24
        poly(L, [(fx, 760), (fx + 10, 700 - 20 * abs(math.sin(t * 8 + j))), (fx + 20, 760)], (250, 160, 60), a=0.9)
    L.d.chord(P(cx - 120, cy - 60, cx + 120, cy + 120), 0, 180, fill=L.c((50, 50, 54)))
    rect(L, cx - 130, cy - 10, cx + 130, cy + 30, (60, 60, 66), r=10)
    L.d.ellipse(P(cx - 116, cy - 22, cx + 116, cy + 6), fill=L.c((90, 40, 26)))
    for j in range(5):
        u = (t * 0.7 + j / 5) % 1
        circ(L, cx - 80 + j * 40, cy - 14 - u * 80, 6 + 6 * u, fill=(220, 210, 200), a=0.3 * (1 - u))
    # ingredientes que caen
    ings = [("vino", None), ("azúcar", "azucar"), ("nuez", "nuez")]
    tv = 0.2
    if t < tv + 1.0:
        u = prog(t, tv, 0.9)
        x, y = lerp(430, cx + 30, u), lerp(420, cy - 10, u)
        rect(L, x - 12, y - 30, x + 12, y + 30, (80, 20, 40), a=1 - u, r=6)
        st["overlay"].append(("cruz", 430, 420, prog(t, tv, 0.3)))
    ta = wt(e, "azúcar") - 0.2
    for j in range(6):
        u = prog(t, ta + j * 0.08, 0.7)
        if 0 < u < 1:
            x, y = lerp(130 + j * 12, cx - 20, u), lerp(400, cy - 10, u * u)
            rect(L, x - 8, y - 8, x + 8, y + 8, BLANCO)
    tn = wt(e, "nuez") - 0.2
    u = prog(t, tn, 0.8)
    if 0 < u < 1:
        nuez(L, lerp(410, cx + 20, u), lerp(390, cy - 10, u * u), 1.2)
    tc = wt(e, "Coca", 0) - 0.15
    qc = prog(t, tc, 0.4)
    if qc > 0:
        st["overlay"].append(("ecuacion", qc, prog(t, wt(e, "cola", 1) - 0.15, 0.4), t))


def esc_soda(L, e, t, D, T, st):
    farmacia(L, T)
    pemberton(L, 380, 572, "de_pie", flip=True)
    mostrador(L)
    # grifo de soda
    rect(L, 160, 520, 200, 650, (190, 190, 200), r=6)
    rect(L, 200, 540, 250, 556, (190, 190, 200), r=4)
    tg = wt(e, "gas") - 0.6
    nivel = prog(t, tg, 1.4)
    if 0 < nivel < 1:
        linea(L, [(244, 558), (244, 640)], (90, 40, 26), w=4)
    vaso(L, 244, 630, 0.8, nivel=nivel, t=t)
    tc = wt(e, "Cinco") - 0.2
    if t > tc:
        st["overlay"].append(("moneda", prog(t, tc, 0.4), t))
    tn = wt(e, "nació") - 0.1
    qn = prog(t, tn, 0.4)
    if qn > 0:
        st["overlay"].append(("nace", qn))


def esc_fracaso(L, e, t, D, T, st):
    tm = wt(e, "Pemberton") - 0.3
    if t < tm:
        rect(L, 0, 0, W, H, (60, 44, 34))
        # gráfico de ventas plano
        x0, y0, x1, y1 = 70, 370, 470, 640
        linea(L, [(x0, y0), (x0, y1), (x1, y1)], CREMA_V, w=3)
        u = prog(t, 0.3, 1.5)
        pts = [(x0 + (x1 - x0) * k / 40, y1 - 30 - 6 * math.sin(k * 0.9)) for k in range(int(40 * u) + 1)]
        if len(pts) > 1:
            linea(L, pts, ROJO, w=4)
        texto(L, "ventas", x0 + 10, y0 + 10, 16, CREMA_V, fuente="bold", anchor="lm", sombra=False)
        tv = wt(e, "nueve") - 0.2
        for j in range(9):
            q = prog(t, tv + j * 0.06, 0.25)
            if q > 0:
                vaso(L, 90 + j * 44, 720, 0.45 * eob(q), nivel=1.0, t=t)
        st["overlay"].append(("contador9", prog(t, tv, 0.4)))
    else:
        rect(L, 0, 0, W, H, (40, 40, 46))
        rect(L, 0, 700, W, H, (60, 70, 50))
        q = prog(t, tm, 0.6)
        # lápida
        x, y = 270, 560
        rect(L, x - 90, y - 120, x + 90, y + 150, (130, 130, 136), a=q, r=80)
        rect(L, x - 90, y - 40, x + 90, y + 150, (130, 130, 136), a=q)
        texto(L, "J. S. PEMBERTON", x, y - 40, 18, (60, 60, 66), a=q, fuente="black", sombra=False)
        texto(L, "1831 – 1888", x, y, 20, (60, 60, 66), a=q, fuente="black", sombra=False)
        linea(L, [(x - 50, y + 30), (x + 50, y + 30)], (90, 90, 96), w=2, a=q)
        for j in range(3):
            circ(L, 170 + j * 100, 712, 12, fill=(200, 60, 60), a=q)
        qa = prog(t, wt(e, "arruinado") - 0.2, 0.4)
        if qa > 0:
            st["overlay"].append(("bolsillo", qa))


def esc_candler(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (40, 36, 52))
    rect(L, 0, 330, W, 760, (70, 64, 86))
    candler(L, 120, 540, "senala" if t > 1.0 else "de_pie")
    # el fajo de dinero por la fórmula
    q = prog(t, wt(e, "compró") - 0.2, 0.4)
    if q > 0 and t < wt(e, "cupones") - 0.3:
        st["overlay"].append(("papel", 330, 480, "FÓRMULA", q))
    cosas = [("cupones", "cupon", 320, 440), ("carteles", "cartel", 430, 560), ("relojes", "reloj", 320, 640),
             ("calendarios", "calendario", 440, 700)]
    for pal, tipo, x, y in cosas:
        qq = prog(t, wt(e, pal) - 0.2, 0.4)
        if qq > 0:
            st["overlay"].append((tipo, x, y, qq, t))
    tm = wt(e, "Marketing") - 0.2
    if t > tm:
        st["overlay"].append(("grafico_sube", prog(t, tm, 1.4)))


def esc_coca(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (30, 40, 34))
    rect(L, 0, 330, W, 780, (40, 56, 46))
    hoja(L, 270, 520, 3.0, -0.4)
    tc = wt(e, "cocaína") - 0.2
    # partículas blancas que salen de la hoja
    for j in range(24):
        u = ((t - 0.5) * 0.4 + j / 24) % 1
        if t < 0.5:
            continue
        ang = j * 2.4
        x = 270 + math.cos(ang) * 60 * u
        y = 520 - 120 * u + math.sin(ang) * 20
        desaparece = 1 - prog(t, wt(e, "eliminaron") - 0.2, 0.6)
        circ(L, x, y, 3, fill=BLANCO, a=(1 - u) * desaparece)
    qc = prog(t, tc, 0.4)
    if qc > 0:
        st["overlay"].append(("etiqueta_c", qc))
    te = wt(e, "eliminaron") - 0.3
    st["overlay"].append(("sello", "ELIMINADA · 1903", 270, 690, prog(t, te, 0.3), VERDE))


def esc_botella(L, e, t, D, T, st):
    ta = wt(e, "oscuras") - 0.25
    tr = wt(e, "rota") - 0.25
    if t < ta:
        # plano azul
        rect(L, 0, 0, W, H, (20, 60, 120))
        for x in range(0, W, 30):
            linea(L, [(x, 0), (x, H)], (40, 90, 150), w=1)
        for y in range(0, H, 30):
            linea(L, [(0, y), (W, y)], (40, 90, 150), w=1)
        pts = contorno_botella(270, 560, 380)
        u = eio(prog(t, 0.2, 2.2))
        n = max(2, int(len(pts) * u))
        linea(L, pts[:n], BLANCO, w=3)
        if u >= 1:
            linea(L, pts + [pts[0]], BLANCO, w=3)
            for yy, lab in ((560 - 190, "cuello"), (560 + 10, "curvas"), (560 + 190, "base")):
                linea(L, [(360, yy), (440, yy)], (180, 210, 240), w=1.5)
                texto(L, lab, 446, yy, 14, (200, 225, 250), fuente="semi", anchor="lm", sombra=False)
        texto(L, "1915", 90, 380, 28, (200, 225, 250), fuente="mono", sombra=False)
    elif t < tr:
        rect(L, 0, 0, W, H, (6, 6, 10))
        q = prog(t, ta, 0.5)
        pts = contorno_botella(270, 560, 380)
        poly(L, pts, (30, 30, 36))
        linea(L, pts + [pts[0]], (120, 140, 160), w=2, a=q)
        st["overlay"].append(("mano_toca", q, t - ta))
    else:
        rect(L, 0, 0, W, H, (180, 160, 140))
        rect(L, 0, 700, W, H, (150, 120, 100))
        q = prog(t, tr, 0.4)
        # trozos que aún dibujan la silueta
        pts = contorno_botella(270, 560, 380)
        rs = random.Random(2)
        for j in range(0, len(pts) - 6, 6):
            trozo = pts[j:j + 7]
            cx = sum(p[0] for p in trozo) / len(trozo)
            cy = sum(p[1] for p in trozo) / len(trozo)
            dx, dy = (cx - 270) * 0.12 * q + rs.uniform(-6, 6) * q, rs.uniform(-6, 6) * q
            poly(L, [(px + dx, py + dy) for px, py in trozo] + [(270 + dx * 0.5, cy + dy)], (120, 170, 140), a=0.9)
        st["overlay"].append(("check_forma", prog(t, tr + 0.5, 0.4)))


def esc_hoy(L, e, t, D, T, st):
    tm = wt(e, "marcas") - 0.4
    if t < tm:
        rect(L, 0, 0, W, H, (40, 42, 48))
        cx, cy = 270, 560
        abre = eio(prog(t, wt(e, "acorazada") - 0.2, 1.0))
        circ(L, cx, cy, 170, fill=(90, 94, 104))
        circ(L, cx, cy, 150, fill=(130, 134, 144))
        if abre > 0:
            circ(L, cx, cy, 140 * abre, fill=(255, 220, 140))
            rect(L, cx - 40 * abre, cy - 50 * abre, cx + 40 * abre, cy + 50 * abre, CREMA_V, r=4)
            texto(L, "FÓRMULA", cx, cy - 30 * abre, 12 * abre + 1, (90, 40, 30), fuente="black", sombra=False)
            for j in range(4):
                linea(L, [(cx - 28 * abre, cy - 10 * abre + j * 12 * abre), (cx + 28 * abre, cy - 10 * abre + j * 12 * abre)],
                      (150, 120, 100), w=1.5)
        else:
            ang = t * 3
            for j in range(12):
                a2 = ang + j * math.pi / 6
                linea(L, [(cx + 50 * math.cos(a2), cy + 50 * math.sin(a2)), (cx + 64 * math.cos(a2), cy + 64 * math.sin(a2))],
                      (60, 62, 70), w=4)
            circ(L, cx, cy, 44, fill=(70, 72, 80))
            for j in range(8):
                a2 = j * math.pi / 4
                circ(L, cx + 128 * math.cos(a2), cy + 128 * math.sin(a2), 9, fill=(90, 94, 104))
        texto(L, "ATLANTA", 270, 790, 22, (180, 180, 190), fuente="black", sombra=False)
    else:
        rect(L, 0, 0, W, H, (150, 20, 30))
        tc = t - tm
        for j in range(30):
            u = (tc * 0.6 + j / 30) % 1
            x = 30 + (j * 83) % 480
            botella_moderna(L, x, 330 + u * 520, 90, a=0.5)
        st["overlay"].append(("contador_hoy", prog(t, tm, 1.8)))


def esc_final(L, e, t, D, T, st):
    farmacia(L, T)
    pemberton(L, 220, 572, "pensando")
    mostrador(L)
    vaso(L, 360, 630, 0.8, nivel=1.0, t=t)
    qs = prog(t, wt(e, "Síguenos") - 0.2, 0.4)
    if qs > 0:
        st["overlay"].append(("seguir", qs, t))
    st["sin_paso"] = True


FUNCS = {"gancho": esc_gancho, "pemberton": esc_pemberton, "vino": esc_vino, "receta": esc_receta, "soda": esc_soda,
         "fracaso": esc_fracaso, "candler": esc_candler, "coca": esc_coca, "botella": esc_botella, "hoy": esc_hoy,
         "final": esc_final}


# ------------------------------------------------------------------ overlays (después del filtro sepia)
def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "ficha":
            _, x, y, anio, txt, q = it
            s = eob(q)
            rect(O, x - 90 * s, y - 40 * s, x + 90 * s, y + 40 * s, CREMA_V, a=q, r=8)
            texto(O, anio, x, y - 14 * s, 20 * s, ROJO_CC, a=q, fuente="black", sombra=False)
            texto(O, txt, x, y + 14 * s, 13 * s, (60, 40, 30), a=q, fuente="bold", sombra=False)
        elif tipo == "frasco_morfina":
            _, x, y, q = it
            frasco(O, x, y, 1.0 * eob(q), (70, 100, 130), etiqueta="MORFINA", a=q)
        elif tipo == "dolor":
            _, q, t = it
            for j in range(3):
                u = (t * 1.5 + j / 3) % 1
                texto(O, "~", 290 + j * 12, 300 + 40 - u * 30, 22, ROJO, a=q * (1 - u), fuente="black")
        elif tipo == "periodico":
            _, q, t = it
            s = eob(q)
            ang = (1 - q) * 6
            x, y = 270, 470
            rect(O, x - 200 * s, y - 110 * s, x + 200 * s, y + 110 * s, (236, 230, 214), a=q, r=4)
            texto(O, "DIARIO DE ATLANTA · 1886", x, y - 80 * s, 14 * s, (60, 60, 60), a=q, fuente="black", sombra=False)
            linea(O, [(x - 180 * s, y - 62 * s), (x + 180 * s, y - 62 * s)], (60, 60, 60), w=2, a=q)
            texto(O, "ATLANTA PROHÍBE", x, y - 22 * s, 30 * s, (20, 20, 20), a=q, fuente="black", sombra=False)
            texto(O, "EL ALCOHOL", x, y + 16 * s, 30 * s, (20, 20, 20), a=q, fuente="black", sombra=False)
            for j in range(3):
                linea(O, [(x - 170 * s, y + 50 * s + j * 14 * s), (x + 170 * s, y + 50 * s + j * 14 * s)], (150, 150, 150),
                      w=2, a=q)
            _ = ang
        elif tipo == "cruz":
            _, x, y, q = it
            k = eo3(q)
            linea(O, [(x - 30, y - 30), (x - 30 + 60 * k, y - 30 + 60 * k)], ROJO, w=8)
            linea(O, [(x + 30, y - 30), (x + 30 - 60 * k, y - 30 + 60 * k)], ROJO, w=8)
        elif tipo == "ecuacion":
            _, q, q2, t = it
            hoja(O, 130, 360, 1.3 * eob(q), -0.3, a=q)
            texto(O, "COCA", 130, 410, 26, BLANCO, a=q, fuente="black")
            texto(O, "+", 270, 380, 40, BLANCO, a=q2, fuente="black")
            if q2 > 0:
                nuez(O, 400, 360, 1.4 * eob(q2), a=q2)
                texto(O, "COLA", 410, 410, 26, BLANCO, a=q2, fuente="black")
        elif tipo == "moneda":
            _, q, t = it
            moneda(O, 420, 420 + 10 * math.sin(t * 4), 1.6 * eob(q), a=q)
        elif tipo == "nace":
            _, q = it
            s = eob(q)
            rect(O, 70, 440 - 34 * s, 470, 440 + 34 * s, ROJO_CC, a=q, r=34 * s)
            texto(O, "COCA-COLA", 270, 440, 36 * s, BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "contador9":
            q = it[1]
            texto(O, "≈ 9 vasos al día", 270, 470, 30, BLANCO, a=q, fuente="sym")
        elif tipo == "bolsillo":
            q = it[1]
            texto(O, "casi arruinado", 270, 820, 24, (230, 200, 160), a=q, fuente="black")
        elif tipo == "papel":
            _, x, y, txt, q = it
            s = eob(q)
            rect(O, x - 70 * s, y - 50 * s, x + 70 * s, y + 50 * s, CREMA_V, a=q, r=4)
            texto(O, txt, x, y - 26 * s, 15 * s, (90, 40, 30), a=q, fuente="black", sombra=False)
            for j in range(3):
                linea(O, [(x - 50 * s, y + j * 14 * s), (x + 50 * s, y + j * 14 * s)], (150, 120, 100), w=1.5, a=q)
        elif tipo == "cupon":
            _, x, y, q, t = it
            for j in range(3):
                u = (t * 0.6 + j / 3) % 1
                xx, yy = x + 30 * math.sin(t * 2 + j), y - 60 * u + j * 10
                rect(O, xx - 60, yy - 24, xx + 60, yy + 24, CREMA_V, a=q, r=4, outline=ROJO_CC, w=2)
                texto(O, "VALE: 1 VASO", xx, yy - 6, 11, ROJO_CC, a=q, fuente="black", sombra=False)
                texto(O, "GRATIS", xx, yy + 10, 12, ROJO_CC, a=q, fuente="black", sombra=False)
        elif tipo == "cartel":
            _, x, y, q, t = it
            s = eob(q)
            rect(O, x - 56 * s, y - 70 * s, x + 56 * s, y + 70 * s, ROJO_CC, a=q, r=6)
            rect(O, x - 48 * s, y - 62 * s, x + 48 * s, y + 62 * s, None, a=q, r=4, outline=CREMA_V, w=2)
            texto(O, "¡BEBA!", x, y - 26 * s, 20 * s, CREMA_V, a=q, fuente="black", sombra=False)
            vaso(O, x, y + 30 * s, 0.5 * s, nivel=1.0, a=q, t=t)
        elif tipo == "reloj":
            _, x, y, q, t = it
            s = eob(q)
            circ(O, x, y, 40 * s, fill=CREMA_V, a=q)
            circ(O, x, y, 40 * s, outline=ROJO_CC, w=4, a=q)
            linea(O, [(x, y), (x + 26 * s * math.cos(t * 2), y + 26 * s * math.sin(t * 2))], (40, 40, 40), w=3, a=q)
            linea(O, [(x, y), (x, y - 18 * s)], (40, 40, 40), w=3, a=q)
        elif tipo == "calendario":
            _, x, y, q, t = it
            s = eob(q)
            rect(O, x - 46 * s, y - 50 * s, x + 46 * s, y + 50 * s, CREMA_V, a=q, r=4)
            rect(O, x - 46 * s, y - 50 * s, x + 46 * s, y - 26 * s, ROJO_CC, a=q, r=4)
            for j in range(12):
                rect(O, x - 36 * s + (j % 4) * 19 * s, y - 16 * s + (j // 4) * 20 * s, x - 24 * s + (j % 4) * 19 * s,
                     y - 6 * s + (j // 4) * 20 * s, (150, 140, 130), a=q)
        elif tipo == "grafico_sube":
            q = it[1]
            pts = [(60 + k * 10, 820 - 140 * (k / 42) ** 2.2) for k in range(int(42 * q) + 1)]
            if len(pts) > 1:
                linea(O, pts, VERDE, w=5)
                texto(O, "↗", pts[-1][0] + 10, pts[-1][1] - 10, 28, VERDE, fuente="sym")
        elif tipo == "etiqueta_c":
            q = it[1]
            rect(O, 120, 380, 420, 430, (0, 0, 0), a=0.6 * q, r=25)
            texto(O, "trazas de cocaína", 270, 405, 22, BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "sello":
            _, txt, x, y, q, col = it
            sello(O, txt, x, y, q, col=col, size=28)
        elif tipo == "mano_toca":
            _, q, dt = it
            texto(O, "reconocible a oscuras", 270, 820, 22, (200, 210, 230), a=q, fuente="black")
        elif tipo == "check_forma":
            q = it[1]
            texto(O, "...y aún rota, se reconoce", 270, 820, 22, (40, 30, 20), a=q, fuente="black", sombra=False)
        elif tipo == "contador_hoy":
            q = it[1]
            v = int(2_000_000_000 * eo3(q))
            txt = f"{v:,}".replace(",", ".")
            rect(O, 40, 470, 500, 570, (0, 0, 0), a=0.55, r=20)
            texto(O, txt, 270, 510, 40, BLANCO, fuente="mono", sombra=False)
            texto(O, "bebidas al día", 270, 550, 18, (240, 220, 220), fuente="bold", sombra=False)
        elif tipo == "seguir":
            _, q, t = it
            s = eob(q) * (1 + 0.04 * math.sin(t * 6))
            rect(O, 150 * 1, 820 - 32 * s, 390, 820 + 32 * s, (254, 44, 85), a=q, r=32 * s)
            texto(O, "+ SEGUIR", 270, 820, 26 * s, BLANCO, a=q, fuente="black", sombra=False)
            texto(O, "para más historias", 270, 870, 16, (230, 220, 200), a=q, fuente="semi")


def sepia(img, k):
    if k <= 0:
        return img
    a = np.asarray(img).astype(np.float32)
    g = a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11
    sp = np.stack([g * 1.08 + 18, g * 0.9 + 8, g * 0.68], -1)
    out = a * (1 - k) + sp * k
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def pelicula(O, T, k):
    """Grano, rayas y parpadeo de película antigua."""
    if k <= 0:
        return
    rs = random.Random(int(T * 24))
    for _ in range(3):
        if rs.random() < 0.5:
            x = rs.uniform(0, W)
            linea(O, [(x, 0), (x + rs.uniform(-4, 4), H)], (250, 240, 220), w=0.8, a=0.25 * k)
    for _ in range(int(60 * k)):
        circ(O, rs.uniform(0, W), rs.uniform(0, H), rs.uniform(0.4, 1.2), fill=(30, 20, 10), a=0.35 * k)
    rect(O, 0, 0, W, H, (0, 0, 0), a=0.05 * k * (rs.random()))


def anio(O, e, t):
    txt = ANIO.get(e["nombre"])
    if not txt:
        return
    q = prog(t, 0.1, 0.4)
    rect(O, 20, 300, 20 + ancho(txt, 18, "mono") + 24, 334, (0, 0, 0), a=0.55 * q, r=8)
    texto(O, txt, 32, 317, 18, (240, 220, 180), a=q, fuente="mono", anchor="lm", sombra=False)


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


_VIN = None


def VINETA():
    global _VIN
    if _VIN is None:
        sw, sh = IW // 8, IH // 8
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        r = np.sqrt(((xx - sw / 2) / sw) ** 2 + ((yy - sh / 2) / sh) ** 2 * 0.8)
        v = np.clip(1.25 - r * 1.05, 0.4, 1)
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
    # cámara: zoom lento (efecto Ken Burns)
    z = 1.04 + 0.06 * eio(t / D)
    cw, ch = IW / z, IH / z
    x0, y0 = (IW - cw) / 2, (IH - ch) / 2 + 20 * K
    img = L.img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    k = SEPIA_ESCENAS.get(e["nombre"], 0)
    img = sepia(img, k)
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    pelicula(O, T, k)
    overlays(O, st, T)
    anio(O, e, t)
    paso(O, st, t)
    subtitulos(O, T)
    out = O.img
    if T < 0.2:
        out = Image.blend(Image.new("RGB", (IW, IH), (0, 0, 0)), out, T / 0.2)
    if T > TOTAL - 0.6:
        out = Image.blend(out, Image.new("RGB", (IW, IH), (0, 0, 0)), cl((T - (TOTAL - 0.6)) / 0.6))
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


def musica(n):
    """Piano de época (ragtime suave) hasta Candler; después, ritmo moderno."""
    out = np.zeros(n, np.float32)
    t_mod = next(e for e in ESC if e["nombre"] == "candler")["t0"]
    beat = 60 / 112
    acordes = [[48, 52, 55], [53, 57, 60], [55, 59, 62], [48, 52, 55]]
    melodia = [76, 74, 72, 74, 76, 76, 76, 0, 74, 74, 74, 0, 76, 79, 79, 0]
    k = 0
    while k * beat / 2 < TOTAL:
        t0 = k * beat / 2
        ac = acordes[(k // 8) % 4]
        moderno = t0 >= t_mod
        if k % 2 == 0:
            colocar(out, piano(nota(ac[0] - 12), 0.5, 0.05), t0)
        else:
            for m in ac:
                colocar(out, piano(nota(m), 0.35, 0.025), t0)
        mm = melodia[k % 16]
        if mm and k % 1 == 0:
            colocar(out, piano(nota(mm), 0.4, 0.028 if not moderno else 0.02), t0 + (0.04 if k % 2 else 0))
        if moderno and k % 2 == 0:
            m2 = int(0.4 * SR)
            u = np.arange(m2) / SR
            colocar(out, (0.15 * np.sin(2 * np.pi * (45 + 80 * np.exp(-u * 30)) * u) * np.exp(-u * 8)).astype(np.float32), t0)
            if (k // 2) % 2 == 1:
                rng = np.random.default_rng(k)
                colocar(out, (0.05 * np.diff(rng.standard_normal(m2 + 1)) * np.exp(-u * 30)).astype(np.float32), t0)
        k += 1
    return out


def fizz(dur=1.5, seed=0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    s = np.diff(rng.standard_normal(n + 1)).astype(np.float32) * 0.15
    pops = np.zeros(n, np.float32)
    for _ in range(int(dur * 60)):
        i = rng.integers(0, n - 200)
        pops[i:i + 200] += np.sin(np.arange(200) * rng.uniform(0.6, 1.4)) * np.exp(-np.arange(200) / 40) * 0.3
    env = np.clip(np.arange(n) / (0.1 * SR), 0, 1) * np.clip((n - np.arange(n)) / (0.4 * SR), 0, 1)
    return (s + pops) * env


def caja():
    n = int(0.9 * SR)
    u = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 2100 * u) + np.sin(2 * np.pi * 2650 * u)) * np.exp(-u * 6) * 0.3
    s[:int(0.05 * SR)] += np.random.default_rng(1).standard_normal(int(0.05 * SR)) * 0.2
    return s.astype(np.float32)


def mezclar():
    n = int((TOTAL + 0.3) * SR)
    voz = np.zeros(n, np.float32)
    for e in ESC:
        colocar(voz, leer(os.path.join(BUILD, f"voz_{e['i']}.mp3")), e["voz_t0"])
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    mus = musica(n) * 0.9
    fx = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    for j, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(j, 0.45), e["t0"] - 0.22, 0.3)
    g = E["gancho"]
    colocar(fx, fizz(2.0, 1), g["t0"] + 0.3, 0.25)
    colocar(fx, golpe(), g["t0"] + wt(g, "prohibida") - 0.2, 0.6)
    v = E["vino"]
    colocar(fx, whoosh(9, 0.5), v["t0"] + wt(v, "prohibió") - 0.5, 0.5)
    colocar(fx, golpe() * 0.6, v["t0"] + wt(v, "prohibió") - 0.05, 0.4)
    s = E["soda"]
    colocar(fx, fizz(1.8, 2), s["t0"] + wt(s, "gas") - 0.5, 0.35)
    colocar(fx, caja(), s["t0"] + wt(s, "Cinco") - 0.2, 0.5)
    c = E["coca"]
    colocar(fx, golpe(), c["t0"] + wt(c, "eliminaron") - 0.3, 0.5)
    b = E["botella"]
    colocar(fx, cristal(), b["t0"] + wt(b, "rota") - 0.25, 0.6)
    h = E["hoy"]
    colocar(fx, golpe() * 0.8, h["t0"] + wt(h, "acorazada") - 0.2, 0.6)
    colocar(fx, fizz(2.5, 3), h["t0"] + wt(h, "marcas") - 0.4, 0.25)
    env = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.5 * np.clip(env * 12, 0, 1)
    total = voz + (mus + fx) * duck
    total *= np.clip((TOTAL - np.arange(n) / SR) / 0.6, 0, 1)
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
