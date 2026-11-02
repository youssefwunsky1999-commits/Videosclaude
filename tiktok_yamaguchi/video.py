"""TikTok vertical «Sobrevivió a dos bombas atómicas» (Tsutomu Yamaguchi, 1945).
Optimizado para retención: gancho visible en el fotograma 0, cabecera fija, «zoom punch» en palabras clave,
like a mitad de vídeo con bucle abierto y llamada a seguir al final. Estética de cartel japonés,
música de koto y taiko sintetizada, voz con pausas y procesado de estudio.

    python3 voz.py && python3 video.py        -> yamaguchi_tiktok.mp4"""
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
SALIDA = os.path.join(AQUI, "yamaguchi_tiktok.mp4")

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


EXTRA = {"gancho": 0.2, "bomba1": 0.6, "tren": 0.3, "bomba2": 0.6, "final": 1.6}
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
CLAVE = {"sobrevivió", "dos", "atómicas", "real.", "real", "1945", "hiroshima", "8:15", "destello", "cegador",
         "tres", "quemaduras", "tímpanos", "ciego", "sobrevive", "nagasaki", "like", "imposible", "loco", "otro", "93",
         "oficialmente", "nunca", "sígueme", "inventada", "bomba", "ciudad"}


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


# --- Escenas del TikTok «Sobrevivió a dos bombas atómicas» (se insertan en video.py al montarlo) ---

POSES.update({
    "mira_cielo": dict(rodilla=(4, 95), pie=(2, 190), cuello=(-4, -150), cabeza=(-10, -196), codo=(34, -140), mano=(40, -196),
                       codo2=(-6, -76), mano2=(-2, -12)),
    "cubre": dict(rodilla=(16, 90), pie=(6, 188), cuello=(-20, -140), cabeza=(-36, -178), codo=(-40, -130), mano=(-50, -180),
                  codo2=(-30, -120), mano2=(-44, -170)),
    "habla": dict(rodilla=(4, 95), pie=(2, 190), cuello=(2, -150), cabeza=(8, -196), codo=(40, -110), mano=(80, -130),
                  codo2=(-6, -76), mano2=(-2, -12)),
    "jefe": dict(rodilla=(4, 95), pie=(2, 190), cuello=(0, -150), cabeza=(4, -196), codo=(30, -120), mano=(26, -170),
                 codo2=(-30, -90), mano2=(-50, -40)),
    "sentado_tren": dict(rodilla=(70, 0), pie=(72, 85), cuello=(-6, -118), cabeza=(-2, -158), codo=(26, -58), mano=(70, -44)),
    "anciano": dict(rodilla=(6, 95), pie=(2, 190), cuello=(12, -146), cabeza=(24, -186), codo=(30, -80), mano=(50, -20),
                    codo2=(-6, -76), mano2=(-2, -12)),
})

PAPEL = (240, 230, 208)
PAPEL2 = (226, 212, 186)
TINTA = (30, 26, 24)
ROJO_J = (196, 40, 40)
GRIS_J = (120, 112, 100)
TRAJE_J = ((70, 74, 80), (56, 60, 66), (60, 62, 68), (48, 50, 56))
TRAJE_JEFE = ((40, 44, 56), (30, 34, 44), (44, 46, 54), (34, 36, 42))
CABECERA = "SOBREVIVIÓ A 2 BOMBAS ATÓMICAS"
FECHA = {"viaje": "AGOSTO 1945", "bomba1": "6 AGO · 8:15", "heridas": "6 AGO 1945", "tren": "7 AGO 1945",
         "jefe": "9 AGO · 11:02", "bomba2": "9 AGO · 11:02", "vida": "1916 – 2010"}


def papel(L, T, col=PAPEL):
    rect(L, 0, 0, W, H, col)
    rs = random.Random(2)
    for _ in range(140):
        x, y = rs.uniform(0, W), rs.uniform(0, H)
        linea(L, [(x, y), (x + rs.uniform(-12, 12), y + rs.uniform(-3, 3))], PAPEL2, w=1, a=0.5)


def sol(L, x, y, r, col=ROJO_J, a=1.0):
    circ(L, x, y, r, fill=col, a=a)


def ciudad(L, y0, col=TINTA, a=1.0, semilla=1):
    rs = random.Random(semilla)
    x = -10
    while x < W + 10:
        w = rs.uniform(30, 70)
        h = rs.uniform(30, 110)
        rect(L, x, y0 - h, x + w, y0, col, a=a)
        if rs.random() < 0.5:   # tejado japonés
            poly(L, [(x - 8, y0 - h), (x + w + 8, y0 - h), (x + w - 6, y0 - h - 16), (x + 6, y0 - h - 16)], col, a=a)
        x += w + rs.uniform(2, 10)
    rect(L, 0, y0, W, H, col, a=a)


def hongo(L, x, y, u, a=1.0):
    """Nube en forma de hongo que crece (u de 0 a 1)."""
    if u <= 0:
        return
    alto = 330 * eo3(u)
    rs = random.Random(4)
    # tallo
    for k in range(10):
        yy = y - alto * k / 10
        circ(L, x + rs.uniform(-6, 6), yy, 24 + 10 * (k / 10), fill=mezcla((230, 120, 60), (120, 100, 90), k / 10), a=a)
    # sombrero
    cy = y - alto
    for k in range(18):
        ang = k / 18 * 2 * math.pi
        rr = 90 * eo3(u)
        circ(L, x + math.cos(ang) * rr, cy + math.sin(ang) * rr * 0.4, 46 * eo3(u) + 6,
             fill=mezcla((250, 160, 80), (140, 120, 110), 0.5 + 0.5 * math.sin(ang)), a=a)
    circ(L, x, cy, 70 * eo3(u), fill=(255, 200, 120), a=a)
    # anillo
    L.d.ellipse(P(x - 130 * eo3(u), cy + 60 - 10, x + 130 * eo3(u), cy + 60 + 10), outline=L.c((230, 220, 210), a * 0.7),
                width=3 * K)


def avion_b(L, x, y, s=1.0, a=1.0):
    poly(L, [(x - 40 * s, y), (x + 40 * s, y - 2 * s), (x + 48 * s, y + 3 * s), (x - 40 * s, y + 6 * s)], TINTA, a=a)
    poly(L, [(x - 6 * s, y), (x + 14 * s, y), (x - 20 * s, y - 50 * s), (x - 30 * s, y - 50 * s)], TINTA, a=a)
    poly(L, [(x - 6 * s, y + 4 * s), (x + 14 * s, y + 4 * s), (x - 20 * s, y + 52 * s), (x - 30 * s, y + 52 * s)], TINTA, a=a)
    poly(L, [(x - 40 * s, y), (x - 34 * s, y), (x - 48 * s, y - 16 * s), (x - 52 * s, y - 16 * s)], TINTA, a=a)


def yamaguchi(L, x, y, pose="de_pie", esc=0.7, vendado=False, flip=False, a=1.0):
    info = persona(L, x, y, pose, esc, flip=flip, ropa=TRAJE_J, pelo=(24, 20, 18), a=a)
    if vendado:
        cx, cy = info["cabeza"]
        r = 34 * esc
        rect(L, cx - r, cy - r * 0.55, cx + r, cy - r * 0.15, BLANCO, a=a, r=4)
        linea(L, [(cx - r * 0.8, cy - r * 0.9), (cx + r * 0.6, cy + r * 0.1)], BLANCO, w=6 * esc, a=a)
    return info


def mapa(L, t, u_tren=0.0, hiro=1.0, naga=1.0):
    """Mapa esquemático del suroeste de Japón (Honshu occidental y Kyushu)."""
    rect(L, 0, 0, W, H, (190, 210, 220))
    honshu = [(250, 420), (330, 400), (420, 380), (540, 350), (540, 470), (450, 470), (380, 480), (300, 500), (250, 500),
              (220, 470)]
    kyushu = [(150, 500), (210, 490), (240, 530), (250, 600), (230, 690), (190, 720), (150, 700), (110, 640), (120, 560)]
    poly(L, honshu, PAPEL)
    poly(L, kyushu, PAPEL)
    linea(L, honshu + [honshu[0]], TINTA, w=2)
    linea(L, kyushu + [kyushu[0]], TINTA, w=2)
    H_, N_ = (330, 470), (130, 610)
    if hiro:
        sol(L, *H_, 10, a=hiro)
        texto(L, "HIROSHIMA", H_[0] + 14, H_[1] + 26, 18, TINTA, a=hiro, fuente="black", anchor="lm", sombra=False)
    if naga:
        sol(L, *N_, 10, a=naga)
        texto(L, "NAGASAKI", N_[0] - 10, N_[1] + 30, 18, TINTA, a=naga, fuente="black", anchor="lm", sombra=False)
    if u_tren > 0:
        pts = []
        for k in range(int(40 * u_tren) + 1):
            v = k / 40
            pts.append((lerp(H_[0], N_[0], v), lerp(H_[1], N_[1], v) - 60 * math.sin(v * math.pi)))
        if len(pts) > 1:
            for k in range(0, len(pts) - 1, 2):
                linea(L, [pts[k], pts[k + 1]], ROJO_J, w=4)
            circ(L, pts[-1][0], pts[-1][1], 8, fill=TINTA)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    papel(L, T)
    sol(L, 270, 700, 200, a=0.95)
    yamaguchi(L, 270, 800, "de_pie", 1.05)
    rect(L, 0, 840, W, H, TINTA)
    st["overlay"].append(("titular", t, e))


def esc_viaje(L, e, t, D, T, st):
    mapa(L, t, hiro=prog(t, wt(e, "Hiroshima") - 0.3, 0.4), naga=0)
    q = prog(t, wt(e, "Tsutomu") - 0.2, 0.4)
    if q > 0:
        st["overlay"].append(("ficha", q))


def esc_bomba1(L, e, t, D, T, st):
    tf = wt(e, "destello") - 0.15
    papel(L, T, (232, 214, 186))
    sol(L, 270, 420, 90, col=(240, 200, 150))
    if t < tf + 0.2:
        ciudad(L, 760, TINTA, semilla=3)
        yamaguchi(L, 120, 760 - 190 * 0.5 - 6, "mira_cielo" if t > wt(e, "avión") - 0.4 else "de_pie", 0.5)
        ta = wt(e, "avión") - 0.4
        if t > ta:
            avion_b(L, lerp(-60, 330, prog(t, ta, 2.0)), 330, 0.7)
    else:
        dt = t - tf - 0.2
        rect(L, 0, 0, W, H, (240, 150, 80))
        hongo(L, 270, 760, cl(dt / 3.0))
        ciudad(L, 760, (60, 30, 20), semilla=3)
        circ(L, 270, 760, 60 + 500 * eo3(cl(dt / 1.2)), outline=(255, 240, 200), w=6, a=1 - cl(dt / 1.2))
        st["shake"] = 14 * math.exp(-dt * 3)
    if tf <= t < tf + 0.6:
        st["flash"] = 1 - (t - tf) / 0.6
    q = prog(t, wt(e, "8:15") - 0.2, 0.3)
    if q > 0 and t < tf:
        st["overlay"].append(("reloj", q))


def esc_heridas(L, e, t, D, T, st):
    papel(L, T)
    sol(L, 270, 560, 170, col=(220, 190, 170))
    yamaguchi(L, 270, 600, "de_pie", 0.95, vendado=t > 0.4)
    marcas = [("quemaduras", "QUEMADURAS", 120, 400), ("tímpanos", "TÍMPANOS ROTOS", 400, 470), ("ciego", "CIEGO", 130, 560)]
    for pal, txt, x, y in marcas:
        q = prog(t, wt(e, pal) - 0.15, 0.3)
        if q > 0:
            st["overlay"].append(("marca", txt, x, y, q))
    q3 = prog(t, wt(e, "tres") - 0.2, 0.4)
    if q3 > 0 and t < wt(e, "quemaduras") - 0.2:
        st["overlay"].append(("grande", "3 km", 400, q3))
    qs = prog(t, wt(e, "sobrevive") - 0.2, 0.3)
    if qs > 0:
        st["overlay"].append(("sello", "VIVO", 270, 760, qs))


def esc_tren(L, e, t, D, T, st):
    tn = wt(e, "Nagasaki") - 0.3
    if t < tn - 0.4:
        papel(L, T, (214, 226, 220))
        # paisaje que pasa
        for k in range(6):
            x = (k * 140 - t * 200) % (W + 200) - 100
            poly(L, [(x, 600), (x + 70, 470), (x + 140, 600)], (150, 170, 150))
        rect(L, 0, 600, W, H, (120, 130, 110))
        # vagón
        x0 = 40
        rect(L, x0, 480, x0 + 460, 640, (90, 50, 40), r=10)
        for k in range(4):
            rect(L, x0 + 20 + k * 110, 500, x0 + 100 + k * 110, 570, (200, 220, 230), r=4)
        rect(L, x0 + 20 + 110, 500, x0 + 100 + 110, 570, (200, 220, 230), r=4)
        yamaguchi(L, 180, 560, "sentado_tren", 0.42, vendado=True)
        for k in range(4):
            circ(L, x0 + 60 + k * 110, 650, 16, fill=TINTA)
        st["shake"] = 1.5
    else:
        mapa(L, t, u_tren=prog(t, tn - 0.4, 0.8), hiro=1.0, naga=prog(t, tn, 0.3))
        st["overlay"].append(("giro", prog(t, tn, 0.35)))


def esc_like(L, e, t, D, T, st):
    papel(L, T, (250, 236, 236))
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    q = prog(t, wt(e, "imposible") - 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("grande", "IMPOSIBLE", 370, q))


def esc_jefe(L, e, t, D, T, st):
    papel(L, T)
    # oficina: ventana con la ciudad
    rect(L, 300, 380, 500, 560, (200, 220, 230))
    ciudad(L, 560, (120, 130, 140), semilla=7)
    rect(L, 0, 560, W, H, PAPEL)
    rect(L, 290, 372, 510, 568, None, outline=TINTA, w=6)
    linea(L, [(400, 372), (400, 568)], TINTA, w=4)
    rect(L, 0, 740, W, H, (150, 110, 70))
    yamaguchi(L, 140, 740 - 190 * 0.62, "habla", 0.62, vendado=True)
    persona(L, 360, 740 - 190 * 0.66, "jefe" if t > wt(e, "jefe", 1) - 0.2 else "de_pie", 0.66, flip=True, ropa=TRAJE_JEFE,
            pelo=(60, 60, 60), bigote=True)
    q1 = prog(t, wt(e, "bomba") - 0.3, 0.3) * (1 - prog(t, wt(e, "jefe", 1) - 0.3, 0.3))
    if q1 > 0:
        st["overlay"].append(("bocadillo", "¡Una sola bomba\ndestruyó Hiroshima!", 170, 420, q1))
    q2 = prog(t, wt(e, "loco") - 0.4, 0.3)
    if q2 > 0:
        st["overlay"].append(("bocadillo", "¡Imposible!\n¿Estás loco?", 360, 400, q2))


def esc_bomba2(L, e, t, D, T, st):
    tf = wt(e, "destello") - 0.15
    if t < tf:
        esc_jefe(L, ESC_JEFE[0], 99, 99, T, {"overlay": []})
        st["oscuro"] = 0.2 * prog(t, 0, tf)
    else:
        dt = t - tf
        rect(L, 0, 0, W, H, (240, 150, 80))
        hongo(L, 270, 760, cl(dt / 3.0))
        ciudad(L, 760, (60, 30, 20), semilla=9)
        circ(L, 270, 760, 60 + 500 * eo3(cl(dt / 1.2)), outline=(255, 240, 200), w=6, a=1 - cl(dt / 1.2))
        st["shake"] = 16 * math.exp(-dt * 3)
        if dt < 0.7:
            st["flash"] = 1 - dt / 0.7
        q = prog(t, wt(e, "Otra", 0) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("grande", "3 km", 400, q * (1 - prog(t, wt(e, "Otra", 1) - 0.3, 0.2))))
        q2 = prog(t, wt(e, "sobrevive") - 0.2, 0.3)
        if q2 > 0:
            st["overlay"].append(("sello", "VIVO OTRA VEZ", 270, 400, q2))
        st["overlay"].append(("x2", prog(t, tf + 0.5, 0.4)))


def esc_vida(L, e, t, D, T, st):
    papel(L, T)
    sol(L, 270, 560, 190, a=0.9)
    yamaguchi(L, 270, 600, "anciano", 0.95)
    # pelo canoso
    q = prog(t, wt(e, "93") - 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("grande", "93 años", 400, q * (1 - prog(t, wt(e, "Japón") - 0.2, 0.3))))
    qr = prog(t, wt(e, "reconoció") - 0.2, 0.4)
    if qr > 0:
        st["overlay"].append(("sello", "RECONOCIDO 2009", 270, 790, qr))
    qp = prog(t, wt(e, "nunca") - 0.3, 0.4)
    if qp > 0:
        st["overlay"].append(("paz", qp, t))


def esc_final(L, e, t, D, T, st):
    papel(L, T)
    sol(L, 270, 520, 150)
    st["overlay"].append(("seguir", prog(t, 0.0, 0.4), t))
    st["sin_cabecera"] = True


ESC_JEFE = []
FUNCS = {"gancho": esc_gancho, "viaje": esc_viaje, "bomba1": esc_bomba1, "heridas": esc_heridas, "tren": esc_tren,
         "like": esc_like, "jefe": esc_jefe, "bomba2": esc_bomba2, "vida": esc_vida, "final": esc_final}


def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "titular":
            _, t, e = it
            # visible desde el fotograma 0, con un «golpe» de escala
            s = 1 + 0.35 * math.exp(-t * 9)
            texto(O, "SOBREVIVIÓ A", 270, 335, 40 * s, TINTA, fuente="black", sombra=False)
            k2 = 1 + 0.5 * math.exp(-max(0, t - 0.35) * 8) if t > 0.35 else 1.5
            texto(O, "2", 270, 420, 110 * k2, ROJO_J, a=1.0, fuente="black", sombra=False)
            texto(O, "BOMBAS ATÓMICAS", 270, 505, 40 * s, TINTA, fuente="black", sombra=False)
            q = prog(t, wt(e, "real") - 0.2, 0.3)
            if q > 0:
                s_ = 1 + 1.4 * (1 - eo3(q))
                w_ = ancho("100% REAL", 34 * s_) + 34 * s_
                rect(O, 270 - w_ / 2, 590 - 26 * s_, 270 + w_ / 2, 590 + 26 * s_, PAPEL, a=q, r=10 * s_)
                sello(O, "100% REAL", 270, 590, q, size=34)
        elif tipo == "ficha":
            q = it[1]
            rect(O, 40, 760, 330, 840, TINTA, a=0.9 * q, r=10)
            texto(O, "TSUTOMU YAMAGUCHI", 56, 786, 18, PAPEL, a=q, fuente="black", anchor="lm", sombra=False)
            texto(O, "ingeniero naval · 29 años", 56, 816, 15, (200, 190, 170), a=q, fuente="semi", anchor="lm", sombra=False)
        elif tipo == "reloj":
            q = it[1]
            rect(O, 330, 340, 500, 400, TINTA, a=0.9 * q, r=10)
            texto(O, "8:15", 415, 370, 32, (255, 120, 90), a=q, fuente="mono", sombra=False)
        elif tipo == "marca":
            _, txt, x, y, q = it
            s = eob(q)
            w = ancho(txt, 18) + 24
            rect(O, x - w / 2 * s, y - 18 * s, x + w / 2 * s, y + 18 * s, ROJO_J, a=q, r=6)
            texto(O, txt, x, y, 18 * s, BLANCO, a=q, fuente="black", sombra=False)
        elif tipo == "grande":
            _, txt, y, q = it
            if q > 0:
                texto(O, txt, 270, y, 70 * (0.8 + 0.2 * eob(q)), ROJO_J, a=q, fuente="black")
        elif tipo == "sello":
            _, txt, x, y, q = it
            sello(O, txt, x, y, q)
        elif tipo == "giro":
            q = it[1]
            s = 1 + 0.8 * (1 - eo3(q))
            texto(O, "¿SU CIUDAD?", 270, 760, 30, TINTA, a=q, fuente="black", sombra=False)
            texto(O, "NAGASAKI", 270, 820, 64 * s, ROJO_J, a=q, fuente="black", sombra=False)
        elif tipo == "like":
            _, t, tl = it
            # corazón que se pulsa como un doble toque de TikTok
            q = prog(t, tl, 0.35)
            s = eob(q) * (1 + 0.08 * math.sin(t * 8))
            corazon(O, 270, 560, 110 * s, (254, 44, 85), a=cl(q * 1.5))
            texto(O, "DALE LIKE", 270, 735, 46 * (0.8 + 0.2 * eob(q)), TINTA, a=q, fuente="black", sombra=False)
            texto(O, "si no lo sabías", 270, 780, 20, GRIS_J, a=q, fuente="semi", sombra=False)
            rs = random.Random(3)
            for j in range(10):
                u = (t - tl - j * 0.08) / 1.2
                if 0 < u < 1:
                    corazon(O, 270 + rs.uniform(-160, 160) * u, 560 - 260 * u, 24 * (1 - u * 0.5), (254, 44, 85), a=1 - u)
        elif tipo == "bocadillo":
            _, txt, x, y, q = it
            lineas_b = txt.split("\n")
            w = max(ancho(l, 20) for l in lineas_b) + 30
            h = 34 * len(lineas_b) + 16
            x = cl(x, w / 2 + 10, W - w / 2 - 10)
            rect(O, x - w / 2, y - h / 2, x + w / 2, y + h / 2, BLANCO, a=q, r=16, outline=TINTA, w=2)
            poly(O, [(x - 10, y + h / 2 - 2), (x + 10, y + h / 2 - 2), (x, y + h / 2 + 18)], BLANCO, a=q)
            for j, l in enumerate(lineas_b):
                texto(O, l, x, y - h / 2 + 24 + j * 34, 20, TINTA, a=q, fuente="black", sombra=False)
        elif tipo == "x2":
            q = it[1]
            texto(O, "×2", 440, 340, 60 * eob(q) + 1, BLANCO, a=q, fuente="black")
        elif tipo == "paz":
            _, q, t = it
            texto(O, "☮", 430, 380, 60 * eob(q) + 1, TINTA, a=q, fuente="sym", sombra=False)
            texto(O, "NUNCA MÁS", 270, 860, 30, TINTA, a=q, fuente="black", sombra=False)
        elif tipo == "seguir":
            _, q, t = it
            # avatar + botón de seguir con toque animado
            circ(O, 270, 520, 70, fill=TINTA)
            texto(O, "M", 270, 520, 60, PAPEL, fuente="black", sombra=False)
            tt = (t % 2.0)
            toque = prog(tt, 0.8, 0.3)
            r = 22 * (1 - 0.15 * math.sin(toque * math.pi))
            circ(O, 270, 592, r, fill=(254, 44, 85) if toque < 0.5 else BLANCO)
            texto(O, "+" if toque < 0.5 else "✓", 270, 592, 26, BLANCO if toque < 0.5 else (254, 44, 85), fuente="sym",
                  sombra=False)
            if 0 < toque < 1:
                circ(O, 270, 592, 22 + 40 * toque, outline=(254, 44, 85), w=3, a=1 - toque)
            texto(O, "@mente404_0", 270, 650, 26, TINTA, fuente="black", sombra=False)
            texto(O, "Una historia real cada día", 270, 760, 24, ROJO_J, fuente="black", sombra=False)
            texto(O, "que parece inventada", 270, 795, 22, TINTA, fuente="semi", sombra=False)


def corazon(O, x, y, r, col, a=1.0):
    if r <= 1:
        return
    circ(O, x - r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    circ(O, x + r * 0.5, y - r * 0.2, r * 0.55, fill=col, a=a)
    poly(O, [(x - r * 1.02, y - r * 0.05), (x + r * 1.02, y - r * 0.05), (x, y + r * 0.95)], col, a=a)


def sello(O, txt, x, y, q, size=40):
    if q <= 0:
        return
    s = 1 + 1.4 * (1 - eo3(q))
    w = ancho(txt, size * s) + 34 * s
    rect(O, x - w / 2, y - size * 0.75 * s, x + w / 2, y + size * 0.75 * s, None, a=q, r=10 * s, outline=ROJO_J, w=5 * s)
    texto(O, txt, x, y, size * s, ROJO_J, a=q, fuente="black", sombra=False)


def cabecera(O, st):
    if st.get("sin_cabecera"):
        return
    w = ancho(CABECERA, 15) + 30
    rect(O, 270 - w / 2, 148, 270 + w / 2, 180, TINTA, a=0.85, r=16)
    texto(O, CABECERA, 270, 164, 15, PAPEL, fuente="black", sombra=False)


def fecha(O, e, t):
    txt = FECHA.get(e["nombre"])
    if not txt:
        return
    q = prog(t, 0.05, 0.3)
    rect(O, 20, 300, 20 + ancho(txt, 16, "mono") + 24, 332, TINTA, a=0.8 * q, r=8)
    texto(O, txt, 32, 316, 16, PAPEL, a=q, fuente="mono", anchor="lm", sombra=False)


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


ESC_JEFE.append(next(x for x in ESC if x["nombre"] == "jefe"))
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
        out = Image.blend(out, Image.new("RGB", (IW, IH), PAPEL), cl((T - (TOTAL - 0.5)) / 0.5))
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




def koto(f, dur=2.0, vol=0.1, seed=0):
    """Cuerda pulsada por síntesis Karplus-Strong."""
    n = int(dur * SR)
    p = max(2, int(SR / f))
    rng = np.random.default_rng(seed)
    buf = rng.uniform(-1, 1, p).astype(np.float32)
    out = np.zeros(n, np.float32)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * vol


def taiko(vol=0.5):
    n = int(0.9 * SR)
    u = np.arange(n) / SR
    s = np.sin(2 * np.pi * (60 + 70 * np.exp(-u * 18)) * u) * np.exp(-u * 5)
    s += 0.3 * np.random.default_rng(1).standard_normal(n) * np.exp(-u * 40)
    return (s * vol).astype(np.float32)


def silbido_alto(dur=0.8):
    n = int(dur * SR)
    u = np.arange(n) / SR
    return (np.sin(2 * np.pi * (3000 + 3000 * u / dur) * u) * np.clip(u / dur, 0, 1) ** 2 * 0.25).astype(np.float32)


def estallido():
    n = int(4.0 * SR)
    u = np.arange(n) / SR
    rng = np.random.default_rng(3)
    r = rng.standard_normal(n).astype(np.float32)
    r = np.convolve(r, np.ones(80) / 80, mode="same") * 10
    s = r * np.exp(-u * 0.9) + np.sin(2 * np.pi * (28 + 40 * np.exp(-u * 3)) * u) * np.exp(-u * 1.2) * 0.9
    return (s * 0.7).astype(np.float32)


def tren(dur):
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    t = 0.0
    k = 0
    while t < dur:
        m = int(0.12 * SR)
        u = np.arange(m) / SR
        a0 = int(t * SR)
        seg = np.random.default_rng(k).standard_normal(m).astype(np.float32)
        seg = np.convolve(seg, np.ones(12) / 12, mode="same") * np.exp(-u * 25)
        out[a0:a0 + m] += seg[:max(0, min(m, n - a0))] * (0.5 if k % 2 else 0.35)
        t += 0.22 if k % 2 == 0 else 0.34
        k += 1
    return out * 1.5


def pop():
    n = int(0.25 * SR)
    u = np.arange(n) / SR
    return (np.sin(2 * np.pi * (500 + 900 * u * 4) * u) * np.exp(-u * 18) * 0.6).astype(np.float32)


ESCALA = [62, 63, 67, 69, 70, 74, 75, 79]     # escala japonesa (in-sen) sobre Re


def musica(n):
    out = np.zeros(n, np.float32)
    t_esp = next(e for e in ESC if e["nombre"] == "vida")["t0"]
    rs = random.Random(5)
    t = 0.3
    k = 0
    patron = [0, 2, 4, 3, 5, 4, 2, 1]
    while t < TOTAL:
        nota_ = ESCALA[patron[k % 8]] if t < t_esp else [62, 66, 69, 74, 71, 69, 66, 64][k % 8]
        f = 440 * 2 ** ((nota_ - 69) / 12)
        colocar(out, koto(f, 1.6, 0.06, seed=k), t)
        if k % 4 == 0:
            colocar(out, koto(f / 2, 2.0, 0.05, seed=k + 100), t)
        t += 0.55 if t < t_esp else 0.6
        k += 1
    # taiko de fondo marcando el pulso (no en la vida tranquila)
    t = 0.0
    k = 0
    while t < t_esp:
        colocar(out, taiko(0.22 if k % 4 else 0.35), t)
        t += 1.1
        k += 1
    _ = rs
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
    fx = np.zeros(n, np.float32)
    E = {e["nombre"]: e for e in ESC}
    colocar(fx, taiko(1.0), 0.0, 0.9)                         # golpe inicial (fotograma 0)
    colocar(fx, braam(), 0.0, 0.6)
    g = E["gancho"]
    colocar(fx, taiko(1.0), g["t0"] + 0.05 + 0.35, 0.7)        # el «2»
    colocar(fx, golpe(), g["t0"] + wt(g, "real") - 0.2, 0.5)
    for nombre in ("bomba1", "bomba2"):
        b = E[nombre]
        tf = b["t0"] + wt(b, "destello") - 0.15
        colocar(fx, silbido_alto(0.8), tf - 0.8, 0.5)
        colocar(fx, estallido(), tf + 0.1, 1.0)
        # silencio tenso antes del destello
        a0, a1 = int((tf - 1.0) * SR), int(tf * SR)
        mus[a0:a1] *= np.linspace(1, 0.1, a1 - a0)
        mus[a1:a1 + int(1.5 * SR)] *= 0.1
    h = E["heridas"]
    colocar(fx, golpe() * 0.5, h["t0"] + wt(h, "sobrevive") - 0.2, 0.6)
    tr = E["tren"]
    colocar(fx, tren(wt(tr, "Nagasaki") - 0.6), tr["t0"], 0.5)
    colocar(fx, braam(), tr["t0"] + wt(tr, "Nagasaki") - 0.3, 0.9)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.7)
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.1, 0.5)
    colocar(fx, braam(), lk["t0"] + wt(lk, "imposible") - 0.3, 0.7)
    j = E["jefe"]
    colocar(fx, golpe() * 0.4, j["t0"] + wt(j, "loco") - 0.4, 0.5)
    v = E["vida"]
    colocar(fx, golpe() * 0.5, v["t0"] + wt(v, "reconoció") - 0.2, 0.5)
    f = E["final"]
    for k in range(3):
        colocar(fx, pop(), f["t0"] + 0.8 + k * 2.0, 0.5)
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
