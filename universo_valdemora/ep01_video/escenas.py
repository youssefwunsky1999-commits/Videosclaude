# --- Valdemora · Ep. 01 «Las 3:17»: escenas (se insertan en video.py al montarlo) ---

# ------------------------------------------------------------------ fichas visuales (no cambiar entre escenas)
PIEL_A = (246, 214, 178)
LEO_L = dict(camisa=(217, 162, 59), pantalon=(30, 38, 70), zapato=(245, 245, 245), suela=(210, 40, 40),
             pelo=(70, 44, 30), peinado="flequillo", sudadera=True)
DOBLE_L = dict(LEO_L, camisa=(190, 140, 50), pelo=(60, 38, 26))          # sudadera algo húmeda y oscurecida
ABUELA_L = dict(camisa=(120, 30, 46), pantalon=(70, 70, 76), falda=(70, 70, 76), zapato=(110, 70, 40),
                suela=(80, 50, 30), pelo=(196, 196, 204), peinado="moño", gafas=(214, 176, 80), rebeca=True)
JULIAN_L = dict(camisa=(240, 240, 236), pantalon=(120, 120, 124), zapato=(30, 30, 30), suela=(20, 20, 20),
                pelo=(24, 22, 20), peinado="peinado", tirantes=(110, 70, 40))
ALUMNOS = [dict(camisa=c, pantalon=(50, 56, 80), zapato=(240, 240, 240), suela=(60, 60, 60), pelo=p, peinado="corto")
           for c, p in (((90, 130, 200), (40, 30, 24)), ((200, 80, 80), (150, 90, 40)), ((90, 170, 110), (30, 30, 30)),
                        ((230, 230, 230), (200, 150, 70)), ((150, 100, 190), (60, 40, 30)), ((240, 160, 70), (20, 20, 20)))]
CABECERA = "VALDEMORA · EP. 01"


def cara_ojos(L, ex, ey, s, tipo, mira=0.0, a=1.0):
    tinta = (26, 22, 20)
    dx = mira * 3 * s
    if tipo == "cerrados":
        linea(L, [(ex - 4 * s, ey), (ex + 4 * s, ey)], tinta, w=2 * s, a=a)
    elif tipo == "miedo":
        L.d.ellipse(P(ex - 6 * s, ey - 8 * s, ex + 6 * s, ey + 8 * s), fill=L.c(BLANCO, a))
        circ(L, ex + dx, ey, 2.4 * s, fill=tinta, a=a)
    elif tipo == "doble":
        L.d.ellipse(P(ex - 6.5 * s, ey - 9 * s, ex + 6.5 * s, ey + 9 * s), fill=L.c((4, 4, 6), a))
        circ(L, ex - 2 * s, ey - 4 * s, 1.8 * s, fill=(255, 255, 255), a=a * 0.9)
    else:
        L.d.ellipse(P(ex - 3.6 * s + dx, ey - 6 * s, ex + 3.6 * s + dx, ey + 6 * s), fill=L.c(tinta, a))
        circ(L, ex - 1 * s + dx, ey - 2.5 * s, 1.1 * s, fill=(255, 255, 255), a=a * 0.8)


def avatar(L, x, y, s, look, cara="neutral", mira=0.0, brazos=(0.08, -0.08), paso=0.0, espalda=False, luz=1.0,
           boca=0.0, frio=0.0, sonrisa=1.0, lagrima=0.0, a=1.0):
    """Personaje de bloques 3D visto de frente; (x, y) = pies. Respeta las fichas visuales."""
    def C(c):
        c = mezcla(c, (70, 90, 140), frio * 0.5)
        return tuple(int(v * luz) for v in c)
    pr = 7 * s
    lh = 60 * s
    if look.get("falda"):
        for dx in (-13 * s, 3 * s):
            cubo(L, x + dx, y - 22 * s, 10 * s, 18 * s, C(PIEL_A), pr * 0.5, a)
            cubo(L, x + dx - 2 * s, y - 6 * s, 14 * s, 7 * s, C(look["zapato"]), pr * 0.5, a)
        cubo(L, x - 28 * s, y - lh - 2 * s, 56 * s, lh - 18 * s, C(look["falda"]), pr, a)
    else:
        for k, dx in enumerate((-18 * s, 1 * s)):
            dy = paso * 7 * s * (1 if k == 0 else -1)
            cubo(L, x + dx, y - lh + dy, 17 * s, lh - 9 * s - dy, C(look["pantalon"]), pr, a)
            cubo(L, x + dx - 1 * s, y - 9 * s - dy * 0.2, 19 * s, 7 * s, C(look["zapato"]), pr * 0.6, a)
            rect(L, x + dx - 1 * s, y - 3 * s - dy * 0.2, x + dx + 18 * s, y, C(look["suela"]), a=a)
    ty = y - lh - 62 * s
    if look.get("sudadera"):
        cubo(L, x - 24 * s, ty - 8 * s, 48 * s, 16 * s, C(sombra_c(look["camisa"], 0.8)), pr, a)
    cubo(L, x - 27 * s, ty, 54 * s, 62 * s, C(look["camisa"]), pr, a)
    if look.get("sudadera") and not espalda:
        rect(L, x - 16 * s, ty + 38 * s, x + 16 * s, ty + 54 * s, C(sombra_c(look["camisa"], 0.82)), a=a, r=3 * s)
        for dx in (-6 * s, 6 * s):
            linea(L, [(x + dx, ty + 2 * s), (x + dx, ty + 18 * s)], C((240, 230, 200)), w=1.6 * s, a=a)
    if look.get("rebeca") and not espalda:
        poly(L, [(x - 10 * s, ty), (x + 10 * s, ty), (x, ty + 22 * s)], C((240, 230, 210)), a=a)
        for k in range(4):
            circ(L, x, ty + 26 * s + k * 9 * s, 1.8 * s, fill=C((230, 200, 120)), a=a)
    if look.get("tirantes"):
        for dx in (-12 * s, 12 * s):
            linea(L, [(x + dx, ty), (x + dx, ty + 62 * s)], C(look["tirantes"]), w=3 * s, a=a)
    for lado, ang in ((-1, brazos[0]), (1, brazos[1])):
        hx = x + lado * 35 * s
        hy = ty + 5 * s
        largo = 56 * s
        ca, sa = math.cos(ang), math.sin(ang)
        wv = 16 * s
        pts = [(-wv / 2, 0), (wv / 2, 0), (wv / 2, largo), (-wv / 2, largo)]
        rot = [(hx + px * ca + py * sa * lado, hy - px * sa * lado + py * ca) for px, py in pts]
        poly(L, rot, C(sombra_c(look["camisa"], 0.92)), a=a)
        mx, my = (rot[2][0] + rot[3][0]) / 2, (rot[2][1] + rot[3][1]) / 2
        rect(L, mx - 8 * s, my - 2 * s, mx + 8 * s, my + 12 * s, C(PIEL_A), a=a, r=2 * s)
    hs = 48 * s
    hx0, hy0 = x - hs / 2, ty - hs - 3 * s
    cubo(L, hx0, hy0, hs, hs, C(PIEL_A), pr, a)
    pelo = C(look["pelo"])
    est = look.get("peinado")
    if espalda:
        rect(L, hx0 - 1, hy0 - 6 * s, hx0 + hs + pr, hy0 + hs * 0.7, pelo, a=a)
    else:
        if est == "flequillo":
            rect(L, hx0 - 2, hy0 - 7 * s, hx0 + hs + pr, hy0 + 9 * s, pelo, a=a)
            for k in range(5):
                bx = hx0 + k * 10 * s
                poly(L, [(bx, hy0 + 8 * s), (bx + 12 * s, hy0 + 8 * s), (bx + 14 * s, hy0 + (13 + k * 1.5) * s)], pelo, a=a)
            rect(L, hx0 - 2, hy0, hx0 + 5 * s, hy0 + 22 * s, pelo, a=a)
        elif est == "moño":
            rect(L, hx0 - 2, hy0 - 5 * s, hx0 + hs + pr, hy0 + 8 * s, pelo, a=a)
            cubo(L, x - 11 * s, hy0 - 24 * s, 22 * s, 20 * s, pelo, pr * 0.7, a)
        elif est == "peinado":
            rect(L, hx0 - 2, hy0 - 6 * s, hx0 + hs + pr, hy0 + 7 * s, pelo, a=a)
            linea(L, [(hx0 + 14 * s, hy0 - 6 * s), (hx0 + 14 * s, hy0 + 6 * s)], C((60, 56, 52)), w=1.2 * s, a=a)
        else:
            rect(L, hx0 - 2, hy0 - 6 * s, hx0 + hs + pr, hy0 + 10 * s, pelo, a=a)
        ey = hy0 + 25 * s
        exs = (hx0 + 15 * s, hx0 + 33 * s)
        tinta = (26, 22, 20)
        for ex in exs:
            cara_ojos(L, ex, ey, s, cara if cara in ("miedo", "doble", "cerrados") else "neutral", mira, a)
        if cara == "miedo":
            for ex in exs:
                linea(L, [(ex - 5 * s, ey - 13 * s), (ex + 5 * s, ey - 15 * s)], pelo, w=2.4 * s, a=a)
        elif cara in ("seria", "triste"):
            linea(L, [(exs[0] - 5 * s, ey - 11 * s), (exs[0] + 5 * s, ey - 9 * s)], pelo, w=2.4 * s, a=a)
            linea(L, [(exs[1] - 5 * s, ey - 9 * s), (exs[1] + 5 * s, ey - 11 * s)], pelo, w=2.4 * s, a=a)
        if look.get("gafas"):
            for ex in exs:
                circ(L, ex, ey, 7.5 * s, outline=C(look["gafas"]), w=1.6 * s, a=a)
            linea(L, [(exs[0] + 7.5 * s, ey), (exs[1] - 7.5 * s, ey)], C(look["gafas"]), w=1.4 * s, a=a)
        my = hy0 + 38 * s
        if cara == "doble":
            ancho_b = 26 * s * sonrisa
            L.d.arc(P(x - ancho_b / 2, my - 10 * s, x + ancho_b / 2, my + 6 * s), 15, 165, fill=L.c(tinta, a),
                    width=max(1, int(2.8 * s * K)))
        elif cara == "miedo" or boca > 0:
            L.d.ellipse(P(x - 4 * s, my - 2 * s, x + 4 * s, my + 6 * s + 4 * s * boca), fill=L.c((70, 30, 30), a))
        elif cara == "triste":
            L.d.arc(P(x - 8 * s, my, x + 8 * s, my + 10 * s), 200, 340, fill=L.c(tinta, a), width=max(1, int(2 * s * K)))
        elif cara == "seria":
            linea(L, [(x - 7 * s, my + 2 * s), (x + 7 * s, my + 2 * s)], tinta, w=2 * s, a=a)
        else:
            L.d.arc(P(x - 8 * s, my - 6 * s, x + 8 * s, my + 4 * s), 20, 160, fill=L.c(tinta, a),
                    width=max(1, int(2 * s * K)))
        if lagrima > 0:
            ly = ey + 8 * s + 18 * s * (lagrima % 1)
            L.d.ellipse(P(exs[0] - 2 * s, ly - 3 * s, exs[0] + 2 * s, ly + 3 * s), fill=L.c((170, 210, 255), a * 0.9))
    return dict(cabeza=(x, hy0 + hs / 2), hs=hs)


# ------------------------------------------------------------------ escenarios
def cielo_noche(L, T, top=(8, 10, 22), bot=(30, 36, 60)):
    for i in range(0, H, 8):
        rect(L, 0, i, W, i + 8, mezcla(top, bot, i / H))
    rs = random.Random(4)
    for _ in range(60):
        circ(L, rs.uniform(0, W), rs.uniform(0, 560), rs.uniform(0.6, 1.6), fill=BLANCO,
             a=0.3 + 0.3 * math.sin(T * 2 + rs.random() * 6))


def montanas(L, y, col, semilla, alto=180):
    rs = random.Random(semilla)
    pts = [(-20, y)]
    for k in range(9):
        pts.append((k * 70 + rs.uniform(-20, 20), y - rs.uniform(alto * 0.4, alto)))
    pts += [(W + 20, y), (W + 20, H), (-20, H)]
    poly(L, pts, col)


def casa_piedra(L, x, y, w, h, luz_on, escala=1.0, frio=0.0):
    pared = mezcla((150, 140, 128), (60, 66, 90), 0.45 + frio * 0.3)
    cubo(L, x, y - h, w, h, pared, 10 * escala)
    poly(L, [(x - 8 * escala, y - h), (x + w / 2 + 5 * escala, y - h - h * 0.5), (x + w + 18 * escala, y - h)],
         mezcla((150, 70, 50), (40, 30, 40), 0.55))
    for k in range(2):
        wx = x + w * (0.2 + k * 0.45)
        ww = w * 0.22
        col = (255, 210, 120) if luz_on else (30, 34, 50)
        rect(L, wx, y - h * 0.75, wx + ww, y - h * 0.45, col)
        if luz_on:
            circ(L, wx + ww / 2, y - h * 0.6, ww * 1.4, fill=(255, 200, 120), a=0.08)
    rect(L, x + w * 0.42, y - h * 0.38, x + w * 0.58, y, (60, 44, 34))


def iglesia(L, x, y, s, hora=(3, 17)):
    cubo(L, x - 40 * s, y - 220 * s, 80 * s, 220 * s, (110, 106, 100), 12 * s)
    poly(L, [(x - 46 * s, y - 220 * s), (x, y - 300 * s), (x + 58 * s, y - 220 * s)], (70, 50, 44))
    cx, cy = x + 6, y - 180 * s
    circ(L, cx, cy, 22 * s, fill=(230, 226, 210))
    circ(L, cx, cy, 22 * s, outline=(40, 40, 40), w=2 * s)
    hh, mm = hora
    am = math.radians(-90 + mm * 6)
    ah = math.radians(-90 + (hh % 12) * 30 + mm * 0.5)
    linea(L, [(cx, cy), (cx + 17 * s * math.cos(am), cy + 17 * s * math.sin(am))], (20, 20, 20), w=2 * s)
    linea(L, [(cx, cy), (cx + 11 * s * math.cos(ah), cy + 11 * s * math.sin(ah))], (20, 20, 20), w=3 * s)


def farola_v(L, x, y, s=1.0, on=1.0):
    rect(L, x - 3 * s, y - 170 * s, x + 3 * s, y, (40, 40, 46))
    cubo(L, x - 12 * s, y - 190 * s, 24 * s, 20 * s, (50, 50, 56), 5 * s)
    if on > 0:
        circ(L, x, y - 180 * s, 9 * s, fill=(255, 230, 160), a=on)
        poly(L, [(x - 10 * s, y - 172 * s), (x + 10 * s, y - 172 * s), (x + 80 * s, y), (x - 80 * s, y)], (255, 220, 150),
             a=0.12 * on)


def puerta_verde(L, x, y, w, h, temblor=0.0, mirilla_brillo=0.0):
    dx = temblor
    cubo(L, x - 8, y - h - 8, w + 16, h + 8, (60, 44, 34), 10)
    cubo(L, x + dx, y - h, w, h, (34, 70, 52), 8)
    for k in range(2):
        rect(L, x + dx + 12, y - h + 20 + k * h * 0.48, x + dx + w - 12, y - h + 10 + (k + 1) * h * 0.46, (28, 60, 44), r=3)
    circ(L, x + dx + w - 22, y - h * 0.48, 6, fill=(210, 176, 90))
    circ(L, x + dx + w / 2, y - h * 0.72, 5, fill=(210, 176, 90))
    if mirilla_brillo > 0:
        circ(L, x + dx + w / 2, y - h * 0.72, 12, fill=(255, 240, 180), a=0.5 * mirilla_brillo)


def reloj_pendulo(L, x, y, s, t, hora=(3, 17), parado=False):
    cubo(L, x - 28 * s, y - 150 * s, 56 * s, 150 * s, (70, 44, 30), 8 * s)
    circ(L, x, y - 118 * s, 20 * s, fill=(236, 226, 200))
    hh, mm = hora
    for ang, ln, w_ in ((math.radians(-90 + mm * 6), 15, 2), (math.radians(-90 + (hh % 12) * 30 + mm * 0.5), 10, 3)):
        linea(L, [(x, y - 118 * s), (x + ln * s * math.cos(ang), y - 118 * s + ln * s * math.sin(ang))], (30, 30, 30),
              w=w_ * s)
    ang = 0 if parado else 0.32 * math.sin(t * 3.2)
    px, py = x + 46 * s * math.sin(ang), y - 86 * s + 46 * s * math.cos(ang)
    linea(L, [(x, y - 86 * s), (px, py)], (200, 170, 90), w=2 * s)
    circ(L, px, py, 8 * s, fill=(210, 176, 90))


def papel_pintado(L, x0, y0, x1, y1, base=(110, 40, 50), motivo=(140, 60, 66)):
    rect(L, x0, y0, x1, y1, base)
    for yy in range(int(y0) + 20, int(y1), 46):
        for xx in range(int(x0) + ((yy // 46) % 2) * 23, int(x1), 46):
            circ(L, xx, yy, 5, fill=motivo, a=0.6)


# ------------------------------------------------------------------ escenas
def esc_regla(L, e, t, D, T, st):
    ta = wt(e, "abras") - 0.1
    cielo_noche(L, T)
    circ(L, 430, 330, 34, fill=(220, 226, 240))
    circ(L, 430, 330, 90, fill=(200, 210, 240), a=0.06)
    montanas(L, 560, (24, 28, 44), 3, 200)
    montanas(L, 610, (32, 36, 56), 5, 140)
    iglesia(L, 270, 640, 1.0)
    for y, sc, n in ((660, 0.55, 9), (730, 0.75, 7), (820, 1.0, 5)):
        for j in range(n):
            x = -20 + j * (W + 40) / n + (12 if n % 2 else 0)
            apaga_en = ta + 0.15 * (x / W) * 4
            casa_piedra(L, x, y, 70 * sc, 70 * sc, luz_on=t < apaga_en, escala=sc)
    rect(L, 0, 820, W, H, (26, 26, 34))
    farola_v(L, 120, 880, 0.9, on=1.0 if t < ta + 0.8 else 0.25)
    st["niebla"] = 0.55
    st["cam"] = (1.0 + 1.1 * eio(prog(t, 0.3, D)), lerp(270, 300, eio(t / D)), lerp(480, 760, eio(t / D)))
    st["titulo_si"] = t
    st["grado"] = "frio"


def cocina(L, T, t):
    rect(L, 0, 0, W, H, (40, 30, 26))
    rect(L, 0, 300, W, 800, (120, 92, 70))
    for x in range(0, W, 54):
        linea(L, [(x, 300), (x, 800)], (110, 84, 64), w=2)
    cubo(L, 20, 380, 170, 120, (90, 60, 40), 10)
    cubo(L, 20, 600, 220, 200, (100, 68, 46), 10)
    rect(L, 20, 590, 240, 604, (180, 170, 160))
    rect(L, 320, 380, 440, 500, (30, 40, 70))
    circ(L, 400, 410, 14, fill=(220, 226, 240), a=0.8)
    linea(L, [(380, 380), (380, 500)], (70, 50, 40), w=4)
    reloj_pendulo(L, 480, 640, 1.0, t)
    for bx, by in ((300, 800), (360, 800), (330, 750)):
        cubo(L, bx, by - 50, 70, 50, (190, 150, 100), 8)
        linea(L, [(bx, by - 25), (bx + 70, by - 25)], (150, 110, 70), w=3)
    rect(L, 0, 800, W, H, (70, 50, 38))
    ang = 0.05 * math.sin(T * 1.2)
    lx = 270 + 200 * math.sin(ang)
    linea(L, [(270, 300), (lx, 400)], (30, 30, 30), w=2)
    poly(L, [(lx - 34, 430), (lx + 34, 430), (lx + 16, 400), (lx - 16, 400)], (220, 150, 60))
    circ(L, lx, 432, 10, fill=(255, 220, 150))
    circ(L, lx, 440, 160, fill=(255, 200, 120), a=0.06)
    return lx, 432


def esc_advertencia(L, e, t, D, T, st):
    cocina(L, T, t)
    tg = wt(e, "advierte") - 0.4
    agarra = eio(prog(t, tg, 0.4))
    avatar(L, 160, 900, 1.6, ABUELA_L, cara="seria" if agarra > 0.5 else "neutral", brazos=(0.08, -0.08 - 0.9 * agarra))
    avatar(L, 380, 900, 1.6, LEO_L, cara="miedo" if agarra > 0.8 else "neutral", mira=-1 if agarra > 0.5 else 0,
           brazos=(0.08 + 0.5 * agarra, -0.08))
    st["cam"] = (1.05 + 0.12 * eio(t / D), 270, 560)
    st["grado"] = "calido"


def esc_abuela1(L, e, t, D, T, st):
    tr = D * 0.62
    if t < tr:
        cocina(L, T, t)
        st["desenfoque"] = 7
        st["primer_plano"] = ("abuela", t)
        st["cam"] = (1.0 + 0.05 * eio(t / tr), 270, 480)
    else:
        rect(L, 0, 0, W, H, (40, 30, 26))
        rect(L, 0, 300, W, 900, (110, 84, 64))
        reloj_pendulo(L, 270, 900, 3.2, t)
        st["cam"] = (1.0 + 0.1 * eio((t - tr) / (D - tr)), 270, 560)
    st["grado"] = "calido"


def aula(L, T, t, pan, giro):
    rect(L, 0, 0, W, H, (190, 196, 200))
    rect(L, 0, 300, W, 760, (206, 210, 206))
    cubo(L, 60 - pan * 0.3, 360, 300, 140, (40, 70, 56), 10)
    for k in range(3):
        rect(L, 390 + k * 60 - pan * 0.3, 360, 440 + k * 60 - pan * 0.3, 520, (200, 210, 220))
    rect(L, 0, 760, W, H, (150, 120, 90))
    xv = 0
    for fila, (y, s) in enumerate(((720, 0.9), (830, 1.1))):
        for j in range(5):
            x = 60 + j * 130 - pan * (0.6 + fila * 0.4)
            vacio = fila == 1 and j == 2
            if vacio:
                xv = x
            else:
                look = ALUMNOS[(j + fila * 2) % len(ALUMNOS)]
                mira = (1.2 if x < 270 else -1.2) * giro
                avatar(L, x, y + 40 * s, 0.95 * s, look, cara="seria" if giro > 0.5 else "neutral", mira=mira)
            cubo(L, x - 44 * s, y, 88 * s, 18 * s, (170, 120, 70), 8 * s)
            rect(L, x - 38 * s, y + 18 * s, x - 32 * s, y + 70 * s, (90, 70, 50))
            rect(L, x + 32 * s, y + 18 * s, x + 38 * s, y + 70 * s, (90, 70, 50))
            if vacio:
                for k in range(5):
                    linea(L, [(x - 22 + k * 9, y + 4), (x - 16 + k * 9, y + 14)], (90, 60, 40), w=2)
    return xv


def esc_pupitre(L, e, t, D, T, st):
    tn = wt(e, "nadie") - 0.2
    pan = 180 * eio(prog(t, 0.0, tn - 0.3)) - 60
    giro = eio(prog(t, tn, 0.25))
    xv = aula(L, T, t, pan, giro)
    avatar(L, xv + 70, 930, 1.2, LEO_L, cara="miedo" if giro > 0.5 else "neutral", mira=-1)
    q = prog(t, tn + 0.3, 0.4)
    if q > 0:
        st["overlay"].append(("marco_vacio", xv, 830, q))
    st["cam"] = (1.08 + 0.1 * giro, 270, 600)
    st["grado"] = "aula"
    st["mano"] = 0.4


def pasillo(L, T, t, temblor=0.0, brillo=0.0, luz_puerta=0.0):
    rect(L, 0, 0, W, H, (10, 10, 16))
    vx, vy = 270, 520
    papel_pintado(L, 0, 0, W, H, (60, 22, 30), (80, 34, 40))
    poly(L, [(0, 0), (W, 0), (vx + 80, vy - 150), (vx - 80, vy - 150)], (30, 22, 24))
    poly(L, [(0, H), (W, H), (vx + 80, vy + 170), (vx - 80, vy + 170)], (50, 36, 28))
    for k in range(7):
        u = k / 7
        linea(L, [(lerp(0, vx - 80, u), lerp(H, vy + 170, u)), (lerp(W, vx + 80, u), lerp(H, vy + 170, u))], (40, 30, 24), w=2)
    puerta_verde(L, vx - 70, vy + 170, 140, 300, temblor=temblor, mirilla_brillo=brillo)
    if luz_puerta > 0:
        rect(L, vx - 70, vy + 166, vx + 70, vy + 172, (255, 220, 160), a=luz_puerta)
    reloj_pendulo(L, 70, 760, 1.2, t)


def esc_golpes(L, e, t, D, T, st):
    tf = 1.6
    tl = wt(e, "llamó") + 0.2
    golpes = [tl, tl + 0.75, tl + 1.5]
    g = any(0 <= t - tg < 0.18 for tg in golpes)
    if t < tf:
        rect(L, 0, 0, W, H, (6, 6, 10))
        cubo(L, 110, 420, 320, 170, (20, 20, 24), 14)
        txt = "3:16" if t < tf * 0.55 else ("3:1_" if t < tf * 0.65 else "3:17")
        texto(L, txt, 270, 505, 110, (255, 40, 40), fuente="mono", sombra=False)
        circ(L, 270, 505, 220, fill=(255, 40, 40), a=0.05)
        st["cam"] = (1.0 + 0.15 * eio(t / tf), 270, 500)
    else:
        pasillo(L, T, t, temblor=5 * math.sin(T * 90) if g else 0, brillo=1.0 if g else 0.3, luz_puerta=0.6)
        avance = eio(prog(t, tf, D - tf))
        avatar(L, 130, 990, 2.2, LEO_L, espalda=True, brazos=(0.15, -0.3), paso=math.sin(t * 5) * 0.4 * (1 - avance))
        for k, tg in enumerate(golpes):
            q = prog(t, tg, 0.12)
            if q > 0:
                st["overlay"].append(("toc", k, q * (1 - prog(t, tg + 0.6, 0.3))))
        st["cam"] = (1.05 + 0.5 * avance, 270, 560)
        st["mano"] = 1.0
        st["shake"] = 5 if g else 0
    st["grado"] = "noche"


def porche(L, T, t, acercar=0.0, sonrisa=1.0, parpadeo_farola=False):
    rect(L, 0, 0, W, H, (14, 18, 30))
    montanas(L, 600, (24, 28, 42), 8, 120)
    rect(L, 0, 600, W, H, (40, 40, 50))
    on = 0.3 if parpadeo_farola and (T * 7) % 1 < 0.25 else 1.0
    farola_v(L, 420, 820, 1.0, on=on)
    s = 2.0 + 2.2 * acercar
    avatar(L, 270, 940 + 380 * acercar, s, DOBLE_L, cara="doble", sonrisa=sonrisa, frio=0.4, luz=0.85 * on + 0.15)


def esc_mirilla(L, e, t, D, T, st):
    ts = wt(e, "sonreía") - 0.2
    porche(L, T, t, acercar=0.0, sonrisa=0.6 + 0.4 * prog(t, ts, 0.6))
    st["ojo_pez"] = True
    st["niebla"] = 0.6
    st["cam"] = (1.0 + 0.04 * math.sin(t * 1.3), 270 + 6 * math.sin(t * 0.9), 560)
    for pal in ("ropa", "cara"):
        q = prog(t, wt(e, pal) - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("igual", pal, q))
    st["grado"] = "noche"


def esc_doble1(L, e, t, D, T, st):
    if t < 0.7:
        pasillo(L, T, t, luz_puerta=0.6)
        st["desenfoque"] = 8
        st["primer_plano"] = ("leo", t)
    else:
        porche(L, T, t, acercar=eio(prog(t, 0.7, D - 0.7)), sonrisa=1.1, parpadeo_farola=True)
        st["ojo_pez"] = True
        st["niebla"] = 0.5
    st["grado"] = "noche"


def foto_1979(t, guino=False):
    """Fotografía sepia de 1979: Julián y su doble. Devuelve una imagen RGB."""
    fw, fh = 300, 380
    img = Image.new("RGB", (fw * K, fh * K), (30, 30, 30))
    F_ = Capa(img)
    rect(F_, 0, 0, fw, fh, (120, 120, 120))
    rect(F_, 0, 220, fw, fh, (90, 90, 90))
    for k in range(6):
        linea(F_, [(0, 300 + k * 14), (fw, 290 + k * 16)], (110, 110, 110), w=2)
    casa_piedra(F_, 10, 220, 80, 90, False)
    casa_piedra(F_, 200, 220, 90, 100, False)
    avatar(F_, 100, 360, 1.25, JULIAN_L, cara="neutral")
    avatar(F_, 210, 360, 1.25, JULIAN_L, cara="doble", sonrisa=1.25 if guino else 1.0)
    a = np.asarray(img).astype(np.float32)
    g = a.mean(axis=2)
    sep = np.stack([g * 1.08 + 20, g * 0.9 + 8, g * 0.68], -1)
    rs = np.random.default_rng(int(t * 24) % 50)
    sep += rs.normal(0, 10, sep.shape[:2])[..., None]
    yy, xx = np.mgrid[0:sep.shape[0], 0:sep.shape[1]]
    r = np.sqrt(((xx - sep.shape[1] / 2) / sep.shape[1]) ** 2 + ((yy - sep.shape[0] / 2) / sep.shape[0]) ** 2)
    sep *= np.clip(1.25 - r * 1.2, 0.4, 1)[..., None]
    foto = Image.fromarray(np.clip(sep, 0, 255).astype(np.uint8))
    marco = Image.new("RGB", ((fw + 24) * K, (fh + 24) * K), (236, 226, 204))
    marco.paste(foto, (12 * K, 12 * K))
    return marco


def esc_foto(L, e, t, D, T, st):
    tf = wt(e, "1979") - 0.4
    pasillo(L, T, t, luz_puerta=0.6)
    golpe_bg = (t % 1.6) < 0.12
    if t < tf:
        k = eio(prog(t, 0, 1.0))
        avatar(L, lerp(560, 330, k), 980, 2.0, ABUELA_L, cara="seria", brazos=(0.1, -0.6 * k))
        avatar(L, 150, 990, 2.0, LEO_L, cara="miedo", mira=1)
        st["cam"] = (1.05, 270, 600)
    else:
        u = eio(prog(t, tf, D - tf - 0.6))
        avatar(L, 330, 980, 2.0, ABUELA_L, cara="triste", brazos=(0.1, -1.0), lagrima=t * 0.6)
        avatar(L, 150, 990, 2.0, LEO_L, cara="miedo", mira=1)
        st["foto"] = (u, t)
        st["desenfoque"] = 3
    st["shake"] = 2 if golpe_bg else 0
    st["grado"] = "noche"


def esc_abuela2(L, e, t, D, T, st):
    pasillo(L, T, t, luz_puerta=0.6)
    st["desenfoque"] = 8
    st["primer_plano"] = ("abuela_llora", t)
    st["grado"] = "noche"
    st["cam"] = (1.0 + 0.06 * eio(t / D), 270, 500)


def habitacion(L, T, t, flex=0.0, mira=0.0, gira=0.0):
    rect(L, 0, 0, W, H, (10, 12, 22))
    rect(L, 0, 300, W, 800, (30, 34, 54))
    rect(L, 40, 360, 170, 520, (20, 26, 50))
    circ(L, 100, 410, 20, fill=(210, 220, 240))
    linea(L, [(105, 360), (105, 520)], (40, 44, 66), w=4)
    poly(L, [(40, 520), (170, 520), (300, 800), (130, 800)], (150, 170, 220), a=0.05)
    rect(L, 0, 800, W, H, (22, 20, 28))
    cubo(L, 30, 720, 200, 50, (40, 70, 140), 12)
    cubo(L, 30, 690, 60, 30, (220, 220, 230), 8)
    rect(L, 30, 770, 44, 820, (60, 44, 34))
    rect(L, 216, 770, 230, 820, (60, 44, 34))
    cubo(L, 240, 760, 60, 40, (150, 120, 80), 8)
    ax, ay, aw, ah = 320, 380, 190, 420
    cubo(L, ax, ay, aw, ah, (54, 36, 26), 16)
    for k in range(2):
        dx = flex * (3 if k == 0 else -3) * math.sin(T * 80)
        rect(L, ax + 10 + k * (aw / 2 - 5) + dx, ay + 12, ax + aw / 2 - 5 + k * (aw / 2 - 5) + dx, ay + ah - 12, (64, 44, 32))
        circ(L, ax + aw / 2 - 16 + k * 32 + dx, ay + ah / 2, 6, fill=(210, 176, 90))
    rect(L, ax + aw / 2 - 2, ay + 12, ax + aw / 2 + 2, ay + ah - 12, (6, 4, 4))
    avatar(L, 150, 800, 1.3, LEO_L, cara="miedo" if gira > 0.3 else "neutral", mira=mira, brazos=(0.4, -0.4))


def esc_silencio(L, e, t, D, T, st):
    t3 = wt(e, "tres") - 0.1
    golpes = [t3 + 0.35, t3 + 0.95, t3 + 1.55]
    flex = 1.0 if any(0 <= t - tg < 0.15 for tg in golpes) else 0.0
    gira = eio(prog(t, golpes[0], 1.6))
    habitacion(L, T, t, flex=flex, mira=1.3 * gira, gira=gira)
    z = 1.02 + 0.45 * eio(prog(t, 1.2, D - 1.2))
    st["cam"] = (z, lerp(270, 400, eio(prog(t, 1.2, D))), lerp(560, 600, eio(prog(t, 1.2, D))))
    st["shake"] = 3 * flex
    st["grado"] = "noche"


def puertas_armario(L, gap):
    for k in range(2):
        x0 = 0 if k == 0 else 270 + gap / 2
        x1 = 270 - gap / 2 if k == 0 else W
        rect(L, x0, 0, x1, H, (60, 40, 28))
        for jj in range(14):
            xx = x0 + 20 + jj * 19
            if xx < x1:
                linea(L, [(xx, 0), (xx + 4, H)], (52, 34, 24), w=2)
    circ(L, 270 - gap / 2 - 24, 520, 14, fill=(210, 176, 90))
    circ(L, 270 + gap / 2 + 24, 520, 14, fill=(210, 176, 90))


def esc_armario(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (2, 2, 4))
    puertas_armario(L, 16)
    st["cam"] = (1.0 + 0.35 * eio(t / D), 270, 520)
    st["grado"] = "noche"


def esc_doble2(L, e, t, D, T, st):
    fin = e["voz_t0"] - e["t0"] + e["palabras"][-1]["t"] + e["palabras"][-1]["d"] + 0.15
    if t < fin:
        abre = eio(prog(t, fin - 1.0, 1.0))
        gap = 16 + 26 * abre
        rect(L, 0, 0, W, H, (2, 2, 4))
        q = prog(t, 0.2, 0.25)
        if q > 0:
            hs = 150
            hx0, hy0 = 270 - hs / 2, 420
            rect(L, hx0, hy0, hx0 + hs, hy0 + hs, (34, 26, 22), a=q)
            for ex in (270 - 30, 270 + 30):
                L.d.ellipse(P(ex - 20, hy0 + 60, ex + 20, hy0 + 112), fill=L.c((2, 2, 2), q))
                circ(L, ex - 7, hy0 + 74, 5, fill=(255, 255, 255), a=q)
            ss = prog(t, 0.8, 0.8)
            if ss > 0:
                L.d.arc(P(270 - 60 * ss, hy0 + 100, 270 + 60 * ss, hy0 + 140), 15, 165, fill=L.c((120, 110, 100), ss),
                        width=int(4 * K))
        puertas_armario(L, gap)
        st["cam"] = (1.35 + 0.25 * eio(t / fin), 270, 500)
    else:
        rect(L, 0, 0, W, H, (0, 0, 0))
        st["final"] = t - fin
        st["sin_cabecera"] = True
    st["grado"] = "noche"


FUNCS = {"regla": esc_regla, "advertencia": esc_advertencia, "abuela1": esc_abuela1, "pupitre": esc_pupitre,
         "golpes": esc_golpes, "mirilla": esc_mirilla, "doble1": esc_doble1, "foto": esc_foto, "abuela2": esc_abuela2,
         "silencio": esc_silencio, "armario": esc_armario, "doble2": esc_doble2}


# ------------------------------------------------------------------ posproducción
_NIEBLA = None


def niebla(img, T, k):
    global _NIEBLA
    if _NIEBLA is None:
        rng = np.random.default_rng(3)
        n = rng.random((60, 220)).astype(np.float32)
        _NIEBLA = Image.fromarray((n * 255).astype(np.uint8)).resize((440, 120), Image.BILINEAR).filter(
            ImageFilter.GaussianBlur(6))
    off = int((T * 14) % 220)
    capa = _NIEBLA.crop((off, 0, off + 220, 120)).resize((IW, IH), Image.BILINEAR)
    capa = capa.point(lambda v: int(cl((v - 90) / 120) * 255 * k))
    gris = Image.new("RGB", (IW, IH), (150, 160, 180))
    return Image.composite(gris, img, capa)


def desenfocar(img, r):
    small = img.resize((IW // 4, IH // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r / 2))
    return small.resize((IW, IH), Image.BILINEAR)


_FISH = None


def ojo_de_pez(img):
    global _FISH
    if _FISH is None:
        yy, xx = np.mgrid[0:IH, 0:IW].astype(np.float32)
        cx, cy = IW / 2, IH * 0.52
        R = IW * 0.56
        dx, dy = (xx - cx) / R, (yy - cy) / R
        r = np.sqrt(dx * dx + dy * dy)
        f = np.where(r > 0, np.sin(np.clip(r, 0, 1.5) * 1.05) / (r + 1e-6), 1.0) * 0.92
        sx = np.clip(cx + dx * f * R, 0, IW - 1).astype(np.int32)
        sy = np.clip(cy + dy * f * R, 0, IH - 1).astype(np.int32)
        mask = np.clip((1.0 - r) * 18, 0, 1)
        _FISH = (sy, sx, mask[..., None].astype(np.float32))
    sy, sx, mask = _FISH
    a = np.asarray(img)
    return Image.fromarray((a[sy, sx].astype(np.float32) * mask).astype(np.uint8))


def grado(img, tipo):
    a = np.asarray(img).astype(np.float32)
    if tipo in ("frio", "noche"):
        a = a * np.array([0.82, 0.92, 1.12]) + np.array([0, 4, 14])
    elif tipo == "calido":
        a = a * np.array([1.08, 0.98, 0.82]) + np.array([10, 4, 0])
    elif tipo == "aula":
        g = a.mean(axis=2, keepdims=True)
        a = (a * 0.75 + g * 0.25) * np.array([0.92, 1.0, 1.04])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def primer_plano(img, tipo, t, T):
    L = Capa(img)
    if tipo == "abuela":
        avatar(L, 250, 1500, 5.2, ABUELA_L, cara="seria", brazos=(0.1, -2.3 + 0.1 * math.sin(t * 2)),
               boca=(0.5 + 0.5 * math.sin(t * 20)) if 0.2 < t < 3.5 else 0)
    elif tipo == "leo":
        avatar(L, 270, 1550, 5.6, LEO_L, cara="miedo", boca=0.6, frio=0.4)
    elif tipo == "abuela_llora":
        avatar(L, 270, 1520, 5.4, ABUELA_L, cara="triste", lagrima=t * 0.5, frio=0.3,
               boca=(0.5 + 0.5 * math.sin(t * 18)) * 0.6)
    return L.img


def post(img, st, T, e, t):
    if st.get("desenfoque"):
        img = desenfocar(img, st["desenfoque"])
    if st.get("primer_plano"):
        img = primer_plano(img, *st["primer_plano"], T)
    if st.get("foto"):
        u, tt = st["foto"]
        foto = foto_1979(tt, guino=(int(tt * 30) % 37 == 0))
        esc = lerp(0.35, 1.55, u)
        foto = foto.resize((max(1, int(foto.width * esc)), max(1, int(foto.height * esc))), Image.BILINEAR)
        rot = foto.rotate(lerp(-8, 0, u), expand=True, fillcolor=(0, 0, 0))
        cx, cy = lerp(330 * K, IW / 2, u), lerp(640 * K, IH * 0.52, u)
        m = rot.convert("L").point(lambda v: 255 if v > 3 else 0)
        img.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)), m)
    if st.get("ojo_pez"):
        img = ojo_de_pez(img)
    if st.get("niebla"):
        img = niebla(img, T, st["niebla"])
    return grado(img, st.get("grado", "noche"))
