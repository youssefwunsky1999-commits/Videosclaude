"""Paso 2: renderiza las animaciones fotograma a fotograma, sintetiza la música
y lo monta todo con ffmpeg.

    python3 voz.py && python3 video.py   ->  claude_gratis.mp4
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
SALIDA = os.path.join(AQUI, "claude_gratis.mp4")

W, H = 1280, 720          # unidades de diseño
K = 2                     # supermuestreo interno (antialiasing)
IW, IH = W * K, H * K
OW, OH = 1920, 1080       # resolución final
FPS = 30
SR = 44100

VOZ_OFF = 0.35            # retardo de la voz dentro de cada escena
COLA = 0.75               # aire tras cada frase
LEAD = 0.6                # silencio inicial

# Paleta
# Paleta clara inspirada en la marca de Anthropic (crema + arcilla + tinta)
NARANJA = (217, 119, 87)      # arcilla
NARANJA2 = (196, 98, 66)      # arcilla oscura (texto sobre crema)
CREMA = (25, 25, 23)          # tinta: color principal del texto
GRIS = (120, 117, 108)
FONDO = (250, 249, 245)       # texto claro sobre botones
PAPEL = (240, 238, 230)       # fondo del vídeo
BLANCO = (255, 255, 252)
LINEA = (214, 209, 196)
AZUL = (106, 155, 204)
VERDE = (120, 140, 93)
AMARILLO = (212, 162, 127)

SERIF = os.path.join(AQUI, "fuentes", "SourceSerif4.ttf")
FUENTES = {
    "black": SERIF,
    "bold": SERIF,
    "semi": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "reg": "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "monob": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "sym": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}


@lru_cache(maxsize=512)
def F(nombre, px):
    f = ImageFont.truetype(FUENTES[nombre], max(1, int(px)))
    if FUENTES[nombre] == SERIF:
        f.set_variation_by_name("SemiBold" if nombre == "black" else "Medium")
    return f


# ---------------------------------------------------------------- easing
def cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, dur):
    return cl((t - t0) / dur) if dur > 0 else float(t >= t0)


def eo3(x):
    x = cl(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = cl(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eob(x, s=1.9):
    x = cl(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def mezcla(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- timeline
with open(os.path.join(BUILD, "palabras.json")) as f:
    DATOS = json.load(f)


def duracion_mp3(p):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", p])
    return float(out)


ESCENAS = []
_t = LEAD
for i, seg in enumerate(DATOS):
    dv = duracion_mp3(os.path.join(BUILD, f"voz_{i}.mp3"))
    dur = VOZ_OFF + dv + COLA
    if i == len(DATOS) - 1:
        dur += 2.2
    if i == 0:
        dur += 0.4
    ESCENAS.append({"i": i, "nombre": seg["escena"], "t0": _t, "dur": dur, "voz": dv,
                    "palabras": seg["palabras"], "texto": seg["texto"]})
    _t += dur
ESCENAS[0]["t0"] = 0.0
ESCENAS[0]["dur"] += LEAD
ESCENAS[0]["voz_t0"] = LEAD + VOZ_OFF + 0.4
for e in ESCENAS[1:]:
    e["voz_t0"] = e["t0"] + VOZ_OFF
TOTAL = _t
NFRAMES = int(TOTAL * FPS)


def wt(escena, palabra, n=0):
    """Instante (relativo a la escena) en que se pronuncia `palabra`."""
    vistos = 0
    for w in escena["palabras"]:
        if w["w"].lower().startswith(palabra.lower()):
            if vistos == n:
                return escena["voz_t0"] - escena["t0"] + w["t"]
            vistos += 1
    raise KeyError(palabra)


# ---------------------------------------------------------------- subtítulos
def construir_subtitulos():
    bloques = []
    for e in ESCENAS:
        toks = e["texto"].split()
        ws = e["palabras"]
        if len(toks) != len(ws):
            toks = [w["w"] for w in ws]
        items = []
        j = 0
        while j < len(toks):
            if toks[j].lower() == "claude" and j + 2 < len(toks) and toks[j + 1] == "punto":
                items.append(["claude.ai" + toks[j + 2][2:], ws[j]["t"], ws[j + 2]["t"] + ws[j + 2]["d"]])
                j += 3
                continue
            items.append([toks[j], ws[j]["t"], ws[j]["t"] + ws[j]["d"]])
            j += 1
        for it in items:
            it[1] += e["voz_t0"]
            it[2] += e["voz_t0"]
        chunk = []
        for it in items:
            chunk.append(it)
            largo = sum(len(c[0]) + 1 for c in chunk)
            if it[0][-1] in ".:?!" or largo > 34:
                bloques.append(chunk)
                chunk = []
        if chunk:
            bloques.append(chunk)
    # cada bloque se muestra hasta que empieza el siguiente (o un poco después de acabar)
    res = []
    for k, b in enumerate(bloques):
        ini = b[0][1] - 0.08
        fin = b[-1][2] + 0.5
        if k + 1 < len(bloques):
            fin = min(fin + 0.3, bloques[k + 1][0][1] - 0.08)
        res.append((ini, fin, b))
    return res


SUBS = construir_subtitulos()


# ---------------------------------------------------------------- lienzo
class Lienzo:
    def __init__(self, fondo):
        self.bg = fondo
        self.fx = Image.new("RGBA", (IW, IH), (0, 0, 0, 0))     # capa con brillo
        self.top = Image.new("RGBA", (IW, IH), (0, 0, 0, 0))    # capa nítida
        self.dfx = ImageDraw.Draw(self.fx, "RGBA")
        self.dtop = ImageDraw.Draw(self.top, "RGBA")
        self.A = 1.0
        self.shake = (0, 0)

    def d(self, glow):
        return self.dfx if glow else self.dtop

    def c(self, color, a=1.0):
        return tuple(color[:3]) + (int(255 * cl(a * self.A)),)


def P(*v):
    return [x * K for x in v]


def texto(L, s, x, y, size, color=CREMA, a=1.0, fuente="bold", anchor="mm", glow=False):
    if a * L.A <= 0.003:
        return
    L.d(glow).text((x * K, y * K), s, font=F(fuente, size * K), fill=L.c(color, a), anchor=anchor)


def ancho(s, size, fuente="bold"):
    return F(fuente, size * K).getlength(s) / K


def rrect(L, x0, y0, x1, y1, r, fill=None, outline=None, w=2, a=1.0, glow=False):
    L.d(glow).rounded_rectangle(P(x0, y0, x1, y1), radius=r * K,
                                fill=L.c(fill, a) if fill else None,
                                outline=L.c(outline, a) if outline else None, width=int(w * K))


def circulo(L, x, y, r, fill=None, outline=None, w=2, a=1.0, glow=False):
    if r <= 0:
        return
    L.d(glow).ellipse(P(x - r, y - r, x + r, y + r), fill=L.c(fill, a) if fill else None,
                      outline=L.c(outline, a) if outline else None, width=int(w * K))


def linea(L, pts, color, w=2, a=1.0, glow=False):
    L.d(glow).line([(x * K, y * K) for x, y in pts], fill=L.c(color, a), width=max(1, int(w * K)),
                   joint="curve")


def logo(L, cx, cy, R, rot, a=1.0, glow=True, color=NARANJA):
    """Destello de Claude: rayos irregulares alrededor de un núcleo."""
    if R <= 0.5:
        return
    largos = [1.0, .80, .93, .74, 1.0, .84, .95, .76, .98, .82, .90, .78]
    n = len(largos)
    d = L.d(glow)
    for i in range(n):
        ang = math.radians(rot + i * 360 / n)
        ca, sa = math.cos(ang), math.sin(ang)
        px, py = -sa, ca
        Lr = R * largos[i]
        w = R * 0.085
        bx, by = cx + ca * R * 0.1, cy + sa * R * 0.1
        tx, ty = cx + ca * Lr, cy + sa * Lr
        pts = [(bx + px * w, by + py * w), (tx + px * w * .5, ty + py * w * .5),
               (tx - px * w * .5, ty - py * w * .5), (bx - px * w, by - py * w)]
        d.polygon([(x * K, y * K) for x, y in pts], fill=L.c(color, a))
        circulo(L, tx, ty, w * .5, fill=color, a=a, glow=glow)
    circulo(L, cx, cy, R * .17, fill=color, a=a, glow=glow)


# ---------------------------------------------------------------- fondo
def _fondo_base():
    y, x = np.mgrid[0:IH, 0:IW].astype(np.float32)
    nx, ny = (x - IW / 2) / IW, (y - IH / 2) / IH
    r = np.sqrt(nx ** 2 * 1.2 + ny ** 2)
    v = np.clip(1 - r * 1.25, 0, 1) ** 1.6
    base = np.array(PAPEL, np.float32)
    img = base[None, None, :] * (0.95 + 0.05 * v[..., None])
    return np.clip(img, 0, 255).astype(np.uint8)


FONDO_BASE = None
SW, SH = IW // 16, IH // 16
_yy, _xx = np.mgrid[0:SH, 0:SW].astype(np.float32)

rnd = random.Random(7)
POLVO = [(rnd.random() * W, rnd.random() * H, rnd.uniform(.6, 2.2), rnd.uniform(4, 22), rnd.random() * 6.28)
         for _ in range(80)]


def fondo(T, tinte=NARANJA, intensidad=1.0):
    global FONDO_BASE
    if FONDO_BASE is None:
        FONDO_BASE = _fondo_base()
    # manchas de luz que flotan
    acc = np.zeros((SH, SW, 3), np.float32)
    for k, (fx, fy, fase, col, rad) in enumerate([(0.13, 0.17, 0, (30, 70, 90), .30), (0.09, 0.11, 2, (40, 30, 10), .34)]):
        cx = SW * (0.5 + 0.38 * math.sin(T * fx + fase))
        cy = SH * (0.5 + 0.35 * math.cos(T * fy * 1.3 + fase))
        g = np.exp(-(((_xx - cx) / (SW * rad)) ** 2 + ((_yy - cy) / (SW * rad)) ** 2))
        acc += g[..., None] * np.array(col, np.float32)[None, None, :] * 0.18 * intensidad
    manchas = Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR)
    img = ImageChops.subtract(Image.fromarray(FONDO_BASE), manchas)
    d = ImageDraw.Draw(img, "RGBA")
    for (x, y, r, vel, fase) in POLVO:
        yy = (y - T * vel) % (H + 20) - 10
        xx = x + 8 * math.sin(T * 0.5 + fase)
        a = 0.25 + 0.25 * math.sin(T * 2 + fase)
        d.ellipse(P(xx - r, yy - r, xx + r, yy + r), fill=(217, 119, 87, int(255 * a * 0.35)))
    return img


# ================================================================ ESCENAS
def esc_intro(L, e, t, D, T, fr):
    k = prog(t, 0.55, 0.9)
    R = 105 * eob(k)
    cy = 290 - 20 * eio(prog(t, 2.2, 1.0))
    logo(L, 640, cy, R, 30 * t + 40 * (1 - eo3(k)), glow=False)
    # onda expansiva
    for j, t0 in enumerate([0.75, 1.0]):
        q = prog(t, t0, 1.3)
        if 0 < q < 1:
            circulo(L, 640, cy, 60 + 520 * eo3(q), outline=NARANJA, w=4 * (1 - q) + 1, a=(1 - q) * .6)
    # "Claude" letra a letra
    tc = wt(e, "Claude") - 0.25
    nombre = "Claude"
    size = 96
    total = ancho(nombre, size, "black")
    x = 640 - total / 2
    for j, ch in enumerate(nombre):
        q = prog(t, tc + j * 0.06, 0.45)
        wch = ancho(ch, size, "black")
        if q > 0:
            texto(L, ch, x + wch / 2, 470 + 40 * (1 - eo3(q)), size * 1.1, CREMA, a=q, fuente="black")
        x += wch
    q = prog(t, wt(e, "inteligencia") - 0.1, 0.6)
    texto(L, "INTELIGENCIA ARTIFICIAL", 640, 560 + 10 * (1 - eo3(q)), 22, NARANJA2, a=q, fuente="semi")
    q = prog(t, wt(e, "Anthropic") - 0.1, 0.6)
    texto(L, "creada por Anthropic", 640, 598, 20, GRIS, a=q, fuente="reg")


rc = random.Random(3)
CONFETI = [(rc.uniform(0, 6.283), rc.uniform(350, 1100), rc.choice([NARANJA, CREMA, AMARILLO, NARANJA2, AZUL]),
            rc.uniform(5, 11), rc.uniform(-12, 12), rc.random()) for _ in range(170)]


def esc_gratis(L, e, t, D, T, fr):
    ti = wt(e, "gratis") - 0.12
    # previa: "¿de verdad?"
    q0 = prog(t, 0.15, 0.4)
    texto(L, "Y sí...", 640, 300, 48, GRIS, a=q0 * (1 - prog(t, ti - 0.2, 0.2)), fuente="semi")
    k = prog(t, ti, 0.32)
    if t >= ti:
        s = 1 + 2.4 * (1 - eo3(k))
        a = eo3(k)
        # temblor de cámara
        dt = t - ti - 0.32
        if dt > 0:
            amp = 14 * math.exp(-dt * 6)
            L.shake = (int(amp * math.sin(dt * 70) * K), int(amp * math.cos(dt * 53) * K))
        y = 250 - 40 * eio(prog(t, wt(e, "Entras") - 0.3, 0.7))
        texto(L, "Gratis", 640, y + 6, 190 * s, CREMA, a=a * 0.5, fuente="black", glow=True)
        texto(L, "Gratis", 640, y, 190 * s, NARANJA, a=a, fuente="black")
        # confeti
        dt = t - ti - 0.2
        if dt > 0:
            for (ang, vel, col, sz, spin, fase) in CONFETI:
                x = 640 + math.cos(ang) * vel * dt * math.exp(-dt * 0.9)
                yy = y + math.sin(ang) * vel * dt * math.exp(-dt * 0.9) + 260 * dt * dt
                al = cl(1.6 - dt * 0.55)
                if al <= 0:
                    continue
                r = math.radians(spin * 40 * dt + fase * 360)
                w2, h2 = sz, sz * 0.45 * abs(math.cos(dt * 6 + fase * 6)) + 1
                cs, sn = math.cos(r), math.sin(r)
                pts = [(x + cs * dx - sn * dy, yy + sn * dx + cs * dy) for dx, dy in
                       [(-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2)]]
                L.dtop.polygon([(px * K, py * K) for px, py in pts], fill=L.c(col, al))
        # etiqueta 0 €
        q = prog(t, ti + 0.45, 0.5)
        if q > 0:
            sc = eob(q)
            ang = -12 * sc
            cx, cy = 985, y - 95
            circulo(L, cx, cy, 62 * sc, fill=CREMA, a=q)
            texto(L, "0 €", cx, cy, 44 * sc, FONDO, a=q, fuente="black")
            _ = ang
    # barra del navegador
    tb = wt(e, "claude") - 0.2
    q = prog(t, tb, 0.7)
    if q > 0:
        y0 = 470 + 120 * (1 - eo3(q))
        x0, x1 = 330, 950
        rrect(L, x0, y0 + 4, x1, y0 + 78, 37, fill=CREMA, a=q * 0.3, glow=True)
        rrect(L, x0, y0, x1, y0 + 74, 37, fill=BLANCO, outline=LINEA, w=2, a=q)
        # candado
        rrect(L, x0 + 30, y0 + 34, x0 + 52, y0 + 52, 4, fill=VERDE, a=q)
        L.dtop.arc(P(x0 + 33, y0 + 22, x0 + 49, y0 + 42), 180, 360, fill=L.c(VERDE, q), width=3 * K)
        url = "claude.ai"
        n = int(cl((t - tb - 0.3) / 0.5) * len(url))
        texto(L, url[:n], x0 + 72, y0 + 37, 32, CREMA, a=q, fuente="semi", anchor="lm")
        if (t * 2) % 1 < .6 and n < len(url) + 1:
            cxp = x0 + 74 + ancho(url[:n], 32, "semi")
            rrect(L, cxp, y0 + 20, cxp + 3, y0 + 54, 1, fill=NARANJA, a=q)
        # botón "Empezar"
        tc = wt(e, "creas") - 0.1
        qb = prog(t, tc, 0.5)
        bx = x1 - 175
        pulso = 1 + 0.04 * math.sin(t * 8) * prog(t, tc + 0.5, 0.3)
        rrect(L, bx, y0 + 12, bx + 160 * pulso, y0 + 62, 25, fill=NARANJA, a=qb)
        texto(L, "Empezar", bx + 80 * pulso, y0 + 37, 24, FONDO, a=qb, fuente="bold")
        # clic
        tk = wt(e, "empiezas") - 0.1
        qk = prog(t, tk, 0.6)
        if 0 < qk < 1:
            circulo(L, bx + 80, y0 + 37, 20 + 70 * eo3(qk), outline=CREMA, w=3, a=1 - qk)
        if t > tc + 0.2:
            mx = bx + 80 + 120 * (1 - eio(prog(t, tc + 0.2, tk - tc - 0.2)))
            my = y0 + 40 + 80 * (1 - eio(prog(t, tc + 0.2, tk - tc - 0.2)))
            cursor(L, mx, my, qb)


def cursor(L, x, y, a=1.0):
    pts = [(x, y), (x, y + 30), (x + 8, y + 23), (x + 14, y + 36), (x + 19, y + 34), (x + 13, y + 21),
           (x + 23, y + 21)]
    L.dtop.polygon([(px * K, py * K) for px, py in pts], fill=L.c(CREMA, a), outline=L.c(FONDO, a))


def icono_check(L, x, y, s, color, a):
    linea(L, [(x - s * .45, y), (x - s * .1, y + s * .35), (x + s * .5, y - s * .35)], color, w=s * .16, a=a)


def esc_planes(L, e, t, D, T, fr):
    q = prog(t, 0.05, 0.6)
    texto(L, "CON TOTAL SINCERIDAD", 640, 120 - 10 * (1 - eo3(q)), 24, NARANJA2, a=q, fuente="semi")
    tarjetas = [
        (0.35, "Plan gratuito", "0 €", "para empezar", VERDE, "check"),
        (wt(e, "límites") - 0.15, "Límites de uso", "∞ ✗", "mensajes por periodo", AMARILLO, "reloj"),
        (wt(e, "pago") - 0.25, "Planes de pago", "+", "si necesitas más", AZUL, "mas"),
    ]
    tfin = wt(e, "empezar") - 0.2
    for j, (t0, tit, big, sub, col, ico) in enumerate(tarjetas):
        qk = prog(t, t0, 0.6)
        if qk <= 0:
            continue
        cx = 300 + j * 340
        y = 360 + 60 * (1 - eo3(qk))
        a = qk
        resalta = prog(t, tfin, 0.4) if j == 0 else 0
        atenua = 1 - 0.55 * prog(t, tfin, 0.4) if j > 0 else 1
        a *= atenua
        rrect(L, cx - 150, y - 134, cx + 150, y + 146, 28, fill=CREMA, a=a * 0.25, glow=True)
        rrect(L, cx - 150, y - 140, cx + 150, y + 140, 28, fill=BLANCO, outline=mezcla(LINEA, col, resalta),
              w=1.5 + 3 * resalta, a=a)
        if resalta:
            rrect(L, cx - 156, y - 146, cx + 156, y + 146, 32, outline=col, w=3, a=resalta * (0.5 + 0.5 * math.sin(t * 6)))
        circulo(L, cx, y - 62, 38, fill=col, a=a * 0.18)
        if ico == "check":
            icono_check(L, cx, y - 62, 40, col, a)
        elif ico == "reloj":
            circulo(L, cx, y - 62, 24, outline=col, w=4, a=a)
            ang = t * 4
            linea(L, [(cx, y - 62), (cx + 15 * math.cos(ang), y - 62 + 15 * math.sin(ang))], col, w=4, a=a)
            linea(L, [(cx, y - 62), (cx, y - 75)], col, w=4, a=a)
        else:
            linea(L, [(cx - 18, y - 62), (cx + 18, y - 62)], col, w=6, a=a)
            linea(L, [(cx, y - 80), (cx, y - 44)], col, w=6, a=a)
        texto(L, tit, cx, y + 10, 30, CREMA, a=a, fuente="bold")
        if j == 0:
            texto(L, big, cx, y + 62, 46, col, a=a, fuente="black")
        elif j == 1:
            # barra de uso que se llena
            pu = eio(prog(t, t0 + 0.3, 1.5))
            rrect(L, cx - 100, y + 52, cx + 100, y + 70, 9, fill=(222, 217, 206), a=a)
            rrect(L, cx - 100, y + 52, cx - 100 + 200 * pu * 0.86, y + 70, 9, fill=col, a=a)
        else:
            texto(L, "Pro · Max · Team", cx, y + 62, 22, col, a=a, fuente="semi")
        texto(L, sub, cx, y + 106, 19, GRIS, a=a, fuente="reg")


rr = random.Random(11)
CAPAS = [4, 6, 6, 3]
NODOS = []
for ci, n in enumerate(CAPAS):
    x = 560 + ci * 170
    NODOS.append([(x, 385 + (k - (n - 1) / 2) * 70) for k in range(n)])
ARISTAS = [(ci, a, b) for ci in range(len(CAPAS) - 1) for a in range(CAPAS[ci]) for b in range(CAPAS[ci + 1])]
PULSOS = [(rr.randrange(len(ARISTAS)), rr.random() * 3) for _ in range(40)]
FRAGMENTOS = ["hola", "def f(x):", "érase una vez", "E = mc²", "poema", "receta", "historia", "¿por qué?",
              "lenguaje", "1 + 1 = 2", "<html>", "gracias", "ciencia", "música", "λ", "datos"]


def esc_red(L, e, t, D, T, fr):
    q = prog(t, 0.05, 0.6)
    texto(L, "¿CÓMO FUNCIONO?", 640, 82, 46, CREMA, a=q, fuente="black")
    texto(L, "1 · Entrenamiento", 640, 128, 22, NARANJA2, a=prog(t, wt(e, "entrenaron") - 0.1, 0.5), fuente="semi")
    qr = prog(t, 0.4, 1.0)
    brillo = prog(t, wt(e, "patrones") - 0.2, 0.6)
    for (ci, a, b) in ARISTAS:
        (x0, y0), (x1, y1) = NODOS[ci][a], NODOS[ci + 1][b]
        aparece = prog(t, 0.4 + ci * 0.25, 0.6)
        linea(L, [(x0, y0), (x1, y1)], (160, 152, 140), w=1.2, a=0.35 * aparece * qr)
    # pulsos viajando por las conexiones
    tp = wt(e, "entrenaron") - 0.3
    if t > tp:
        for idx, fase in PULSOS:
            ci, a, b = ARISTAS[idx]
            (x0, y0), (x1, y1) = NODOS[ci][a], NODOS[ci + 1][b]
            u = ((t - tp) * (0.8 + brillo) + fase) % 1.4
            if u > 1:
                continue
            x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
            circulo(L, x, y, 4 + 2 * brillo, fill=NARANJA, a=qr * math.sin(u * math.pi))
    for ci, capa in enumerate(NODOS):
        for k, (x, y) in enumerate(capa):
            ap = eob(prog(t, 0.3 + ci * 0.2 + k * 0.04, 0.5))
            act = 0.5 + 0.5 * math.sin(t * 5 + k * 1.7 + ci)
            col = mezcla((185, 179, 168), NARANJA, cl(brillo * act + 0.15))
            circulo(L, x, y, 17 * ap, fill=BLANCO, outline=col, w=3, a=qr)
            circulo(L, x, y, 9 * ap, fill=col, a=qr)
    # fragmentos de texto que entran en la red
    for j, frag in enumerate(FRAGMENTOS):
        t0 = 0.6 + j * 0.38
        u = (t - t0) / 2.2
        if not 0 < u < 1:
            continue
        objetivo = NODOS[0][j % 4]
        y_ini = 200 + (j * 97) % 330
        x = 90 + (objetivo[0] - 120) * eio(u)
        y = y_ini + (objetivo[1] - y_ini) * eio(u)
        a = math.sin(u * math.pi) * (1 - u * 0.6)
        texto(L, frag, x, y, 22 - 8 * u, GRIS, a=a, fuente="mono")
    q = prog(t, wt(e, "patrones") - 0.1, 0.6)
    texto(L, "patrones del lenguaje", 640 + 175, 600 - 10 * (1 - eo3(q)), 26, NARANJA2, a=q, fuente="bold")


TOKENS = ["¿", "Cómo", " func", "ionas", ",", " Cla", "ude", "?"]
TOKEN_IDS = ["30", "71429", "2829", "51104", "11", "3162", "3846", "30"]
TOKEN_COLS = [NARANJA, AZUL, VERDE, AMARILLO, (200, 130, 220), NARANJA2, (110, 210, 210), AZUL]


def esc_tokens(L, e, t, D, T, fr):
    texto(L, "2 · Tokens", 640, 120, 24, NARANJA2, a=prog(t, 0.05, 0.5), fuente="semi")
    size = 60
    frase = "".join(TOKENS)
    nvis = int(cl((t - 0.3) / 1.0) * len(frase) + 0.5)
    td = wt(e, "divido") - 0.05
    sep = eio(prog(t, td, 0.9))
    gap = 26 * sep
    anchos = [ancho(s.strip() if sep > 0.5 else s, size, "bold") for s in TOKENS]
    anchos = [ancho(s, size, "bold") for s in TOKENS]
    total = sum(anchos) + gap * (len(TOKENS) - 1)
    x = 640 - total / 2
    usados = 0
    tt = wt(e, "tokens") - 0.1
    for j, (tok, w) in enumerate(zip(TOKENS, anchos)):
        vis = tok[:max(0, nvis - usados)]
        usados += len(tok)
        cx = x + w / 2
        if sep > 0:
            col = TOKEN_COLS[j]
            bob = math.sin(t * 3 + j) * 4 * sep
            rrect(L, x - 8, 320 - 40 + bob, x + w + 8, 320 + 52 + bob, 14, fill=CREMA, a=0.25 * sep, glow=True)
            rrect(L, x - 8, 320 - 46 + bob, x + w + 8, 320 + 46 + bob, 14, fill=mezcla(BLANCO, col, 0.28), a=sep)
            rrect(L, x - 8, 320 - 46 + bob, x + w + 8, 320 + 46 + bob, 14, outline=col, w=2, a=sep)
            texto(L, tok, x, 322 + bob, size, CREMA, fuente="bold", anchor="lm")
            qi = prog(t, tt + j * 0.07, 0.4)
            texto(L, TOKEN_IDS[j], cx, 400 + 12 * (1 - eo3(qi)), 20, mezcla(col, CREMA, 0.35), a=qi, fuente="mono")
        else:
            texto(L, vis, x, 322, size, CREMA, fuente="bold", anchor="lm")
        x += w + gap
    if sep == 0 and (t * 2) % 1 < .6:
        cxp = 640 - total / 2 + ancho(frase[:nvis], size, "bold") + 4
        rrect(L, cxp, 290, cxp + 4, 354, 2, fill=NARANJA)
    q = prog(t, tt, 0.6)
    rrect(L, 520, 470, 760, 530, 30, fill=BLANCO, outline=NARANJA, w=2, a=q)
    texto(L, f"{len(TOKENS)} tokens", 640, 500, 28, CREMA, a=q, fuente="bold")
    # tijera simbólica
    if 0 < prog(t, td - 0.2, 1.0) < 1:
        u = prog(t, td - 0.2, 1.0)
        xx = 640 - total / 2 - 60 + (total + 120) * eio(u)
        linea(L, [(xx, 250), (xx, 390)], NARANJA, w=3, a=math.sin(u * math.pi))


CANDIDATOS = [("azul", 0.71), ("gris", 0.13), ("infinito", 0.08), ("precioso", 0.05)]


def esc_prediccion(L, e, t, D, T, fr):
    texto(L, "3 · Predicción", 640, 110, 24, NARANJA2, a=prog(t, 0.05, 0.5), fuente="semi")
    size = 54
    base = "El cielo es"
    ts = wt(e, "probable") - 0.1
    vuela = eio(prog(t, ts + 0.3, 0.7))
    wbase = ancho(base + " ", size, "bold")
    wazul = ancho("azul", size, "bold")
    x0 = 640 - (wbase + wazul) / 2
    texto(L, base, x0, 210, size, CREMA, a=prog(t, 0.2, 0.4), fuente="bold", anchor="lm")
    if vuela < 1 and (t * 2) % 1 < .6:
        rrect(L, x0 + wbase, 182, x0 + wbase + 4, 240, 2, fill=NARANJA)
    # barras de probabilidad
    tb = wt(e, "respuesta") - 0.2
    for j, (pal, p) in enumerate(CANDIDATOS):
        q = prog(t, tb + j * 0.15, 0.6)
        if q <= 0:
            continue
        y = 330 + j * 70
        elegido = j == 0 and t > ts
        col = NARANJA if elegido else (195, 189, 177)
        texto(L, pal, 470, y, 32, CREMA if elegido else GRIS, a=q, fuente="bold", anchor="rm")
        rrect(L, 495, y - 20, 495 + 420, y + 20, 10, fill=(228, 224, 214), a=q)
        ww = 420 * p * eo3(prog(t, tb + j * 0.15 + 0.2, 0.9))
        rrect(L, 495, y - 20, 495 + max(20, ww), y + 20, 10, fill=col, a=q)
        texto(L, f"{int(p * 100 * eo3(prog(t, tb + j * .15 + .2, .9)))} %", 935, y, 26, col if elegido else GRIS,
              a=q, fuente="semi", anchor="lm")
    if t > ts + 0.3:
        x = (470 - ancho("azul", 32, "bold") / 2) + (x0 + wbase + wazul / 2 - (470 - ancho("azul", 32, "bold") / 2)) * vuela
        y = 330 + (210 - 330) * vuela
        s = 32 + (size - 32) * vuela
        texto(L, "azul", x, y, s, NARANJA, fuente="bold")
    # contexto: mensajes anteriores a la izquierda
    tc = wt(e, "contexto") - 0.3
    q = prog(t, tc, 0.6)
    if q > 0:
        for j in range(4):
            qq = prog(t, tc + j * 0.08, 0.4)
            w = [150, 110, 170, 90][j]
            x = 60 if j % 2 == 0 else 100
            rrect(L, x, 290 + j * 62, x + w, 330 + j * 62, 18, fill=NARANJA if j % 2 else (222, 217, 206), a=0.7 * qq)
        rrect(L, 40, 270, 290, 540, 22, outline=NARANJA, w=2, a=q * (0.6 + 0.4 * math.sin(t * 6)))
        texto(L, "contexto", 165, 570, 22, NARANJA2, a=q, fuente="semi")
        # flecha hacia las barras
        linea(L, [(300, 405), (360, 405)], NARANJA2, w=3, a=q)
        linea(L, [(348, 395), (360, 405), (348, 415)], NARANJA2, w=3, a=q)


def esc_herramientas(L, e, t, D, T, fr):
    texto(L, "Más que palabras: herramientas", 640, 95, 36, CREMA, a=prog(t, 0.05, 0.5), fuente="black")
    q = prog(t, 0.25, 0.6)
    x0, y0, x1, y1 = 250, 150, 1030, 560
    y0 += 30 * (1 - eo3(q))
    y1 += 30 * (1 - eo3(q))
    rrect(L, x0, y0 + 6, x1, y1 + 6, 18, fill=CREMA, a=q * 0.5, glow=True)
    rrect(L, x0, y0, x1, y1, 18, fill=(28, 28, 26), a=q)
    rrect(L, x0, y0, x1, y0 + 40, 18, fill=(44, 43, 40), a=q)
    L.dtop.rectangle(P(x0, y0 + 22, x1, y0 + 40), fill=L.c((44, 43, 40), q))
    for j, c in enumerate([(235, 95, 85), (240, 190, 80), (110, 200, 110)]):
        circulo(L, x0 + 24 + j * 22, y0 + 20, 7, fill=c, a=q)
    texto(L, "claude — terminal", 640, y0 + 20, 16, GRIS, a=q, fuente="semi")
    tw = wt(e, "Escribo") - 0.2
    tx = wt(e, "ejecuto") - 0.3
    tr = wt(e, "reviso") - 0.2
    lineas = [
        (0.7, "> crea un vídeo explicando quién soy", PAPEL, 0.9),
        (tw, "● Write   video.py", NARANJA, 0.5),
        (tw + 0.4, "  + 500 líneas de Python", (150, 200, 120), 0),
        (tx, "● Bash    python3 video.py", NARANJA, 0.5),
        (tx + 0.5, "  ✓ voz sintetizada", (150, 200, 120), 0),
        (tx + 0.8, f"  ✓ {NFRAMES} fotogramas renderizados", (150, 200, 120), 0),
        (tx + 1.1, "  ✓ música generada", (150, 200, 120), 0),
        (tr, "● Read    claude_gratis.mp4", NARANJA, 0.5),
        (tr + 0.5, "  ✓ todo correcto", (150, 200, 120), 0),
    ]
    ly = y0 + 72
    for (t0, s, col, dur) in lineas:
        if t < t0:
            break
        n = len(s) if dur == 0 else int(cl((t - t0) / dur) * len(s))
        texto(L, s[:n], x0 + 30, ly, 21, col, a=q, fuente="mono", anchor="lm")
        if n < len(s) or (t0 == lineas[-1][0] and (t * 2) % 1 < .6):
            cx = x0 + 32 + ancho(s[:n], 21, "mono")
            L.dtop.rectangle(P(cx, ly - 12, cx + 11, ly + 12), fill=L.c(PAPEL, q * 0.8))
        ly += 40
    # chips orbitando
    chips = ["Código", "Terminal", "Archivos", "Web"]
    qo = prog(t, 1.2, 0.8)
    for j, ch in enumerate(chips):
        ang = t * 0.5 + j * math.pi / 2
        cx = 640 + 520 * math.cos(ang)
        cy = 355 + 255 * math.sin(ang)
        if math.sin(ang) < -0.2 and abs(math.cos(ang)) < 0.75:
            continue
        w = ancho(ch, 20, "semi") + 36
        rrect(L, cx - w / 2, cy - 20, cx + w / 2, cy + 20, 20, fill=BLANCO, outline=NARANJA, w=2, a=qo * 0.95)
        texto(L, ch, cx, cy, 20, CREMA, a=qo, fuente="semi")


with open(os.path.abspath(__file__)) as _f:
    CODIGO = [ln.rstrip() for ln in _f if ln.strip()][:400]


def esc_meta(L, e, t, D, T, fr):
    # lluvia del código fuente real de este vídeo
    for col in range(4):
        vel = 30 + col * 9
        off = int(t * vel / 22)
        for k in range(36):
            idx = (col * 97 + k + off) % len(CODIGO)
            y = 720 + 20 - ((t * vel + k * 22) % (36 * 22))
            x = 30 + col * 320
            texto(L, CODIGO[idx][:42], x, y, 13, NARANJA if (k + col) % 9 == 0 else GRIS, a=0.22, fuente="mono",
                  anchor="lm")
    q = prog(t, 0.2, 0.6)
    texto(L, "Este vídeo", 640, 205 - 20 * (1 - eo3(q)), 64, CREMA, a=q, fuente="black")
    q2 = prog(t, wt(e, "hecho") - 0.25, 0.4)
    s = 1 + 0.6 * (1 - eo3(q2))
    texto(L, "lo he hecho yo", 640, 285, 70 * s, NARANJA, a=q2, fuente="black")
    badges = [("voz", "Voz"), ("animaciones", "Animación"), ("música", "Música")]
    for j, (pal, et) in enumerate(badges):
        qb = prog(t, wt(e, pal) - 0.2, 0.5)
        if qb <= 0:
            continue
        cx = 380 + j * 260
        cy = 445
        sc = eob(qb)
        circulo(L, cx, cy + 5, 62 * sc, fill=CREMA, a=qb * 0.25, glow=True)
        circulo(L, cx, cy, 62 * sc, fill=BLANCO, outline=NARANJA, w=2, a=qb)
        if j == 0:   # onda de voz
            for b in range(7):
                h = 8 + 20 * abs(math.sin(t * 9 + b * 1.3))
                xb = cx - 30 + b * 10
                rrect(L, xb - 3, cy - h, xb + 3, cy + h, 3, fill=NARANJA2, a=qb)
        elif j == 1:  # cuadrado que gira
            r = 26 * sc
            ang = t * 2.5
            pts = [(cx + r * math.cos(ang + m * math.pi / 2), cy + r * math.sin(ang + m * math.pi / 2)) for m in range(4)]
            L.dtop.polygon([(px * K, py * K) for px, py in pts], outline=L.c(NARANJA2, qb), width=4 * K)
            circulo(L, cx, cy, 8 * sc, fill=CREMA, a=qb)
        else:        # notas musicales
            yb = 4 * math.sin(t * 6)
            texto(L, "♪♫", cx, cy + yb, 46 * sc, NARANJA2, a=qb, fuente="sym")
        texto(L, et, cx, cy + 90, 22, CREMA, a=qb, fuente="semi")
    qc = prog(t, wt(e, "código") - 0.15, 0.35)
    if qc > 0:
        s = 1 + 1.3 * (1 - eo3(qc))
        w = 330 * s
        rrect(L, 640 - w / 2, 598 - 34 * s, 640 + w / 2, 598 + 34 * s, 16 * s, fill=NARANJA, a=qc)
        texto(L, "100 % código", 640, 596, 40 * s, FONDO, a=qc, fuente="black")
    texto(L, f"fotograma {fr:05d} / {NFRAMES:05d}", 1250, 30, 15, GRIS, a=0.8 * q, fuente="mono", anchor="rm")


def esc_outro(L, e, t, D, T, fr):
    k = prog(t, 0.1, 0.9)
    logo(L, 640, 230, 85 * eob(k), 25 * t, glow=False)
    q = prog(t, wt(e, "Pregúntame") - 0.2, 0.6)
    texto(L, "Pregúntame lo que quieras", 640, 385 + 20 * (1 - eo3(q)), 56, CREMA, a=q, fuente="black")
    q2 = prog(t, wt(e, "Soy") - 0.2, 0.6)
    pul = 1 + 0.035 * math.sin(t * 5)
    w = 290 * pul
    rrect(L, 640 - w / 2, 476, 640 + w / 2, 546, 35, fill=CREMA, a=q2 * 0.35, glow=True)
    rrect(L, 640 - w / 2, 470, 640 + w / 2, 540, 35, fill=NARANJA, a=q2)
    texto(L, "claude.ai", 640, 505, 34, FONDO, a=q2, fuente="black")
    q3 = prog(t, wt(e, "Soy") + 0.9, 0.8)
    texto(L, "Vídeo creado por Claude: guion, voz neuronal, animación y música generadas con código.",
          640, 600, 17, GRIS, a=q3, fuente="reg")
    texto(L, "El plan gratuito tiene límites de uso; hay planes de pago opcionales.", 640, 628, 15, GRIS,
          a=q3 * 0.8, fuente="reg")


FUNCS = {"intro": esc_intro, "gratis": esc_gratis, "planes": esc_planes, "red": esc_red, "tokens": esc_tokens,
         "prediccion": esc_prediccion, "herramientas": esc_herramientas, "meta": esc_meta, "outro": esc_outro}


# ---------------------------------------------------------------- composición
def subtitulos(img, T):
    for ini, fin, bloque in SUBS:
        if ini <= T < fin:
            a = cl((T - ini) / 0.12) * cl((fin - T) / 0.12)
            d = ImageDraw.Draw(img, "RGBA")
            size = 30
            f = F("semi", size * K)
            espacio = f.getlength(" ")
            ws = [f.getlength(w[0]) for w in bloque]
            total = sum(ws) + espacio * (len(ws) - 1)
            x = IW / 2 - total / 2
            y = (H - 62) * K
            d.rounded_rectangle((x - 22 * K, y - 28 * K, x + total + 22 * K, y + 26 * K), radius=16 * K,
                                fill=(255, 255, 252, int(225 * a)), outline=LINEA + (int(255 * a),), width=K)
            for (w, t0, t1), ww in zip(bloque, ws):
                if T >= t0:
                    col = NARANJA2 if T < t1 + 0.05 else CREMA
                    al = 1.0
                else:
                    col, al = CREMA, 0.4
                d.text((x, y), w, font=f, fill=col + (int(255 * a * al),), anchor="lm")
                x += ww + espacio
            break


def render_frame(fr):
    T = fr / FPS
    esc = ESCENAS[-1]
    for e in ESCENAS:
        if e["t0"] <= T < e["t0"] + e["dur"]:
            esc = e
            break
    t = T - esc["t0"]
    D = esc["dur"]
    L = Lienzo(fondo(T))
    L.A = eo3(t / 0.4) * (cl((D - t) / 0.3) if esc is not ESCENAS[-1] else 1)
    if esc is ESCENAS[0]:
        L.A = 1
    FUNCS[esc["nombre"]](L, esc, t, D, T, fr)
    # sombra suave: desenfoque del alfa de la capa fx, desplazado hacia abajo
    small = L.fx.resize((IW // 8, IH // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    al = np.asarray(small).astype(np.float32)[..., 3] / 255.0
    sombra = Image.fromarray(np.clip(al * 70, 0, 255).astype(np.uint8)).resize((IW, IH), Image.BILINEAR)
    sombra = ImageChops.offset(sombra, 0, 10 * K)
    img = ImageChops.subtract(L.bg, Image.merge("RGB", (sombra, sombra, sombra))).convert("RGBA")
    fx, top = Image.new("RGBA", (IW, IH), (0, 0, 0, 0)), L.top   # fx solo proyecta sombra
    if L.shake != (0, 0):
        fx = ImageChops.offset(fx, *L.shake)
        top = ImageChops.offset(top, *L.shake)
    img.alpha_composite(fx)
    img.alpha_composite(top)
    if esc is ESCENAS[0] and t < 0.5:
        img.alpha_composite(Image.new("RGBA", (IW, IH), PAPEL + (int(255 * (1 - t / 0.5)),)))
    if T > TOTAL - 1.0:
        img.alpha_composite(Image.new("RGBA", (IW, IH), PAPEL + (int(255 * cl((T - (TOTAL - 1.0)) / 0.9)),)))
    # transición: paneles de color que barren la pantalla en cada corte
    for e2 in ESCENAS[1:]:
        u = (T - (e2["t0"] - 0.38)) / 0.76
        if 0 < u < 1:
            dpan = ImageDraw.Draw(img, "RGBA")
            for col, retraso in [(NARANJA, 0.0), (CREMA, 0.08)]:
                v = eio(cl((u - retraso) / 0.92))
                x = -1.45 * W + 2.75 * W * v
                ap = 1.3 * W
                dpan.polygon([((x + 180) * K, 0), ((x + ap + 180) * K, 0), ((x + ap) * K, IH), (x * K, IH)],
                             fill=col + (255,))
            break
    subtitulos(img, T)
    # barra de progreso
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, IH - 4 * K, IW * T / TOTAL, IH), fill=NARANJA + (200,))
    return img.convert("RGB").resize((OW, OH), Image.LANCZOS).tobytes()


# ---------------------------------------------------------------- audio
def leer_mp3(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def nota(m):
    return 440 * 2 ** ((m - 69) / 12)


def musica(n):
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    bpm = 96
    beat = 60 / bpm
    compas = beat * 4
    acordes = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    # pad
    for i in range(int(TOTAL / (compas * 2)) + 2):
        t0 = i * compas * 2
        a0, a1 = int(t0 * SR), min(n, int((t0 + compas * 2 + 1.5) * SR))
        if a0 >= n:
            break
        tt = t[a0:a1] - t0
        env = np.clip(tt / 1.2, 0, 1) * np.clip((compas * 2 + 1.5 - tt) / 1.5, 0, 1)
        for m in acordes[i % 4]:
            for det in (-0.12, 0.12):
                f = nota(m) * 2 ** (det / 12)
                s = np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(6 * np.pi * f * tt)
                out[a0:a1] += 0.018 * s * env
        f = nota(acordes[i % 4][0] - 12)
        out[a0:a1] += 0.05 * np.sin(2 * np.pi * f * tt) * env
    # arpegio
    paso = beat / 2
    k = 0
    while k * paso < TOTAL:
        t0 = k * paso
        ac = acordes[int(t0 / (compas * 2)) % 4]
        m = ac[[0, 1, 2, 1, 0, 2, 1, 2][k % 8]] + 12
        a0 = int(t0 * SR)
        a1 = min(n, a0 + int(0.6 * SR))
        tt = t[a0:a1] - t0
        f = nota(m)
        vol = 0.022 if t0 > ESCENAS[1]["t0"] else 0.012
        out[a0:a1] += vol * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 7)
        k += 1
    # bombo y hi-hat desde "GRATIS"
    rng = np.random.default_rng(1)
    inicio = ESCENAS[1]["t0"] + wt(ESCENAS[1], "gratis")
    fin = ESCENAS[-1]["t0"] + ESCENAS[-1]["dur"] - 2.5
    b = 0
    while True:
        t0 = inicio + b * beat
        if t0 > fin:
            break
        a0 = int(t0 * SR)
        a1 = min(n, a0 + int(0.35 * SR))
        tt = t[a0:a1] - t0
        out[a0:a1] += 0.16 * np.sin(2 * np.pi * (45 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9)
        h0 = int((t0 + beat / 2) * SR)
        h1 = min(n, h0 + int(0.06 * SR))
        if h0 < n:
            ruido = rng.standard_normal(h1 - h0).astype(np.float32)
            ruido = np.diff(ruido, prepend=0)
            out[h0:h1] += 0.02 * ruido * np.exp(-np.arange(h1 - h0) / SR * 60)
        b += 1
    return out


def whoosh(dur=0.7, seed=0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32)
    y = np.zeros(n, np.float32)
    lp = 0.0
    bp = 0.0
    for i in range(n):
        u = i / n
        c = 0.02 + 0.25 * math.sin(u * math.pi)
        lp += c * (x[i] - lp)
        bp += c * (lp - bp)
        y[i] = lp - bp
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return y * env * 0.5


def impacto():
    n = int(1.2 * SR)
    tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * (35 + 80 * np.exp(-tt * 8)) * tt) * np.exp(-tt * 3.2)
    rng = np.random.default_rng(5)
    s += 0.25 * rng.standard_normal(n) * np.exp(-tt * 18)
    return (s * 0.55).astype(np.float32)


def mezclar():
    n = int((TOTAL + 0.5) * SR)
    voz = np.zeros(n, np.float32)
    for e in ESCENAS:
        v = leer_mp3(os.path.join(BUILD, f"voz_{e['i']}.mp3"))
        a0 = int(e["voz_t0"] * SR)
        voz[a0:a0 + len(v)] += v[:n - a0]
    voz *= 0.9 / (np.abs(voz).max() + 1e-6)
    mus = musica(n)
    # ducking: baja la música cuando hablo
    envv = np.convolve(np.abs(voz), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.5 * np.clip(envv * 12, 0, 1)
    duck = np.convolve(duck, np.ones(8820) / 8820, mode="same")
    fx = np.zeros(n, np.float32)
    for j, e in enumerate(ESCENAS[1:]):
        w = whoosh(0.7, j)
        a0 = max(0, int((e["t0"] - 0.3) * SR))
        fx[a0:a0 + len(w)] += w[:n - a0] * 0.6
    imp = impacto()
    a0 = int((ESCENAS[1]["t0"] + wt(ESCENAS[1], "gratis") + 0.15) * SR)
    fx[a0:a0 + len(imp)] += imp[:n - a0]
    total = voz + mus * duck * 1.1 + fx
    fade = np.clip((TOTAL - np.arange(n) / SR) / 1.5, 0, 1)
    total *= fade
    total = np.tanh(total * 1.1) * 0.92
    pcm = (total * 32767).astype(np.int16)
    ruta = os.path.join(BUILD, "mezcla.wav")
    with wave.open(ruta, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return ruta


# ---------------------------------------------------------------- main
def main():
    solo = sys.argv[1:] and sys.argv[1] == "--preview"
    if solo:
        # fotogramas sueltos para revisar
        for seg in sys.argv[2:]:
            fr = int(float(seg) * FPS)
            Image.frombytes("RGB", (OW, OH), render_frame(fr)).save(os.path.join(BUILD, f"prev_{seg}.png"))
        return
    print(f"Duración {TOTAL:.1f}s · {NFRAMES} fotogramas")
    audio = mezclar()
    print("audio listo")
    vid = os.path.join(BUILD, "video_sin_audio.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", vid],
                          stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for k, buf in enumerate(pool.imap(render_frame, range(NFRAMES), chunksize=4)):
            ff.stdin.write(buf)
            if k % 150 == 0:
                print(f"  {k}/{NFRAMES}", flush=True)
    ff.stdin.close()
    ff.wait()
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", vid, "-i", audio, "-map", "0:v", "-map", "1:a",
                           "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000",
                           "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000",
                           "-shortest", "-movflags", "+faststart", SALIDA])
    print("listo:", SALIDA)


if __name__ == "__main__":
    main()
