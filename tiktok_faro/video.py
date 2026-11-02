"""TikTok vertical de misterio «Imagina que...»: los fareros desaparecidos de las islas Flannan (1900).
Tormenta nocturna, lluvia, relámpagos, personajes planos, subtítulos palabra a palabra y sonido ambiente.

    python3 voz.py && python3 video.py        -> faro_tiktok.mp4"""
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
SALIDA = os.path.join(AQUI, "faro_tiktok.mp4")

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


EXTRA = {"gancho": 0.4, "falso": 0.4, "final": 1.4}
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
CLAVE = {"imagina", "farero", "1900", "nadie", "esperándote", "solo", "cerrada", "apagado", "parado", "tres",
         "desaparecido", "limpia", "15", "impermeables", "colgado", "abrigo", "nunca", "treinta", "barandillas",
         "cuerdas", "ola", "gigante", "falsas", "inquietante", "cuerpos", "noche", "comentarios"}


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


# --- Escenas del TikTok «Imagina que...» — islas Flannan, 1900 (se insertan en video.py al montarlo) ---

POSES.update({
    "sube1": dict(rodilla=(30, 70), pie=(36, 150), cuello=(16, -146), cabeza=(26, -190), codo=(-10, -80), mano=(-20, -20),
                  codo2=(30, -84), mano2=(46, -30)),
    "sube2": dict(rodilla=(10, 92), pie=(-20, 186), cuello=(16, -146), cabeza=(26, -190), codo=(30, -84), mano=(46, -30),
                  codo2=(-10, -80), mano2=(-20, -20)),
    "mira": dict(rodilla=(4, 95), pie=(2, 190), cuello=(4, -150), cabeza=(12, -194), codo=(36, -110), mano=(70, -120),
                 codo2=(-6, -76), mano2=(-2, -12)),
    "linterna": dict(rodilla=(4, 95), pie=(2, 190), cuello=(4, -150), cabeza=(10, -194), codo=(40, -96), mano=(86, -100),
                     codo2=(-6, -76), mano2=(-2, -12)),
})

NOCHE = (10, 16, 28)
MAR = (18, 40, 60)
MAR2 = (26, 56, 80)
ROCA = (34, 36, 42)
ROCA2 = (46, 48, 56)
CAL = (220, 222, 226)
IMPER = ((190, 160, 50), (160, 132, 40), (60, 60, 66), (48, 48, 54))       # impermeable amarillo
TIZA = (230, 230, 220)
FECHA = {"gancho": "26 DIC 1900", "subida": "26 DIC 1900", "cocina": "26 DIC 1900", "tres": "26 DIC 1900",
         "lampara": "15 DIC 1900", "abrigos": "26 DIC 1900", "embarcadero": "26 DIC 1900", "teoria": "¿15 DIC?"}


def relampago(T):
    """Intensidad de relámpago (0..1) en T, a ráfagas pseudoaleatorias."""
    k = int(T / 3.7)
    rs = random.Random(k * 7 + 3)
    t0 = k * 3.7 + rs.uniform(0.3, 3.0)
    dt = T - t0
    if rs.random() < 0.55 and 0 <= dt < 0.5:
        return (1 - dt / 0.5) * (0.6 + 0.4 * math.sin(dt * 60))
    return 0.0


def mar(L, T, y0=760, amp=10, col=MAR, col2=MAR2):
    for capa, (c, fase, a2) in enumerate([(col2, 0.0, amp), (col, 1.3, amp * 1.4)]):
        yy = y0 + capa * 26
        pts = [(x, yy + a2 * math.sin(x / 38 + T * (1.4 + capa * 0.5) + fase) + 4 * math.sin(x / 13 + T * 3))
               for x in range(-10, W + 20, 10)]
        poly(L, pts + [(W + 20, H), (-10, H)], c)
        linea(L, pts, (120, 160, 180), w=1.5, a=0.35)


def lluvia(O, T, a=1.0):
    rs = random.Random(5)
    for _ in range(90):
        x0 = rs.uniform(-100, W)
        v = rs.uniform(700, 1000)
        y = (rs.uniform(0, H) + T * v) % (H + 40) - 20
        x = x0 + (y * 0.25)
        linea(O, [(x, y), (x + 4, y + 16)], (170, 190, 210), w=1, a=0.35 * a)


def isla(L, T, faro_luz=0.0, barco=None):
    # acantilado
    poly(L, [(60, 900), (90, 560), (150, 520), (260, 480), (380, 500), (440, 540), (500, 600), (540, 640), (540, 900)], ROCA)
    poly(L, [(90, 560), (150, 520), (260, 480), (380, 500), (440, 540), (420, 560), (300, 520), (160, 552)], (60, 74, 58))
    # faro
    x, base = 300, 490
    rect(L, x - 30, base - 150, x + 30, base, CAL)
    rect(L, x - 30, base - 110, x + 30, base - 96, (180, 60, 50))
    rect(L, x - 36, base - 158, x + 36, base - 150, (40, 40, 44))
    rect(L, x - 22, base - 196, x + 22, base - 158, (60, 70, 80) if faro_luz <= 0 else (255, 240, 180))
    L.d.pieslice(P(x - 26, base - 222, x + 26, base - 172), 180, 360, fill=L.c((40, 40, 44)))
    # casa de los fareros
    rect(L, 190, base - 50, 270, base, (200, 200, 205))
    poly(L, [(184, base - 50), (230, base - 80), (276, base - 50)], (70, 60, 60))
    if barco:
        bx, by = barco
        poly(L, [(bx - 60, by), (bx + 60, by), (bx + 44, by + 24), (bx - 48, by + 24)], (30, 30, 34))
        rect(L, bx - 20, by - 30, bx + 22, by, (200, 200, 205))
        rect(L, bx + 2, by - 54, bx + 14, by - 30, (60, 40, 30))
        for j in range(4):
            u = (T * 0.5 + j / 4) % 1
            circ(L, bx + 8 - 40 * u, by - 60 - 50 * u, 8 + 10 * u, fill=(120, 120, 130), a=0.5 * (1 - u))


def cielo(L, T):
    for i in range(0, H, 8):
        rect(L, 0, i, W, i + 8, mezcla((14, 20, 36), (30, 40, 56), cl(i / 700)))
    rs = random.Random(3)
    for j in range(6):
        x = (rs.uniform(-200, W) + T * rs.uniform(8, 20)) % (W + 300) - 150
        y = rs.uniform(300, 520)
        for k in range(4):
            circ(L, x + k * 40, y + (k % 2) * 10, 46, fill=(40, 48, 64), a=0.6)


def esc_gancho(L, e, t, D, T, st):
    cielo(L, T)
    u = eio(prog(t, 0, wt(e, "faro") - 0.5))
    isla(L, T, barco=(lerp(-60, 150, u), 770))
    mar(L, T)
    st["lluvia"] = 1.0
    q = prog(t, wt(e, "nadie") - 0.2, 0.6)
    if q > 0:
        st["overlay"].append(("interrogante", 300, 390, q, t))
    q2 = prog(t, wt(e, "Escocia") - 0.4, 0.5)
    if q2 > 0 and t < wt(e, "26") - 0.2:
        st["overlay"].append(("mapa", q2))


def esc_subida(L, e, t, D, T, st):
    cielo(L, T)
    # escalera tallada en el acantilado (diagonal)
    poly(L, [(0, 900), (0, 548), (140, 540), (540, 530), (540, 900)], ROCA)
    for j in range(12):
        x = 40 + j * 36
        y = 830 - j * 30
        rect(L, x, y, x + 40, y + 10, ROCA2)
    rect(L, 420, 440, 540, 530, (200, 200, 205))
    poly(L, [(412, 440), (480, 412), (548, 440)], (70, 60, 60))
    rect(L, 448, 466, 492, 530, (70, 50, 40))      # puerta cerrada
    circ(L, 484, 500, 4, fill=(200, 170, 90))
    mar(L, T, y0=880, amp=8)
    u = prog(t, 0.2, wt(e, "puerta") - 0.6)
    j = u * 10
    x = 60 + j * 36
    y = 830 - j * 30 - 190 * 0.55
    pose = pose_mix("sube1", "sube2", 0.5 + 0.5 * math.sin(t * 7)) if u < 1 else "mira"
    persona(L, x, y, pose, 0.55, ropa=IMPER, pelo=(60, 50, 40), bigote=True)
    st["lluvia"] = 1.0
    qb = prog(t, wt(e, "bandera") - 0.2, 0.4)
    if qb > 0 and t < wt(e, "Joseph") - 0.1:
        st["overlay"].append(("asta", qb))
    qn = prog(t, wt(e, "Joseph") - 0.1, 0.4)
    if qn > 0 and t < wt(e, "puerta") - 0.4:
        st["overlay"].append(("nombre", "JOSEPH MOORE", "farero de relevo", qn))
    qp = prog(t, wt(e, "cerrada") - 0.3, 0.4)
    if qp > 0:
        st["overlay"].append(("candado", 470, 476, qp))


def esc_cocina(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (36, 34, 32))
    rect(L, 0, 330, W, 760, (88, 80, 70))
    rect(L, 0, 760, W, H, (56, 48, 42))
    # chimenea apagada
    rect(L, 40, 520, 190, 760, (70, 60, 56))
    rect(L, 70, 600, 160, 760, (20, 18, 18))
    for j in range(3):
        rect(L, 84 + j * 22, 740, 104 + j * 22, 752, (50, 40, 36), r=3)
    # mesa y sillas
    rect(L, 250, 640, 470, 656, (110, 76, 50))
    for lx in (262, 450):
        rect(L, lx, 656, lx + 10, 760, (90, 60, 40))
    rect(L, 220, 600, 230, 760, (90, 60, 40))
    rect(L, 200, 680, 250, 690, (90, 60, 40))
    # reloj de pared parado
    cx, cy = 360, 450
    rect(L, cx - 40, cy - 60, cx + 40, cy + 110, (100, 64, 40), r=10)
    circ(L, cx, cy - 10, 32, fill=(236, 230, 210))
    for k in range(12):
        a2 = k * math.pi / 6
        circ(L, cx + 26 * math.cos(a2), cy - 10 + 26 * math.sin(a2), 1.5, fill=(40, 40, 40))
    parado = t > wt(e, "reloj") + 0.6
    ang_m = math.radians(-90 + (40 if parado else 40 + (t * 360 / 60) % 360))
    linea(L, [(cx, cy - 10), (cx + 22 * math.cos(ang_m), cy - 10 + 22 * math.sin(ang_m))], (30, 30, 30), w=2.5)
    linea(L, [(cx, cy - 10), (cx + 14 * math.cos(math.radians(150)), cy - 10 + 14 * math.sin(math.radians(150)))],
          (30, 30, 30), w=3.5)
    pend = 0 if parado else 0.35 * math.sin(t * 5)
    px, py = cx + 50 * math.sin(pend), cy + 30 + 50 * math.cos(pend)
    linea(L, [(cx, cy + 30), (px, py)], (200, 170, 90), w=2)
    circ(L, px, py, 9, fill=(200, 170, 90))
    st["oscuro"] = 0.25
    qf = prog(t, wt(e, "fuego") - 0.2, 0.4)
    if qf > 0:
        st["overlay"].append(("etiqueta", 115, 570, "fuego apagado", qf))
    qr = prog(t, wt(e, "parado") - 0.2, 0.4)
    if qr > 0:
        st["overlay"].append(("etiqueta", cx, 360, "parado", qr))


def esc_tres(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (14, 18, 26))
    nombres = [("James", "Ducat"), ("Thomas", "Marshall"), ("Donald", "MacArthur")]
    for j, (n1, n2) in enumerate(nombres):
        q = prog(t, wt(e, n1) - 0.15, 0.4)
        if q <= 0:
            continue
        x = 105 + j * 165
        y = 520
        s = eob(q)
        rect(L, x - 72, y - 130, x + 72, y + 110, (30, 36, 48), a=q, r=10)
        # silueta sin rostro
        circ(L, x, y - 48, 34 * s, fill=(60, 66, 80), a=q)
        L.d.chord(P(x - 56 * s, y - 6, x + 56 * s, y + 100 * s), 180, 360, fill=L.c((60, 66, 80), q))
        texto(L, "?", x, y - 48, 34 * s, (150, 160, 180), a=q, fuente="black", sombra=False)
        texto(L, n1.upper(), x, y + 62, 15, (220, 220, 230), a=q, fuente="black", sombra=False)
        texto(L, n2.upper(), x, y + 84, 15, (220, 220, 230), a=q, fuente="black", sombra=False)
    st["overlay"].append(("sello", "DESAPARECIDOS", 270, 720, prog(t, wt(e, "desaparecido") - 0.2, 0.3)))


def esc_lampara(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (16, 20, 30))
    # sala de la linterna: lente de Fresnel
    cx, cy = 270, 520
    rect(L, cx - 160, 330, cx + 160, 720, (26, 32, 44))
    for k in range(10):
        linea(L, [(cx - 160 + k * 32, 330), (cx - 160 + k * 32, 720)], (40, 48, 64), w=2)
    for r in range(110, 10, -14):
        circ(L, cx, cy, r, outline=(170, 200, 210), w=3, a=0.55)
    circ(L, cx, cy, 12, fill=(240, 230, 190))
    brillo = 0.5 + 0.5 * math.sin(t * 3)
    for j in range(6):
        a2 = t * 0.4 + j * math.pi / 3
        linea(L, [(cx + 40 * math.cos(a2), cy + 40 * math.sin(a2)), (cx + 60 * math.cos(a2), cy + 60 * math.sin(a2))],
              BLANCO, w=2, a=0.5 * brillo)
    rect(L, cx - 120, 720, cx + 120, 760, (60, 60, 66))
    ql = prog(t, wt(e, "limpia") - 0.2, 0.4)
    if ql > 0:
        st["overlay"].append(("etiqueta", cx, 360, "limpia · con aceite", ql))
    qp = prog(t, wt(e, "anotaciones") - 0.3, 0.4)
    if qp > 0:
        st["overlay"].append(("pizarra", qp, t))


def esc_abrigos(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (20, 18, 18))
    rect(L, 0, 330, W, 780, (70, 60, 52))
    rect(L, 60, 400, 480, 420, (90, 64, 42), r=4)
    for j in range(3):
        x = 140 + j * 130
        circ(L, x, 430, 7, fill=(60, 44, 30))
        linea(L, [(x, 430), (x, 452)], (60, 44, 30), w=4)
    # dos perchas vacías; el tercer impermeable (el de MacArthur) sigue colgado
    q = prog(t, wt(e, "Faltan") - 0.3, 0.5)
    for j in range(2):
        x = 140 + j * 130
        texto(L, "?", x, 520, 46, (160, 150, 130), a=q * (0.5 + 0.5 * math.sin(t * 4 + j)), fuente="black", sombra=False)
    x = 400
    poly(L, [(x - 40, 452), (x + 40, 452), (x + 58, 680), (x - 58, 680)], IMPER[0])
    poly(L, [(x - 40, 452), (x - 20, 452), (x - 54, 600), (x - 70, 590)], IMPER[1])
    poly(L, [(x + 40, 452), (x + 20, 452), (x + 54, 600), (x + 70, 590)], IMPER[1])
    linea(L, [(x, 460), (x, 676)], IMPER[1], w=2)
    # haz de linterna que barre
    bx = 270 + 180 * math.sin(t * 0.8)
    st["haz"] = (bx, 520)
    qc = prog(t, wt(e, "colgado") - 0.2, 0.4)
    if qc > 0:
        st["overlay"].append(("etiqueta", x, 720, "el abrigo de MacArthur", qc))
    qn = prog(t, wt(e, "norma") - 0.2, 0.4)
    if qn > 0:
        st["overlay"].append(("norma", qn))


def esc_embarcadero(L, e, t, D, T, st):
    cielo(L, T)
    poly(L, [(0, 380), (300, 400), (360, 520), (380, 900), (0, 900)], ROCA)
    # plataforma y barandilla doblada
    rect(L, 160, 600, 380, 614, (90, 84, 76))
    q = prog(t, wt(e, "arrancado") - 0.3, 0.6)
    for j in range(6):
        x = 180 + j * 36
        doblez = q * (0.3 + 0.7 * (j % 3 == 1)) * 40
        linea(L, [(x, 600), (x + doblez, 560 + doblez * 0.4)], (160, 160, 170), w=4)
    if q < 0.5:
        linea(L, [(180, 562), (360, 562)], (160, 160, 170), w=4)
    # mar abajo con olas que golpean
    mar(L, T, y0=820, amp=14)
    k = (t % 3.0) / 3.0
    if k < 0.4:
        h = math.sin(k / 0.4 * math.pi)
        poly(L, [(380, 820), (540, 820), (540, 820 - 320 * h), (430, 820 - 260 * h)], (200, 220, 230), a=0.6 * h)
    # marca de altura
    linea(L, [(470, 600), (470, 820)], AMARILLO, w=2)
    linea(L, [(460, 600), (480, 600)], AMARILLO, w=2)
    linea(L, [(460, 820), (480, 820)], AMARILLO, w=2)
    qa = prog(t, wt(e, "treinta") - 0.2, 0.4)
    texto(L, "+30 m", 470, 700, 22, AMARILLO, a=qa, fuente="black")
    qc = prog(t, wt(e, "caja") - 0.2, 0.4)
    if qc > 0:
        st["overlay"].append(("etiqueta", 270, 520, "caja de cuerdas: desaparecida", qc))
    st["lluvia"] = 1.0


def esc_teoria(L, e, t, D, T, st):
    cielo(L, T)
    poly(L, [(0, 520), (360, 540), (380, 900), (0, 900)], ROCA)
    tw = wt(e, "ola") - 0.2
    ola = eio(prog(t, tw, 1.2))
    # tres siluetas en el borde
    for j in range(3):
        x = 140 + j * 70
        if ola < 0.6:
            persona(L, x, 540 - 190 * 0.42, "de_pie", 0.42, sombra=(10, 12, 18), a=1 - ola / 0.6)
    mar(L, T, y0=800, amp=14)
    if ola > 0:
        cresta = 900 - 640 * math.sin(ola * math.pi)
        xs = lerp(560, -100, ola)
        poly(L, [(xs, 900), (xs + 120, cresta), (xs + 260, cresta + 40), (W + 40, 820), (W + 40, 900)], (40, 80, 110), a=0.95)
        linea(L, [(xs + 60, cresta + 120), (xs + 120, cresta), (xs + 260, cresta + 40)], (220, 235, 245), w=5)
    st["lluvia"] = 1.0
    q1 = prog(t, wt(e, "abrigo") - 0.3, 0.4)
    if q1 > 0:
        st["overlay"].append(("pregunta", "¿Sin abrigo?", 300, q1))
    q2 = prog(t, wt(e, "tres") - 0.4, 0.4)
    if q2 > 0:
        st["overlay"].append(("pregunta", "¿Faro solo?", 360, q2))


def esc_falso(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (24, 22, 20))
    tv = wt(e, "verdad") - 0.3
    if t < tv:
        q = prog(t, 0.2, 0.5)
        rect(L, 80, 360, 460, 760, (230, 220, 196), a=q, r=6)
        lineas_d = ["18 dic: Fuertes vientos.", "Marshall llora...", "Ducat muy callado...", "Dios lo ve todo..."]
        for j, ln in enumerate(lineas_d):
            n = int(len(ln) * prog(t, 0.6 + j * 0.5, 0.6))
            texto(L, ln[:n], 110, 420 + j * 60, 22, (60, 50, 70), a=q, fuente="semi", anchor="lm", sombra=False)
        st["overlay"].append(("sello", "FALSO", 270, 560, prog(t, wt(e, "falsas") - 0.25, 0.3)))
    else:
        mar(L, T, y0=500, amp=12)
        q = prog(t, wt(e, "cuerpos") - 0.4, 0.6)
        st["overlay"].append(("nunca", q))
        st["lluvia"] = 0.6


def esc_final(L, e, t, D, T, st):
    cielo(L, T)
    isla(L, T)
    mar(L, T)
    st["lluvia"] = 0.8
    q = prog(t, wt(e, "comentarios") - 0.4, 0.4)
    if q > 0:
        st["overlay"].append(("comentario", q, t))
    st["sin_paso"] = True


FUNCS = {"gancho": esc_gancho, "subida": esc_subida, "cocina": esc_cocina, "tres": esc_tres, "lampara": esc_lampara,
         "abrigos": esc_abrigos, "embarcadero": esc_embarcadero, "teoria": esc_teoria, "falso": esc_falso,
         "final": esc_final}


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "interrogante":
            _, x, y, q, t = it
            texto(O, "?", x, y - 8 * math.sin(t * 2), 70 * eob(q), ROJO, a=q, fuente="black")
        elif tipo == "mapa":
            q = it[1]
            rect(O, 330, 330, 510, 470, (20, 30, 44), a=0.85 * q, r=12, outline=(120, 140, 160), w=1.5)
            poly(O, [(400, 450), (410, 400), (430, 380), (440, 350), (460, 360), (450, 400), (440, 450)], (90, 110, 90), a=q)
            circ(O, 360, 372, 5, fill=ROJO, a=q)
            texto(O, "Flannan", 360, 392, 11, BLANCO, a=q, fuente="bold", sombra=False)
            texto(O, "ESCOCIA", 446, 462, 10, (200, 200, 210), a=q, fuente="black", sombra=False)
        elif tipo == "asta":
            q = it[1]
            linea(O, [(520, 440), (520, 370)], (180, 180, 190), w=3, a=q)
            texto(O, "sin bandera", 450, 380, 16, (220, 220, 230), a=q, fuente="bold")
        elif tipo == "nombre":
            _, n, sub, q = it
            rect(O, 40, 330, 300, 392, (0, 0, 0), a=0.6 * q, r=12)
            texto(O, n, 56, 350, 20, BLANCO, a=q, fuente="black", anchor="lm", sombra=False)
            texto(O, sub, 56, 376, 14, (200, 200, 210), a=q, fuente="semi", anchor="lm", sombra=False)
        elif tipo == "candado":
            _, x, y, q = it
            s = eob(q)
            rect(O, x - 16 * s, y - 4 * s, x + 16 * s, y + 22 * s, (200, 170, 90), a=q, r=4)
            O.d.arc(P(x - 11 * s, y - 22 * s, x + 11 * s, y + 4 * s), 180, 360, fill=O.c((200, 170, 90), q), width=int(4 * K))
        elif tipo == "etiqueta":
            _, x, y, txt, q = it
            w = ancho(txt, 16, "bold") + 24
            x = cl(x, w / 2 + 10, W - w / 2 - 10)
            rect(O, x - w / 2, y - 16, x + w / 2, y + 16, (0, 0, 0), a=0.6 * q, r=16)
            texto(O, txt, x, y, 16, BLANCO, a=q, fuente="bold", sombra=False)
        elif tipo == "sello":
            _, txt, x, y, q = it
            if q > 0:
                s = 1 + 1.4 * (1 - eo3(q))
                w = ancho(txt, 34 * s) + 34 * s
                rect(O, x - w / 2, y - 28 * s, x + w / 2, y + 28 * s, None, a=q, r=8 * s, outline=ROJO, w=5 * s)
                texto(O, txt, x, y, 34 * s, ROJO, a=q, fuente="black", sombra=False)
        elif tipo == "pizarra":
            _, q, t = it
            rect(O, 120, 600, 420, 760, (40, 46, 44), a=q, r=6, outline=(120, 90, 60), w=6)
            txt = "15 dic — 1 a.m. ..."
            n = int(len(txt) * prog(t, 0, 1.2) * q)
            texto(O, txt[:n], 140, 650, 22, TIZA, a=q, fuente="semi", anchor="lm", sombra=False)
            texto(O, "última anotación", 270, 720, 14, (180, 180, 170), a=q, fuente="bold", sombra=False)
        elif tipo == "norma":
            q = it[1]
            rect(O, 60, 780, 480, 830, AMARILLO, a=q, r=25)
            texto(O, "NORMA: NUNCA DEJAR EL FARO SOLO", 270, 805, 17, (20, 20, 20), a=q, fuente="black", sombra=False)
        elif tipo == "pregunta":
            _, txt, y, q = it
            texto(O, txt, 270, y + 20 * (1 - eo3(q)), 40, AMARILLO, a=q, fuente="black")
        elif tipo == "nunca":
            q = it[1]
            texto(O, "NUNCA", 270, 380, 70 * (0.7 + 0.3 * eob(q)), BLANCO, a=q, fuente="black")
            texto(O, "aparecieron los cuerpos", 270, 440, 24, (200, 210, 220), a=q, fuente="black")
        elif tipo == "comentario":
            _, q, t = it
            s = eob(q)
            rect(O, 90, 640 - 40 * s, 450, 640 + 40 * s, BLANCO, a=q, r=40 * s)
            poly(O, [(150, 676), (180, 676), (140, 706)], BLANCO, a=q)
            puntos = "." * (1 + int(t * 3) % 3)
            texto(O, "¿Qué pasó? " + puntos, 270, 640, 26 * s, (30, 30, 30), a=q, fuente="black", sombra=False)


def haz_linterna(img, st):
    if "haz" not in st:
        return img
    bx, by = st["haz"]
    m = Image.new("L", (IW // 4, IH // 4), 0)
    d = ImageDraw.Draw(m)
    k = K / 4
    d.ellipse(((bx - 110) * k, (by - 150) * k, (bx + 110) * k, (by + 150) * k), fill=150)
    m = m.filter(ImageFilter.GaussianBlur(10)).resize((IW, IH), Image.BILINEAR)
    oscuro = Image.eval(img, lambda v: int(v * 0.35))
    luz = Image.eval(img, lambda v: min(255, int(v * 1.25 + 10)))
    return Image.composite(luz, oscuro, m)


def frio(img, k=0.45):
    a = np.asarray(img).astype(np.float32)
    g = a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11
    tint = np.stack([g * 0.82, g * 0.98, g * 1.12 + 6], -1)
    return Image.fromarray(np.clip(a * (1 - k) + tint * k, 0, 255).astype(np.uint8))


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
        v = np.clip(1.2 - r * 1.2, 0.3, 1)
        _VIN = Image.fromarray((v * 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR).convert("RGB")
    return _VIN


EXTERIOR = {"gancho", "subida", "embarcadero", "teoria", "final"}


def render_frame(fr):
    T = fr / FPS
    e = escena_en(T)
    t = T - e["t0"]
    D = e["dur"]
    img = Image.new("RGB", (IW, IH), (0, 0, 0))
    L = Capa(img)
    st = {"overlay": []}
    FUNCS[e["nombre"]](L, e, t, D, T, st)
    z = 1.04 + 0.07 * eio(t / D)
    cw, ch = IW / z, IH / z
    x0, y0 = (IW - cw) / 2, (IH - ch) / 2 + 20 * K
    img = L.img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    img = haz_linterna(img, st)
    if st.get("oscuro"):
        img = Image.blend(img, Image.new("RGB", (IW, IH), (0, 0, 0)), st["oscuro"])
    img = frio(img)
    rl = relampago(T) if e["nombre"] in EXTERIOR else 0
    if rl > 0:
        img = Image.blend(img, Image.new("RGB", (IW, IH), (200, 215, 240)), 0.45 * rl)
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    if st.get("lluvia"):
        lluvia(O, T, st["lluvia"])
    overlays(O, st, T)
    fecha(O, e, t)
    subtitulos(O, T)
    out = O.img
    if T < 0.3:
        out = Image.blend(Image.new("RGB", (IW, IH), (0, 0, 0)), out, T / 0.3)
    if T > TOTAL - 1.0:
        out = Image.blend(out, Image.new("RGB", (IW, IH), (0, 0, 0)), cl((T - (TOTAL - 1.0)) / 1.0))
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


def musica(n):
    """Dron grave inquietante con notas sueltas de piano en menor."""
    tt = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * tt)
    for f, g in ((55, 0.10), (65.4, 0.05), (82.4, 0.04), (77.8, 0.015)):
        out += g * np.sin(2 * np.pi * f * tt + 0.4 * np.sin(2 * np.pi * 0.11 * tt)) * lfo
    notas = [69, 72, 71, 64, 69, 76, 74, 72]
    k = 0
    while k * 2.6 < TOTAL:
        t0 = k * 2.6 + 0.5
        a0 = int(t0 * SR)
        m = min(n - a0, int(3 * SR))
        if m > 0:
            u = np.arange(m) / SR
            f = 440 * 2 ** ((notas[k % len(notas)] - 69) / 12)
            out[a0:a0 + m] += 0.04 * (np.sin(2 * np.pi * f * u) + 0.3 * np.sin(4 * np.pi * f * u)) * np.exp(-u * 1.3)
        k += 1
    return out


def trueno(seed):
    n = int(3.0 * SR)
    u = np.arange(n) / SR
    r = ruido_filtrado(n, 120, seed)
    env = np.exp(-u * 1.2) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * u) ** 2)
    return (r * env * 0.9).astype(np.float32)


def tictac():
    n = int(0.04 * SR)
    u = np.arange(n) / SR
    return (np.sin(2 * np.pi * 3000 * u) * np.exp(-u * 150)).astype(np.float32)


def crujido():
    n = int(1.2 * SR)
    u = np.arange(n) / SR
    f = 180 + 120 * np.sin(2 * np.pi * 1.5 * u)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.15 * np.sin(np.pi * u / 1.2)
    return np.convolve(s, np.ones(20) / 20, mode="same").astype(np.float32)


def mezclar():
    n = int((TOTAL + 0.3) * SR)
    voz = np.zeros(n, np.float32)
    for e in ESC:
        colocar(voz, leer(os.path.join(BUILD, f"voz_{e['i']}.mp3")), e["voz_t0"])
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    mus = musica(n)
    tt = np.arange(n) / SR
    # ambiente de tormenta: viento + lluvia + olas (más bajo en interiores)
    exterior = np.array([1.0 if escena_en(min(x, TOTAL - 0.01))["nombre"] in EXTERIOR else 0.3
                         for x in np.arange(0, TOTAL + 0.3, 0.05)], np.float32)
    exterior = np.convolve(exterior, np.ones(10) / 10, mode="same")
    env_ext = np.interp(tt, np.arange(0, TOTAL + 0.3, 0.05)[:len(exterior)], exterior)
    viento = ruido_filtrado(n, 60, 1) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * tt)) * 0.18
    lluvia_s = ruido_filtrado(n, 3, 2, hp=30) * 0.06
    olas = ruido_filtrado(n, 200, 3) * (0.5 + 0.5 * np.sin(2 * np.pi * tt / 3.0)) ** 3 * 0.35
    amb = (viento + lluvia_s + olas) * env_ext * 0.7
    fx = np.zeros(n, np.float32)
    # truenos tras cada relámpago exterior
    for k in range(int(TOTAL / 3.7) + 1):
        rs = random.Random(k * 7 + 3)
        t0 = k * 3.7 + rs.uniform(0.3, 3.0)
        if rs.random() < 0.55 and t0 < TOTAL and escena_en(t0)["nombre"] in EXTERIOR:
            colocar(fx, trueno(k), t0 + 0.25, 0.5)
    E = {e["nombre"]: e for e in ESC}
    c = E["cocina"]
    t_stop = c["t0"] + wt(c, "reloj") + 0.6
    t = c["t0"] + 0.3
    while t < t_stop:
        colocar(fx, tictac(), t, 0.35)
        t += 0.5
    colocar(fx, crujido(), E["subida"]["t0"] + wt(E["subida"], "puerta") - 0.2, 0.5)
    for nombre, pal in (("tres", "desaparecido"), ("falso", "falsas")):
        e = E[nombre]
        colocar(fx, golpe(), e["t0"] + wt(e, pal) - 0.25, 0.6)
    te = E["teoria"]
    colocar(fx, golpe() * 0.8, te["t0"] + wt(te, "ola") + 0.5, 0.7)
    colocar(fx, trueno(99) * 1.2, te["t0"] + wt(te, "ola") + 0.4, 0.6)
    for j, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(j, 0.5), e["t0"] - 0.25, 0.25)
    env = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.5 * np.clip(env * 12, 0, 1)
    total = voz + (mus + amb + fx) * duck
    total *= np.clip((TOTAL - tt) / 1.0, 0, 1)
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
