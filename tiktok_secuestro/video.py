"""TikTok vertical «Si te secuestran...»: personajes planos, iluminación de bombilla,
subtítulos grandes palabra a palabra, música de tensión y efectos.

    python3 voz.py && python3 video.py        -> secuestro_tiktok.mp4
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
SALIDA = os.path.join(AQUI, "secuestro_tiktok.mp4")

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
    d = VOZ_OFF + dv + COLA + (1.4 if i == len(DATOS) - 1 else 0) + (0.5 if seg["escena"] == "rescate" else 0)
    ESC.append({"i": i, "nombre": seg["escena"], "t0": _t, "dur": d, "voz_t0": _t + VOZ_OFF + (0.5 if seg["escena"] == "rescate" else 0),
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
CLAVE = {"secuestran", "peligro", "nunca", "imaginas", "respira", "pánico", "todo", "detalle", "persona", "nombre",
         "familia", "provoques", "duerme", "peligroso", "rescate", "suelo", "vista", "corras", "amenaza", "guarda",
         "necesites", "giros", "sonidos", "olores", "tiempo", "come", "bebe", "conoces"}


def construir_subs():
    bloques = []
    for e in ESC:
        toks = e["texto"].split()
        ws = e["palabras"]
        if len(toks) != len(ws):
            toks = [w["w"] for w in ws]
        chunk = []
        for tok, w in zip(toks, ws):
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


# ------------------------------------------------------------------ habitación
SUELO_Y = 640
BOMBILLA_ANCLA = (250, -10)
CABLE = 330


def habitacion_base():
    img = Image.new("RGB", (IW, IH), (92, 80, 68))
    L = Capa(img)
    # pared con degradado vertical
    for i in range(0, SUELO_Y, 4):
        k = i / SUELO_Y
        rect(L, 0, i, W, i + 4, mezcla((70, 62, 54), (104, 90, 76), k))
    # ladrillos
    rnd = random.Random(2)
    for fila in range(0, SUELO_Y // 26 + 1):
        y = fila * 26
        off = (fila % 2) * 30
        linea(L, [(0, y), (W, y)], (60, 52, 45), w=1.2, a=0.6)
        for cx in range(-off, W, 60):
            linea(L, [(cx, y), (cx, y + 26)], (60, 52, 45), w=1.2, a=0.6)
            if rnd.random() < .15:
                rect(L, cx + 2, y + 2, cx + 58, y + 24, (110, 96, 82), a=0.25)
    # zócalo y suelo
    rect(L, 0, SUELO_Y - 10, W, SUELO_Y, (54, 46, 40))
    for i in range(SUELO_Y, H, 4):
        k = (i - SUELO_Y) / (H - SUELO_Y)
        rect(L, 0, i, W, i + 4, mezcla((88, 76, 64), (50, 44, 38), k))
    # ventanuco con barrotes
    rect(L, 18, 300, 132, 372, (42, 38, 36), r=4)
    rect(L, 24, 306, 126, 366, (120, 140, 160))
    for bx in range(36, 126, 20):
        rect(L, bx, 304, bx + 6, 368, (50, 50, 54))
    # tubería en la pared
    rect(L, 0, 252, W, 260, (66, 58, 50))
    return img


ROOM = None


def luz(T, extra=None, ambiente=0.30, potencia=1.0, bx=None, by=None):
    """Mapa de luz (baja resolución) centrado en la bombilla."""
    sw, sh = IW // 12, IH // 12
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    ux, uy = bx / W * sw, by / H * sh
    d2 = ((xx - ux) / sw) ** 2 + ((yy - uy) / sw * 0.85) ** 2
    m = np.exp(-d2 / 0.14) * 1.1 * potencia
    # charco de luz en el suelo
    fy = SUELO_Y / H * sh + 6
    d3 = ((xx - ux) / (sw * 0.55)) ** 2 + ((yy - fy) / (sh * 0.07)) ** 2
    m += np.exp(-d3) * 0.35 * potencia
    m = ambiente + m
    col = np.stack([m * 1.0, m * 0.9, m * 0.74], -1)
    if extra is not None:
        col = col + extra
    img = Image.fromarray(np.clip(col * 255, 0, 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR)
    return img


def bombilla_pos(T, amp=7):
    ang = math.radians(amp * math.sin(T * 1.6))
    return BOMBILLA_ANCLA[0] + CABLE * math.sin(ang), BOMBILLA_ANCLA[1] + CABLE * math.cos(ang)


def dibujar_bombilla(L, bx, by, encendida=1.0):
    linea(L, [BOMBILLA_ANCLA, (bx, by - 14)], (20, 20, 20), w=1.6)
    rect(L, bx - 7, by - 22, bx + 7, by - 8, (60, 60, 60), r=2)
    circ(L, bx, by, 15, fill=mezcla((120, 110, 90), (255, 248, 220), encendida))


def sombra_de(bx, x):
    """Desplazamiento de la sombra proyectada en la pared según la bombilla."""
    return (x - bx) * 0.35 + 30, -20


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    bx, by = st["bombilla"]
    # captor aparece desde la sombra
    k = eio(prog(t, 0.3, 1.6))
    cx = lerp(560, 395, k)
    vx = 190
    st["luces"] = []
    for sombra in (True, False):
        if sombra:
            ox, oy = sombra_de(bx, vx)
            sil = (40, 34, 30)
            silla(L, vx + ox, 555 + oy, sombra=sil, a=0.55)
            persona(L, vx + ox, 555 + oy, "sentado", 1.0, sombra=sil, a=0.55)
            ox2, _ = sombra_de(bx, cx)
            persona(L, cx + ox2 + 20, 450 - 40, "de_pie", 1.2, flip=True, tipo="captor", sombra=sil, a=0.5)
        else:
            silla(L, vx, 555)
            mira = prog(t, 1.2, 0.4)
            persona(L, vx, 555, pose_mix("sentado", "sentado_respira", 0.5 + 0.5 * math.sin(t * 5) * 0.3), 1.0,
                    ojos=1 + 0.6 * mira)
            persona(L, cx, 450, "de_pie", 1.0, flip=True, tipo="captor")
    # destello del futuro (sirenas) cuando dice "peligro"
    tp = wt(e, "peligro")
    q = prog(t, tp - 0.1, 1.2)
    if 0 < q < 1:
        st["sirena"] = (1 - q) * (0.5 + 0.5 * math.sin(t * 30))
    # signo de interrogación al final
    qi = prog(t, wt(e, "imaginas") - 0.2, 0.5)
    if qi > 0:
        st["overlay"].append(("icono_pregunta", qi))


def esc_calma(L, e, t, D, T, st):
    bx, by = st["bombilla"]
    vx = 230
    resp = 0.5 + 0.5 * math.sin(t * 2.2)
    ox, oy = sombra_de(bx, vx)
    silla(L, vx + ox, 555 + oy, sombra=(40, 34, 30), a=0.55)
    persona(L, vx + ox, 555 + oy, "sentado_respira", 1.0, sombra=(40, 34, 30), a=0.55)
    silla(L, vx, 555)
    persona(L, vx, 555, pose_mix("sentado_respira", "sentado", resp * 0.3), 1.0 + 0.01 * resp,
            ojos=0.1 if 0.6 < (t % 3) < 2.4 and t > wt(e, "respira") else 1)
    st["overlay"].append(("monitor", t, e))
    st["paso"] = (1, "MANTÉN LA CALMA")


def esc_observa(L, e, t, D, T, st):
    st["sin_luz"] = True
    # mapa nocturno
    rect(L, 0, 0, W, H, (16, 22, 34))
    for gx in range(0, W + 1, 45):
        linea(L, [(gx, 0), (gx, H)], (30, 40, 58), w=1)
    for gy in range(0, H + 1, 45):
        linea(L, [(0, gy), (W, gy)], (30, 40, 58), w=1)
    # manzanas
    rnd = random.Random(4)
    for gx in range(0, W, 90):
        for gy in range(300, 860, 90):
            if rnd.random() < .7:
                rect(L, gx + 12, gy + 12, gx + 78, gy + 78, (24, 32, 48), r=6)
    ruta = [(60, 624), (60, 546), (240, 546), (240, 468), (420, 468), (420, 384), (150, 384), (150, 330), (470, 330)]
    largos = [math.dist(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1)]
    total = sum(largos)
    tr0, tr1 = wt(e, "giros") - 0.3, wt(e, "Cada") - 0.2
    avance = eio(prog(t, tr0, tr1 - tr0)) * total
    pts = [ruta[0]]
    acc = 0
    cur = ruta[0]
    giros = 0
    for i, lg in enumerate(largos):
        if acc + lg <= avance:
            pts.append(ruta[i + 1])
            acc += lg
            cur = ruta[i + 1]
            giros = i
        else:
            u = (avance - acc) / lg
            cur = (lerp(ruta[i][0], ruta[i + 1][0], u), lerp(ruta[i][1], ruta[i + 1][1], u))
            pts.append(cur)
            break
    linea(L, pts, (255, 200, 80), w=7, a=0.35)
    linea(L, pts, AMARILLO, w=3.5)
    for i in range(1, len(pts) - 1):
        circ(L, pts[i][0], pts[i][1], 6, fill=BLANCO)
    # coche
    circ(L, cur[0], cur[1], 14, fill=ROJO)
    circ(L, cur[0], cur[1], 22 + 6 * math.sin(t * 8), outline=ROJO, w=2, a=0.6)
    # etiquetas: giros, sonidos, olores, tiempo
    etiquetas = [("giros", f"↱ {giros} giros", 30, 700), ("sonidos", "♪ campanas", 270, 700),
                 ("olores", "≈ olor a pan", 30, 752), ("tiempo", "◷ 14 min", 270, 752)]
    st["paso"] = (2, "FÍJATE EN TODO")
    for pal, txt, x, y in etiquetas:
        q = prog(t, wt(e, pal) - 0.15, 0.4)
        if q > 0:
            if pal == "tiempo":
                txt = f"◷ {int(lerp(3, 14, prog(t, wt(e, 'tiempo'), 1.2)))} min"
            st["overlay"].append(("chip", txt, x + 20 * (1 - eo3(q)), y, q))
    q = prog(t, wt(e, "encontrarte") - 0.3, 0.5)
    if q > 0:
        circ(L, 470, 330, 28 * eob(q), outline=VERDE, w=4, a=q)
        circ(L, 470, 330, 10 * eob(q), fill=VERDE, a=q)


def esc_humaniza(L, e, t, D, T, st):
    bx, by = st["bombilla"]
    vx, cx = 180, 390
    habla = 0.5 + 0.5 * math.sin(t * 11)
    hablando = any(w["t"] + e["voz_t0"] - e["t0"] <= t <= w["t"] + w["d"] + e["voz_t0"] - e["t0"] for w in e["palabras"])
    suaviza = eio(prog(t, wt(e, "Cuesta") - 0.2, 1.0))
    for sombra in (True, False):
        sil = (40, 34, 30) if sombra else None
        ox, oy = sombra_de(bx, vx) if sombra else (0, 0)
        silla(L, vx + ox, 555 + oy, sombra=sil, a=0.55 if sombra else 1)
        persona(L, vx + ox, 555 + oy, pose_mix("sentado", "sentado_habla", habla if t > 0.4 else 0), 1.0,
                sombra=sil, a=0.55 if sombra else 1, boca=habla if hablando and not sombra else 0)
        ox, oy = sombra_de(bx, cx) if sombra else (0, 0)
        persona(L, cx + ox, 450 + oy, pose_mix("de_pie_brazos", "de_pie_inclina", suaviza), 1.0, flip=True, tipo="captor",
                sombra=sil, a=0.5 if sombra else 1)
    st["paso"] = (3, "QUE TE VEAN COMO PERSONA")
    qn = prog(t, wt(e, "nombre") - 0.2, 0.4)
    if qn > 0:
        st["overlay"].append(("bocadillo", "Me llamo Dani…", 150, 330, qn * (1 - prog(t, wt(e, "habla") - 0.1, 0.25))))
    qf = prog(t, wt(e, "familia") - 0.25, 0.4)
    if qf > 0:
        st["overlay"].append(("foto", 300, 372, qf * (1 - prog(t, wt(e, "Cuesta") + 0.6, 0.3))))
    if suaviza > 0:
        st["overlay"].append(("corazon", cx - 10, 205, suaviza))


def esc_fuerzas(L, e, t, D, T, st):
    bx, by = st["bombilla"]
    vx = 220
    tc, tb, td = wt(e, "Come") - 0.1, wt(e, "bebe") - 0.1, wt(e, "duerme") - 0.1
    if t < tc:
        pose, ojos = "sentado", 1
    elif t < td:
        k = 0.5 + 0.5 * math.sin((t - tc) * 7)
        pose, ojos = pose_mix("sentado", "sentado_come", 0.4 + 0.6 * k), 1
    else:
        pose, ojos = pose_mix("sentado", "sentado_duerme", eio(prog(t, td, 0.6))), 0
    for sombra in (True, False):
        sil = (40, 34, 30) if sombra else None
        ox, oy = sombra_de(bx, vx) if sombra else (0, 0)
        silla(L, vx + ox, 555 + oy, sombra=sil, a=0.55 if sombra else 1)
        info = persona(L, vx + ox, 555 + oy, pose, 1.0, sombra=sil, a=0.55 if sombra else 1, ojos=ojos)
    # cuenco de comida y vaso en el suelo
    rect(L, 330, 616, 380, 640, (200, 200, 205), r=8)
    rect(L, 334, 610, 376, 618, (230, 210, 150), r=4)
    rect(L, 400, 600, 422, 640, (180, 210, 230), a=0.85, r=3)
    rect(L, 402, 612 + 18 * prog(t, tb, 1.5), 420, 638, (90, 150, 220), a=0.9)
    if t >= tc and t < td:
        circ(L, info["mano"][0] + 6, info["mano"][1] - 8, 6, fill=(230, 210, 150))
    st["paso"] = (4, "GUARDA FUERZAS")
    st["overlay"].append(("bateria", prog(t, tc, D - tc), t > wt(e, "provoques") - 0.2 and t < tc, t))
    if t > td:
        st["overlay"].append(("zzz", info["cabeza"][0] + 30, info["cabeza"][1] - 40, t - td))


def esc_rescate(L, e, t, D, T, st):
    bx, by = st["bombilla"]
    vx = 200
    t_puerta = wt(e, "rescate") - 0.05
    t_suelo = wt(e, "suelo") - 0.2
    # puerta a la derecha
    abierta = eo3(prog(t, t_puerta, 0.25))
    rect(L, 440, 360, 540, 640, (30, 26, 24))
    if abierta < 1:
        rect(L, 440 + 100 * abierta, 360, 540, 640, (96, 74, 54))
        circ(L, 452 + 100 * abierta, 500, 5, fill=(200, 180, 120))
    else:
        poly(L, [(540, 360), (560, 340), (560, 660), (540, 640)], (96, 74, 54))
    k_suelo = eio(prog(t, t_suelo, 0.7))
    if k_suelo <= 0:
        pose = "sentado"
        px, py = vx, 555
    elif k_suelo < 0.5:
        pose = pose_mix("sentado", "agachado", k_suelo * 2)
        px, py = vx + 20 * k_suelo * 2, lerp(555, 568, k_suelo * 2)
    else:
        pose = pose_mix("agachado", "suelo", (k_suelo - 0.5) * 2)
        px, py = lerp(220, 150, (k_suelo - 0.5) * 2), lerp(568, 620, (k_suelo - 0.5) * 2)
    silla(L, vx, 555)
    if t >= t_puerta:
        # entra la policía
        for j, (x0, x1) in enumerate([(600, 400), (640, 470)]):
            q = eo3(prog(t, t_puerta + 0.3 + j * 0.25, 0.6))
            if q > 0:
                persona(L, lerp(x0, x1, q), 450, "apunta", 1.0, flip=False, tipo="policia")
                st["luces"].append((lerp(x0, x1, q) - 104, 322, -1))
    persona(L, px, py, pose, 1.0, ojos=1.6 if t > t_puerta else 1)
    if t > t_puerta:
        st["sirena"] = 0.55 + 0.45 * math.sin(t * 16)
    st["flash"] = (1 - prog(t, t_puerta, 0.35)) if t > t_puerta else 0
    st["shake"] = 10 * math.exp(-(t - t_puerta) * 7) if t > t_puerta else 0
    st["paso"] = (5, "EL RESCATE")
    for j, (pal, txt) in enumerate([("suelo", "AL SUELO"), ("vista", "MANOS A LA VISTA"), ("corras", "NO CORRAS")]):
        q = prog(t, wt(e, pal) - 0.15, 0.3)
        if q > 0:
            st["overlay"].append(("check", txt, 300 + j * 52, q))
    # tensión: zoom lento antes del rescate
    st["zoom"] = 1.2 + 0.15 * eio(prog(t, 0, t_puerta)) * (1 - prog(t, t_puerta, 0.2))
    st["foco"] = (300, 480)


def esc_final(L, e, t, D, T, st):
    st["sin_luz"] = True
    rect(L, 0, 0, W, H, (14, 14, 18))
    q = prog(t, 0.05, 0.5)
    # icono de guardar (marcador)
    s = eob(prog(t, wt(e, "Guarda") - 0.1, 0.5))
    lleno = prog(t, wt(e, "vídeo") - 0.1, 0.3)
    cx, cy = 270, 430
    w, h = 70 * s, 92 * s
    pts = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx, cy + h / 2 - 26 * s),
           (cx - w / 2, cy + h / 2)]
    poly(L, pts, mezcla((70, 70, 80), AMARILLO, lleno), a=q)
    if lleno > 0:
        for j in range(10):
            ang = j / 10 * 6.283
            rr = 70 + 70 * eo3(lleno)
            circ(L, cx + rr * math.cos(ang), cy + rr * math.sin(ang), 5 * (1 - lleno) + 1, fill=AMARILLO, a=1 - lleno)
    st["paso"] = None


FUNCS = {"gancho": esc_gancho, "calma": esc_calma, "observa": esc_observa, "humaniza": esc_humaniza,
         "fuerzas": esc_fuerzas, "rescate": esc_rescate, "final": esc_final}


# ------------------------------------------------------------------ overlays (sin iluminación)
def overlays(O, st, T):
    for it in st["overlay"]:
        tipo = it[0]
        if tipo == "monitor":
            _, t, e = it
            q = prog(t, 0.2, 0.4)
            rect(O, 300, 330, 510, 440, (10, 16, 14), a=0.85 * q, r=12, outline=(60, 90, 70), w=1.5)
            bpm = int(lerp(142, 78, eio(prog(t, wt(e, "respira"), 3.5))))
            col = mezcla(ROJO, VERDE, prog(t, wt(e, "respira") + 1.5, 2))
            pts = []
            for i in range(120):
                x = 310 + i * 1.6
                ph = (i / 120 * 3 + t * bpm / 60) % 1
                y = 400 - (34 if 0.1 < ph < 0.14 else -10 if 0.14 < ph < 0.17 else 0) - 4 * math.sin(ph * 6.28)
                pts.append((x, y))
            linea(O, pts, col, w=2.2, a=q)
            texto(O, f"{bpm}", 412, 352, 26, col, a=q, fuente="black", sombra=False)
            texto(O, "BPM", 455, 356, 12, col, a=q, fuente="bold", sombra=False)
            texto(O, "♥", 330, 352, 20, col, a=q * (0.6 + 0.4 * math.sin(t * bpm / 60 * 6.28)), fuente="mono",
                  sombra=False)
        elif tipo == "chip":
            _, txt, x, y, q = it
            w = ancho(txt, 20, "sym") + 30
            rect(O, x, y - 20, x + w, y + 20, (0, 0, 0), a=0.6 * q, r=20, outline=AMARILLO, w=1.5)
            texto(O, txt, x + 15, y, 20, BLANCO, a=q, fuente="sym", anchor="lm", sombra=False)
        elif tipo == "bocadillo":
            _, txt, x, y, q = it
            if q <= 0:
                continue
            w = ancho(txt, 20, "bold") + 32
            rect(O, x - w / 2, y - 24, x + w / 2, y + 24, BLANCO, a=q, r=18)
            poly(O, [(x - 10, y + 22), (x + 10, y + 22), (x + 2, y + 40)], BLANCO, a=q)
            texto(O, txt, x, y, 20, (30, 30, 30), a=q, fuente="bold", sombra=False)
        elif tipo == "foto":
            _, x, y, q = it
            if q <= 0:
                continue
            sc = eob(q)
            rect(O, x - 52 * sc, y - 40 * sc, x + 52 * sc, y + 40 * sc, BLANCO, a=q, r=6)
            rect(O, x - 44 * sc, y - 32 * sc, x + 44 * sc, y + 24 * sc, (140, 190, 220), a=q)
            for j, (dx, rr, col) in enumerate([(-22, 10, NARANJA), (0, 12, (200, 90, 140)), (22, 7, (90, 170, 90))]):
                circ(O, x + dx * sc, y - 8 * sc, rr * .7 * sc, fill=PIEL, a=q)
                rect(O, x + (dx - rr * .8) * sc, y + (rr * .2) * sc, x + (dx + rr * .8) * sc, y + 24 * sc, col, a=q, r=4)
            texto(O, "♥", x + 44 * sc, y - 40 * sc, 22 * sc, ROJO, a=q, fuente="mono", sombra=False)
        elif tipo == "corazon":
            _, x, y, q = it
            texto(O, "?", x, y, 34, BLANCO, a=q * (1 - q) * 3, fuente="black")
        elif tipo == "bateria":
            _, nivel, alerta, t = it
            x, y = 370, 330
            rect(O, x, y, x + 120, y + 52, (0, 0, 0), a=0.55, r=10, outline=BLANCO, w=2.5)
            rect(O, x + 120, y + 16, x + 128, y + 36, BLANCO, r=2)
            col = mezcla(ROJO, VERDE, nivel)
            rect(O, x + 6, y + 6, x + 6 + 108 * (0.12 + 0.88 * nivel), y + 46, col, r=6)
            texto(O, f"{int(12 + 88 * nivel)} %", x + 60, y + 78, 20, BLANCO, fuente="black")
            if alerta:
                texto(O, "✕ discutir", 120, 330, 22, ROJO, a=0.6 + 0.4 * math.sin(t * 10), fuente="sym")
        elif tipo == "zzz":
            _, x, y, dt = it
            for j in range(3):
                u = (dt * 0.6 + j / 3) % 1
                texto(O, "z", x + 30 * u + j * 6, y - 60 * u, 16 + 12 * u, BLANCO, a=math.sin(u * math.pi), fuente="black")
        elif tipo == "check":
            _, txt, y, q = it
            s = eob(q)
            x = 120
            circ(O, x, y, 18 * s, fill=VERDE, a=q)
            linea(O, [(x - 8, y), (x - 2, y + 7), (x + 9, y - 7)], BLANCO, w=3.5, a=q)
            texto(O, txt, x + 32, y, 26 * (0.6 + 0.4 * s), BLANCO, a=q, fuente="black", anchor="lm")
        elif tipo == "icono_pregunta":
            _, q = it
            texto(O, "?", 410, 190 + 20 * (1 - eo3(q)), 70, ROJO, a=q, fuente="black")


def paso(O, st, t):
    if not st.get("paso"):
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


def render_frame(fr):
    global ROOM
    if ROOM is None:
        ROOM = habitacion_base()
    T = fr / FPS
    e = escena_en(T)
    t = T - e["t0"]
    D = e["dur"]
    img = ROOM.copy()
    L = Capa(img)
    st = {"overlay": [], "luces": [], "sirena": 0, "flash": 0, "shake": 0, "zoom": 1.0, "foco": (270, 480),
          "bombilla": bombilla_pos(T, amp=12 if e["nombre"] == "rescate" and t > 2 else 7)}
    # zoom lento por defecto (sensación de cámara)
    FUNCS[e["nombre"]](L, e, t, D, T, st)
    if st["zoom"] == 1.0 and e["nombre"] not in ("observa", "final"):
        st["zoom"] = 1.22 + 0.06 * eio(t / D)
        st["foco"] = (285, 480)
    if not st.get("sin_luz"):
        bx, by = st["bombilla"]
        extra = None
        if st["sirena"]:
            sw, sh = IW // 12, IH // 12
            s = st["sirena"]
            rojo = (math.sin(T * 14) > 0)
            c = np.array([0.9, 0.12, 0.12] if rojo else [0.15, 0.3, 1.0], np.float32) * s * 0.55
            extra = np.ones((sh, sw, 3), np.float32) * c
        lm = luz(T, extra, bx=bx, by=by, potencia=0.9 if e["nombre"] != "rescate" else 0.75)
        img = ImageChops.multiply(img, lm)
        L = Capa(img)
        dibujar_bombilla(L, bx, by)
        # halo de la bombilla
        halo = Image.new("L", (IW // 8, IH // 8), 0)
        hd = ImageDraw.Draw(halo)
        hx, hy, hr = bx * K / 8, by * K / 8, 26 * K / 8
        hd.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=200)
        halo = halo.filter(ImageFilter.GaussianBlur(10)).resize((IW, IH), Image.BILINEAR)
        img = ImageChops.add(img, Image.merge("RGB", (halo, halo.point(lambda v: v * .9), halo.point(lambda v: v * .7))))
        # linternas
        if st["luces"]:
            haz = Image.new("L", (IW // 4, IH // 4), 0)
            hd = ImageDraw.Draw(haz)
            for (lx, ly, dirx) in st["luces"]:
                k4 = K / 4
                hd.polygon([(lx * k4, ly * k4), ((lx - 420) * k4, (ly + 150) * k4), ((lx - 420) * k4, (ly + 330) * k4)],
                           fill=90)
            haz = haz.filter(ImageFilter.GaussianBlur(6)).resize((IW, IH), Image.BILINEAR)
            img = ImageChops.add(img, Image.merge("RGB", (haz, haz, haz.point(lambda v: v * .85))))
    # cámara: zoom + temblor
    z = st["zoom"]
    sh = st["shake"]
    if z != 1.0 or sh:
        fx, fy = st["foco"]
        cw, ch = IW / z, IH / z
        x0 = cl(fx * K - cw / 2, 0, IW - cw) + sh * K * math.sin(T * 90)
        y0 = cl(fy * K - ch / 2, 0, IH - ch) + sh * K * math.cos(T * 70)
        img = img.transform((IW, IH), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    # viñeta
    img = ImageChops.multiply(img, VINETA())
    if st["flash"]:
        img = Image.blend(img, Image.new("RGB", (IW, IH), (255, 255, 255)), st["flash"])
    # overlays
    O = Capa(img)
    overlays(O, st, T)
    paso(O, st, t)
    subtitulos(O, T)
    if e["nombre"] == "final":
        q = prog(t, wt(e, "Ojalá") - 0.1, 0.5)
        texto(O, "Ojalá nunca", 270, 600, 40, BLANCO, a=q)
        texto(O, "lo necesites.", 270, 648, 40, BLANCO, a=q)
        q2 = prog(t, wt(e, "necesites") + 0.5, 0.5)
        texto(O, "Comparte con quien quieras proteger", 270, 720, 17, (200, 200, 200), a=q2, fuente="semi", sombra=False)
    # fundido de entrada/salida
    if T < 0.25:
        img = Image.blend(Image.new("RGB", (IW, IH), (0, 0, 0)), img, T / 0.25)
    if T > TOTAL - 0.6:
        img = Image.blend(img, Image.new("RGB", (IW, IH), (0, 0, 0)), cl((T - (TOTAL - 0.6)) / 0.6))
    return img.resize((OW, OH), Image.LANCZOS).tobytes()


_VIN = None


def VINETA():
    global _VIN
    if _VIN is None:
        sw, sh = IW // 8, IH // 8
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        r = np.sqrt(((xx - sw / 2) / sw) ** 2 + ((yy - sh / 2) / sh) ** 2 * 0.8)
        v = np.clip(1.15 - r * 1.1, 0.35, 1)
        _VIN = Image.fromarray((v * 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR).convert("RGB")
    return _VIN


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


def musica(n):
    tt = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    # dron grave inquietante (La menor, con segunda menor que roza)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.08 * tt)
    for f, g in ((55, 0.12), (82.4, 0.06), (110, 0.04), (116.5, 0.018)):
        out += g * np.sin(2 * np.pi * f * tt + 0.3 * np.sin(2 * np.pi * 0.13 * tt)) * lfo
    # pulso tipo "tic-tac" de tensión
    beat = 60 / 84
    k = 0
    while k * beat < TOTAL:
        t0 = k * beat
        a0 = int(t0 * SR)
        m = min(n - a0, int(0.08 * SR))
        if m > 0:
            u = np.arange(m) / SR
            out[a0:a0 + m] += 0.05 * np.sin(2 * np.pi * (1800 if k % 2 else 1400) * u) * np.exp(-u * 70)
        k += 1
    # notas de piano tristes
    notas = [69, 72, 76, 74, 69, 72, 71, 67]
    paso = beat * 4
    k = 0
    while k * paso < TOTAL:
        t0 = k * paso + 0.2
        a0 = int(t0 * SR)
        m = min(n - a0, int(2.4 * SR))
        if m > 0:
            u = np.arange(m) / SR
            f = 440 * 2 ** ((notas[k % len(notas)] - 69) / 12)
            out[a0:a0 + m] += 0.045 * (np.sin(2 * np.pi * f * u) + 0.3 * np.sin(4 * np.pi * f * u)) * np.exp(-u * 1.6)
        k += 1
    return out


def mezclar():
    n = int((TOTAL + 0.3) * SR)
    voz = np.zeros(n, np.float32)
    for e in ESC:
        colocar(voz, leer(os.path.join(BUILD, f"voz_{e['i']}.mp3")), e["voz_t0"])
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    mus = musica(n)
    fx = np.zeros(n, np.float32)
    # latidos en el gancho y en la calma
    g = ESC[0]
    k = 0
    while k * 0.62 < g["dur"] + ESC[1]["dur"]:
        tt = k * (0.62 if k * 0.62 < g["dur"] else 0.62 + 0.04 * (k - g["dur"] / 0.62))
        colocar(fx, latido(), tt, 0.5)
        k += 1
    for j, e in enumerate(ESC[1:]):
        colocar(fx, whoosh(j), e["t0"] - 0.25, 0.35)
    r = next(e for e in ESC if e["nombre"] == "rescate")
    tp = r["t0"] + wt(r, "rescate") - 0.05
    # silencio dramático antes de la puerta
    a0, a1 = int((tp - 1.0) * SR), int(tp * SR)
    mus[a0:a1] *= np.linspace(1, 0.15, a1 - a0)
    colocar(fx, golpe(), tp, 0.9)
    colocar(fx, sirena(r["dur"] - (tp - r["t0"])), tp + 0.2, 0.12)
    colocar(fx, golpe() * 0.4, ESC[0]["t0"] + 0.05, 0.6)
    # ducking
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
