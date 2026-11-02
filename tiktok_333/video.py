"""TikTok vertical de terror «El mensaje de las 3:33» (ficción original): dormitorio de noche, mensaje desde el
propio número, golpes en la puerta, susurro con otra voz, foto en visión nocturna y susto final con glitch.

    python3 voz.py && python3 video.py        -> 333_tiktok.mp4"""
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
SALIDA = os.path.join(AQUI, "333_tiktok.mp4")

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


EXTRA = {"golpes": 0.8, "susurro": 0.4, "foto": 0.5, "ultimo": 1.4, "final": 1.2}
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
CLAVE = {"número…", "abras", "lucía.", "sola.", "despertó", "3:33.", "mensaje…", "número.", "puerta.", "yo.", "broma.",
         "golpes.", "susurró:", "frío.", "like.", "peor", "vibró.", "foto,", "rincón", "algo", "mirándola.", "último",
         "ti.", "vio.", "333", "dos."}


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
            for seq, num in ((["tres", "tres", "tres"], "333"), (["uno", "uno", "dos"], "112")):
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


# --- Escenas del TikTok de terror «El mensaje de las 3:33» (se insertan en video.py al montarlo) ---

POSES.update({
    "en_cama": dict(rodilla=(70, -4), pie=(140, 2), cuello=(-6, -118), cabeza=(-2, -158), codo=(30, -60), mano=(70, -50),
                    codo2=(24, -64), mano2=(62, -54)),
    "en_cama_movil": dict(rodilla=(70, -4), pie=(140, 2), cuello=(-2, -118), cabeza=(6, -156), codo=(34, -84), mano=(64, -120),
                          codo2=(28, -80), mano2=(58, -116)),
    "dormida": dict(rodilla=(72, -14), pie=(146, -2), cuello=(-112, -4), cabeza=(-152, -18), codo=(-60, -30), mano=(-20, -20),
                    codo2=(-50, -26), mano2=(-10, -16)),
    "de_pie_miedo": dict(rodilla=(4, 95), pie=(2, 190), cuello=(-6, -146), cabeza=(-14, -188), codo=(-30, -100), mano=(-20, -150),
                         codo2=(-20, -96), mano2=(-6, -150)),
})

NOCHE = (6, 8, 16)
LUNA = (150, 170, 220)
PIJAMA = ((150, 120, 190), (120, 96, 160), (150, 120, 190), (120, 96, 160))
PELO_L = (60, 34, 24)
ROJO_D = (255, 40, 40)
VERDE_NV = (90, 255, 120)
CABECERA = "EL MENSAJE DE LAS 3:33"


def melena(L, info, s=0.6, flip=False):
    cx, cy = info["cabeza"]
    r = 34 * s
    d = -1 if flip else 1
    poly(L, [(cx - r * 0.9 * d, cy - r * 0.6), (cx - r * 0.1 * d, cy - r * 1.05), (cx - r * 1.2 * d, cy + r * 1.6),
             (cx - r * 0.5 * d, cy + r * 1.5)], PELO_L)


def dormitorio(L, T, luz=1.0, puerta_luz=0.0, pies=0.0, golpe=0.0, telefono_luz=0.0):
    rect(L, 0, 0, W, H, NOCHE)
    rect(L, 0, 300, W, 780, (18, 20, 34))
    # ventana con luna
    rect(L, 40, 360, 180, 520, (24, 30, 56))
    circ(L, 110, 420, 26, fill=LUNA, a=0.9 * luz)
    linea(L, [(110, 360), (110, 520)], (40, 44, 70), w=4)
    linea(L, [(40, 440), (180, 440)], (40, 44, 70), w=4)
    poly(L, [(40, 520), (180, 520), (300, 780), (120, 780)], LUNA, a=0.05 * luz)
    # puerta (derecha)
    dx = 4 * golpe * math.sin(T * 80)
    rect(L, 390 + dx, 400, 500 + dx, 780, (40, 32, 30))
    rect(L, 384, 394, 506, 404, (30, 26, 26))
    circ(L, 404 + dx, 600, 5, fill=(150, 140, 100))
    if puerta_luz > 0:
        rect(L, 390, 776, 500, 782, (255, 220, 160), a=puerta_luz)
        if pies > 0:
            for k, x in enumerate((420, 466)):
                rect(L, x + 6 * math.sin(T * 1.3 + k), 776, x + 18 + 6 * math.sin(T * 1.3 + k), 782, (0, 0, 0), a=pies)
            poly(L, [(390, 782), (500, 782), (520, 900), (370, 900)], (255, 220, 160), a=0.06 * puerta_luz)
    rect(L, 0, 780, W, H, (14, 14, 22))
    # cama y mesita con reloj
    rect(L, 40, 660, 330, 700, (40, 40, 70), r=6)
    rect(L, 30, 600, 46, 790, (60, 44, 36))
    rect(L, 324, 640, 340, 790, (60, 44, 36))
    rect(L, 46, 640, 120, 662, (200, 200, 220), r=8)
    rect(L, 120, 646, 330, 668, (70, 60, 110), r=6)
    rect(L, 340, 680, 384, 780, (50, 38, 32))
    rect(L, 344, 656, 380, 680, (10, 10, 12), r=3)
    texto(L, "3:33", 362, 668, 13, ROJO_D, fuente="mono", sombra=False)
    if telefono_luz > 0:
        circ(L, 362, 676, 40, fill=(140, 180, 255), a=0.12 * telefono_luz)


def movil(O, x, y, s=1.0, a=1.0, vibra=0.0, T=0.0):
    dx = vibra * 3 * math.sin(T * 90)
    w, h = 230 * s, 430 * s
    x0, y0 = x - w / 2 + dx, y - h / 2
    rect(O, x0, y0, x0 + w, y0 + h, (12, 12, 14), a=a, r=28 * s)
    rect(O, x0 + 10 * s, y0 + 14 * s, x0 + w - 10 * s, y0 + h - 14 * s, (18, 22, 34), a=a, r=20 * s)
    rect(O, x - 30 * s + dx, y0 + 20 * s, x + 30 * s + dx, y0 + 30 * s, (8, 8, 10), a=a, r=5 * s)
    return x0 + dx, y0, w, h


def burbuja_chat(O, x, y, txt, a=1.0, ancho_max=190, propia=False, size=15):
    palabras = txt.split()
    lineas = []
    cur = ""
    for p in palabras:
        prueba = (cur + " " + p).strip()
        if ancho(prueba, size, "semi") > ancho_max - 24 and cur:
            lineas.append(cur)
            cur = p
        else:
            cur = prueba
    lineas.append(cur)
    w = max(ancho(l, size, "semi") for l in lineas) + 24
    h = len(lineas) * (size + 6) + 14
    col = (40, 110, 230) if propia else (52, 56, 70)
    x0 = x if not propia else x - w
    rect(O, x0, y, x0 + w, y + h, col, a=a, r=14)
    for k, l in enumerate(lineas):
        texto(O, l, x0 + 12, y + 14 + k * (size + 6) + size / 2 - 2, size, BLANCO, a=a, fuente="semi", anchor="lm",
              sombra=False)
    return h


def ente(L, x, y, s=1.0, a=1.0, ojos=1.0, col=(4, 4, 6)):
    """Figura alta y delgada con ojos blancos."""
    poly(L, [(x - 18 * s, y), (x - 26 * s, y - 220 * s), (x - 14 * s, y - 300 * s), (x + 14 * s, y - 300 * s),
             (x + 26 * s, y - 220 * s), (x + 18 * s, y)], col, a=a)
    circ(L, x, y - 330 * s, 32 * s, fill=col, a=a)
    for lado in (-1, 1):
        linea(L, [(x + lado * 22 * s, y - 280 * s), (x + lado * 46 * s, y - 160 * s), (x + lado * 40 * s, y - 40 * s)], col,
              w=8 * s, a=a)
    if ojos > 0:
        for lado in (-1, 1):
            circ(L, x + lado * 11 * s, y - 334 * s, 6 * s, fill=(240, 240, 240), a=a * ojos)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, NOCHE)
    st["overlay"].append(("bloqueo", t, e, T))


def esc_lucia(L, e, t, D, T, st):
    tw = wt(e, "despertó") - 0.2
    dormitorio(L, T)
    if t < tw:
        info = persona(L, 220, 652, "dormida", 0.55, ropa=PIJAMA, pelo=PELO_L, ojos=0.1)
    else:
        k = eio(prog(t, tw, 0.6))
        info = persona(L, lerp(200, 110, k), 652, pose_mix("dormida", "en_cama", k), 0.55, ropa=PIJAMA, pelo=PELO_L,
                       ojos=0.1 if k < 0.7 else 1.4)
        melena(L, info, 0.55)
    rect(L, 120, 646, 330, 668, (70, 60, 110), r=6)    # manta por encima
    q = prog(t, wt(e, "3:33") - 0.2, 0.4)
    if q > 0:
        st["overlay"].append(("reloj333", q, t))


def esc_mensaje(L, e, t, D, T, st):
    dormitorio(L, T, telefono_luz=1.0)
    info = persona(L, 110, 652, "en_cama_movil", 0.55, ropa=PIJAMA, pelo=PELO_L, ojos=1.4)
    melena(L, info, 0.55)
    rect(L, 120, 646, 330, 668, (70, 60, 110), r=6)
    st["overlay"].append(("chat", t, prog(t, wt(e, "propio") - 0.3, 0.4), None, T))


def esc_texto(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, NOCHE)
    st["overlay"].append(("chat", t, 1.0, prog(t, wt(e, "No", 0) - 0.3, 0.3), T))
    if t > wt(e, "soy") - 0.2:
        st["glitch"] = 0.6 * math.exp(-(t - wt(e, "soy") + 0.2) * 3)


def esc_golpes(L, e, t, D, T, st):
    tl = wt(e, "llamaron") - 0.1
    golpes = [tl + 0.2, tl + 0.75, tl + 1.3] if tl else []
    g = 0
    for tg in golpes:
        if 0 <= t - tg < 0.2:
            g = 1
    dormitorio(L, T, puerta_luz=prog(t, tl - 0.4, 0.5), pies=prog(t, tl, 0.6), golpe=g)
    info = persona(L, 110, 652, "en_cama", 0.55, ropa=PIJAMA, pelo=PELO_L, ojos=1.6)
    melena(L, info, 0.55)
    rect(L, 120, 646, 330, 668, (70, 60, 110), r=6)
    for k, tg in enumerate(golpes):
        q = prog(t, tg, 0.15)
        if q > 0:
            st["overlay"].append(("toc", k, q * (1 - prog(t, tg + 0.8, 0.3))))
    st["shake"] = 6 * g


def esc_voz(L, e, t, D, T, st):
    dormitorio(L, T, puerta_luz=1.0, pies=1.0)
    st["zoom_puerta"] = eio(t / D)
    info = persona(L, 110, 652, "en_cama", 0.55, ropa=PIJAMA, pelo=PELO_L, ojos=1.6)
    melena(L, info, 0.55)
    rect(L, 120, 646, 330, 668, (70, 60, 110), r=6)


def esc_susurro(L, e, t, D, T, st):
    dormitorio(L, T, puerta_luz=1.0 + 0.0, pies=1.0)
    st["zoom_puerta"] = 1.0
    st["glitch"] = 0.15 + 0.1 * math.sin(t * 7)
    st["susurro"] = True


def esc_like(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (16, 4, 8))
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    q = prog(t, wt(e, "peor") - 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("grande", "LO PEOR VIENE AHORA", 380, q, ROJO_D))


def esc_vibra(L, e, t, D, T, st):
    tp = wt(e, "pararon") - 0.3
    tv = wt(e, "vibró") - 0.3
    dormitorio(L, T, puerta_luz=1 - prog(t, tp, 0.6), pies=1 - prog(t, tp, 0.4), telefono_luz=prog(t, tv, 0.2))
    info = persona(L, 110, 652, "en_cama", 0.55, ropa=PIJAMA, pelo=PELO_L, ojos=1.6)
    melena(L, info, 0.55)
    rect(L, 120, 646, 330, 668, (70, 60, 110), r=6)
    if t > tv:
        st["overlay"].append(("movil_vibra", t, T))


def esc_foto(L, e, t, D, T, st):
    ta = wt(e, "algo") - 0.4
    # foto en visión nocturna, tomada desde el rincón
    rect(L, 0, 0, W, H, (4, 16, 6))
    q = prog(t, 0.2, 0.5)
    x0, y0, x1, y1 = 50, 340, 490, 800
    rect(L, x0, y0, x1, y1, (10, 40, 16), a=q)
    # cama en perspectiva
    poly(L, [(80, 700), (380, 640), (470, 700), (170, 780)], (30, 90, 40), a=q)
    poly(L, [(110, 690), (190, 676), (210, 700), (130, 714)], (60, 150, 70), a=q)
    poly(L, [(170, 700), (380, 656), (440, 690), (230, 740)], (40, 120, 54), a=q)
    circ(L, 160, 690, 18, fill=(80, 190, 90), a=q)
    # la figura junto a la cama
    if t > ta:
        qa = prog(t, ta, 1.2)
        ente(L, 330, 650, 0.85, a=qa, ojos=qa, col=(2, 10, 4))
    st["nv"] = True
    texto(L, "03:28  REC ●", 470, 365, 14, (150, 255, 160), a=q, fuente="mono", anchor="rm", sombra=False)


def t_susto(e):
    """Instante (relativo a la escena) del susto: justo al terminar la última palabra."""
    w = e["palabras"][-1]
    return e["voz_t0"] - e["t0"] + w["t"] + w["d"] + 0.25


def esc_ultimo(L, e, t, D, T, st):
    tsu = t_susto(e)
    if t < tsu:
        rect(L, 0, 0, W, H, NOCHE)
        st["overlay"].append(("chat_final", t, prog(t, wt(e, "Te") - 0.3, 0.3), prog(t, wt(e, "Ahora") - 0.3, 0.3), T))
    else:
        # susto: la cara aparece de golpe
        dt = t - tsu
        rect(L, 0, 0, W, H, (0, 0, 0))
        s = 1.6 + 0.4 * eo3(cl(dt / 0.3))
        ente(L, 270, 1090, s * 1.03, a=1.0, ojos=0, col=(70, 70, 86))      # contorno iluminado
        ente(L, 270, 1090, s, a=1.0, ojos=0, col=(8, 8, 10))
        hx, hy = 270, 1090 - 330 * s
        for lado in (-1, 1):
            circ(L, hx + lado * 12 * s, hy - 4 * s, 9 * s, fill=(255, 255, 255))
            circ(L, hx + lado * 12 * s, hy - 4 * s, 3 * s, fill=(200, 0, 0))
        L.d.ellipse(P(hx - 10 * s, hy + 10 * s, hx + 10 * s, hy + 30 * s), fill=L.c((0, 0, 0)),
                    outline=L.c((90, 90, 100)), width=int(2 * K))
        st["glitch"] = 1.0 * math.exp(-dt * 2.5)
        st["shake"] = 10 * math.exp(-dt * 4)


def esc_final(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (0, 0, 0))
    st["overlay"].append(("final", t, prog(t, wt(e, "333") - 0.3, 0.4), prog(t, wt(e, "sígueme") - 0.3, 0.4)))
    st["sin_cabecera"] = t < 0.8


FUNCS = {"gancho": esc_gancho, "lucia": esc_lucia, "mensaje": esc_mensaje, "texto": esc_texto, "golpes": esc_golpes,
         "voz": esc_voz, "susurro": esc_susurro, "like": esc_like, "vibra": esc_vibra, "foto": esc_foto,
         "ultimo": esc_ultimo, "final": esc_final}


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "bloqueo":
            _, t, e, T_ = it
            x0, y0, w, h = movil(O, 270, 600, 1.15, T=T_)
            texto(O, "3:33", 270, y0 + 110, 70, (230, 236, 250), fuente="black", sombra=False)
            texto(O, "martes, 13", 270, y0 + 160, 16, (170, 180, 200), fuente="semi", sombra=False)
            q = cl(t / 0.15 + 0.6)
            yy = y0 + 210
            rect(O, x0 + 16, yy, x0 + w - 16, yy + 80, (40, 44, 58), a=q, r=14)
            texto(O, "Tú (este número) · ahora", x0 + 30, yy + 20, 11, (170, 180, 200), a=q, fuente="bold", anchor="lm",
                  sombra=False)
            texto(O, "No abras la puerta.", x0 + 30, yy + 44, 15, BLANCO, a=q, fuente="semi", anchor="lm", sombra=False)
            texto(O, "No soy yo.", x0 + 30, yy + 64, 15, BLANCO, a=q, fuente="semi", anchor="lm", sombra=False)
        elif tipo == "reloj333":
            _, q, t = it
            parp = 0.7 + 0.3 * (math.sin(t * 6) > 0)
            rect(O, 150, 340, 390, 430, (0, 0, 0), a=0.85 * q, r=10)
            texto(O, "3:33", 270, 385, 64, ROJO_D, a=q * parp, fuente="mono", sombra=False)
        elif tipo == "chat":
            _, t, q_remit, q_msg, T_ = it
            x0, y0, w, h = movil(O, 270, 600, 1.15, T=T_)
            rect(O, x0 + 10, y0 + 40, x0 + w - 10, y0 + 92, (28, 32, 46))
            circ(O, x0 + 40, y0 + 66, 16, fill=(90, 100, 130))
            texto(O, "Tú (este número)", x0 + 64, y0 + 60, 14, BLANCO, fuente="black", anchor="lm", sombra=False)
            texto(O, "en línea", x0 + 64, y0 + 78, 10, (120, 220, 140), a=q_remit, fuente="semi", anchor="lm", sombra=False)
            if q_msg is None:
                puntos = int(t * 3) % 3 + 1
                rect(O, x0 + 20, y0 + 120, x0 + 90, y0 + 152, (52, 56, 70), r=14)
                for k in range(3):
                    circ(O, x0 + 36 + k * 18, y0 + 136, 4, fill=BLANCO, a=1.0 if k < puntos else 0.3)
            else:
                burbuja_chat(O, x0 + 20, y0 + 120, "No abras la puerta. No soy yo.", a=q_msg, size=17)
                texto(O, "3:33", x0 + w - 24, y0 + h - 40, 11, (140, 150, 170), fuente="semi", anchor="rm", sombra=False)
        elif tipo == "toc":
            _, k, q = it
            if q > 0:
                x, y = 330 + k * 40, 470 + k * 90
                texto(O, "TOC", x, y, 40 * (0.7 + 0.3 * eob(q)), BLANCO, a=q, fuente="black")
        elif tipo == "like":
            _, t, tl = it
            q = prog(t, tl, 0.35)
            s = eob(q) * (1 + 0.08 * math.sin(t * 8))
            corazon(O, 270, 580, 110 * s, (200, 20, 40), a=cl(q * 1.5))
            texto(O, "DALE LIKE", 270, 750, 46 * (0.8 + 0.2 * eob(q)), BLANCO, a=q, fuente="black")
        elif tipo == "grande":
            _, txt, y, q, col = it
            texto(O, txt, 270, y, 34 * (0.8 + 0.2 * eob(q)), col, a=q, fuente="black")
        elif tipo == "movil_vibra":
            _, t, T_ = it
            x0, y0, w, h = movil(O, 270, 470, 0.7, vibra=1.0, T=T_)
            texto(O, "1 foto nueva", 270, y0 + 120, 14, BLANCO, fuente="black", sombra=False)
            texto(O, "de: Tú (este número)", 270, y0 + 144, 10, (170, 180, 200), fuente="semi", sombra=False)
        elif tipo == "chat_final":
            _, t, q1, q2, T_ = it
            x0, y0, w, h = movil(O, 270, 600, 1.15, T=T_)
            rect(O, x0 + 10, y0 + 40, x0 + w - 10, y0 + 92, (28, 32, 46))
            texto(O, "Tú (este número)", x0 + 64, y0 + 60, 14, BLANCO, fuente="black", anchor="lm", sombra=False)
            hh = burbuja_chat(O, x0 + 20, y0 + 120, "No abras la puerta. No soy yo.", a=1.0, size=15)
            rect(O, x0 + 20, y0 + 130 + hh, x0 + 160, y0 + 220 + hh, (10, 40, 16), r=10)
            texto(O, "FOTO · 03:28", x0 + 90, y0 + 175 + hh, 13, (90, 200, 100), fuente="mono", sombra=False)
            if q1 > 0:
                h2 = burbuja_chat(O, x0 + 20, y0 + 236 + hh, "Te dije que no era yo.", a=q1, size=16)
                if q2 > 0:
                    burbuja_chat(O, x0 + 20, y0 + 246 + hh + h2, "Ahora mira detrás de ti.", a=q2, size=16)
        elif tipo == "final":
            _, t, q3, qs = it
            texto(O, "3:33", 270, 420, 90, ROJO_D, a=cl(t / 0.6), fuente="mono", sombra=False)
            if q3 > 0:
                rect(O, 90, 520, 450, 600, BLANCO, a=q3, r=40)
                poly(O, [(150, 596), (180, 596), (140, 626)], BLANCO, a=q3)
                texto(O, "Comenta «333»", 270, 560, 30, (20, 20, 20), a=q3, fuente="black", sombra=False)
            if qs > 0:
                rect(O, 130, 660, 410, 720, (200, 20, 40), a=qs, r=30)
                texto(O, "+ SEGUIR · PARTE 2", 270, 690, 22, BLANCO, a=qs, fuente="black", sombra=False)


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
    rect(O, 270 - w / 2, 148, 270 + w / 2, 180, (120, 10, 20), a=0.9, r=16)
    texto(O, CABECERA, 270, 164, 15, BLANCO, fuente="black", sombra=False)


def fecha(O, e, t):
    return


def efectos(img, st, T):
    """Grano, visión nocturna y glitch RGB."""
    if st.get("nv"):
        a = np.asarray(img).astype(np.float32)
        g = a.mean(axis=2)
        a = np.stack([g * 0.35, g * 1.15 + 10, g * 0.4], -1)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    gl = st.get("glitch", 0)
    if gl > 0.02:
        r, g, b = img.split()
        d = int(gl * 14 * K)
        r = ImageChops.offset(r, d, 0)
        b = ImageChops.offset(b, -d, 0)
        img = Image.merge("RGB", (r, g, b))
        rs = random.Random(int(T * 30))
        dr = ImageDraw.Draw(img)
        for _ in range(int(gl * 8)):
            y = rs.uniform(0, IH)
            hh = rs.uniform(4, 30) * K
            dx = int(rs.uniform(-40, 40) * K * gl)
            tira = img.crop((0, int(y), IW, int(y + hh)))
            img.paste(tira, (dx, int(y)))
        _ = dr
    # grano
    rs = random.Random(int(T * 24))
    ruido = Image.effect_noise((IW // 4, IH // 4), 40).resize((IW, IH), Image.NEAREST).convert("RGB")
    img = Image.blend(img, ImageChops.multiply(img, ruido), 0.12)
    _ = rs
    return img


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
        v = np.clip(1.25 - r * 1.15, 0.32, 1)
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
    fx, fy = 270, 480
    if "zoom_puerta" in st:
        zp = st["zoom_puerta"]
        z += 0.7 * zp
        fx, fy = lerp(270, 445, zp), lerp(480, 640, zp)
    cw, ch = IW / z, IH / z
    sh = st.get("shake", 0)
    x0 = cl(fx * K - cw / 2, 0, IW - cw) + sh * K * math.sin(T * 61)
    y0 = cl(fy * K - ch / 2, 0, IH - ch) + sh * K * math.cos(T * 47)
    img = L.img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    if st.get("oscuro"):
        img = Image.blend(img, Image.new("RGB", (IW, IH), (0, 0, 0)), st["oscuro"])
    if st.get("flash"):
        img = Image.blend(img, Image.new("RGB", (IW, IH), (255, 255, 250)), cl(st["flash"]))
    img = ImageChops.multiply(img, VINETA())
    img = efectos(img, st, T)
    O = Capa(img)
    overlays(O, st, T)
    cabecera(O, st)
    fecha(O, e, t)
    subtitulos(O, T)
    out = O.img
    if T > TOTAL - 0.5:
        out = Image.blend(out, Image.new("RGB", (IW, IH), (0, 0, 0)), cl((T - (TOTAL - 0.5)) / 0.5))
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


def vibracion(dur=1.6):
    m = int(dur * SR)
    u = np.arange(m) / SR
    on = ((u % 0.8) < 0.5).astype(np.float32)
    s = np.sign(np.sin(2 * np.pi * 150 * u)) * on * 0.12
    return np.convolve(s, np.ones(20) / 20, mode="same").astype(np.float32)


def notificacion():
    m = int(1.4 * SR)
    u = np.arange(m) / SR
    s = (np.sin(2 * np.pi * 660 * u) + 0.5 * np.sin(2 * np.pi * 932 * u)) * np.exp(-u * 3) * 0.25
    return s.astype(np.float32)


def estatica(dur):
    m = int(dur * SR)
    r = np.random.default_rng(5).standard_normal(m).astype(np.float32)
    return (np.diff(r, prepend=0) * 0.15 * np.clip((dur * SR - np.arange(m)) / (0.3 * SR), 0, 1)).astype(np.float32)


def susto():
    m = int(2.5 * SR)
    u = np.arange(m) / SR
    s = np.zeros(m, np.float32)
    for f in (233, 247, 262, 349, 370, 494, 523):
        s += np.sign(np.sin(2 * np.pi * f * u)) * 0.06
    s = np.convolve(s, np.ones(8) / 8, mode="same")
    r = np.random.default_rng(7).standard_normal(m).astype(np.float32)
    s += r * 0.4 * np.exp(-u * 3)
    s += np.sin(2 * np.pi * (40 + 60 * np.exp(-u * 5)) * u) * 0.8
    return (s * np.exp(-u * 1.2)).astype(np.float32)


def mezclar():
    n = int((TOTAL + 0.3) * SR)
    voz = np.zeros(n, np.float32)
    sus = np.zeros(n, np.float32)
    for e in ESC:
        clip = leer(os.path.join(BUILD, f"voz_{e['i']}.mp3"))
        colocar(sus if e["nombre"] == "susurro" else voz, clip, e["voz_t0"])
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    voz = procesar_voz(voz)
    voz = np.pad(voz, (0, max(0, n - len(voz))))[:n]
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    sus = procesar_susurro(sus * 0.9 / (np.abs(sus).max() + 1e-6))
    sus = np.pad(sus, (0, max(0, n - len(sus))))[:n]
    sus *= 0.8 / (np.abs(sus).max() + 1e-6)
    voz = voz + sus
    tt = np.arange(n) / SR
    mus = musica(n)
    fx = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    colocar(fx, notificacion(), 0.05, 0.6)
    colocar(fx, braam(), 0.0, 0.5)
    lu = E["lucia"]
    t = lu["t0"] + 0.3
    while t < E["golpes"]["t0"]:
        m = int(0.03 * SR)
        colocar(fx, (np.sin(2 * np.pi * 2500 * np.arange(m) / SR) * np.exp(-np.arange(m) / SR * 200) * 0.12).astype(np.float32), t)
        t += 1.0
    me = E["mensaje"]
    colocar(fx, notificacion(), me["t0"] + 0.2, 0.5)
    tx = E["texto"]
    colocar(fx, estatica(0.6), tx["t0"] + wt(tx, "soy") - 0.2, 0.5)
    colocar(fx, braam(), tx["t0"] + wt(tx, "soy") - 0.2, 0.6)
    g = E["golpes"]
    tl = g["t0"] + wt(g, "llamaron") - 0.1
    for d in (0.2, 0.75, 1.3):
        colocar(fx, toc(), tl + d, 0.9)
    # latidos que se aceleran desde los golpes hasta el susto
    t = tl + 1.8
    periodo = 0.9
    fin_lat = E["like"]["t0"]
    while t < fin_lat:
        colocar(fx, latido(0.7), t, 0.6)
        t += periodo
        periodo = max(0.5, periodo * 0.96)
    su = E["susurro"]
    colocar(fx, estatica(su["dur"]) * 0.4, su["t0"], 0.4)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.5)
    colocar(fx, braam(), lk["t0"] + wt(lk, "peor") - 0.3, 0.7)
    vb = E["vibra"]
    colocar(fx, vibracion(1.6), vb["t0"] + wt(vb, "vibró") - 0.3, 0.8)
    fo = E["foto"]
    colocar(fx, estatica(0.4), fo["t0"] + 0.1, 0.4)
    colocar(fx, braam(), fo["t0"] + wt(fo, "algo") - 0.4, 0.8)
    t = fo["t0"] + 0.5
    while t < E["ultimo"]["t0"] + 2:
        colocar(fx, latido(0.8), t, 0.6)
        t += 0.55
    ul = E["ultimo"]
    ts = ul["t0"] + t_susto(ul)
    colocar(fx, susto(), ts, 1.0)
    colocar(fx, estatica(1.0), ts, 0.6)
    # silencio total justo antes del susto
    a0, a1 = int((ts - 0.7) * SR), int(ts * SR)
    mus[a0:a1] *= np.linspace(1, 0, a1 - a0)
    fx[a0:a1] *= np.linspace(1, 0, a1 - a0)
    fi = E["final"]
    colocar(fx, notificacion(), fi["t0"] + 0.4, 0.4)
    for k, e in enumerate(ESC[1:]):
        if e["nombre"] not in ("susurro", "texto"):
            colocar(fx, whoosh(k, 0.5), e["t0"] - 0.25, 0.25)
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
