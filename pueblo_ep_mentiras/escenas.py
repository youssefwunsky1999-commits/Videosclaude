# --- «En este pueblo, si mientes… te crece la cabeza»: escenas (se añaden tras el motor de Valdemora) ---

# ------------------------------------------------------------------ elenco fijo (no cambiar entre episodios)
NICO = dict(camisa=(120, 180, 240), pantalon=(90, 90, 100), zapato=(245, 245, 245), suela=(60, 60, 70),
            pelo=(110, 70, 40), peinado="corto", gorra=(250, 140, 50), sudadera=True)
ALCALDE = dict(camisa=(110, 60, 150), pantalon=(80, 44, 110), zapato=(30, 30, 30), suela=(20, 20, 20),
               pelo=(235, 235, 235), peinado="corto", chistera=(30, 30, 36), bigote=(235, 235, 235))
TITO = dict(camisa=(250, 210, 60), pantalon=(220, 70, 60), zapato=(250, 250, 250), suela=(220, 70, 60),
            pelo=(40, 30, 24), peinado="flequillo")
CARMEN = dict(camisa=(250, 150, 190), pantalon=(250, 150, 190), falda=(240, 120, 170), zapato=(200, 60, 100),
              suela=(150, 40, 70), pelo=(230, 120, 40), peinado="rizos")
PEPE = dict(camisa=(90, 170, 90), rayas=(250, 220, 60), pantalon=(60, 70, 110), zapato=(90, 60, 40),
            suela=(60, 40, 30), pelo=(60, 60, 60), peinado="corto", bigote=(60, 60, 60))
VECINOS_P = [dict(camisa=c, pantalon=p, zapato=(245, 245, 245), suela=(80, 80, 90), pelo=h, peinado="corto")
             for c, p, h in (((240, 120, 120), (70, 80, 120), (40, 30, 20)), ((140, 200, 160), (90, 90, 100), (150, 90, 40)),
                             ((250, 230, 150), (100, 80, 60), (30, 30, 30)), ((170, 150, 230), (60, 60, 80), (220, 190, 120)),
                             ((120, 200, 220), (70, 70, 90), (80, 50, 30)))]
ROSA = (255, 110, 170)
CABECERA = "EN ESTE PUEBLO · LA REGLA DE LAS MENTIRAS"


def avatar_p(L, x, y, s, look, cara="feliz", mira=0.0, brazos=(0.08, -0.08), paso=0.0, cabeza=1.0, boca=0.0, sudor=0.0,
             sombrero=1.0, a=1.0):
    """Personaje de bloques de frente con cabeza escalable (la que crece al mentir). (x, y) = pies."""
    pr = 7 * s
    lh = 60 * s
    if look.get("falda"):
        for dx in (-13 * s, 3 * s):
            cubo(L, x + dx, y - 22 * s, 10 * s, 18 * s, PIEL_A, pr * 0.5, a)
            cubo(L, x + dx - 2 * s, y - 6 * s, 14 * s, 7 * s, look["zapato"], pr * 0.5, a)
        cubo(L, x - 28 * s, y - lh - 2 * s, 56 * s, lh - 18 * s, look["falda"], pr, a)
    else:
        for k, dx in enumerate((-18 * s, 1 * s)):
            dy = paso * 7 * s * (1 if k == 0 else -1)
            cubo(L, x + dx, y - lh + dy, 17 * s, lh - 9 * s - dy, look["pantalon"], pr, a)
            cubo(L, x + dx - 1 * s, y - 9 * s - dy * 0.2, 19 * s, 7 * s, look["zapato"], pr * 0.6, a)
            rect(L, x + dx - 1 * s, y - 3 * s - dy * 0.2, x + dx + 18 * s, y, look["suela"], a=a)
    ty = y - lh - 62 * s
    cubo(L, x - 27 * s, ty, 54 * s, 62 * s, look["camisa"], pr, a)
    if look.get("rayas"):
        for k in range(4):
            rect(L, x - 27 * s, ty + 8 * s + k * 14 * s, x + 27 * s, ty + 14 * s + k * 14 * s, look["rayas"], a=a)
            for j in range(4):
                poly(L, [(x - 20 * s + j * 13 * s, ty + 11 * s + k * 14 * s), (x - 14 * s + j * 13 * s, ty + 6 * s + k * 14 * s),
                         (x - 8 * s + j * 13 * s, ty + 11 * s + k * 14 * s)], (220, 60, 60), a=a)
    if look.get("sudadera"):
        rect(L, x - 16 * s, ty + 38 * s, x + 16 * s, ty + 54 * s, sombra_c(look["camisa"], 0.85), a=a, r=3 * s)
    for lado, ang in ((-1, brazos[0]), (1, brazos[1])):
        hx, hy = x + lado * 35 * s, ty + 5 * s
        ca, sa = math.cos(ang), math.sin(ang)
        wv, largo = 16 * s, 56 * s
        pts = [(-wv / 2, 0), (wv / 2, 0), (wv / 2, largo), (-wv / 2, largo)]
        rot = [(hx + px * ca + py * sa * lado, hy - px * sa * lado + py * ca) for px, py in pts]
        poly(L, rot, sombra_c(look["camisa"], 0.92), a=a)
        mx, my = (rot[2][0] + rot[3][0]) / 2, (rot[2][1] + rot[3][1]) / 2
        rect(L, mx - 8 * s, my - 2 * s, mx + 8 * s, my + 12 * s, PIEL_A, a=a, r=2 * s)
    # cabeza (escala propia)
    q = s * cabeza
    hs = 48 * q
    hx0, hy0 = x - hs / 2, ty - hs - 3 * s
    cubo(L, hx0, hy0, hs, hs, PIEL_A, 7 * q, a)
    pelo = look["pelo"]
    est = look.get("peinado")
    if est == "flequillo":
        rect(L, hx0 - 2, hy0 - 7 * q, hx0 + hs + 7 * q, hy0 + 9 * q, pelo, a=a)
        for k in range(5):
            bx = hx0 + k * 10 * q
            poly(L, [(bx, hy0 + 8 * q), (bx + 12 * q, hy0 + 8 * q), (bx + 14 * q, hy0 + (13 + k * 1.5) * q)], pelo, a=a)
    elif est == "rizos":
        for k in range(7):
            circ(L, hx0 + 3 * q + k * 7 * q, hy0 + 1 * q, 9 * q, fill=pelo, a=a)
        for lado in (0, 1):
            circ(L, hx0 + lado * hs, hy0 + 16 * q, 10 * q, fill=pelo, a=a)
    else:
        rect(L, hx0 - 2, hy0 - 5 * q, hx0 + hs + 7 * q, hy0 + 8 * q, pelo, a=a)
    if look.get("gorra"):
        rect(L, hx0 - 2, hy0 - 14 * q, hx0 + hs + 7 * q, hy0 + 4 * q, look["gorra"], a=a, r=6 * q)
        rect(L, hx0 + hs * 0.4, hy0, hx0 + hs + 18 * q, hy0 + 6 * q, look["gorra"], a=a, r=2 * q)
    ey = hy0 + 25 * q
    exs = (hx0 + 15 * q, hx0 + 33 * q)
    tinta = (26, 22, 20)
    for ex in exs:
        if cara == "susto":
            L.d.ellipse(P(ex - 6 * q, ey - 8 * q, ex + 6 * q, ey + 8 * q), fill=L.c(BLANCO, a))
            circ(L, ex + mira * 3 * q, ey, 2.6 * q, fill=tinta, a=a)
        elif cara == "cerrados":
            L.d.arc(P(ex - 5 * q, ey - 3 * q, ex + 5 * q, ey + 5 * q), 200, 340, fill=L.c(tinta, a), width=max(1, int(2 * q * K)))
        else:
            L.d.ellipse(P(ex - 3.6 * q + mira * 3 * q, ey - 6 * q, ex + 3.6 * q + mira * 3 * q, ey + 6 * q), fill=L.c(tinta, a))
            circ(L, ex - 1 * q + mira * 3 * q, ey - 2.5 * q, 1.2 * q, fill=BLANCO, a=a * 0.8)
    if cara in ("feliz", "cerrados"):
        circ(L, exs[0] - 6 * q, ey + 9 * q, 4 * q, fill=(255, 150, 150), a=a * 0.5)
        circ(L, exs[1] + 6 * q, ey + 9 * q, 4 * q, fill=(255, 150, 150), a=a * 0.5)
    my = hy0 + 38 * q
    if look.get("bigote"):
        rect(L, x - 12 * q, my - 6 * q, x + 12 * q, my - 1 * q, look["bigote"], a=a, r=2 * q)
    if boca > 0 or cara == "susto":
        ab = max(boca, 0.7 if cara == "susto" else 0)
        L.d.ellipse(P(x - 5 * q, my - 1 * q, x + 5 * q, my + 4 * q + 6 * q * ab), fill=L.c((90, 30, 40), a))
    elif cara == "triste":
        L.d.arc(P(x - 8 * q, my, x + 8 * q, my + 10 * q), 200, 340, fill=L.c(tinta, a), width=max(1, int(2 * q * K)))
    else:
        L.d.arc(P(x - 9 * q, my - 7 * q, x + 9 * q, my + 4 * q), 20, 160, fill=L.c(tinta, a), width=max(1, int(2.2 * q * K)))
    if sudor > 0:
        for k in range(2):
            u = (sudor + k * 0.5) % 1
            L.d.ellipse(P(hx0 + hs - 4 * q, hy0 + 10 * q + u * 20 * q, hx0 + hs + 2 * q, hy0 + 18 * q + u * 20 * q),
                        fill=L.c((140, 200, 255), a * (1 - u)))
    if look.get("chistera") and sombrero > 0:
        c = look["chistera"]
        cubo(L, x - 36 * s, hy0 - 10 * s, 72 * s, 12 * s, c, 6 * s, a)
        cubo(L, x - 26 * s, hy0 - 96 * s, 52 * s, 88 * s, c, 8 * s, a)
        rect(L, x - 26 * s, hy0 - 26 * s, x + 26 * s, hy0 - 16 * s, (230, 190, 70), a=a)
    return dict(cabeza=(x, hy0 + hs / 2), hs=hs, top=hy0)


def chistera_suelta(L, x, y, s, ang):
    ca, sa = math.cos(ang), math.sin(ang)

    def R(px, py):
        return (x + px * ca - py * sa, y + px * sa + py * ca)
    poly(L, [R(-36 * s, 0), R(36 * s, 0), R(36 * s, 12 * s), R(-36 * s, 12 * s)], (30, 30, 36))
    poly(L, [R(-26 * s, -88 * s), R(26 * s, -88 * s), R(26 * s, 0), R(-26 * s, 0)], (30, 30, 36))
    poly(L, [R(-26 * s, -20 * s), R(26 * s, -20 * s), R(26 * s, -10 * s), R(-26 * s, -10 * s)], (230, 190, 70))


# ------------------------------------------------------------------ escenario de día
def cielo_dia(L, T):
    for i in range(0, H, 8):
        rect(L, 0, i, W, i + 8, mezcla((120, 190, 245), (215, 235, 250), i / 700))
    for j in range(4):
        cx = (j * 170 + T * 10) % (W + 220) - 110
        for k in range(3):
            cubo(L, cx + k * 34, 360 - (k % 2) * 18 + (j % 2) * 40, 46, 30, (252, 252, 255), 8, a=0.95)


def casa_pastel(L, x, y, w, h, col, tejado):
    cubo(L, x, y - h, w, h, col, 12)
    poly(L, [(x - 10, y - h), (x + w / 2 + 6, y - h - h * 0.45), (x + w + 22, y - h)], tejado)
    rect(L, x + w / 2 - 16, y - 56, x + w / 2 + 16, y, (120, 80, 60))
    for wx in (x + 12, x + w - 44):
        rect(L, wx, y - h + 28, wx + 32, y - h + 64, (170, 215, 245))
        linea(L, [(wx + 16, y - h + 28), (wx + 16, y - h + 64)], BLANCO, w=2)
        rect(L, wx - 4, y - h + 64, wx + 36, y - h + 70, (250, 250, 250))


def ayuntamiento(L, x, y):
    cubo(L, x - 120, y - 170, 240, 170, (245, 240, 228), 14)
    for k in range(5):
        cubo(L, x - 104 + k * 46, y - 150, 16, 150, (255, 252, 244), 6)
    poly(L, [(x - 132, y - 170), (x, y - 220), (x + 146, y - 170)], (220, 214, 200))
    cubo(L, x - 34, y - 330, 68, 120, (245, 240, 228), 10)
    circ(L, x + 4, y - 280, 26, fill=BLANCO)
    circ(L, x + 4, y - 280, 26, outline=(60, 60, 60), w=2)
    linea(L, [(x + 4, y - 280), (x + 4, y - 298)], (30, 30, 30), w=3)
    linea(L, [(x + 4, y - 280), (x + 18, y - 280)], (30, 30, 30), w=3)
    poly(L, [(x - 40, y - 330), (x + 4, y - 370), (x + 48, y - 330)], (200, 80, 70))
    rect(L, x - 20, y - 70, x + 28, y, (120, 80, 60))


def arbol_c(L, x, y, s=1.0):
    rect(L, x - 7 * s, y - 50 * s, x + 7 * s, y, (120, 80, 50))
    for dy, w in ((-92, 62), (-128, 46), (-156, 30)):
        cubo(L, x - w * s / 2, y + dy * s, w * s, 38 * s, (90, 180, 90), 8 * s)


def fuente(L, x, y, T):
    cubo(L, x - 70, y - 30, 140, 30, (200, 200, 210), 10)
    cubo(L, x - 12, y - 90, 24, 60, (210, 210, 220), 6)
    for k in range(6):
        u = (T * 1.5 + k / 6) % 1
        circ(L, x + (k - 2.5) * 14 * u, y - 90 - 40 * math.sin(u * math.pi), 4, fill=(150, 210, 250), a=1 - u * 0.5)


def plaza(L, T):
    cielo_dia(L, T)
    casa_pastel(L, -40, 640, 140, 140, (250, 190, 200), (200, 90, 90))
    casa_pastel(L, 440, 640, 140, 150, (190, 230, 210), (90, 120, 160))
    ayuntamiento(L, 270, 640)
    arbol_c(L, 120, 650, 0.8)
    arbol_c(L, 430, 650, 0.8)
    rect(L, 0, 640, W, H, (226, 214, 196))
    for yy in range(650, H, 34):
        for xx in range(((yy // 34) % 2) * 30 - 30, W, 60):
            rect(L, xx + 3, yy + 3, xx + 57, yy + 31, (214, 200, 180), r=6)
    fuente(L, 270, 760, T)


def calle_dia(L, T):
    cielo_dia(L, T)
    casa_pastel(L, 10, 640, 150, 150, (250, 230, 150), (200, 100, 60))
    casa_pastel(L, 200, 640, 150, 170, (200, 190, 240), (110, 80, 140))
    casa_pastel(L, 390, 640, 140, 140, (250, 190, 200), (200, 90, 90))
    rect(L, 0, 640, W, 700, (210, 210, 214))
    rect(L, 0, 700, W, H, (90, 92, 100))
    for xx in range(0, W, 90):
        rect(L, xx + 10, 820, xx + 50, 828, (250, 220, 80))


def plano(t, lista, dur=1.4):
    """Planos con corte seco cada `dur` segundos: lista de (zoom, fx, fy)."""
    k = min(int(t / dur), len(lista) - 1)
    return lista[k], k


def lineas_viento(L, T, a=1.0):
    rs = random.Random(5)
    for _ in range(14):
        y = rs.uniform(300, 760)
        x = (rs.uniform(0, W) + T * 600) % (W + 200) - 100
        linea(L, [(x, y), (x + 70, y - 6)], BLANCO, w=2, a=0.6 * a)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    plaza(L, T)
    for j, look in enumerate(VECINOS_P[:3]):
        avatar_p(L, 80 + j * 50, 880, 0.9, look, brazos=(0.1, -0.1 - 0.2 * math.sin(T * 3 + j)))
    avatar_p(L, 380, 900, 1.2, TITO, cara="feliz")
    avatar_p(L, 470, 880, 1.0, NICO, mira=-1)
    (z, fx, fy), k = plano(t, [(1.0, 270, 560), (1.9, 380, 640), (1.35, 300, 600)], dur=1.5)
    st["cam"] = (z, fx, fy)
    st["titulo"] = t


def esc_demo(L, e, t, D, T, st):
    plaza(L, T)
    # tarta y migas
    cubo(L, 200, 840, 80, 50, (250, 230, 200), 8)
    rect(L, 200, 830, 280, 842, ROSA)
    fin = e["voz_t0"] - e["t0"] + e["palabras"][-1]["t"] + e["palabras"][-1]["d"]
    crece = eob(prog(t, fin + 0.05, 0.5), 2.4)
    avatar_p(L, 380, 900, 1.2, TITO, cara="susto" if crece > 0.5 else "feliz", cabeza=1 + 1.4 * crece,
             boca=(0.5 + 0.5 * math.sin(t * 22)) if t < fin else 0)
    for k in range(5):
        circ(L, 360 + k * 9, 710 + (k % 2) * 6, 3, fill=(200, 150, 100))
    st["cam"] = (1.9, 380, 620) if t < fin else (1.3, 360, 560)
    if crece > 0:
        st["overlay"].append(("mentira", 380, 380, crece))


def esc_nadie(L, e, t, D, T, st):
    calle_dia(L, T)
    tv = wt(e, "vecina") - 0.2
    tg = wt(e, "gracias") - 0.2
    for j, look in enumerate(VECINOS_P):
        avatar_p(L, (j * 140 + T * 50) % (W + 200) - 100, 860, 0.8, look, paso=math.sin(T * 8 + j))
    avatar_p(L, 160, 930, 1.3, CARMEN, brazos=(0.1, -1.1 if tv + 1 < t < tg else -0.1), boca=(0.5 + 0.5 * math.sin(t * 20)) if tv + 1 < t < tg else 0)
    avatar_p(L, 380, 930, 1.3, PEPE, cara="cerrados" if t > tg else "feliz")
    lista = [(1.0, 270, 560), (1.15, 270, 600), (1.8, 160, 600), (1.8, 380, 600), (1.4, 270, 620), (1.8, 380, 600), (1.1, 270, 600)]
    (z, fx, fy), k = plano(t, lista, dur=1.45)
    st["cam"] = (z, fx, fy)
    if tv + 1.0 < t < tg + 0.2:
        st["overlay"].append(("bocadillo_p", "¡Te queda fatal!", 170, 420, prog(t, tv + 1.0, 0.2)))
    if t > tg:
        st["overlay"].append(("bocadillo_p", "¡Gracias, cariño!", 380, 420, prog(t, tg, 0.2)))


def esc_yo(L, e, t, D, T, st):
    ta = wt(e, "alcalde") - 0.4
    if t < ta:
        calle_dia(L, T)
        u = eio(prog(t, 0, 2.4))
        x = lerp(-60, 270, u)
        avatar_p(L, x, 930, 1.4, NICO, paso=math.sin(t * 9) if u < 1 else 0, brazos=(0.1, -0.1))
        cubo(L, x + 50, 840, 50, 40, (170, 90, 60), 6)
        (z, fx, fy), k = plano(t, [(1.1, 270, 600), (1.7, 270, 600), (1.3, 300, 620)], dur=1.6)
        st["cam"] = (z, fx, fy)
        q = prog(t, wt(e, "Nico") - 0.2, 0.3)
        if q > 0:
            st["overlay"].append(("nombre", "NICO", "el narrador", q))
    else:
        plaza(L, T)
        avatar_p(L, 270, 880, 1.3, ALCALDE)
        st["cam"] = (1.2 + 0.2 * eio(prog(t, ta, 1.0)), 270, 560)
        st["overlay"].append(("nombre", "DON RAMIRO", "el alcalde", prog(t, ta, 0.3)))


def esc_sombrero(L, e, t, D, T, st):
    td = wt(e, "dormir") - 0.4
    tg = wt(e, "agosto") - 0.4
    if t < td:
        plaza(L, T)
        avatar_p(L, 270, 880, 1.3, ALCALDE, brazos=(0.1, -0.3 * math.sin(t * 3)))
        (z, fx, fy), k = plano(t, [(1.2, 270, 520), (1.9, 270, 460), (1.4, 270, 560)], dur=1.4)
        st["cam"] = (z, fx, fy)
    elif t < tg:
        rect(L, 0, 0, W, H, (40, 50, 90))
        circ(L, 430, 380, 30, fill=(240, 240, 220))
        cubo(L, 80, 760, 380, 70, (90, 120, 200), 14)
        cubo(L, 80, 700, 110, 60, BLANCO, 10)
        avatar_p(L, 250, 900, 1.2, ALCALDE, cara="cerrados")
        cubo(L, 170, 760, 290, 90, (90, 120, 200), 14)
        st["overlay"].append(("zzz", 300, 500, t))
        st["cam"] = (1.2, 270, 620)
    else:
        rect(L, 0, 0, W, H, (255, 220, 120))
        circ(L, 440, 360, 60, fill=(255, 170, 40))
        plaza(L, T) if False else None
        rect(L, 0, 640, W, H, (240, 200, 150))
        avatar_p(L, 270, 900, 1.4, ALCALDE, sudor=t * 1.5, brazos=(0.4, -0.4))
        st["overlay"].append(("termometro", prog(t, tg, 0.3)))
        st["cam"] = (1.2, 270, 580)


def esc_viento(L, e, t, D, T, st):
    tv = wt(e, "viento") - 0.3
    plaza(L, T)
    for j, look in enumerate(VECINOS_P[:4]):
        avatar_p(L, 60 + j * 60, 900, 0.9, look)
    vuela = prog(t, tv, 1.6)
    avatar_p(L, 330, 900, 1.3, ALCALDE, sombrero=0 if vuela > 0 else 1, brazos=(0.1, -1.6 * min(1, vuela * 3)),
             cara="susto" if vuela > 0.3 else "feliz", cabeza=1.0)
    if vuela > 0:
        hx = lerp(330, 620, eo3(vuela))
        hy = lerp(560, 260, eo3(vuela)) - 60 * math.sin(vuela * math.pi)
        chistera_suelta(L, hx, hy, 1.3, vuela * 9)
        lineas_viento(L, T)
    (z, fx, fy), k = plano(t, [(1.1, 270, 600), (1.6, 330, 560), (1.15, 330, 520), (1.0, 300, 480)], dur=1.3)
    st["cam"] = (z, fx, fy)


def esc_cabeza(L, e, t, D, T, st):
    plaza(L, T)
    crece = eob(prog(t, 0.0, 0.8), 1.6)
    for j, look in enumerate(VECINOS_P[:4]):
        avatar_p(L, 60 + j * 60, 900, 0.9, look, cara="susto")
    avatar_p(L, 330, 900, 1.3, ALCALDE, sombrero=0, cabeza=1 + 2.4 * crece, cara="susto")
    lista = [(1.0, 300, 480), (1.6, 90, 680), (1.25, 330, 400), (1.8, 150, 680)]
    (z, fx, fy), k = plano(t, lista, dur=1.35)
    st["cam"] = (z, fx, fy)
    st["shake"] = 6 * math.exp(-t * 4)


def esc_like(L, e, t, D, T, st):
    plaza(L, T)
    avatar_p(L, 330, 900, 1.3, ALCALDE, sombrero=0, cabeza=3.4, cara="triste")
    st["cam"] = (1.0, 300, 480)
    st["desenfoque_p"] = 6
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    q = prog(t, wt(e, "qué") - 0.2, 0.3)
    if q > 0:
        st["overlay"].append(("grande_p", "¿SOBRE QUÉ?", 380, q, (255, 230, 60)))


def esc_pregunta(L, e, t, D, T, st):
    plaza(L, T)
    for j, look in enumerate(VECINOS_P):
        ang = math.pi * (0.15 + 0.7 * j / 4)
        avatar_p(L, 270 + 230 * math.cos(ang) * -1, 940 - 20 * math.sin(ang), 1.0, look, mira=1 if j < 2 else -1)
    avatar_p(L, 270, 880, 1.2, ALCALDE, sombrero=0, cabeza=3.4, cara="triste")
    (z, fx, fy), k = plano(t, [(1.0, 270, 520), (1.6, 100, 700), (1.6, 440, 700), (1.25, 270, 460)], dur=1.25)
    st["cam"] = (z, fx, fy)


def esc_confesion(L, e, t, D, T, st):
    tp = wt(e, "pueblo") - 0.4
    if t < tp:
        plaza(L, T)
        avatar_p(L, 270, 1100, 2.2, ALCALDE, sombrero=0, cabeza=2.2, cara="triste",
                 boca=(0.5 + 0.5 * math.sin(t * 20)) * 0.8)
        st["cam"] = (1.0, 270, 480)
        st["desenfoque_p"] = 4
    else:
        # recuerdo: hace 30 años, cartel del pueblo más feliz
        rect(L, 0, 0, W, H, (230, 210, 170))
        cubo(L, 70, 420, 400, 120, (250, 240, 210), 10)
        texto(L, "EL PUEBLO MÁS", 270, 460, 30, (140, 60, 40), fuente="black", sombra=False)
        texto(L, "FELIZ DEL MUNDO", 270, 504, 30, (140, 60, 40), fuente="black", sombra=False)
        rect(L, 120, 540, 132, 700, (120, 80, 50))
        rect(L, 408, 540, 420, 700, (120, 80, 50))
        rect(L, 0, 700, W, H, (200, 180, 140))
        avatar_p(L, 270, 920, 1.3, dict(ALCALDE, pelo=(40, 30, 24), bigote=(40, 30, 24)), sombrero=0)
        st["sepia_p"] = True
        st["overlay"].append(("hace30", prog(t, tp, 0.3)))
        st["cam"] = (1.0 + 0.08 * eio(prog(t, tp, 3)), 270, 540)


def esc_encoge(L, e, t, D, T, st):
    plaza(L, T)
    enc = eio(prog(t, 0.2, 1.0))
    for j, look in enumerate(VECINOS_P[:4]):
        avatar_p(L, 60 + j * 60, 900, 0.9, look, cara="feliz" if enc > 0.8 else "susto")
    avatar_p(L, 330, 900, 1.3, ALCALDE, sombrero=0, cabeza=lerp(3.4, 1.0, enc), cara="feliz" if enc > 0.8 else "triste")
    if 0 < enc < 1 or t < 1.6:
        st["overlay"].append(("chispas", 330, 560, t))
    (z, fx, fy), k = plano(t, [(1.0, 300, 500), (1.5, 330, 600), (1.1, 200, 640), (1.6, 90, 690)], dur=1.4)
    st["cam"] = (z, fx, fy)


def esc_vecinos(L, e, t, D, T, st):
    plaza(L, T)
    for j, look in enumerate(VECINOS_P + [CARMEN, PEPE, TITO]):
        x = 40 + j * 58
        avatar_p(L, x, 920 + (j % 2) * 20, 0.9, look, cara="cerrados", brazos=(0.3, -1.4 - 0.2 * math.sin(T * 6 + j)))
    avatar_p(L, 270, 830, 1.0, ALCALDE, sombrero=1, cara="cerrados")
    st["cam"] = (1.05, 270, 600)
    st["overlay"].append(("corazones", t))


def esc_final(L, e, t, D, T, st):
    fin = e["voz_t0"] - e["t0"] + e["palabras"][-1]["t"] + e["palabras"][-1]["d"]
    tc = wt(e, "cierto") - 0.3
    if t < tc:
        plaza(L, T)
        for j, look in enumerate(VECINOS_P[:3]):
            avatar_p(L, 80 + j * 60, 900, 0.9, look)
        avatar_p(L, 330, 900, 1.2, ALCALDE)
        st["cam"] = (1.05, 270, 560)
    elif t < fin + 2.0:
        plaza(L, T)
        crece = eob(prog(t, fin + 0.05, 0.5), 2.4)
        avatar_p(L, 270, 1150, 2.6, NICO, cabeza=1 + 1.3 * crece, cara="susto" if crece > 0.5 else "feliz",
                 boca=(0.5 + 0.5 * math.sin(t * 20)) if t < fin else 0)
        st["desenfoque_p"] = 5
        st["cam"] = (1.0, 270, 480)
        if crece > 0:
            st["overlay"].append(("mentira", 270, 330, crece))
    else:
        plaza(L, T)
        st["desenfoque_p"] = 8
        st["overlay"].append(("cierre", t - fin - 2.0))
        st["sin_cabecera"] = True
        st["cam"] = (1.0, 270, 480)


FUNCS = {"gancho": esc_gancho, "demo": esc_demo, "nadie": esc_nadie, "yo": esc_yo, "sombrero": esc_sombrero,
         "viento": esc_viento, "cabeza": esc_cabeza, "like": esc_like, "pregunta": esc_pregunta,
         "confesion": esc_confesion, "encoge": esc_encoge, "vecinos": esc_vecinos, "final": esc_final}
