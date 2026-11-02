"""TikTok vertical «Si alguien te sigue por la calle de noche»: consejos generales de seguridad con personajes
planos (estilo del vídeo del secuestro), calle nocturna con farolas, voz con pausas y diseño sonoro.

    python3 voz.py && python3 video.py        -> te_siguen_tiktok.mp4"""
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
SALIDA = os.path.join(AQUI, "te_siguen_tiktok.mp4")

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


EXTRA = {"gancho": 0.3, "porque": 0.4, "comprobar": 0.8, "luz": 0.6, "grita": 0.8, "final": 1.6}
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
CLAVE = {"no", "vayas", "peor", "sigue", "jamás", "casa.", "vives.", "expertos", "compruébalo.", "cruza", "casualidad.", "luz", "gente:",
         "bar,", "tienda,", "farmacia.", "ayuda.", "112", "cuelgues.", "describe", "like.", "ruido.", "grita", "concreto:",
         "policía!", "antes.", "seguridad,", "cascos", "móvil.", "objetivo.", "guarda", "mándaselo", "sígueme"}


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


# --- Escenas del TikTok «Si alguien te sigue por la calle de noche» (se insertan en video.py al montarlo) ---

POSES.update({
    "camina1": dict(rodilla=(26, 92), pie=(36, 188), cuello=(6, -150), cabeza=(12, -196), codo=(-16, -76), mano=(-26, -14),
                    codo2=(18, -76), mano2=(32, -16)),
    "camina2": dict(rodilla=(-12, 94), pie=(-30, 188), cuello=(6, -150), cabeza=(12, -196), codo=(18, -76), mano=(32, -16),
                    codo2=(-16, -76), mano2=(-26, -14)),
    "corre1": dict(rodilla=(40, 72), pie=(22, 172), cuello=(18, -146), cabeza=(30, -190), codo=(-28, -92), mano=(-46, -48),
                   codo2=(40, -96), mano2=(60, -130)),
    "corre2": dict(rodilla=(-18, 90), pie=(-62, 166), cuello=(18, -146), cabeza=(30, -190), codo=(34, -94), mano=(58, -126),
                   codo2=(-26, -92), mano2=(-44, -50)),
    "grita": dict(rodilla=(10, 94), pie=(14, 190), cuello=(8, -150), cabeza=(16, -196), codo=(50, -150), mano=(100, -176),
                  codo2=(-10, -80), mano2=(-4, -20)),
    "movil_oreja": dict(rodilla=(4, 95), pie=(2, 190), cuello=(2, -150), cabeza=(6, -196), codo=(34, -140), mano=(14, -190),
                        codo2=(-8, -74), mano2=(-4, -10)),
    "mira_atras": dict(rodilla=(10, 94), pie=(4, 190), cuello=(-6, -150), cabeza=(-16, -194), codo=(-16, -76), mano=(-26, -14),
                       codo2=(18, -76), mano2=(32, -16)),
})

PROTA = ((235, 128, 70), (205, 104, 52), (62, 86, 150), (48, 68, 122))     # chaqueta naranja y vaqueros
TESTIGO = ((210, 50, 50), (170, 36, 36), (60, 60, 70), (46, 46, 56))     # chaqueta roja
CABECERA = "QUÉ HACER SI TE SIGUEN"
SUELO = 760


def camina(t, vel=8):
    return pose_mix("camina1", "camina2", 0.5 + 0.5 * math.sin(t * vel))


def seguidor(L, x, y, t, s=0.8, anda=True, pose=None):
    """Perseguidor: figura oscura con capucha (siempre igual)."""
    p = pose or (camina(t + 0.6) if anda else "de_pie")
    info = persona(L, x, y - 190 * s, p, s, tipo="captor")
    cx, cy = info["cabeza"]
    r = 34 * s
    L.d.pieslice(P(cx - r * 1.25, cy - r * 1.35, cx + r * 1.25, cy + r * 1.1), 180, 360, fill=L.c((14, 14, 18)))
    return info


def prota(L, x, y, t, s=0.8, pose=None, ojos=1.0, boca=0.0, flip=False):
    return persona(L, x, y - 190 * s, pose or camina(t), s, ropa=PROTA, pelo=(60, 36, 24), ojos=ojos, boca=boca, flip=flip)


def calle(L, T, desplaza=0.0, lamparas=(110, 400), escaparate=None):
    rect(L, 0, 0, W, H, (8, 10, 20))
    # edificios del fondo con paralaje
    rs = random.Random(3)
    x = -((desplaza * 0.4) % 160) - 40
    k = 0
    while x < W + 40:
        w = 70 + (k * 37) % 50
        h = 220 + (k * 53) % 180
        rect(L, x, SUELO - 60 - h, x + w, SUELO - 60, (22, 24, 38))
        for wy in range(int(SUELO - 60 - h + 14), SUELO - 70, 26):
            for wx in range(int(x + 8), int(x + w - 12), 18):
                if random.Random(k * 1000 + wy * 7 + wx).random() < 0.25:
                    rect(L, wx, wy, wx + 9, wy + 12, (255, 210, 120))
        x += w + 6
        k += 1
    _ = rs
    # acera lejana, calzada y acera cercana
    rect(L, 0, SUELO - 60, W, SUELO, (70, 70, 80))
    rect(L, 0, SUELO, W, 880, (36, 38, 46))
    off = -(desplaza % 90)
    for xx in range(int(off) - 90, W + 90, 90):
        rect(L, xx, 816, xx + 46, 822, (200, 190, 120))
    rect(L, 0, 880, W, H, (70, 70, 80))
    for lx in lamparas:
        lx2 = lx - desplaza % (W + 200) if desplaza else lx
        rect(L, lx2 - 3, SUELO - 260, lx2 + 3, SUELO - 60, (40, 40, 46))
        rect(L, lx2 - 16, SUELO - 270, lx2 + 16, SUELO - 256, (50, 50, 56), r=3)
        circ(L, lx2, SUELO - 252, 7, fill=(255, 236, 180))
    if escaparate:
        ex, nombre, col = escaparate
        rect(L, ex, SUELO - 260, ex + 220, SUELO - 60, (40, 40, 50))
        rect(L, ex + 14, SUELO - 210, ex + 206, SUELO - 70, (255, 236, 190))
        rect(L, ex + 90, SUELO - 140, ex + 130, SUELO - 60, (200, 220, 230))
        rect(L, ex + 20, SUELO - 250, ex + 200, SUELO - 216, col, r=4)
        texto(L, nombre, ex + 110, SUELO - 233, 16, BLANCO, fuente="black", sombra=False)
        if nombre == "FARMACIA":
            cx_, cy_ = ex + 236, SUELO - 236
            rect(L, cx_ - 14, cy_ - 5, cx_ + 14, cy_ + 5, (60, 220, 110))
            rect(L, cx_ - 5, cy_ - 14, cx_ + 5, cy_ + 14, (60, 220, 110))


def mapa_luz(T, fuentes, ambiente=0.42, parpadeo=None):
    """fuentes: lista de (x, y, radio, intensidad, color)."""
    sw, sh = IW // 12, IH // 12
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    acc = np.ones((sh, sw, 3), np.float32) * ambiente * np.array([0.7, 0.78, 1.0], np.float32)
    for (x, y, r, k, col) in fuentes:
        ux, uy = x / W * sw, y / H * sh
        d2 = ((xx - ux) ** 2 + (yy - uy) ** 2) / (r / W * sw) ** 2
        acc += np.exp(-d2)[..., None] * k * np.array(col, np.float32)[None, None, :] / 255
    return Image.fromarray(np.clip(acc * 255, 0, 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    calle(L, T, desplaza=T * 60)
    x = 340
    mira = (t % 2.4) < 0.9
    prota(L, x, SUELO - 20, t, pose="mira_atras" if mira else None, ojos=1.7 if mira else 1.0)
    seguidor(L, 200 + 6 * math.sin(t), SUELO - 24, t)
    st["cam"] = (1.32 - 0.12 * eio(t / D), 270, 560)
    st["alarma"] = t
    st["luces"] = [(110 - (T * 60) % (W + 200), SUELO - 250, 190, 1.0, (255, 220, 160)),
                   (400 - (T * 60) % (W + 200), SUELO - 250, 190, 1.0, (255, 220, 160)), (330, 600, 120, 0.25, (255, 230, 200))]
    st["overlay"].append(("titular", t, 1.0))


def esc_porque(L, e, t, D, T, st):
    calle(L, T)
    # portal de su casa
    rect(L, 340, SUELO - 300, 520, SUELO - 60, (60, 50, 46))
    rect(L, 400, SUELO - 200, 470, SUELO - 60, (90, 64, 44))
    circ(L, 460, SUELO - 130, 4, fill=(220, 190, 110))
    rect(L, 360, SUELO - 280, 500, SUELO - 236, (240, 220, 160))
    texto(L, "Nº 14", 430, SUELO - 258, 18, (40, 30, 20), fuente="black", sombra=False)
    u = eio(prog(t, 0, 2.0))
    prota(L, lerp(230, 360, u), SUELO - 20, t, pose=None if u < 1 else "de_pie")
    seguidor(L, 80, SUELO - 24, t, anda=False)
    st["luces"] = [(430, SUELO - 240, 140, 0.7, (255, 220, 160)), (110, SUELO - 250, 190, 0.8, (255, 220, 160))]
    q = prog(t, wt(e, "vives") - 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("pin", q, t))
    qe = prog(t, wt(e, "expertos") - 0.3, 0.4)
    if qe > 0:
        st["overlay"].append(("fuente", qe))


def esc_comprobar(L, e, t, D, T, st):
    calle(L, T)
    tc = wt(e, "Cruza") - 0.2
    ts = wt(e, "mismo") - 0.6
    u1 = eio(prog(t, tc, 1.4))
    u2 = eio(prog(t, ts, 1.4))
    # cruzar: de la acera lejana a la cercana (más grande por la perspectiva)
    y1 = lerp(SUELO - 20, 930, u1)
    s1 = lerp(0.8, 1.0, u1)
    prota(L, lerp(300, 330, u1), y1, t, s=s1, pose="mira_atras" if t > ts + 1.0 else None, ojos=1.7 if t > ts + 1 else 1)
    y2 = lerp(SUELO - 24, 930, u2)
    s2 = lerp(0.8, 1.0, u2)
    seguidor(L, lerp(110, 150, u2), y2, t, s=s2)
    st["luces"] = [(110, SUELO - 250, 190, 0.9, (255, 220, 160)), (400, SUELO - 250, 190, 0.9, (255, 220, 160))]
    qa = prog(t, wt(e, "casualidad") - 0.4, 0.3)
    if qa > 0:
        st["overlay"].append(("alerta", qa, t))
    st["latido"] = True


def esc_luz(L, e, t, D, T, st):
    calle(L, T, escaparate=(300, "FARMACIA", (40, 160, 90)), lamparas=(110,))
    te = wt(e, "Entra") - 0.2
    u = eio(prog(t, 0.3, te - 0.3))
    if t < te + 0.5:
        prota(L, lerp(120, 400, u), SUELO - 20, t, pose=None if u < 1 else "de_pie")
    sx = lerp(20, 140, u)
    seguidor(L, sx, SUELO - 24, t, anda=u < 1, pose=None if u < 1 else "de_pie")
    st["luces"] = [(410, SUELO - 160, 230, 1.1, (230, 255, 230)), (110, SUELO - 250, 190, 0.7, (255, 220, 160))]
    sitios = [("bar", "BAR"), ("tienda", "TIENDA"), ("farmacia", "FARMACIA")]
    for j, (pal, txt) in enumerate(sitios):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("chip", txt, j, q))


def esc_llamar(L, e, t, D, T, st):
    # dentro de la farmacia, a salvo junto al mostrador
    rect(L, 0, 0, W, H, (220, 236, 226))
    rect(L, 0, 300, W, 760, (236, 246, 240))
    for k in range(4):
        rect(L, 20, 340 + k * 70, 240, 346 + k * 70, (180, 200, 190))
        for j in range(6):
            rect(L, 30 + j * 34, 310 + k * 70, 52 + j * 34, 340 + k * 70, [(200, 80, 80), (80, 140, 200), (240, 200, 80)][(j + k) % 3])
    rect(L, 0, 760, W, H, (200, 210, 206))
    rect(L, 260, 640, 540, 760, (140, 180, 160))
    prota(L, 160, SUELO, t, s=0.8, pose="movil_oreja")
    st["luces"] = None
    st["overlay"].append(("telefono", t, e))


def esc_like(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (40, 12, 16))
    st["luces"] = None
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))


def esc_grita(L, e, t, D, T, st):
    calle(L, T, lamparas=(110, 420))
    tg = wt(e, "Grita") - 0.2
    tt = wt(e, "Tú") - 0.2
    huye = eio(prog(t, tt + 1.4, 1.2))
    prota(L, 240, SUELO - 20, t, pose="grita" if t > tg else "de_pie", ojos=1.5, boca=1.0 if t > tg else 0)
    if huye <= 0:
        seguidor(L, 120, SUELO - 24, t, anda=False)
    else:
        seguidor(L, lerp(120, -120, huye), SUELO - 24, t * 1.8, pose=pose_mix("corre1", "corre2", 0.5 + 0.5 * math.sin(t * 14)))
    # testigo con chaqueta roja que se gira y llama
    gira = t > tt + 0.6
    persona(L, 440, SUELO - 20 - 190 * 0.8, "movil_oreja" if gira else "de_pie", 0.8, ropa=TESTIGO, pelo=(30, 30, 30),
            flip=gira, ojos=1.4 if gira else 1.0)
    st["luces"] = [(110, SUELO - 250, 190, 0.9, (255, 220, 160)), (420, SUELO - 250, 190, 1.0, (255, 220, 160)),
                   (240, 600, 120, 0.3, (255, 230, 200))]
    if t > tt:
        st["overlay"].append(("bocadillo", prog(t, tt, 0.25)))
    if t > tg and t < tt:
        st["overlay"].append(("ruido", prog(t, tg, 0.2), t))
    qr = prog(t, wt(e, "reacciona") - 0.3, 0.4)
    if qr > 0:
        st["overlay"].append(("efecto", qr))


def esc_prevencion(L, e, t, D, T, st):
    calle(L, T, desplaza=T * 50)
    prota(L, 270, SUELO - 20, t, s=0.9)
    st["luces"] = [(110 - (T * 50) % (W + 200), SUELO - 250, 190, 1.0, (255, 220, 160)),
                   (400 - (T * 50) % (W + 200), SUELO - 250, 190, 1.0, (255, 220, 160)), (270, 600, 140, 0.35, (255, 230, 200))]
    for j, (pal, txt, ok) in enumerate([("seguridad", "CAMINA SEGURO", True), ("cascos", "SIN CASCOS", False),
                                        ("móvil", "SIN MIRAR EL MÓVIL", False)]):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("regla", txt, j, q))
    qm = prog(t, wt(e, "objetivo") - 0.3, 0.4)
    if qm > 0:
        st["overlay"].append(("sello", "MAL OBJETIVO", qm))


def esc_final(L, e, t, D, T, st):
    calle(L, T)
    prota(L, 270, SUELO - 20, t, pose="de_pie")
    st["luces"] = [(110, SUELO - 250, 190, 0.9, (255, 220, 160)), (400, SUELO - 250, 190, 0.9, (255, 220, 160))]
    st["overlay"].append(("final", t, prog(t, wt(e, "Guarda") - 0.2, 0.3), prog(t, wt(e, "mándaselo") - 0.2, 0.3),
                          prog(t, wt(e, "sígueme") - 0.2, 0.3)))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "porque": esc_porque, "comprobar": esc_comprobar, "luz": esc_luz, "llamar": esc_llamar,
         "like": esc_like, "grita": esc_grita, "prevencion": esc_prevencion, "final": esc_final}


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
            s2 = 1 + 0.6 * math.exp(-t * 10)
            texto(O, "SI TE SIGUEN DE NOCHE", 270, 610, 24 * s, AMARILLO, fuente="black")
            sello_t(O, "NO VAYAS A CASA", 270, 668, 1.0, size=38 * s2)
        elif tipo == "pin":
            _, q, t = it
            x, y = 430, 400 - 8 * math.sin(t * 3)
            s = eob(q)
            circ(O, x, y, 26 * s, fill=ROJO, a=q)
            poly(O, [(x - 18 * s, y + 10 * s), (x + 18 * s, y + 10 * s), (x, y + 44 * s)], ROJO, a=q)
            circ(O, x, y, 9 * s, fill=BLANCO, a=q)
            texto(O, "TU CASA", x, y + 66, 18, BLANCO, a=q, fuente="black")
            linea(O, [(140, 470), (400, 420)], ROJO, w=3, a=q * 0.7)
        elif tipo == "fuente":
            q = it[1]
            rect(O, 80, 860, 460, 900, (0, 0, 0), a=0.6 * q, r=20)
            texto(O, "Consejos generales de seguridad", 270, 880, 15, (220, 220, 230), a=q, fuente="bold", sombra=False)
        elif tipo == "alerta":
            _, q, t = it
            texto(O, "!", 160, 520 - 10 * math.sin(t * 10), 90 * eob(q) + 1, ROJO, a=q, fuente="black")
            sello_t(O, "NO ES CASUALIDAD", 270, 380, q, size=28)
        elif tipo == "chip":
            _, txt, j, q = it
            y = 360 + j * 54
            w = ancho(txt, 22) + 70
            rect(O, 270 - w / 2, y - 22, 270 + w / 2, y + 22, (40, 160, 90), a=q, r=22)
            circ(O, 270 - w / 2 + 24, y, 12, fill=BLANCO, a=q)
            linea(O, [(270 - w / 2 + 18, y), (270 - w / 2 + 23, y + 5), (270 - w / 2 + 31, y - 6)], (40, 160, 90), w=3, a=q)
            texto(O, txt, 270 + 14, y, 22, BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "telefono":
            _, t, e = it
            x0, y0 = 300, 330
            rect(O, x0, y0, x0 + 210, y0 + 380, (16, 16, 20), r=24)
            rect(O, x0 + 10, y0 + 14, x0 + 200, y0 + 366, (30, 120, 70), r=18)
            texto(O, "112", x0 + 105, y0 + 70, 40, BLANCO, fuente="black", sombra=False)
            seg = int(t)
            texto(O, f"00:{seg:02d}", x0 + 105, y0 + 110, 16, BLANCO, fuente="mono", sombra=False)
            items = [("dónde", "Dónde estás"), ("describe", "Cómo es"), ("cuelgues", "No cuelgues")]
            for j, (pal, txt) in enumerate(items):
                q = prog(t, wt(e, pal) - 0.2, 0.3)
                if q > 0:
                    y = y0 + 170 + j * 56
                    rect(O, x0 + 20, y - 20, x0 + 190, y + 20, BLANCO, a=q, r=12)
                    texto(O, "✓ " + txt, x0 + 30, y, 15, (30, 120, 70), a=q, fuente="sym", anchor="lm", sombra=False)
        elif tipo == "like":
            _, t, tl = it
            q = prog(t, tl, 0.35)
            s = eob(q) * (1 + 0.08 * math.sin(t * 8))
            corazon(O, 270, 560, 110 * s, (254, 44, 85), a=cl(q * 1.5))
            texto(O, "DALE LIKE", 270, 740, 46 * (0.8 + 0.2 * eob(q)), BLANCO, a=q, fuente="black")
            texto(O, "y compártelo", 270, 790, 22, (230, 200, 200), a=q, fuente="semi")
        elif tipo == "bocadillo":
            q = it[1]
            s = eob(q)
            rect(O, 60, 340, 480, 430, BLANCO, a=q, r=20)
            poly(O, [(220, 428), (250, 428), (230, 460)], BLANCO, a=q)
            texto(O, "¡TÚ, EL DE LA CHAQUETA ROJA,", 270, 370, 18 * s, (30, 30, 30), a=q, fuente="black", sombra=False)
            texto(O, "LLAMA A LA POLICÍA!", 270, 402, 22 * s, ROJO, a=q, fuente="black", sombra=False)
        elif tipo == "ruido":
            _, q, t = it
            for k in range(3):
                u = (t * 2 + k / 3) % 1
                O.d.arc(P(330 - 40 - 60 * u, 560 - 40 - 60 * u, 330 + 40 + 60 * u, 560 + 40 + 60 * u), 300, 60,
                        fill=O.c(AMARILLO, q * (1 - u)), width=3 * K)
        elif tipo == "efecto":
            q = it[1]
            rect(O, 70, 860, 470, 902, (0, 0, 0), a=0.6 * q, r=20)
            texto(O, "Pedir ayuda a alguien concreto funciona", 270, 881, 15, BLANCO, a=q, fuente="bold", sombra=False)
        elif tipo == "regla":
            _, txt, j, q = it
            y = 360 + j * 56
            col = VERDE if j == 0 else ROJO
            w = ancho(txt, 22) + 70
            rect(O, 270 - w / 2, y - 22, 270 + w / 2, y + 22, (0, 0, 0), a=0.65 * q, r=22)
            texto(O, ("✓ " if j == 0 else "✗ ") + txt, 270, y, 22, col, a=q, fuente="sym", sombra=False)
        elif tipo == "sello":
            _, txt, q = it
            sello_t(O, txt, 270, 560, q, col=VERDE, size=34)
        elif tipo == "final":
            _, t, qg, qm, qs = it
            if qg > 0:
                cx, cy, s = 150, 420, eob(qg)
                w, h = 46 * s, 60 * s
                poly(O, [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2),
                         (cx, cy + h / 2 - 17 * s), (cx - w / 2, cy + h / 2)], AMARILLO, a=qg)
                texto(O, "GUÁRDALO", cx, cy + 56, 16, BLANCO, a=qg, fuente="black")
            if qm > 0:
                texto(O, "↗", 390, 420, 60 * eob(qm) + 1, (40, 160, 230), a=qm, fuente="sym")
                texto(O, "MÁNDASELO", 390, 476, 16, BLANCO, a=qm, fuente="black")
            if qs > 0:
                rect(O, 130, 560, 410, 620, (254, 44, 85), a=qs, r=30)
                texto(O, "+ SEGUIR", 270, 590, 26, BLANCO, a=qs, fuente="black", sombra=False)


def cabecera(O, st):
    if st.get("sin_cabecera"):
        return
    w = ancho(CABECERA, 15) + 30
    rect(O, 270 - w / 2, 148, 270 + w / 2, 180, (180, 30, 30), a=0.92, r=16)
    texto(O, CABECERA, 270, 164, 15, BLANCO, fuente="black", sombra=False)


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
    if st.get("luces") is not None and st["luces"] != []:
        img = ImageChops.multiply(img, mapa_luz(T, st["luces"]))
    z, fx, fy = st.get("cam", (1.04 + 0.06 * eio(t / D), 270, 500))
    z += golpe_zoom(T)
    cw, ch = IW / z, IH / z
    sh = st.get("shake", 0)
    x0 = cl(fx * K - cw / 2, 0, IW - cw) + (2 * math.sin(T * 1.7) + sh * math.sin(T * 61)) * K
    y0 = cl(fy * K - ch / 2, 0, IH - ch) + (2 * math.cos(T * 1.3)) * K
    img = img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    img = ImageChops.multiply(img, VINETA())
    if "alarma" in st:
        pulso = 0.5 + 0.5 * math.sin(st["alarma"] * 7)
        img = Image.blend(img, Image.new("RGB", (IW, IH), (160, 0, 0)), 0.10 + 0.08 * pulso)
    O = Capa(img)
    overlays(O, st, T)
    cabecera(O, st)
    subtitulos(O, T)
    out = O.img
    if T > TOTAL - 0.5:
        out = Image.blend(out, Image.new("RGB", (IW, IH), (0, 0, 0)), cl((T - (TOTAL - 0.5)) / 0.5))
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


def musica(n):
    """Ostinato de tensión en menor; se vuelve más luminoso en la prevención."""
    out = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    t_luz = E["prevencion"]["t0"]
    beat = 60 / 100
    k = 0
    notas_m = [45, 48, 52, 48, 44, 48, 52, 48]
    notas_M = [45, 49, 52, 49, 47, 50, 54, 50]
    while k * beat / 2 < TOTAL:
        t0 = k * beat / 2
        nn = (notas_M if t0 >= t_luz else notas_m)[k % 8]
        f = 440 * 2 ** ((nn - 69) / 12)
        m = int(0.35 * SR)
        u = np.arange(m) / SR
        colocar(out, ((np.sin(2 * np.pi * f * u) + 0.3 * np.sin(4 * np.pi * f * u)) * np.exp(-u * 6) * 0.045)
                .astype(np.float32), t0)
        if k % 4 == 0:
            mm = int(0.4 * SR)
            uu = np.arange(mm) / SR
            colocar(out, (np.sin(2 * np.pi * (45 + 60 * np.exp(-uu * 25)) * uu) * np.exp(-uu * 8) * 0.12).astype(np.float32), t0)
        k += 1
    tt = np.arange(n) / SR
    out += (0.05 * np.sin(2 * np.pi * 55 * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * tt))).astype(np.float32)
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
    mus = musica(n) * 0.9
    fx = (ruido(n, 200, 1) * 0.12 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * tt))).astype(np.float32)   # tráfico lejano
    E = {e["nombre"]: e for e in ESC}
    colocar(fx, braam(), 0.0, 0.6)
    g = E["gancho"]
    colocar(fx, pasos(g["dur"], 0.42, 10, vol=0.5), 0.0, 1.0)
    colocar(fx, pasos(g["dur"], 0.44, 50, eco=True, vol=0.4), 0.2, 1.0)
    colocar(fx, braam(), g["t0"] + wt(g, "casa") - 0.3, 0.8)
    colocar(fx, golpe(), 0.0, 0.8)
    t_ = 0.0
    while t_ < g["dur"]:
        colocar(fx, latido(0.9), t_, 0.55)
        t_ += 0.62
    p = E["porque"]
    colocar(fx, pasos(2.0, 0.42, 20, vol=0.5), p["t0"], 1.0)
    colocar(fx, golpe() * 0.5, p["t0"] + wt(p, "vives") - 0.3, 0.5)
    c = E["comprobar"]
    colocar(fx, pasos(c["dur"], 0.4, 30, vol=0.5), c["t0"], 1.0)
    colocar(fx, pasos(c["dur"], 0.41, 70, eco=True, vol=0.45), c["t0"] + 0.15, 1.0)
    colocar(fx, braam(), c["t0"] + wt(c, "casualidad") - 0.4, 0.8)
    t = c["t0"] + wt(c, "mismo") - 0.6
    per = 0.8
    while t < E["luz"]["t0"] + 3:
        colocar(fx, latido(0.8), t, 0.5)
        t += per
        per = max(0.5, per * 0.95)
    lz = E["luz"]
    colocar(fx, dingdong(), lz["t0"] + wt(lz, "Entra") - 0.1, 0.6)
    ll = E["llamar"]
    colocar(fx, tono(2), ll["t0"] + 0.2, 0.6)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.6)
    gr = E["grita"]
    colocar(fx, braam(), gr["t0"] + wt(gr, "Grita") - 0.2, 0.6)
    tt_ = gr["t0"] + wt(gr, "Tú") - 0.2
    colocar(fx, pasos(1.4, 0.2, 90, vol=0.6), tt_ + 1.4, 1.0)
    pv = E["prevencion"]
    colocar(fx, pasos(pv["dur"], 0.45, 40, vol=0.4), pv["t0"], 1.0)
    for pal in ("seguridad", "cascos", "móvil"):
        colocar(fx, pop(), pv["t0"] + wt(pv, pal) - 0.2, 0.4)
    colocar(fx, golpe() * 0.6, pv["t0"] + wt(pv, "objetivo") - 0.3, 0.5)
    fi = E["final"]
    for pal in ("Guarda", "mándaselo", "sígueme"):
        colocar(fx, pop(), fi["t0"] + wt(fi, pal) - 0.2, 0.5)
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
