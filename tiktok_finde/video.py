"""TikTok vertical «¿Quién inventó el fin de semana?»: historia y economía del trabajo (La Canadiense 1919,
Henry Ford 1926, las 40 horas de 1983 y la semana de 4 días). Optimizado para retención: gancho en el
fotograma 0, cabecera fija, zoom en palabras clave, like a mitad con bucle abierto y llamada a seguir.

    python3 voz.py && python3 video.py        -> finde_tiktok.mp4"""
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
SALIDA = os.path.join(AQUI, "finde_tiktok.mp4")

W, H = 540, 960            # unidades de diseño (9:16)
K = 3                      # resolución interna = 1620x2880
IW, IH = W * K, H * K
OW, OH = 1080, 1920
FPS = 30
SR = 44100
VOZ_OFF = 0.12
COLA = 0.25

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


EXTRA = {"gancho": 0.3, "canadiense": 0.3, "porque": 0.3, "final": 1.4}
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
CLAVE = {"cinco", "dos", "gobierno", "millonario", "ti.", "catorce", "seis", "niños", "1919", "huelga", "oscuras",
         "8", "primeras", "sábado", "ford", "1926", "sueldo", "bondad", "no.", "gasta", "coche", "like", "fuerte",
         "40", "1983", "cuatro", "negocio", "sígueme", "inventada", "trabajarías"}


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


# --- Escenas del TikTok «¿Quién inventó el fin de semana?» (se insertan en video.py al montarlo) ---

POSES.update({
    "pancarta": dict(rodilla=(4, 95), pie=(2, 190), cuello=(0, -150), cabeza=(4, -196), codo=(20, -200), mano=(24, -250),
                     codo2=(-14, -200), mano2=(-10, -250)),
    "trabaja": dict(rodilla=(4, 95), pie=(2, 190), cuello=(10, -146), cabeza=(22, -188), codo=(46, -100), mano=(84, -80),
                    codo2=(40, -96), mano2=(76, -70)),
    "cansado": dict(rodilla=(10, 92), pie=(4, 190), cuello=(16, -140), cabeza=(34, -170), codo=(24, -70), mano=(20, -10),
                    codo2=(10, -70), mano2=(4, -10)),
    "senala": dict(rodilla=(4, 95), pie=(2, 190), cuello=(2, -150), cabeza=(8, -196), codo=(46, -150), mano=(96, -190),
                   codo2=(-8, -74), mano2=(-4, -10)),
    "bolsas": dict(rodilla=(26, 92), pie=(36, 188), cuello=(10, -150), cabeza=(18, -194), codo=(24, -80), mano=(30, -20),
                   codo2=(-20, -80), mano2=(-26, -20)),
    "relax": dict(rodilla=(70, -6), pie=(150, 10), cuello=(-30, -112), cabeza=(-30, -152), codo=(-60, -130), mano=(-30, -170),
                  codo2=(-20, -60), mano2=(20, -40)),
})

CREMA_P = (240, 228, 204)
NEGRO_P = (26, 24, 24)
ROJO_P = (204, 44, 40)
OCRE = (214, 160, 60)
GRIS_P = (130, 124, 116)
OBRERO = ((70, 80, 100), (56, 64, 82), (60, 60, 70), (48, 48, 56))
FORD = ((40, 40, 46), (30, 30, 36), (40, 40, 46), (30, 30, 36))
CABECERA = "¿QUIÉN INVENTÓ EL FIN DE SEMANA?"
DIAS = ["L", "M", "X", "J", "V", "S", "D"]
FECHA = {"antes": "1900", "canadiense": "BARCELONA 1919", "ford": "EE. UU. 1926", "porque": "1926",
         "hoy": "ESPAÑA 1983 → HOY"}


def fondo_cartel(L, T, col=CREMA_P, rayos=True):
    rect(L, 0, 0, W, H, col)
    if rayos:
        cx, cy = 270, 1100
        for k in range(14):
            a0 = math.pi + k * math.pi / 14 + T * 0.03
            a1 = a0 + math.pi / 28
            poly(L, [(cx, cy), (cx + 1400 * math.cos(a0), cy + 1400 * math.sin(a0)),
                     (cx + 1400 * math.cos(a1), cy + 1400 * math.sin(a1))], mezcla(col, ROJO_P, 0.08))


def calendario(L, x, y, estados, q=1.0, s=1.0, t=0.0, resalta=None):
    """estados: 7 valores 'w' (trabajo), 'f' (libre), 'x' (tachado), 'm' (medio)."""
    w = 58 * s
    for k, (d, e) in enumerate(zip(DIAS, estados)):
        qk = prog(q, k / 9, 0.3)
        if qk <= 0:
            continue
        cx = x + (k - 3) * (w + 6 * s)
        sc = eob(qk)
        col = {"w": NEGRO_P, "f": ROJO_P, "x": GRIS_P, "m": OCRE}[e]
        if resalta is not None and k in resalta:
            sc *= 1 + 0.08 * math.sin(t * 8)
        rect(L, cx - w / 2 * sc, y - w / 2 * sc, cx + w / 2 * sc, y + w / 2 * sc, col, a=qk, r=8 * s)
        texto(L, d, cx, y - 6 * s, 26 * s * sc, CREMA_P, a=qk, fuente="black", sombra=False)
        sub = {"w": "trabajo", "f": "libre", "x": "", "m": "½"}[e]
        if sub:
            texto(L, sub, cx, y + 18 * s, 9 * s * sc, CREMA_P, a=qk * 0.85, fuente="bold", sombra=False)
        if e == "x":
            linea(L, [(cx - 20 * s, y - 20 * s), (cx + 20 * s, y + 20 * s)], ROJO_P, w=4 * s, a=qk)


def fabrica(L, T, y0=720, humo=True):
    rect(L, 40, y0 - 220, 500, y0, (90, 60, 50))
    for k in range(5):
        poly(L, [(40 + k * 92, y0 - 220), (40 + k * 92 + 46, y0 - 270), (40 + (k + 1) * 92, y0 - 220)], (70, 46, 40))
    for k in range(4):
        rect(L, 70 + k * 110, y0 - 180, 130 + k * 110, y0 - 120, (240, 200, 120), r=4)
    for cx in (110, 420):
        rect(L, cx, y0 - 360, cx + 36, y0 - 220, (70, 46, 40))
        if humo:
            for j in range(6):
                u = (T * 0.25 + j / 6) % 1
                circ(L, cx + 18 + 40 * u, y0 - 370 - 160 * u, 18 + 30 * u, fill=(120, 116, 110), a=0.6 * (1 - u))
    rect(L, 0, y0, W, H, (60, 50, 46))


def reloj_grande(L, x, y, r, horas, a=1.0):
    circ(L, x, y, r, fill=CREMA_P, a=a)
    circ(L, x, y, r, outline=NEGRO_P, w=5, a=a)
    for k in range(12):
        ang = k * math.pi / 6
        linea(L, [(x + r * 0.82 * math.cos(ang), y + r * 0.82 * math.sin(ang)), (x + r * 0.92 * math.cos(ang),
               y + r * 0.92 * math.sin(ang))], NEGRO_P, w=3, a=a)
    am = math.radians(-90 + horas * 360)
    ah = math.radians(-90 + horas * 30)
    linea(L, [(x, y), (x + r * 0.75 * math.cos(am), y + r * 0.75 * math.sin(am))], NEGRO_P, w=4, a=a)
    linea(L, [(x, y), (x + r * 0.5 * math.cos(ah), y + r * 0.5 * math.sin(ah))], ROJO_P, w=6, a=a)


def coche_t(L, x, y, s=1.0, a=1.0, col=NEGRO_P):
    """Coche de época estilo años 20, de perfil."""
    rect(L, x - 60 * s, y - 20 * s, x + 60 * s, y + 8 * s, col, a=a, r=6 * s)
    rect(L, x - 40 * s, y - 56 * s, x + 20 * s, y - 20 * s, col, a=a, r=4 * s)
    rect(L, x - 32 * s, y - 50 * s, x + 12 * s, y - 28 * s, (180, 200, 210), a=a)
    for wx in (-38, 40):
        circ(L, x + wx * s, y + 10 * s, 16 * s, fill=(20, 20, 20), a=a)
        circ(L, x + wx * s, y + 10 * s, 6 * s, fill=(200, 200, 200), a=a)


def bolsa(L, x, y, s=1.0, col=OCRE):
    rect(L, x - 14 * s, y - 18 * s, x + 14 * s, y + 18 * s, col, r=3)
    L.d.arc(P(x - 8 * s, y - 30 * s, x + 8 * s, y - 10 * s), 180, 360, fill=L.c(NEGRO_P), width=int(2 * K))


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    fondo_cartel(L, T)
    tm = wt(e, "millonario") - 0.25
    calendario(L, 270, 480, ["w"] * 5 + ["f"] * 2, q=cl(0.85 + t), s=1.0, t=t, resalta=[5, 6])
    if t > tm:
        q = prog(t, tm, 0.35)
        s = eob(q)
        # silueta de millonario con chistera y puro
        x, y = 270, 720
        rect(L, x - 70 * s, y - 40 * s, x + 70 * s, y + 160 * s, NEGRO_P, a=q, r=30 * s)
        circ(L, x, y - 80 * s, 52 * s, fill=NEGRO_P, a=q)
        rect(L, x - 44 * s, y - 210 * s, x + 44 * s, y - 120 * s, NEGRO_P, a=q, r=4)
        rect(L, x - 70 * s, y - 128 * s, x + 70 * s, y - 112 * s, NEGRO_P, a=q, r=4)
        rect(L, x - 44 * s, y - 140 * s, x + 44 * s, y - 128 * s, ROJO_P, a=q)
        rect(L, x + 40 * s, y - 72 * s, x + 86 * s, y - 64 * s, OCRE, a=q, r=3)
        texto(L, "$", x, y + 50 * s, 70 * s, OCRE, a=q, fuente="black", sombra=False)
    st["overlay"].append(("titular", t, e))


def esc_antes(L, e, t, D, T, st):
    fondo_cartel(L, T, rayos=False)
    fabrica(L, T, 760)
    reloj_grande(L, 400, 420, 70, horas=t * 1.6, a=1.0)
    th = wt(e, "catorce") - 0.2
    if t > th:
        st["overlay"].append(("grande", "14 h/día", 330, prog(t, th, 0.3)))
    ts = wt(e, "Seis") - 0.2
    if t > ts:
        calendario(L, 270, 860, ["w"] * 6 + ["f"], q=prog(t, ts, 0.8), s=0.8)
    tn = wt(e, "Niños") - 0.2
    if t > tn:
        q = prog(t, tn, 0.4)
        for j in range(3):
            persona(L, 120 + j * 70, 760 - 190 * 0.34, "trabaja", 0.34, ropa=OBRERO, pelo=(60, 40, 30), a=q)
    else:
        for j in range(2):
            persona(L, 130 + j * 110, 760 - 190 * 0.5, "cansado" if t > 1.5 else "trabaja", 0.5, ropa=OBRERO,
                    pelo=(60, 40, 30))


def esc_canadiense(L, e, t, D, T, st):
    to = wt(e, "oscuras") - 0.3
    tr = wt(e, "Resultado") - 0.2
    if t < tr:
        apaga = prog(t, to, 0.6)
        rect(L, 0, 0, W, H, mezcla((30, 34, 60), (6, 6, 12), apaga))
        rs = random.Random(3)
        x = -10
        while x < W:
            w = rs.uniform(30, 70)
            h = rs.uniform(80, 260)
            rect(L, x, 760 - h, x + w, 760, (40, 40, 50))
            for wy in range(int(760 - h + 12), 750, 22):
                for wx in range(int(x + 6), int(x + w - 8), 14):
                    encendida = rs.random() < 0.7 and rs.random() > apaga * (0.6 + 0.4 * rs.random())
                    if encendida:
                        rect(L, wx, wy, wx + 7, wy + 10, (250, 210, 110))
            x += w + 4
        rect(L, 0, 760, W, H, (30, 30, 36))
        # torre eléctrica con chispas
        linea(L, [(420, 760), (460, 420), (500, 760)], (90, 90, 100), w=4)
        linea(L, [(430, 520), (490, 520)], (90, 90, 100), w=3)
        if 0 < apaga < 1:
            for j in range(6):
                circ(L, 460 + random.Random(int(t * 20) + j).uniform(-30, 30), 430 + j * 6, 3, fill=(255, 255, 180))
        # huelguistas con pancartas
        if t > 0.6:
            for j in range(5):
                persona(L, 40 + j * 70, 860 - 190 * 0.36, "pancarta", 0.36, ropa=OBRERO, pelo=(50, 40, 30))
            st["overlay"].append(("pancartas", prog(t, 0.6, 0.5)))
        st["overlay"].append(("huelga", prog(t, wt(e, "huelga") - 0.2, 0.3) * (1 - apaga * 0.4)))
    else:
        fondo_cartel(L, T)
        q = prog(t, tr, 0.4)
        st["overlay"].append(("periodico", q))
        q8 = prog(t, wt(e, "8") - 0.2, 0.4)
        if q8 > 0:
            reloj_grande(L, 270, 760, 80 * eob(q8) + 1, horas=8 / 12 * 12 + 0.0001, a=q8)


def esc_ford(L, e, t, D, T, st):
    fondo_cartel(L, T)
    # cadena de montaje
    rect(L, 0, 720, W, 740, NEGRO_P)
    for k in range(5):
        x = (k * 140 + t * 70) % (W + 140) - 70
        coche_t(L, x, 700, 0.7)
    persona(L, 110, 720 - 190 * 0.7 - 8, "senala" if t > 1.0 else "de_pie", 0.7, ropa=FORD, pelo=(170, 170, 170))
    q = prog(t, wt(e, "Ford") - 0.2, 0.4)
    if q > 0:
        st["overlay"].append(("ficha", "HENRY FORD", "fabricante de coches", q))
    td = wt(e, "dos") - 0.2
    if t > td:
        calendario(L, 270, 860, ["w"] * 5 + ["f", "f"], q=prog(t, td, 0.8), s=0.8, t=t, resalta=[5, 6])
    ts = wt(e, "sueldo") - 0.3
    if t > ts:
        st["overlay"].append(("sello", "MISMO SUELDO", 360, 400, prog(t, ts, 0.3)))


def esc_porque(L, e, t, D, T, st):
    fondo_cartel(L, T)
    tg = wt(e, "gasta") - 0.3
    tc = wt(e, "coche") - 0.4
    if t < tg:
        q = prog(t, 0.1, 0.3)
        st["overlay"].append(("grande", "¿Por bondad?", 420, q))
        qn = prog(t, wt(e, "No") - 0.15, 0.25)
        if qn > 0:
            st["overlay"].append(("cruz_g", qn))
    else:
        # gente gastando en su día libre
        for j in range(3):
            x = 110 + j * 150
            persona(L, x, 760 - 190 * 0.5, pose_mix("bolsas", "de_pie", 0.5 + 0.5 * math.sin(t * 6 + j)), 0.5,
                    ropa=OBRERO, pelo=(60, 40, 30))
            bolsa(L, x + 16, 750, 1.0)
            bolsa(L, x - 16, 752, 0.9, ROJO_P)
        rect(L, 0, 860, W, H, NEGRO_P)
        if t > tc:
            q = prog(t, tc, 0.6)
            coche_t(L, lerp(-80, 400, eo3(q)), 840, 1.0, col=ROJO_P)
        for j in range(4):
            u = (t * 0.7 + j / 4) % 1
            texto(L, "$", 80 + j * 120, 620 - 120 * u, 34, OCRE, a=1 - u, fuente="black", sombra=False)
        st["overlay"].append(("cita", prog(t, tg, 0.4)))


def esc_like(L, e, t, D, T, st):
    fondo_cartel(L, T, (250, 236, 232))
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    q = prog(t, wt(e, "fuerte") - 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("grande", "ESPERA…", 370, q))


def esc_hoy(L, e, t, D, T, st):
    fondo_cartel(L, T)
    t83 = wt(e, "1983") - 0.3
    t4 = wt(e, "cuatro") - 0.5
    if t < t4:
        q = prog(t, 0.1, 0.4)
        st["overlay"].append(("boe", q, prog(t, t83, 0.4)))
    else:
        calendario(L, 270, 520, ["w"] * 4 + ["f"] * 3, q=prog(t, t4, 0.9), s=1.0, t=t, resalta=[4])
        st["overlay"].append(("grande", "4 DÍAS", 680, prog(t, t4 + 0.4, 0.4)))


def esc_reflexion(L, e, t, D, T, st):
    fondo_cartel(L, T, (232, 220, 196))
    # tumbado en una hamaca en su sábado
    rect(L, 0, 760, W, H, (120, 160, 90))
    linea(L, [(110, 640), (270, 720), (430, 640)], (150, 100, 60), w=6)
    persona(L, 270, 690, "relax", 0.6, ropa=OBRERO, pelo=(60, 40, 30))
    sol_ = 1 + 0.05 * math.sin(t * 2)
    circ(L, 450, 390, 50 * sol_, fill=OCRE)
    q1 = prog(t, wt(e, "huelga") - 0.3, 0.4)
    q2 = prog(t, wt(e, "negocio") - 0.4, 0.4)
    if q1 > 0:
        st["overlay"].append(("dos_caras", q1, q2))


def esc_final(L, e, t, D, T, st):
    fondo_cartel(L, T)
    calendario(L, 270, 420, ["w"] * 4 + ["f"] * 3, q=cl(t * 1.5), s=0.8, t=t)
    st["overlay"].append(("seguir", t))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "antes": esc_antes, "canadiense": esc_canadiense, "ford": esc_ford,
         "porque": esc_porque, "like": esc_like, "hoy": esc_hoy, "reflexion": esc_reflexion, "final": esc_final}


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "titular":
            _, t, e = it
            s = 1 + 0.35 * math.exp(-t * 9)
            texto(O, "¿QUIÉN INVENTÓ", 270, 340, 40 * s, NEGRO_P, fuente="black", sombra=False)
            texto(O, "EL FIN DE SEMANA?", 270, 390, 40 * s, ROJO_P, fuente="black", sombra=False)
            q = prog(t, wt(e, "ti") - 0.2, 0.3)
            if q > 0:
                ss = 1 + 1.3 * (1 - eo3(q))
                w = ancho("NO FUE POR TI", 34 * ss) + 34 * ss
                rect(O, 270 - w / 2, 590 - 26 * ss, 270 + w / 2, 590 + 26 * ss, CREMA_P, a=q, r=8)
                rect(O, 270 - w / 2, 590 - 26 * ss, 270 + w / 2, 590 + 26 * ss, None, a=q, r=8, outline=ROJO_P, w=5)
                texto(O, "NO FUE POR TI", 270, 590, 34 * ss, ROJO_P, a=q, fuente="black", sombra=False)
        elif tipo == "grande":
            _, txt, y, q = it
            if q > 0:
                texto(O, txt, 270, y, 58 * (0.8 + 0.2 * eob(q)), ROJO_P, a=q, fuente="black")
        elif tipo == "huelga":
            q = it[1]
            if q > 0:
                texto(O, "HUELGA", 270, 370, 70 * (0.8 + 0.2 * eob(q)), ROJO_P, a=q, fuente="black")
                texto(O, "LA CANADIENSE", 270, 420, 22, CREMA_P, a=q, fuente="black")
        elif tipo == "pancartas":
            q = it[1]
            for j in range(5):
                x = 40 + j * 70
                rect(O, x - 30, 690, x + 30, 720, CREMA_P, a=q, r=3)
                texto(O, "8 H", x, 705, 15, ROJO_P, a=q, fuente="black", sombra=False)
        elif tipo == "periodico":
            q = it[1]
            s = eob(q)
            rect(O, 60, 360, 480, 620, (236, 230, 214), a=q, r=4)
            texto(O, "GACETA DE MADRID · 1919", 270, 390, 13, (60, 60, 60), a=q, fuente="black", sombra=False)
            linea(O, [(80, 408), (460, 408)], (60, 60, 60), w=2, a=q)
            texto(O, "JORNADA DE", 270, 460, 40 * s, NEGRO_P, a=q, fuente="black", sombra=False)
            texto(O, "8 HORAS", 270, 520, 62 * s, ROJO_P, a=q, fuente="black", sombra=False)
            for j in range(3):
                linea(O, [(90, 570 + j * 14), (450, 570 + j * 14)], (150, 150, 150), w=2, a=q)
        elif tipo == "ficha":
            _, n, sub, q = it
            rect(O, 220, 360, 500, 430, NEGRO_P, a=0.9 * q, r=12)
            texto(O, n, 236, 382, 22, CREMA_P, a=q, fuente="black", anchor="lm", sombra=False)
            texto(O, sub, 236, 410, 15, (200, 190, 170), a=q, fuente="semi", anchor="lm", sombra=False)
        elif tipo == "sello":
            _, txt, x, y, q = it
            if q > 0:
                ss = 1 + 1.3 * (1 - eo3(q))
                w = ancho(txt, 30 * ss) + 30 * ss
                rect(O, x - w / 2, y - 24 * ss, x + w / 2, y + 24 * ss, CREMA_P, a=q, r=8)
                rect(O, x - w / 2, y - 24 * ss, x + w / 2, y + 24 * ss, None, a=q, r=8, outline=ROJO_P, w=5)
                texto(O, txt, x, y, 30 * ss, ROJO_P, a=q, fuente="black", sombra=False)
        elif tipo == "cruz_g":
            q = it[1]
            texto(O, "NO", 270, 560, 120 * (0.7 + 0.3 * eob(q)), NEGRO_P, a=q, fuente="black", sombra=False)
        elif tipo == "cita":
            q = it[1]
            rect(O, 40, 340, 500, 470, NEGRO_P, a=0.9 * q, r=12)
            texto(O, "«Quien tiene más ocio necesita", 270, 378, 18, CREMA_P, a=q, fuente="semi", sombra=False)
            texto(O, "más ropa, más comida…", 270, 404, 18, CREMA_P, a=q, fuente="semi", sombra=False)
            texto(O, "y más transporte»", 270, 430, 18, OCRE, a=q, fuente="black", sombra=False)
            texto(O, "— Henry Ford, 1926", 470, 456, 12, (190, 180, 160), a=q, fuente="semi", anchor="rm", sombra=False)
        elif tipo == "like":
            _, t, tl = it
            q = prog(t, tl, 0.35)
            s = eob(q) * (1 + 0.08 * math.sin(t * 8))
            corazon(O, 270, 580, 110 * s, (254, 44, 85), a=cl(q * 1.5))
            texto(O, "DALE LIKE", 270, 750, 46 * (0.8 + 0.2 * eob(q)), NEGRO_P, a=q, fuente="black", sombra=False)
            texto(O, "si no lo sabías", 270, 795, 20, GRIS_P, a=q, fuente="semi", sombra=False)
            rs = random.Random(3)
            for j in range(10):
                u = (t - tl - j * 0.08) / 1.2
                if 0 < u < 1:
                    corazon(O, 270 + rs.uniform(-160, 160) * u, 580 - 260 * u, 24 * (1 - u * 0.5), (254, 44, 85), a=1 - u)
        elif tipo == "boe":
            _, q, q83 = it
            rect(O, 70, 360, 470, 800, (250, 248, 240), a=q, r=4)
            texto(O, "BOLETÍN OFICIAL DEL ESTADO", 270, 400, 15, NEGRO_P, a=q, fuente="black", sombra=False)
            linea(O, [(90, 420), (450, 420)], NEGRO_P, w=2, a=q)
            texto(O, "Jornada máxima:", 270, 480, 26, NEGRO_P, a=q, fuente="bold", sombra=False)
            texto(O, "40 HORAS", 270, 550, 64, ROJO_P, a=q, fuente="black", sombra=False)
            texto(O, "a la semana", 270, 600, 22, NEGRO_P, a=q, fuente="bold", sombra=False)
            if q83 > 0:
                ss = 1 + 1.3 * (1 - eo3(q83))
                texto(O, "1983", 270, 700, 70 * ss, ROJO_P, a=q83, fuente="black", sombra=False)
        elif tipo == "dos_caras":
            _, q1, q2 = it
            rect(O, 30, 340, 260, 440, ROJO_P, a=q1, r=12)
            texto(O, "alguien hizo", 145, 372, 18, CREMA_P, a=q1, fuente="bold", sombra=False)
            texto(O, "HUELGA", 145, 410, 34, CREMA_P, a=q1, fuente="black", sombra=False)
            if q2 > 0:
                rect(O, 280, 340, 510, 440, NEGRO_P, a=q2, r=12)
                texto(O, "alguien vio un", 395, 372, 18, CREMA_P, a=q2, fuente="bold", sombra=False)
                texto(O, "NEGOCIO", 395, 410, 34, OCRE, a=q2, fuente="black", sombra=False)
        elif tipo == "seguir":
            t = it[1]
            circ(O, 270, 600, 70, fill=NEGRO_P)
            texto(O, "M", 270, 600, 60, CREMA_P, fuente="black", sombra=False)
            tt = (t % 2.0)
            toque = prog(tt, 0.8, 0.3)
            r = 22 * (1 - 0.15 * math.sin(toque * math.pi))
            circ(O, 270, 672, r, fill=(254, 44, 85) if toque < 0.5 else BLANCO)
            texto(O, "+" if toque < 0.5 else "✓", 270, 672, 26, BLANCO if toque < 0.5 else (254, 44, 85), fuente="sym",
                  sombra=False)
            if 0 < toque < 1:
                circ(O, 270, 672, 22 + 40 * toque, outline=(254, 44, 85), w=3, a=1 - toque)
            texto(O, "@mente404_0", 270, 730, 26, NEGRO_P, fuente="black", sombra=False)
            texto(O, "Una historia real cada día", 270, 800, 24, ROJO_P, fuente="black", sombra=False)


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
    rect(O, 270 - w / 2, 148, 270 + w / 2, 180, NEGRO_P, a=0.88, r=16)
    texto(O, CABECERA, 270, 164, 15, CREMA_P, fuente="black", sombra=False)


def fecha(O, e, t):
    txt = FECHA.get(e["nombre"])
    if not txt:
        return
    q = prog(t, 0.05, 0.3)
    rect(O, 20, 300, 20 + ancho(txt, 16, "mono") + 24, 332, NEGRO_P, a=0.85 * q, r=8)
    texto(O, txt, 32, 316, 16, CREMA_P, a=q, fuente="mono", anchor="lm", sombra=False)


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
        out = Image.blend(out, Image.new("RGB", (IW, IH), CREMA_P), cl((T - (TOTAL - 0.5)) / 0.5))
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




def musica(n):
    """Piano de época con bajo de tuba (años 20); marcha con caja durante la huelga."""
    out = np.zeros(n, np.float32)
    beat = 60 / 118
    acordes = [[48, 52, 55], [53, 57, 60], [55, 59, 62], [48, 52, 55]]
    melodia = [72, 76, 79, 76, 74, 77, 74, 71, 72, 76, 79, 81, 79, 76, 74, 72]
    E = {e["nombre"]: e for e in ESC}
    h0 = E["canadiense"]["t0"]
    h1 = h0 + wt(E["canadiense"], "Resultado") - 0.2
    k = 0
    while k * beat / 2 < TOTAL:
        t0 = k * beat / 2
        ac = acordes[(k // 8) % 4]
        if k % 2 == 0:
            colocar(out, piano(440 * 2 ** ((ac[0] - 24 - 69) / 12), 0.45, 0.07), t0)     # tuba/bajo
        else:
            for m in ac:
                colocar(out, piano(440 * 2 ** ((m - 69) / 12), 0.3, 0.022), t0)
        mm = melodia[k % 16]
        if not (h0 <= t0 < h1):
            colocar(out, piano(440 * 2 ** ((mm - 69) / 12), 0.35, 0.022), t0 + (0.03 if k % 2 else 0))
        else:
            # caja de marcha
            m2 = int(0.12 * SR)
            u = np.arange(m2) / SR
            r = np.random.default_rng(k).standard_normal(m2).astype(np.float32)
            colocar(out, (r * np.exp(-u * 30) * 0.12).astype(np.float32), t0)
        k += 1
    return out


def gentio(dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    rng = np.random.default_rng(7)
    r = rng.standard_normal(n).astype(np.float32)
    r = np.convolve(r, np.ones(8) / 8, mode="same") - np.convolve(r, np.ones(80) / 80, mode="same")
    coro = (0.5 + 0.5 * np.sin(2 * np.pi * tt / 1.2)) ** 4          # «¡ocho horas!» rítmico
    return (r * (0.4 + 0.6 * coro) * 2.0 * np.clip(tt / 0.4, 0, 1) * np.clip((dur - tt) / 0.4, 0, 1)).astype(np.float32)


def apagon():
    n = int(1.4 * SR)
    u = np.arange(n) / SR
    f = 120 * np.exp(-u * 2.2) + 30
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-u * 1.5) * 0.5
    s += np.random.default_rng(2).standard_normal(n) * np.exp(-u * 20) * 0.3
    return s.astype(np.float32)


def chispa():
    n = int(0.3 * SR)
    u = np.arange(n) / SR
    r = np.random.default_rng(4).standard_normal(n).astype(np.float32)
    return (np.diff(r, prepend=0) * (np.sin(2 * np.pi * 30 * u) > 0) * np.exp(-u * 8) * 0.4).astype(np.float32)


def maquina(dur):
    out = np.zeros(int(dur * SR), np.float32)
    t = 0.0
    k = 0
    while t < dur - 0.2:
        m = int(0.15 * SR)
        u = np.arange(m) / SR
        s = (np.sin(2 * np.pi * 180 * u) + 0.6 * np.sin(2 * np.pi * 410 * u)) * np.exp(-u * 30) * 0.35
        colocar(out, s.astype(np.float32), t)
        t += 0.45
        k += 1
    return out


def bocina():
    n = int(0.9 * SR)
    u = np.arange(n) / SR
    f = np.where(u < 0.35, 260 + 300 * u, 420 - 200 * (u - 0.35))
    s = np.tanh(3 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.clip(u / 0.03, 0, 1) * np.clip((0.9 - u) / 0.1, 0, 1)
    return (s * 0.3).astype(np.float32)


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
    colocar(fx, golpe(), 0.0, 0.6)
    g = E["gancho"]
    colocar(fx, braam(), g["t0"] + wt(g, "millonario") - 0.25, 0.6)
    colocar(fx, golpe(), g["t0"] + wt(g, "ti") - 0.2, 0.6)
    a = E["antes"]
    colocar(fx, maquina(a["dur"]), a["t0"], 0.5)
    c = E["canadiense"]
    tr = c["t0"] + wt(c, "Resultado") - 0.2
    colocar(fx, gentio(tr - c["t0"] - 0.6), c["t0"] + 0.6, 0.35)
    to = c["t0"] + wt(c, "oscuras") - 0.3
    colocar(fx, chispa(), to - 0.1, 0.6)
    colocar(fx, apagon(), to, 0.8)
    colocar(fx, golpe(), tr, 0.6)
    f = E["ford"]
    colocar(fx, maquina(f["dur"]) * 0.6, f["t0"], 0.4)
    colocar(fx, golpe() * 0.6, f["t0"] + wt(f, "sueldo") - 0.3, 0.5)
    p = E["porque"]
    colocar(fx, golpe(), p["t0"] + wt(p, "No") - 0.15, 0.5)
    colocar(fx, caja(), p["t0"] + wt(p, "gasta") - 0.2, 0.5)
    colocar(fx, bocina(), p["t0"] + wt(p, "coche") - 0.2, 0.5)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.7)
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.1, 0.5)
    colocar(fx, braam(), lk["t0"] + wt(lk, "fuerte") - 0.3, 0.6)
    h = E["hoy"]
    colocar(fx, golpe(), h["t0"] + wt(h, "1983") - 0.3, 0.6)
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
