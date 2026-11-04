# --- «En este planeta no hay nadie»: escenas (se añaden tras el motor de «En este pueblo») ---

CABECERA = "EN ESTE PLANETA · HABITANTES: 0"
PCX, PCY, PR = 270, 1480, 860          # planeta: centro y radio (horizonte en y≈620)
NUEVO = dict(camisa=(255, 120, 170), pantalon=(70, 70, 110), zapato=(250, 250, 250), suela=(60, 60, 80),
             pelo=(60, 40, 30), peinado="rizos")
AMIGO = dict(camisa=(110, 220, 170), pantalon=(60, 70, 90), zapato=(250, 250, 250), suela=(60, 60, 80),
             pelo=(30, 30, 30), peinado="corto", gorra=(90, 120, 230))


def espacio(L, T, tono=0.0):
    for i in range(0, H, 8):
        rect(L, 0, i, W, i + 8, mezcla(mezcla((10, 12, 40), (40, 20, 70), i / H), (20, 40, 90), tono))
    rs = random.Random(9)
    for _ in range(120):
        x, y = rs.uniform(0, W), rs.uniform(0, H)
        circ(L, x, y, rs.uniform(0.6, 2.0), fill=BLANCO, a=0.4 + 0.4 * math.sin(T * 2 + rs.random() * 6))
    for k, (x, y, r, c) in enumerate(((420, 300, 40, (250, 200, 120)), (90, 420, 18, (160, 200, 255)))):
        circ(L, x + 6 * math.sin(T * 0.3 + k), y, r, fill=c)
        circ(L, x + 6 * math.sin(T * 0.3 + k) - r * 0.3, y - r * 0.3, r * 0.25, fill=BLANCO, a=0.4)


def planeta(L, T):
    circ(L, PCX, PCY, PR + 26, fill=(120, 200, 255), a=0.12)
    circ(L, PCX, PCY, PR, fill=(110, 190, 100))
    circ(L, PCX, PCY, PR - 30, fill=(96, 172, 88))
    rs = random.Random(3)
    for _ in range(40):
        a2 = rs.uniform(-0.5, 0.5)
        r = PR - rs.uniform(10, 120)
        circ(L, PCX + r * math.sin(a2), PCY - r * math.cos(a2), rs.uniform(4, 10), fill=(130, 210, 110), a=0.7)


_SPRITES = {}


def sprite(nombre):
    """Objetos del planeta dibujados una vez como imagen con transparencia (ancla: centro inferior)."""
    if nombre in _SPRITES:
        return _SPRITES[nombre]
    tam = {"casa": (200, 200), "banco": (140, 80), "arbol": (110, 200), "estadio": (380, 260), "edificio": (110, 300),
           "rodador": (60, 60)}[nombre]
    img = Image.new("RGBA", (tam[0] * K, tam[1] * K), (0, 0, 0, 0))
    C = Capa(img)
    w, h = tam
    if nombre == "casa":
        cubo(C, 30, 90, 130, 110, (250, 220, 170), 12)
        poly(C, [(18, 90), (102, 30), (186, 90)], (220, 90, 80))
        rect(C, 80, 140, 110, 200, (130, 90, 60))
        rect(C, 40, 110, 70, 140, (170, 215, 245))
        rect(C, 124, 110, 154, 140, (170, 215, 245))
    elif nombre == "banco":
        rect(C, 10, 30, 130, 42, (160, 110, 70), r=3)
        rect(C, 10, 50, 130, 62, (150, 100, 60), r=3)
        for x in (20, 116):
            rect(C, x, 60, x + 8, 80, (80, 80, 90))
    elif nombre == "arbol":
        rect(C, 48, 120, 62, 200, (120, 80, 50))
        for dy, ww in ((60, 90), (24, 66), (0, 40)):
            cubo(C, 55 - ww / 2, dy + 20, ww, 46, (80, 170, 90), 8)
    elif nombre == "estadio":
        poly(C, [(10, 260), (40, 90), (340, 90), (370, 260)], (200, 200, 214))
        for k in range(5):
            y = 110 + k * 30
            poly(C, [(40 - k * 6, y), (340 + k * 6, y), (344 + k * 6, y + 14), (36 - k * 6, y + 14)], (220, 70, 80))
        rect(C, 60, 240, 320, 260, (120, 200, 110))
        for x in (30, 350):
            rect(C, x - 3, 10, x + 3, 100, (90, 90, 100))
            rect(C, x - 18, 0, x + 18, 16, (240, 240, 210), r=3)
    elif nombre == "edificio":
        cubo(C, 10, 20, 90, 280, (170, 180, 210), 10)
        for yy in range(40, 290, 28):
            for xx in (22, 52, 80):
                rect(C, xx, yy, xx + 14, yy + 16, (255, 230, 150))
    elif nombre == "rodador":
        circ(C, 30, 30, 26, outline=(180, 150, 90), w=4)
        linea(C, [(10, 20), (50, 40)], (180, 150, 90), w=3)
        linea(C, [(12, 42), (48, 18)], (180, 150, 90), w=3)
    _SPRITES[nombre] = img
    return img


def poner(L, nombre, ang, escala=1.0, hundir=6):
    """Coloca un sprite sobre la superficie del planeta en el ángulo `ang` (radianes, 0 = arriba)."""
    spr = sprite(nombre)
    if escala != 1.0:
        spr = spr.resize((max(1, int(spr.width * escala)), max(1, int(spr.height * escala))), Image.BILINEAR)
    rot = spr.rotate(-math.degrees(ang), resample=Image.BICUBIC, expand=True)
    bx = PCX + (PR - hundir) * math.sin(ang)
    by = PCY - (PR - hundir) * math.cos(ang)
    # el ancla (centro inferior) tras rotar queda desplazada del centro de la imagen
    hh = spr.height / K / 2
    cx = bx + hh * math.sin(ang)
    cy = by - hh * math.cos(ang)
    L.img.paste(rot, (int(cx * K - rot.width / 2), int(cy * K - rot.height / 2)), rot)
    L.d = ImageDraw.Draw(L.img, "RGBA")


def mundo(L, T, giro=0.0, objetos=True, extra=()):
    espacio(L, T)
    planeta(L, T)
    if objetos:
        for nombre, a0, esc in (("arbol", -0.42, 0.8), ("casa", -0.22, 1.0), ("banco", 0.16, 1.0), ("arbol", 0.3, 0.7),
                                ("estadio", 0.62, 1.0)) + tuple(extra):
            ang = a0 - giro
            if -1.2 < ang < 1.2:
                poner(L, nombre, ang, esc)


def nico_en(L, ang, s=1.2, **kw):
    x = PCX + PR * math.sin(ang)
    y = PCY - PR * math.cos(ang) + 4
    return avatar_p(L, x, y, s, NICO, **kw)


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    mundo(L, T, giro=0.02 * t)
    nico_en(L, 0.0, 1.3, brazos=(0.1, -1.5 - 0.35 * math.sin(t * 8)))
    st["cam"] = (lerp(1.55, 1.05, eio(t / D)), 270, lerp(640, 560, eio(t / D)))
    st["titulo"] = t


def esc_estadio(L, e, t, D, T, st):
    tc, tb, te = wt(e, "casa") - 0.3, wt(e, "banco") - 0.3, wt(e, "estadio") - 0.3
    destinos = [(0, 0.0), (tc, -0.22), (tb, 0.16), (te, 0.62)]
    giro = 0.0
    for (ta, ga), (tb_, gb) in zip(destinos, destinos[1:]):
        if t >= ta:
            giro = lerp(ga, gb, eio(prog(t, tb_ - 0.6, 0.6)))
    mundo(L, T, giro=giro)
    nico_en(L, 0.0 if t < te else -0.25, 1.1, paso=math.sin(t * 8) if t < te else 0)
    tv = wt(e, "vacías") - 0.3
    st["cam"] = (1.15 if t < tv else 1.6, 270, 600 if t < tv else 560)
    if t > tv:
        st["overlay"].append(("vacio", prog(t, tv, 0.3), t))


def esc_saludo(L, e, t, D, T, st):
    mundo(L, T)
    nico_en(L, 0.0, 1.5, brazos=(-0.9, 0.9), boca=0.8 if t > 0.6 else 0)
    st["cam"] = (1.5, 270, 620)


def esc_eco(L, e, t, D, T, st):
    mundo(L, T)
    nico_en(L, 0.0, 1.3, brazos=(-0.9, 0.9), boca=1.0)
    st["overlay"].append(("ondas", t))
    st["cam"] = (lerp(1.4, 0.95, eio(t / D)), 270, 560)


def esc_nadie(L, e, t, D, T, st):
    mundo(L, T)
    nico_en(L, 0.0, 1.3, cara="triste")
    u = prog(t, 0.0, D)
    poner(L, "rodador", lerp(-0.4, 0.4, u), 1.0, hundir=-2)
    st["cam"] = (1.4, 270, 620)
    st["overlay"].append(("silencio", prog(t, 0.2, 0.4)))


def esc_descubre(L, e, t, D, T, st):
    mundo(L, T, giro=0.0)
    ts = wt(e, "sigue") - 0.3
    ta = wt(e, "aparece") - 0.3
    nico_en(L, -0.18, 1.1, cara="susto" if t > ta else "feliz", mira=1)
    if t > ts:
        st["overlay"].append(("boton_seguir", prog(t, ts, 0.3), t - ts))
    if t > ta:
        st["overlay"].append(("regla", prog(t, ta, 0.4)))
        st["rayo"] = (290, prog(t, ta, 0.6))
    st["cam"] = (1.1, 270, 560)


def esc_llega(L, e, t, D, T, st):
    mundo(L, T)
    nico_en(L, -0.18, 1.1, cara="feliz", mira=1)
    tp = 1.0
    if t < tp:
        st["rayo"] = (300, 1.0)
    else:
        aparece = eob(prog(t, tp, 0.5))
        x = PCX + PR * math.sin(0.04)
        y = PCY - PR * math.cos(0.04) + 4
        avatar_p(L, x, y, 1.1 * max(0.01, aparece), NUEVO, brazos=(0.1, -1.4))
        if t < tp + 0.8:
            st["overlay"].append(("puf", 300, 520, t - tp))
        st["overlay"].append(("tag", "@¿TÚ?", 300, 380, prog(t, tp + 0.3, 0.3)))
        st["contador"] = 1
    st["cam"] = (1.35, 260, 600)


def esc_nombre(L, e, t, D, T, st):
    mundo(L, T)
    nico_en(L, -0.18, 1.1, mira=1)
    x = PCX + PR * math.sin(0.04)
    y = PCY - PR * math.cos(0.04) + 4
    avatar_p(L, x, y, 1.1, NUEVO, brazos=(0.1, -0.3 - 0.4 * math.sin(t * 4)))
    tc = wt(e, "comentas") - 0.3
    if t > tc:
        st["overlay"].append(("comentario", t - tc))
        nombre = "Ana"[:int(cl((t - tc - 0.6) / 0.6) * 3)]
        st["overlay"].append(("tag", "@" + (nombre.upper() if nombre else "…"), 300, 380, 1.0))
    else:
        st["overlay"].append(("tag", "@¿TÚ?", 300, 380, 1.0))
    st["cam"] = (1.35, 260, 600)
    st["contador"] = 1


def esc_amigo(L, e, t, D, T, st):
    mundo(L, T)
    nico_en(L, -0.18, 1.1, mira=1)
    for ang, look in ((0.04, NUEVO),):
        avatar_p(L, PCX + PR * math.sin(ang), PCY - PR * math.cos(ang) + 4, 1.1, look, brazos=(0.1, -0.3))
    ts = wt(e, "compartes") - 0.3
    if t > ts:
        st["overlay"].append(("compartir", prog(t, ts, 0.3)))
    ta = wt(e, "amigo") - 0.3
    if t > ta:
        ap = eob(prog(t, ta, 0.5))
        ang = 0.22
        avatar_p(L, PCX + PR * math.sin(ang), PCY - PR * math.cos(ang) + 4, 1.0 * max(0.01, ap), AMIGO, brazos=(0.1, -1.3))
        if t < ta + 0.8:
            st["overlay"].append(("puf", 460, 540, t - ta))
        st["contador"] = 2
    else:
        st["contador"] = 1
    st["overlay"].append(("tag", "@ANA", 300, 380, 1.0))
    st["cam"] = (1.2, 300, 600)


def esc_metas(L, e, t, D, T, st):
    tc = wt(e, "cien") - 0.3
    tm = wt(e, "mil") - 0.3
    if t < tm:
        # estadio lleno
        espacio(L, T, tono=0.3)
        planeta(L, T)
        poner(L, "estadio", 0.0, 1.35)
        llena = eio(prog(t, tc, 1.6))
        rs = random.Random(2)
        for k in range(int(70 * llena)):
            x = rs.uniform(40, 500)
            fila = rs.randrange(5)
            y = 470 + fila * 40
            col = rs.choice(VECINOS_P)["camisa"]
            rect(L, x - 7, y - 4, x + 7, y + 12, col)
            rect(L, x - 5, y - 16, x + 5, y - 5, PIEL_A)
        st["overlay"].append(("meta", "100", "ESTADIO LLENO", prog(t, tc, 0.4)))
        st["cam"] = (1.15, 270, 560)
        st["celebra"] = llena
    else:
        espacio(L, T, tono=0.3)
        planeta(L, T)
        crece = eio(prog(t, tm, 2.0))
        for k, ang in enumerate((-0.55, -0.4, -0.26, -0.12, 0.12, 0.26, 0.4, 0.55)):
            h = cl(crece * 1.4 - k * 0.06)
            if h > 0.02:
                poner(L, "edificio", ang, 0.6 + 0.6 * h * (1 if k % 2 else 0.8))
        poner(L, "estadio", 0.0, 0.9)
        st["overlay"].append(("meta", "1.000", "UNA CIUDAD ENTERA", prog(t, tm, 0.4)))
        st["cam"] = (1.0, 270, 520)


def esc_final(L, e, t, D, T, st):
    mundo(L, T)
    nico_en(L, 0.0, 1.3, mira=0, brazos=(0.1, -0.3))
    st["cam"] = (1.3, 270, 620)
    st["overlay"].append(("final", t, prog(t, wt(e, "primero") - 0.3, 0.4)))
    st["contador"] = 0
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "estadio": esc_estadio, "saludo": esc_saludo, "eco": esc_eco, "nadie": esc_nadie,
         "descubre": esc_descubre, "llega": esc_llega, "nombre": esc_nombre, "amigo": esc_amigo, "metas": esc_metas,
         "final": esc_final}
