"""Reel vertical «Tu tarjeta no tiene batería» (formato «Cómo funciona por dentro»): estilo macro oscuro con
proyección 3D real de la tarjeta y el datáfono, brillo (bloom) y subtítulos con la palabra activa recuadrada.

    python3 voz.py && python3 video.py        -> contactless_reel.mp4
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
SALIDA = os.path.join(AQUI, "contactless_reel.mp4")

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


EXTRA = {"paradoja": 0.4, "pregunta": 0.4, "campo": 0.5, "antena": 0.5, "corriente": 0.5, "respuesta": 0.5, "cerca": 0.6, "dos": 0.5, "codigo": 0.6, "final": 0.8, "cta": 1.6}
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
CLAVE = {"batería", "presta", "energía", "campo", "magnético", "13", "millones", "antena", "corriente", "chip", "curioso",
         "absorbiendo", "parpadeos", "unos", "ceros", "centímetros", "dos", "código", "vez", "parpadeado", "nunca", "sígueme"}


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
            for seq, num in ((["trece", "millones"], "13 millones"),):
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



def flecha_suelo(L, x, y, s, col, a=1.0, dx=1.0, dy=0.0):
    px, py = -dy, dx
    tip = (x + dx * s, y + dy * s)
    i1 = (x - dx * s * 0.6 + px * s * 0.8, y - dy * s * 0.6 + py * s * 0.8)
    i2 = (x - dx * s * 0.6 - px * s * 0.8, y - dy * s * 0.6 - py * s * 0.8)
    linea(L, [i1, tip, i2], col, w=max(2, s * 0.28), a=a)



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




# =====================================================================================================
# Reel «Tu tarjeta no tiene batería» · estilo macro oscuro con proyección 3D real y brillo (bloom)
# =====================================================================================================
CIAN = (96, 206, 255)
ORO = (255, 198, 96)
OK = (80, 224, 140)
GRIS = (150, 156, 170)
TINTA = (226, 230, 238)


def rot(p, rx=0.0, ry=0.0, rz=0.0):
    x, y, z = p
    if rz:
        c, s = math.cos(rz), math.sin(rz)
        x, y = x * c - y * s, x * s + y * c
    if rx:
        c, s = math.cos(rx), math.sin(rx)
        y, z = y * c - z * s, y * s + z * c
    if ry:
        c, s = math.cos(ry), math.sin(ry)
        x, z = x * c + z * s, -x * s + z * c
    return x, y, z


class Cam:
    def __init__(self, yaw=0.0, pitch=0.0, dist=300.0, f=620.0, cx=270.0, cy=520.0, mira=(0, 0, 0)):
        self.yaw, self.pitch, self.dist, self.f, self.cx, self.cy, self.mira = yaw, pitch, dist, f, cx, cy, mira

    def __call__(self, p):
        x, y, z = (p[0] - self.mira[0], p[1] - self.mira[1], p[2] - self.mira[2])
        x, y, z = rot((x, y, z), 0, self.yaw, 0)
        x, y, z = rot((x, y, z), self.pitch, 0, 0)
        z += self.dist
        z = max(z, 1.0)
        return self.cx + self.f * x / z, self.cy - self.f * y / z


class Obj:
    """Objeto plano en el espacio: (u, v, w) locales -> mundo."""

    def __init__(self, pos=(0, 0, 0), rx=0.0, ry=0.0, rz=0.0):
        self.pos, self.rx, self.ry, self.rz = pos, rx, ry, rz

    def __call__(self, u, v, w=0.0):
        x, y, z = rot((u, v, w), self.rx, self.ry, self.rz)
        return x + self.pos[0], y + self.pos[1], z + self.pos[2]


def area(pts):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1])) / 2


def rrect_uv(w, h, r, n=6):
    """Contorno de un rectángulo redondeado centrado (lista de (u, v))."""
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                       (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def poli3(L, cam, ob, uv, col, a=1.0, w=0.0):
    pts = [cam(ob(u, v, w)) for u, v in uv]
    poly(L, pts, col, a)
    return pts


def linea3(L, cam, ob, uv, col, ancho=1.5, a=1.0, w=0.0, cerrada=False):
    pts = [cam(ob(u, v, w)) for u, v in uv]
    if cerrada:
        pts = pts + pts[:1]
    linea(L, pts, col, w=ancho, a=a)
    return pts


# ------------------------------------------------------------------ tarjeta
CW, CH = 85.6, 54.0
CHIP = (-26.0, 4.0)
CONTORNO = rrect_uv(CW, CH, 3.2)


def espiral():
    """Antena: 5 vueltas siguiendo el borde, de fuera a dentro, que acaban en el chip."""
    pts = []
    for i in range(5):
        d = 4.0 + i * 2.1
        for (u, v) in rrect_uv(CW - 2 * d, CH - 2 * d, max(1.0, 3.2 - i * 0.4), 4)[:-1]:
            pts.append((u, v))
    pts.append(CHIP)
    return pts


ESPIRAL = espiral()
_LE = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(ESPIRAL, ESPIRAL[1:])]
LESP = sum(_LE)


def punto_esp(d):
    d %= LESP
    for (a, b), l in zip(zip(ESPIRAL, ESPIRAL[1:]), _LE):
        if d <= l:
            k = d / l
            return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        d -= l
    return ESPIRAL[-1]


def tarjeta(L, G, cam, ob, T, rayosx=0.0, corriente=0.0, chip_on=0.0, a=1.0, tinte=None):
    """Tarjeta en 3D. rayosx: 0 opaca -> 1 transparente con la antena a la vista."""
    frente = poli3(L, cam, ob, CONTORNO, (70, 76, 92), a=a, w=-0.8)   # canto
    caras = [cam(ob(u, v, 0.8)) for u, v in CONTORNO]
    cara_visible = area(caras) < 0
    base = tinte or (34, 38, 50)
    opa = a * (1 - 0.82 * rayosx)
    poly(L, caras, base, opa)
    # brillo diagonal
    brillo = [(-CW / 2, CH / 2), (-CW / 2 + 26, CH / 2), (-CW / 2 + 52, -CH / 2), (-CW / 2 + 26, -CH / 2)]
    off = (T * 18) % 160 - 40
    poli3(L, cam, ob, [(cl(u + off, -CW / 2 + 2, CW / 2 - 2), v) for u, v in brillo], (255, 255, 255), a=0.05 * opa, w=0.9)
    linea(L, caras + caras[:1], (120, 128, 150), w=1.2, a=a * 0.8)
    _ = frente, cara_visible
    if opa > 0.05:
        # chip de contactos, símbolo sin contacto y número
        cu, cv = CHIP
        poli3(L, cam, ob, rrect_uv(11, 9, 1.4), (212, 172, 92), a=opa, w=0.9)
        for k in (-1, 1):
            linea3(L, cam, ob, [(cu - 5.5, cv + k * 1.6), (cu + 5.5, cv + k * 1.6)], (150, 110, 50), 1.0, opa, 0.95)
        pts = [(u + cu, v + cv) for u, v in rrect_uv(11, 9, 1.4)]
        _ = pts
        for k in range(4):
            r = 2.5 + k * 2.2
            arco = [(30 + r * math.cos(math.radians(a_)) - 6, 8 + r * math.sin(math.radians(a_))) for a_ in range(-50, 51, 10)]
            linea3(L, cam, ob, arco, TINTA, 1.4, opa * 0.85, 0.95)
        p = cam(ob(-34, -14, 0.95))
        q = cam(ob(20, -14, 0.95))
        texto(L, "••••  ••••  ••••  4821", (p[0] + q[0]) / 2, (p[1] + q[1]) / 2, 10, TINTA, a=opa * 0.8, fuente="mono",
              sombra=False)
    if rayosx > 0:
        col = mezcla(GRIS, ORO, cl(corriente))
        linea3(L, cam, ob, ESPIRAL, col, 1.6, a * rayosx, 0.0)
        if corriente > 0:
            linea3(G, cam, ob, ESPIRAL, ORO, 1.6, a * rayosx * corriente * 0.9, 0.0)
            for k in range(26):
                d = (T * 140 + k * LESP / 26) % LESP
                u, v = punto_esp(d)
                x, y = cam(ob(u, v, 0))
                circ(G, x, y, 2.2, fill=(255, 236, 190), a=a * corriente)
        # chip (dado de silicio)
        cu, cv = CHIP
        poli3(L, cam, ob, [(cu - 4, cv - 4), (cu + 4, cv - 4), (cu + 4, cv + 4), (cu - 4, cv + 4)], (60, 64, 80),
              a=a * rayosx)
        if chip_on > 0:
            puls = 0.7 + 0.3 * math.sin(T * 14)
            poli3(G, cam, ob, [(cu - 4, cv - 4), (cu + 4, cv - 4), (cu + 4, cv + 4), (cu - 4, cv + 4)], ORO,
                  a=a * chip_on * puls)
            poli3(L, cam, ob, [(cu - 4, cv - 4), (cu + 4, cv - 4), (cu + 4, cv + 4), (cu - 4, cv + 4)], ORO,
                  a=a * chip_on * puls)


# ------------------------------------------------------------------ datáfono (tumbado, pantalla hacia arriba)
TW, TH, TD = 74.0, 150.0, 16.0


def datafono(L, G, cam, ob, T, pantalla="", col_p=TINTA, a=1.0, onda=0.0):
    caja_uv = rrect_uv(TW, TH, 9)
    top = [cam(ob(u, v, TD)) for u, v in caja_uv]
    bot = [cam(ob(u, v, 0)) for u, v in caja_uv]
    # lados visibles: cuadriláteros entre contorno inferior y superior
    for i in range(len(caja_uv)):
        j = (i + 1) % len(caja_uv)
        quad = [bot[i], bot[j], top[j], top[i]]
        if area(quad) < 0:
            poly(L, quad, (28, 30, 38), a)
    poly(L, top, (46, 50, 62), a)
    linea(L, top + top[:1], (90, 96, 116), w=1.2, a=a)
    # pantalla
    scr = [(-28, 20), (28, 20), (28, 60), (-28, 60)]
    poli3(L, cam, ob, scr, (12, 16, 22), a=a, w=TD + 0.2)
    if pantalla:
        c = cam(ob(0, 40, TD + 0.3))
        texto(L, pantalla, c[0], c[1], 11, col_p, a=a, fuente="mono", sombra=False)
        texto(G, pantalla, c[0], c[1], 11, col_p, a=a * 0.6, fuente="mono", sombra=False)
    # teclado
    for fila in range(4):
        for colm in range(3):
            u, v = -20 + colm * 20, -8 - fila * 14
            poli3(L, cam, ob, [(x + u, y + v) for x, y in rrect_uv(14, 9, 2, 2)],
                  (70, 76, 92) if (fila, colm) != (3, 2) else (40, 150, 90), a=a, w=TD + 0.3)
    # símbolo sin contacto en la parte alta
    for k in range(3):
        r = 3 + k * 2.6
        arco = [(r * math.cos(math.radians(a_)) - 4, 66 + r * math.sin(math.radians(a_))) for a_ in range(-50, 51, 10)]
        linea3(L, cam, ob, arco, TINTA, 1.2, a * 0.7, TD + 0.3)
    if onda > 0:
        c = cam(ob(0, 40, TD + 0.3))
        _ = c


def anillos(L, G, cam, ob, T, intensidad=1.0, alcance=110.0, centro=(0, 40), n=7, invierte=True):
    """Campo magnético: anillos que suben desde la zona de la antena del datáfono."""
    if intensidad <= 0:
        return
    for k in range(n):
        h = ((T * 38 + k * alcance / n) % alcance)
        fade = (1 - h / alcance) ** 1.4
        r = 18 + h * 0.45
        uv = [(centro[0] + r * math.cos(a_ * math.pi / 18), centro[1] + r * math.sin(a_ * math.pi / 18)) for a_ in range(37)]
        pts = [cam(ob(u, v, TD + 4 + h)) for u, v in uv]
        linea(L, pts, CIAN, w=1.3, a=intensidad * fade * 0.8)
        linea(G, pts, CIAN, w=1.8, a=intensidad * fade * 0.6)
        if invierte:
            sentido = 1 if int(T * 30 + k) % 2 else -1
            for a_ in (0, 12, 24):
                ang = a_ * math.pi / 18
                u0, v0 = centro[0] + r * math.cos(ang), centro[1] + r * math.sin(ang)
                u1, v1 = centro[0] + r * math.cos(ang + 0.25 * sentido), centro[1] + r * math.sin(ang + 0.25 * sentido)
                p0, p1 = cam(ob(u0, v0, TD + 4 + h)), cam(ob(u1, v1, TD + 4 + h))
                dx, dy = p1[0] - p0[0], p1[1] - p0[1]
                nrm = math.hypot(dx, dy) or 1
                dx, dy = dx / nrm, dy / nrm
                flecha_suelo(L, p1[0], p1[1], 4, CIAN, a=intensidad * fade, dx=dx, dy=dy)


def rotulo(L, x, y, tx, ty, txt, a=1.0, col=TINTA):
    """Etiqueta técnica: punto + línea fina + texto en mayúsculas (estilo plano de ingeniería)."""
    if a <= 0:
        return
    circ(L, x, y, 3, fill=col, a=a)
    linea(L, [(x, y), (tx, ty)], col, w=1, a=a * 0.7)
    wt_ = ancho(txt, 12, "mono")
    if tx >= x:
        xt = min(tx + 6, W - 14 - wt_)
        texto(L, txt, xt, ty, 12, col, a=a, fuente="mono", anchor="lm", sombra=False)
    else:
        xt = max(tx - 6, 14 + wt_)
        texto(L, txt, xt, ty, 12, col, a=a, fuente="mono", anchor="rm", sombra=False)


# ------------------------------------------------------------------ fondo
_FONDO = None


def fondo():
    global _FONDO
    if _FONDO is None:
        sw, sh = IW // 6, IH // 6
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        r = np.sqrt(((xx - sw / 2) / sw) ** 2 + ((yy - sh * 0.48) / sh) ** 2 * 0.7)
        k = np.clip(1 - r * 1.6, 0, 1)[..., None]
        c0 = np.array([7, 8, 11], np.float32)
        c1 = np.array([30, 33, 44], np.float32)
        img = (c0 + (c1 - c0) * k).astype(np.uint8)
        _FONDO = Image.fromarray(img).resize((IW, IH), Image.BILINEAR)
    return _FONDO


def polvo(L, T, n=40):
    rs = random.Random(5)
    for k in range(n):
        x = rs.uniform(0, W)
        y = (rs.uniform(0, H) - T * rs.uniform(3, 9)) % H
        circ(L, x, y, rs.uniform(0.6, 1.6), fill=(200, 210, 230), a=0.15 + 0.1 * math.sin(T + k))


def suavizar(c0, c1, k):
    return Cam(*[lerp(getattr(c0, n), getattr(c1, n), k) for n in ("yaw", "pitch", "dist", "f", "cx", "cy")],
               mira=tuple(lerp(a, b, k) for a, b in zip(c0.mira, c1.mira)))


# vista estándar «tarjeta sobre datáfono»
def cam_mesa(T, yaw=-0.5, pitch=0.62, dist=330, cy=560, mira=(0, 40, -40), zoom=1.3):
    return Cam(yaw + 0.04 * math.sin(T * 0.4), pitch, dist / zoom, 640, 270, cy, mira)


def ob_terminal():
    return Obj((0, 0, 0), rx=-math.pi / 2)


def ob_tarjeta_sobre(h, giro=0.0, dx=0.0, dz=0.0):
    return Obj((dx, h + TD, -40 + dz), rx=-math.pi / 2, rz=giro)


# ================================================================== escenas
def esc_paradoja(L, G, e, t, D, T, st):
    cam = Cam(-0.35 + 0.25 * eio(t / D), 0.18, 160, 640, 270, 520)
    ob = Obj((0, 0, 0), rx=0.25 + 0.05 * math.sin(T), ry=0.5 * math.sin(T * 0.5), rz=-0.12)
    tarjeta(L, G, cam, ob, T)
    for j, (pal, txt, (u, v), (tx, ty)) in enumerate((("batería", "BATERÍA", (10, -8), (430, 640)),
                                                     ("cable", "CABLES", (-40, 20), (90, 380)),
                                                     ("botón", "BOTONES", (36, 20), (440, 400)))):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            x, y = cam(ob(u, v, 1))
            rotulo(L, x, y, tx, ty, txt + "  ✗", a=q, col=(255, 120, 120))
    qh = prog(t, wt(e, "habla") - 0.2, 0.35)
    if qh > 0:
        for k in range(3):
            u = (t * 1.2 + k / 3) % 1
            circ(G, 270, 520, 60 + 160 * u, outline=OK, w=2, a=qh * (1 - u))
        rotulo(L, 270, 720, 330, 790, "BIP · PAGO ACEPTADO", a=qh, col=OK)
    st["sin_ui"] = True


def esc_pregunta(L, G, e, t, D, T, st):
    cam = Cam(0.3 - 0.1 * eio(t / D), 0.2, 145 - 20 * eio(t / D), 640, 270, 500)
    ob = Obj((0, 0, 0), rx=0.25, ry=0.4 + 0.1 * math.sin(T * 0.5), rz=-0.1)
    tarjeta(L, G, cam, ob, T)
    # icono de batería vacía
    x0, y0 = 220, 720
    rect(L, x0, y0, x0 + 90, y0 + 40, None, outline=GRIS, w=3, r=6)
    rect(L, x0 + 90, y0 + 12, x0 + 98, y0 + 28, GRIS, r=2)
    texto(L, "0 %", x0 + 45, y0 + 20, 16, (255, 120, 120), fuente="mono", sombra=False)
    qp = prog(t, wt(e, "presta") - 0.4, 0.6)
    if qp > 0:
        # energía dorada que llega desde abajo (el datáfono)
        for k in range(10):
            u = (t * 0.9 + k / 10) % 1
            x = 270 + 60 * math.sin(k * 2.3 + T)
            y = lerp(960, 560, u)
            circ(G, x, y, 3, fill=ORO, a=qp * math.sin(u * math.pi))
            circ(L, x, y, 2, fill=ORO, a=qp * math.sin(u * math.pi))
        rotulo(L, 270, 860, 330, 900, "ENERGÍA DEL DATÁFONO", a=qp, col=ORO)


def esc_campo(L, G, e, t, D, T, st):
    cam = cam_mesa(T, yaw=-0.55 + 0.2 * eio(t / D), dist=380 - 60 * eio(t / D), zoom=1.6, cy=620)
    datafono(L, G, cam, ob_terminal(), T, pantalla="ACERQUE TARJETA")
    q = prog(t, wt(e, "campo") - 0.3, 0.8)
    anillos(L, G, cam, ob_terminal(), T, intensidad=q)
    qn = prog(t, wt(e, "trece") - 0.3, 0.4)
    if qn > 0:
        n = int(13_560_000 * eo3(prog(t, wt(e, "trece") - 0.3, 1.4)))
        txt = f"{n:,}".replace(",", ".")
        texto(L, txt, 270, 360, 34, CIAN, a=qn, fuente="mono")
        texto(G, txt, 270, 360, 34, CIAN, a=qn * 0.5, fuente="mono")
        texto(L, "CAMBIOS DE SENTIDO POR SEGUNDO", 270, 396, 12, GRIS, a=qn, fuente="mono", sombra=False)
    if q > 0:
        x, y = cam(ob_terminal()(30, 40, TD + 60))
        rotulo(L, x, y, 440, 470, "CAMPO MAGNÉTICO", a=q, col=CIAN)


def esc_antena(L, G, e, t, D, T, st):
    k = eio(prog(t, 0, 1.2))
    cam = Cam(lerp(-0.2, 0.0, k), lerp(0.2, 0.05, k), lerp(170, 125, k), 640, 270, 560)
    ob = Obj((0, 0, 0), rx=lerp(0.25, 0.08, k), ry=lerp(0.3, 0.0, k), rz=lerp(-0.1, 0.0, k))
    rx = eio(prog(t, wt(e, "borde") - 0.6, 0.8))
    tarjeta(L, G, cam, ob, T, rayosx=rx)
    if rx > 0.3:
        dibujado = eio(prog(t, wt(e, "enrollado") - 0.3, 1.2))
        if dibujado < 1:
            n = int(len(ESPIRAL) * dibujado)
            if n > 1:
                linea3(G, cam, ob, ESPIRAL[:n], ORO, 2.0, 0.9, 0.0)
        qa = prog(t, wt(e, "antena") - 0.3, 0.3)
        x, y = cam(ob(CW / 2 - 5, 0, 0))
        rotulo(L, x, y, 470, 400, "ANTENA · 5 VUELTAS", a=qa, col=ORO)
        x, y = cam(ob(*CHIP, 0))
        rotulo(L, x, y, 80, 700, "CHIP", a=qa, col=TINTA)


def esc_corriente(L, G, e, t, D, T, st):
    cam = cam_mesa(T, yaw=-0.35, pitch=0.5, dist=300, cy=600, mira=(0, 50, -40))
    ot = ob_terminal()
    datafono(L, G, cam, ot, T, pantalla="ACERQUE TARJETA")
    llega = eo3(prog(t, 0, 1.4))
    h = lerp(140, 26, llega)
    anillos(L, G, cam, ot, T, intensidad=1.0, alcance=h + 30)
    qc = prog(t, wt(e, "corriente") - 0.3, 0.6)
    qd = prog(t, wt(e, "despertar") - 0.2, 0.4)
    tarjeta(L, G, cam, ob_tarjeta_sobre(h), T, rayosx=0.9, corriente=qc, chip_on=qd)
    if qd > 0:
        x, y = cam(ob_tarjeta_sobre(h)(*CHIP, 0))
        rotulo(L, x, y, 90, 420, "CHIP: ENCENDIDO", a=qd, col=ORO)
    if qc > 0:
        texto(L, f"{0.3 * qc + 0.02 * math.sin(T * 20):.2f} mA", 400, 420, 20, ORO, a=qc, fuente="mono")


def onda(O, G, x0, y0, w, h, T, bits, prog_bits, col=CIAN, caos=0.0):
    """Señal vista por el datáfono: portadora con bajadas cuando el chip absorbe más."""
    pts = []
    n = 360
    nb = len(bits)
    for i in range(n + 1):
        u = i / n
        b = min(nb - 1, int(u * nb))
        activo = u <= prog_bits
        amp = 1.0
        if activo and bits[b] == "1":
            amp = 0.55
        if caos:
            amp *= 1 - caos * 0.5 * (0.5 + 0.5 * math.sin(u * 47 + T * 9) * math.sin(u * 13))
        y = y0 + h / 2 * amp * math.sin(u * 160 + T * 40)
        pts.append((x0 + w * u, y))
    linea(O, pts, col, w=1.2, a=0.9)
    linea(G, pts, col, w=1.6, a=0.4)
    for b, bit in enumerate(bits):
        u = (b + 0.5) / nb
        if u <= prog_bits:
            texto(O, bit, x0 + w * u, y0 + h / 2 + 22, 18, ORO if bit == "1" else TINTA, fuente="mono", sombra=False)


def esc_respuesta(L, G, e, t, D, T, st):
    cam = cam_mesa(T, yaw=-0.3 + 0.1 * eio(t / D), pitch=0.55, dist=290, cy=700, mira=(0, 50, -40))
    ot = ob_terminal()
    datafono(L, G, cam, ot, T, pantalla="LEYENDO…")
    anillos(L, G, cam, ot, T, intensidad=0.8, alcance=60)
    bits = "1011001110"
    t_ab = wt(e, "absorbiendo") - 0.2
    pb = prog(t, t_ab, wt(e, "ceros") - t_ab)
    b = min(len(bits) - 1, int(pb * len(bits)))
    absorbe = pb > 0 and bits[b] == "1" and pb < 1
    tarjeta(L, G, cam, ob_tarjeta_sobre(26), T, rayosx=0.9, corriente=1.0 if absorbe else 0.45, chip_on=1.0)
    qf = prog(t, wt(e, "fuerza") - 0.3, 0.3)
    if qf > 0 and pb <= 0:
        sello_t(L, "NO PUEDE EMITIR", 270, 420, qf, col=(255, 120, 120), size=24)
    if pb > 0:
        rect(L, 40, 330, 500, 470, (0, 0, 0), a=0.55, r=14)
        texto(L, "LO QUE «VE» EL DATÁFONO", 270, 346, 12, GRIS, fuente="mono", sombra=False)
        onda(L, G, 60, 395, 420, 70, T, bits, pb)


def esc_cerca(L, G, e, t, D, T, st):
    cam = cam_mesa(T, yaw=-0.75, pitch=0.32, dist=380, cy=660, mira=(0, 60, -40), zoom=1.15)
    ot = ob_terminal()
    datafono(L, G, cam, ot, T, pantalla="ACERQUE TARJETA")
    sube = eio(prog(t, wt(e, "centímetros") - 1.2, 1.6))
    h = lerp(22, 120, sube)
    anillos(L, G, cam, ot, T, intensidad=1.0, alcance=60)
    on = cl(1 - (h - 40) / 25)
    tarjeta(L, G, cam, ob_tarjeta_sobre(h), T, rayosx=0.9, corriente=on, chip_on=on)
    # regla vertical
    x_r = 470
    for cm_ in range(0, 11, 2):
        x, y = cam(Obj((80, 0, -40))(0, cm_ * 10 + TD, 0))
        linea(L, [(x - 6, y), (x + 6, y)], GRIS, w=1.2)
        texto(L, f"{cm_} cm", x + 12, y, 11, GRIS, fuente="mono", anchor="lm", sombra=False)
    pc = cam(Obj((80, 0, -40))(0, h + TD, 0))
    circ(L, pc[0], pc[1], 5, fill=ORO if on > 0.5 else (255, 120, 120))
    _ = x_r
    # medidor de campo
    texto(L, "ENERGÍA QUE LLEGA", 270, 362, 12, GRIS, fuente="mono", sombra=False)
    rect(L, 120, 380, 420, 400, (40, 44, 56), r=10)
    v = cl((60 - h) / 38, 0.03, 1)
    rect(L, 122, 382, 122 + 296 * v, 398, mezcla((255, 120, 120), OK, v), r=8)
    if on < 0.2:
        x, y = cam(ob_tarjeta_sobre(h)(*CHIP, 0))
        rotulo(L, x, y, 90, 470, "CHIP: APAGADO", a=1 - on, col=(255, 120, 120))


def esc_dos(L, G, e, t, D, T, st):
    cam = cam_mesa(T, yaw=-0.4, pitch=0.55, dist=320, cy=680, mira=(0, 50, -40))
    ot = ob_terminal()
    q2 = prog(t, wt(e, "responden") - 0.3, 0.4)
    datafono(L, G, cam, ot, T, pantalla="UNA SOLA TARJETA" if q2 > 0.5 else "ACERQUE TARJETA",
             col_p=(255, 120, 120) if q2 > 0.5 else TINTA)
    anillos(L, G, cam, ot, T, intensidad=0.8, alcance=70)
    entra = eo3(prog(t, 0, 1.2))
    h = lerp(150, 26, entra)
    tarjeta(L, G, cam, ob_tarjeta_sobre(h, giro=0.08, dx=-6), T, rayosx=0.9, corriente=q2, chip_on=q2, tinte=(60, 30, 40))
    tarjeta(L, G, cam, ob_tarjeta_sobre(h + 8, giro=-0.06, dx=6, dz=-8), T, rayosx=0.9, corriente=q2, chip_on=q2)
    if q2 > 0:
        rect(L, 40, 330, 500, 470, (0, 0, 0), a=0.55, r=14)
        texto(L, "DOS RESPUESTAS A LA VEZ", 270, 346, 12, (255, 120, 120), fuente="mono", sombra=False)
        onda(L, G, 60, 405, 420, 70, T, "??????????", 0, col=(255, 140, 140), caos=q2)
        texto(L, "?", 400, 560 - 8 * math.sin(t * 6), 60 * eob(prog(t, wt(e, "cuál") - 0.3, 0.3)) + 1, (255, 120, 120),
              a=prog(t, wt(e, "cuál") - 0.3, 0.3), fuente="black")


def esc_codigo(L, G, e, t, D, T, st):
    cam = cam_mesa(T, yaw=-0.45, pitch=0.55, dist=340, cy=780, mira=(0, 50, -40))
    datafono(L, G, cam, ob_terminal(), T, pantalla="APROBADO", col_p=OK)
    tarjeta(L, G, cam, ob_tarjeta_sobre(26), T, rayosx=0.0)
    filas = [("PAGO 1", "7F3A·91C2", "✓", OK, "código"), ("COPIA", "7F3A·91C2", "✗", (255, 120, 120), "solo"),
             ("PAGO 2", "B21E·04D7", "✓", OK, "vez")]
    rect(L, 50, 330, 490, 520, (0, 0, 0), a=0.6 * prog(t, wt(e, "código") - 0.6, 0.3), r=16)
    for j, (et, cod, marca, col, pal) in enumerate(filas):
        q = prog(t, wt(e, pal) - 0.35, 0.3)
        if q <= 0:
            continue
        y = 370 + j * 56
        texto(L, et, 80, y, 15, GRIS, a=q, fuente="mono", anchor="lm", sombra=False)
        texto(L, cod, 290, y, 22, TINTA, a=q, fuente="mono", sombra=False)
        texto(L, marca, 450, y, 26 * eob(q) + 1, col, a=q, fuente="sym", sombra=False)
        texto(G, marca, 450, y, 26, col, a=q * 0.6, fuente="sym", sombra=False)
        if j == 1:
            linea(L, [(200, y + 2), (380, y + 2)], (255, 120, 120), w=3, a=q)


def esc_final(L, G, e, t, D, T, st):
    k = eio(t / D)
    cam = cam_mesa(T, yaw=-0.5 + 0.35 * k, pitch=0.6, dist=330 - 70 * k, cy=560, mira=(0, 50, -40))
    ot = ob_terminal()
    qp = prog(t, wt(e, "parpadeado") - 0.3, 0.4)
    datafono(L, G, cam, ot, T, pantalla="✓")
    anillos(L, G, cam, ot, T, intensidad=1.0, alcance=50)
    parp = 0.5 + 0.5 * math.sin(T * 22) if qp > 0 else 0.6
    tarjeta(L, G, cam, ob_tarjeta_sobre(26), T, rayosx=0.9, corriente=parp, chip_on=1.0)


def esc_cta(L, G, e, t, D, T, st):
    if t > D - 1.1:
        esc_paradoja(L, G, ESC[0], 0.05, ESC[0]["dur"], T, st)
        st["sin_ui"] = True
        return
    cam = Cam(-0.2, 0.15, 170, 640, 270, 660)
    ob = Obj((0, 0, 0), rx=0.25, ry=0.6 * math.sin(T * 0.6), rz=-0.12)
    tarjeta(L, G, cam, ob, T)
    st["overlay"].append(("cta", prog(t, wt(e, "Sígueme") - 0.2, 0.35), prog(t, wt(e, "envíaselo") - 0.2, 0.35)))


FUNCS = {"paradoja": esc_paradoja, "pregunta": esc_pregunta, "campo": esc_campo, "antena": esc_antena,
         "corriente": esc_corriente, "respuesta": esc_respuesta, "cerca": esc_cerca, "dos": esc_dos, "codigo": esc_codigo,
         "final": esc_final, "cta": esc_cta}


def overlays(O, st, T):
    for it in st["overlay"]:
        if it[0] == "cta":
            _, qs, qe = it
            if qs > 0:
                s = eob(qs)
                rect(O, 270 - 120 * s, 380, 270 + 120 * s, 432, (254, 44, 85), a=qs, r=26)
                texto(O, "+ SEGUIR", 270, 406, 22 * s, BLANCO, a=qs, fuente="black", sombra=False)
            if qe > 0:
                s = eob(qe)
                rect(O, 270 - 150 * s, 450, 270 + 150 * s, 502, (255, 255, 255), a=qe * 0.12, r=26,
                     outline=(255, 255, 255), w=2)
                texto(O, "ENVÍASELO  ↗", 270, 476, 20 * s, BLANCO, a=qe, fuente="sym", sombra=False)


def subtitulos(O, T):
    """Estilo del reel: frase pequeña arriba, palabras futuras tenues y la activa en un recuadro."""
    for ini, fin, bloque in SUBS:
        if ini <= T < fin:
            size = 30
            f_w = [ancho(w[0], size, "xbold") for w in bloque]
            esp = ancho(" ", size, "xbold")
            total = sum(f_w) + esp * (len(f_w) - 1)
            lineas = [list(range(len(bloque)))]
            if total > 440:
                lineas = [list(range(len(bloque) - 1)), [len(bloque) - 1]]
            y0 = 128
            for li, idxs in enumerate(lineas):
                tw = sum(f_w[i] for i in idxs) + esp * (len(idxs) - 1)
                x = 270 - tw / 2
                for i in idxs:
                    w, t0, t1 = bloque[i]
                    dicha = T >= t0
                    activa = t0 <= T < t1 + 0.12
                    y = y0 + li * 40
                    if activa:
                        rect(O, x - 6, y - 21, x + f_w[i] + 6, y + 21, (90, 170, 255), a=0.22, r=8,
                             outline=(140, 200, 255), w=1.6)
                    limpio = w.lower().strip("¿?¡!.,:")
                    col = ORO if limpio in CLAVE and dicha else (TINTA if dicha else GRIS)
                    texto(O, w, x + f_w[i] / 2, y, size, col, a=1.0 if dicha else 0.35, fuente="xbold", sombra=False)
                    x += f_w[i] + esp
            break


def bloom(G):
    g = G.resize((IW // 6, IH // 6), Image.BILINEAR)
    g1 = g.filter(ImageFilter.GaussianBlur(3)).resize((IW, IH), Image.BILINEAR)
    g2 = g.filter(ImageFilter.GaussianBlur(14)).resize((IW, IH), Image.BILINEAR)
    return ImageChops.add(g1, g2)


def render_frame(fr):
    T = fr / FPS
    e = escena_en(T)
    t = T - e["t0"]
    D = e["dur"]
    base = fondo().copy()
    L = Capa(base)
    G = Capa(Image.new("RGB", (IW, IH), (0, 0, 0)))
    st = {"overlay": []}
    polvo(L, T)
    FUNCS[e["nombre"]](L, G, e, t, D, T, st)
    img = ImageChops.add(L.img, bloom(G.img))
    img = ImageChops.add(img, G.img.point(lambda v: v // 2))
    z = 1.02 + 0.02 * math.sin(T * 0.5)
    cw, ch = IW / z, IH / z
    x0 = (IW - cw) / 2 + 3 * K * math.sin(T * 0.7)
    y0 = (IH - ch) / 2 + 3 * K * math.cos(T * 0.6)
    img = img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    # transición: fundido corto entre escenas
    if t < 0.18 and e["i"] > 0:
        img = Image.blend(Image.new("RGB", (IW, IH), (6, 7, 9)), img, t / 0.18)
    O = Capa(img)
    overlays(O, st, T)
    subtitulos(O, T)
    return O.img.resize((OW, OH), Image.LANCZOS).tobytes()


def musica(n):
    """Ambiente electrónico suave: pad de acordes + pulso tenue + arpegio fino."""
    out = np.zeros(n, np.float32)
    tt = np.arange(n) / SR
    acordes = [[50, 57, 62, 65], [46, 53, 58, 62], [48, 55, 60, 64], [45, 52, 57, 60]]
    dur = 60 / 84 * 4
    k = 0
    while k * dur < TOTAL + dur:
        ac = acordes[k % 4]
        m = int(dur * 1.3 * SR)
        u = np.arange(m) / SR
        env = np.clip(u / 0.8, 0, 1) * np.clip((dur * 1.3 - u) / 1.0, 0, 1)
        s = np.zeros(m, np.float32)
        for nn in ac:
            f = nota(nn)
            s += (np.sin(2 * np.pi * f * u) + 0.3 * np.sin(2 * np.pi * f * 2.003 * u)).astype(np.float32)
        colocar(out, (s * env * 0.012).astype(np.float32), k * dur)
        for j in range(8):
            f = nota(ac[j % 4] + 24)
            mm = int(0.25 * SR)
            uu = np.arange(mm) / SR
            colocar(out, (np.sin(2 * np.pi * f * uu) * np.exp(-uu * 14) * 0.018).astype(np.float32), k * dur + j * dur / 8)
        k += 1
    out += (0.025 * np.sin(2 * np.pi * 41 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * tt * 84 / 60))).astype(np.float32)
    return out


def zumbido(dur, f=220):
    m = int(dur * SR)
    u = np.arange(m) / SR
    s = np.sin(2 * np.pi * f * u) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * u)) + 0.3 * np.sin(2 * np.pi * f * 3 * u)
    env = np.clip(u / 0.3, 0, 1) * np.clip((dur - u) / 0.4, 0, 1)
    return (s * env * 0.12).astype(np.float32)


def bip():
    m = int(0.35 * SR)
    u = np.arange(m) / SR
    return (np.sin(2 * np.pi * 1760 * u) * (u < 0.3) * np.clip((0.3 - u) / 0.02, 0, 1) * 0.25).astype(np.float32)


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
    fx = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    p = E["paradoja"]
    for pal in ("batería", "cable", "botón"):
        colocar(fx, tic(), p["t0"] + wt(p, pal) - 0.2, 0.5)
    colocar(fx, bip(), p["t0"] + wt(p, "habla") - 0.15, 0.7)
    pr = E["pregunta"]
    colocar(fx, whoosh(4, 0.8), pr["t0"] + wt(pr, "presta") - 0.4, 0.4)
    c = E["campo"]
    colocar(fx, zumbido(c["dur"] - wt(c, "campo") + 0.3), c["t0"] + wt(c, "campo") - 0.3, 0.6)
    for k in range(10):
        colocar(fx, tic() * 0.5, c["t0"] + wt(c, "trece") - 0.3 + k * 0.14, 0.4)
    a = E["antena"]
    colocar(fx, whoosh(7, 1.0), a["t0"] + wt(a, "borde") - 0.6, 0.4)
    colocar(fx, pop(), a["t0"] + wt(a, "antena") - 0.3, 0.4)
    co = E["corriente"]
    colocar(fx, zumbido(co["dur"], 180), co["t0"], 0.5)
    colocar(fx, golpe() * 0.4, co["t0"] + wt(co, "despertar") - 0.2, 0.5)
    r = E["respuesta"]
    colocar(fx, zumbido(r["dur"], 200), r["t0"], 0.35)
    t_ab = wt(r, "absorbiendo") - 0.2
    span = wt(r, "ceros") - t_ab
    for k in range(10):
        colocar(fx, tic() * (0.7 if "1011001110"[k] == "1" else 0.3), r["t0"] + t_ab + span * k / 10, 0.5)
    ce = E["cerca"]
    colocar(fx, zumbido(2.0, 150), ce["t0"], 0.4)
    d = E["dos"]
    colocar(fx, zumbido(d["dur"] - wt(d, "responden") + 0.3, 233) + zumbido(d["dur"] - wt(d, "responden") + 0.3, 247),
            d["t0"] + wt(d, "responden") - 0.3, 0.4)
    co2 = E["codigo"]
    for pal, son in (("código", bip()), ("solo", golpe() * 0.4), ("vez", bip())):
        colocar(fx, son, co2["t0"] + wt(co2, pal) - 0.3, 0.6)
    f = E["final"]
    colocar(fx, zumbido(f["dur"], 220), f["t0"], 0.4)
    ct = E["cta"]
    colocar(fx, pop(), ct["t0"] + wt(ct, "Sígueme") - 0.2, 0.5)
    for k, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(k, 0.4), e["t0"] - 0.2, 0.18)
    envv = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.45 * np.clip(envv * 12, 0, 1)
    total = voz + (mus + fx) * duck
    total *= np.clip((TOTAL - tt) / 0.3, 0, 1)
    total = np.tanh(total * 1.05) * 0.95
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
