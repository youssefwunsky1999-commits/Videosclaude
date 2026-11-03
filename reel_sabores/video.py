"""Reel vertical «Cómo distinguimos los sabores» (serie «Mitos y verdades del cuerpo»): ilustración pintada con
degradados, grano y desenfoque, transiciones encadenadas sin cortes y subtítulos pequeños arriba a la izquierda.

    python3 voz.py && python3 video.py        -> sabores_reel.mp4
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
sys.path.insert(0, AQUI)
import guion as G_  # noqa: E402
SALIDA = os.path.join(AQUI, G_.SALIDA)

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


EXTRA = G_.EXTRA
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
CLAVE = set(G_.CLAVE)


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
            for seq, num in G_.FUSIONES:
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




# =====================================================================================================
# Reel «Cómo distinguimos los sabores» · estilo ilustración pintada (degradados, grano, desenfoque, sin cortes)
# =====================================================================================================
TINTA = (240, 236, 230)
GRIS_T = (150, 146, 160)
ROSA = (232, 128, 140)
ROSA_O = (196, 92, 110)
DORADO = (255, 206, 120)
CREMA = (250, 236, 214)


def degradado(L, c0, c1, y0=0, y1=H, pasos=48):
    for k in range(pasos):
        ya = y0 + (y1 - y0) * k / pasos
        yb = y0 + (y1 - y0) * (k + 1) / pasos + 1
        rect(L, 0, ya, W, yb, mezcla(c0, c1, k / (pasos - 1)))


def suave(L, x, y, r, col, a=1.0, capas=9):
    """Mancha de luz/color con borde difuso."""
    for k in range(capas):
        rr = r * (1 - k / capas)
        circ(L, x, y, rr, fill=col, a=a / capas * 1.6)


def desenfocar(L, r):
    if r <= 0:
        return
    small = L.img.resize((IW // 4, IH // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r))
    L.img.paste(small.resize((IW, IH), Image.BILINEAR))


def chaikin(pts, n=3):
    for _ in range(n):
        nuevo = []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            nuevo += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = nuevo
    return pts


PERFIL = [(0, -120), (50, -142), (100, -128), (128, -96), (136, -58), (140, -40), (156, -14), (172, 2), (166, 10),
          (146, 12), (150, 26), (142, 34), (150, 46), (142, 56), (138, 76), (122, 96), (96, 106), (98, 170), (10, 170),
          (-20, 110), (-42, 40), (-46, -40), (-30, -96)]
PERFIL = chaikin(PERFIL, 2)


def perfil(L, x, y, s=1.0, col=(120, 110, 190), col2=(70, 60, 130), a=1.0, nariz_col=None, ojo=True):
    pts = [(x + px * s, y + py * s) for px, py in PERFIL]
    poly(L, [(x + px * s + 10 * s, y + py * s + 8 * s) for px, py in PERFIL], col2, a)
    poly(L, pts, col, a)
    suave(L, x + 90 * s, y - 40 * s, 70 * s, mezcla(col, (255, 255, 255), 0.35), a * 0.5)
    if nariz_col:
        suave(L, x + 160 * s, y - 2 * s, 26 * s, nariz_col, a)
    if ojo:
        L.d.arc(P(x + 92 * s, y - 64 * s, x + 118 * s, y - 46 * s), 20, 160, fill=L.c((40, 30, 60), a), width=int(3 * K * s))
        for k in range(4):
            xx = x + (96 + k * 6) * s
            linea(L, [(xx, y - 48 * s), (xx - 2 * s, y - 40 * s)], (40, 30, 60), w=2 * s, a=a)
    # pelo
    L.d.chord(P(x - 52 * s, y - 150 * s, x + 110 * s, y + 10 * s), 150, 330, fill=L.c((40, 30, 50), a))


def pinza(L, x, y, s=1.0, a=1.0):
    for dy, col in ((-9, (214, 170, 110)), (9, (196, 150, 92))):
        rect(L, x - 6 * s, y + dy * s - 6 * s, x + 64 * s, y + dy * s + 6 * s, col, a=a, r=4 * s)
    rect(L, x + 30 * s, y - 4 * s, x + 44 * s, y + 4 * s, (170, 170, 180), a=a, r=2 * s)


def manzana(L, x, y, s=1.0, a=1.0):
    suave(L, x, y, 90 * s, (255, 120, 120), a * 0.25)
    circ(L, x - 18 * s, y, 46 * s, fill=(200, 40, 50), a=a)
    circ(L, x + 18 * s, y, 46 * s, fill=(210, 50, 56), a=a)
    suave(L, x - 22 * s, y - 18 * s, 22 * s, (255, 200, 200), a * 0.6)
    rect(L, x - 3 * s, y - 64 * s, x + 3 * s, y - 40 * s, (90, 60, 30), a=a)
    L.d.ellipse(P(x + 2 * s, y - 70 * s, x + 34 * s, y - 52 * s), fill=L.c((90, 170, 80), a))


def cebolla(L, x, y, s=1.0, a=1.0):
    suave(L, x, y, 90 * s, (220, 180, 255), a * 0.25)
    for k, col in enumerate(((150, 80, 150), (190, 120, 190), (236, 210, 236))):
        r = (52 - k * 14) * s
        L.d.ellipse(P(x - r, y - r * 1.05, x + r, y + r), fill=L.c(col, a))
    poly(L, [(x - 8 * s, y - 50 * s), (x + 8 * s, y - 50 * s), (x, y - 78 * s)], (150, 80, 150), a)


LENGUA = chaikin([(-150, -200), (-120, -230), (0, -240), (120, -230), (150, -200), (160, -40), (140, 80), (90, 170),
                  (0, 210), (-90, 170), (-140, 80), (-160, -40)], 3)


def lengua(L, x, y, s=1.0, a=1.0, papilas=True, T=0.0):
    poly(L, [(x + px * s, y + py * s + 10 * s) for px, py in LENGUA], ROSA_O, a)
    poly(L, [(x + px * s, y + py * s) for px, py in LENGUA], ROSA, a)
    linea(L, [(x, y - 220 * s), (x, y + 150 * s)], ROSA_O, w=5 * s, a=a * 0.6)
    suave(L, x - 50 * s, y - 80 * s, 80 * s, (255, 200, 210), a * 0.4)
    if papilas:
        rs = random.Random(4)
        for _ in range(140):
            px, py = rs.uniform(-140, 140), rs.uniform(-220, 180)
            if abs(px) > 150 - max(0, py - 60) * 0.5:
                continue
            circ(L, x + px * s, y + py * s, rs.uniform(1.5, 3.2) * s, fill=(250, 180, 190), a=a * 0.8)


SABORES = [("dulce", "DULCE", (255, 150, 200)), ("salado", "SALADO", (230, 236, 255)), ("ácido", "ÁCIDO", (255, 230, 90)),
           ("amargo", "AMARGO", (150, 100, 70)), ("umami", "UMAMI", (255, 150, 70))]


def icono_sabor(L, k, x, y, s=1.0, a=1.0):
    col = SABORES[k][2]
    suave(L, x, y, 60 * s, col, a * 0.5)
    circ(L, x, y, 34 * s, fill=(30, 26, 40), a=a * 0.85)
    circ(L, x, y, 34 * s, outline=col, w=3, a=a)
    if k == 0:      # terrón de azúcar
        rect(L, x - 14 * s, y - 14 * s, x + 14 * s, y + 14 * s, (255, 255, 255), a=a, r=3)
    elif k == 1:    # cristales de sal
        for dx, dy in ((-10, 4), (8, -8), (6, 10), (-4, -10)):
            rect(L, x + dx * s - 5 * s, y + dy * s - 5 * s, x + dx * s + 5 * s, y + dy * s + 5 * s, (255, 255, 255), a=a)
    elif k == 2:    # rodaja de limón
        circ(L, x, y, 18 * s, fill=(255, 220, 60), a=a)
        for j in range(6):
            ang = j * math.pi / 3
            linea(L, [(x, y), (x + 16 * s * math.cos(ang), y + 16 * s * math.sin(ang))], (255, 250, 200), w=2, a=a)
    elif k == 3:    # grano de café
        L.d.ellipse(P(x - 12 * s, y - 17 * s, x + 12 * s, y + 17 * s), fill=L.c((110, 70, 40), a))
        linea(L, [(x, y - 14 * s), (x - 3 * s, y), (x, y + 14 * s)], (60, 36, 20), w=2, a=a)
    else:           # cuenco de caldo
        L.d.chord(P(x - 20 * s, y - 16 * s, x + 20 * s, y + 20 * s), 0, 180, fill=L.c((240, 240, 240), a))
        for j in range(3):
            linea(L, [(x - 8 * s + j * 8 * s, y - 6 * s), (x - 4 * s + j * 8 * s, y - 14 * s), (x - 8 * s + j * 8 * s, y - 22 * s)],
                  (255, 255, 255), w=2, a=a * 0.7)


def pastilla(O, txt, x, y, q, col=(90, 200, 255), size=22):
    if q <= 0:
        return
    w = ancho(txt, size) + 34
    s = eob(q)
    suave(O, x, y, w * 0.7 * s, col, q * 0.35)
    rect(O, x - w / 2 * s, y - 22 * s, x + w / 2 * s, y + 22 * s, (20, 30, 50), a=q * 0.85, r=12)
    rect(O, x - w / 2 * s, y - 22 * s, x + w / 2 * s, y + 22 * s, None, outline=col, w=2, a=q, r=12)
    texto(O, txt, x, y, size * s, TINTA, a=q, fuente="black", sombra=False)


def particulas(L, x0, y0, x1, y1, T, n=12, col=(255, 120, 120), a=1.0, curva=0.0, vel=0.5, r=4):
    for k in range(n):
        u = (T * vel + k / n) % 1
        x = lerp(x0, x1, u) + curva * math.sin(u * math.pi)
        y = lerp(y0, y1, u)
        circ(L, x, y, r, fill=col, a=a * math.sin(u * math.pi))


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    degradado(L, (40, 30, 70), (14, 12, 30))
    suave(L, 380, 560, 300, (120, 80, 170), 0.5)
    desenfocar(L, 6)
    perfil(L, 120, 600, 1.45)
    pinza(L, 120 + 156 * 1.45, 600 - 4 * 1.45, 1.3)
    qm = prog(t, wt(e, "manzana") - 0.3, 0.4)
    qc = prog(t, wt(e, "cebolla") - 0.3, 0.4)
    duda = prog(t, wt(e, "costar") - 0.3, 0.4)
    w = 6 * math.sin(T * 7) * duda
    if qm > 0:
        manzana(L, 420 + w, 430, 0.9 * eob(qm), a=qm)
    if qc > 0:
        cebolla(L, 420 - w, 720, 0.9 * eob(qc), a=qc)
    if duda > 0:
        texto(L, "?", 470, 575 + 6 * math.sin(T * 4), 70 * eob(duda) + 1, DORADO, a=duda, fuente="black")
    st["cam"] = (1.08 - 0.05 * eio(t / D), 270, 540)


def esc_cinco(L, e, t, D, T, st):
    degradado(L, (60, 24, 40), (20, 10, 20))
    suave(L, 270, 600, 320, (200, 80, 110), 0.4)
    desenfocar(L, 6)
    lengua(L, 270, 640, 1.2, T=T)
    q = prog(t, wt(e, "cinco") - 0.3, 0.4)
    if q > 0:
        suave(L, 270, 450, 140 * eob(q), DORADO, q * 0.5)
        texto(L, "5", 270, 450, 150 * eob(q) + 1, CREMA, a=q, fuente="black", sombra=False)
    st["cam"] = (1.02 + 0.06 * eio(t / D), 270, 560)


def esc_lista(L, e, t, D, T, st):
    degradado(L, (60, 24, 40), (20, 10, 20))
    suave(L, 270, 600, 320, (200, 80, 110), 0.4)
    desenfocar(L, 6)
    lengua(L, 270, 760, 1.0, a=0.9)
    for k, (pal, nom, col) in enumerate(SABORES):
        q = prog(t, wt(e, pal) - 0.3, 0.35)
        if q <= 0:
            continue
        ang = math.pi * (1.1 + 0.8 * k / 4)
        x, y = 270 + 190 * math.cos(ang), 560 + 190 * math.sin(ang)
        icono_sabor(L, k, x, y + 4 * math.sin(T * 2 + k), 1.15 * eob(q), a=q)
        texto(L, nom, x, y + 60, 16, col, a=q, fuente="black")
    qu = prog(t, wt(e, "caldo") - 0.3, 0.4)
    if qu > 0:
        pastilla(L, "UMAMI = «SABROSO» EN JAPONÉS", 270, 640, qu, col=(255, 150, 70), size=17)


def esc_botones(L, e, t, D, T, st):
    degradado(L, (110, 50, 70), (50, 20, 34))
    rs = random.Random(9)
    for k in range(18):
        x, y = rs.uniform(-40, 580), rs.uniform(300, 1000)
        suave(L, x, y, rs.uniform(60, 110), (220, 110, 130), 0.6)
    desenfocar(L, 8)
    z = eio(prog(t, 0, 1.6))
    cx, cy = 270, 620
    r = 50 + 160 * z
    renueva = prog(t, wt(e, "renuevan") - 0.3, 0.4)
    suave(L, cx, cy, r * 1.5, (255, 170, 180), 0.5)
    L.d.ellipse(P(cx - r * 0.78, cy - r, cx + r * 0.78, cy + r), fill=L.c((236, 170, 176)))
    for k in range(7):
        dx = (k - 3) * r * 0.19
        h = r * 0.88 * (1 - abs(k - 3) * 0.13)
        col = mezcla((250, 196, 200), (255, 222, 150), 0.5 + 0.5 * math.sin(T * 3 + k)) if renueva > 0 else \
            ((250, 196, 200) if k % 2 else (244, 184, 190))
        L.d.ellipse(P(cx + dx - r * 0.1, cy - h, cx + dx + r * 0.1, cy + h * 0.95), fill=L.c(col))
        circ(L, cx + dx, cy + h * 0.2, r * 0.035, fill=(200, 110, 130))
    circ(L, cx, cy - r * 0.98, r * 0.1, fill=(120, 50, 70))
    for k in range(5):
        linea(L, [(cx - 8 + k * 4, cy - r * 0.92), (cx - 10 + k * 5, cy - r * 1.1)], (120, 50, 70), w=2)
    qb = prog(t, wt(e, "botones") - 0.3, 0.4)
    if qb > 0:
        pastilla(L, "BOTÓN GUSTATIVO", 270, 330 + 0, qb, col=ROSA, size=20)
    if renueva > 0:
        L.d.arc(P(cx - r - 30, cy - r - 30, cx + r + 30, cy + r + 30), (T * 120) % 360, (T * 120) % 360 + 270,
                fill=L.c(DORADO, renueva), width=4 * K)
    st["cam"] = (1.02 + 0.04 * eio(t / D), 270, 600)


def mapa_lengua(L, x, y, s, a, mezcla_q, T):
    lengua(L, x, y, s, a=a, papilas=False)
    zonas = [(0, 150, 60, 0), (-110, 20, 50, 1), (110, 20, 50, 1), (-115, -110, 50, 2), (115, -110, 50, 2),
             (0, -180, 70, 3)]
    for (zx, zy, zr, k) in zonas:
        col = SABORES[k][2]
        suave(L, x + zx * s, y + zy * s, zr * s * 1.4, col, a * (1 - mezcla_q) * 0.9)
        if mezcla_q < 0.5:
            texto(L, SABORES[k][1], x + zx * s, y + zy * s, 14, (40, 20, 30), a=a * (1 - 2 * mezcla_q), fuente="black",
                  sombra=False)
    if mezcla_q > 0:
        rs = random.Random(3)
        for j in range(80):
            px, py = rs.uniform(-130, 130), rs.uniform(-210, 170)
            col = SABORES[j % 5][2]
            circ(L, x + px * s, y + py * s, 5 * s, fill=col, a=a * mezcla_q)


def esc_mito(L, e, t, D, T, st):
    degradado(L, (30, 40, 70), (12, 14, 30))
    suave(L, 270, 600, 300, (80, 100, 170), 0.4)
    desenfocar(L, 6)
    qx = prog(t, wt(e, "mito") - 0.3, 0.3)
    q5 = prog(t, wt(e, "cinco") - 0.4, 0.8)
    mapa_lengua(L, 270, 640, 1.15, 1.0, q5, T)
    if qx > 0 and q5 < 0.5:
        sello_t(L, "MITO", 270, 520, qx * (1 - 2 * q5), col=ROJO, size=48)
    q19 = prog(t, wt(e, "mil") - 0.3, 0.4)
    if q19 > 0:
        pastilla(L, "1901", 270, 360, q19 * (1 - q5 * 0.6), size=28)
    if q5 > 0.5:
        pastilla(L, "TODA LA LENGUA NOTA LOS 5", 270, 360, prog(q5, 0.5, 0.5), col=(120, 230, 160), size=19)


def corte_cabeza(L, x, y, s, a=1.0, bloqueo=0.0):
    """Corte de perfil: boca, paladar y fosa nasal conectadas por detrás (vía retronasal)."""
    perfil(L, x, y, s, col=(220, 170, 150), col2=(170, 120, 110), a=a, ojo=False)
    # fosa nasal
    nas = [(60, -40), (150, -30), (165, -2), (140, 6), (60, 4), (30, -10)]
    poly(L, [(x + px * s, y + py * s) for px, py in nas], mezcla((120, 50, 60), (150, 150, 150), bloqueo), a)
    # boca
    boca = [(60, 30), (146, 30), (150, 46), (60, 56), (30, 50)]
    poly(L, [(x + px * s, y + py * s) for px, py in boca], (120, 50, 60), a)
    # conducto por detrás del paladar
    poly(L, [(x + 26 * s, y - 12 * s), (x + 44 * s, y - 8 * s), (x + 44 * s, y + 40 * s), (x + 24 * s, y + 48 * s)],
         (120, 50, 60), a)
    # zona del olfato
    suave(L, x + 100 * s, y - 44 * s, 24 * s, DORADO, a * (1 - bloqueo))
    rect(L, x + 60 * s, y + 6 * s, x + 150 * s, y + 18 * s, (240, 200, 190), a=a)   # paladar


def esc_nariz(L, e, t, D, T, st):
    degradado(L, (70, 40, 60), (20, 14, 26))
    suave(L, 300, 600, 300, (170, 100, 140), 0.4)
    desenfocar(L, 6)
    x, y, s = 70, 660, 2.05
    corte_cabeza(L, x, y, s)
    qf = prog(t, wt(e, "fresa") - 0.3, 0.3)
    qc = prog(t, wt(e, "café") - 0.3, 0.3)
    if qf > 0:
        suave(L, 330, 300, 50, (255, 80, 100), qf * 0.6)
        poly(L, [(310, 280), (350, 280), (330, 330)], (230, 40, 60), qf)
        texto(L, "¿fresa?", 330, 350, 18, TINTA, a=qf, fuente="black")
    if qc > 0:
        suave(L, 450, 300, 40, (150, 100, 70), qc * 0.6)
        L.d.ellipse(P(436, 282, 464, 320), fill=L.c((110, 70, 40), qc))
        texto(L, "¿café?", 450, 350, 18, TINTA, a=qc, fuente="black")
    qa = prog(t, wt(e, "aromas") - 0.4, 0.5)
    if qa > 0:
        # de la boca, por detrás del paladar, hasta la fosa nasal y el olfato
        particulas(L, x + 100 * s, y + 40 * s, x + 34 * s, y + 30 * s, T, 6, (255, 120, 140), qa, 0, 0.6)
        particulas(L, x + 34 * s, y + 30 * s, x + 34 * s, y - 6 * s, T + 0.3, 6, (255, 120, 140), qa, 0, 0.6)
        particulas(L, x + 34 * s, y - 6 * s, x + 100 * s, y - 40 * s, T + 0.6, 6, (255, 200, 140), qa, 0, 0.6)
        suave(L, x + 100 * s, y - 44 * s, 60 * s * (0.8 + 0.2 * math.sin(T * 6)), DORADO, qa * 0.6)
        pastilla(L, "VÍA RETRONASAL", 270, 900, qa, col=DORADO, size=18)
    st["cam"] = (1.0 + 0.05 * eio(t / D), 270, 560)


def cerebro(L, x, y, s=1.0, brillo=0.0, a=1.0):
    suave(L, x, y, 170 * s, mezcla((255, 160, 180), DORADO, brillo), a * (0.4 + 0.5 * brillo))
    L.d.ellipse(P(x - 130 * s, y - 90 * s, x + 130 * s, y + 90 * s), fill=L.c(mezcla((240, 160, 170), (255, 220, 150), brillo), a))
    for k in range(7):
        xx = x - 100 * s + k * 33 * s
        L.d.arc(P(xx - 26 * s, y - 70 * s + (k % 2) * 30 * s, xx + 26 * s, y - 10 * s + (k % 2) * 30 * s), 200, 340,
                fill=L.c((200, 110, 130), a), width=int(4 * K * s))
        L.d.arc(P(xx - 22 * s, y + 0 * s, xx + 22 * s, y + 50 * s), 20, 160, fill=L.c((200, 110, 130), a), width=int(4 * K * s))


def esc_cerebro(L, e, t, D, T, st):
    degradado(L, (30, 24, 60), (10, 8, 22))
    suave(L, 270, 450, 300, (90, 70, 170), 0.4)
    desenfocar(L, 6)
    entradas = [("lengua", "LENGUA", ROSA), ("olfato", "OLFATO", DORADO), ("textura", "TEXTURA", (180, 220, 255)),
                ("temperatura", "TEMPERATURA", (255, 140, 90)), ("color", "COLOR", (150, 255, 170))]
    qs = prog(t, wt(e, "sabor") - 0.4, 0.5)
    cerebro(L, 270, 450, 1.0, brillo=qs)
    for k, (pal, nom, col) in enumerate(entradas):
        q = prog(t, wt(e, pal) - 0.3, 0.3)
        if q <= 0:
            continue
        x = 70 + k * 100
        y = 820
        suave(L, x, y, 40, col, q * 0.6)
        circ(L, x, y, 22, fill=col, a=q)
        texto(L, nom, x, y + 40, 12, col, a=q, fuente="black")
        particulas(L, x, y - 26, 270 + (k - 2) * 40, 530, T + k * 0.2, 8, col, q, (k - 2) * 20, 0.7)
    if qs > 0:
        texto(L, "SABOR", 270, 450, 46 * eob(qs) + 1, (90, 40, 20), a=qs, fuente="black", sombra=False)


def esc_resfriado(L, e, t, D, T, st):
    degradado(L, (40, 60, 90), (14, 20, 34))
    suave(L, 270, 600, 300, (90, 130, 190), 0.35)
    desenfocar(L, 6)
    x, y, s = 70, 660, 2.05
    corte_cabeza(L, x, y, s, bloqueo=1.0)
    suave(L, x + 168 * s, y - 2 * s, 18 * s, (255, 90, 90), 0.8)
    for k in range(6):
        u = (T * 0.8 + k / 6) % 1
        px = x + 34 * s
        py = lerp(y + 30 * s, y + 4 * s, u)
        rebote = u > 0.7
        circ(L, px + (30 * (u - 0.7) * 10 if rebote else 0), py, 4, fill=(255, 120, 140), a=math.sin(u * math.pi))
    q = prog(t, wt(e, "nada") - 0.3, 0.4)
    if q > 0:
        L.d.ellipse(P(330, 360, 490, 420), fill=L.c((200, 200, 205), q))
        L.d.ellipse(P(350, 368, 470, 410), fill=L.c((170, 170, 176), q))
        pastilla(L, "SIN OLFATO, SIN SABOR", 270, 880, q, col=(150, 190, 255), size=18)
    st["tinte"] = ((60, 90, 140), 0.12)


def guindilla(L, x, y, s=1.0, a=1.0):
    suave(L, x, y, 120 * s, (255, 60, 40), a * 0.4)
    pts = [(x - 90 * s, y - 20 * s), (x - 40 * s, y - 34 * s), (x + 40 * s, y - 20 * s), (x + 110 * s, y + 30 * s),
           (x + 40 * s, y + 10 * s), (x - 40 * s, y + 14 * s), (x - 90 * s, y + 14 * s)]
    poly(L, pts, (220, 30, 30), a)
    suave(L, x - 30 * s, y - 16 * s, 20 * s, (255, 160, 140), a * 0.6)
    rect(L, x - 116 * s, y - 14 * s, x - 86 * s, y + 8 * s, (60, 140, 60), a=a, r=6)


def llama(L, x, y, s, T, a=1.0):
    for k, col in enumerate(((255, 80, 40), (255, 160, 60), (255, 230, 120))):
        h = (70 - k * 18) * s * (1 + 0.15 * math.sin(T * 10 + k + x))
        w = (26 - k * 7) * s
        poly(L, [(x - w, y), (x - w * 0.4, y - h * 0.6), (x + 4 * s * math.sin(T * 8 + x), y - h), (x + w * 0.4, y - h * 0.6),
                 (x + w, y)], col, a)


def esc_picante(L, e, t, D, T, st):
    degradado(L, (90, 20, 20), (30, 6, 8))
    suave(L, 270, 640, 320, (220, 60, 40), 0.45)
    desenfocar(L, 6)
    lengua(L, 270, 760, 1.0)
    qd = prog(t, wt(e, "dolor") - 0.3, 0.4)
    qc = prog(t, wt(e, "calor") - 0.4, 0.4)
    guindilla(L, 270, 420, 1.3)
    if qc > 0 or qd > 0:
        for k in range(6):
            llama(L, 160 + k * 44, 720 + 20 * math.sin(k), 0.9, T, a=max(qc, qd * 0.6))
    if qd > 0:
        sello_t(L, "DOLOR, NO SABOR", 270, 570, qd, col=(255, 210, 120), size=30)
    if qc > 0:
        pastilla(L, "RECEPTOR DEL CALOR (TRPV1)", 270, 900, qc, col=(255, 140, 90), size=17)
    st["shake"] = 2 * qc


def esc_cierre(L, e, t, D, T, st):
    degradado(L, (50, 36, 80), (16, 12, 30))
    suave(L, 270, 560, 300, (150, 110, 200), 0.4)
    desenfocar(L, 6)
    q = prog(t, wt(e, "nariz") - 0.4, 0.6)
    perfil(L, 120, 600, 1.45, nariz_col=DORADO if q > 0 else None)
    if q > 0:
        suave(L, 120 + 165 * 1.45, 600, 120 * (0.8 + 0.2 * math.sin(T * 4)), DORADO, q * 0.6)
        for k in range(10):
            ang = k / 10 * 2 * math.pi + T
            r = 80 + 20 * math.sin(T * 3 + k)
            circ(L, 120 + 165 * 1.45 + r * math.cos(ang), 600 + r * math.sin(ang), 3, fill=CREMA, a=q)


def esc_cta(L, e, t, D, T, st):
    if t > D - 1.0:
        esc_gancho(L, ESC[0], 0.05, ESC[0]["dur"], T, st)
        return
    esc_cierre(L, ESC[-2], ESC[-2]["dur"], ESC[-2]["dur"], T, st)
    q = prog(t, wt(e, "Envíaselo") - 0.3, 0.4)
    if q > 0:
        s = eob(q)
        rect(L, 270 - 150 * s, 820, 270 + 150 * s, 876, (255, 255, 255), a=q * 0.14, r=28, outline=(255, 255, 255), w=2)
        texto(L, "ENVÍASELO  ↗", 270, 848, 22 * s, BLANCO, a=q, fuente="sym", sombra=False)


FUNCS = {"gancho": esc_gancho, "cinco": esc_cinco, "lista": esc_lista, "botones": esc_botones, "mito": esc_mito,
         "nariz": esc_nariz, "cerebro": esc_cerebro, "resfriado": esc_resfriado, "picante": esc_picante,
         "cierre": esc_cierre, "cta": esc_cta}


def subtitulos(O, T):
    """Estilo del reel de referencia: frase pequeña arriba a la izquierda; dichas en blanco, futuras tenues."""
    for ini, fin, bloque in SUBS:
        if ini <= T < fin:
            size = 30
            x0, y = 52, 190
            x = x0
            for (w, t0, t1) in bloque:
                fw = ancho(w, size, "bold")
                if x + fw > W - 40:
                    x = x0
                    y += 40
                dicha = T >= t0
                limpio = w.lower().strip("¿?¡!.,:")
                if dicha and limpio in CLAVE:
                    rect(O, x - 6, y - 20, x + fw + 6, y + 20, (120, 170, 255), a=0.2, r=8, outline=(150, 190, 255), w=1.5)
                texto(O, w, x, y, size, TINTA if dicha else GRIS_T, a=1.0 if dicha else 0.45, fuente="bold", anchor="lm",
                      sombra=False)
                x += fw + ancho(" ", size, "bold")
            break


_GRANO = None


def grano(i):
    global _GRANO
    if _GRANO is None:
        rng = np.random.default_rng(1)
        # grano suave (generado a media resolución y ampliado): se nota, pero comprime bien
        _GRANO = []
        for _ in range(4):
            g = (rng.standard_normal((OH // 2, OW // 2)) * 4.5).astype(np.float32)
            g = np.asarray(Image.fromarray(g, mode="F").resize((OW, OH), Image.BILINEAR))
            _GRANO.append(g.astype(np.int16)[..., None])
    return _GRANO[i % 4]


def escena_cuadro(e, t, T):
    L = Capa(Image.new("RGB", (IW, IH), (0, 0, 0)))
    st = {"overlay": []}
    FUNCS[e["nombre"]](L, e, t, e["dur"], T, st)
    img = L.img
    z, fx, fy = st.get("cam", (1.02 + 0.05 * eio(t / e["dur"]), 270, 540))
    z += golpe_zoom(T) * 0.5
    cw, ch = IW / z, IH / z
    sh = st.get("shake", 0)
    x0 = cl(fx * K - cw / 2, 0, IW - cw) + (1.5 * math.sin(T * 0.9) + sh * math.sin(T * 61)) * K
    y0 = cl(fy * K - ch / 2, 0, IH - ch) + (1.5 * math.cos(T * 0.7)) * K
    img = img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    if "tinte" in st:
        col, k = st["tinte"]
        img = Image.blend(img, Image.new("RGB", (IW, IH), col), k)
    return img


def render_frame(fr):
    T = fr / FPS
    e = escena_en(T)
    t = T - e["t0"]
    img = escena_cuadro(e, t, T)
    FUN = 0.45
    if t < FUN and e["i"] > 0:
        p = ESC[e["i"] - 1]
        prev = escena_cuadro(p, p["dur"] - 0.01 + t * 0.3, T)
        # empuje: la anterior se acerca mientras se funde
        z = 1 + 0.12 * eio(t / FUN)
        cw, ch = IW / z, IH / z
        prev = prev.transform((IW, IH), Image.EXTENT, ((IW - cw) / 2, (IH - ch) / 2, (IW + cw) / 2, (IH + ch) / 2),
                              Image.BILINEAR)
        img = Image.blend(prev, img, eio(t / FUN))
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    texto(O, "m i t o s   d e l   c u e r p o", 270, 104, 12, (200, 196, 210), a=0.6, fuente="semi", sombra=False)
    subtitulos(O, T)
    out = np.asarray(O.img.resize((OW, OH), Image.LANCZOS), dtype=np.int16)
    out = np.clip(out + grano(fr), 0, 255).astype(np.uint8)
    return out.tobytes()


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
    mus = musica(n) * 1.1
    fx = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    g = E["gancho"]
    for pal in ("manzana", "cebolla"):
        colocar(fx, pop(), g["t0"] + wt(g, pal) - 0.3, 0.5)
    c = E["cinco"]
    colocar(fx, golpe() * 0.5, c["t0"] + wt(c, "cinco") - 0.3, 0.5)
    li = E["lista"]
    for pal, _, _ in SABORES:
        colocar(fx, burbuja(hash(pal) % 50), li["t0"] + wt(li, pal) - 0.3, 0.6)
    b = E["botones"]
    colocar(fx, whoosh(3, 1.2), b["t0"], 0.4)
    m = E["mito"]
    colocar(fx, golpe() * 0.6, m["t0"] + wt(m, "mito") - 0.3, 0.6)
    colocar(fx, dingdong(), m["t0"] + wt(m, "cinco") - 0.4, 0.4)
    na = E["nariz"]
    colocar(fx, whoosh(9, 1.4), na["t0"] + wt(na, "aromas") - 0.4, 0.4)
    ce = E["cerebro"]
    for pal in ("lengua", "olfato", "textura", "temperatura", "color"):
        colocar(fx, tic(), ce["t0"] + wt(ce, pal) - 0.3, 0.5)
    colocar(fx, golpe() * 0.5, ce["t0"] + wt(ce, "sabor") - 0.4, 0.5)
    pi = E["picante"]
    colocar(fx, braam() * 0.6, pi["t0"] + wt(pi, "dolor") - 0.3, 0.5)
    ct = E["cta"]
    colocar(fx, pop(), ct["t0"] + wt(ct, "Envíaselo") - 0.3, 0.5)
    for k, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(k, 0.5), e["t0"] - 0.25, 0.15)
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
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "8M", "-bufsize", "16M",
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
