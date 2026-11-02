"""TikTok vertical de misterio: la tragedia de los Andes de 1972 (La sociedad de la nieve).
Radar, choque, frío, radio, avalancha, travesía y rescate; voz con pausas dramáticas y procesado de
estudio, diseño sonoro (viento, motor, metal, estática, avalancha, río, helicópteros) y música cinematográfica.

    python3 voz.py && python3 video.py        -> andes_tiktok.mp4"""
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
SALIDA = os.path.join(AQUI, "andes_tiktok.mp4")

W, H = 540, 960            # unidades de diseño (9:16)
K = 3                      # resolución interna = 1620x2880
IW, IH = W * K, H * K
OW, OH = 1080, 1920
FPS = 30
SR = 44100
VOZ_OFF = 0.12
COLA = 0.3

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


EXTRA = {"choque": 0.3, "nota": 0.4, "final": 1.2}
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
CLAVE = {"1972", "45", "desaparece", "andes", "72", "nubes", "pronto", "cumbre", "doce", "3.600", "30", "cero",
         "radio", "cancelado", "comida", "difícil", "avalancha", "ocho", "pie", "equipo", "diez", "nota", "piedra",
         "avión", "montañas", "dieciséis", "casa", "nieve", "aguantado", "comentarios"}


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


# --- Escenas del TikTok «Andes, 1972» (se insertan en video.py al montarlo) ---

POSES.update({
    "camina1": dict(rodilla=(26, 92), pie=(36, 188), cuello=(14, -148), cabeza=(24, -192), codo=(-16, -76), mano=(-26, -14),
                    codo2=(18, -76), mano2=(32, -16)),
    "camina2": dict(rodilla=(-12, 94), pie=(-30, 188), cuello=(14, -148), cabeza=(24, -192), codo=(18, -76), mano=(32, -16),
                    codo2=(-16, -76), mano2=(-26, -14)),
    "lanza": dict(rodilla=(10, 94), pie=(14, 190), cuello=(-6, -148), cabeza=(-4, -194), codo=(-30, -180), mano=(-10, -236),
                  codo2=(20, -80), mano2=(30, -20)),
    "lanza2": dict(rodilla=(10, 94), pie=(14, 190), cuello=(10, -148), cabeza=(16, -194), codo=(50, -150), mano=(96, -170),
                   codo2=(20, -80), mano2=(30, -20)),
    "sentado_frio": dict(rodilla=(60, -10), pie=(70, 76), cuello=(10, -112), cabeza=(22, -150), codo=(40, -60), mano=(56, -40),
                         codo2=(36, -66), mano2=(50, -50)),
})

NIEVE = (232, 238, 246)
NIEVE_S = (186, 200, 220)
CIELO_N = (8, 12, 26)
ROCA_A = (60, 66, 82)
ROCA_A2 = (84, 92, 110)
CHAQUETA = ((150, 40, 40), (120, 30, 30), (50, 56, 70), (40, 44, 56))
CHAQUETA2 = ((60, 90, 140), (46, 70, 112), (50, 56, 70), (40, 44, 56))
ARRIERO = ((120, 90, 60), (96, 70, 46), (70, 60, 50), (56, 48, 40))
FECHA = {"gancho": "13 OCT 1972", "choque": "13 OCT 1972", "frio": "13 OCT 1972", "radio": "DÍA 11",
         "alud": "DÍA 17", "caminata": "DÍA 61", "nota": "DÍA 69", "rescate": "DÍA 72"}


def cordillera(L, T, y_base, alto, semilla, col=ROCA_A, nieve=NIEVE, desplaza=0.0, picos=6):
    rs = random.Random(semilla)
    pts = []
    n = picos * 2 + 1
    for k in range(n + 1):
        x = -60 + k * (W + 120) / n + desplaza
        y = y_base - (alto * rs.uniform(0.55, 1.0) if k % 2 == 1 else alto * rs.uniform(0.1, 0.35))
        pts.append((x, y))
    poly(L, pts + [(W + 80 + desplaza, H), (-80 + desplaza, H)], col)
    # casquetes de nieve
    for k in range(1, len(pts) - 1, 2):
        (x0, y0), (x1, y1), (x2, y2) = pts[k - 1], pts[k], pts[k + 1]
        f = 0.38
        poly(L, [(x1, y1), (lerp(x1, x2, f), lerp(y1, y2, f)), (lerp(x1, x2, f * 0.6), lerp(y1, y2, f) + 10),
                 (lerp(x1, x0, f * 0.5), lerp(y1, y0, f) + 14), (lerp(x1, x0, f), lerp(y1, y0, f))], nieve)
    return pts


def nubes(L, T, y, a=0.7, vel=12, semilla=1, col=(200, 210, 225)):
    rs = random.Random(semilla)
    for j in range(7):
        x = (rs.uniform(-200, W) + T * vel * rs.uniform(0.6, 1.4)) % (W + 400) - 200
        yy = y + rs.uniform(-60, 60)
        for k in range(5):
            circ(L, x + k * 34, yy + (k % 2) * 12, 40 + (k % 3) * 8, fill=col, a=a)


def avion(L, cx, cy, s=1.0, ang=0.0, a=1.0, sin_ala=0.0, sin_cola=0.0, t=0.0):
    """Bimotor turbohélice de ala alta, de perfil (mirando a la derecha)."""
    ca, sa = math.cos(ang), math.sin(ang)

    def Q(pts):
        return [(cx + (x * ca - y * sa) * s, cy + (x * sa + y * ca) * s) for x, y in pts]
    cuerpo = [(-130, -14), (90, -16), (120, -8), (132, 4), (120, 14), (-110, 16), (-150, 4)]
    if sin_cola < 1:
        poly(L, Q([(-118, -12), (-150, -66), (-132, -66), (-96, -14)]), (210, 214, 222), a=a * (1 - sin_cola))
        poly(L, Q([(-140, 2), (-176, -4), (-170, 6), (-138, 10)]), (200, 204, 212), a=a * (1 - sin_cola))
    poly(L, Q(cuerpo), (236, 238, 242), a=a)
    poly(L, Q([(-130, 2), (126, 2), (122, 8), (-140, 8)]), (190, 40, 50), a=a)
    for k in range(9):
        x = -96 + k * 20
        poly(L, Q([(x, -8), (x + 9, -8), (x + 9, -2), (x, -2)]), (60, 90, 130), a=a)
    poly(L, Q([(104, -12), (118, -8), (110, -4), (100, -6)]), (60, 90, 130), a=a)
    if sin_ala < 1:
        aa = a * (1 - sin_ala)
        poly(L, Q([(-30, -18), (40, -18), (44, -24), (-26, -24)]), (200, 204, 212), a=aa)
        poly(L, Q([(10, -24), (46, -24), (50, -12), (12, -12)]), (180, 184, 194), a=aa)
        hx, hy = Q([(52, -18)])[0]
        L.d.ellipse(P(hx - 3 * s, hy - 22 * s, hx + 3 * s, hy + 22 * s), fill=L.c((230, 230, 240), aa * 0.5))


def nieve_cayendo(O, T, a=1.0, vel=60, n=110):
    rs = random.Random(8)
    for _ in range(n):
        x0 = rs.uniform(0, W)
        v = rs.uniform(0.6, 1.4) * vel
        y = (rs.uniform(0, H) + T * v) % (H + 20) - 10
        x = x0 + 10 * math.sin(T * 1.5 + x0)
        circ(O, x, y, rs.uniform(1, 2.6), fill=BLANCO, a=0.7 * a)


def fuselaje(L, x, y, s=1.0, a=1.0, enterrado=0.0):
    """Fuselaje partido, semienterrado en la nieve, con el morro hacia arriba."""
    ang = -0.25
    avion(L, x, y, s, ang, a=a, sin_ala=1, sin_cola=1)
    poly(L, [(x - 150 * s, y + 30 * s), (x - 140 * s, y - 10 * s), (x - 132 * s, y + 34 * s)], (100, 104, 112), a=a)
    if enterrado > 0:
        sube = 84 * s * enterrado
        poly(L, [(x - 230 * s, y + 26 * s - sube), (x - 60 * s, y + 18 * s - sube), (x + 80 * s, y + 24 * s - sube),
                 (x + 230 * s, y + 20 * s - sube), (x + 230 * s, y + 120 * s), (x - 230 * s, y + 120 * s)], NIEVE, a=1)


def ladera(L, y0=700, inclin=0.25):
    poly(L, [(-20, y0 - 120), (W + 20, y0 - 120 + W * inclin), (W + 20, H), (-20, H)], NIEVE)
    poly(L, [(-20, y0 - 120), (W + 20, y0 - 120 + W * inclin), (W + 20, y0 - 112 + W * inclin), (-20, y0 - 112)],
         NIEVE_S)


def cielo_noche(L, T, claro=0.0):
    for i in range(0, H, 8):
        rect(L, 0, i, W, i + 8, mezcla(mezcla(CIELO_N, (60, 90, 140), claro), mezcla((26, 34, 60), (150, 180, 220), claro),
                                       cl(i / 760)))
    rs = random.Random(4)
    for _ in range(60):
        circ(L, rs.uniform(0, W), rs.uniform(0, 600), rs.uniform(0.5, 1.5), fill=BLANCO,
             a=(0.3 + 0.3 * math.sin(T * 2 + rs.random() * 6)) * (1 - claro))


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    cielo_noche(L, T)
    # radar
    cx, cy, R = 270, 560, 190
    circ(L, cx, cy, R, fill=(6, 26, 18))
    for r in (R, R * 0.66, R * 0.33):
        circ(L, cx, cy, r, outline=(40, 140, 80), w=1.5)
    linea(L, [(cx - R, cy), (cx + R, cy)], (40, 140, 80), w=1)
    linea(L, [(cx, cy - R), (cx, cy + R)], (40, 140, 80), w=1)
    ang = t * 2.2
    for k in range(14):
        a2 = ang - k * 0.05
        linea(L, [(cx, cy), (cx + R * math.cos(a2), cy + R * math.sin(a2))], (80, 230, 140), w=3, a=0.5 * (1 - k / 14))
    td = wt(e, "desaparece") - 0.2
    # punto del avión: avanza y se apaga
    bx, by = cx - 60 + 18 * t, cy - 40 - 6 * t
    vivo = 1 - prog(t, td, 0.3)
    if vivo > 0:
        brillo = 0.4 + 0.6 * max(0, math.cos((math.atan2(by - cy, bx - cx) - ang) % (2 * math.pi)))
        circ(L, bx, by, 7, fill=(140, 255, 170), a=vivo * brillo)
        texto(L, "FAU 571", bx + 14, by - 14, 12, (140, 255, 170), a=vivo * 0.8, fuente="mono", anchor="lm", sombra=False)
    else:
        q = prog(t, td + 0.3, 0.4)
        st["overlay"].append(("perdida", q, t))
    st["overlay"].append(("cifra", "45", "personas a bordo", prog(t, wt(e, "45") - 0.2, 0.4) * (1 - prog(t, td, 0.3))))
    q72 = prog(t, wt(e, "72") - 0.3, 0.5)
    if q72 > 0:
        st["overlay"].append(("dias72", q72))


def esc_choque(L, e, t, D, T, st):
    tg = wt(e, "Gira") - 0.2
    tc = wt(e, "choca") - 0.3
    if t < tc:
        cielo_noche(L, T, claro=0.35)
        cordillera(L, T, 760, 280, 2, ROCA_A, NIEVE, desplaza=-30 * t)
        nubes(L, T, 520, a=0.75, vel=-40, semilla=3)
        ang = -0.25 * prog(t, tg, 0.8)
        y = 470 + 120 * prog(t, tg, 1.6)
        avion(L, 230, y, 1.3, ang + 0.02 * math.sin(t * 4), t=t)
        nubes(L, T, 420, a=0.5, vel=-60, semilla=5)
        st["overlay"].append(("cree", prog(t, wt(e, "cruzado") - 0.3, 0.4) * (1 - prog(t, tg, 0.3))))
    else:
        dt = t - tc
        cielo_noche(L, T, claro=0.3)
        cordillera(L, T, 640, 380, 7, ROCA_A, NIEVE)
        ladera(L, 760, 0.35)
        # el fuselaje se desliza ladera abajo
        u = eo3(cl(dt / 2.4))
        x = lerp(80, 360, u)
        y = lerp(560, 760, u)
        avion(L, x, y, 0.9, 0.35, sin_ala=cl(dt * 4), sin_cola=cl(dt * 4))
        # trozos de ala volando y nieve levantada
        rs = random.Random(5)
        for j in range(30):
            vx, vy = rs.uniform(-200, 200), rs.uniform(-300, -60)
            px, py = 120 + vx * dt, 560 + vy * dt + 300 * dt * dt
            if py < H:
                circ(L, px, py, rs.uniform(2, 6), fill=NIEVE if j % 3 else (180, 184, 194), a=cl(1.5 - dt))
        for j in range(16):
            u2 = (dt * 1.5 + j / 16) % 1
            circ(L, x - 60 - 60 * u2, y + 20 - 30 * u2, 10 + 20 * u2, fill=BLANCO, a=0.5 * (1 - u2) * cl(2.4 - dt))
        st["flash"] = cl(1 - dt / 0.25)
        st["shake"] = 14 * math.exp(-dt * 3)


def esc_frio(L, e, t, D, T, st):
    cielo_noche(L, T)
    cordillera(L, T, 600, 300, 11, ROCA_A, NIEVE)
    ladera(L, 760, 0.12)
    fuselaje(L, 300, 640, 1.0, enterrado=0.15)
    tm = wt(e, "resto") - 0.2
    if t > tm:
        st["overlay"].append(("altimetro", prog(t, tm, 0.5), prog(t, wt(e, "3.600") - 0.2, 1.0)))
        st["overlay"].append(("termometro", prog(t, wt(e, "30") - 0.4, 0.5), prog(t, wt(e, "30") - 0.2, 1.2)))
    q = prog(t, 0.3, 0.4) * (1 - prog(t, tm, 0.3))
    if q > 0:
        st["overlay"].append(("cifra", "12", "muertos", q))
    st["nieve"] = 1.0
    st["viento"] = 1.0


def esc_radio(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (16, 18, 24))
    # interior oscuro del fuselaje: costillas
    for k in range(7):
        x = 40 + k * 76
        L.d.arc(P(x - 120, 300, x + 120, 900), 200, 340, fill=L.c((40, 44, 54)), width=6 * K)
    # radio de transistores
    cx, cy = 270, 580
    s = 1 + 0.03 * math.sin(t * 3)
    rect(L, cx - 130 * s, cy - 80 * s, cx + 130 * s, cy + 80 * s, (120, 90, 60), r=14)
    rect(L, cx - 110 * s, cy - 60 * s, cx + 10 * s, cy + 60 * s, (60, 50, 40), r=8)
    for k in range(7):
        linea(L, [(cx - 100 * s, cy - 48 * s + k * 16 * s), (cx, cy - 48 * s + k * 16 * s)], (90, 76, 60), w=2)
    rect(L, cx + 30 * s, cy - 50 * s, cx + 110 * s, cy - 10 * s, (230, 220, 190), r=4)
    aguja = cx + 40 * s + 60 * s * (0.5 + 0.5 * math.sin(t * 0.8))
    linea(L, [(aguja, cy - 48 * s), (aguja, cy - 12 * s)], ROJO, w=2)
    circ(L, cx + 70 * s, cy + 30 * s, 20 * s, fill=(80, 70, 60))
    linea(L, [(cx + 100 * s, cy - 80 * s), (cx + 190, cy - 280)], (180, 180, 190), w=3)
    # ondas
    for k in range(4):
        u = (t * 0.8 + k / 4) % 1
        L.d.arc(P(cx + 190 - 40 - 80 * u, cy - 280 - 40 - 80 * u, cx + 190 + 40 + 80 * u, cy - 280 + 40 + 80 * u),
                200, 340, fill=L.c((150, 200, 255), 1 - u), width=2 * K)
    tn = wt(e, "búsqueda") - 0.3
    if t > tn:
        st["overlay"].append(("cancelada", prog(t, tn, 0.35)))
    st["oscuro"] = 0.1


def esc_decision(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (10, 12, 18))
    for k in range(7):
        x = 40 + k * 76
        L.d.arc(P(x - 120, 300, x + 120, 900), 200, 340, fill=L.c((30, 34, 42)), width=6 * K)
    # siluetas sentadas, en penumbra
    for j, x in enumerate((100, 200, 300, 400)):
        persona(L, x, 700, "sentado_frio", 0.62, sombra=(22, 26, 34), flip=j % 2 == 1)
    # una vela
    circ(L, 270, 760, 6, fill=(255, 220, 140), a=0.9)
    st["vela"] = (270, 750)
    q = prog(t, wt(e, "decisión") - 0.3, 0.6)
    if q > 0:
        st["overlay"].append(("frase", "la decisión más difícil", 560, q))
    st["viento"] = 0.6


def esc_alud(L, e, t, D, T, st):
    cielo_noche(L, T)
    cordillera(L, T, 560, 260, 13, ROCA_A, NIEVE)
    ladera(L, 760, 0.12)
    ta = wt(e, "avalancha") - 0.2
    u = eio(prog(t, ta, 1.6))
    fuselaje(L, 300, 640, 1.0, enterrado=0.15 + 0.85 * prog(t, ta + 1.0, 0.8))
    if u > 0:
        frente = lerp(-200, 700, u)
        pts = [(-50, 300)]
        for k in range(12):
            x = frente - k * 60
            pts.append((x, 420 + k * 30 + 30 * math.sin(k + t * 6)))
        pts += [(-50, H)]
        poly(L, pts, (240, 244, 250), a=0.95)
        for j in range(40):
            rs = random.Random(j)
            px = frente - rs.uniform(0, 500)
            py = 400 + rs.uniform(0, 400)
            circ(L, px, py, rs.uniform(10, 34), fill=BLANCO, a=0.6)
        st["shake"] = 10 * math.sin(u * math.pi)
    qm = prog(t, wt(e, "ocho") - 0.3, 0.4)
    if qm > 0:
        st["overlay"].append(("cifra", "8", "muertos más", qm))
    st["nieve"] = 1.0


def esc_caminata(L, e, t, D, T, st):
    cielo_noche(L, T, claro=0.75)
    cordillera(L, T, 520, 300, 21, (110, 120, 140), NIEVE, picos=5)
    cordillera(L, T, 700, 260, 22, ROCA_A2, NIEVE, picos=4)
    ladera(L, 820, 0.0)
    # dos figuras caminando, con huellas
    u = prog(t, 0.2, D - 0.6)
    x = lerp(60, 420, u)
    for j in range(int(u * 30)):
        hx = 60 + j * 12
        rect(L, hx, 790 + (j % 2) * 6, hx + 6, 794 + (j % 2) * 6, NIEVE_S)
    for k, ropa in enumerate((CHAQUETA, CHAQUETA2)):
        pose = pose_mix("camina1", "camina2", 0.5 + 0.5 * math.sin(t * 5 + k * 1.5))
        persona(L, x - k * 50, 790 - 190 * 0.42, pose, 0.42, ropa=ropa, pelo=(60, 40, 30), barba=True)
    tn = wt(e, "Nando") - 0.2
    if t > tn and t < wt(e, "Sin") - 0.2:
        st["overlay"].append(("nombres2", prog(t, tn, 0.4)))
    td = wt(e, "diez") - 0.6
    if t > td:
        st["overlay"].append(("dias", prog(t, td, 1.6)))
    st["viento"] = 1.0


def esc_nota(L, e, t, D, T, st):
    tl = wt(e, "Vengo") - 0.4
    if t < tl:
        cielo_noche(L, T, claro=0.9)
        cordillera(L, T, 560, 220, 31, (120, 130, 110), (230, 236, 240), picos=5)
        rect(L, 0, 640, W, H, (110, 120, 80))
        # río
        rect(L, 0, 700, W, 760, (80, 120, 160))
        for k in range(10):
            xx = (k * 70 + t * 80) % (W + 60) - 30
            linea(L, [(xx, 720 + (k % 3) * 12), (xx + 30, 720 + (k % 3) * 12)], (200, 225, 245), w=2)
        # orilla de abajo: Parrado y Canessa; arriba: el arriero con su caballo
        tlanza = wt(e, "lanzan") - 0.2
        lan = prog(t, tlanza, 0.5)
        persona(L, 130, 820, pose_mix("lanza", "lanza2", eo3(lan)) if t > tlanza - 0.4 else "de_pie", 0.45, ropa=CHAQUETA,
                pelo=(60, 40, 30), barba=True)
        persona(L, 200, 820, "de_pie", 0.45, ropa=CHAQUETA2, pelo=(60, 40, 30), barba=True)
        # caballo
        hx, hy = 380, 640
        rect(L, hx - 50, hy - 40, hx + 40, hy, (120, 80, 50), r=16)
        for lx in (hx - 40, hx - 20, hx + 14, hx + 30):
            rect(L, lx, hy - 4, lx + 7, hy + 50, (100, 64, 40))
        poly(L, [(hx + 30, hy - 36), (hx + 70, hy - 76), (hx + 84, hy - 64), (hx + 44, hy - 20)], (120, 80, 50))
        persona(L, 320, 690 - 190 * 0.36, "de_pie", 0.36, ropa=ARRIERO, pelo=(40, 30, 20), bigote=True, flip=True)
        if lan > 0:
            u = lan
            sx, sy = lerp(140, 310, u), lerp(720, 660, u) - 120 * math.sin(u * math.pi)
            circ(L, sx, sy, 7, fill=(120, 120, 126))
            rect(L, sx - 8, sy - 3, sx + 8, sy + 3, BLANCO)
        q = prog(t, wt(e, "arriero") - 0.2, 0.4)
        if q > 0:
            st["overlay"].append(("etiqueta", 330, 560, "arriero chileno", q))
    else:
        rect(L, 0, 0, W, H, (40, 36, 30))
        q = prog(t, tl, 0.5)
        st["overlay"].append(("papel", q, t - tl))


def esc_rescate(L, e, t, D, T, st):
    cielo_noche(L, T, claro=0.95)
    cordillera(L, T, 600, 300, 41, (130, 140, 160), NIEVE)
    ladera(L, 780, 0.1)
    fuselaje(L, 300, 680, 0.8, enterrado=0.3)
    for k in range(2):
        u = prog(t, 0.2 + k * 0.6, 3.5)
        x = lerp(-80, 220 + k * 140, eo3(u))
        y = lerp(360, 470 + k * 30, eo3(u))
        rect(L, x - 40, y - 14, x + 30, y + 16, (200, 90, 40), r=14)
        rect(L, x + 30, y - 6, x + 90, y + 2, (200, 90, 40))
        rect(L, x + 84, y - 18, x + 92, y + 2, (200, 90, 40))
        linea(L, [(x - 30, y + 24), (x + 20, y + 24)], (40, 40, 40), w=3)
        anch = 70 * abs(math.sin(t * 30 + k))
        linea(L, [(x - anch, y - 22), (x + anch, y - 22)], (40, 40, 40), w=3)
        linea(L, [(x - 5, y - 22), (x - 5, y - 14)], (40, 40, 40), w=3)
    q = prog(t, wt(e, "dieciséis") - 0.3, 0.5)
    if q > 0:
        st["overlay"].append(("cifra", "16", "supervivientes", q))


def esc_final(L, e, t, D, T, st):
    cielo_noche(L, T, claro=0.25)
    cordillera(L, T, 640, 360, 51, ROCA_A, NIEVE)
    ladera(L, 800, 0.0)
    # cruz en memoria
    rect(L, 266, 560, 274, 700, (40, 40, 46))
    rect(L, 246, 590, 294, 598, (40, 40, 46))
    q = prog(t, wt(e, "aguantado") - 0.4, 0.4)
    if q > 0:
        st["overlay"].append(("comentario", q, t))
    st["nieve"] = 0.6
    st["sin_paso"] = True


FUNCS = {"gancho": esc_gancho, "choque": esc_choque, "frio": esc_frio, "radio": esc_radio, "decision": esc_decision,
         "alud": esc_alud, "caminata": esc_caminata, "nota": esc_nota, "rescate": esc_rescate, "final": esc_final}


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "perdida":
            _, q, t = it
            parp = 0.55 + 0.45 * math.sin(t * 10)
            rect(O, 110, 790, 430, 840, ROJO, a=q * parp, r=10)
            texto(O, "SEÑAL PERDIDA", 270, 815, 26, BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "cifra":
            _, num, sub, q = it
            if q <= 0:
                continue
            s = eob(q)
            texto(O, num, 270, 380 + 10 * (1 - s), 76 * s, BLANCO, a=q, fuente="black")
            texto(O, sub, 270, 432, 20, (200, 210, 230), a=q, fuente="bold")
        elif tipo == "dias72":
            q = it[1]
            rect(O, 140, 860, 400, 910, (0, 0, 0), a=0.6 * q, r=25)
            texto(O, "72 DÍAS", 270, 885, 30, AMARILLO, a=q, fuente="black", sombra=False)
        elif tipo == "cree":
            q = it[1]
            texto(O, "«ya hemos cruzado»", 270, 360, 26, (220, 230, 245), a=q, fuente="black")
        elif tipo == "altimetro":
            _, q, v = it
            rect(O, 30, 360, 200, 430, (0, 0, 0), a=0.6 * q, r=12)
            texto(O, f"{int(3600 * eo3(v)):,}".replace(",", ".") + " m", 115, 395, 28, BLANCO, a=q, fuente="mono",
                  sombra=False)
        elif tipo == "termometro":
            _, q, v = it
            if q <= 0:
                continue
            x, y = 450, 400
            rect(O, x - 12, y - 70, x + 12, y + 60, BLANCO, a=q, r=12)
            circ(O, x, y + 70, 22, fill=BLANCO, a=q)
            nivel = 1 - v
            col = mezcla((80, 160, 255), (40, 90, 220), v)
            rect(O, x - 6, y + 50 - 110 * (0.15 + 0.6 * nivel), x + 6, y + 60, col, a=q, r=6)
            circ(O, x, y + 70, 16, fill=col, a=q)
            texto(O, f"{int(-30 * v)}°C", x - 40, y + 70, 26, (160, 210, 255), a=q, fuente="black", anchor="rm")
        elif tipo == "cancelada":
            q = it[1]
            s = 1 + 1.3 * (1 - eo3(q))
            rect(O, 60, 340 - 40 * s, 480, 340 + 40 * s, None, a=q, r=10, outline=ROJO, w=5 * s)
            texto(O, "BÚSQUEDA CANCELADA", 270, 340, 30 * s, ROJO, a=q, fuente="black", sombra=False)
        elif tipo == "frase":
            _, txt, y, q = it
            texto(O, txt, 270, y, 30, (230, 230, 240), a=q, fuente="black")
        elif tipo == "nombres2":
            q = it[1]
            rect(O, 40, 340, 330, 410, (0, 0, 0), a=0.6 * q, r=12)
            texto(O, "NANDO PARRADO", 56, 362, 18, BLANCO, a=q, fuente="black", anchor="lm", sombra=False)
            texto(O, "ROBERTO CANESSA", 56, 390, 18, BLANCO, a=q, fuente="black", anchor="lm", sombra=False)
        elif tipo == "dias":
            q = it[1]
            d = 1 + int(9 * q)
            rect(O, 330, 340, 500, 400, (0, 0, 0), a=0.6, r=12)
            texto(O, f"DÍA {d}/10", 415, 370, 22, AMARILLO, fuente="mono", sombra=False)
        elif tipo == "etiqueta":
            _, x, y, txt, q = it
            w = ancho(txt, 16, "bold") + 24
            rect(O, x - w / 2, y - 16, x + w / 2, y + 16, (0, 0, 0), a=0.6 * q, r=16)
            texto(O, txt, x, y, 16, BLANCO, a=q, fuente="bold", sombra=False)
        elif tipo == "papel":
            _, q, dt = it
            ang = (1 - eo3(q)) * 0.3
            rect(O, 70, 340, 470, 780, (236, 228, 206), a=q, r=4)
            lineas_n = ["Vengo de un avión", "que cayó en", "las montañas..."]
            total = sum(len(x) for x in lineas_n)
            n = int(total * cl(dt / 2.6))
            for j, ln in enumerate(lineas_n):
                vis = ln[:max(0, n)]
                n -= len(ln)
                texto(O, vis, 100, 440 + j * 62, 34, (40, 40, 70), a=q, fuente="semi", anchor="lm", sombra=False)
            texto(O, "— Nando Parrado, 1972", 440, 720, 16, (100, 90, 80), a=q * cl(dt - 2.4), fuente="semi", anchor="rm",
                  sombra=False)
            _ = ang
        elif tipo == "comentario":
            _, q, t = it
            s = eob(q)
            rect(O, 80, 440 - 40 * s, 460, 440 + 40 * s, BLANCO, a=q, r=40 * s)
            poly(O, [(140, 476), (170, 476), (130, 506)], BLANCO, a=q)
            texto(O, "¿Tú habrías aguantado?", 270, 440, 24 * s, (30, 30, 30), a=q, fuente="black", sombra=False)


def vela(img, st):
    if "vela" not in st:
        return img
    x, y = st["vela"]
    m = Image.new("L", (IW // 4, IH // 4), 0)
    k = K / 4
    ImageDraw.Draw(m).ellipse(((x - 170) * k, (y - 260) * k, (x + 170) * k, (y + 100) * k), fill=200)
    m = m.filter(ImageFilter.GaussianBlur(14)).resize((IW, IH), Image.BILINEAR)
    calido = Image.eval(img, lambda v: min(255, int(v * 1.6 + 14)))
    calido = ImageChops.multiply(calido, Image.new("RGB", (IW, IH), (255, 200, 140)))
    return Image.composite(calido, img, m)


def fecha(O, e, t):
    txt = FECHA.get(e["nombre"])
    if not txt:
        return
    q = prog(t, 0.1, 0.4)
    rect(O, 20, 300, 20 + ancho(txt, 16, "mono") + 24, 332, (0, 0, 0), a=0.55 * q, r=8)
    texto(O, txt, 32, 316, 16, (220, 230, 240), a=q, fuente="mono", anchor="lm", sombra=False)


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
        v = np.clip(1.2 - r * 1.15, 0.3, 1)
        _VIN = Image.fromarray((v * 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR).convert("RGB")
    return _VIN


def frio(img, k=0.3):
    a = np.asarray(img).astype(np.float32)
    g = a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11
    tint = np.stack([g * 0.86, g * 0.97, g * 1.1 + 6], -1)
    return Image.fromarray(np.clip(a * (1 - k) + tint * k, 0, 255).astype(np.uint8))


def render_frame(fr):
    T = fr / FPS
    e = escena_en(T)
    t = T - e["t0"]
    D = e["dur"]
    img = Image.new("RGB", (IW, IH), (0, 0, 0))
    L = Capa(img)
    st = {"overlay": []}
    FUNCS[e["nombre"]](L, e, t, D, T, st)
    z = 1.04 + 0.08 * eio(t / D)
    cw, ch = IW / z, IH / z
    sh = st.get("shake", 0)
    x0 = (IW - cw) / 2 + sh * K * math.sin(T * 61)
    y0 = (IH - ch) / 2 + 20 * K + sh * K * math.cos(T * 47)
    img = L.img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    img = vela(img, st)
    if st.get("oscuro"):
        img = Image.blend(img, Image.new("RGB", (IW, IH), (0, 0, 0)), st["oscuro"])
    img = frio(img)
    if st.get("flash"):
        img = Image.blend(img, Image.new("RGB", (IW, IH), (255, 255, 255)), st["flash"])
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    if st.get("nieve"):
        nieve_cayendo(O, T, st["nieve"], vel=60 + 140 * st.get("viento", 0))
    overlays(O, st, T)
    fecha(O, e, t)
    subtitulos(O, T)
    # franjas de cine
    rect(O, 0, 0, W, 18, (0, 0, 0))
    rect(O, 0, H - 18, W, H, (0, 0, 0))
    out = O.img
    if T < 0.4:
        out = Image.blend(Image.new("RGB", (IW, IH), (0, 0, 0)), out, T / 0.4)
    if T > TOTAL - 1.2:
        out = Image.blend(out, Image.new("RGB", (IW, IH), (0, 0, 0)), cl((T - (TOTAL - 1.2)) / 1.2))
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


def musica(n):
    """Cuerdas graves en Re menor; al llegar el rescate, acordes en Re mayor con piano."""
    tt = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    t_esp = next(e for e in ESC if e["nombre"] == "nota")["t0"] + 2.0
    acordes_m = [[38, 50, 53, 57], [34, 46, 50, 53], [36, 48, 52, 55], [33, 45, 49, 52]]
    acordes_M = [[38, 50, 54, 57], [43, 55, 59, 62], [45, 57, 61, 64], [38, 50, 54, 57]]
    dur_ac = 5.0
    k = 0
    while k * dur_ac < TOTAL:
        t0 = k * dur_ac
        mayor = t0 >= t_esp
        ac = (acordes_M if mayor else acordes_m)[k % 4]
        a0 = int(t0 * SR)
        m = min(n - a0, int((dur_ac + 1.5) * SR))
        u = np.arange(m) / SR
        env = np.clip(u / 1.5, 0, 1) * np.clip((dur_ac + 1.5 - u) / 1.5, 0, 1)
        for nm in ac:
            f = 440 * 2 ** ((nm - 69) / 12)
            v = saw(f, u, 6) + saw(f * 1.004, u, 6)
            out[a0:a0 + m] += 0.012 * np.convolve(v, np.ones(30) / 30, mode="same") * env
        if mayor:
            for j, nm in enumerate(ac[1:] + [ac[1] + 12]):
                ta = a0 + int(j * 0.6 * SR)
                mm = min(n - ta, int(2.5 * SR))
                if mm > 0:
                    uu = np.arange(mm) / SR
                    f = 440 * 2 ** ((nm + 12 - 69) / 12)
                    out[ta:ta + mm] += 0.05 * (np.sin(2 * np.pi * f * uu) + 0.3 * np.sin(4 * np.pi * f * uu)) * np.exp(-uu * 1.8)
        k += 1
    # pulso grave de tensión (latido de fondo) antes del rescate
    t = 0.0
    while t < t_esp:
        a0 = int(t * SR)
        m = min(n - a0, int(0.4 * SR))
        u = np.arange(m) / SR
        out[a0:a0 + m] += 0.08 * np.sin(2 * np.pi * 48 * u) * np.exp(-u * 10)
        t += 1.1
    return out


def viento(n, seed=1):
    """Viento de montaña con silbido."""
    tt = np.arange(n) / SR
    base = ruido(n, 30, seed) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * tt + 1) * np.sin(2 * np.pi * 0.23 * tt))
    f = 520 + 180 * np.sin(2 * np.pi * 0.07 * tt) + 60 * np.sin(2 * np.pi * 0.31 * tt)
    silbido = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * tt)) ** 2
    return base * 0.5 + silbido * 0.06


def motor(dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = 0.6 * saw(88, tt, 10) * (0.7 + 0.3 * np.sin(2 * np.pi * 21 * tt))
    s = np.convolve(s, np.ones(25) / 25, mode="same") + 0.3 * ruido(n, 8, 4)
    return (s * np.clip(tt / 1.0, 0, 1) * np.clip((dur - tt) / 0.3, 0, 1) * 0.3).astype(np.float32)


def metal(dur=1.6):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 900 + 500 * np.sin(2 * np.pi * 2.3 * tt) - 400 * tt
    s = np.tanh(3 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-tt * 1.6) * 0.25
    return (s + ruido(n, 2, 6) * np.exp(-tt * 3) * 0.3).astype(np.float32)


def estatica(dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = ruido(n, 1, 7, hp=8) * 0.3 * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * tt))
    f = 1200 + 900 * np.sin(2 * np.pi * 0.4 * tt)
    s += 0.05 * np.sin(2 * np.pi * np.cumsum(f) / SR)
    return (s * np.clip(tt / 0.2, 0, 1) * np.clip((dur - tt) / 0.3, 0, 1)).astype(np.float32)


def latido():
    n = int(0.5 * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for t0, a in ((0, 1.0), (0.16, 0.7)):
        u = np.clip(tt - t0, 0, None)
        s += a * np.sin(2 * np.pi * 50 * u) * np.exp(-u * 16) * (tt >= t0)
    return s


def avalancha(dur=4.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    env = np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 0.7
    return (ruido(n, 60, 9) * env * 1.0 + ruido(n, 6, 10) * env * 0.3).astype(np.float32)


def pasos_nieve(dur):
    out = np.zeros(int(dur * SR), np.float32)
    t = 0.0
    k = 0
    while t < dur - 0.2:
        m = int(0.12 * SR)
        u = np.arange(m) / SR
        a0 = int(t * SR)
        out[a0:a0 + m] += ruido(m, 3, 20 + k, hp=20) * np.exp(-u * 30) * 0.5
        t += 0.42
        k += 1
    return out


def rio(dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    return (ruido(n, 4, 11, hp=40) * 0.25 * np.clip(tt / 0.5, 0, 1) * np.clip((dur - tt) / 0.5, 0, 1)).astype(np.float32)


def helicoptero(dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    pulso = (0.5 + 0.5 * np.sin(2 * np.pi * 6.5 * tt)) ** 6
    s = ruido(n, 40, 12) * pulso * 0.8 + 0.05 * np.sin(2 * np.pi * 1800 * tt)
    return (s * np.clip(tt / 2.5, 0, 1) * np.clip((dur - tt) / 0.8, 0, 1)).astype(np.float32)


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
    E = {e["nombre"]: e for e in ESC}
    # viento: fuerte en exteriores de montaña
    niv = {"gancho": 0.25, "choque": 0.6, "frio": 1.0, "radio": 0.35, "decision": 0.45, "alud": 0.8, "caminata": 1.0,
           "nota": 0.3, "rescate": 0.5, "final": 0.7}
    pasos = np.arange(0, TOTAL + 0.3, 0.05)
    env = np.convolve([niv[escena_en(min(x, TOTAL - 0.01))["nombre"]] for x in pasos], np.ones(16) / 16, mode="same")
    amb = viento(n) * np.interp(tt, pasos, env) * 0.22
    fx = np.zeros(n, np.float32)
    g = E["gancho"]
    colocar(fx, estatica(2.0) * 0.4, g["t0"] + 0.3, 0.4)
    colocar(fx, braam(), g["t0"] + wt(g, "desaparece") - 0.1, 0.9)
    colocar(fx, braam(), g["t0"] + wt(g, "72") - 0.1, 0.8)
    c = E["choque"]
    tc = c["t0"] + wt(c, "choca") - 0.3
    colocar(fx, motor(tc - c["t0"] + 0.2), c["t0"], 0.6)
    colocar(fx, metal(), tc, 0.8)
    colocar(fx, golpe(), tc, 1.0)
    colocar(fx, braam(), tc, 0.9)
    colocar(fx, avalancha(2.6) * 0.5, tc + 0.2, 0.6)
    r = E["radio"]
    colocar(fx, estatica(r["dur"] - 0.3), r["t0"] + 0.1, 0.5)
    tb = r["t0"] + wt(r, "búsqueda") - 0.3
    colocar(fx, braam(), tb, 0.8)
    for k in range(6):
        colocar(fx, latido(), tb + 0.6 + k * 0.8, 0.6)
    d = E["decision"]
    for k in range(int(d["dur"] / 0.9)):
        colocar(fx, latido(), d["t0"] + 0.3 + k * 0.9, 0.45)
    a = E["alud"]
    colocar(fx, avalancha(4.5), a["t0"] + wt(a, "avalancha") - 0.6, 1.0)
    colocar(fx, braam(), a["t0"] + wt(a, "ocho") - 0.3, 0.8)
    cm = E["caminata"]
    colocar(fx, pasos_nieve(cm["dur"] - 0.4), cm["t0"] + 0.2, 0.5)
    nt = E["nota"]
    colocar(fx, rio(wt(nt, "Vengo") - 0.2), nt["t0"], 0.6)
    colocar(fx, golpe() * 0.4, nt["t0"] + wt(nt, "lanzan") + 0.35, 0.4)
    rs_ = E["rescate"]
    colocar(fx, helicoptero(rs_["dur"] + 0.6), rs_["t0"] - 0.2, 0.5)
    for j, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(j, 0.6), e["t0"] - 0.3, 0.3)
    envv = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.55 * np.clip(envv * 12, 0, 1)
    total = voz + (mus + amb + fx) * duck
    total *= np.clip((TOTAL - tt) / 1.2, 0, 1)
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
