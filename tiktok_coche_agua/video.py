"""TikTok vertical «Si tu coche cae al agua...»: corte transversal submarino, cuenta atrás,
personajes planos, subtítulos grandes palabra a palabra, música y efectos.

    python3 voz.py && python3 video.py        -> coche_agua_tiktok.mp4
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
SALIDA = os.path.join(AQUI, "coche_agua_tiktok.mp4")

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
CLAVE = {"minuto", "vida", "emergencias", "todavía", "segundo", "roba", "cinturón", "ventanilla", "puerta", "rompe",
         "esquina", "parabrisas", "romperse", "niños", "primero", "superficie", "112", "ventana", "fuera", "guarda",
         "solo", "nada", "agua"}


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


def pose_mix(a, b, k):
    pa, pb = POSES[a], POSES[b]
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
    capsula(L, hombro, cod, 22 * e, cuerpo_s, a)
    capsula(L, cod, (man[0] - 8 * s, man[1] + 4 * e), 20 * e, cuerpo_s, a)
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


# --- Escenas del TikTok «Si tu coche cae al agua...» (se insertan en video.py al montarlo) ---

POSES.update({
    "conduce": dict(rodilla=(70, 0), pie=(80, 80), cuello=(-10, -118), cabeza=(-4, -158), codo=(34, -70), mano=(84, -84)),
    "movil": dict(rodilla=(70, 0), pie=(80, 80), cuello=(-6, -118), cabeza=(0, -158), codo=(34, -82), mano=(14, -150)),
    "desabrocha": dict(rodilla=(70, 0), pie=(80, 80), cuello=(-6, -116), cabeza=(2, -156), codo=(34, -46), mano=(-12, -30)),
    "ventanilla": dict(rodilla=(70, 0), pie=(80, 80), cuello=(-2, -118), cabeza=(6, -158), codo=(56, -78), mano=(96, -96)),
    "golpea": dict(rodilla=(70, 0), pie=(80, 80), cuello=(4, -118), cabeza=(12, -156), codo=(60, -112), mano=(112, -116)),
    "nada": dict(rodilla=(10, 92), pie=(-6, 182), cuello=(0, -150), cabeza=(4, -196), codo=(30, -210), mano=(14, -262)),
    "nada2": dict(rodilla=(-10, 92), pie=(12, 182), cuello=(0, -150), cabeza=(4, -196), codo=(-30, -200), mano=(-10, -258)),
})

SUPERFICIE = 175           # línea del agua (vista submarina)
COCHE = (58, 132, 196)
COCHE_S = (40, 100, 160)

rb = random.Random(5)
BURBUJAS = [(rb.uniform(0, W), rb.uniform(0, H), rb.uniform(2, 7), rb.uniform(25, 70), rb.random() * 6) for _ in range(70)]


def rot(c, ang, p):
    ca, sa = math.cos(ang), math.sin(ang)
    return (c[0] + p[0] * ca - p[1] * sa, c[1] + p[0] * sa + p[1] * ca)


VENTANA = [(-80, -14), (-56, -62), (58, -62), (86, -14)]
VENT_DEL = [(4, -14), (4, -62), (58, -62), (86, -14)]        # ventanilla del conductor


def coche_capa(st, detalle=True):
    """Dibuja el coche en su propio lienzo (coords locales, centro = (0,0)). Devuelve imagen RGBA."""
    bw, bh = 360, 200
    img = Image.new("RGBA", (bw * K, bh * K), (0, 0, 0, 0))
    L = Capa(img)
    ox, oy = bw / 2, bh / 2 + 10

    def Q(pts):
        return [(x + ox, y + oy) for x, y in pts]

    nivel = st.get("nivel", 0.0)              # 0..1 agua dentro de la cabina
    ang = st.get("ang", 0.0)
    if detalle:
        # interior
        poly(L, Q(VENTANA), (78, 104, 128))
        rect(L, ox - 40, oy - 58, ox - 34, oy - 14, (36, 40, 50))
        # personas dentro, recortadas por la ventana
        per = Image.new("RGBA", img.size, (0, 0, 0, 0))
        LP = Capa(per)
        if st.get("nino", True):
            persona(LP, ox - 46, oy + 26, "sentado", 0.34)
        if st.get("conductor", True):
            info = persona(LP, ox + 20, oy + 30, st.get("pose", "conduce"), 0.42, ojos=st.get("ojos", 1.3))
            if st.get("cinturon", 1.0) > 0:
                k = st.get("cinturon", 1.0)
                hx, hy = ox + 20, oy + 30
                linea(LP, [(lerp(ox - 30, hx - 6, k), lerp(oy - 56, hy - 44, k)), (hx + 12, hy - 4)], (60, 60, 64), w=4)
            # volante
            linea(LP, [(ox + 58, oy - 26), (ox + 70, oy - 4)], (30, 30, 34), w=5)
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).polygon([((x + ox) * K, (y + oy) * K) for x, y in VENTANA], fill=255)
        img.paste(per, (0, 0), ImageChops.multiply(mask, per.getchannel("A")))
        L = Capa(img)
        # agua dentro (horizontal en el mundo -> inclinada en local)
        if nivel > 0:
            ly = -14 - 52 * nivel
            dx, dy = math.cos(-ang), math.sin(-ang)
            p0 = (0 - 400 * dx, ly - 400 * dy)
            p1 = (0 + 400 * dx, ly + 400 * dy)
            agua = Image.new("RGBA", img.size, (0, 0, 0, 0))
            LA = Capa(agua)
            poly(LA, Q([p0, p1, (p1[0], p1[1] + 500), (p0[0], p0[1] + 500)]), (60, 140, 200), a=0.6)
            linea(LA, Q([p0, p1]), (190, 230, 255), w=2, a=0.9)
            img.alpha_composite(Image.composite(agua, Image.new("RGBA", img.size, (0, 0, 0, 0)), mask))
        # cristal de la ventanilla del conductor
        baja = st.get("cristal_baja", 0.0)
        if baja < 1:
            top = -62 + 48 * baja
            pts = [(4, -14), (4, top), (58 + 28 * (top + 62) / 48, top), (86, -14)]
            vidrio = Image.new("RGBA", img.size, (0, 0, 0, 0))
            LV = Capa(vidrio)
            poly(LV, Q(pts), (170, 220, 245), a=0.28)
            linea(LV, Q([(14, top + 6), (30, top + 20)]), (240, 250, 255), w=2, a=0.5)
            img.alpha_composite(vidrio)
            L = Capa(img)
        grietas = st.get("grietas", 0.0)
        if grietas > 0:
            cx0, cy0 = 76, -20
            for j in range(9):
                a2 = math.radians(150 + j * 14)
                ln = 70 * grietas * (0.6 + 0.4 * ((j * 37) % 10) / 10)
                linea(L, Q([(cx0, cy0), (cx0 + ln * math.cos(a2), cy0 + ln * math.sin(a2))]), (240, 250, 255), w=1.5)
    else:
        poly(L, Q(VENTANA), (30, 40, 56))
    # carrocería: techo con el hueco de la ventana
    techo = Image.new("RGBA", img.size, (0, 0, 0, 0))
    poly(Capa(techo), Q([(-90, -10), (-60, -70), (62, -70), (98, -10)]), COCHE_S)
    hueco = Image.new("L", img.size, 0)
    ImageDraw.Draw(hueco).polygon([((x + ox) * K, (y + oy) * K) for x, y in VENTANA], fill=255)
    techo.putalpha(ImageChops.subtract(techo.getchannel("A"), hueco))
    img.alpha_composite(techo)
    L = Capa(img)
    rect(L, ox - 160, oy - 14, ox + 160, oy + 46, COCHE, r=16)
    rect(L, ox - 160, oy + 14, ox + 160, oy + 22, COCHE_S)
    linea(L, Q([(0, -66), (2, -12)]), COCHE_S, w=6)
    rect(L, ox + 140, oy - 6, ox + 160, oy + 8, (255, 230, 150), r=4)     # faro
    rect(L, ox - 160, oy - 4, ox - 148, oy + 8, (220, 70, 60), r=3)
    rect(L, ox + 10, oy, ox + 30, oy + 4, COCHE_S, r=2)                    # tirador
    for wx in (-98, 98):
        circ(L, ox + wx, oy + 46, 26, fill=(26, 26, 30))
        circ(L, ox + wx, oy + 46, 11, fill=(150, 150, 160))
    # redibuja el marco de la ventana (sin tapar el interior)
    marco = Q(VENTANA + [VENTANA[0]])
    linea(L, marco, COCHE_S, w=5)
    return img


def pegar_coche(img, capa, cx, cy, ang):
    r = capa.rotate(-math.degrees(ang), resample=Image.BICUBIC, expand=True)
    img.paste(r, (int(cx * K - r.width / 2), int((cy + 10) * K - r.height / 2)), r)


def fondo_submarino(L, T, profundo=0.0):
    for i in range(0, H, 6):
        k = cl((i - SUPERFICIE) / (H - SUPERFICIE))
        col = mezcla((40, 120, 170), (6, 22, 44), cl(k * 0.9 + profundo))
        if i < SUPERFICIE:
            col = mezcla((120, 170, 210), (70, 140, 190), i / SUPERFICIE)
        rect(L, 0, i, W, i + 6, col)
    # superficie ondulada
    pts = [(x, SUPERFICIE + 5 * math.sin(x / 30 + T * 2)) for x in range(0, W + 10, 10)]
    poly(L, pts + [(W, 0), (0, 0)], (150, 195, 225), a=0.9)
    linea(L, pts, (220, 240, 255), w=2.5)
    # rayos de luz
    for j in range(5):
        x = 60 + j * 110 + 20 * math.sin(T * 0.6 + j)
        poly(L, [(x, SUPERFICIE), (x + 40, SUPERFICIE), (x - 40 + 30 * j, H), (x - 140 + 30 * j, H)], (190, 230, 255),
             a=0.05 + 0.03 * math.sin(T + j))
    # burbujas sueltas
    for (x, y, r, v, f) in BURBUJAS:
        yy = (y - T * v) % (H - SUPERFICIE) + SUPERFICIE
        circ(L, x + 6 * math.sin(T * 2 + f), yy, r * 0.6, outline=(200, 235, 255), w=1, a=0.35)


def burbujas_desde(L, x, y, t, n=10, a=1.0, sem=0):
    for j in range(n):
        u = (t * 0.9 + j / n + sem * 0.13) % 1
        bx = x + 18 * math.sin(j * 2.3 + t * 3) + (j % 3 - 1) * 8
        by = y - u * 220
        if by < SUPERFICIE:
            continue
        circ(L, bx, by, 3 + (j % 4) * 1.5, outline=(220, 245, 255), w=1.4, a=a * (1 - u))


def pos_coche(T):
    """El coche se hunde despacio con el morro hacia abajo."""
    T0 = ESC[0]["t0"] + IMPACTO
    u = max(0.0, T - T0)
    cy = 470 + 70 * (1 - math.exp(-u / 25))
    ang = math.radians(16 + 2 * math.sin(u * 0.7))
    return (270, cy, ang)


IMPACTO = 1.75                 # segundo (dentro del gancho) en que el coche toca el agua


def restante(T):
    return max(0.0, 60 - (T - (ESC[0]["t0"] + IMPACTO)))


def nivel_agua(T):
    return cl((60 - restante(T)) / 62) * 0.85


def submarino_base(L, T, st, pose="conduce", **kw):
    fondo_submarino(L, T)
    cx, cy, ang = pos_coche(T)
    st.update(dict(ang=ang, nivel=nivel_agua(T), pose=pose))
    st.update(kw)
    capa = coche_capa(st)
    pegar_coche(L.img, capa, cx, cy, ang)
    L.d = ImageDraw.Draw(L.img, "RGBA")
    burbujas_desde(L, *rot((cx, cy), ang, (-40, -70)), T, n=6, a=0.8)
    st["cam"] = (cx, cy - 30)
    return cx, cy, ang


def esc_gancho(L, e, t, D, T, st):
    t_corte = wt(e, "Y") - 0.15
    if t < t_corte:
        # vista exterior: puente, caída y salpicadura
        for i in range(0, H, 6):
            rect(L, 0, i, W, i + 6, mezcla((250, 170, 120), (90, 110, 170), i / 600) if i < 600 else
                 mezcla((50, 100, 150), (20, 50, 90), (i - 600) / 360))
        circ(L, 400, 330, 50, fill=(255, 220, 160), a=0.9)
        # puente
        rect(L, -10, 360, 330, 382, (60, 60, 70))
        for px in (40, 200):
            rect(L, px, 382, px + 26, 640, (70, 70, 80))
        for rx in range(0, 330, 22):
            rect(L, rx, 334, rx + 4, 360, (90, 90, 100))
        rect(L, -10, 330, 330, 336, (90, 90, 100))
        # barandilla rota
        if t > 0.35:
            linea(L, [(312, 335), (340, 300)], (90, 90, 100), w=3)
        # agua
        pts = [(x, 610 + 6 * math.sin(x / 25 + T * 2)) for x in range(0, W + 10, 10)]
        poly(L, pts + [(W, H), (0, H)], (40, 96, 150))
        linea(L, pts, (170, 210, 240), w=2)
        # coche: avanza, cae en parábola y gira
        if t < IMPACTO:
            u = t / IMPACTO
            x = lerp(150, 420, u)
            y = 330 if t < 0.4 else 330 + 290 * ((t - 0.4) / (IMPACTO - 0.4)) ** 2
            ang = math.radians(0 if t < 0.4 else 40 * (t - 0.4) / (IMPACTO - 0.4))
            capa = coche_capa({}, detalle=False).resize((int(360 * K * 0.5), int(200 * K * 0.5)), Image.BICUBIC)
            pegar_coche(L.img, capa, x, y - 10, ang)
            L.d = ImageDraw.Draw(L.img, "RGBA")
        else:
            dt = t - IMPACTO
            # el coche asoma y se hunde
            hund = cl(dt / 1.2)
            capa = coche_capa({}, detalle=False).resize((int(360 * K * 0.5), int(200 * K * 0.5)), Image.BICUBIC)
            pegar_coche(L.img, capa, 420, 615 + 50 * hund, math.radians(40))
            L.d = ImageDraw.Draw(L.img, "RGBA")
            pts = [(x, 610 + 6 * math.sin(x / 25 + T * 2)) for x in range(0, W + 10, 10)]
            poly(L, pts + [(W, H), (0, H)], (40, 96, 150), a=0.85)
            # salpicadura
            rs = random.Random(1)
            for j in range(60):
                ang = rs.uniform(-2.6, -0.5)
                v = rs.uniform(150, 420)
                x = 420 + math.cos(ang) * v * dt
                y = 610 + math.sin(ang) * v * dt + 420 * dt * dt
                if y < 615:
                    circ(L, x, y, rs.uniform(3, 8), fill=(220, 240, 255), a=cl(1.5 - dt))
            for j in range(3):
                rr = (dt * 120 + j * 30)
                L.d.ellipse(P(420 - rr, 610 - rr * 0.15, 420 + rr, 610 + rr * 0.15),
                            outline=L.c((220, 240, 255), cl(1 - dt / 2)), width=2 * K)
            st["shake"] = 8 * math.exp(-dt * 6)
    else:
        submarino_base(L, T, st, pose="conduce", ojos=1.8)
        st["zoom"] = 1.5
        q = prog(t, wt(e, "costarte") - 0.2, 0.4)
        if q > 0:
            st["overlay"].append(("pregunta", q))
    if t > wt(e, "minuto") - 0.2:
        st["timer"] = True


def esc_telefono(L, e, t, D, T, st):
    tn = wt(e, "No") - 0.1
    pose = "movil" if t < tn + 0.4 else pose_mix("movil", "conduce", prog(t, tn + 0.4, 0.4))
    submarino_base(L, T, st, pose=pose, ojos=1.8)
    st["zoom"] = 1.55
    st["paso"] = ("✕", "NO LLAMES TODAVÍA")
    q = prog(t, 0.1, 0.3)
    st["overlay"].append(("movil", q, prog(t, tn, 0.3), t))
    st["timer"] = True


def esc_cinturon(L, e, t, D, T, st):
    k = 1 - eio(prog(t, wt(e, "suéltate") + 0.1, 0.6))
    pose = pose_mix("conduce", "desabrocha", min(1, prog(t, 0.2, 0.4)) * (1 - prog(t, D - 0.5, 0.4)))
    submarino_base(L, T, st, pose=pose, cinturon=k)
    st["zoom"] = 1.6
    st["paso"] = ("1", "CINTURÓN")
    st["timer"] = True
    if k < 0.2:
        st["overlay"].append(("clic", prog(t, wt(e, "suéltate") + 0.5, 0.5)))


def esc_ventana(L, e, t, D, T, st):
    t_abre = wt(e, "abre") - 0.1
    t_puerta = wt(e, "agua") - 0.2
    baja = eio(prog(t, t_abre + 0.2, 1.4))
    pose = pose_mix("conduce", "ventanilla", prog(t, t_abre - 0.2, 0.4))
    cx, cy, ang = submarino_base(L, T, st, pose=pose, cinturon=0, cristal_baja=baja)
    st["zoom"] = 1.6 if t < t_puerta else lerp(1.6, 1.25, eio(prog(t, t_puerta, 0.6)))
    st["paso"] = ("2", "VENTANILLA, NO PUERTA")
    st["timer"] = True
    if t > t_puerta:
        # flechas de presión del agua sobre la puerta
        q = prog(t, t_puerta, 0.4)
        for j in range(4):
            px, py = rot((cx, cy), ang, (30, 12 + j * 0))
            off = 12 * math.sin(t * 8 + j)
            x0 = cx + 150 - j * 8 + off
            y0 = cy - 40 + j * 30
            linea(L, [(x0 + 60, y0), (x0, y0)], (255, 90, 80), w=5, a=q)
            poly(L, [(x0 - 4, y0), (x0 + 12, y0 - 10), (x0 + 12, y0 + 10)], (255, 90, 80), a=q)
        st["overlay"].append(("puerta_x", q))


def esc_romper(L, e, t, D, T, st):
    t_rompe = wt(e, "rompe") - 0.1
    t_esq = wt(e, "esquina") - 0.05
    t_para = wt(e, "parabrisas") - 0.2
    golpe = prog(t, t_esq, 0.12)
    pose = pose_mix("ventanilla", "golpea", 0.5 + 0.5 * math.sin(min(t, t_esq) * 6)) if t_rompe < t < t_esq else \
        ("golpea" if t >= t_esq else "ventanilla")
    grietas = eo3(prog(t, t_esq, 0.25))
    roto = t > t_esq + 0.5
    cx, cy, ang = submarino_base(L, T, st, pose=pose, cinturon=0, cristal_baja=1.0 if roto else 0.0,
                                 grietas=0 if roto else grietas)
    st["zoom"] = 1.65 if t < t_para else 1.65
    st["shake"] = 6 * math.exp(-(t - t_esq) * 9) if t > t_esq else 0
    st["paso"] = ("2", "ROMPE POR UNA ESQUINA")
    st["timer"] = True
    if roto:
        # trozos de cristal flotando
        rs = random.Random(3)
        dt = t - t_esq - 0.5
        bx, by = rot((cx, cy), ang, (76, -20))
        for j in range(26):
            a2 = rs.uniform(0, 6.28)
            v = rs.uniform(10, 60)
            x = bx + math.cos(a2) * v * (dt + 0.3)
            y = by + math.sin(a2) * v * (dt + 0.3) - 10 * dt
            s = rs.uniform(2, 5)
            poly(L, [(x, y - s), (x + s, y), (x, y + s * 0.7), (x - s * 0.8, y)], (200, 235, 255), a=cl(1.2 - dt * 0.4))
    if t > t_rompe:
        st["overlay"].append(("martillo", prog(t, t_rompe, 0.3), t < t_esq, t))
    if t > t_para:
        st["overlay"].append(("parabrisas", prog(t, t_para, 0.3)))


def esc_ninos(L, e, t, D, T, st):
    t_sale = wt(e, "sácalos") - 0.1
    sale = eio(prog(t, t_sale, 1.4))
    cx, cy, ang = submarino_base(L, T, st, pose="ventanilla", cinturon=0, cristal_baja=1.0, nino=sale < 0.05)
    st["zoom"] = 1.45
    st["paso"] = ("3", "NIÑOS PRIMERO")
    st["timer"] = True
    if sale >= 0.05:
        wx, wy = rot((cx, cy), ang, (40, -60))
        x = lerp(wx, wx + 20, sale)
        y = lerp(wy + 10, wy - 150, sale)
        persona(L, x, y, pose_mix("nada", "nada2", 0.5 + 0.5 * math.sin(t * 8)), 0.34)
        burbujas_desde(L, x, y - 70, t, n=5, sem=2)


def esc_fuera(L, e, t, D, T, st):
    t_sal = wt(e, "sal") - 0.2
    t_llama = wt(e, "llama") - 0.2
    fondo_submarino(L, T)
    cx, cy, ang = pos_coche(T)
    cy += 120 * eio(prog(t, t_sal, 3))
    st.update(dict(ang=ang, nivel=nivel_agua(T), conductor=t < t_sal, nino=False, cinturon=0, cristal_baja=1.0,
                   pose="ventanilla"))
    capa = coche_capa(st)
    pegar_coche(L.img, capa, cx, cy, ang)
    L.d = ImageDraw.Draw(L.img, "RGBA")
    burbujas_desde(L, *rot((cx, cy), ang, (-40, -70)), T, n=8)
    # niño ya en la superficie
    nx, ny = 200, SUPERFICIE + 30 + 4 * math.sin(t * 3)
    persona(L, nx, ny + 60, "nada", 0.34)
    if t >= t_sal:
        u = eio(prog(t, t_sal, 2.2))
        wx, wy = rot((cx, cy), ang, (40, -60))
        x = lerp(wx, 330, u)
        y = lerp(wy + 40, SUPERFICIE + 105, u)
        persona(L, x, y, pose_mix("nada", "nada2", 0.5 + 0.5 * math.sin(t * 7)), 0.48)
        burbujas_desde(L, x, y - 100, t, n=6, sem=4)
        if u >= 1:
            st["timer_ok"] = True
    st["zoom"] = 1.0
    st["paso"] = ("4", "FUERA")
    st["timer"] = True
    if t > t_llama:
        st["overlay"].append(("llama112", prog(t, t_llama, 0.4), t))


def esc_final(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (10, 24, 40))
    fondo_submarino(L, T, profundo=0.4)
    rect(L, 0, 0, W, H, (6, 14, 26), a=0.55)
    items = [("cinturón", "CINTURÓN"), ("ventana", "VENTANA"), ("niños", "NIÑOS"), ("fuera", "FUERA")]
    for j, (pal, txt) in enumerate(items):
        q = prog(t, wt(e, pal) - 0.15, 0.35)
        if q <= 0:
            continue
        y = 360 + j * 74
        s = eob(q)
        rect(L, 70, y - 30, 470, y + 30, (255, 255, 255), a=0.08 * q, r=30)
        circ(L, 108, y, 22 * s, fill=AMARILLO, a=q)
        texto(L, str(j + 1), 108, y, 24 * s, (20, 20, 20), a=q, fuente="black", sombra=False)
        texto(L, txt, 150, y, 36 * (0.7 + 0.3 * s), BLANCO, a=q, fuente="black", anchor="lm")
    q = prog(t, wt(e, "guarda") - 0.1, 0.4)
    if q > 0:
        lleno = prog(t, wt(e, "vídeo") - 0.1, 0.3)
        cx, cy, s = 270, 700, eob(q)
        w, h = 46 * s, 60 * s
        poly(L, [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx, cy + h / 2 - 17 * s),
                 (cx - w / 2, cy + h / 2)], mezcla((90, 90, 100), AMARILLO, lleno), a=q)
    st["sin_paso"] = True


FUNCS = {"gancho": esc_gancho, "telefono": esc_telefono, "cinturon": esc_cinturon, "ventana": esc_ventana,
         "romper": esc_romper, "ninos": esc_ninos, "fuera": esc_fuera, "final": esc_final}


# ------------------------------------------------------------------ overlays
def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "pregunta":
            q = it[1]
            texto(O, "?", 430, 360 + 20 * (1 - eo3(q)), 80, ROJO, a=q, fuente="black")
        elif tipo == "movil":
            _, q, tach, t = it
            x, y = 400, 420
            s = eob(q)
            rect(O, x - 38 * s, y - 70 * s, x + 38 * s, y + 70 * s, (20, 20, 24), a=q, r=12)
            rect(O, x - 32 * s, y - 60 * s, x + 32 * s, y + 56 * s, (60, 180, 110), a=q, r=6)
            texto(O, "112", x, y - 20 * s, 22 * s, BLANCO, a=q, fuente="black", sombra=False)
            texto(O, "llamando…" if tach == 0 else "", x, y + 10 * s, 11 * s, BLANCO, a=q, fuente="bold", sombra=False)
            if tach > 0:
                k = eo3(tach)
                linea(O, [(x - 60, y - 60), (x - 60 + 120 * k, y - 60 + 120 * k)], ROJO, w=10)
                if k > 0.5:
                    linea(O, [(x + 60, y - 60), (x + 60 - 120 * (k - .5) * 2, y - 60 + 120 * (k - .5) * 2)], ROJO, w=10)
        elif tipo == "clic":
            q = it[1]
            texto(O, "¡CLIC!", 160, 400 - 20 * eo3(q), 34, AMARILLO, a=1 - q * 0.6, fuente="black")
        elif tipo == "puerta_x":
            q = it[1]
            rect(O, 330, 560, 510, 610, (0, 0, 0), a=0.6 * q, r=24)
            texto(O, "✕ PUERTA", 420, 585, 24, ROJO, a=q, fuente="sym", sombra=False)
        elif tipo == "martillo":
            _, q, golpeando, t = it
            x, y = 420, 400
            ang = math.radians(-30 + (25 * math.sin(t * 14) if golpeando else 20))
            ca, sa = math.cos(ang), math.sin(ang)

            def R2(px, py):
                return (x + px * ca - py * sa, y + px * sa + py * ca)
            linea(O, [R2(0, 60), R2(0, -10)], (240, 200, 60), w=12, a=q)
            poly(O, [R2(-28, -26), R2(28, -26), R2(36, -12), R2(28, 0), R2(-28, 0)], ROJO, a=q)
            poly(O, [R2(28, -26), R2(44, -13), R2(28, 0)], (220, 220, 230), a=q)
            texto(O, "rompecristales", x, y + 92, 15, BLANCO, a=q, fuente="bold")
        elif tipo == "parabrisas":
            q = it[1]
            rect(O, 70, 560, 470, 612, (0, 0, 0), a=0.65 * q, r=26)
            texto(O, "✕ PARABRISAS: NO SE ROMPE", 270, 586, 20, ROJO, a=q, fuente="sym", sombra=False)
        elif tipo == "llama112":
            _, q, t = it
            x, y = 400, 270 + 70
            s = eob(q)
            rect(O, x - 70 * s, y - 26 * s, x + 70 * s, y + 26 * s, VERDE, a=q, r=26)
            texto(O, "☎ 112", x, y, 26 * s, BLANCO, a=q, fuente="sym", sombra=False)
            for j in range(3):
                u = (t * 1.2 + j / 3) % 1
                O.d.arc(P(x - 70 - 30 * u, y - 40 - 30 * u, x + 70 + 30 * u, y + 40 + 30 * u), 300, 60,
                        fill=O.c(VERDE, q * (1 - u)), width=3 * K)


def temporizador(O, st, T):
    if not st.get("timer"):
        return
    r = restante(T)
    ok = st.get("timer_ok")
    x, y = 460, 345
    urg = cl((30 - r) / 30)
    col = VERDE if ok else mezcla(BLANCO, ROJO, urg)
    pul = 1 + (0.06 * max(0, math.sin(T * 6.28)) * urg if not ok else 0)
    circ(O, x, y, 40 * pul, fill=(0, 0, 0), a=0.6)
    frac = r / 60
    O.d.arc(P(x - 36 * pul, y - 36 * pul, x + 36 * pul, y + 36 * pul), -90, -90 + 360 * frac, fill=O.c(col), width=5 * K)
    if ok:
        texto(O, "✓", x, y, 34, VERDE, fuente="sym", sombra=False)
    else:
        texto(O, f"{int(math.ceil(r))}", x, y - 4, 28, col, fuente="black", sombra=False)
        texto(O, "seg", x, y + 18, 10, col, fuente="bold", sombra=False)


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
    texto(O, s, x0 + 24, 150, 18, (20, 20, 20), a=q, fuente="black", sombra=False)
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
    st = {"overlay": [], "shake": 0, "zoom": 1.0, "cam": (270, 480)}
    FUNCS[e["nombre"]](L, e, t, D, T, st)
    img = L.img
    z = st["zoom"]
    sh = st["shake"]
    if z != 1.0 or sh:
        z = z * (1 + 0.02 * eio(t / D))
        fx, fy = st["cam"]
        cw, ch = IW / z, IH / z
        x0 = cl(fx * K - cw / 2, 0, IW - cw) + sh * K * math.sin(T * 90)
        y0 = cl(fy * K - ch * 0.58, 0, IH - ch) + sh * K * math.cos(T * 70)
        img = img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    img = ImageChops.multiply(img, VINETA())
    O = Capa(img)
    overlays(O, st, T)
    temporizador(O, st, T)
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
    # rumor submarino grave
    rng = np.random.default_rng(2)
    r = rng.standard_normal(n).astype(np.float32)
    r = np.convolve(r, np.ones(400) / 400, mode="same") * 3
    out += r * 0.08
    # bajo pulsante de urgencia (Re menor) a 120 bpm
    beat = 0.5
    prog_ = [38, 38, 34, 36]
    k = 0
    while k * beat < TOTAL:
        t0 = k * beat
        a0 = int(t0 * SR)
        m = min(n - a0, int(0.45 * SR))
        if m > 0:
            u = np.arange(m) / SR
            f = 440 * 2 ** ((prog_[(k // 8) % 4] - 69) / 12)
            out[a0:a0 + m] += 0.12 * np.tanh(2 * np.sin(2 * np.pi * f * u)) * np.exp(-u * 5)
        k += 1
    # pad
    for f, g in ((146.8, 0.03), (174.6, 0.025), (220, 0.02)):
        out += g * np.sin(2 * np.pi * f * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * tt))
    return out


def mezclar():
    n = int((TOTAL + 0.3) * SR)
    voz = np.zeros(n, np.float32)
    for e in ESC:
        colocar(voz, leer(os.path.join(BUILD, f"voz_{e['i']}.mp3")), e["voz_t0"])
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    mus = musica(n)
    fx = np.zeros(n, np.float32)
    t_imp = ESC[0]["t0"] + IMPACTO
    mus[:int(t_imp * SR)] *= 0.35
    colocar(fx, splash(), t_imp, 0.9)
    colocar(fx, golpe() * 0.5, 0.35, 0.5)          # barandilla
    # tic-tac del temporizador (1 por segundo) hasta salir
    fuera = next(e for e in ESC if e["nombre"] == "fuera")
    t_fin = fuera["t0"] + wt(fuera, "sal") + 2.0
    t = t_imp + 1
    while t < t_fin:
        colocar(fx, tic(), t, 0.25 + 0.25 * cl((t - t_imp) / 50))
        t += 1
    for j, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(j, 0.45), e["t0"] - 0.22, 0.3)
    rom = next(e for e in ESC if e["nombre"] == "romper")
    colocar(fx, golpe() * 0.6, rom["t0"] + wt(rom, "esquina") - 0.05, 0.6)
    colocar(fx, cristal(), rom["t0"] + wt(rom, "esquina") - 0.02, 0.8)
    rng = np.random.default_rng(4)
    for k in range(70):
        colocar(fx, burbuja(k), rng.uniform(t_imp, t_fin), 0.06)
    # final: la música cae al salir
    a0 = int(t_fin * SR)
    mus[a0:] *= np.linspace(1, 0.5, n - a0)
    env = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.45 * np.clip(env * 12, 0, 1)
    total = voz + mus * duck + fx
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
