"""TikTok vertical «¿Por qué te pierdes en IKEA?»: los trucos de diseño de la tienda contados como un «plan»
(formato historia con giro), con personajes planos, plano cenital del laberinto y subtítulos palabra a palabra.

    python3 voz.py && python3 video.py        -> ikea_tiktok.mp4
    python3 video.py --preview 1 5.5 12       -> build/prev_*.png"""
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
SALIDA = os.path.join(AQUI, "ikea_tiktok.mp4")

W, H = 540, 960            # unidades de diseño (9:16)
K = 3                      # resolución interna = 1620x2880
IW, IH = W * K, H * K
OW, OH = 1080, 1920
FPS = 30
SR = 44100
VOZ_OFF = 0.12
COLA = 0.12

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


EXTRA = {"gancho": 0.25, "bolsa": 0.2, "camino": 0.3, "dato": 0.4, "montaje": 0.3, "final": 1.5}
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
CLAVE = {"ikea", "culpa", "propósito", "pierdas", "bolsa", "amarilla", "enorme", "lámpara", "grande", "único", "flechas",
         "atajos", "nadie", "casa", "viviendo", "cansado", "restaurante", "sigues", "baratas", "velas", "perchas", "planta",
         "60 %", "lista", "montas", "valoras", "efecto", "media", "tienda", "contento", "sígueme", "peores"}


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
            for seq, num in ((["dos", "mil"], "2.000"), (["sesenta", "por", "ciento"], "60 %")):
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


# --- Escenas del TikTok «Por qué te pierdes en IKEA» (se insertan en video.py al montarlo) ---

POSES.update({
    "camina1": dict(rodilla=(26, 92), pie=(36, 188), cuello=(6, -150), cabeza=(12, -196), codo=(-16, -76), mano=(-26, -14),
                    codo2=(18, -76), mano2=(32, -16)),
    "camina2": dict(rodilla=(-12, 94), pie=(-30, 188), cuello=(6, -150), cabeza=(12, -196), codo=(18, -76), mano=(32, -16),
                    codo2=(-16, -76), mano2=(-26, -14)),
    "empuja": dict(rodilla=(26, 92), pie=(36, 188), cuello=(14, -148), cabeza=(24, -192), codo=(50, -92), mano=(92, -84),
                   codo2=(46, -88), mano2=(88, -80)),
    "empuja2": dict(rodilla=(-10, 94), pie=(-26, 188), cuello=(14, -148), cabeza=(24, -192), codo=(50, -92), mano=(92, -84),
                    codo2=(46, -88), mano2=(88, -80)),
    "trabaja1": dict(rodilla=(4, 95), pie=(2, 190), cuello=(4, -150), cabeza=(10, -194), codo=(44, -112), mano=(92, -112),
                     codo2=(30, -80), mano2=(70, -60)),
    "trabaja2": dict(rodilla=(4, 95), pie=(2, 190), cuello=(4, -150), cabeza=(10, -194), codo=(46, -100), mano=(94, -88),
                     codo2=(30, -80), mano2=(70, -60)),
    "piensa": dict(rodilla=(4, 95), pie=(2, 190), cuello=(0, -150), cabeza=(4, -196), codo=(30, -118), mano=(20, -166),
                   codo2=(-8, -74), mano2=(-4, -10)),
    "lleva": dict(rodilla=(4, 95), pie=(2, 190), cuello=(0, -150), cabeza=(4, -196), codo=(22, -80), mano=(40, -40),
                  codo2=(-8, -74), mano2=(-4, -10)),
})

PROTA = ((235, 128, 70), (205, 104, 52), (62, 86, 150), (48, 68, 122))     # jersey naranja y vaqueros
AZUL_T = (24, 82, 168)        # azul «de tienda de muebles» (sin logotipo)
AZUL_T2 = (18, 62, 132)
AMAR_B = (255, 206, 0)        # amarillo de la bolsa
AMAR_B2 = (222, 172, 0)
PARED = (240, 236, 226)
SUELO_C = (226, 196, 148)
SUELO_L = (206, 174, 124)
CABECERA = "TRUCOS DE LAS TIENDAS · 1"
PISO = 700


def camina(t, vel=8, a="camina1", b="camina2"):
    return pose_mix(a, b, 0.5 + 0.5 * math.sin(t * vel))


def prota(L, x, y, t, s=0.9, pose=None, ojos=1.0, boca=0.0, flip=False):
    return persona(L, x, y - 190 * s, pose or camina(t), s, ropa=PROTA, pelo=(60, 36, 24), ojos=ojos, boca=boca, flip=flip)


def interior(L, T, pared=PARED, franja=True, flechas=True):
    rect(L, 0, 0, W, PISO, pared)
    if franja:
        rect(L, 0, 300, W, 318, AZUL_T)
        rect(L, 0, 318, W, 324, AMAR_B)
    rect(L, 0, PISO, W, H, SUELO_C)
    for k in range(9):
        y = PISO + 12 + k * k * 4.2
        linea(L, [(0, y), (W, y)], SUELO_L, w=1.4)
    rect(L, 0, PISO - 8, W, PISO, (200, 196, 186))
    if flechas:
        off = (T * 50) % 90
        for k in range(-1, 7):
            x = k * 90 + off
            flecha_suelo(L, x, 900, 26, (255, 255, 255), a=0.7)


def flecha_suelo(L, x, y, s, col, a=1.0, dx=1.0, dy=0.0):
    px, py = -dy, dx
    tip = (x + dx * s, y + dy * s)
    i1 = (x - dx * s * 0.6 + px * s * 0.8, y - dy * s * 0.6 + py * s * 0.8)
    i2 = (x - dx * s * 0.6 - px * s * 0.8, y - dy * s * 0.6 - py * s * 0.8)
    linea(L, [i1, tip, i2], col, w=max(2, s * 0.28), a=a)


def bolsa(L, x, y, w=150, h=130, a=1.0):
    """Bolsa amarilla grande; (x, y) = centro del borde superior."""
    for dx in (-w * 0.28, w * 0.28):
        L.d.arc(P(x + dx - 26, y - 70, x + dx + 26, y + 10), 180, 360, fill=L.c(AMAR_B2, a), width=int(9 * K))
    poly(L, [(x - w / 2, y), (x + w / 2, y), (x + w / 2 - 8, y + h), (x - w / 2 + 8, y + h)], AMAR_B, a)
    rect(L, x - w / 2, y, x + w / 2, y + 12, AMAR_B2, a=a)
    linea(L, [(x - w / 2 + 14, y + h * 0.35), (x + w / 2 - 14, y + h * 0.35)], AMAR_B2, w=3, a=a)


def lampara(L, x, y, s=1.0, a=1.0, encendida=False):
    """Lámpara de pie pequeña; (x, y) = base."""
    if encendida:
        circ(L, x, y - 120 * s, 50 * s, fill=(255, 240, 180), a=a * 0.35)
    rect(L, x - 22 * s, y - 6 * s, x + 22 * s, y, (60, 60, 66), a=a, r=3)
    rect(L, x - 3 * s, y - 110 * s, x + 3 * s, y - 6 * s, (70, 70, 76), a=a)
    poly(L, [(x - 20 * s, y - 108 * s), (x + 20 * s, y - 108 * s), (x + 34 * s, y - 70 * s), (x - 34 * s, y - 70 * s)],
         (250, 236, 200) if encendida else (236, 226, 204), a)


def planta(L, x, y, s=1.0, a=1.0):
    poly(L, [(x - 22 * s, y - 40 * s), (x + 22 * s, y - 40 * s), (x + 16 * s, y), (x - 16 * s, y)], (196, 110, 70), a)
    for ang, l in ((-60, 60), (-90, 72), (-120, 60), (-40, 46), (-140, 46)):
        r = math.radians(ang)
        cx, cy = x + math.cos(r) * l * 0.55 * s, y - 40 * s + math.sin(r) * l * 0.55 * s
        L.d.ellipse(P(cx - 14 * s, cy - 24 * s, cx + 14 * s, cy + 24 * s), fill=L.c((70, 150, 80), a))


def sofa(L, x, y, w=260, col=(110, 132, 170), col2=(88, 106, 140), a=1.0):
    """Sofá; (x, y) = centro de la base."""
    rect(L, x - w / 2, y - 150, x + w / 2, y - 60, col2, a=a, r=16)
    rect(L, x - w / 2 + 10, y - 80, x + w / 2 - 10, y - 30, col, a=a, r=10)
    for k in range(2):
        cx = x - w / 4 + k * w / 2
        rect(L, cx - w / 4 + 16, y - 140, cx + w / 4 - 16, y - 82, col, a=a, r=12)
    rect(L, x - w / 2 - 14, y - 110, x - w / 2 + 22, y - 30, col2, a=a, r=12)
    rect(L, x + w / 2 - 22, y - 110, x + w / 2 + 14, y - 30, col2, a=a, r=12)
    rect(L, x - w / 2 + 4, y - 30, x - w / 2 + 14, y, (60, 50, 40), a=a)
    rect(L, x + w / 2 - 14, y - 30, x + w / 2 - 4, y, (60, 50, 40), a=a)


def etiqueta(L, x, y, txt, a=1.0, ang=0.0):
    linea(L, [(x, y - 30), (x + 6 * math.sin(ang), y)], (90, 90, 90), w=1.5, a=a)
    rect(L, x - 34, y, x + 34, y + 30, AMAR_B, a=a, r=4)
    texto(L, txt, x, y + 15, 15, (20, 20, 20), a=a, fuente="black", sombra=False)


def nube(O, x, y, w, h, q, col=BLANCO, cola=(-1, 1)):
    """Bocadillo de pensamiento."""
    if q <= 0:
        return
    s = eob(q)
    w, h = w * s, h * s
    rect(O, x - w / 2, y - h / 2, x + w / 2, y + h / 2, col, a=q, r=min(w, h) * 0.45)
    for k, r in enumerate((14, 9, 6)):
        circ(O, x + cola[0] * (w * 0.25 + k * 22), y + h / 2 + 14 + k * 20, r * s, fill=col, a=q)


# ------------------------------------------------------------------ plano de la tienda (vista cenital)
FILAS = [390, 480, 570, 660, 750, 840]
X0, X1 = 46, 494
SECCIONES = ["SALONES", "COCINAS", "DORMITORIOS", "RESTAURANTE", "COSAS PEQUEÑAS", "ALMACÉN"]
RUTA = [(64, 390)]
for _k, _y in enumerate(FILAS):
    if _k % 2 == 0:
        RUTA += [(456, _y)] + ([(456, FILAS[_k + 1])] if _k + 1 < len(FILAS) else [])
    else:
        RUTA += [(84, _y)] + ([(84, FILAS[_k + 1])] if _k + 1 < len(FILAS) else [])
RUTA += [(30, FILAS[-1])]
_LONG = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(RUTA, RUTA[1:])]
LRUTA = sum(_LONG)
ATAJOS = [(1, 250), (3, 300), (2, 170)]         # (muro, x) huecos que nadie ve


def punto_ruta(d):
    d = cl(d, 0, LRUTA - 0.01)
    for (a, b), l in zip(zip(RUTA, RUTA[1:]), _LONG):
        if d <= l:
            k = d / l
            return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, (b[0] - a[0]) / l, (b[1] - a[1]) / l
        d -= l
    a, b = RUTA[-2], RUTA[-1]
    return b[0], b[1], 1, 0


def plano(L, T, t, avance=None, perdido=0.0, flechas=1.0, atajos=0.0, invisibles=0.0, etiquetas=1.0, rastro=True,
          resalta=-1):
    rect(L, 0, 0, W, H, (26, 30, 44))
    for gx in range(0, W, 30):
        linea(L, [(gx, 0), (gx, H)], (34, 40, 58), w=1)
    for gy in range(0, H, 30):
        linea(L, [(0, gy), (W, gy)], (34, 40, 58), w=1)
    rect(L, X0 - 10, FILAS[0] - 52, X1 + 10, FILAS[-1] + 52, (70, 74, 90), r=10)
    rect(L, X0, FILAS[0] - 42, X1, FILAS[-1] + 42, (238, 232, 216), r=6)
    tintes = [(250, 226, 200), (226, 238, 214), (220, 228, 246), (248, 222, 222), (242, 236, 206), (224, 224, 230)]
    for k, y in enumerate(FILAS):
        rect(L, X0, y - 42, X1, y + 42, tintes[k], a=0.7)
        if etiquetas > 0:
            hl = k == resalta
            texto(L, SECCIONES[k], 270, y - 24, 13 if not hl else 15, (90, 80, 70) if not hl else (200, 40, 40),
                  a=etiquetas * (0.75 if not hl else 1.0), fuente="black", sombra=False)
    for k in range(len(FILAS) - 1):
        y = (FILAS[k] + FILAS[k + 1]) / 2
        xa, xb = (X0, 420) if k % 2 == 0 else (120, X1)
        segs = [(xa, xb)]
        for (m, gx) in ATAJOS:
            if m == k:
                nuevos = []
                for (p, q) in segs:
                    if p < gx < q:
                        nuevos += [(p, gx - 18), (gx + 18, q)]
                    else:
                        nuevos.append((p, q))
                segs = nuevos
        for (p, q) in segs:
            rect(L, p, y - 5, q, y + 5, (96, 98, 112), r=3)
        for (m, gx) in ATAJOS:
            if m == k:
                # el hueco se disimula con un panel del mismo color… salvo cuando se revela
                rect(L, gx - 18, y - 5, gx + 18, y + 5, (110, 112, 124), a=1 - atajos * (1 - invisibles * 0.85))
                if atajos > 0:
                    pul = 0.6 + 0.4 * math.sin(T * 10)
                    for j in range(4):
                        rect(L, gx - 18 + j * 10, y - 3, gx - 12 + j * 10, y + 3, VERDE,
                             a=atajos * pul * (1 - invisibles * 0.8))
                    texto(L, "ATAJO", gx, y + 16, 12, (30, 140, 70), a=atajos * (1 - invisibles * 0.8), fuente="black",
                          sombra=False)
    # entrada y salida
    rect(L, 30, FILAS[0] - 20, 56, FILAS[0] + 20, (40, 160, 90), r=4)
    texto(L, "ENTRADA", 120, FILAS[0] - 2, 11, (30, 120, 70), fuente="black", sombra=False, a=0.0 if etiquetas else 0)
    rect(L, 18, FILAS[-1] - 20, 50, FILAS[-1] + 20, (40, 160, 90), r=4)
    texto(L, "SALIDA", 34, FILAS[-1] + 34, 12, (40, 160, 90), fuente="black", sombra=False)
    texto(L, "ENTRADA", 44, FILAS[0] - 32, 12, (40, 160, 90), fuente="black", sombra=False)
    if flechas > 0:
        off = (T * 45) % 40
        d = off
        while d < LRUTA:
            x, y, dx, dy = punto_ruta(d)
            flecha_suelo(L, x, y + 16, 7, (230, 170, 30), a=flechas * 0.9, dx=dx, dy=dy)
            d += 40
    if avance is not None:
        d = avance * LRUTA
        if perdido > 0:
            d += perdido * 70 * math.sin(T * 3.1) + perdido * 30 * math.sin(T * 7.3)
        d = cl(d, 0, LRUTA)
        if rastro:
            k = 0.0
            while k < d:
                x, y, _, _ = punto_ruta(k)
                circ(L, x, y, 2.2, fill=(235, 128, 70), a=0.55)
                k += 9
        x, y, _, _ = punto_ruta(d)
        pul = 1 + 0.15 * math.sin(T * 9)
        circ(L, x, y, 16 * pul, fill=(235, 128, 70), a=0.3)
        circ(L, x, y, 11, fill=(235, 128, 70), outline=BLANCO, w=3)
        return x, y
    return None


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    x, y = plano(L, T, t, avance=0.22, perdido=1.0, flechas=0.6, etiquetas=0.8)
    for k in range(3):
        u = (t * 0.9 + k / 3) % 1
        texto(L, "?", x - 26 + k * 26, y - 30 - 34 * u, 22 + 6 * k, ROJO, a=math.sin(u * math.pi), fuente="black")
    st["cam"] = (1.45 - 0.3 * eio(t / D), x * 0.4 + 270 * 0.6, 300)
    st["overlay"].append(("titular", t, prog(t, wt(e, "hecho") - 0.2, 0.3)))
    st["sin_cabecera"] = True


def esc_bolsa(L, e, t, D, T, st):
    interior(L, T)
    texto(L, "ENTRADA", 120, 360, 22, AZUL_T, fuente="black", sombra=False)
    rect(L, 40, 380, 200, 700, (210, 224, 236), r=4)
    rect(L, 116, 380, 124, 700, (170, 186, 200))
    q = eo3(prog(t, wt(e, "bolsa") - 0.4, 0.45))
    grande = prog(t, wt(e, "grande") - 0.6, 0.6)
    x = 300
    info = prota(L, x, 860, t, pose="lleva" if q > 0.6 else "de_pie", ojos=1.0 + 0.8 * grande)
    mx, my = info["mano"]
    esc = 1 + 0.45 * eob(grande)
    bx = lerp(620, mx + 30, q)
    by = lerp(my - 60, my - 10, q)
    bolsa(L, bx, by, 150 * esc, 135 * esc)
    if q > 0:
        texto(L, "BOLSA ENORME", bx, by + 70 * esc, 16 * esc, AZUL_T2, a=q, fuente="black", sombra=False)
    ql = prog(t, wt(e, "lámpara") - 0.3, 0.35)
    if ql > 0:
        nube(L, 170, 450, 130, 120, ql)
        lampara(L, 170, 494, 0.62, a=ql)
        texto(L, "1 lámpara", 170, 410, 14, (40, 40, 40), a=ql, fuente="black", sombra=False)
    if grande > 0:
        texto(L, "?", 380, 470 - 10 * math.sin(t * 6), 60 * eob(grande) + 1, ROJO, a=grande, fuente="black")
    st["paso"] = (1, "LA BOLSA")
    st["sin_cabecera"] = True


def esc_camino(L, e, t, D, T, st):
    u = eio(prog(t, 0.2, D - 0.6))
    ta = prog(t, wt(e, "atajos") - 0.3, 0.3)
    ti = prog(t, wt(e, "nadie") - 0.1, 0.5)
    fila = min(5, int(u * LRUTA / (LRUTA / 6)))
    x, y = plano(L, T, t, avance=u * 0.98, flechas=1.0, atajos=ta, invisibles=ti, resalta=fila)
    st["cam"] = (1.12, 270, 600)
    qf = prog(t, wt(e, "flechas") - 0.2, 0.3)
    if qf > 0:
        st["overlay"].append(("sello", "UN SOLO CAMINO", qf * (1 - ta), 360, AMARILLO))
    if ti > 0:
        st["overlay"].append(("sello", "CASI NADIE LOS VE", ti, 360, VERDE))
    st["paso"] = (2, "EL CAMINO")
    st["sin_cabecera"] = True


def esc_salones(L, e, t, D, T, st):
    interior(L, T, pared=(232, 226, 240), franja=False)
    # cuadro, alfombra, sofá, lámpara, planta
    rect(L, 210, 380, 370, 480, (90, 70, 50), r=4)
    rect(L, 220, 390, 360, 470, (170, 210, 230))
    poly(L, [(220, 470), (270, 420), (310, 450), (360, 400), (360, 470)], (110, 160, 110))
    L.d.ellipse(P(150, 740, 470, 800), fill=L.c((200, 90, 90)))
    sofa(L, 310, 730, 260)
    lampara(L, 470, 732, 1.6, encendida=True)
    planta(L, 140, 732, 1.2)
    etiqueta(L, 310, 600, "199 €", ang=math.sin(T * 2))
    ph = prog(t, wt(e, "casa") - 0.3, 0.4)
    pv = prog(t, wt(e, "imaginas") - 0.3, 0.4)
    prota(L, 80, 880, t, s=0.85, pose="piensa" if ph > 0 else "de_pie", ojos=1.0, boca=0.3 * pv)
    if ph > 0:
        nube(L, 150, 400, 130, 110, ph)
        poly(L, [(150, 360), (190, 392), (110, 392)], AZUL_T, a=ph)
        rect(L, 120, 392, 180, 436, AZUL_T, a=ph)
        rect(L, 142, 410, 158, 436, AMAR_B, a=ph)
    if pv > 0:
        corazon(L, 210, 360 - 6 * math.sin(t * 5), 22 * eob(pv), (254, 44, 85), a=pv)
        st["overlay"].append(("sello", "TU FUTURA CASA", pv, 560, AMARILLO))
    st["paso"] = (3, "LOS SALONES")
    st["sin_cabecera"] = True


def esc_restaurante(L, e, t, D, T, st):
    interior(L, T, pared=(246, 232, 214), flechas=False)
    texto(L, "RESTAURANTE", 270, 360, 26, AZUL_T, fuente="black", sombra=False)
    sigue = prog(t, wt(e, "sigues") - 0.3, 0.4)
    if sigue <= 0:
        silla(L, 150, 690)
        persona(L, 150, 690, "sentado_come" if (t % 1.0) < 0.5 else "sentado", 1.0, ropa=PROTA, pelo=(60, 36, 24))
    else:
        prota(L, lerp(170, 420, eio(sigue)), 880, t, s=0.9)
    rect(L, 220, 640, 460, 656, (150, 100, 60))
    rect(L, 330, 656, 346, 790, (120, 80, 48))
    L.d.ellipse(P(250, 618, 350, 646), fill=L.c(BLANCO))
    comido = prog(t, wt(e, "Comes") - 0.2, 1.2)
    for k in range(5):
        if k / 5 >= comido:
            circ(L, 278 + (k % 3) * 18, 626 + (k // 3) * 8, 8, fill=(140, 80, 44))
    st["overlay"].append(("energia", eo3(prog(t, wt(e, "recuperas") - 0.3, 1.0)), prog(t, 0.2, 0.3)))
    if sigue > 0:
        st["overlay"].append(("sello", "…Y SIGUES COMPRANDO", sigue, 560, AMARILLO))
    st["paso"] = (4, "EL RESTAURANTE")
    st["sin_cabecera"] = True


OBJETOS = ["vela", "percha", "planta", "vela", "cojin", "taza", "vela", "marco", "percha", "taza"]


def objeto(L, tipo, x, y, s=1.0, a=1.0):
    if tipo == "vela":
        rect(L, x - 12 * s, y - 10 * s, x + 12 * s, y + 10 * s, BLANCO, a=a, r=3)
        poly(L, [(x - 4 * s, y - 10 * s), (x + 4 * s, y - 10 * s), (x, y - 24 * s)], (255, 170, 40), a)
    elif tipo == "percha":
        linea(L, [(x - 26 * s, y + 10 * s), (x, y - 6 * s), (x + 26 * s, y + 10 * s), (x - 26 * s, y + 10 * s)],
              (120, 80, 50), w=4 * s, a=a)
        L.d.arc(P(x - 6 * s, y - 20 * s, x + 6 * s, y - 6 * s), 180, 90, fill=L.c((90, 90, 90), a), width=int(2 * K * s))
    elif tipo == "planta":
        planta(L, x, y + 16 * s, 0.6 * s, a=a)
    elif tipo == "cojin":
        rect(L, x - 22 * s, y - 18 * s, x + 22 * s, y + 18 * s, (220, 90, 90), a=a, r=8 * s)
    elif tipo == "taza":
        rect(L, x - 14 * s, y - 14 * s, x + 12 * s, y + 14 * s, (90, 150, 200), a=a, r=4)
        L.d.arc(P(x + 6 * s, y - 8 * s, x + 22 * s, y + 8 * s), 270, 90, fill=L.c((90, 150, 200), a), width=int(4 * K * s))
    else:
        rect(L, x - 20 * s, y - 24 * s, x + 20 * s, y + 24 * s, (60, 50, 40), a=a, r=2)
        rect(L, x - 14 * s, y - 18 * s, x + 14 * s, y + 18 * s, (240, 230, 200), a=a)


def tiempos_mercado(e):
    base = [wt(e, "velas"), wt(e, "perchas"), wt(e, "planta")]
    t_tot = wt(e, "Total")
    extra = [t_tot + 0.25 * k for k in range(len(OBJETOS) - 3)]
    return base + extra


def esc_mercado(L, e, t, D, T, st):
    interior(L, T, pared=(236, 240, 232), franja=True)
    rect(L, 20, 520, 520, 536, (150, 110, 70))
    cajones = {"vela": 90, "percha": 210, "planta": 330, "cojin": 450, "taza": 450, "marco": 330}
    for tipo, cx in (("vela", 90), ("percha", 210), ("planta", 330), ("cojin", 450)):
        rect(L, cx - 54, 430, cx + 54, 520, (200, 160, 110), r=6)
        for j in range(3):
            objeto(L, tipo, cx - 30 + j * 30, 420 - (j % 2) * 8, 0.8)
        etiqueta(L, cx, 540, "1 €" if tipo != "planta" else "3 €")
    rect(L, 0, 600, W, PISO, PARED)
    bx, by = 270, 730
    tiempos = tiempos_mercado(e)
    dentro = 0
    for k, (tipo, t0) in enumerate(zip(OBJETOS, tiempos)):
        u = prog(t, t0 - 0.35, 0.45)
        if u <= 0:
            continue
        x0 = cajones[tipo]
        x = lerp(x0, bx - 30 + (k % 4) * 20, u)
        y = lerp(430, by + 16 - k * 3, u) - 140 * math.sin(u * math.pi)
        if u < 1:
            objeto(L, tipo, x, y, 0.9)
        else:
            dentro += 1
    for k in range(dentro):
        objeto(L, OBJETOS[k], bx - 45 + (k % 4) * 30, by - 4 - (k // 4) * 22, 0.85)
    bolsa(L, bx, by + 10, 190, 150)
    precios = [1.0, 1.0, 3.0, 1.0, 4.99, 2.5, 1.0, 5.99, 1.0, 2.5]
    total = sum(p for p, t0 in zip(precios, tiempos) if t >= t0)
    st["overlay"].append(("ticket", total, prog(t, tiempos[0] - 0.4, 0.3)))
    st["paso"] = (5, "LAS COSAS PEQUEÑAS")
    st["sin_cabecera"] = True


def esc_dato(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, AZUL_T2)
    for k in range(12):
        circ(L, (k * 97) % W, (k * 211) % H, 80, fill=AZUL_T, a=0.35)
    q = eo3(prog(t, wt(e, "sesenta") - 0.4, 1.0))
    cx, cy, r = 270, 560, 150
    circ(L, cx, cy, r, fill=(60, 90, 150))
    if q > 0:
        L.d.pieslice(P(cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * 0.6 * q, fill=L.c(AMAR_B))
    circ(L, cx, cy, r * 0.62, fill=AZUL_T2)
    st["overlay"].append(("dato", q, prog(t, wt(e, "lista") - 0.3, 0.4), prog(t, wt(e, "profesor") - 0.2, 0.4)))
    st["cam"] = (1.04 + 0.05 * eio(t / D), 270, 560)


def esc_montaje(L, e, t, D, T, st):
    interior(L, T, pared=(222, 236, 228), franja=False, flechas=False)
    q = prog(t, 0.2, 2.6)
    piezas = [  # (x0,y0,x1,y1) destino
        (300, 420, 316, 800), (444, 420, 460, 800),
        (316, 420, 444, 434), (316, 540, 444, 554), (316, 660, 444, 674), (316, 786, 444, 800),
    ]
    for k, (a, b, c, d) in enumerate(piezas):
        u = eo3(cl(q * 6 - k))
        off_x = (1 - u) * (60 + 40 * k) * (1 if k % 2 else -1)
        off_y = (1 - u) * (300 - 30 * k)
        rect(L, a + off_x, b + off_y, c + off_x, d + off_y, (232, 210, 170), outline=(180, 150, 110), w=2)
    if q >= 1:
        objeto(L, "planta", 350, 525, 0.9)
        objeto(L, "taza", 410, 520, 0.9)
        objeto(L, "marco", 360, 640, 0.9)
        objeto(L, "vela", 410, 650, 1.0)
    trabaja = q < 1
    info = prota(L, 170, 880, t, s=0.9, pose=camina(t, 10, "trabaja1", "trabaja2") if trabaja else "de_pie",
                 boca=0.4 * prog(t, wt(e, "valoras") - 0.3, 0.4))
    mx, my = info["mano"]
    if trabaja:
        linea(L, [(mx, my), (mx + 26, my - 4), (mx + 26, my - 18)], (110, 110, 120), w=4)
        if (t * 6) % 1 < 0.3:
            circ(L, mx + 40, my - 10, 4, fill=AMAR_B)
    qv = prog(t, wt(e, "valoras") - 0.3, 0.4)
    if qv > 0:
        corazon(L, 380, 380 - 8 * math.sin(t * 5), 40 * eob(qv), (254, 44, 85), a=qv)
    qe = prog(t, wt(e, "efecto") - 0.3, 0.35)
    if qe > 0:
        st["overlay"].append(("sello", "EFECTO IKEA", qe, 560, AMARILLO))
        st["overlay"].append(("fuente", qe, "Norton, Mochon y Ariely (2011)"))
    st["paso"] = (6, "EL MONTAJE")
    st["sin_cabecera"] = True


def carro(L, x, y, n, a=1.0):
    """Carro con la compra apilada; (x, y) = suelo bajo el centro."""
    rect(L, x - 80, y - 60, x + 80, y - 50, (90, 90, 100), a=a)
    for wx in (x - 60, x + 60):
        circ(L, wx, y - 14, 14, fill=(40, 40, 46), a=a)
    linea(L, [(x - 80, y - 56), (x - 96, y - 150)], (90, 90, 100), w=5, a=a)
    alturas = [(150, 40, (200, 170, 120)), (130, 34, (214, 184, 134)), (110, 30, (200, 170, 120)), (90, 26, (190, 160, 110))]
    top = y - 60
    for k in range(min(n, len(alturas))):
        w_, h_, col = alturas[k]
        rect(L, x - w_ / 2, top - h_, x + w_ / 2, top, col, a=a, outline=(150, 120, 80), w=2)
        top -= h_
    if n > 4:
        planta(L, x - 30, top, 0.8, a=a)
    if n > 5:
        lampara(L, x + 30, top, 0.6, a=a)
    if n > 6:
        bolsa(L, x + 90, y - 140, 80, 70, a=a)


def esc_final(L, e, t, D, T, st):
    bucle = t > D - 1.1
    if bucle:
        plano(L, T, t, avance=0.0, flechas=0.6, etiquetas=0.8)
        st["cam"] = (1.45, 270 * 0.6 + 64 * 0.4, 300)
        st["sin_cabecera"] = True
        return
    rect(L, 0, 0, W, 640, (190, 220, 245))
    rect(L, 0, 380, W, 640, AZUL_T)
    rect(L, 0, 370, W, 384, AMAR_B)
    rect(L, 40, 470, 200, 640, (170, 196, 220))
    texto(L, "SALIDA", 120, 450, 22, AMAR_B, fuente="black", sombra=False)
    rect(L, 0, 640, W, H, (120, 124, 132))
    for k in range(6):
        rect(L, k * 100 + 20, 760, k * 100 + 30, 860, (240, 240, 240))
    u = eio(prog(t, 0.0, 2.6))
    x = lerp(90, 250, u)
    prota(L, x, 880, t, s=0.85, pose=camina(t, 8, "empuja", "empuja2") if u < 1 else "empuja",
          boca=0.5 * prog(t, wt(e, "contento") - 0.3, 0.3))
    carro(L, x + 170, 880, 1 + int(prog(t, wt(e, "media") - 0.6, 1.2) * 7))
    qs = prog(t, wt(e, "Sígueme") - 0.2, 0.35)
    qp = prog(t, wt(e, "súper") - 0.2, 0.35)
    st["overlay"].append(("final", qs, qp))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "bolsa": esc_bolsa, "camino": esc_camino, "salones": esc_salones,
         "restaurante": esc_restaurante, "mercado": esc_mercado, "dato": esc_dato, "montaje": esc_montaje,
         "final": esc_final}


def corazon(O, x, y, r, col, a=1.0):
    if r <= 1:
        return
    circ(O, x - r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    circ(O, x + r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    poly(O, [(x - r * 1.02, y - r * 0.05), (x + r * 1.02, y - r * 0.05), (x, y + r * 0.95)], col, a=a)


def sello_t(O, txt, x, y, q, col=ROJO, size=34):
    if q <= 0:
        return
    s = 1 + 1.3 * (1 - eo3(q))
    w = ancho(txt, size * s) + 30 * s
    rect(O, x - w / 2, y - size * 0.75 * s, x + w / 2, y + size * 0.75 * s, (0, 0, 0), a=0.55 * q, r=10)
    rect(O, x - w / 2, y - size * 0.75 * s, x + w / 2, y + size * 0.75 * s, None, a=q, r=10, outline=col, w=5 * s)
    texto(O, txt, x, y, size * s, col, a=q, fuente="black", sombra=False)


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "titular":
            _, t, q = it
            s = 1 + 0.35 * math.exp(-t * 9)
            rect(O, 40, 318, 500, 372, (0, 0, 0), a=0.55, r=16)
            texto(O, "¿POR QUÉ TE PIERDES EN IKEA?", 270, 345, 25 * s, AMARILLO, fuente="black")
            sello_t(O, "ESTÁ HECHO A PROPÓSITO", 270, 900, q, size=28)
        elif tipo == "sello":
            _, txt, q, y, col = it
            sello_t(O, txt, 270, y, q, col=col, size=30)
        elif tipo == "energia":
            _, q, qa = it
            if qa <= 0:
                continue
            x0, y0 = 110, 420
            texto(O, "ENERGÍA", x0 + 125, y0 - 26, 18, BLANCO, a=qa, fuente="black")
            rect(O, x0, y0, x0 + 250, y0 + 30, (0, 0, 0), a=0.6 * qa, r=15)
            v = 0.15 + 0.85 * q
            col = mezcla(ROJO, VERDE, q)
            rect(O, x0 + 4, y0 + 4, x0 + 4 + 242 * v, y0 + 26, col, a=qa, r=12)
            texto(O, f"{int(v * 100)} %", x0 + 266, y0 + 15, 18, col, a=qa, fuente="black", anchor="lm")
        elif tipo == "ticket":
            _, total, q = it
            if q <= 0:
                continue
            x0, y0 = 330, 330
            rect(O, x0, y0, x0 + 170, y0 + 74, BLANCO, a=q, r=6)
            for k in range(9):
                poly(O, [(x0 + k * 19, y0 + 74), (x0 + k * 19 + 19, y0 + 74), (x0 + k * 19 + 9.5, y0 + 84)], BLANCO, a=q)
            texto(O, "TICKET", x0 + 85, y0 + 18, 14, (90, 90, 90), a=q, fuente="black", sombra=False)
            euros = f"{total:.2f} €".replace(".", ",")
            texto(O, euros, x0 + 85, y0 + 50, 28, ROJO if total > 10 else (30, 30, 30), a=q, fuente="black", sombra=False)
        elif tipo == "dato":
            _, q, ql, qp = it
            if q > 0:
                texto(O, f"{int(round(60 * q))} %", 270, 560, 74, AMAR_B, a=cl(q * 3), fuente="black")
            if ql > 0:
                sello_t(O, "NO ESTABA EN LA LISTA", 270, 790, ql, col=AMARILLO, size=28)
            if qp > 0:
                rect(O, 90, 362, 450, 402, (0, 0, 0), a=0.5 * qp, r=20)
                texto(O, "Prof. Alan Penn · University College London", 270, 382, 14, (225, 230, 240), a=qp,
                      fuente="bold", sombra=False)
        elif tipo == "fuente":
            _, q, txt = it
            rect(O, 110, 862, 430, 900, (0, 0, 0), a=0.55 * q, r=19)
            texto(O, txt, 270, 881, 14, (230, 230, 235), a=q, fuente="bold", sombra=False)
        elif tipo == "final":
            _, qs, qp = it
            if qs > 0:
                s = eob(qs)
                rect(O, 270 - 140 * s, 330, 270 + 140 * s, 390, (254, 44, 85), a=qs, r=30)
                texto(O, "+ SEGUIR", 270, 360, 26 * s, BLANCO, a=qs, fuente="black", sombra=False)
            if qp > 0:
                rect(O, 70, 410, 470, 470, (0, 0, 0), a=0.6 * qp, r=16)
                texto(O, "PRÓXIMO: LOS TRUCOS DEL SÚPER", 270, 440, 19, AMARILLO, a=qp, fuente="black", sombra=False)


def cabecera(O, st):
    if st.get("sin_cabecera"):
        return
    w = ancho(CABECERA, 15) + 30
    rect(O, 270 - w / 2, 148, 270 + w / 2, 180, AZUL_T, a=0.92, r=16)
    texto(O, CABECERA, 270, 164, 15, BLANCO, fuente="black", sombra=False)


def insignia(O, st, t):
    if not st.get("paso"):
        return
    n, txt = st["paso"]
    q = eo3(prog(t, 0.05, 0.4))
    s = f"{n}"
    w = ancho(txt, 19, "black") + 74
    x0 = 270 - w / 2 + 30 * (1 - q)
    rect(O, x0, 138, x0 + w, 182, AZUL_T, a=0.92 * q, r=22)
    circ(O, x0 + 24, 160, 16, fill=AMAR_B, a=q)
    texto(O, s, x0 + 24, 160, 18, (20, 20, 20), a=q, fuente="black", sombra=False)
    texto(O, txt, x0 + 48, 160, 19, BLANCO, a=q, fuente="black", anchor="lm", sombra=False)


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



_VIN = None


def VINETA():
    global _VIN
    if _VIN is None:
        sw, sh = IW // 8, IH // 8
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        r = np.sqrt(((xx - sw / 2) / sw) ** 2 + ((yy - sh / 2) / sh) ** 2 * 0.8)
        v = np.clip(1.25 - r * 1.1, 0.4, 1)
        _VIN = Image.fromarray((v * 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR).convert("RGB")
    return _VIN


def render_frame(fr):
    T = fr / FPS
    e = escena_en(T)
    t = T - e["t0"]
    D = e["dur"]
    img = Image.new("RGB", (IW, IH), (0, 0, 0))
    L = Capa(img)
    st = {"overlay": [], "luces": []}
    FUNCS[e["nombre"]](L, e, t, D, T, st)
    img = L.img
    z, fx, fy = st.get("cam", (1.04 + 0.06 * eio(t / D), 270, 500))
    z += golpe_zoom(T)
    cw, ch = IW / z, IH / z
    sh = st.get("shake", 0)
    x0 = cl(fx * K - cw / 2, 0, IW - cw) + (2 * math.sin(T * 1.7) + sh * math.sin(T * 61)) * K
    y0 = cl(fy * K - ch / 2, 0, IH - ch) + (2 * math.cos(T * 1.3)) * K
    img = img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    overlays(O, st, T)
    cabecera(O, st)
    insignia(O, st, t)
    subtitulos(O, T)
    out = O.img
    return out.resize((OW, OH), Image.LANCZOS).tobytes()


# ------------------------------------------------------------------ audio
def ruido(n, lp, seed, hp=None):
    rng = np.random.default_rng(seed)
    r = rng.standard_normal(n).astype(np.float32)
    if lp > 1:
        r = np.convolve(r, np.ones(lp) / lp, mode="same")
    if hp:
        r = r - np.convolve(r, np.ones(hp) / hp, mode="same")
    return r / (np.abs(r).max() + 1e-6)


def paso(seed, eco=False):
    m = int(0.12 * SR)
    u = np.arange(m) / SR
    r = np.random.default_rng(seed).standard_normal(m).astype(np.float32)
    s = (np.convolve(r, np.ones(8) / 8, mode="same") * np.exp(-u * 45) + np.sin(2 * np.pi * 90 * u) * np.exp(-u * 30) * 0.4)
    if eco:
        out = np.zeros(int(0.5 * SR), np.float32)
        out[:m] += s
        out[int(0.13 * SR):int(0.13 * SR) + m] += s * 0.35
        out[int(0.27 * SR):int(0.27 * SR) + m] += s * 0.15
        return out
    return s.astype(np.float32)


def pasos(dur, cada, seed, eco=False, vol=0.5):
    out = np.zeros(int(dur * SR) + SR, np.float32)
    t = 0.0
    k = 0
    while t < dur:
        colocar(out, paso(seed + k, eco) * vol, t)
        t += cada
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


def dingdong():
    m = int(1.4 * SR)
    u = np.arange(m) / SR
    s = np.sin(2 * np.pi * 784 * u) * np.exp(-u * 3) * (u < 0.7)
    u2 = np.clip(u - 0.45, 0, None)
    s += np.sin(2 * np.pi * 622 * u2) * np.exp(-u2 * 3) * (u >= 0.45)
    return (s * 0.3).astype(np.float32)


def tono(veces=2):
    out = np.zeros(int(veces * 1.2 * SR), np.float32)
    for k in range(veces):
        m = int(0.6 * SR)
        u = np.arange(m) / SR
        colocar(out, (np.sin(2 * np.pi * 425 * u) * 0.12).astype(np.float32), k * 1.2)
    return out


def caja():
    """«Ching» de caja registradora."""
    m = int(0.9 * SR)
    u = np.arange(m) / SR
    s = np.zeros(m, np.float32)
    for f, a in ((2093, 0.5), (2637, 0.35), (3136, 0.25)):
        s += a * np.sin(2 * np.pi * f * u) * np.exp(-u * 5)
    s[:int(0.03 * SR)] += np.random.default_rng(4).standard_normal(int(0.03 * SR)) * 0.4
    return (s * 0.35).astype(np.float32)


def musica(n):
    """Ostinato ligero y juguetón en mayor (pizzicato + bajo + bombo suave)."""
    out = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    t_dato = E["dato"]["t0"]
    t_fin = E["dato"]["t0"] + E["dato"]["dur"]
    beat = 60 / 116
    k = 0
    acordes = [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]]
    while k * beat / 2 < TOTAL:
        t0 = k * beat / 2
        ac = acordes[(k // 8) % 4]
        nn = ac[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12
        tenso = t_dato <= t0 < t_fin
        if tenso:
            nn -= 1 if k % 2 else 0
        m = int(0.22 * SR)
        u = np.arange(m) / SR
        f = nota(nn)
        colocar(out, ((np.sin(2 * np.pi * f * u) + 0.25 * np.sin(4 * np.pi * f * u)) * np.exp(-u * 16) * 0.05)
                .astype(np.float32), t0)
        if k % 2 == 0:
            mm = int(0.4 * SR)
            uu = np.arange(mm) / SR
            fb = nota(ac[0] - 24)
            colocar(out, (np.sin(2 * np.pi * fb * uu) * np.exp(-uu * 5) * 0.08).astype(np.float32), t0)
        if k % 4 == 0:
            mm = int(0.3 * SR)
            uu = np.arange(mm) / SR
            colocar(out, (np.sin(2 * np.pi * (50 + 70 * np.exp(-uu * 30)) * uu) * np.exp(-uu * 10) * 0.12)
                    .astype(np.float32), t0)
        if k % 4 == 2:
            colocar(out, ruido(int(0.06 * SR), 1, k, hp=6) * np.exp(-np.arange(int(0.06 * SR)) / SR * 60) * 0.03, t0)
        k += 1
    return out


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
    mus = musica(n)
    fx = (ruido(n, 300, 1) * 0.05).astype(np.float32)     # murmullo de tienda
    E = {e["nombre"]: e for e in ESC}
    g = E["gancho"]
    colocar(fx, dingdong(), 0.0, 0.8)
    colocar(fx, golpe() * 0.7, g["t0"] + wt(g, "hecho") - 0.2, 0.7)
    b = E["bolsa"]
    colocar(fx, whoosh(3, 0.4), b["t0"] + wt(b, "bolsa") - 0.5, 0.5)
    colocar(fx, pop(), b["t0"] + wt(b, "lámpara") - 0.3, 0.5)
    colocar(fx, pop(), b["t0"] + wt(b, "grande") - 0.5, 0.6)
    c = E["camino"]
    colocar(fx, pasos(c["dur"] - 0.5, 0.3, 11, vol=0.35), c["t0"] + 0.2, 1.0)
    colocar(fx, pop(), c["t0"] + wt(c, "atajos") - 0.3, 0.5)
    colocar(fx, golpe() * 0.4, c["t0"] + wt(c, "nadie") - 0.1, 0.5)
    s = E["salones"]
    colocar(fx, pop(), s["t0"] + wt(s, "casa") - 0.3, 0.5)
    colocar(fx, pop(), s["t0"] + wt(s, "imaginas") - 0.3, 0.5)
    r = E["restaurante"]
    for k in range(4):
        colocar(fx, tic() * 0.5, r["t0"] + wt(r, "Comes") + 0.25 * k, 0.6)
    colocar(fx, pop(), r["t0"] + wt(r, "sigues") - 0.3, 0.5)
    m = E["mercado"]
    for k, t0 in enumerate(tiempos_mercado(m)):
        colocar(fx, burbuja(k + 3), m["t0"] + t0 - 0.05, 0.6)
    colocar(fx, caja(), m["t0"] + tiempos_mercado(m)[-1] + 0.1, 0.8)
    d = E["dato"]
    colocar(fx, golpe() * 0.8, d["t0"] + wt(d, "sesenta") - 0.3, 0.8)
    colocar(fx, pop(), d["t0"] + wt(d, "lista") - 0.3, 0.6)
    mo = E["montaje"]
    for k in range(10):
        colocar(fx, tic() * 0.4, mo["t0"] + 0.3 + 0.26 * k, 0.6)
    colocar(fx, pop(), mo["t0"] + wt(mo, "valoras") - 0.3, 0.5)
    colocar(fx, golpe() * 0.5, mo["t0"] + wt(mo, "efecto") - 0.3, 0.6)
    f = E["final"]
    colocar(fx, caja(), f["t0"] + wt(f, "media") - 0.2, 0.7)
    colocar(fx, pop(), f["t0"] + wt(f, "Sígueme") - 0.2, 0.6)
    for k, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(k, 0.35), e["t0"] - 0.17, 0.3)
    envv = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.5 * np.clip(envv * 12, 0, 1)
    total = voz + (mus + fx) * duck
    total *= np.clip((TOTAL - tt) / 0.3, 0, 1)
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
