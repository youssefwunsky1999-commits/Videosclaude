"""TikTok vertical «Si te pilla un terremoto...»: salón en corte que tiembla, sismógrafo,
personajes planos, subtítulos grandes palabra a palabra, música y efectos.

    python3 voz.py && python3 video.py        -> terremoto_tiktok.mp4
    python3 video.py --preview 2 10 30        -> fotogramas sueltos en build/
"""
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
SALIDA = os.path.join(AQUI, "terremoto_tiktok.mp4")

W, H = 540, 960            # unidades de diseño (9:16)
K = 3                      # resolución interna = 1620x2880
IW, IH = W * K, H * K
OW, OH = 1080, 1920
FPS = 30
SR = 44100
VOZ_OFF = 0.12
COLA = 0.4

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


ESC = []
_t = 0.0
for i, seg in enumerate(DATOS):
    dv = dur_mp3(os.path.join(BUILD, f"voz_{i}.mp3"))
    d = VOZ_OFF + dv + COLA + (1.4 if i == len(DATOS) - 1 else 0) + 0
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
CLAVE = {"terremoto", "mito", "caro", "marco", "puerta", "resistente", "golpearte", "corriendo", "calle", "cristales",
         "cornisas", "tres", "agáchate", "cúbrete", "agárrate", "suelo", "mesa", "cabeza", "cuello", "pata", "cama",
         "almohada", "escaleras", "ascensor", "réplicas", "guarda", "compártelo"}


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
            if j + 2 < len(pares) and [p[0].lower().strip(".,") for p in pares[j:j + 3]] == ["uno", "uno", "dos"]:
                w0 = dict(pares[j][1])
                w0["d"] = pares[j + 2][1]["t"] + pares[j + 2][1]["d"] - w0["t"]
                fus.append(("112" + pares[j + 2][0][3:], w0))
                j += 3
                continue
            fus.append(pares[j])
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
        L.d.rectangle(P(x0, y0, x1, y1), fill=L.c(fill, a))


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


def persona(L, x, y, pose, esc=1.0, flip=False, tipo="victima", sombra=None, a=1.0, ojos=1.0, boca=0.0):
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
                     185 if s > 0 else 175, 355 if s > 0 else 365, fill=L.c(PELO, a))
        poly(L, [(cab[0] - r * s, cab[1] - r * .3), (cab[0] - r * .3 * s, cab[1] - r), (cab[0] - r * 1.02 * s, cab[1] + r * .25)],
             PELO, a)
        circ(L, cab[0] - r * .05 * s, cab[1] + r * .25, r * .22, fill=(232, 150, 130), a=a * .5)  # mejilla
        ex = cab[0] + r * .45 * s
        ey = cab[1] - r * .05
        if ojos > 0.15:
            circ(L, ex, ey, 3.6 * e * ojos + 1, fill=(28, 24, 22), a=a)
        else:
            linea(L, [(ex - 5 * e, ey), (ex + 5 * e, ey)], (28, 24, 22), w=2 * e, a=a)
        linea(L, [(ex - 7 * e, ey - 10 * e), (ex + 7 * e, ey - 11 * e)], PELO, w=2.6 * e, a=a)
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


# --- Escenas del TikTok «Si te pilla un terremoto...» (se insertan en video.py al montarlo) ---

POSES.update({
    "corre1": dict(rodilla=(40, 72), pie=(22, 172), cuello=(18, -146), cabeza=(30, -190), codo=(-28, -92), mano=(-46, -48),
                   codo2=(40, -96), mano2=(60, -130)),
    "corre2": dict(rodilla=(-18, 90), pie=(-62, 166), cuello=(18, -146), cabeza=(30, -190), codo=(34, -94), mano=(58, -126),
                   codo2=(-26, -92), mano2=(-44, -50)),
    "cubre_pie": dict(rodilla=(6, 94), pie=(4, 190), cuello=(8, -148), cabeza=(14, -192), codo=(40, -200), mano=(18, -232),
                      codo2=(-30, -200), mano2=(6, -232)),
    "agachado": dict(rodilla=(70, 40), pie=(-10, 76), cuello=(60, -80), cabeza=(98, -96), codo=(86, -140), mano=(112, -118),
                     codo2=(80, -40), mano2=(110, -10)),
    "agarra": dict(rodilla=(70, 40), pie=(-10, 76), cuello=(62, -76), cabeza=(100, -90), codo=(86, -136), mano=(114, -112),
                   codo2=(110, -40), mano2=(150, -40)),
    "cama": dict(rodilla=(72, -14), pie=(146, -2), cuello=(-112, -4), cabeza=(-152, -18), codo=(-120, -60), mano=(-150, -56),
                 codo2=(-104, -54), mano2=(-138, -50)),
    "camina1": dict(rodilla=(26, 92), pie=(36, 188), cuello=(6, -150), cabeza=(12, -196), codo=(-16, -76), mano=(-26, -14),
                    codo2=(18, -76), mano2=(32, -16)),
    "camina2": dict(rodilla=(-12, 94), pie=(-30, 188), cuello=(6, -150), cabeza=(12, -196), codo=(18, -76), mano=(32, -16),
                    codo2=(-16, -76), mano2=(-26, -14)),
})

TECHO, SUELO = 362, 730
PARED = (236, 214, 188)
PARED_S = (214, 190, 164)
MADERA_SUELO = (150, 104, 70)


def amp(T):
    """Intensidad del temblor (0..1) en el instante T."""
    e = escena_en(T)
    t = T - e["t0"]
    n = e["nombre"]
    base = {"gancho": 0.75, "marco": 0.6, "salir": 0.8, "tres": 0.5, "mesa": 0.85, "cama": 0.6, "despues": 0.0,
            "final": 0.0}[n]
    if n == "gancho":
        base *= prog(t, 0.25, 0.6)
    if n == "despues":
        try:
            tr = wt(e, "réplicas") - 0.25
            base = 0.9 * math.exp(-max(0, t - tr) * 1.4) if t > tr else 0
        except KeyError:
            pass
    if n == "cama":
        base *= 1 - prog(t, e["dur"] - 0.6, 0.6)
    return base


def temblor(T, a, escala=10):
    return (escala * a * (math.sin(T * 47) * 0.6 + math.sin(T * 31.7) * 0.4),
            escala * 0.6 * a * (math.sin(T * 53.3) * 0.5 + math.sin(T * 23.1) * 0.5))


def salon(L, T, a, t, opciones=()):
    """Salón en corte: pared, suelo, ventana, cuadro, lámpara, estantería."""
    rect(L, 0, 0, W, H, (20, 18, 22))
    rect(L, 0, TECHO, W, SUELO, PARED)
    # zócalo y suelo de madera
    rect(L, 0, SUELO - 10, W, SUELO, PARED_S)
    rect(L, 0, SUELO, W, SUELO + 40, MADERA_SUELO)
    for x in range(0, W, 60):
        linea(L, [(x, SUELO), (x, SUELO + 40)], (120, 80, 52), w=1.5)
    rect(L, 0, SUELO + 40, W, H, (54, 46, 44))
    rect(L, 0, TECHO - 14, W, TECHO, (200, 180, 158))
    # grietas que crecen con el tiempo
    g = st_grietas = cl(t / 6) * (0.3 + a)
    if g > 0.05:
        pts = [(330, TECHO), (322, TECHO + 30 * g), (340, TECHO + 60 * g), (326, TECHO + 100 * g), (338, TECHO + 140 * g)]
        linea(L, pts, (120, 100, 86), w=2)
        linea(L, [(330, TECHO + 50 * g), (360, TECHO + 70 * g)], (120, 100, 86), w=1.5)
    # ventana
    if "ventana" in opciones:
        rect(L, 40, 420, 150, 540, (250, 246, 236), r=4)
        rect(L, 48, 428, 142, 532, (150, 200, 230))
        linea(L, [(95, 428), (95, 532)], (250, 246, 236), w=4)
        if a > 0.5:
            linea(L, [(60, 440), (80, 470), (70, 500)], BLANCO, w=1.5)
            linea(L, [(120, 450), (110, 480), (130, 515)], BLANCO, w=1.5)
    # cuadro que se balancea y cae
    if "cuadro" in opciones:
        cae = prog(t, 2.5, 0.5)
        ang = math.radians(10 * a * math.sin(T * 9))
        cx, cy = 300, 430 + 260 * cae ** 2
        if cae < 1:
            w2, h2 = 34, 26
            ca, sa = math.cos(ang + cae * 1.2), math.sin(ang + cae * 1.2)
            pts = [(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca) for dx, dy in [(-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2)]]
            poly(L, pts, (120, 80, 50))
            ip = [(cx + dx * .78 * ca - dy * .7 * sa, cy + dx * .78 * sa + dy * .7 * ca) for dx, dy in
                  [(-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2)]]
            poly(L, ip, (120, 170, 200))
        else:
            poly(L, [(270, SUELO - 4), (330, SUELO - 4), (334, SUELO + 6), (266, SUELO + 6)], (120, 80, 50))
    # estantería con libros que caen
    if "estante" in opciones:
        x0 = 420
        rect(L, x0, 470, x0 + 90, SUELO - 10, (140, 96, 60))
        for k, yb in enumerate((520, 590, 660)):
            rect(L, x0 + 6, yb, x0 + 84, yb + 6, (110, 74, 46))
            for j in range(6):
                bx = x0 + 10 + j * 12
                cae = prog(t, 1.5 + j * 0.3 + k * 0.5, 0.45) if a > 0.3 and (j + k) % 3 == 0 else 0
                col = [(200, 70, 60), (60, 110, 170), (230, 180, 70), (80, 150, 100)][(j + k) % 4]
                if cae == 0:
                    rect(L, bx, yb - 40 + (j % 2) * 6, bx + 10, yb, col)
                else:
                    y = lerp(yb - 40, SUELO - 6, cae ** 2)
                    xx = bx - 30 * cae - j * 4
                    rect(L, xx, y, xx + (10 + 30 * cae), y + (40 - 30 * cae), col)
    # lámpara colgante
    if "lampara" in opciones:
        ang = math.radians(25 * a * math.sin(T * 4.5))
        lx, ly = 220 + 90 * math.sin(ang), TECHO + 90 * math.cos(ang)
        linea(L, [(220, TECHO), (lx, ly)], (60, 60, 60), w=1.5)
        poly(L, [(lx - 26, ly + 22), (lx + 26, ly + 22), (lx + 12, ly), (lx - 12, ly)], (240, 200, 100))
        circ(L, lx, ly + 24, 7, fill=(255, 245, 200))
    # polvo que cae del techo
    if a > 0.2:
        rs = random.Random(int(T * 3))
        for j in range(int(14 * a)):
            x = rs.uniform(20, 520)
            y = TECHO + ((T * 160 + j * 37) % 380)
            circ(L, x, y, rs.uniform(1, 2.5), fill=(200, 190, 170), a=0.7)


def mesa(L, x0, x1, top, a=1.0):
    rect(L, x0 - 10, top, x1 + 10, top + 14, (150, 98, 60), a=a, r=3)
    for lx in (x0, x1 - 12):
        rect(L, lx, top + 14, lx + 12, SUELO, (122, 78, 46), a=a)


def puerta_marco(L, x, a=1.0, abre=0.0):
    rect(L, x - 8, 470, x + 110, SUELO, (196, 170, 140))
    rect(L, x, 480, x + 100, SUELO, (70, 60, 56))
    ancho_p = 100 * (1 - abre * 0.75)
    rect(L, x, 480, x + ancho_p, SUELO, (160, 110, 70))
    circ(L, x + ancho_p - 14, 610, 4, fill=(230, 200, 120))


def esc_gancho(L, e, t, D, T, st):
    a = amp(T)
    salon(L, T, a, t, ("ventana", "cuadro", "estante", "lampara"))
    mesa(L, 160, 400, 560)
    mira = prog(t, 0.6, 0.3)
    pose = "de_pie" if t < 1.0 else pose_mix("de_pie", "cubre_pie", 0.5 + 0.5 * math.sin(t * 3))
    persona(L, 92, 540, pose, 0.75, ojos=1 + 0.8 * mira)
    q = prog(t, wt(e, "mito") - 0.2, 0.4)
    if q > 0:
        st["overlay"].append(("sello", "MITO", q, -8))
    st["shake_amp"] = a


def esc_marco(L, e, t, D, T, st):
    a = amp(T)
    salon(L, T, a, t + 3, ("cuadro", "lampara"))
    puerta_marco(L, 330, abre=0.5 + 0.5 * math.sin(T * 6) * a)
    persona(L, 380, 540, "cubre_pie", 0.75)
    st["paso"] = ("✕", "MARCO DE LA PUERTA")
    tg = wt(e, "golpearte") - 0.3
    if t > tg:
        st["overlay"].append(("impacto", 440, 450, prog(t, tg, 0.4)))
    q = prog(t, wt(e, "resistente") - 0.2, 0.4)
    if q > 0:
        st["overlay"].append(("cruz", 380, 520, q))
    st["shake_amp"] = a


def esc_salir(L, e, t, D, T, st):
    a = amp(T)
    # fachada del edificio
    rect(L, 0, 0, W, H, (150, 190, 220))
    rect(L, 30, 120, 510, SUELO, (210, 160, 120))
    rect(L, 20, 110, 520, 130, (180, 130, 96))
    for fy in (170, 320, 470):
        rect(L, 10, fy - 14, 530, fy, (190, 140, 104))
        for fx in (70, 220, 370):
            rect(L, fx, fy + 16, fx + 100, fy + 106, (120, 170, 210))
            linea(L, [(fx + 50, fy + 16), (fx + 50, fy + 106)], (240, 230, 220), w=3)
    rect(L, 220, 600, 320, SUELO, (90, 60, 40))
    rect(L, 0, SUELO, W, H, (120, 120, 126))
    # la persona sale corriendo
    u = prog(t, 0.3, 3.0)
    x = lerp(270, 430, u)
    pose = pose_mix("corre1", "corre2", 0.5 + 0.5 * math.sin(t * 12))
    persona(L, x, 560, pose, 0.7)
    # cristales y trozos de cornisa cayendo
    rs = random.Random(7)
    for j in range(26):
        t0 = rs.uniform(0, D)
        dt = (t - t0) % 2.2
        fx = rs.choice([120, 270, 420]) + rs.uniform(-40, 40)
        fy0 = rs.choice([200, 350, 120])
        y = fy0 + 380 * dt * dt
        if y < SUELO:
            if j % 3 == 0:
                rect(L, fx, y, fx + 22, y + 14, (170, 120, 90))
            else:
                s = rs.uniform(4, 9)
                poly(L, [(fx, y - s), (fx + s * .6, y), (fx, y + s), (fx - s * .5, y)], (220, 240, 255))
    st["paso"] = ("✕", "SALIR CORRIENDO")
    q = prog(t, wt(e, "cristales") - 0.2, 0.4)
    if q > 0:
        st["overlay"].append(("cruz", x, 500, q))
    st["shake_amp"] = a


def esc_tres(L, e, t, D, T, st):
    a = amp(T)
    salon(L, T, a, t, ("lampara", "estante"))
    mesa(L, 160, 400, 560)
    ta, tc, tg = wt(e, "agáchate"), wt(e, "cúbrete"), wt(e, "agárrate")
    if t < ta:
        pose, x, y = "de_pie", 92, 540
    elif t < tc:
        k = eio(prog(t, ta, 0.5))
        pose, x, y = pose_mix("de_pie", "agachado", k), lerp(92, 120, k), lerp(540, 655, k)
    elif t < tg:
        k = eio(prog(t, tc, 0.6))
        pose, x, y = "agachado", lerp(120, 282, k), 655
    else:
        pose, x, y = pose_mix("agachado", "agarra", eio(prog(t, tg, 0.4))), 282, 655
    persona(L, x, y, pose, 0.75)
    for j, (pal, txt) in enumerate([("agáchate", "AGÁCHATE"), ("cúbrete", "CÚBRETE"), ("agárrate", "AGÁRRATE")]):
        q = prog(t, wt(e, pal) - 0.1, 0.3)
        if q > 0:
            st["overlay"].append(("palabra", txt, 400, 410 + j * 52, q, j))
    st["shake_amp"] = a


def esc_mesa(L, e, t, D, T, st):
    a = amp(T)
    salon(L, T, a, t + 2, ("lampara", "cuadro", "ventana"))
    desliza = 18 * math.sin(T * 2.2) * prog(t, wt(e, "mesa", 1) - 0.4, 0.5)
    mesa(L, 160 + desliza, 400 + desliza, 560)
    persona(L, 282 + desliza, 655, "agarra", 0.75)
    st["paso"] = ("✓", "BAJO UNA MESA")
    tc = wt(e, "cabeza") - 0.15
    if t > tc:
        st["overlay"].append(("aro", 282 + 100 * 0.75 + desliza, 655 - 90 * 0.75, prog(t, tc, 0.4), t))
    tp = wt(e, "pata") - 0.15
    if t > tp:
        st["overlay"].append(("aro", 282 + 150 * 0.75 + desliza, 655 - 40 * 0.75, prog(t, tp, 0.4), t))
    st["shake_amp"] = a


def esc_cama(L, e, t, D, T, st):
    a = amp(T)
    salon(L, T, a, t + 4, ("lampara", "ventana"))
    # cama
    rect(L, 170, 640, 500, 680, (90, 70, 120), r=6)
    rect(L, 160, 600, 176, SUELO, (110, 80, 60))
    rect(L, 494, 630, 510, SUELO, (110, 80, 60))
    rect(L, 176, 628, 494, 646, (240, 240, 250), r=6)
    tap = eio(prog(t, wt(e, "tápate") - 0.2, 0.6))
    persona(L, 360, 626, "cama", 0.62)
    # almohada sobre la cabeza
    px, py = lerp(210, 268, tap), lerp(624, 610, tap)
    rect(L, px - 34, py - 12, px + 34, py + 12, (250, 250, 255), r=10)
    rect(L, 300, 616, 500, 640, (100, 140, 200), r=6)   # manta
    st["paso"] = ("✓", "EN LA CAMA")
    st["shake_amp"] = a


def esc_despues(L, e, t, D, T, st):
    a = amp(T)
    # escalera en diagonal
    rect(L, 0, 0, W, H, (20, 18, 22))
    rect(L, 0, 170, W, SUELO + 40, (226, 214, 196))
    for j in range(10):
        x = 60 + j * 40
        y = 470 + j * 26
        rect(L, x, y, x + 46, SUELO + 40, (180, 160, 140))
        rect(L, x, y, x + 46, y + 6, (150, 130, 112))
    linea(L, [(60, 430), (460, 690)], (120, 100, 90), w=4)
    # ascensor tachado
    rect(L, 440, 360, 520, 520, (170, 175, 185), r=4)
    linea(L, [(480, 360), (480, 520)], (130, 135, 145), w=2)
    q = prog(t, wt(e, "ascensor") - 0.2, 0.4)
    if q > 0:
        st["overlay"].append(("cruz", 480, 440, q))
    u = prog(t, wt(e, "sal") - 0.1, D - 1.5)
    j = u * 9
    x = 80 + j * 40
    y = 470 + j * 26 - 190 * 0.62 + 4
    persona(L, x, y, pose_mix("camina1", "camina2", 0.5 + 0.5 * math.sin(t * 7)), 0.62)
    st["paso"] = ("✓", "CUANDO PARE")
    tr = wt(e, "réplicas") - 0.25
    if t > tr:
        st["overlay"].append(("replica", prog(t, tr, 0.3), t))
    st["shake_amp"] = a


def esc_final(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (24, 20, 26))
    items = [("agáchate", "AGÁCHATE", "↓"), ("cúbrete", "CÚBRETE", "▣"), ("agárrate", "AGÁRRATE", "✊")]
    for j, (pal, txt, ico) in enumerate(items):
        q = prog(t, wt(e, pal) - 0.15, 0.35)
        if q <= 0:
            continue
        y = 380 + j * 84
        s = eob(q)
        rect(L, 70, y - 34, 470, y + 34, (60, 54, 62), a=q, r=34)
        circ(L, 112, y, 26 * s, fill=AMARILLO, a=q)
        texto(L, str(j + 1), 112, y, 26 * s, (20, 20, 20), a=q, fuente="black", sombra=False)
        texto(L, txt, 156, y, 38 * (0.7 + 0.3 * s), BLANCO, a=q, fuente="black", anchor="lm")
    q = prog(t, wt(e, "Guarda") - 0.1, 0.4)
    if q > 0:
        lleno = prog(t, wt(e, "vídeo") - 0.1, 0.3)
        cx, cy, s = 270, 690, eob(q)
        w, h = 46 * s, 60 * s
        poly(L, [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx, cy + h / 2 - 17 * s),
                 (cx - w / 2, cy + h / 2)], mezcla((90, 90, 100), AMARILLO, lleno), a=q)
    st["sin_paso"] = True
    st["shake_amp"] = 0


FUNCS = {"gancho": esc_gancho, "marco": esc_marco, "salir": esc_salir, "tres": esc_tres, "mesa": esc_mesa,
         "cama": esc_cama, "despues": esc_despues, "final": esc_final}


# ------------------------------------------------------------------ overlays
def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "sello":
            _, txt, q, ang = it
            s = 1 + 1.5 * (1 - eo3(q))
            w = ancho(txt, 60 * s) + 40 * s
            rect(O, 270 - w / 2, 455 - 42 * s, 270 + w / 2, 455 + 42 * s, None, a=q, r=12 * s, outline=ROJO, w=6 * s)
            texto(O, txt, 270, 455, 60 * s, ROJO, a=q, fuente="black", sombra=False)
        elif tipo == "cruz":
            _, x, y, q = it
            k = eo3(q)
            r = 46
            linea(O, [(x - r, y - r), (x - r + 2 * r * min(1, k * 2), y - r + 2 * r * min(1, k * 2))], ROJO, w=12)
            if k > 0.5:
                kk = (k - 0.5) * 2
                linea(O, [(x + r, y - r), (x + r - 2 * r * kk, y - r + 2 * r * kk)], ROJO, w=12)
        elif tipo == "impacto":
            _, x, y, q = it
            for j in range(8):
                ang = j / 8 * 6.283
                r0, r1 = 14 + 10 * q, 30 + 26 * q
                linea(O, [(x + r0 * math.cos(ang), y + r0 * math.sin(ang)), (x + r1 * math.cos(ang), y + r1 * math.sin(ang))],
                      AMARILLO, w=4, a=1 - q * 0.5)
            texto(O, "¡PAM!", x + 20, y - 50, 26, AMARILLO, a=q, fuente="black")
        elif tipo == "palabra":
            _, txt, x, y, q, j = it
            s = eob(q)
            texto(O, txt, x, y, 34 * (0.6 + 0.4 * s), [AMARILLO, BLANCO, AMARILLO][j], a=q, fuente="black")
        elif tipo == "aro":
            _, x, y, q, t = it
            r = 26 + 4 * math.sin(t * 8)
            circ(O, x, y, r * eob(q), outline=VERDE, w=4, a=q)
        elif tipo == "replica":
            _, q, t = it
            parp = 0.6 + 0.4 * math.sin(t * 14)
            rect(O, 120, 540, 420, 600, ROJO, a=q * parp, r=30)
            texto(O, "⚠ RÉPLICA", 270, 570, 30, BLANCO, a=q, fuente="sym", sombra=False)


SISMO = []


def sismografo(O, T, a):
    """Trazo de sismógrafo que se desplaza bajo los subtítulos."""
    pts = []
    for i in range(110):
        tt = T - (110 - i) / 60
        ai = amp(max(0, tt))
        y = 312 + 16 * ai * (math.sin(tt * 61) * 0.6 + math.sin(tt * 37.3) * 0.4)
        pts.append((50 + i * 4.1, y))
    rect(O, 40, 292, 500, 332, (0, 0, 0), a=0.35, r=10)
    linea(O, pts, mezcla(VERDE, ROJO, cl(a * 1.3)), w=2)
    texto(O, "SISMÓGRAFO", 56, 300, 9, (200, 200, 200), fuente="bold", anchor="lm", sombra=False)


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
        v = np.clip(1.2 - r * 1.0, 0.45, 1)
        _VIN = Image.fromarray((v * 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR).convert("RGB")
    return _VIN


def render_frame(fr):
    T = fr / FPS
    e = escena_en(T)
    t = T - e["t0"]
    D = e["dur"]
    img = Image.new("RGB", (IW, IH), (0, 0, 0))
    L = Capa(img)
    st = {"overlay": [], "shake_amp": 0.0}
    FUNCS[e["nombre"]](L, e, t, D, T, st)
    img = L.img
    # cámara: ligero zoom para tener margen y temblor según la intensidad del terremoto
    z = 1.08
    dx, dy = temblor(T, st["shake_amp"], escala=14)
    cw, ch = IW / z, IH / z
    x0 = (IW - cw) / 2 + dx * K
    y0 = (IH - ch) / 2 + dy * K + 8 * K
    img = img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    overlays(O, st, T)
    if e["nombre"] != "final":
        sismografo(O, T, st["shake_amp"])
    paso(O, st, t)
    subtitulos(O, T)
    if T < 0.2:
        img = Image.blend(Image.new("RGB", (IW, IH), (0, 0, 0)), img, T / 0.2)
    if T > TOTAL - 0.6:
        img = Image.blend(img, Image.new("RGB", (IW, IH), (0, 0, 0)), cl((T - (TOTAL - 0.6)) / 0.6))
    return img.resize((OW, OH), Image.LANCZOS).tobytes()


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




def musica(n):
    tt = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    beat = 60 / 110
    notas = [40, 40, 36, 38]
    k = 0
    while k * beat < TOTAL:
        t0 = k * beat
        a0 = int(t0 * SR)
        m = min(n - a0, int(0.4 * SR))
        if m > 0:
            u = np.arange(m) / SR
            f = 440 * 2 ** ((notas[(k // 8) % 4] - 69) / 12)
            out[a0:a0 + m] += 0.11 * np.tanh(2 * np.sin(2 * np.pi * f * u)) * np.exp(-u * 6)
            if k % 2 == 1:
                out[a0:a0 + min(m, 2000)] += 0.03 * np.sin(2 * np.pi * 1600 * u[:2000]) * np.exp(-u[:2000] * 80)
        k += 1
    for f, g in ((164.8, 0.03), (196, 0.025), (246.9, 0.02)):
        out += g * np.sin(2 * np.pi * f * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * tt))
    return out


def rumor(n):
    """Retumbar grave del terremoto modulado por la intensidad."""
    rng = np.random.default_rng(11)
    r = rng.standard_normal(n).astype(np.float32)
    r = np.convolve(r, np.ones(300) / 300, mode="same")
    r = np.convolve(r, np.ones(300) / 300, mode="same") * 40
    pasos = np.arange(0, TOTAL + 0.3, 0.01)
    env = np.array([amp(min(x, TOTAL - 0.01)) for x in pasos], np.float32)
    env = np.interp(np.arange(n) / SR, pasos, env).astype(np.float32)
    tt = np.arange(n) / SR
    grave = np.sin(2 * np.pi * 38 * tt + 2 * np.sin(2 * np.pi * 3 * tt))
    return (r * 0.5 + grave * 0.25) * env


def mezclar():
    n = int((TOTAL + 0.3) * SR)
    voz = np.zeros(n, np.float32)
    for e in ESC:
        colocar(voz, leer(os.path.join(BUILD, f"voz_{e['i']}.mp3")), e["voz_t0"])
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    mus = musica(n)
    fx = rumor(n) * 0.07
    g = ESC[0]
    colocar(fx, golpe() * 0.5, g["t0"] + 2.6, 0.5)              # cae el cuadro
    for k in range(4):
        colocar(fx, golpe() * 0.25, g["t0"] + 1.8 + k * 0.45, 0.3)  # libros
    colocar(fx, golpe(), g["t0"] + wt(g, "mito") - 0.2, 0.6)
    m = next(e for e in ESC if e["nombre"] == "marco")
    colocar(fx, golpe(), m["t0"] + wt(m, "golpearte") - 0.2, 0.7)
    s = next(e for e in ESC if e["nombre"] == "salir")
    for k in range(5):
        colocar(fx, cristal(), s["t0"] + 0.4 + k * 1.1, 0.35)
    d = next(e for e in ESC if e["nombre"] == "despues")
    colocar(fx, golpe(), d["t0"] + wt(d, "réplicas") - 0.25, 0.7)
    for j, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(j, 0.45), e["t0"] - 0.22, 0.3)
    env = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.45 * np.clip(env * 12, 0, 1)
    total = voz + (mus + fx * 0.8) * duck
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
