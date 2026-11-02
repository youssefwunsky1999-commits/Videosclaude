"""TikTok vertical «Mente404 FC — 200 seguidores»: estadio nocturno con la afición, nombres de
seguidores en tarjetas, alineación en el campo, sorteo del jugador del partido y llamada a seguir.

Los nombres se editan en seguidores.py.

    python3 voz.py && python3 video.py        -> seguidores_tiktok.mp4
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
SALIDA = os.path.join(AQUI, "seguidores_tiktok.mp4")

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


EXTRA = {"gancho": 0.6, "primero": 1.4, "ultimo": 1.4, "alineacion": 2.2, "mvp": 3.2, "cta": 0.4, "final": 2.2}
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
CLAVE = {"nadie", "200", "estadio", "persona", "primer", "último", "asiento", "alineación", "404", "hueco",
         "libre", "partido", "azar", "próximo", "síguenos", "comparte", "amigo", "nombre", "campo", "gracias", "1000"}


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
            for seq, num in ((["cuatro", "cero", "cuatro"], "404"), (["uno", "uno", "dos"], "112")):
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
            if limpio in ("doscientos", "mil"):
                tok = {"doscientos": "200", "mil": "1000"}[limpio] + tok[len(limpio):]
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


# --- Escenas del TikTok «Mente404 FC — 200 seguidores» (se insertan en video.py al montarlo) ---
from seguidores import CUENTA, META, OTROS, PRIMERO, TOTAL_SEGUIDORES, ULTIMO

TODOS = [PRIMERO] + OTROS + [ULTIMO]
_mvp_ruta = os.path.join(BUILD, "mvp.txt")
if os.path.exists(_mvp_ruta) and open(_mvp_ruta).read().strip() in TODOS:
    MVP = open(_mvp_ruta).read().strip()
else:
    MVP = random.SystemRandom().choice(TODOS)      # sorteo real entre los nombres del vídeo
    with open(_mvp_ruta, "w") as _f:
        _f.write(MVP)

NAVY = (24, 34, 72)
ORO = (240, 196, 80)
ORO2 = (255, 228, 140)
CESPED = (54, 150, 72)
CESPED2 = (46, 134, 64)
CAMISETAS = [(235, 128, 70), (24, 34, 72), (240, 240, 240), (235, 128, 70), (200, 60, 60), (24, 34, 72)]
PIELES = [(240, 196, 160), (214, 160, 120), (170, 112, 76), (250, 214, 180), (120, 80, 56)]

FILAS = []          # (y, escala, [x...])
for i in range(6):
    s = 0.62 + i * 0.09
    y = 440 + i * 62
    paso_x = 54 * s
    xs = [x for x in np.arange(18 + (i % 2) * paso_x / 2, W - 10, paso_x)]
    FILAS.append((y, s, xs))
rf = random.Random(21)
AFICION = []        # (fila, col, umbral de aparición, camiseta, piel, pelo)
for fi, (y, s, xs) in enumerate(FILAS):
    for ci, x in enumerate(xs):
        AFICION.append((fi, ci, rf.random(), rf.choice(CAMISETAS), rf.choice(PIELES),
                        rf.choice([(40, 30, 26), (90, 60, 30), (20, 20, 20), (200, 160, 80)]), rf.random() * 6.28))
SITIO_PRIMERO = (3, 4)
SITIO_ULTIMO = (5, 6)
SITIO_LIBRE = (5, 3)


def pos_sitio(fi, ci):
    y, s, xs = FILAS[fi]
    return xs[ci], y, s


def aficionado(L, x, y, s, camiseta, piel, pelo, brazos=0.0, salto=0.0, aparece=1.0, fase=0.0):
    if aparece <= 0:
        return
    k = eob(aparece)
    s = s * k
    y = y - salto * 14 * s
    # brazos levantados al celebrar
    if brazos > 0:
        for lado in (-1, 1):
            hx, hy = x + lado * 15 * s, y - 30 * s
            mx = x + lado * (22 + 6 * math.sin(fase)) * s
            my = y - 30 * s - 44 * s * brazos
            capsula(L, (hx, hy), (mx, my), 8 * s, camiseta)
            circ(L, mx, my, 5.5 * s, fill=piel)
    rect(L, x - 17 * s, y - 36 * s, x + 17 * s, y + 8 * s, camiseta, r=10 * s)
    rect(L, x - 17 * s, y - 34 * s, x + 17 * s, y - 28 * s, ORO if camiseta == NAVY else NAVY, a=0.8)   # bufanda
    circ(L, x, y - 50 * s, 13 * s, fill=piel)
    L.d.pieslice(P(x - 13.5 * s, y - 64 * s, x + 13.5 * s, y - 40 * s), 180, 360, fill=L.c(pelo))
    circ(L, x - 4.5 * s, y - 49 * s, 1.8 * s + 0.4, fill=(30, 26, 24))
    circ(L, x + 4.5 * s, y - 49 * s, 1.8 * s + 0.4, fill=(30, 26, 24))
    if brazos > 0.5:
        circ(L, x, y - 43 * s, 3 * s, fill=(120, 50, 46))


def estadio(L, T, llenado=1.0, celebra=0.0, oscuro=0.0, sin=()):
    # cielo nocturno
    for i in range(0, 420, 6):
        rect(L, 0, i, W, i + 6, mezcla((8, 10, 24), (28, 36, 70), i / 420))
    rs = random.Random(1)
    for _ in range(40):
        circ(L, rs.uniform(0, W), rs.uniform(0, 300), rs.uniform(0.5, 1.4), fill=BLANCO, a=0.5)
    # torres de focos
    for fx in (50, 490):
        linea(L, [(fx, 140), (fx + (20 if fx < 270 else -20), 420)], (60, 66, 80), w=5)
        rect(L, fx - 34, 112, fx + 34, 146, (50, 54, 66), r=4)
        for gx in range(4):
            for gy in range(2):
                circ(L, fx - 24 + gx * 16, 122 + gy * 14, 5.5, fill=(255, 250, 220))
        d = 1 if fx < 270 else -1
        poly(L, [(fx - 30, 146), (fx + 30, 146), (fx + d * 330, 900), (fx + d * 80, 900)], (255, 250, 220), a=0.05)
    # techo y gradas
    rect(L, 0, 392, W, 410, (40, 44, 56))
    rect(L, 0, 410, W, 800, (52, 56, 70))
    for fi, (y, s, xs) in enumerate(FILAS):
        rect(L, 0, y - 6 * s, W, y + 18 * s, mezcla((90, 30, 40), (150, 40, 50), fi / 5))
        for x in xs:
            rect(L, x - 16 * s, y - 22 * s, x + 16 * s, y + 4 * s, (170, 50, 60), r=5 * s)
    # afición
    for (fi, ci, umbral, cam, piel, pelo, fase) in AFICION:
        if (fi, ci) in sin:
            continue
        y, s, xs = FILAS[fi]
        x = xs[ci]
        ap = cl((llenado - umbral) * 12)
        salto = celebra * max(0, math.sin(T * 9 + fase)) if celebra else 0.15 * max(0, math.sin(T * 2 + fase))
        aficionado(L, x, y, s, cam, piel, pelo, brazos=celebra, salto=salto, aparece=ap, fase=T * 8 + fase)
    # vallas publicitarias LED
    rect(L, 0, 800, W, 840, (14, 14, 20))
    txt = f"MENTE404 FC · GRACIAS · {TOTAL_SEGUIDORES} · @{CUENTA} · "
    off = (T * 60) % ancho(txt, 20, "black")
    texto(L, txt * 3, -off, 820, 20, ORO, fuente="black", anchor="lm", sombra=False)
    # césped
    for i, y in enumerate(range(840, H, 24)):
        rect(L, 0, y, W, y + 24, CESPED if i % 2 == 0 else CESPED2)
    linea(L, [(0, 852), (W, 852)], BLANCO, w=3)
    if oscuro > 0:
        rect(L, 0, 0, W, H, (0, 0, 0), a=oscuro)


def foco(O, x, y, r, q):
    """Oscurece todo menos un círculo (cañón de luz)."""
    if q <= 0:
        return
    m = Image.new("L", (IW // 4, IH // 4), int(170 * q))
    d = ImageDraw.Draw(m)
    k = K / 4
    d.ellipse(((x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(6)).resize((IW, IH), Image.BILINEAR)
    negro = Image.new("RGB", (IW, IH), (0, 0, 0))
    O.img.paste(negro, (0, 0), m)
    O.d = ImageDraw.Draw(O.img, "RGBA")
    poly(O, [(x - 30, 0), (x + 30, 0), (x + r, y), (x - r, y)], (255, 250, 220), a=0.12 * q)


def tarjeta(O, x, y, titulo, nombre, numero, q, color=ORO):
    if q <= 0:
        return
    s = eob(q)
    w, h = 190 * s, 120 * s
    rect(O, x - w / 2, y - h / 2 + 6, x + w / 2, y + h / 2 + 6, (0, 0, 0), a=0.4 * q, r=16 * s)
    rect(O, x - w / 2, y - h / 2, x + w / 2, y + h / 2, color, a=q, r=16 * s)
    rect(O, x - w / 2 + 5 * s, y - h / 2 + 5 * s, x + w / 2 - 5 * s, y + h / 2 - 5 * s, None, a=q, r=12 * s,
         outline=ORO2, w=2)
    texto(O, titulo, x, y - 36 * s, 13 * s, NAVY, a=q, fuente="black", sombra=False)
    size = 22 * s
    while ancho("@" + nombre, size) > w - 24 and size > 10:
        size -= 1
    texto(O, "@" + nombre, x, y + 2 * s, size, NAVY, a=q, fuente="black", sombra=False)
    texto(O, numero, x, y + 36 * s, 15 * s, (120, 70, 20), a=q, fuente="black", sombra=False)


def marcador(O, valor, q=1.0, titulo="SEGUIDORES"):
    rect(O, 150, 296, 390, 380, (10, 12, 18), a=q, r=10, outline=(70, 74, 90), w=2)
    texto(O, titulo, 270, 314, 13, (180, 180, 190), a=q, fuente="black", sombra=False)
    texto(O, f"{int(valor):03d}", 270, 350, 42, ORO, a=q, fuente="mono", sombra=False)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    t0 = wt(e, "Hoy") - 0.3
    t1 = wt(e, "doscientos") + 0.3
    valor = TOTAL_SEGUIDORES * eio(prog(t, t0, t1 - t0))
    estadio(L, T, llenado=valor / TOTAL_SEGUIDORES, celebra=prog(t, t1, 0.4))
    st["overlay"].append(("marcador", valor, 1.0))
    if t > t1:
        st["confeti"] = t - t1


def esc_primero(L, e, t, D, T, st):
    estadio(L, T, llenado=1.0)
    x, y, s = pos_sitio(*SITIO_PRIMERO)
    q = prog(t, 0.2, 0.5)
    st["foco"] = (x, y - 30 * s, 62, q)
    st["overlay"].append(("tarjeta", x + (110 if x < 270 else -110), y - 190, "PRIMER SEGUIDOR", PRIMERO, "#1",
                          prog(t, wt(e, "primer") - 0.2, 0.5)))
    st["zoom"] = (1.0 + 0.35 * eio(prog(t, 0.1, 1.2)), (x, y - 60))


def esc_ultimo(L, e, t, D, T, st):
    estadio(L, T, llenado=1.0)
    x, y, s = pos_sitio(*SITIO_ULTIMO)
    q = prog(t, 0.2, 0.5)
    st["foco"] = (x, y - 30 * s, 66, q)
    st["overlay"].append(("tarjeta", x + (110 if x < 270 else -110), y - 190, "ÚLTIMO EN LLEGAR", ULTIMO,
                          f"#{TOTAL_SEGUIDORES}", prog(t, wt(e, "último") - 0.2, 0.5)))
    st["zoom"] = (1.0 + 0.35 * eio(prog(t, 0.1, 1.2)), (x, y - 60))


FORMACION = [  # (x, y, dorsal, nombre)
    (245, 770, "1", PRIMERO),
    (70, 660, "2", OTROS[0]), (190, 680, "4", OTROS[1]), (300, 680, "5", OTROS[2]), (420, 660, "3", OTROS[3]),
    (110, 545, "6", OTROS[4]), (245, 560, "8", OTROS[5]), (380, 545, "7", OTROS[6]),
    (100, 420, "11", OTROS[7]), (245, 400, "10", None), (390, 420, "9", ULTIMO),
]


def campo(L):
    rect(L, 0, 0, W, H, (16, 40, 24))
    x0, y0, x1, y1 = 20, 330, 470, 840
    for i, yy in enumerate(range(y0, y1, 34)):
        rect(L, x0, yy, x1, min(y1, yy + 34), CESPED if i % 2 == 0 else CESPED2)
    c = (230, 240, 230)
    rect(L, x0, y0, x1, y1, None, outline=c, w=3)
    linea(L, [(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], c, w=2)
    circ(L, (x0 + x1) / 2, (y0 + y1) / 2, 50, outline=c, w=2)
    rect(L, 140, y1 - 80, 350, y1, None, outline=c, w=2)
    rect(L, 140, y0, 350, y0 + 80, None, outline=c, w=2)


def jugador(O, x, y, dorsal, nombre, q, t, libre=False):
    if q <= 0:
        return
    s = eob(q)
    col = (235, 128, 70) if dorsal != "1" else (90, 200, 120)
    if libre:
        col = mezcla((80, 80, 90), ORO, 0.5 + 0.5 * math.sin(t * 6))
    # camiseta
    pts = [(-16, -16), (-6, -20), (6, -20), (16, -16), (24, -6), (16, 0), (14, 20), (-14, 20), (-16, 0), (-24, -6)]
    poly(O, [(x + px * s, y + py * s) for px, py in pts], col, a=q)
    texto(O, dorsal, x, y + 2 * s, 15 * s, NAVY if not libre else BLANCO, a=q, fuente="black", sombra=False)
    etiqueta = "¿TÚ?" if libre else nombre
    size = 14.5
    while ancho(etiqueta, size, "bold") > 124 and size > 8:
        size -= 0.5
    w = ancho(etiqueta, size, "bold") + 16
    rect(O, x - w / 2, y + 25 * s, x + w / 2, y + 47 * s, (0, 0, 0) if not libre else ORO, a=0.75 * q, r=9)
    texto(O, etiqueta, x, y + 36 * s, size, BLANCO if not libre else NAVY, a=q, fuente="bold", sombra=False)


def esc_alineacion(L, e, t, D, T, st):
    campo(L)
    t0 = wt(e, "alineación") - 0.3
    st["alineacion"] = (t0, wt(e, "hueco") - 0.3, t)
    st["paso"] = ("11", f"ALINEACIÓN · {CUENTA.upper()}")


def esc_mvp(L, e, t, D, T, st):
    estadio(L, T, llenado=1.0, oscuro=0.55, celebra=0.0)
    t_spin = 0.3
    t_stop = wt(e, "es") + 0.9
    st["mvp"] = (t, t_spin, t_stop)
    if t > t_stop + 0.15:
        st["confeti"] = t - t_stop
        st["celebra"] = True


def esc_cta(L, e, t, D, T, st):
    estadio(L, T, llenado=1.0, sin=(SITIO_LIBRE,))
    x, y, s = pos_sitio(*SITIO_LIBRE)
    st["foco"] = (x, y - 10, 58, prog(t, 0.2, 0.5))
    st["zoom"] = (1.0 + 0.2 * eio(prog(t, 0.1, 1.2)), (x, y - 120))
    st["overlay"].append(("libre", x, y, t))
    st["overlay"].append(("botones", t, wt(e, "Síguenos") - 0.2, wt(e, "comparte") - 0.2))


def esc_final(L, e, t, D, T, st):
    estadio(L, T, llenado=1.0, celebra=1.0)
    st["confeti"] = t + 1.0
    st["overlay"].append(("meta", prog(t, wt(e, "mil") - 0.6, 1.2), t))
    st["sin_paso"] = True


FUNCS = {"gancho": esc_gancho, "primero": esc_primero, "ultimo": esc_ultimo, "alineacion": esc_alineacion,
         "mvp": esc_mvp, "cta": esc_cta, "final": esc_final}

rcf = random.Random(9)
CONFETI = [(rcf.uniform(0, W), rcf.uniform(-300, 0), rcf.uniform(60, 160), rcf.choice([ORO, BLANCO, (235, 128, 70), AZUL, ROJO]),
            rcf.uniform(4, 8), rcf.random() * 6.28) for _ in range(140)]


def confeti(O, dt):
    for (x, y0, v, col, sz, f) in CONFETI:
        y = y0 + v * dt * 1.6
        if y > H or y < -10:
            continue
        xx = x + 18 * math.sin(dt * 3 + f)
        h = sz * 0.5 * abs(math.cos(dt * 6 + f)) + 1
        rect(O, xx - sz / 2, y - h / 2, xx + sz / 2, y + h / 2, col)


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "marcador":
            marcador(O, it[1], it[2])
        elif tipo == "tarjeta":
            _, x, y, tit, nombre, num, q = it
            x = cl(x, 110, 380)
            tarjeta(O, x, y, tit, nombre, num, q)
        elif tipo == "libre":
            _, x, y, t = it
            parp = 0.6 + 0.4 * math.sin(t * 6)
            rect(O, x - 16, y - 50, x + 16, y + 6, ORO, a=0.25 * parp, r=8)
            texto(O, "?", x, y - 26, 30, ORO, a=parp, fuente="black")
            w = ancho("TU NOMBRE AQUÍ", 17) + 24
            rect(O, x - w / 2, y - 120, x + w / 2, y - 86, ORO, a=0.95, r=17)
            texto(O, "TU NOMBRE AQUÍ", x, y - 103, 17, NAVY, fuente="black", sombra=False)
            poly(O, [(x - 8, y - 87), (x + 8, y - 87), (x, y - 76)], ORO)
        elif tipo == "botones":
            _, t, ts, tc = it
            for j, (t0, etiqueta, ico) in enumerate([(ts, "SEGUIR", "+"), (tc, "COMPARTIR", "↗")]):
                q = prog(t, t0, 0.4)
                if q <= 0:
                    continue
                x, y = 160 + j * 220, 700
                s = eob(q)
                toque = prog(t, t0 + 0.6, 0.35)
                sc = s * (1 - 0.12 * math.sin(toque * math.pi))
                col = (254, 44, 85) if j == 0 else (40, 160, 230)
                rect(O, x - 95 * sc, y - 30 * sc, x + 95 * sc, y + 30 * sc, col, a=q, r=30 * sc)
                texto(O, f"{ico} {etiqueta}", x, y, 22 * sc, BLANCO, a=q, fuente="sym", sombra=False)
                if 0 < toque < 1:
                    circ(O, x + 40, y + 10, 14 + 40 * toque, outline=BLANCO, w=3, a=1 - toque)
                    circ(O, x + 40, y + 10, 10, fill=BLANCO, a=1 - toque)
        elif tipo == "meta":
            _, q, t = it
            texto(O, "¡GRACIAS!", 270, 330, 58, ORO, fuente="black")
            texto(O, f"@{CUENTA}", 270, 385, 22, BLANCO, fuente="black")
            if q > 0:
                rect(O, 70, 600, 470, 630, (0, 0, 0), a=0.6 * q, r=15)
                frac = TOTAL_SEGUIDORES / META
                rect(O, 74, 604, 74 + 392 * frac * eo3(q), 626, ORO, a=q, r=11)
                texto(O, f"{TOTAL_SEGUIDORES}", 70, 655, 18, BLANCO, a=q, fuente="black", anchor="lm")
                texto(O, f"META: {META}", 470, 655, 18, ORO, a=q, fuente="black", anchor="rm")


def capa_alineacion(O, st):
    if "alineacion" not in st:
        return
    t0, t_hueco, t = st["alineacion"]
    for j, (x, y, dorsal, nombre) in enumerate(FORMACION):
        libre = nombre is None
        tj = t_hueco if libre else t0 + j * 0.32
        jugador(O, x, y, dorsal, nombre, prog(t, tj, 0.35), t, libre=libre)


def capa_mvp(O, st):
    if "mvp" not in st:
        return
    t, t_spin, t_stop = st["mvp"]
    texto(O, "JUGADOR DEL PARTIDO", 270, 400, 26, ORO, fuente="black")
    texto(O, "elegido al azar", 270, 432, 16, (210, 210, 210), fuente="semi")
    x0, x1, yc = 70, 470, 540
    rect(O, x0, yc - 70, x1, yc + 70, (12, 14, 24), a=0.92, r=18, outline=ORO, w=3)
    idx_final = TODOS.index(MVP)
    n = len(TODOS)
    # posición de la "ruleta": decelera hasta el nombre sorteado
    vueltas = 4
    total = vueltas * n + idx_final
    u = eo3(prog(t, t_spin, t_stop - t_spin))
    pos = total * u
    clip = Image.new("L", O.img.size, 0)
    ImageDraw.Draw(clip).rounded_rectangle(P(x0 + 4, yc - 66, x1 - 4, yc + 66), radius=14 * K, fill=255)
    capa = Image.new("RGBA", O.img.size, (0, 0, 0, 0))
    C = Capa(capa)
    for k in range(-2, 3):
        i = int(math.floor(pos)) + k
        frac = pos - math.floor(pos)
        y = yc + (k - frac) * 56
        nombre = TODOS[i % n]
        size = 26
        while ancho("@" + nombre, size) > 380 and size > 12:
            size -= 1
        a = cl(1 - abs(y - yc) / 120)
        col = ORO if abs(y - yc) < 20 and u >= 1 else BLANCO
        texto(C, "@" + nombre, 270, y, size, col, a=a, fuente="black", sombra=False)
    O.img.paste(capa, (0, 0), ImageChops.multiply(clip, capa.getchannel("A")))
    O.d = ImageDraw.Draw(O.img, "RGBA")
    linea(O, [(x0 + 10, yc - 26), (x0 + 10, yc + 26)], ORO, w=4)
    linea(O, [(x1 - 10, yc - 26), (x1 - 10, yc + 26)], ORO, w=4)
    q = prog(t, t_stop + 0.1, 0.5)
    if q > 0:
        tarjeta(O, 270, 712, "MVP", MVP, "JUGADOR DEL PARTIDO", q)


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
        v = np.clip(1.25 - r * 1.0, 0.5, 1)
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
    img = L.img
    # cañón de luz (en coordenadas de escena, antes del zoom)
    if "foco" in st:
        x, y, r, q = st["foco"]
        foco(Capa(img), x, y, r, q)
    z, (fx, fy) = st.get("zoom", (1.0, (270, 480)))
    if z != 1.0:
        cw, ch = IW / z, IH / z
        x0 = cl(fx * K - cw / 2, 0, IW - cw)
        y0 = cl(fy * K - ch / 2, 0, IH - ch)
        img = img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
        # las tarjetas siguen al zoom
        for k, it in enumerate(st["overlay"]):
            if it[0] in ("tarjeta", "libre"):
                it = list(it)
                it[1] = (it[1] * K - x0) / cw * W
                it[2] = (it[2] * K - y0) / ch * H
                st["overlay"][k] = tuple(it)
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    capa_alineacion(O, st)
    capa_mvp(O, st)
    overlays(O, st, T)
    if "confeti" in st:
        confeti(O, st["confeti"])
    paso(O, st, t)
    subtitulos(O, T)
    if T < 0.2:
        img = Image.blend(Image.new("RGB", (IW, IH), (0, 0, 0)), O.img, T / 0.2)
        O = Capa(img)
    if T > TOTAL - 0.6:
        O = Capa(Image.blend(O.img, Image.new("RGB", (IW, IH), (0, 0, 0)), cl((T - (TOTAL - 0.6)) / 0.6)))
    return O.img.resize((OW, OH), Image.LANCZOS).tobytes()


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


def musica(n):
    """Himno alegre: bombo, palmas, bajo y acordes (Do-Sol-Lam-Fa) a 124 bpm."""
    tt = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    beat = 60 / 124
    acordes = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
    rng = np.random.default_rng(6)
    k = 0
    while k * beat < TOTAL:
        t0 = k * beat
        a0 = int(t0 * SR)
        ac = acordes[(k // 8) % 4]
        m = min(n - a0, int(0.5 * SR))
        if m > 0:
            u = np.arange(m) / SR
            out[a0:a0 + m] += 0.16 * np.sin(2 * np.pi * (45 + 80 * np.exp(-u * 30)) * u) * np.exp(-u * 8)  # bombo
            out[a0:a0 + m] += 0.06 * np.sin(2 * np.pi * nota(ac[0] - 24) * u) * np.exp(-u * 3)            # bajo
            if k % 2 == 1:
                ruido = rng.standard_normal(m).astype(np.float32)
                out[a0:a0 + m] += 0.07 * np.diff(ruido, prepend=0) * np.exp(-u * 25)                          # palmas
            for j, mm in enumerate(ac):
                if (k + j) % 2 == 0:
                    out[a0:a0 + m] += 0.02 * np.sin(2 * np.pi * nota(mm + 12) * u) * np.exp(-u * 4)
        k += 1
    return out


def afición(n, niveles):
    """Rumor de la grada: ruido filtrado cuyo volumen sigue la curva `niveles`."""
    rng = np.random.default_rng(12)
    r = rng.standard_normal(n).astype(np.float32)
    r = np.convolve(r, np.ones(6) / 6, mode="same") - np.convolve(r, np.ones(60) / 60, mode="same")
    pasos = np.arange(0, TOTAL + 0.3, 0.05)
    env = np.interp(np.arange(n) / SR, pasos, np.array([niveles(x) for x in pasos]))
    # oleaje del público
    env *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.3 * np.arange(n) / SR)
    return (r * env * 1.6).astype(np.float32)


def silbato():
    n = int(0.9 * SR)
    tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * 2900 * tt + 8 * np.sin(2 * np.pi * 28 * tt)) * (tt < 0.35)
    s += np.sin(2 * np.pi * 2900 * tt + 8 * np.sin(2 * np.pi * 28 * tt)) * (tt > 0.45) * np.exp(-(tt - 0.45) * 3)
    return (s * 0.4).astype(np.float32)


def ding():
    n = int(1.2 * SR)
    tt = np.arange(n) / SR
    return ((np.sin(2 * np.pi * 1320 * tt) + 0.5 * np.sin(2 * np.pi * 1980 * tt)) * np.exp(-tt * 4) * 0.5).astype(np.float32)


def nivel_aficion(T):
    e = escena_en(T)
    t = T - e["t0"]
    n = e["nombre"]
    if n == "gancho":
        return 0.15 + 0.6 * prog(t, wt(e, "Hoy") - 0.3, 3.0) + 0.6 * prog(t, wt(e, "doscientos") + 0.3, 0.3) * math.exp(-max(0, t - wt(e, "doscientos") - 0.6))
    if n == "mvp":
        ts = wt(e, "es") + 0.9
        return 0.2 + (1.3 * math.exp(-max(0, t - ts) * 0.8) if t > ts else 0)
    if n == "final":
        return 1.0
    if n == "alineacion":
        return 0.25
    return 0.45


def mezclar():
    n = int((TOTAL + 0.3) * SR)
    voz = np.zeros(n, np.float32)
    for e in ESC:
        colocar(voz, leer(os.path.join(BUILD, f"voz_{e['i']}.mp3")), e["voz_t0"])
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    mus = musica(n) * 0.8
    fx = afición(n, nivel_aficion) * 0.25
    colocar(fx, silbato(), 0.15, 0.35)
    for j, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(j, 0.45), e["t0"] - 0.22, 0.3)
    # tic-tac de la ruleta del MVP
    m = next(e for e in ESC if e["nombre"] == "mvp")
    t_spin, t_stop = 0.3, wt(m, "es") + 0.9
    pos_ant = 0
    for k in range(int((t_stop - t_spin) * 200)):
        u = k / ((t_stop - t_spin) * 200)
        pos = (4 * len(TODOS) + TODOS.index(MVP)) * eo3(u)
        if int(pos) != pos_ant:
            colocar(fx, tic(), m["t0"] + t_spin + k / 200, 0.25)
            pos_ant = int(pos)
    colocar(fx, ding(), m["t0"] + t_stop + 0.1, 0.5)
    # entradas de las tarjetas
    for nombre, pal in (("primero", "primer"), ("ultimo", "último")):
        e = next(x for x in ESC if x["nombre"] == nombre)
        colocar(fx, ding() * 0.5, e["t0"] + wt(e, pal) - 0.2, 0.35)
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
