"""TikTok vertical «El problema de la vivienda»: datos reales (Banco de España, CJE, idealista, Colliers/APCE,
REAF), por qué falta suelo, el incentivo fiscal de los precios altos, la solución (más oferta) y un llamamiento
neutral a informarse antes de las elecciones del 29 de noviembre de 2026. Las fuentes están en guion.py.

    python3 voz.py && python3 video.py        -> vivienda_tiktok.mp4"""
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
SALIDA = os.path.join(AQUI, "vivienda_tiktok.mp4")

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


EXTRA = {"final": 0.8}
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
CLAVE = {"98%", "gana", "750.000", "240.000", "92.000", "8%", "sueldo,", "no.", "suelo.", "15", "juez", "fracasado",
         "dos", "like.", "nadie", "recauda:", "10%", "ibi", "irpf", "14%", "incentivo", "oferta.", "suelo,", "construir.",
         "29", "elecciones.", "urnas.", "alquiler?", "sígueme"}


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


# --- Escenas del TikTok «El problema de la vivienda» (se insertan en video.py al montarlo) ---

POSES.update({
    "agobio": dict(rodilla=(6, 95), pie=(2, 190), cuello=(4, -148), cabeza=(10, -190), codo=(30, -150), mano=(16, -200),
                   codo2=(-20, -150), mano2=(-4, -200)),
    "senala": dict(rodilla=(4, 95), pie=(2, 190), cuello=(2, -150), cabeza=(8, -196), codo=(46, -150), mano=(96, -190),
                   codo2=(-8, -74), mano2=(-4, -10)),
    "vota": dict(rodilla=(4, 95), pie=(2, 190), cuello=(4, -150), cabeza=(10, -196), codo=(40, -100), mano=(80, -120),
                 codo2=(-6, -76), mano2=(-2, -12)),
})

NAVY = (14, 22, 44)
NAVY2 = (24, 36, 66)
AMAR = (255, 206, 60)
ROJO_V = (238, 70, 70)
VERDE_V = (80, 210, 140)
AZUL_V = (90, 160, 240)
TXT = (236, 240, 248)
GRIS_V = (130, 140, 165)
JOVEN = ((60, 140, 220), (46, 112, 180), (50, 56, 76), (40, 44, 60))
CABECERA = "EL PROBLEMA DE LA VIVIENDA"
FUENTE = {"gancho": "Fuente: Consejo de la Juventud (2025)", "deficit": "Fuente: Banco de España, Informe Anual 2025",
          "precios": "Fuente: idealista (2025)", "suelo": "Fuente: Colliers y APCEspaña",
          "ley": "Congreso: may. 2024 y feb. 2025", "recaudacion": "Fuente: REAF, fiscalidad autonómica 2025",
          "votar": "Elecciones generales · 29 nov. 2026"}


def fondo(L, T, col=NAVY, col2=NAVY2):
    for i in range(0, H, 8):
        rect(L, 0, i, W, i + 8, mezcla(col, col2, i / H))
    for x in range(0, W + 1, 45):
        linea(L, [(x, 0), (x, H)], (255, 255, 255), w=0.6, a=0.03)
    for y in range(0, H + 1, 45):
        linea(L, [(0, y), (W, y)], (255, 255, 255), w=0.6, a=0.03)


def edificio(L, x, y, w, h, col=(60, 76, 110), luces=0.6, semilla=0, a=1.0):
    rect(L, x, y - h, x + w, y, col, a=a)
    rs = random.Random(semilla)
    for wy in range(int(y - h + 10), int(y - 14), 20):
        for wx in range(int(x + 8), int(x + w - 12), 18):
            on = rs.random() < luces
            rect(L, wx, wy, wx + 9, wy + 11, (255, 220, 130) if on else (40, 50, 76), a=a)


def ciudad(L, T, y0=780, luces=0.6, sem=1):
    rs = random.Random(sem)
    x = -10
    k = 0
    while x < W:
        w = rs.uniform(50, 90)
        h = rs.uniform(140, 330)
        edificio(L, x, y0, w, h, mezcla((50, 64, 96), (70, 86, 120), rs.random()), luces, semilla=sem * 100 + k)
        x += w + rs.uniform(4, 12)
        k += 1
    rect(L, 0, y0, W, H, (20, 26, 42))


def cartel_alquila(L, x, y, s=1.0, a=1.0, precio=None):
    rect(L, x - 60 * s, y - 34 * s, x + 60 * s, y + 34 * s, ROJO_V, a=a, r=6 * s)
    texto(L, "SE ALQUILA", x, y - (8 if precio else 0) * s, 18 * s, BLANCO, a=a, fuente="black", sombra=False)
    if precio:
        texto(L, precio, x, y + 16 * s, 15 * s, AMAR, a=a, fuente="black", sombra=False)


def barra(L, x, y, w, h_max, frac, col, etiqueta, valor, q, sub=""):
    h = h_max * frac * eo3(q)
    rect(L, x, y - h, x + w, y, col, a=q, r=8)
    texto(L, valor, x + w / 2, y - h - 26, 28, col, a=q, fuente="black")
    texto(L, etiqueta, x + w / 2, y + 24, 18, TXT, a=q, fuente="bold")
    if sub:
        texto(L, sub, x + w / 2, y + 46, 13, GRIS_V, a=q, fuente="semi")


def grua(L, x, y, t, a=1.0):
    linea(L, [(x, y), (x, y - 300)], AMAR, w=6, a=a)
    linea(L, [(x - 60, y - 300), (x + 200, y - 300)], AMAR, w=6, a=a)
    for k in range(0, 300, 30):
        linea(L, [(x - 6, y - k), (x + 6, y - k - 30)], AMAR, w=2, a=a)
    cx = x + 60 + 120 * (0.5 + 0.5 * math.sin(t * 0.8))
    linea(L, [(cx, y - 300), (cx, y - 160)], (200, 200, 210), w=2, a=a)
    rect(L, cx - 26, y - 160, cx + 26, y - 130, (150, 90, 60), a=a)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    fondo(L, T)
    # barras: sueldo frente a alquiler, visibles desde el fotograma 0
    q = cl(0.75 + t * 0.8)
    barra(L, 90, 800, 150, 250, 1.0, VERDE_V, "Sueldo joven", "1.191 €", q, "medio, al mes")
    barra(L, 300, 800, 150, 250, 1176 / 1191, ROJO_V, "Alquiler", "1.176 €", cl(q - 0.1), "piso para uno solo")
    st["overlay"].append(("titular98", t, e))
    tq = wt(e, "gana") - 0.2
    if t > tq:
        st["overlay"].append(("interrogante", prog(t, tq, 0.3), t))


def esc_deficit(L, e, t, D, T, st):
    fondo(L, T)
    t1 = wt(e, "750.000") - 0.2
    t2 = wt(e, "240.000") - 0.2
    t3 = wt(e, "92.000") - 0.2
    if t < t2 - 0.3:
        q = prog(t, t1, 0.4)
        # rejilla de casas vacías: cada icono = 25.000 viviendas que faltan
        for k in range(30):
            qk = prog(t, t1 + k * 0.03, 0.2)
            if qk <= 0:
                continue
            x = 70 + (k % 6) * 80
            y = 430 + (k // 6) * 80
            s = eob(qk)
            poly(L, [(x - 24 * s, y), (x, y - 22 * s), (x + 24 * s, y)], ROJO_V, a=qk)
            rect(L, x - 18 * s, y, x + 18 * s, y + 24 * s, None, a=qk, outline=ROJO_V, w=3)
        st["overlay"].append(("cifra", "750.000", "viviendas que faltan", 360, q))
    else:
        q2 = prog(t, t2, 0.4)
        q3 = prog(t, t3, 0.4)
        barra(L, 90, 780, 150, 340, 1.0, AZUL_V, "Hogares nuevos", "240.000", q2, "en 2025")
        if q3 > 0:
            barra(L, 300, 780, 150, 340, 92 / 240, AMAR, "Casas terminadas", "92.000", q3, "en 2025")
            if q3 >= 1:
                st["overlay"].append(("diferencia", prog(t, t3 + 0.5, 0.4)))


def esc_precios(L, e, t, D, T, st):
    fondo(L, T)
    ciudad(L, T, 820, luces=0.5, sem=3)
    # gente buscando y pocos carteles
    for j in range(5):
        persona(L, 70 + j * 100, 820 - 190 * 0.4, "agobio" if t > 1.4 else "de_pie", 0.4, ropa=JOVEN,
                pelo=(50, 36, 30))
    cartel_alquila(L, 300, 520, 1.1, precio="1.176 €/mes")
    t8 = wt(e, "8%") - 0.3
    if t > t8:
        st["overlay"].append(("grafico_sube", prog(t, t8, 1.0)))
    ts = wt(e, "sueldo") - 0.2
    if t > ts:
        st["overlay"].append(("sueldo_plano", prog(t, ts, 0.4)))


def esc_suelo(L, e, t, D, T, st):
    fondo(L, T, (20, 30, 30), (36, 52, 44))
    tf = wt(e, "suelo") - 0.2
    t15 = wt(e, "15") - 0.3
    tj = wt(e, "juez") - 0.2
    # parcela vacía con vallas y carteles
    rect(L, 40, 640, 500, 800, (120, 100, 70))
    for x in range(40, 501, 30):
        linea(L, [(x, 640), (x, 600)], (200, 200, 200), w=2)
    linea(L, [(40, 610), (500, 610)], (200, 200, 200), w=2)
    q = prog(t, tf, 0.3)
    if q > 0:
        rect(L, 180, 520, 360, 580, AMAR, a=q, r=4)
        texto(L, "SUELO", 270, 540, 22, NAVY, a=q, fuente="black", sombra=False)
        texto(L, "NO EDIFICABLE", 270, 564, 13, NAVY, a=q, fuente="black", sombra=False)
        linea(L, [(270, 580), (270, 640)], (180, 180, 180), w=4, a=q)
    if t > t15 and t < tj:
        st["overlay"].append(("calendario_anos", prog(t, t15, 1.2)))
    if t > tj:
        st["overlay"].append(("mazo", prog(t, tj, 0.35), t - tj))


def esc_ley(L, e, t, D, T, st):
    fondo(L, T)
    # hemiciclo esquemático
    cx, cy = 270, 760
    for fila in range(5):
        r = 120 + fila * 46
        n = 9 + fila * 3
        for k in range(n):
            ang = math.pi + (k + 0.5) / n * math.pi
            x, y = cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.75
            col = [ROJO_V, AZUL_V, AMAR, VERDE_V, (180, 120, 220), GRIS_V][(k + fila) % 6]
            circ(L, x, y, 9, fill=col, a=prog(t, 0.05 + fila * 0.05, 0.3))
    rect(L, cx - 60, cy - 20, cx + 60, cy + 30, (80, 90, 120), r=6)
    st["overlay"].append(("rechazada", prog(t, wt(e, "fracasado") - 0.2, 0.3), prog(t, wt(e, "dos") - 0.1, 0.3)))


def esc_like(L, e, t, D, T, st):
    fondo(L, T, (40, 14, 30), (70, 24, 50))
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    q = prog(t, wt(e, "nadie") - 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("grande", "ESPERA…", 370, q, AMAR))


def esc_impuestos(L, e, t, D, T, st):
    fondo(L, T)
    # casa en el centro y monedas que salen hacia «Hacienda»
    x, y = 150, 660
    poly(L, [(x - 90, y - 120), (x, y - 200), (x + 90, y - 120)], ROJO_V)
    rect(L, x - 74, y - 120, x + 74, y, (220, 210, 190))
    rect(L, x - 20, y - 60, x + 20, y, (120, 80, 60))
    # edificio institucional
    hx, hy = 400, 660
    poly(L, [(hx - 90, hy - 160), (hx, hy - 210), (hx + 90, hy - 160)], (200, 200, 210))
    rect(L, hx - 90, hy - 160, hx + 90, hy - 145, (200, 200, 210))
    for k in range(5):
        rect(L, hx - 80 + k * 38, hy - 145, hx - 66 + k * 38, hy - 10, (200, 200, 210))
    rect(L, hx - 100, hy - 10, hx + 100, hy, (200, 200, 210))
    texto(L, "IMPUESTOS", hx, hy - 176, 13, NAVY, fuente="black", sombra=False)
    conceptos = [("10%", "hasta 10% al comprar", 0), ("IBI", "IBI cada año", 1), ("IRPF", "IRPF del alquiler", 2)]
    for pal, txt, k in conceptos:
        tk = wt(e, pal) - 0.25
        if t > tk:
            q = prog(t, tk, 0.4)
            st["overlay"].append(("concepto", txt, 400, 440 - 0 + k * 0, k, q))
    # flujo de monedas
    if t > 0.6:
        for j in range(8):
            u = ((t - 0.6) * 0.7 + j / 8) % 1
            mx = lerp(x + 60, hx - 60, u)
            my = y - 90 - 120 * math.sin(u * math.pi)
            circ(L, mx, my, 12, fill=AMAR)
            texto(L, "€", mx, my, 13, NAVY, fuente="black", sombra=False)


def esc_recaudacion(L, e, t, D, T, st):
    fondo(L, T)
    t14 = wt(e, "14%") - 0.3
    pts = []
    u = eio(prog(t, 0.2, max(0.3, t14 - 0.2)))
    for k in range(int(30 * u) + 1):
        x = 70 + k * 13
        y = 760 - 260 * (k / 30) ** 1.6 - 10 * math.sin(k)
        pts.append((x, y))
    linea(L, [(60, 420), (60, 780), (480, 780)], GRIS_V, w=2)
    if len(pts) > 1:
        linea(L, pts, VERDE_V, w=5)
        circ(L, pts[-1][0], pts[-1][1], 8, fill=VERDE_V)
    texto(L, "recaudación ITP y AJD", 80, 440, 15, GRIS_V, fuente="bold", anchor="lm", sombra=False)
    q = prog(t, t14, 0.4)
    if q > 0:
        st["overlay"].append(("cifra", "+14%", "en 2025", 360, q))
    ti = wt(e, "incentivo") - 0.3
    if t > ti:
        st["overlay"].append(("incentivo", prog(t, ti, 0.4)))


def esc_solucion(L, e, t, D, T, st):
    fondo(L, T, (14, 34, 40), (20, 60, 66))
    tl = wt(e, "Liberar") - 0.2
    sube = eio(prog(t, tl, D - tl - 0.4))
    # edificios que se construyen
    for k in range(4):
        x = 50 + k * 115
        h = 80 + 220 * cl(sube * 1.3 - k * 0.12)
        edificio(L, x, 800, 90, h, (70, 110, 120), luces=0.7, semilla=k)
    rect(L, 0, 800, W, H, (20, 30, 34))
    grua(L, 470, 800, t)
    pasos = [("Liberar", "LIBERAR SUELO"), ("agilizar", "AGILIZAR LICENCIAS"), ("construir", "CONSTRUIR")]
    for j, (pal, txt) in enumerate(pasos):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("paso_sol", txt, j, q))
    qo = prog(t, wt(e, "oferta") - 0.3, 0.4)
    if qo > 0 and t < tl:
        st["overlay"].append(("cifra", "MÁS OFERTA", "", 400, qo))


def esc_votar(L, e, t, D, T, st):
    fondo(L, T)
    # urna con sobre que cae
    cx, cy = 270, 640
    rect(L, cx - 110, cy - 60, cx + 110, cy + 120, (220, 230, 240), a=0.25, r=8)
    rect(L, cx - 110, cy - 60, cx + 110, cy + 120, None, outline=(220, 230, 240), w=3, r=8)
    rect(L, cx - 60, cy - 66, cx + 60, cy - 54, NAVY)
    tv = wt(e, "urnas") - 0.6
    u = eio(prog(t, max(0.3, tv - 0.6), 0.7))
    sy = lerp(360, cy - 40, u)
    rect(L, cx - 40, sy - 26, cx + 40, sy + 26, (240, 230, 200), r=3)
    poly(L, [(cx - 40, sy - 26), (cx + 40, sy - 26), (cx, sy)], (220, 205, 170))
    persona(L, 100, 800 - 190 * 0.5, "vota", 0.5, ropa=JOVEN, pelo=(50, 36, 30))
    q = prog(t, wt(e, "29") - 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("29n", q))
    qp = prog(t, wt(e, "propone") - 0.2, 0.4)
    if qp > 0:
        st["overlay"].append(("checklist", qp))


def esc_final(L, e, t, D, T, st):
    fondo(L, T)
    ciudad(L, T, 860, luces=0.7, sem=9)
    st["overlay"].append(("seguir", t))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "deficit": esc_deficit, "precios": esc_precios, "suelo": esc_suelo, "ley": esc_ley,
         "like": esc_like, "impuestos": esc_impuestos, "recaudacion": esc_recaudacion, "solucion": esc_solucion,
         "votar": esc_votar, "final": esc_final}


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "titular98":
            _, t, e = it
            s = 1 + 0.4 * math.exp(-t * 9)
            texto(O, "98%", 270, 350, 96 * s, AMAR, fuente="black")
            texto(O, "DEL SUELDO EN ALQUILER", 270, 418, 24 * s, TXT, fuente="black")
        elif tipo == "interrogante":
            _, q, t = it
            texto(O, "¿QUIÉN GANA?", 270, 870, 36 * (0.8 + 0.2 * eob(q)), ROJO_V, a=q, fuente="black")
        elif tipo == "cifra":
            _, num, sub, y, q = it
            if q > 0:
                s = 0.8 + 0.2 * eob(q)
                texto(O, num, 270, y, 64 * s, AMAR, a=q, fuente="black")
                if sub:
                    texto(O, sub, 270, y + 44, 20, TXT, a=q, fuente="bold")
        elif tipo == "diferencia":
            q = it[1]
            rect(O, 90, 880, 450, 930, ROJO_V, a=q, r=25)
            texto(O, "FALTAN CASAS CADA AÑO", 270, 905, 20, BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "grafico_sube":
            q = it[1]
            pts = [(60 + k * 12, 420 - 70 * (k / 30) ** 1.8) for k in range(int(30 * q) + 1)]
            rect(O, 40, 330, 500, 450, (0, 0, 0), a=0.5, r=14)
            if len(pts) > 1:
                linea(O, pts, ROJO_V, w=5)
            texto(O, "ALQUILER +8%", 480, 360, 22, ROJO_V, fuente="black", anchor="rm")
        elif tipo == "sueldo_plano":
            q = it[1]
            linea(O, [(60, 430), (60 + 360 * q, 428)], VERDE_V, w=4)
            texto(O, "tu sueldo", 480, 430, 18, VERDE_V, a=q, fuente="black", anchor="rm")
        elif tipo == "calendario_anos":
            q = it[1]
            n = int(15 * q)
            rect(O, 60, 340, 480, 470, (0, 0, 0), a=0.6, r=14)
            for k in range(15):
                x = 84 + (k % 8) * 50
                y = 370 + (k // 8) * 50
                col = AMAR if k < n else (70, 80, 100)
                rect(O, x - 18, y - 16, x + 18, y + 16, col, r=4)
            texto(O, f"{max(1, n)} AÑO" + ("S" if n > 1 else ""), 400, 420, 26, AMAR, fuente="black")
        elif tipo == "mazo":
            _, q, dt = it
            ang = -0.9 + 0.9 * eo3(cl(dt / 0.25))
            x, y = 380, 450
            ca, sa = math.cos(ang), math.sin(ang)

            def R2(px, py):
                return (x + px * ca - py * sa, y + px * sa + py * ca)
            linea(O, [R2(0, 0), R2(-110, 0)], (150, 100, 60), w=10)
            poly(O, [R2(-130, -26), R2(-90, -26), R2(-90, 26), R2(-130, 26)], (120, 76, 44))
            if dt > 0.25:
                qq = prog(dt, 0.25, 0.3)
                s = 1 + 1.3 * (1 - eo3(qq))
                w = ancho("PLAN ANULADO", 32 * s) + 30 * s
                rect(O, 270 - w / 2, 560 - 26 * s, 270 + w / 2, 560 + 26 * s, NAVY, a=qq, r=8)
                rect(O, 270 - w / 2, 560 - 26 * s, 270 + w / 2, 560 + 26 * s, None, a=qq, r=8, outline=ROJO_V, w=5)
                texto(O, "PLAN ANULADO", 270, 560, 32 * s, ROJO_V, a=qq, fuente="black", sombra=False)
        elif tipo == "rechazada":
            _, q, q2 = it
            if q > 0:
                s = 1 + 1.3 * (1 - eo3(q))
                rect(O, 70, 400 - 34 * s, 470, 400 + 34 * s, None, a=q, r=10, outline=ROJO_V, w=5 * s)
                texto(O, "REFORMA FRACASADA", 270, 400, 30 * s, ROJO_V, a=q, fuente="black", sombra=False)
            if q2 > 0:
                texto(O, "×2", 270, 480, 60 * eob(q2) + 1, AMAR, a=q2, fuente="black")
        elif tipo == "like":
            _, t, tl = it
            q = prog(t, tl, 0.35)
            s = eob(q) * (1 + 0.08 * math.sin(t * 8))
            corazon(O, 270, 580, 110 * s, (254, 44, 85), a=cl(q * 1.5))
            texto(O, "DALE LIKE", 270, 750, 46 * (0.8 + 0.2 * eob(q)), TXT, a=q, fuente="black")
            rs = random.Random(3)
            for j in range(10):
                u = (t - tl - j * 0.08) / 1.2
                if 0 < u < 1:
                    corazon(O, 270 + rs.uniform(-160, 160) * u, 580 - 260 * u, 24 * (1 - u * 0.5), (254, 44, 85), a=1 - u)
        elif tipo == "grande":
            _, txt, y, q, col = it
            texto(O, txt, 270, y, 58 * (0.8 + 0.2 * eob(q)), col, a=q, fuente="black")
        elif tipo == "concepto":
            _, txt, x, y, k, q = it
            yy = 360 + k * 50
            w = ancho(txt, 19) + 36
            rect(O, 270 - w / 2, yy - 20, 270 + w / 2, yy + 20, AMAR, a=q, r=20)
            texto(O, txt, 270, yy, 19, NAVY, a=q, fuente="black", sombra=False)
        elif tipo == "incentivo":
            q = it[1]
            rect(O, 50, 830, 490, 890, (0, 0, 0), a=0.7 * q, r=14)
            texto(O, "Incentivo para bajar precios:", 270, 848, 17, TXT, a=q, fuente="bold", sombra=False)
            texto(O, "NINGUNO", 270, 874, 22, ROJO_V, a=q, fuente="black", sombra=False)
        elif tipo == "paso_sol":
            _, txt, j, q = it
            y = 360 + j * 52
            circ(O, 80, y, 18 * eob(q), fill=VERDE_V, a=q)
            linea(O, [(72, y), (78, y + 7), (89, y - 7)], NAVY, w=3.5, a=q)
            texto(O, txt, 110, y, 26 * (0.7 + 0.3 * eob(q)), TXT, a=q, fuente="black", anchor="lm")
        elif tipo == "29n":
            q = it[1]
            s = 0.7 + 0.3 * eob(q)
            texto(O, "29N", 270, 380, 96 * s, AMAR, a=q, fuente="black")
            texto(O, "ELECCIONES GENERALES", 270, 440, 22, TXT, a=q, fuente="black")
        elif tipo == "checklist":
            q = it[1]
            items = ["¿Qué propone sobre suelo?", "¿Y sobre alquiler?", "¿Y sobre construir?"]
            for j, tx in enumerate(items):
                qq = prog(q, j * 0.25, 0.4)
                rect(O, 230, 800 + j * 0 - 0, 230, 800, None)
                texto(O, "☐ " + tx, 200, 800 + j * 36, 17, TXT, a=qq, fuente="sym", anchor="lm")
        elif tipo == "seguir":
            t = it[1]
            circ(O, 270, 560, 70, fill=AMAR)
            texto(O, "M", 270, 560, 60, NAVY, fuente="black", sombra=False)
            tt = (t % 2.0)
            toque = prog(tt, 0.8, 0.3)
            r = 22 * (1 - 0.15 * math.sin(toque * math.pi))
            circ(O, 270, 632, r, fill=(254, 44, 85) if toque < 0.5 else BLANCO)
            texto(O, "+" if toque < 0.5 else "✓", 270, 632, 26, BLANCO if toque < 0.5 else (254, 44, 85), fuente="sym",
                  sombra=False)
            if 0 < toque < 1:
                circ(O, 270, 632, 22 + 40 * toque, outline=(254, 44, 85), w=3, a=1 - toque)
            texto(O, "@mente404_0", 270, 690, 26, TXT, fuente="black")
            texto(O, "Lo que no te cuentan, explicado", 270, 740, 22, AMAR, fuente="black")


def corazon(O, x, y, r, col, a=1.0):
    if r <= 1:
        return
    circ(O, x - r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    circ(O, x + r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    poly(O, [(x - r * 1.02, y - r * 0.05), (x + r * 1.02, y - r * 0.05), (x, y + r * 0.95)], col, a=a)


def cabecera(O, st):
    if st.get("sin_cabecera"):
        return
    w = ancho(CABECERA, 15) + 30
    rect(O, 270 - w / 2, 148, 270 + w / 2, 180, AMAR, a=0.95, r=16)
    texto(O, CABECERA, 270, 164, 15, NAVY, fuente="black", sombra=False)


def fecha(O, e, t):
    """Aquí, en vez de fecha, se muestra la fuente de cada dato."""
    txt = FUENTE.get(e["nombre"])
    if not txt:
        return
    q = prog(t, 0.2, 0.4)
    w = ancho(txt, 12, "semi") + 20
    rect(O, 20, 300, 20 + w, 324, (0, 0, 0), a=0.55 * q, r=8)
    texto(O, txt, 30, 312, 12, (200, 210, 230), a=q, fuente="semi", anchor="lm", sombra=False)


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
        out = Image.blend(out, Image.new("RGB", (IW, IH), NAVY), cl((T - (TOTAL - 0.5)) / 0.5))
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




def saw(f, tt, armonicos=8):
    s = np.zeros_like(tt)
    for k in range(1, armonicos + 1):
        s += np.sin(2 * np.pi * f * k * tt) / k
    return s


def musica(n):
    """Bajo sintetizado pulsante en menor (tensión) que pasa a mayor en «la solución»."""
    out = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    t_sol = E["solucion"]["t0"]
    beat = 60 / 112
    menor = [45, 45, 41, 43]
    mayor = [45, 49, 52, 50]
    k = 0
    while k * beat / 2 < TOTAL:
        t0 = k * beat / 2
        esperanza = t0 >= t_sol
        nota_ = (mayor if esperanza else menor)[(k // 8) % 4]
        f = 440 * 2 ** ((nota_ - 12 - 69) / 12)
        m = int(beat / 2 * SR * 0.9)
        u = np.arange(m) / SR
        s = saw(f, u, 10) * np.exp(-u * 7)
        s = np.convolve(s, np.ones(18) / 18, mode="same")
        colocar(out, (s * 0.08).astype(np.float32), t0)
        if k % 2 == 1:
            mm = int(0.03 * SR)
            r = np.random.default_rng(k).standard_normal(mm).astype(np.float32)
            colocar(out, np.diff(r, prepend=0) * 0.05 * np.exp(-np.arange(mm) / SR * 120), t0)
        if k % 4 == 0:
            mm = int(0.35 * SR)
            uu = np.arange(mm) / SR
            colocar(out, (0.13 * np.sin(2 * np.pi * (45 + 70 * np.exp(-uu * 30)) * uu) * np.exp(-uu * 9)).astype(np.float32), t0)
        if esperanza and k % 4 == 2:
            for nn in (nota_ + 12, nota_ + 16, nota_ + 19):
                colocar(out, piano(440 * 2 ** ((nn - 69) / 12), 1.0, 0.025), t0)
        k += 1
    tt = np.arange(n) / SR
    pad = sum(0.012 * np.sin(2 * np.pi * 440 * 2 ** ((nn - 69) / 12) * tt) for nn in (57, 60, 64))
    return out + pad.astype(np.float32)


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
    mus = musica(n) * 0.85
    fx = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    colocar(fx, braam(), 0.0, 0.7)
    colocar(fx, golpe(), 0.0, 0.5)
    g = E["gancho"]
    colocar(fx, braam(), g["t0"] + wt(g, "gana") - 0.2, 0.6)
    d = E["deficit"]
    for pal in ("750.000", "240.000", "92.000"):
        colocar(fx, ping(), d["t0"] + wt(d, pal) - 0.2, 0.5)
    p = E["precios"]
    colocar(fx, ping(), p["t0"] + wt(p, "8%") - 0.3, 0.5)
    colocar(fx, golpe() * 0.5, p["t0"] + wt(p, "sueldo") - 0.2, 0.5)
    s = E["suelo"]
    colocar(fx, mazo(), s["t0"] + wt(s, "juez") - 0.2 + 0.25, 0.8)
    colocar(fx, golpe(), s["t0"] + wt(s, "juez") + 0.3, 0.5)
    l_ = E["ley"]
    colocar(fx, golpe(), l_["t0"] + wt(l_, "fracasado") - 0.2, 0.6)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.7)
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.1, 0.5)
    colocar(fx, subida(1.2), lk["t0"] + wt(lk, "nadie") - 0.8, 0.6)
    colocar(fx, braam(), lk["t0"] + lk["dur"] - 0.15, 0.7)
    im = E["impuestos"]
    colocar(fx, monedas(im["dur"] - 0.8), im["t0"] + 0.6, 0.6)
    colocar(fx, caja(), im["t0"] + wt(im, "10%") - 0.25, 0.5)
    rc = E["recaudacion"]
    colocar(fx, ping(), rc["t0"] + wt(rc, "14%") - 0.3, 0.5)
    colocar(fx, golpe() * 0.6, rc["t0"] + wt(rc, "incentivo") - 0.3, 0.5)
    so = E["solucion"]
    for pal in ("Liberar", "agilizar", "construir"):
        colocar(fx, ping(), so["t0"] + wt(so, pal) - 0.2, 0.4)
    v = E["votar"]
    colocar(fx, braam(), v["t0"] + wt(v, "29") - 0.3, 0.6)
    colocar(fx, golpe() * 0.3, v["t0"] + wt(v, "urnas") - 0.6 + 0.7, 0.4)
    fi = E["final"]
    for k in range(3):
        colocar(fx, pop(), fi["t0"] + 0.8 + k * 2.0, 0.5)
    for k, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(k, 0.4), e["t0"] - 0.2, 0.35)
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
