"""Valdemora · Ep. 01 «Las 3:17» (ficción original). Vídeo vertical de ~90 s con personajes de bloques 3D,
cámara cinematográfica, niebla, ojo de pez, foto sepia, voces por personaje y diseño sonoro completo.
Biblia del episodio: ../ep01_las_317.md

    python3 voz.py && python3 video.py        -> valdemora_ep01_317.mp4"""
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
SALIDA = os.path.join(AQUI, "valdemora_ep01_317.mp4")

W, H = 540, 960            # unidades de diseño (9:16)
K = 3                      # resolución interna = 1620x2880
IW, IH = W * K, H * K
OW, OH = 1080, 1920
FPS = 30
SR = 44100
VOZ_OFF = 0.08
COLA = 0.18

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


EXTRA = {"regla": 0.2, "golpes": 0.4, "doble2": 1.4}
PRE = {"silencio": 1.2}
ESC = []
_t = 0.0
for i, seg in enumerate(DATOS):
    dv = dur_mp3(os.path.join(BUILD, f"voz_{i}.mp3"))
    d = VOZ_OFF + dv + COLA + EXTRA.get(seg["escena"], 0) + PRE.get(seg["escena"], 0)
    ESC.append({"i": i, "nombre": seg["escena"], "t0": _t, "dur": d, "voz_t0": _t + (0.05 if i == 0 else VOZ_OFF) + PRE.get(seg["escena"], 0),
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
CLAVE = {"3:17…", "abras.", "regla.", "advierte:", "3:17", "puerta.", "superstición.", "vacío", "nadie", "allí.",
         "llamó.", "golpes.", "lentos.", "mirilla.", "cara.", "sonreía.", "ábreme,", "ti.", "1979.", "julián…", "idéntico",
         "abrió.", "nombre.", "silencio.", "más.", "armario.", "dentro."}


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
            for seq, num in ((["mente", "cuatro", "cero", "cuatro"], "MENTE404"), (["uno", "uno", "dos"], "112")):
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


# --- Escenas del TikTok «MENTE404» (se insertan en video.py al montarlo) ---

CIUDAD = "MENTE404"
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




# --- Escenas «MENTE404 · El caso del cartel robado» (se añaden tras las funciones de MENTE404) ---

CABECERA = "MENTE404 · CASO Nº 1: EL CARTEL ROBADO"
DETECTIVE = dict(camisa=(150, 112, 70), pantalon=(70, 56, 44), pelo=(40, 30, 24), sombrero=(60, 48, 40))
TITO = dict(camisa=(60, 100, 200), pantalon=(50, 80, 170), pelo=(30, 30, 30), casco=(250, 200, 40))
PACO = dict(camisa=(250, 250, 250), pantalon=(120, 110, 100), pelo=(120, 80, 50), chef=True)
LOLA = dict(camisa=(110, 180, 90), pantalon=(90, 70, 50), pelo=(200, 90, 40), rizos=True, paja=(230, 200, 120))
SOSPECHOSOS = [("TITO", "EL ELECTRICISTA", TITO), ("PACO", "EL PANADERO", PACO), ("LOLA", "LA JARDINERA", LOLA)]
VIOLETA = (160, 90, 220)


def accesorios(L, x, y, s, look, cara_abierta=0.0):
    """Sombreros y detalles que la figura base no dibuja. (x, y) = pies del personaje."""
    lh, th, hs = 64 * s, 62 * s, 46 * s
    hy0 = y - lh - th - hs - 4 * s
    hx0 = x - hs / 2
    if look.get("sombrero"):
        c = look["sombrero"]
        rect(L, hx0 - 12 * s, hy0 - 4 * s, hx0 + hs + 18 * s, hy0 + 4 * s, c, r=3 * s)
        cubo(L, hx0 + 4 * s, hy0 - 26 * s, hs - 8 * s, 24 * s, c, 6 * s)
        rect(L, hx0 + 4 * s, hy0 - 8 * s, hx0 + hs - 4 * s, hy0 - 3 * s, (30, 24, 20))
    if look.get("chef"):
        cubo(L, hx0 + 2 * s, hy0 - 40 * s, hs - 4 * s, 34 * s, (250, 250, 250), 6 * s)
        for k in range(3):
            circ(L, hx0 + 10 * s + k * 13 * s, hy0 - 42 * s, 10 * s, fill=(250, 250, 250))
    if look.get("paja"):
        c = look["paja"]
        rect(L, hx0 - 16 * s, hy0 - 2 * s, hx0 + hs + 22 * s, hy0 + 6 * s, c, r=4 * s)
        cubo(L, hx0 + 6 * s, hy0 - 18 * s, hs - 12 * s, 18 * s, c, 5 * s)
        rect(L, hx0 + 6 * s, hy0 - 6 * s, hx0 + hs - 6 * s, hy0 - 1 * s, VIOLETA)
    if cara_abierta > 0:
        mx, my = hx0 + 23 * s, hy0 + 33 * s
        rect(L, mx - 6 * s, my - 2 * s, mx + 6 * s, my + 2 * s + 8 * s * cara_abierta, (60, 30, 30), r=3 * s)


def personaje(L, x, y, s, look, t=0.0, anda=False, habla=0.0, brazo=0.1, brazo2=-0.1, cara="feliz", luz=1.0):
    paso = math.sin(t * 9) if anda else 0.0
    b1 = brazo + (0.35 * math.sin(t * 9) if anda else 0)
    b2 = brazo2 - (0.35 * math.sin(t * 9) if anda else 0)
    bote = abs(math.sin(t * 9)) * 4 * s if anda else 0
    bloque(L, x, y - bote, s, look, brazo=b1, brazo2=b2, paso=paso, cara=cara, luz=luz)
    abierta = (0.5 + 0.5 * math.sin(t * 22)) if habla > 0 else 0.0
    accesorios(L, x, y - bote, s, look, cara_abierta=abierta * habla)


def lupa(L, x, y, r=40, a=1.0, ang=0.8):
    circ(L, x, y, r, outline=(200, 170, 90), w=6, a=a)
    circ(L, x, y, r - 3, fill=(200, 230, 255), a=0.12 * a)
    linea(L, [(x + r * math.cos(ang), y + r * math.sin(ang)), (x + (r + 46) * math.cos(ang), y + (r + 46) * math.sin(ang))],
          (90, 60, 40), w=10, a=a)


def lluvia_c(O, T, a=1.0):
    rs = random.Random(5)
    for _ in range(100):
        x0 = rs.uniform(-100, W)
        y = (rs.uniform(0, H) + T * rs.uniform(800, 1100)) % (H + 40) - 20
        linea(O, [(x0 + y * 0.2, y), (x0 + y * 0.2 + 4, y + 16)], (170, 190, 220), w=1, a=0.4 * a)


def sala_interrogatorio(L, T, t):
    rect(L, 0, 0, W, H, (16, 16, 22))
    rect(L, 0, 330, W, 800, (34, 34, 44))
    for x in range(0, W, 60):
        linea(L, [(x, 330), (x, 800)], (40, 40, 52), w=2)
    ang = 0.25 * math.sin(T * 1.8)
    lx, ly = 270 + 150 * math.sin(ang), 330 + 150 * math.cos(ang)
    linea(L, [(270, 300), (lx, ly - 10)], (20, 20, 20), w=2)
    poly(L, [(lx - 30, ly), (lx + 30, ly), (lx + 16, ly - 18), (lx - 16, ly - 18)], (60, 60, 70))
    poly(L, [(lx - 26, ly), (lx + 26, ly), (lx + 170, 820), (lx - 170, 820)], (255, 240, 190), a=0.12)
    circ(L, lx, ly + 2, 8, fill=(255, 245, 210))
    return lx


def mesa_int(L):
    cubo(L, 70, 760, 400, 34, (70, 52, 40), 14)
    rect(L, 90, 794, 110, 900, (50, 38, 30))
    rect(L, 430, 794, 450, 900, (50, 38, 30))


def ficha(O, nombre, oficio, look, q, num):
    if q <= 0:
        return
    x = lerp(-200, 140, eo3(q))
    rect(O, x - 120, 330, x + 120, 410, (240, 236, 220), a=q, r=6)
    rect(O, x - 120, 330, x - 110, 410, (200, 40, 40), a=q)
    texto(O, f"SOSPECHOSO {num}", x - 100, 348, 12, (160, 40, 40), a=q, fuente="black", anchor="lm", sombra=False)
    texto(O, nombre, x - 100, 374, 26, (30, 30, 30), a=q, fuente="black", anchor="lm", sombra=False)
    texto(O, oficio, x - 100, 398, 12, (90, 90, 90), a=q, fuente="bold", anchor="lm", sombra=False)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    cielo(L, T, 1.0)
    rect(L, 0, 700, W, H, (20, 22, 34))
    focos = [110, 270, 430]
    for j, (x, (n, o, look)) in enumerate(zip(focos, SOSPECHOSOS)):
        on = prog(t, j * 0.25, 0.2)
        poly(L, [(x - 20, 300), (x + 20, 300), (x + 90, 900), (x - 90, 900)], (255, 240, 190), a=0.12 * on)
        L.d.ellipse(P(x - 80, 880, x + 80, 920), fill=L.c((255, 240, 190), 0.12 * on))
        personaje(L, x, 900, 0.85, look, t=T + j, luz=0.35 + 0.65 * on, cara="susto")
    st["overlay"].append(("titular_caso", t, e))


def esc_recap(L, e, t, D, T, st):
    tl = wt(e, "luces") - 0.2
    pueblo(L, T, noche=1.0, farolas=1 - prog(t, tl, 0.3), cartel=1 - prog(t, wt(e, "cartel") - 0.3, 0.5), gente=False,
           robado=t > wt(e, "cartel"), sin_luces=t > tl)
    oscuridad(L, 0.4 * prog(t, tl, 0.3))
    st["flashback"] = True


def esc_detective(L, e, t, D, T, st):
    pueblo(L, T, noche=0.0, cartel=0.0, robado=True, gente=False)
    u = prog(t, 0.0, 2.2)
    x = lerp(-60, 270, eo3(u))
    personaje(L, x, 900, 1.05, DETECTIVE, t=t, anda=u < 1, brazo2=-1.2 if u >= 1 else -0.1)
    if u >= 1:
        lupa(L, x + 70, 690 + 4 * math.sin(t * 3), 30)
    q = prog(t, wt(e, "Bloque") - 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("placa", "DETECTIVE BLOQUE", q))


def esc_pista1(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (40, 44, 54))
    # caja eléctrica en la pared
    cubo(L, 150, 400, 240, 320, (150, 156, 166), 16)
    abre = eio(prog(t, wt(e, "rota") - 0.3, 0.6))
    rect(L, 166, 416, 374, 704, (40, 44, 50))
    for k in range(6):
        rect(L, 190 + (k % 3) * 60, 440 + (k // 3) * 90, 230 + (k % 3) * 60, 500 + (k // 3) * 90, (80, 84, 90), r=4)
    puerta_w = 208 * (1 - abre * 0.85)
    cubo(L, 166, 416, puerta_w, 288, (170, 176, 186), 6)
    texto(L, "⚡", 166 + puerta_w / 2, 560, 40, (250, 200, 40), a=1 - abre, fuente="sym", sombra=False)
    tk = wt(e, "llave") - 0.3
    if t > tk:
        q = prog(t, tk, 0.3)
        ang = 0.3 * math.sin(t * 5)
        kx, ky = 380, 560
        circ(L, kx + 20, ky, 14, outline=(230, 190, 70), w=5, a=q)
        linea(L, [(kx + 6, ky), (kx - 40, ky + 30 * ang)], (230, 190, 70), w=6, a=q)
        st["overlay"].append(("lupa_zoom", 396, 560, prog(t, tk + 0.2, 0.4), "ABIERTA CON LLAVE"))
    st["overlay"].append(("num_pista", 1, prog(t, 0.05, 0.3)))


def esc_pista2(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (60, 64, 74))
    rect(L, 0, 520, W, H, ACERA)
    for x in range(0, W, 90):
        linea(L, [(x, 520), (x - 40, H)], (170, 170, 176), w=2)
    rect(L, 120, 330, 134, 560, (90, 90, 100))
    rect(L, 406, 330, 420, 560, (90, 90, 100))
    th = wt(e, "huella") - 0.3
    q = prog(t, th, 0.4)
    x, y = 270, 720
    rect(L, x - 34, y - 60, x + 34, y + 60, (250, 250, 246), a=q, r=8)
    for k in range(4):
        rect(L, x - 30 + k * 17, y - 84, x - 18 + k * 17, y - 66, (250, 250, 246), a=q, r=3)
    rs = random.Random(2)
    for _ in range(40):
        circ(L, x + rs.uniform(-70, 70), y + rs.uniform(-90, 90), rs.uniform(1, 3), fill=BLANCO, a=q * 0.8)
    if q > 0:
        st["overlay"].append(("lupa_zoom", x, y, prog(t, th + 0.3, 0.4), "HARINA"))
    st["overlay"].append(("num_pista", 2, prog(t, 0.05, 0.3)))


def esc_pista3(L, e, t, D, T, st):
    tll = wt(e, "llovió") - 0.4
    noche = 1.0
    rect(L, 0, 0, W, H, (24, 26, 40))
    rect(L, 0, 600, W, H, (70, 56, 44))
    for k in range(8):
        L.d.ellipse(P(20 + k * 64, 640 + (k % 3) * 60, 80 + k * 64, 660 + (k % 3) * 60), fill=L.c((50, 40, 32)))
    q = prog(t, wt(e, "flor") - 0.3, 0.4)
    x, y = 270, 730
    for k in range(5):
        ang = k / 5 * 2 * math.pi + 0.3
        L.d.ellipse(P(x + 22 * math.cos(ang) - 16, y + 10 * math.sin(ang) - 8, x + 22 * math.cos(ang) + 16,
                      y + 10 * math.sin(ang) + 8), fill=L.c(VIOLETA, q))
    circ(L, x, y, 8, fill=(250, 210, 60), a=q)
    linea(L, [(x + 10, y + 6), (x + 70, y + 30)], (70, 140, 60), w=4, a=q)
    if q > 0:
        st["overlay"].append(("lupa_zoom", x, y, prog(t, wt(e, "flor") + 0.3, 0.4), "FLOR VIOLETA"))
    if t > tll:
        st["lluvia"] = prog(t, tll, 0.4)
        st["relampago"] = 1.0 if (t - tll) % 2.2 < 0.12 else 0.0
        st["overlay"].append(("aquella", prog(t, tll, 0.4)))
    st["overlay"].append(("num_pista", 3, prog(t, 0.05, 0.3)))
    _ = noche


def esc_like(L, e, t, D, T, st):
    # tablero de pruebas con hilos rojos
    rect(L, 0, 0, W, H, (60, 40, 30))
    rect(L, 30, 330, 510, 820, (170, 130, 90))
    for k in range(40):
        rs = random.Random(k)
        circ(L, rs.uniform(40, 500), rs.uniform(340, 810), 1.5, fill=(140, 100, 70))
    fotos = [(120, 420, "LLAVE", (230, 190, 70)), (420, 430, "HARINA", BLANCO), (150, 700, "FLOR", VIOLETA),
             (400, 690, "¿?", (200, 40, 40))]
    for j, (x, y, txt, col) in enumerate(fotos):
        q = prog(t, 0.1 + j * 0.25, 0.3)
        rect(L, x - 60, y - 50, x + 60, y + 50, (240, 236, 220), a=q)
        rect(L, x - 50, y - 40, x + 50, y + 22, (40, 40, 50), a=q)
        texto(L, txt, x, y - 10, 16, col, a=q, fuente="black", sombra=False)
        circ(L, x, y - 50, 6, fill=(200, 40, 40), a=q)
    hilo = prog(t, 1.0, 1.5)
    pts = [(120, 370), (420, 380), (400, 640), (150, 650), (120, 370)]
    tot = len(pts) - 1
    for k in range(tot):
        u = cl(hilo * tot - k)
        if u > 0:
            (x0, y0), (x1, y1) = pts[k], pts[k + 1]
            linea(L, [(x0, y0), (lerp(x0, x1, u), lerp(y0, y1, u))], (200, 30, 30), w=3)
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))


def esc_interrogatorio(L, e, t, D, T, st, idx):
    sala_interrogatorio(L, T, t)
    n, o, look = SOSPECHOSOS[idx]
    hablando = any(e["voz_t0"] - e["t0"] + w["t"] <= t <= e["voz_t0"] - e["t0"] + w["t"] + w["d"] for w in e["palabras"])
    personaje(L, 270, 905, 1.5, look, t=t, habla=1.0 if hablando else 0.0, brazo=0.2, brazo2=-0.2 - 0.3 * math.sin(t * 2))
    mesa_int(L)
    # silueta del detective en primer plano
    bloque(L, 470, 1040, 1.2, DETECTIVE, silueta=(8, 8, 12))
    st["overlay"].append(("ficha", n, o, look, prog(t, 0.1, 0.5), idx + 1))
    st["sospechoso"] = idx


def esc_tito(L, e, t, D, T, st):
    esc_interrogatorio(L, e, t, D, T, st, 0)
    q = prog(t, wt(e, "llave") - 0.3, 0.3)
    if q > 0:
        st["overlay"].append(("dato", "TIENE LA LLAVE", 520, q))


def esc_paco(L, e, t, D, T, st):
    esc_interrogatorio(L, e, t, D, T, st, 1)
    q = prog(t, wt(e, "harina") - 0.3, 0.3)
    if q > 0:
        st["overlay"].append(("dato", "LA HARINA ES SUYA", 520, q))


def esc_lola(L, e, t, D, T, st):
    esc_interrogatorio(L, e, t, D, T, st, 2)
    q = prog(t, wt(e, "regando") - 0.3, 0.3)
    if q > 0:
        st["overlay"].append(("dato", "«REGANDO SUS FLORES»", 520, q))


def esc_pregunta(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (12, 12, 20))
    rect(L, 0, 820, W, H, (24, 24, 34))
    foco_x = 270 + 170 * math.sin(t * 2.2)
    for j, (n, o, look) in enumerate(SOSPECHOSOS):
        x = 110 + j * 160
        cerca = cl(1 - abs(foco_x - x) / 120)
        personaje(L, x, 900, 0.85, look, t=T + j, luz=0.3 + 0.7 * cerca, cara="susto")
        texto(L, n, x, 940, 22, BLANCO, a=0.5 + 0.5 * cerca, fuente="black")
    poly(L, [(foco_x - 20, 300), (foco_x + 20, 300), (foco_x + 100, 920), (foco_x - 100, 920)], (255, 240, 190), a=0.12)
    q = prog(t, wt(e, "miente") - 0.3, 0.35)
    if q > 0:
        st["overlay"].append(("miente", q))


def esc_final(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (14, 14, 22))
    for j, (n, o, look) in enumerate(SOSPECHOSOS):
        personaje(L, 110 + j * 160, 900, 0.75, look, t=T + j, luz=0.8)
    st["overlay"].append(("votacion", t, prog(t, wt(e, "aciertas") - 0.3, 0.4)))
    st["sin_cabecera"] = False


FUNCS = {"gancho": esc_gancho, "recap": esc_recap, "detective": esc_detective, "pista1": esc_pista1,
         "pista2": esc_pista2, "pista3": esc_pista3, "like": esc_like, "tito": esc_tito, "paco": esc_paco,
         "lola": esc_lola, "pregunta": esc_pregunta, "final": esc_final}


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "titular_caso":
            _, t, e = it
            s = 1 + 0.4 * math.exp(-t * 9)
            texto(O, "UNO ES UN LADRÓN", 270, 345, 40 * s, (255, 90, 90), fuente="black")
            texto(O, "¿QUIÉN?", 270, 405, 54 * s, AMAR, fuente="black")
        elif tipo == "placa":
            _, txt, q = it
            s = eob(q)
            rect(O, 270 - 150 * s, 330, 270 + 150 * s, 390, (40, 30, 24), a=q, r=10)
            texto(O, txt, 270, 360, 26 * s, AMAR, a=q, fuente="black", sombra=False)
        elif tipo == "num_pista":
            _, n, q = it
            rect(O, 160, 330, 380, 390, (0, 0, 0), a=0.7 * q, r=30)
            texto(O, f"PISTA {n}", 270, 360, 32, AMAR, a=q, fuente="black", sombra=False)
        elif tipo == "lupa_zoom":
            _, x, y, q, txt = it
            if q <= 0:
                continue
            r = 70 * eob(q)
            # recorte ampliado bajo la lupa
            box = (int((x - r / 2) * K), int((y - r / 2) * K), int((x + r / 2) * K), int((y + r / 2) * K))
            if r > 4:
                zona = O.img.crop(box).resize((int(r * 2 * K), int(r * 2 * K)), Image.BILINEAR)
                m = Image.new("L", zona.size, 0)
                ImageDraw.Draw(m).ellipse((0, 0, zona.size[0] - 1, zona.size[1] - 1), fill=255)
                O.img.paste(zona, (int((x - r) * K), int((y - r) * K)), m)
                O.d = ImageDraw.Draw(O.img, "RGBA")
            lupa(O, x, y, r, a=q)
            w = ancho(txt, 18) + 30
            rect(O, 270 - w / 2, 870, 270 + w / 2, 910, AMAR, a=q, r=20)
            texto(O, txt, 270, 890, 18, (20, 20, 20), a=q, fuente="black", sombra=False)
        elif tipo == "aquella":
            q = it[1]
            rect(O, 90, 420, 450, 470, (0, 0, 0), a=0.65 * q, r=25)
            texto(O, "AQUELLA NOCHE LLOVIÓ", 270, 445, 22, (160, 200, 255), a=q, fuente="black", sombra=False)
        elif tipo == "like":
            _, t, tl = it
            q = prog(t, tl, 0.35)
            s = eob(q) * (1 + 0.08 * math.sin(t * 8))
            corazon(O, 270, 560, 70 * s, (254, 44, 85), a=cl(q * 1.5))
            texto(O, "DALE LIKE", 270, 640, 30 * (0.8 + 0.2 * eob(q)), BLANCO, a=q, fuente="black")
        elif tipo == "ficha":
            _, n, o, look, q, num = it
            ficha(O, n, o, look, q, num)
        elif tipo == "dato":
            _, txt, y, q = it
            w = ancho(txt, 20) + 30
            x = 400
            rect(O, x - w / 2, y - 22, x + w / 2, y + 22, (200, 40, 40), a=q, r=8)
            texto(O, txt, x, y, 20 * (0.8 + 0.2 * eob(q)), BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "miente":
            q = it[1]
            s = 1 + 1.2 * (1 - eo3(q))
            texto(O, "UNO MIENTE", 270, 400, 54 * s, (255, 80, 80), a=q, fuente="black")
        elif tipo == "votacion":
            _, t, qa = it
            texto(O, "¿QUIÉN FUE?", 270, 345, 48, AMAR, fuente="black")
            for j, (n, o, look) in enumerate(SOSPECHOSOS):
                y = 430 + j * 66
                s = 1 + 0.04 * math.sin(t * 6 + j)
                rect(O, 120, y - 26 * s, 420, y + 26 * s, BLANCO, a=0.95, r=26)
                texto(O, f"«Fue {n.capitalize()}»", 270, y, 24, (20, 20, 20), fuente="black", sombra=False)
            if qa > 0:
                rect(O, 70, 640, 470, 700, (40, 120, 200), a=qa, r=30)
                texto(O, "ACIERTA → SALES EN LA PARTE 2", 270, 670, 18, BLANCO, a=qa, fuente="black", sombra=False)


def corazon(O, x, y, r, col, a=1.0):
    if r <= 1:
        return
    circ(O, x - r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    circ(O, x + r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    poly(O, [(x - r * 1.02, y - r * 0.05), (x + r * 1.02, y - r * 0.05), (x, y + r * 0.95)], col, a=a)


def cabecera(O, st):
    if st.get("sin_cabecera"):
        return
    w = ancho(CABECERA, 14) + 30
    rect(O, 270 - w / 2, 148, 270 + w / 2, 180, (40, 30, 24), a=0.95, r=16)
    texto(O, CABECERA, 270, 164, 14, AMAR, fuente="black", sombra=False)


def efectos_caso(img, st, T):
    if st.get("flashback"):
        a = np.asarray(img).astype(np.float32)
        g = a.mean(axis=2)
        a = np.stack([g * 0.7, g * 0.85, g * 1.15 + 10], -1)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if st.get("relampago"):
        img = Image.blend(img, Image.new("RGB", (IW, IH), (220, 230, 255)), 0.5 * st["relampago"])
    return img


# ------------------------------------------------------------------ render (caso)
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
    img = efectos_caso(img, st, T)
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    if st.get("lluvia"):
        lluvia_c(O, T, st["lluvia"])
    overlays(O, st, T)
    cabecera(O, st)
    subtitulos(O, T)
    out = O.img
    if T > TOTAL - 0.5:
        out = Image.blend(out, Image.new("RGB", (IW, IH), (0, 0, 0)), cl((T - (TOTAL - 0.5)) / 0.5))
    return out.resize((OW, OH), Image.LANCZOS).tobytes()


def musica(n):
    """Jazz de detectives: contrabajo andante, escobillas y vibráfono (Re menor)."""
    out = np.zeros(n, np.float32)
    beat = 60 / 108
    bajo = [38, 41, 43, 44, 45, 43, 41, 40, 38, 36, 34, 36, 37, 40, 43, 45]
    vib = [[62, 65, 69, 72], [58, 62, 65, 69], [55, 58, 62, 65], [57, 61, 64, 67]]
    E = {e["nombre"]: e for e in ESC}
    k = 0
    while k * beat < TOTAL:
        t0 = k * beat
        f = 440 * 2 ** ((bajo[k % 16] - 69) / 12)
        m = int(beat * SR)
        u = np.arange(m) / SR
        s = (np.sin(2 * np.pi * f * u) + 0.3 * np.sin(4 * np.pi * f * u)) * np.exp(-u * 4) * 0.12
        colocar(out, s.astype(np.float32), t0)
        if k % 2 == 1:
            mm = int(0.18 * SR)
            r = np.random.default_rng(k).standard_normal(mm).astype(np.float32)
            colocar(out, r * 0.025 * np.exp(-np.arange(mm) / SR * 18), t0)
        if k % 4 == 0:
            for nn in vib[(k // 4) % 4]:
                ff = 440 * 2 ** ((nn - 69) / 12)
                mm = int(1.6 * SR)
                uu = np.arange(mm) / SR
                colocar(out, (np.sin(2 * np.pi * ff * uu) * (0.7 + 0.3 * np.sin(2 * np.pi * 5 * uu)) * np.exp(-uu * 2)
                              * 0.012).astype(np.float32), t0 + 0.02 * nn % 0.1)
        k += 1
    return out


def trompeta(notas, dur=0.4):
    out = np.zeros(int(len(notas) * dur * SR + SR), np.float32)
    for j, nn in enumerate(notas):
        f = 440 * 2 ** ((nn - 69) / 12)
        m = int(dur * SR * (2.2 if j == len(notas) - 1 else 0.95))
        u = np.arange(m) / SR
        s = saw(f * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * u)), u, 6)
        s = np.convolve(s, np.ones(12) / 12, mode="same") * np.clip(u / 0.03, 0, 1) * np.exp(-u * 1.2)
        colocar(out, (s * 0.06).astype(np.float32), j * dur)
    return out


def pasos(dur, cada=0.33):
    out = np.zeros(int(dur * SR), np.float32)
    t = 0.0
    k = 0
    while t < dur - 0.1:
        m = int(0.08 * SR)
        u = np.arange(m) / SR
        r = np.random.default_rng(k).standard_normal(m).astype(np.float32)
        colocar(out, (np.convolve(r, np.ones(10) / 10, mode="same") * np.exp(-u * 40) * 0.6).astype(np.float32), t)
        t += cada
        k += 1
    return out


def maquina_escribir(dur=0.8):
    out = np.zeros(int(dur * SR), np.float32)
    rng = np.random.default_rng(3)
    t = 0.0
    while t < dur - 0.05:
        m = int(0.02 * SR)
        colocar(out, (rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 200) * 0.4).astype(np.float32), t)
        t += rng.uniform(0.06, 0.11)
    return out


def lluvia_s(dur):
    m = int(dur * SR)
    r = np.random.default_rng(8).standard_normal(m).astype(np.float32)
    r = r - np.convolve(r, np.ones(20) / 20, mode="same")
    return (r * 0.12 * np.clip(np.arange(m) / (0.4 * SR), 0, 1)).astype(np.float32)


def trueno(seed=1):
    m = int(2.5 * SR)
    u = np.arange(m) / SR
    r = np.random.default_rng(seed).standard_normal(m).astype(np.float32)
    r = np.convolve(r, np.ones(120) / 120, mode="same") * 10
    return (r * np.exp(-u * 1.3) * 0.6).astype(np.float32)


def crujido_lampara(dur):
    m = int(dur * SR)
    u = np.arange(m) / SR
    f = 300 + 80 * np.sin(2 * np.pi * 0.29 * u)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (np.abs(np.sin(2 * np.pi * 0.29 * u)) > 0.95) * 0.03
    return s.astype(np.float32)


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
    fx = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    colocar(fx, braam(), 0.0, 0.6)
    colocar(fx, trompeta([62, 65, 64, 61]), 0.1, 0.6)
    r_ = E["recap"]
    colocar(fx, apagon_s(), r_["t0"] + wt(r_, "luces") - 0.2, 0.6)
    d = E["detective"]
    colocar(fx, pasos(2.2), d["t0"], 0.5)
    colocar(fx, trompeta([57, 62, 65, 69], 0.25), d["t0"] + wt(d, "Bloque") - 0.3, 0.6)
    for nombre, pal in (("pista1", "llave"), ("pista2", "huella"), ("pista3", "flor")):
        p = E[nombre]
        colocar(fx, ping(), p["t0"] + 0.1, 0.4)
        colocar(fx, ping(), p["t0"] + wt(p, pal) - 0.1, 0.6)
    p3 = E["pista3"]
    tll = p3["t0"] + wt(p3, "llovió") - 0.4
    colocar(fx, lluvia_s(p3["t0"] + p3["dur"] - tll + 0.3), tll, 0.25)
    colocar(fx, trueno(2), tll + 0.1, 0.6)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.6)
    for nombre in ("tito", "paco", "lola"):
        s = E[nombre]
        colocar(fx, maquina_escribir(0.8), s["t0"] + 0.1, 0.4)
        colocar(fx, crujido_lampara(s["dur"]), s["t0"], 0.6)
    pr = E["pregunta"]
    colocar(fx, braam(), pr["t0"] + wt(pr, "miente") - 0.3, 0.9)
    colocar(fx, trompeta([62, 61, 60, 59], 0.3), pr["t0"] + wt(pr, "miente") + 0.4, 0.5)
    fi = E["final"]
    for k in range(3):
        colocar(fx, pop(), fi["t0"] + 0.5 + k * 0.4, 0.4)
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




# --- Valdemora · Ep. 01 «Las 3:17»: escenas (se insertan en video.py al montarlo) ---

# ------------------------------------------------------------------ fichas visuales (no cambiar entre escenas)
PIEL_A = (246, 214, 178)
LEO_L = dict(camisa=(217, 162, 59), pantalon=(30, 38, 70), zapato=(245, 245, 245), suela=(210, 40, 40),
             pelo=(70, 44, 30), peinado="flequillo", sudadera=True)
DOBLE_L = dict(LEO_L, camisa=(190, 140, 50), pelo=(60, 38, 26))          # sudadera algo húmeda y oscurecida
ABUELA_L = dict(camisa=(120, 30, 46), pantalon=(70, 70, 76), falda=(70, 70, 76), zapato=(110, 70, 40),
                suela=(80, 50, 30), pelo=(196, 196, 204), peinado="moño", gafas=(214, 176, 80), rebeca=True)
JULIAN_L = dict(camisa=(240, 240, 236), pantalon=(120, 120, 124), zapato=(30, 30, 30), suela=(20, 20, 20),
                pelo=(24, 22, 20), peinado="peinado", tirantes=(110, 70, 40))
ALUMNOS = [dict(camisa=c, pantalon=(50, 56, 80), zapato=(240, 240, 240), suela=(60, 60, 60), pelo=p, peinado="corto")
           for c, p in (((90, 130, 200), (40, 30, 24)), ((200, 80, 80), (150, 90, 40)), ((90, 170, 110), (30, 30, 30)),
                        ((230, 230, 230), (200, 150, 70)), ((150, 100, 190), (60, 40, 30)), ((240, 160, 70), (20, 20, 20)))]
CABECERA = "VALDEMORA · EP. 01"


def cara_ojos(L, ex, ey, s, tipo, mira=0.0, a=1.0):
    tinta = (26, 22, 20)
    dx = mira * 3 * s
    if tipo == "cerrados":
        linea(L, [(ex - 4 * s, ey), (ex + 4 * s, ey)], tinta, w=2 * s, a=a)
    elif tipo == "miedo":
        L.d.ellipse(P(ex - 6 * s, ey - 8 * s, ex + 6 * s, ey + 8 * s), fill=L.c(BLANCO, a))
        circ(L, ex + dx, ey, 2.4 * s, fill=tinta, a=a)
    elif tipo == "doble":
        L.d.ellipse(P(ex - 6.5 * s, ey - 9 * s, ex + 6.5 * s, ey + 9 * s), fill=L.c((4, 4, 6), a))
        circ(L, ex - 2 * s, ey - 4 * s, 1.8 * s, fill=(255, 255, 255), a=a * 0.9)
    else:
        L.d.ellipse(P(ex - 3.6 * s + dx, ey - 6 * s, ex + 3.6 * s + dx, ey + 6 * s), fill=L.c(tinta, a))
        circ(L, ex - 1 * s + dx, ey - 2.5 * s, 1.1 * s, fill=(255, 255, 255), a=a * 0.8)


def avatar(L, x, y, s, look, cara="neutral", mira=0.0, brazos=(0.08, -0.08), paso=0.0, espalda=False, luz=1.0,
           boca=0.0, frio=0.0, sonrisa=1.0, lagrima=0.0, a=1.0):
    """Personaje de bloques 3D visto de frente; (x, y) = pies. Respeta las fichas visuales."""
    def C(c):
        c = mezcla(c, (70, 90, 140), frio * 0.5)
        return tuple(int(v * luz) for v in c)
    pr = 7 * s
    lh = 60 * s
    if look.get("falda"):
        for dx in (-13 * s, 3 * s):
            cubo(L, x + dx, y - 22 * s, 10 * s, 18 * s, C(PIEL_A), pr * 0.5, a)
            cubo(L, x + dx - 2 * s, y - 6 * s, 14 * s, 7 * s, C(look["zapato"]), pr * 0.5, a)
        cubo(L, x - 28 * s, y - lh - 2 * s, 56 * s, lh - 18 * s, C(look["falda"]), pr, a)
    else:
        for k, dx in enumerate((-18 * s, 1 * s)):
            dy = paso * 7 * s * (1 if k == 0 else -1)
            cubo(L, x + dx, y - lh + dy, 17 * s, lh - 9 * s - dy, C(look["pantalon"]), pr, a)
            cubo(L, x + dx - 1 * s, y - 9 * s - dy * 0.2, 19 * s, 7 * s, C(look["zapato"]), pr * 0.6, a)
            rect(L, x + dx - 1 * s, y - 3 * s - dy * 0.2, x + dx + 18 * s, y, C(look["suela"]), a=a)
    ty = y - lh - 62 * s
    if look.get("sudadera"):
        cubo(L, x - 24 * s, ty - 8 * s, 48 * s, 16 * s, C(sombra_c(look["camisa"], 0.8)), pr, a)
    cubo(L, x - 27 * s, ty, 54 * s, 62 * s, C(look["camisa"]), pr, a)
    if look.get("sudadera") and not espalda:
        rect(L, x - 16 * s, ty + 38 * s, x + 16 * s, ty + 54 * s, C(sombra_c(look["camisa"], 0.82)), a=a, r=3 * s)
        for dx in (-6 * s, 6 * s):
            linea(L, [(x + dx, ty + 2 * s), (x + dx, ty + 18 * s)], C((240, 230, 200)), w=1.6 * s, a=a)
    if look.get("rebeca") and not espalda:
        poly(L, [(x - 10 * s, ty), (x + 10 * s, ty), (x, ty + 22 * s)], C((240, 230, 210)), a=a)
        for k in range(4):
            circ(L, x, ty + 26 * s + k * 9 * s, 1.8 * s, fill=C((230, 200, 120)), a=a)
    if look.get("tirantes"):
        for dx in (-12 * s, 12 * s):
            linea(L, [(x + dx, ty), (x + dx, ty + 62 * s)], C(look["tirantes"]), w=3 * s, a=a)
    for lado, ang in ((-1, brazos[0]), (1, brazos[1])):
        hx = x + lado * 35 * s
        hy = ty + 5 * s
        largo = 56 * s
        ca, sa = math.cos(ang), math.sin(ang)
        wv = 16 * s
        pts = [(-wv / 2, 0), (wv / 2, 0), (wv / 2, largo), (-wv / 2, largo)]
        rot = [(hx + px * ca + py * sa * lado, hy - px * sa * lado + py * ca) for px, py in pts]
        poly(L, rot, C(sombra_c(look["camisa"], 0.92)), a=a)
        mx, my = (rot[2][0] + rot[3][0]) / 2, (rot[2][1] + rot[3][1]) / 2
        rect(L, mx - 8 * s, my - 2 * s, mx + 8 * s, my + 12 * s, C(PIEL_A), a=a, r=2 * s)
    hs = 48 * s
    hx0, hy0 = x - hs / 2, ty - hs - 3 * s
    cubo(L, hx0, hy0, hs, hs, C(PIEL_A), pr, a)
    pelo = C(look["pelo"])
    est = look.get("peinado")
    if espalda:
        rect(L, hx0 - 1, hy0 - 6 * s, hx0 + hs + pr, hy0 + hs * 0.7, pelo, a=a)
    else:
        if est == "flequillo":
            rect(L, hx0 - 2, hy0 - 7 * s, hx0 + hs + pr, hy0 + 9 * s, pelo, a=a)
            for k in range(5):
                bx = hx0 + k * 10 * s
                poly(L, [(bx, hy0 + 8 * s), (bx + 12 * s, hy0 + 8 * s), (bx + 14 * s, hy0 + (13 + k * 1.5) * s)], pelo, a=a)
            rect(L, hx0 - 2, hy0, hx0 + 5 * s, hy0 + 22 * s, pelo, a=a)
        elif est == "moño":
            rect(L, hx0 - 2, hy0 - 5 * s, hx0 + hs + pr, hy0 + 8 * s, pelo, a=a)
            cubo(L, x - 11 * s, hy0 - 24 * s, 22 * s, 20 * s, pelo, pr * 0.7, a)
        elif est == "peinado":
            rect(L, hx0 - 2, hy0 - 6 * s, hx0 + hs + pr, hy0 + 7 * s, pelo, a=a)
            linea(L, [(hx0 + 14 * s, hy0 - 6 * s), (hx0 + 14 * s, hy0 + 6 * s)], C((60, 56, 52)), w=1.2 * s, a=a)
        else:
            rect(L, hx0 - 2, hy0 - 6 * s, hx0 + hs + pr, hy0 + 10 * s, pelo, a=a)
        ey = hy0 + 25 * s
        exs = (hx0 + 15 * s, hx0 + 33 * s)
        tinta = (26, 22, 20)
        for ex in exs:
            cara_ojos(L, ex, ey, s, cara if cara in ("miedo", "doble", "cerrados") else "neutral", mira, a)
        if cara == "miedo":
            for ex in exs:
                linea(L, [(ex - 5 * s, ey - 13 * s), (ex + 5 * s, ey - 15 * s)], pelo, w=2.4 * s, a=a)
        elif cara in ("seria", "triste"):
            linea(L, [(exs[0] - 5 * s, ey - 11 * s), (exs[0] + 5 * s, ey - 9 * s)], pelo, w=2.4 * s, a=a)
            linea(L, [(exs[1] - 5 * s, ey - 9 * s), (exs[1] + 5 * s, ey - 11 * s)], pelo, w=2.4 * s, a=a)
        if look.get("gafas"):
            for ex in exs:
                circ(L, ex, ey, 7.5 * s, outline=C(look["gafas"]), w=1.6 * s, a=a)
            linea(L, [(exs[0] + 7.5 * s, ey), (exs[1] - 7.5 * s, ey)], C(look["gafas"]), w=1.4 * s, a=a)
        my = hy0 + 38 * s
        if cara == "doble":
            ancho_b = 26 * s * sonrisa
            L.d.arc(P(x - ancho_b / 2, my - 10 * s, x + ancho_b / 2, my + 6 * s), 15, 165, fill=L.c(tinta, a),
                    width=max(1, int(2.8 * s * K)))
        elif cara == "miedo" or boca > 0:
            L.d.ellipse(P(x - 4 * s, my - 2 * s, x + 4 * s, my + 6 * s + 4 * s * boca), fill=L.c((70, 30, 30), a))
        elif cara == "triste":
            L.d.arc(P(x - 8 * s, my, x + 8 * s, my + 10 * s), 200, 340, fill=L.c(tinta, a), width=max(1, int(2 * s * K)))
        elif cara == "seria":
            linea(L, [(x - 7 * s, my + 2 * s), (x + 7 * s, my + 2 * s)], tinta, w=2 * s, a=a)
        else:
            L.d.arc(P(x - 8 * s, my - 6 * s, x + 8 * s, my + 4 * s), 20, 160, fill=L.c(tinta, a),
                    width=max(1, int(2 * s * K)))
        if lagrima > 0:
            ly = ey + 8 * s + 18 * s * (lagrima % 1)
            L.d.ellipse(P(exs[0] - 2 * s, ly - 3 * s, exs[0] + 2 * s, ly + 3 * s), fill=L.c((170, 210, 255), a * 0.9))
    return dict(cabeza=(x, hy0 + hs / 2), hs=hs)


# ------------------------------------------------------------------ escenarios
def cielo_noche(L, T, top=(8, 10, 22), bot=(30, 36, 60)):
    for i in range(0, H, 8):
        rect(L, 0, i, W, i + 8, mezcla(top, bot, i / H))
    rs = random.Random(4)
    for _ in range(60):
        circ(L, rs.uniform(0, W), rs.uniform(0, 560), rs.uniform(0.6, 1.6), fill=BLANCO,
             a=0.3 + 0.3 * math.sin(T * 2 + rs.random() * 6))


def montanas(L, y, col, semilla, alto=180):
    rs = random.Random(semilla)
    pts = [(-20, y)]
    for k in range(9):
        pts.append((k * 70 + rs.uniform(-20, 20), y - rs.uniform(alto * 0.4, alto)))
    pts += [(W + 20, y), (W + 20, H), (-20, H)]
    poly(L, pts, col)


def casa_piedra(L, x, y, w, h, luz_on, escala=1.0, frio=0.0):
    pared = mezcla((150, 140, 128), (60, 66, 90), 0.45 + frio * 0.3)
    cubo(L, x, y - h, w, h, pared, 10 * escala)
    poly(L, [(x - 8 * escala, y - h), (x + w / 2 + 5 * escala, y - h - h * 0.5), (x + w + 18 * escala, y - h)],
         mezcla((150, 70, 50), (40, 30, 40), 0.55))
    for k in range(2):
        wx = x + w * (0.2 + k * 0.45)
        ww = w * 0.22
        col = (255, 210, 120) if luz_on else (30, 34, 50)
        rect(L, wx, y - h * 0.75, wx + ww, y - h * 0.45, col)
        if luz_on:
            circ(L, wx + ww / 2, y - h * 0.6, ww * 1.4, fill=(255, 200, 120), a=0.08)
    rect(L, x + w * 0.42, y - h * 0.38, x + w * 0.58, y, (60, 44, 34))


def iglesia(L, x, y, s, hora=(3, 17)):
    cubo(L, x - 40 * s, y - 220 * s, 80 * s, 220 * s, (110, 106, 100), 12 * s)
    poly(L, [(x - 46 * s, y - 220 * s), (x, y - 300 * s), (x + 58 * s, y - 220 * s)], (70, 50, 44))
    cx, cy = x + 6, y - 180 * s
    circ(L, cx, cy, 22 * s, fill=(230, 226, 210))
    circ(L, cx, cy, 22 * s, outline=(40, 40, 40), w=2 * s)
    hh, mm = hora
    am = math.radians(-90 + mm * 6)
    ah = math.radians(-90 + (hh % 12) * 30 + mm * 0.5)
    linea(L, [(cx, cy), (cx + 17 * s * math.cos(am), cy + 17 * s * math.sin(am))], (20, 20, 20), w=2 * s)
    linea(L, [(cx, cy), (cx + 11 * s * math.cos(ah), cy + 11 * s * math.sin(ah))], (20, 20, 20), w=3 * s)


def farola_v(L, x, y, s=1.0, on=1.0):
    rect(L, x - 3 * s, y - 170 * s, x + 3 * s, y, (40, 40, 46))
    cubo(L, x - 12 * s, y - 190 * s, 24 * s, 20 * s, (50, 50, 56), 5 * s)
    if on > 0:
        circ(L, x, y - 180 * s, 9 * s, fill=(255, 230, 160), a=on)
        poly(L, [(x - 10 * s, y - 172 * s), (x + 10 * s, y - 172 * s), (x + 80 * s, y), (x - 80 * s, y)], (255, 220, 150),
             a=0.12 * on)


def puerta_verde(L, x, y, w, h, temblor=0.0, mirilla_brillo=0.0):
    dx = temblor
    cubo(L, x - 8, y - h - 8, w + 16, h + 8, (60, 44, 34), 10)
    cubo(L, x + dx, y - h, w, h, (34, 70, 52), 8)
    for k in range(2):
        rect(L, x + dx + 12, y - h + 20 + k * h * 0.48, x + dx + w - 12, y - h + 10 + (k + 1) * h * 0.46, (28, 60, 44), r=3)
    circ(L, x + dx + w - 22, y - h * 0.48, 6, fill=(210, 176, 90))
    circ(L, x + dx + w / 2, y - h * 0.72, 5, fill=(210, 176, 90))
    if mirilla_brillo > 0:
        circ(L, x + dx + w / 2, y - h * 0.72, 12, fill=(255, 240, 180), a=0.5 * mirilla_brillo)


def reloj_pendulo(L, x, y, s, t, hora=(3, 17), parado=False):
    cubo(L, x - 28 * s, y - 150 * s, 56 * s, 150 * s, (70, 44, 30), 8 * s)
    circ(L, x, y - 118 * s, 20 * s, fill=(236, 226, 200))
    hh, mm = hora
    for ang, ln, w_ in ((math.radians(-90 + mm * 6), 15, 2), (math.radians(-90 + (hh % 12) * 30 + mm * 0.5), 10, 3)):
        linea(L, [(x, y - 118 * s), (x + ln * s * math.cos(ang), y - 118 * s + ln * s * math.sin(ang))], (30, 30, 30),
              w=w_ * s)
    ang = 0 if parado else 0.32 * math.sin(t * 3.2)
    px, py = x + 46 * s * math.sin(ang), y - 86 * s + 46 * s * math.cos(ang)
    linea(L, [(x, y - 86 * s), (px, py)], (200, 170, 90), w=2 * s)
    circ(L, px, py, 8 * s, fill=(210, 176, 90))


def papel_pintado(L, x0, y0, x1, y1, base=(110, 40, 50), motivo=(140, 60, 66)):
    rect(L, x0, y0, x1, y1, base)
    for yy in range(int(y0) + 20, int(y1), 46):
        for xx in range(int(x0) + ((yy // 46) % 2) * 23, int(x1), 46):
            circ(L, xx, yy, 5, fill=motivo, a=0.6)


# ------------------------------------------------------------------ escenas
def esc_regla(L, e, t, D, T, st):
    ta = wt(e, "abras") - 0.1
    cielo_noche(L, T)
    circ(L, 430, 330, 34, fill=(220, 226, 240))
    circ(L, 430, 330, 90, fill=(200, 210, 240), a=0.06)
    montanas(L, 560, (24, 28, 44), 3, 200)
    montanas(L, 610, (32, 36, 56), 5, 140)
    iglesia(L, 270, 640, 1.0)
    for y, sc, n in ((660, 0.55, 9), (730, 0.75, 7), (820, 1.0, 5)):
        for j in range(n):
            x = -20 + j * (W + 40) / n + (12 if n % 2 else 0)
            apaga_en = ta + 0.15 * (x / W) * 4
            casa_piedra(L, x, y, 70 * sc, 70 * sc, luz_on=t < apaga_en, escala=sc)
    rect(L, 0, 820, W, H, (26, 26, 34))
    farola_v(L, 120, 880, 0.9, on=1.0 if t < ta + 0.8 else 0.25)
    st["niebla"] = 0.55
    st["cam"] = (1.0 + 1.1 * eio(prog(t, 0.3, D)), lerp(270, 300, eio(t / D)), lerp(480, 760, eio(t / D)))
    st["titulo_si"] = t
    st["grado"] = "frio"


def cocina(L, T, t):
    rect(L, 0, 0, W, H, (40, 30, 26))
    rect(L, 0, 300, W, 800, (120, 92, 70))
    for x in range(0, W, 54):
        linea(L, [(x, 300), (x, 800)], (110, 84, 64), w=2)
    cubo(L, 20, 380, 170, 120, (90, 60, 40), 10)
    cubo(L, 20, 600, 220, 200, (100, 68, 46), 10)
    rect(L, 20, 590, 240, 604, (180, 170, 160))
    rect(L, 320, 380, 440, 500, (30, 40, 70))
    circ(L, 400, 410, 14, fill=(220, 226, 240), a=0.8)
    linea(L, [(380, 380), (380, 500)], (70, 50, 40), w=4)
    reloj_pendulo(L, 480, 640, 1.0, t)
    for bx, by in ((300, 800), (360, 800), (330, 750)):
        cubo(L, bx, by - 50, 70, 50, (190, 150, 100), 8)
        linea(L, [(bx, by - 25), (bx + 70, by - 25)], (150, 110, 70), w=3)
    rect(L, 0, 800, W, H, (70, 50, 38))
    ang = 0.05 * math.sin(T * 1.2)
    lx = 270 + 200 * math.sin(ang)
    linea(L, [(270, 300), (lx, 400)], (30, 30, 30), w=2)
    poly(L, [(lx - 34, 430), (lx + 34, 430), (lx + 16, 400), (lx - 16, 400)], (220, 150, 60))
    circ(L, lx, 432, 10, fill=(255, 220, 150))
    circ(L, lx, 440, 160, fill=(255, 200, 120), a=0.06)
    return lx, 432


def esc_advertencia(L, e, t, D, T, st):
    cocina(L, T, t)
    tg = wt(e, "advierte") - 0.4
    agarra = eio(prog(t, tg, 0.4))
    avatar(L, 160, 900, 1.6, ABUELA_L, cara="seria" if agarra > 0.5 else "neutral", brazos=(0.08, -0.08 - 0.9 * agarra))
    avatar(L, 380, 900, 1.6, LEO_L, cara="miedo" if agarra > 0.8 else "neutral", mira=-1 if agarra > 0.5 else 0,
           brazos=(0.08 + 0.5 * agarra, -0.08))
    st["cam"] = (1.05 + 0.12 * eio(t / D), 270, 560)
    st["grado"] = "calido"


def esc_abuela1(L, e, t, D, T, st):
    tr = D * 0.62
    if t < tr:
        cocina(L, T, t)
        st["desenfoque"] = 7
        st["primer_plano"] = ("abuela", t)
        st["cam"] = (1.0 + 0.05 * eio(t / tr), 270, 480)
    else:
        rect(L, 0, 0, W, H, (40, 30, 26))
        rect(L, 0, 300, W, 900, (110, 84, 64))
        reloj_pendulo(L, 270, 900, 3.2, t)
        st["cam"] = (1.0 + 0.1 * eio((t - tr) / (D - tr)), 270, 560)
    st["grado"] = "calido"


def aula(L, T, t, pan, giro):
    rect(L, 0, 0, W, H, (190, 196, 200))
    rect(L, 0, 300, W, 760, (206, 210, 206))
    cubo(L, 60 - pan * 0.3, 360, 300, 140, (40, 70, 56), 10)
    for k in range(3):
        rect(L, 390 + k * 60 - pan * 0.3, 360, 440 + k * 60 - pan * 0.3, 520, (200, 210, 220))
    rect(L, 0, 760, W, H, (150, 120, 90))
    xv = 0
    for fila, (y, s) in enumerate(((720, 0.9), (830, 1.1))):
        for j in range(5):
            x = 60 + j * 130 - pan * (0.6 + fila * 0.4)
            vacio = fila == 1 and j == 2
            if vacio:
                xv = x
            else:
                look = ALUMNOS[(j + fila * 2) % len(ALUMNOS)]
                mira = (1.2 if x < 270 else -1.2) * giro
                avatar(L, x, y + 40 * s, 0.95 * s, look, cara="seria" if giro > 0.5 else "neutral", mira=mira)
            cubo(L, x - 44 * s, y, 88 * s, 18 * s, (170, 120, 70), 8 * s)
            rect(L, x - 38 * s, y + 18 * s, x - 32 * s, y + 70 * s, (90, 70, 50))
            rect(L, x + 32 * s, y + 18 * s, x + 38 * s, y + 70 * s, (90, 70, 50))
            if vacio:
                for k in range(5):
                    linea(L, [(x - 22 + k * 9, y + 4), (x - 16 + k * 9, y + 14)], (90, 60, 40), w=2)
    return xv


def esc_pupitre(L, e, t, D, T, st):
    tn = wt(e, "nadie") - 0.2
    pan = 180 * eio(prog(t, 0.0, tn - 0.3)) - 60
    giro = eio(prog(t, tn, 0.25))
    xv = aula(L, T, t, pan, giro)
    avatar(L, xv + 70, 930, 1.2, LEO_L, cara="miedo" if giro > 0.5 else "neutral", mira=-1)
    q = prog(t, tn + 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("marco_vacio", xv, 830, q))
    st["cam"] = (1.08 + 0.1 * giro, 270, 600)
    st["grado"] = "aula"
    st["mano"] = 0.4


def pasillo(L, T, t, temblor=0.0, brillo=0.0, luz_puerta=0.0):
    rect(L, 0, 0, W, H, (10, 10, 16))
    vx, vy = 270, 520
    papel_pintado(L, 0, 0, W, H, (60, 22, 30), (80, 34, 40))
    poly(L, [(0, 0), (W, 0), (vx + 80, vy - 150), (vx - 80, vy - 150)], (30, 22, 24))
    poly(L, [(0, H), (W, H), (vx + 80, vy + 170), (vx - 80, vy + 170)], (50, 36, 28))
    for k in range(7):
        u = k / 7
        linea(L, [(lerp(0, vx - 80, u), lerp(H, vy + 170, u)), (lerp(W, vx + 80, u), lerp(H, vy + 170, u))], (40, 30, 24), w=2)
    puerta_verde(L, vx - 70, vy + 170, 140, 300, temblor=temblor, mirilla_brillo=brillo)
    if luz_puerta > 0:
        rect(L, vx - 70, vy + 166, vx + 70, vy + 172, (255, 220, 160), a=luz_puerta)
    reloj_pendulo(L, 70, 760, 1.2, t)


def esc_golpes(L, e, t, D, T, st):
    tf = 1.6
    tl = wt(e, "llamó") + 0.2
    golpes = [tl, tl + 0.75, tl + 1.5]
    g = any(0 <= t - tg < 0.18 for tg in golpes)
    if t < tf:
        rect(L, 0, 0, W, H, (6, 6, 10))
        cubo(L, 110, 420, 320, 170, (20, 20, 24), 14)
        txt = "3:16" if t < tf * 0.55 else ("3:1_" if t < tf * 0.65 else "3:17")
        texto(L, txt, 270, 505, 110, (255, 40, 40), fuente="mono", sombra=False)
        circ(L, 270, 505, 220, fill=(255, 40, 40), a=0.05)
        st["cam"] = (1.0 + 0.15 * eio(t / tf), 270, 500)
    else:
        pasillo(L, T, t, temblor=5 * math.sin(T * 90) if g else 0, brillo=1.0 if g else 0.3, luz_puerta=0.6)
        avance = eio(prog(t, tf, D - tf))
        avatar(L, 130, 990, 2.2, LEO_L, espalda=True, brazos=(0.15, -0.3), paso=math.sin(t * 5) * 0.4 * (1 - avance))
        for k, tg in enumerate(golpes):
            q = prog(t, tg, 0.12)
            if q > 0:
                st["overlay"].append(("toc", k, q * (1 - prog(t, tg + 0.6, 0.3))))
        st["cam"] = (1.05 + 0.5 * avance, 270, 560)
        st["mano"] = 1.0
        st["shake"] = 5 if g else 0
    st["grado"] = "noche"


def porche(L, T, t, acercar=0.0, sonrisa=1.0, parpadeo_farola=False):
    rect(L, 0, 0, W, H, (14, 18, 30))
    montanas(L, 600, (24, 28, 42), 8, 120)
    rect(L, 0, 600, W, H, (40, 40, 50))
    on = 0.3 if parpadeo_farola and (T * 7) % 1 < 0.25 else 1.0
    farola_v(L, 420, 820, 1.0, on=on)
    s = 2.7 + 2.0 * acercar
    circ(L, 270, 560, 200, fill=(255, 220, 160), a=0.05 * on)
    avatar(L, 270, 960 + 420 * acercar, s, DOBLE_L, cara="doble", sonrisa=sonrisa, frio=0.2, luz=0.9 * on + 0.25)


def esc_mirilla(L, e, t, D, T, st):
    ts = wt(e, "sonreía") - 0.2
    porche(L, T, t, acercar=0.0, sonrisa=0.6 + 0.4 * prog(t, ts, 0.6))
    st["ojo_pez"] = True
    st["niebla"] = 0.6
    st["cam"] = (1.0 + 0.04 * math.sin(t * 1.3), 270 + 6 * math.sin(t * 0.9), 560)
    for pal in ("ropa", "cara"):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("igual", pal, q))
    st["grado"] = "noche"


def esc_doble1(L, e, t, D, T, st):
    if t < 0.7:
        pasillo(L, T, t, luz_puerta=0.6)
        st["desenfoque"] = 8
        st["primer_plano"] = ("leo", t)
    else:
        porche(L, T, t, acercar=eio(prog(t, 0.7, D - 0.7)), sonrisa=1.1, parpadeo_farola=True)
        st["ojo_pez"] = True
        st["niebla"] = 0.5
    st["grado"] = "noche"


def foto_1979(t, guino=False):
    """Fotografía sepia de 1979: Julián y su doble. Devuelve una imagen RGB."""
    fw, fh = 300, 380
    img = Image.new("RGB", (fw * K, fh * K), (30, 30, 30))
    F_ = Capa(img)
    rect(F_, 0, 0, fw, fh, (120, 120, 120))
    rect(F_, 0, 220, fw, fh, (90, 90, 90))
    for k in range(6):
        linea(F_, [(0, 300 + k * 14), (fw, 290 + k * 16)], (110, 110, 110), w=2)
    casa_piedra(F_, 10, 220, 80, 90, False)
    casa_piedra(F_, 200, 220, 90, 100, False)
    avatar(F_, 100, 360, 1.25, JULIAN_L, cara="neutral")
    avatar(F_, 210, 360, 1.25, JULIAN_L, cara="doble", sonrisa=1.25 if guino else 1.0)
    a = np.asarray(img).astype(np.float32)
    g = a.mean(axis=2)
    sep = np.stack([g * 1.08 + 20, g * 0.9 + 8, g * 0.68], -1)
    rs = np.random.default_rng(int(t * 24) % 50)
    sep += rs.normal(0, 10, sep.shape[:2])[..., None]
    yy, xx = np.mgrid[0:sep.shape[0], 0:sep.shape[1]]
    r = np.sqrt(((xx - sep.shape[1] / 2) / sep.shape[1]) ** 2 + ((yy - sep.shape[0] / 2) / sep.shape[0]) ** 2)
    sep *= np.clip(1.25 - r * 1.2, 0.4, 1)[..., None]
    foto = Image.fromarray(np.clip(sep, 0, 255).astype(np.uint8))
    marco = Image.new("RGB", ((fw + 24) * K, (fh + 24) * K), (236, 226, 204))
    marco.paste(foto, (12 * K, 12 * K))
    return marco


def esc_foto(L, e, t, D, T, st):
    tf = wt(e, "1979") - 0.4
    pasillo(L, T, t, luz_puerta=0.6)
    golpe_bg = (t % 1.6) < 0.12
    if t < tf:
        k = eio(prog(t, 0, 1.0))
        avatar(L, lerp(560, 330, k), 980, 2.0, ABUELA_L, cara="seria", brazos=(0.1, -0.6 * k))
        avatar(L, 150, 990, 2.0, LEO_L, cara="miedo", mira=1)
        st["cam"] = (1.05, 270, 600)
    else:
        u = eio(prog(t, tf, D - tf - 0.6))
        avatar(L, 330, 980, 2.0, ABUELA_L, cara="triste", brazos=(0.1, -1.0), lagrima=t * 0.6)
        avatar(L, 150, 990, 2.0, LEO_L, cara="miedo", mira=1)
        st["foto"] = (u, t)
        st["desenfoque"] = 3
    st["shake"] = 2 if golpe_bg else 0
    st["grado"] = "noche"


def esc_abuela2(L, e, t, D, T, st):
    pasillo(L, T, t, luz_puerta=0.6)
    st["desenfoque"] = 8
    st["primer_plano"] = ("abuela_llora", t)
    st["grado"] = "noche"
    st["cam"] = (1.0 + 0.06 * eio(t / D), 270, 500)


def habitacion(L, T, t, flex=0.0, mira=0.0, gira=0.0):
    rect(L, 0, 0, W, H, (10, 12, 22))
    rect(L, 0, 300, W, 800, (30, 34, 54))
    rect(L, 40, 360, 170, 520, (20, 26, 50))
    circ(L, 100, 410, 20, fill=(210, 220, 240))
    linea(L, [(105, 360), (105, 520)], (40, 44, 66), w=4)
    poly(L, [(40, 520), (170, 520), (300, 800), (130, 800)], (150, 170, 220), a=0.05)
    rect(L, 0, 800, W, H, (22, 20, 28))
    cubo(L, 30, 720, 200, 50, (40, 70, 140), 12)
    cubo(L, 30, 690, 60, 30, (220, 220, 230), 8)
    rect(L, 30, 770, 44, 820, (60, 44, 34))
    rect(L, 216, 770, 230, 820, (60, 44, 34))
    cubo(L, 240, 760, 60, 40, (150, 120, 80), 8)
    ax, ay, aw, ah = 320, 380, 190, 420
    cubo(L, ax, ay, aw, ah, (54, 36, 26), 16)
    for k in range(2):
        dx = flex * (3 if k == 0 else -3) * math.sin(T * 80)
        rect(L, ax + 10 + k * (aw / 2 - 5) + dx, ay + 12, ax + aw / 2 - 5 + k * (aw / 2 - 5) + dx, ay + ah - 12, (64, 44, 32))
        circ(L, ax + aw / 2 - 16 + k * 32 + dx, ay + ah / 2, 6, fill=(210, 176, 90))
    rect(L, ax + aw / 2 - 2, ay + 12, ax + aw / 2 + 2, ay + ah - 12, (6, 4, 4))
    avatar(L, 150, 800, 1.3, LEO_L, cara="miedo" if gira > 0.3 else "neutral", mira=mira, brazos=(0.4, -0.4))


def esc_silencio(L, e, t, D, T, st):
    t3 = wt(e, "tres") - 0.1
    golpes = [t3 + 0.35, t3 + 0.95, t3 + 1.55]
    flex = 1.0 if any(0 <= t - tg < 0.15 for tg in golpes) else 0.0
    gira = eio(prog(t, golpes[0], 1.6))
    habitacion(L, T, t, flex=flex, mira=1.3 * gira, gira=gira)
    z = 1.02 + 0.45 * eio(prog(t, 1.2, D - 1.2))
    st["cam"] = (z, lerp(270, 400, eio(prog(t, 1.2, D))), lerp(560, 600, eio(prog(t, 1.2, D))))
    st["shake"] = 3 * flex
    st["grado"] = "noche"


def puertas_armario(L, gap):
    for k in range(2):
        x0 = 0 if k == 0 else 270 + gap / 2
        x1 = 270 - gap / 2 if k == 0 else W
        rect(L, x0, 0, x1, H, (60, 40, 28))
        for jj in range(14):
            xx = x0 + 20 + jj * 19
            if xx < x1:
                linea(L, [(xx, 0), (xx + 4, H)], (52, 34, 24), w=2)
    circ(L, 270 - gap / 2 - 24, 520, 14, fill=(210, 176, 90))
    circ(L, 270 + gap / 2 + 24, 520, 14, fill=(210, 176, 90))


def esc_armario(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (2, 2, 4))
    puertas_armario(L, 16)
    st["cam"] = (1.0 + 0.35 * eio(t / D), 270, 520)
    st["grado"] = "noche"


def esc_doble2(L, e, t, D, T, st):
    fin = e["voz_t0"] - e["t0"] + e["palabras"][-1]["t"] + e["palabras"][-1]["d"] + 0.15
    if t < fin:
        abre = eio(prog(t, fin - 1.0, 1.0))
        gap = 16 + 26 * abre
        rect(L, 0, 0, W, H, (2, 2, 4))
        q = prog(t, 0.2, 0.25)
        if q > 0:
            hy0 = 430
            rect(L, 270 - 60, hy0, 270 + 60, hy0 + 140, (70, 56, 46), a=q)
            for ex in (270 - 2, 270 + 26):
                L.d.ellipse(P(ex - 9, hy0 + 30, ex + 9, hy0 + 58), fill=L.c((2, 2, 2), q))
                circ(L, ex - 3, hy0 + 38, 3, fill=(255, 255, 255), a=q)
            ss = prog(t, 0.8, 0.8)
            if ss > 0:
                L.d.arc(P(270 - 26 * ss, hy0 + 70, 270 + 30 * ss, hy0 + 96), 15, 165, fill=L.c((10, 8, 8), ss),
                        width=int(3 * K))
        puertas_armario(L, gap)
        st["cam"] = (1.35 + 0.25 * eio(t / fin), 270, 500)
    else:
        rect(L, 0, 0, W, H, (0, 0, 0))
        st["final"] = t - fin
        st["sin_cabecera"] = True
    st["grado"] = "noche"


FUNCS = {"regla": esc_regla, "advertencia": esc_advertencia, "abuela1": esc_abuela1, "pupitre": esc_pupitre,
         "golpes": esc_golpes, "mirilla": esc_mirilla, "doble1": esc_doble1, "foto": esc_foto, "abuela2": esc_abuela2,
         "silencio": esc_silencio, "armario": esc_armario, "doble2": esc_doble2}


# ------------------------------------------------------------------ posproducción
_NIEBLA = None


def niebla(img, T, k):
    global _NIEBLA
    if _NIEBLA is None:
        rng = np.random.default_rng(3)
        n = rng.random((60, 220)).astype(np.float32)
        _NIEBLA = Image.fromarray((n * 255).astype(np.uint8)).resize((440, 120), Image.BILINEAR).filter(
            ImageFilter.GaussianBlur(6))
    off = int((T * 14) % 220)
    capa = _NIEBLA.crop((off, 0, off + 220, 120)).resize((IW, IH), Image.BILINEAR)
    capa = capa.point(lambda v: int(cl((v - 90) / 120) * 255 * k))
    gris = Image.new("RGB", (IW, IH), (150, 160, 180))
    return Image.composite(gris, img, capa)


def desenfocar(img, r):
    small = img.resize((IW // 4, IH // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r / 2))
    return small.resize((IW, IH), Image.BILINEAR)


_FISH = None


def ojo_de_pez(img):
    global _FISH
    if _FISH is None:
        yy, xx = np.mgrid[0:IH, 0:IW].astype(np.float32)
        cx, cy = IW / 2, IH * 0.52
        R = IW * 0.56
        dx, dy = (xx - cx) / R, (yy - cy) / R
        r = np.sqrt(dx * dx + dy * dy)
        f = np.where(r > 0, np.sin(np.clip(r, 0, 1.5) * 1.05) / (r + 1e-6), 1.0) * 0.92
        sx = np.clip(cx + dx * f * R, 0, IW - 1).astype(np.int32)
        sy = np.clip(cy + dy * f * R, 0, IH - 1).astype(np.int32)
        mask = np.clip((1.0 - r) * 18, 0, 1)
        _FISH = (sy, sx, mask[..., None].astype(np.float32))
    sy, sx, mask = _FISH
    a = np.asarray(img)
    return Image.fromarray((a[sy, sx].astype(np.float32) * mask).astype(np.uint8))


def grado(img, tipo):
    a = np.asarray(img).astype(np.float32)
    if tipo in ("frio", "noche"):
        a = a * np.array([0.82, 0.92, 1.12]) + np.array([0, 4, 14])
    elif tipo == "calido":
        a = a * np.array([1.08, 0.98, 0.82]) + np.array([10, 4, 0])
    elif tipo == "aula":
        g = a.mean(axis=2, keepdims=True)
        a = (a * 0.75 + g * 0.25) * np.array([0.92, 1.0, 1.04])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def primer_plano(img, tipo, t, T):
    L = Capa(img)
    if tipo == "abuela":
        avatar(L, 250, 1500, 5.2, ABUELA_L, cara="seria", brazos=(0.1, -2.3 + 0.1 * math.sin(t * 2)),
               boca=(0.5 + 0.5 * math.sin(t * 20)) if 0.2 < t < 3.5 else 0)
    elif tipo == "leo":
        avatar(L, 270, 1550, 5.6, LEO_L, cara="miedo", boca=0.6, frio=0.4)
    elif tipo == "abuela_llora":
        avatar(L, 270, 1520, 5.4, ABUELA_L, cara="triste", lagrima=t * 0.5, frio=0.3,
               boca=(0.5 + 0.5 * math.sin(t * 18)) * 0.6)
    return L.img


def post(img, st, T, e, t):
    if st.get("desenfoque"):
        img = desenfocar(img, st["desenfoque"])
    if st.get("primer_plano"):
        img = primer_plano(img, *st["primer_plano"], T)
    if st.get("foto"):
        u, tt = st["foto"]
        foto = foto_1979(tt, guino=(int(tt * 30) % 37 == 0))
        esc = lerp(0.35, 1.55, u)
        foto = foto.resize((max(1, int(foto.width * esc)), max(1, int(foto.height * esc))), Image.BILINEAR)
        rot = foto.rotate(lerp(-8, 0, u), expand=True, fillcolor=(0, 0, 0))
        cx, cy = lerp(330 * K, IW / 2, u), lerp(640 * K, IH * 0.52, u)
        m = rot.convert("L").point(lambda v: 255 if v > 3 else 0)
        img.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)), m)
    if st.get("ojo_pez"):
        img = ojo_de_pez(img)
    if st.get("niebla"):
        img = niebla(img, T, st["niebla"])
    return grado(img, st.get("grado", "noche"))


def procesar_susurro(x):
    ent = os.path.join(BUILD, "sus_cruda.wav")
    sal = os.path.join(BUILD, "sus_proc.wav")
    with wave.open(ent, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    filtro = ("highpass=f=250,lowpass=f=3800,tremolo=f=6:d=0.25,"
              "aecho=0.8:0.7:120|260|420:0.35|0.25|0.15,acompressor=threshold=-24dB:ratio=3:makeup=4")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", ent, "-af", filtro, "-ar", str(SR), "-ac", "1", sal])
    return leer(sal)[:len(x)]


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




def pop():
    n = int(0.25 * SR)
    u = np.arange(n) / SR
    return (np.sin(2 * np.pi * (500 + 900 * u * 4) * u) * np.exp(-u * 18) * 0.6).astype(np.float32)


def procesar_susurro(x):
    ent = os.path.join(BUILD, "sus_cruda.wav")
    sal = os.path.join(BUILD, "sus_proc.wav")
    with wave.open(ent, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    filtro = ("highpass=f=250,lowpass=f=3800,tremolo=f=6:d=0.25,"
              "aecho=0.8:0.7:120|260|420:0.35|0.25|0.15,acompressor=threshold=-24dB:ratio=3:makeup=4")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", ent, "-af", filtro, "-ar", str(SR), "-ac", "1", sal])
    return leer(sal)[:len(x)]


def musica(n):
    """Dron grave con disonancia y una caja de música desafinada."""
    tt = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * tt)
    for f, g in ((41.2, 0.10), (43.7, 0.06), (82.4, 0.04), (123.5, 0.02)):
        out += g * np.sin(2 * np.pi * f * tt + 0.5 * np.sin(2 * np.pi * 0.09 * tt)) * lfo
    notas = [76, 75, 72, 71, 76, 79, 78, 72]
    k = 0
    t = 2.0
    while t < TOTAL:
        f = 440 * 2 ** ((notas[k % 8] - 69 + (0.3 if k % 3 == 0 else 0)) / 12)
        m = int(1.6 * SR)
        u = np.arange(m) / SR
        colocar(out, ((np.sin(2 * np.pi * f * u) + 0.4 * np.sin(2 * np.pi * 2.76 * f * u)) * np.exp(-u * 2.5) * 0.03)
                .astype(np.float32), t)
        t += 1.9
        k += 1
    return out


def latido(v=1.0):
    m = int(0.5 * SR)
    u = np.arange(m) / SR
    s = np.zeros(m, np.float32)
    for t0, a in ((0, 1.0), (0.16, 0.7)):
        uu = np.clip(u - t0, 0, None)
        s += a * np.sin(2 * np.pi * 50 * uu) * np.exp(-uu * 16) * (u >= t0)
    return s * v


def toc():
    m = int(0.5 * SR)
    u = np.arange(m) / SR
    r = np.random.default_rng(2).standard_normal(m).astype(np.float32)
    r = np.convolve(r, np.ones(30) / 30, mode="same") * 6
    s = (np.sin(2 * np.pi * 110 * u) * 0.8 + r) * np.exp(-u * 22)
    s += 0.3 * np.sin(2 * np.pi * 90 * u) * np.exp(-u * 6)
    return (s * 0.9).astype(np.float32)




# ------------------------------------------------------------------ render del episodio
GRANO = None


def render_frame(fr):
    global GRANO
    T = fr / FPS
    e = escena_en(T)
    t = T - e["t0"]
    D = e["dur"]
    img = Image.new("RGB", (IW, IH), (0, 0, 0))
    L = Capa(img)
    st = {"overlay": []}
    FUNCS[e["nombre"]](L, e, t, D, T, st)
    z, fx, fy = st.get("cam", (1.03 + 0.04 * eio(t / D), 270, 480))
    z += golpe_zoom(T) * 0.6
    mano = st.get("mano", 0.35)
    sh = st.get("shake", 0)
    jx = (mano * 3 * math.sin(T * 1.7) + sh * math.sin(T * 61)) * K
    jy = (mano * 3 * math.cos(T * 1.3) + sh * math.cos(T * 47)) * K
    cw, ch = IW / z, IH / z
    x0 = cl(fx * K - cw / 2, 0, IW - cw) + jx
    y0 = cl(fy * K - ch / 2, 0, IH - ch) + jy
    img = L.img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    img = post(img, st, T, e, t)
    img = ImageChops.multiply(img, VINETA())
    if GRANO is None:
        GRANO = [Image.effect_noise((IW // 3, IH // 3), 30).resize((IW, IH), Image.NEAREST).convert("RGB") for _ in range(4)]
    img = Image.blend(img, ImageChops.multiply(img, GRANO[fr % 4]), 0.10)
    O = Capa(img)
    overlays(O, st, T, e, t)
    cabecera(O, st)
    subtitulos_ep(O, T)
    rect(O, 0, 0, W, 14, (0, 0, 0))
    rect(O, 0, H - 14, W, H, (0, 0, 0))
    out = O.img
    if T < 0.12:
        out = Image.blend(Image.new("RGB", (IW, IH), (0, 0, 0)), out, T / 0.12)
    return out.resize((OW, OH), Image.LANCZOS).tobytes()


COLOR_VOZ = {"abuela1": (255, 190, 90), "abuela2": (255, 190, 90), "doble1": (255, 70, 70), "doble2": (255, 70, 70)}


def subtitulos_ep(O, T):
    e = escena_en(T)
    col_voz = COLOR_VOZ.get(e["nombre"])
    for ini, fin, bloque in SUBS:
        if ini <= T < fin:
            size = 40
            f_w = [ancho(w[0], size) for w in bloque]
            esp = ancho(" ", size)
            total = sum(f_w) + esp * (len(f_w) - 1)
            lineas = [list(range(len(bloque)))]
            if total > 470:
                lineas = [list(range(len(bloque) - 1)), [len(bloque) - 1]]
            y0 = 250 - (len(lineas) - 1) * 24
            for li, idxs in enumerate(lineas):
                tw = sum(f_w[i] for i in idxs) + esp * (len(idxs) - 1)
                x = 270 - tw / 2
                for i in idxs:
                    w, t0, t1 = bloque[i]
                    if T >= t0:
                        pop_ = eob(prog(T, t0, 0.16))
                        col = col_voz or (AMAR if w.lower() in CLAVE else BLANCO)
                        texto(O, w, x + f_w[i] / 2, y0 + li * 50 + 4 * (1 - pop_), size * (0.86 + 0.14 * pop_), col,
                              fuente="black")
                    x += f_w[i] + esp
            break


def overlays(O, st, T, e, t):
    if "titulo_si" in st:
        tt = st["titulo_si"]
        q = 1 - prog(tt, 3.2, 0.5)
        if q > 0:
            s = 1 + 0.35 * math.exp(-tt * 9)
            texto(O, "SI LLAMAN A LAS", 270, 345, 34 * s, BLANCO, a=q, fuente="black")
            texto(O, "3:17", 270, 420, 96 * s, (255, 60, 60), a=q, fuente="black")
            texto(O, "NO ABRAS", 270, 490, 40 * s, BLANCO, a=q, fuente="black")
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "toc":
            _, k, q = it
            if q > 0:
                texto(O, "TOC", 330 + k * 50, 520 + k * 70, 44 * (0.7 + 0.3 * eob(q)), BLANCO, a=q, fuente="black")
        elif tipo == "igual":
            _, pal, q = it
            txt = "MISMA ROPA" if pal == "ropa" else "MISMA CARA"
            y = 780 if pal == "ropa" else 830
            texto(O, txt, 270, y, 30 * (0.8 + 0.2 * eob(q)), (255, 80, 80), a=q, fuente="black")
        elif tipo == "marco_vacio":
            _, x, y, q = it
            texto(O, "¿?", 270, 620, 60 * eob(q) + 1, (255, 80, 80), a=q, fuente="black")
    if "final" in st:
        tt = st["final"]
        q = prog(tt, 0.3, 0.5)
        texto(O, "VALDEMORA", 270, 430, 54, (220, 220, 230), a=q, fuente="black")
        texto(O, "EP. 01 · LAS 3:17", 270, 485, 22, (255, 70, 70), a=q, fuente="black")
        texto(O, "¿Qué hay dentro del armario?", 270, 590, 20, (190, 190, 200), a=prog(tt, 0.8, 0.5), fuente="semi")


def cabecera(O, st):
    if st.get("sin_cabecera"):
        return
    w = ancho(CABECERA, 13) + 26
    rect(O, 270 - w / 2, 150, 270 + w / 2, 178, (0, 0, 0), a=0.55, r=14)
    texto(O, CABECERA, 270, 164, 13, (220, 220, 230), fuente="black", sombra=False)


# ------------------------------------------------------------------ audio del episodio
TEMA = [76, 72, 75, 71, 76, 79, 78, 71]          # caja de música de Valdemora (siempre la misma)


def caja_musica(nota_, vol=0.05, desafina=0.0):
    f = 440 * 2 ** ((nota_ - 69 + desafina) / 12)
    m = int(1.8 * SR)
    u = np.arange(m) / SR
    return ((np.sin(2 * np.pi * f * u) + 0.4 * np.sin(2 * np.pi * 2.76 * f * u) + 0.15 * np.sin(2 * np.pi * 5.4 * f * u))
            * np.exp(-u * 2.6) * vol).astype(np.float32)


def campana(vol=0.5):
    m = int(4.0 * SR)
    u = np.arange(m) / SR
    s = np.zeros(m, np.float32)
    for f, a, d in ((196, 1.0, 0.7), (392, 0.5, 1.0), (466, 0.35, 1.3), (587, 0.25, 1.6), (784, 0.15, 2.2)):
        s += a * np.sin(2 * np.pi * f * u) * np.exp(-u * d)
    return (s * vol * 0.35).astype(np.float32)


def murmullo(dur):
    m = int(dur * SR)
    r = np.random.default_rng(14).standard_normal(m).astype(np.float32)
    r = np.convolve(r, np.ones(14) / 14, mode="same") - np.convolve(r, np.ones(120) / 120, mode="same")
    u = np.arange(m) / SR
    return (r * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * u)) * 1.2).astype(np.float32)


def bisagra(dur=1.0):
    m = int(dur * SR)
    u = np.arange(m) / SR
    f = 600 + 400 * np.sin(2 * np.pi * 0.8 * u)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (np.sin(2 * np.pi * 25 * u) > 0) * 0.08
    return np.convolve(s, np.ones(10) / 10, mode="same").astype(np.float32)


def papel_s(dur=0.8):
    m = int(dur * SR)
    r = np.random.default_rng(21).standard_normal(m).astype(np.float32)
    env = (np.abs(np.sin(np.arange(m) / SR * 2 * np.pi * 6)) ** 3)
    return (np.diff(r, prepend=0) * env * 0.15).astype(np.float32)


def golpe_sordo():
    x = toc()
    return (np.convolve(x, np.ones(60) / 60, mode="same") * 2.2).astype(np.float32)


def musica(n):
    tt = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.06 * tt)
    for f, g in ((36.7, 0.08), (55.0, 0.05), (77.8, 0.02)):
        out += (g * np.sin(2 * np.pi * f * tt + 0.4 * np.sin(2 * np.pi * 0.08 * tt)) * lfo).astype(np.float32)
    return out


def mezclar():
    n = int((TOTAL + 0.3) * SR)
    voz = np.zeros(n, np.float32)
    dob = np.zeros(n, np.float32)
    for e in ESC:
        clip = leer(os.path.join(BUILD, f"voz_{e['i']}.mp3"))
        colocar(dob if e["nombre"].startswith("doble") else voz, clip, e["voz_t0"])
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    voz = procesar_voz(voz)
    voz = np.pad(voz, (0, max(0, n - len(voz))))[:n]
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    dob = procesar_susurro(dob * 0.9 / (np.abs(dob).max() + 1e-6))
    dob = np.pad(dob, (0, max(0, n - len(dob))))[:n]
    dob *= 0.85 / (np.abs(dob).max() + 1e-6)
    voz = voz + dob
    tt = np.arange(n) / SR
    mus = musica(n)
    fx = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    r = np.random.default_rng(1).standard_normal(n).astype(np.float32)
    fx += (np.convolve(r, np.ones(40) / 40, mode="same") * 0.28 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * tt))).astype(np.float32)
    rg = E["regla"]
    colocar(fx, braam(), 0.0, 0.6)
    for k in range(3):
        colocar(fx, campana(0.7), 0.1 + k * 1.6, 0.6)
    ta = rg["t0"] + wt(rg, "abras") - 0.1
    for k in range(8):
        colocar(fx, ping() * 0.3, ta + k * 0.09, 0.3)
    t = 1.0
    k = 0
    fin_tema = E["silencio"]["t0"]
    while t < fin_tema:
        if not (E["pupitre"]["t0"] <= t < E["golpes"]["t0"] + 1.6):
            colocar(mus, caja_musica(TEMA[k % 8], 0.045, 0.35 if k % 5 == 3 else 0), t)
        t += 0.95
        k += 1
    ad = E["advertencia"]
    t = ad["t0"]
    while t < E["pupitre"]["t0"]:
        colocar(fx, (np.sin(2 * np.pi * 1800 * np.arange(1200) / SR) * np.exp(-np.arange(1200) / SR * 150) * 0.12)
                .astype(np.float32), t)
        t += 0.98
    pu = E["pupitre"]
    tn = pu["t0"] + wt(pu, "nadie") - 0.2
    colocar(fx, murmullo(tn - pu["t0"]) * 0.5, pu["t0"], 0.5)
    colocar(fx, (np.sin(2 * np.pi * 6000 * np.arange(int(2.5 * SR)) / SR) * 0.012).astype(np.float32), tn, 1.0)
    go = E["golpes"]
    colocar(fx, ping(), go["t0"] + 0.9, 0.5)
    tl = go["t0"] + wt(go, "llamó") + 0.2
    for d in (0, 0.75, 1.5):
        colocar(fx, toc(), tl + d, 1.0)
    t = tl + 2.0
    p = 0.9
    while t < E["foto"]["t0"] + 4:
        colocar(fx, latido(0.7), t, 0.42)
        t += p
        p = max(0.55, p * 0.97)
    mi = E["mirilla"]
    colocar(fx, (np.sin(2 * np.pi * 100 * np.arange(int((E["foto"]["t0"] - mi["t0"]) * SR)) / SR) * 0.03).astype(np.float32),
            mi["t0"], 1.0)
    colocar(fx, braam(), mi["t0"] + wt(mi, "sonreía") - 0.2, 0.7)
    fo = E["foto"]
    colocar(fx, papel_s(), fo["t0"] + wt(fo, "1979") - 0.5, 0.6)
    t = fo["t0"]
    while t < E["silencio"]["t0"] - 0.3:
        colocar(fx, toc() * 0.4, t + 0.5, 0.5)
        t += 1.6
    si = E["silencio"]
    a0, a1 = int(si["t0"] * SR), int((si["t0"] + 1.2) * SR)
    fx[a0:a1] *= 0.02
    mus[a0:a1] *= 0.0
    t3 = si["t0"] + wt(si, "tres") - 0.1
    for d in (0.35, 0.95, 1.55):
        colocar(fx, golpe_sordo(), t3 + d, 1.0)
    colocar(fx, braam(), si["t0"] + wt(si, "puerta") - 0.2, 0.8)
    d2 = E["doble2"]
    fin = d2["voz_t0"] + d2["palabras"][-1]["t"] + d2["palabras"][-1]["d"] + 0.15
    colocar(fx, bisagra(1.0), fin - 1.0, 0.6)
    b0 = int(fin * SR)
    fx[b0:] *= 0.0
    mus[b0:] *= 0.0
    colocar(mus, caja_musica(TEMA[0], 0.06, 0.4), fin + 0.5)
    for k, e in enumerate(ESC[1:]):
        if e["nombre"] not in ("doble1", "abuela1", "abuela2", "doble2", "silencio"):
            colocar(fx, whoosh(k, 0.4), e["t0"] - 0.2, 0.25)
    envv = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.55 * np.clip(envv * 12, 0, 1)
    total = voz + (mus + fx) * duck
    total *= np.clip((TOTAL - tt) / 0.4, 0, 1)
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
