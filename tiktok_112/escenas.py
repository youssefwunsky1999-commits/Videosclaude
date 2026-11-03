# --- Escenas del TikTok «¿Sabías que el 112 sabe dónde estás?» ---
FONDO_C = (232, 236, 244)
VERDE_112 = (30, 120, 70)


def movil_grande(L, x0, y0, s=1.0, a=1.0, pantalla=(240, 242, 248)):
    rect(L, x0, y0, x0 + 220 * s, y0 + 420 * s, (16, 16, 20), a=a, r=30 * s)
    rect(L, x0 + 12 * s, y0 + 16 * s, x0 + 208 * s, y0 + 404 * s, pantalla, a=a, r=22 * s)


def mapa(L, x0, y0, x1, y1, T):
    rect(L, x0, y0, x1, y1, (214, 230, 214))
    for k in range(7):
        linea(L, [(x0, y0 + 30 + k * 70), (x1, y0 + 10 + k * 76)], (250, 250, 250), w=8)
    for k in range(4):
        linea(L, [(x0 + 60 + k * 120, y0), (x0 + 30 + k * 130, y1)], (250, 250, 250), w=6)
    for k in range(5):
        rect(L, x0 + 20 + k * 90, y0 + 50 + (k % 2) * 140, x0 + 70 + k * 90, y0 + 100 + (k % 2) * 140, (190, 200, 210))


def pin(L, x, y, T, s=1.0, a=1.0, col=ROJO):
    yy = y - 8 * abs(math.sin(T * 3)) * s
    circ(L, x, yy - 30 * s, 20 * s, fill=col, a=a)
    poly(L, [(x - 16 * s, yy - 22 * s), (x + 16 * s, yy - 22 * s), (x, yy)], col, a)
    circ(L, x, yy - 30 * s, 8 * s, fill=BLANCO, a=a)


def antena(L, x, y, s=1.0, col=(90, 96, 110), a=1.0, ondas=0.0, T=0.0):
    poly(L, [(x - 30 * s, y), (x + 30 * s, y), (x + 4 * s, y - 150 * s), (x - 4 * s, y - 150 * s)], col, a)
    for k in range(4):
        linea(L, [(x - 24 * s + k * 4 * s, y - 30 * s - k * 30 * s), (x + 24 * s - k * 4 * s, y - 30 * s - k * 30 * s)],
              col, w=3, a=a)
    if ondas > 0:
        for k in range(3):
            u = (T * 1.2 + k / 3) % 1
            r = (20 + 50 * u) * s
            L.d.arc(P(x - r, y - 150 * s - r, x + r, y - 150 * s + r), 200, 340, fill=L.c(col, ondas * (1 - u)), width=3 * K)


def esc_gancho(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (24, 28, 40))
    mapa(L, 0, 0, W, H, T)
    q = prog(t, -0.3, 0.4)
    for k in range(3):
        u = (t * 1.1 + k / 3) % 1
        circ(L, 360, 800, 30 + 120 * u, outline=ROJO, w=3, a=q * (1 - u))
    pin(L, 360, 840, T, 1.6 * eob(q) + 0.01, a=q)
    movil_grande(L, 40, 730, 0.5, pantalla=VERDE_112)
    texto(L, "112", 40 + 110 * 0.5, 730 + 100 * 0.5, 30, BLANCO, fuente="black", sombra=False)
    texto(L, f"00:{int(t):02d}", 40 + 110 * 0.5, 730 + 150 * 0.5, 13, BLANCO, fuente="mono", sombra=False)
    st["cam"] = (1.08 - 0.04 * eio(t / D), 270, 560)
    st["overlay"].append(("titular", t, "¿SABÍAS QUE AL LLAMAR AL 112…", "SABEN DÓNDE ESTÁS", 1.0))
    st["sin_cabecera"] = True


def esc_como(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, FONDO_C)
    movil_grande(L, 40, 340, 0.85)
    x0, y0 = 40, 340
    texto(L, "112", x0 + 94, y0 + 70, 38, VERDE_112, fuente="black", sombra=False)
    for j, (pal, txt) in enumerate((("GPS", "GPS"), ("wifi", "WIFI"))):
        q = prog(t, wt(e, pal) - 0.3, 0.3)
        y = y0 + 140 + j * 60
        rect(L, x0 + 26, y, x0 + 162, y + 44, VERDE if q > 0.5 else (200, 204, 214), r=22)
        circ(L, x0 + 140 if q > 0.5 else x0 + 48, y + 22, 16, fill=BLANCO)
        texto(L, txt, x0 + 90, y + 22, 13, (30, 30, 40), fuente="black", sombra=False)
    # edificio del 112
    rect(L, 330, 520, 510, 760, (60, 70, 96), r=6)
    for k in range(3):
        for j in range(4):
            rect(L, 346 + j * 40, 540 + k * 50, 370 + j * 40, 570 + k * 50, (255, 230, 150))
    rect(L, 360, 470, 480, 520, ROJO, r=8)
    texto(L, "112", 420, 495, 26, BLANCO, fuente="black", sombra=False)
    qe = prog(t, wt(e, "envía") - 0.3, 1.2)
    if 0 < qe < 1:
        x = lerp(130, 420, eio(qe))
        y = lerp(560, 600, eio(qe)) - 100 * math.sin(qe * math.pi)
        rect(L, x - 24, y - 16, x + 24, y + 16, BLANCO, r=4, outline=(120, 120, 140), w=2)
        linea(L, [(x - 24, y - 16), (x, y + 2), (x + 24, y - 16)], (120, 120, 140), w=2)
    if qe >= 1:
        pin(L, 420, 450, T, 0.9)
    qv = prog(t, wt(e, "ves") - 0.3, 0.3)
    if qv > 0:
        st["overlay"].append(("sello", "TÚ NI LO VES", qv, 860, AMARILLO))
    qa = prog(t, wt(e, "AML") - 0.3, 0.3)
    if qa > 0:
        texto(L, "AML", 420, 400, 44 * eob(qa) + 1, (40, 40, 60), a=qa, fuente="black", sombra=False)
    st["paso"] = (1, "CÓMO FUNCIONA")


def esc_precision(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (24, 28, 40))
    mapa(L, 0, 300, W, H, T)
    antena(L, 120, 560, 0.8, ondas=1.0, T=T)
    qa = prog(t, wt(e, "antena") - 0.3, 0.4)
    qk = prog(t, wt(e, "kilómetros") - 0.3, 0.4)
    qm = prog(t, wt(e, "metros") - 0.5, 0.8)
    r = lerp(300 * eob(qk) if qk > 0 else 0, 40, eio(qm))
    if r > 1:
        circ(L, 330, 640, r, fill=ROJO if qm > 0 else (240, 130, 60), a=0.18)
        circ(L, 330, 640, r, outline=ROJO if qm > 0 else (240, 130, 60), w=4)
    if qm > 0.5:
        pin(L, 330, 640, T, 1.0)
    if qk > 0:
        texto(L, "ANTES: KILÓMETROS", 270, 360, 26, (240, 130, 60) if qm <= 0 else (150, 150, 160), a=qk, fuente="black")
    if qm > 0:
        texto(L, "AHORA: DECENAS DE METROS", 270, 410, 26, VERDE, a=qm, fuente="black")
    _ = qa
    st["paso"] = (2, "PRECISIÓN")


def esc_gratis(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, FONDO_C)
    for j, (pal, txt) in enumerate((("apagada", "UBICACIÓN APAGADA: FUNCIONA"), ("gratis", "GRATIS"),
                                     ("datos", "NO GASTA TUS DATOS"))):
        q = prog(t, wt(e, pal) - 0.3, 0.3)
        st["overlay"].append(("chip", txt, j * 1.4, q))
    movil_grande(L, 160, 560, 0.75)
    pin(L, 160 + 82, 560 + 200, T, 1.2)
    st["paso"] = (3, "Y ADEMÁS")


def esc_like(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, FONDO_C)
    st["tinte"] = ((0, 0, 0), 0.55)
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    st["sin_cabecera"] = True


def esc_bloqueado(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (24, 28, 40))
    x0, y0, s = 115, 320, 1.4
    movil_grande(L, x0, y0, s, pantalla=(40, 60, 110))
    texto(L, "7:42", x0 + 110 * s, y0 + 90 * s, 54, BLANCO, fuente="black", sombra=False)
    # candado
    rect(L, x0 + 96 * s, y0 + 150 * s, x0 + 124 * s, y0 + 176 * s, BLANCO, r=4)
    L.d.arc(P(x0 + 100 * s, y0 + 134 * s, x0 + 120 * s, y0 + 160 * s), 180, 360, fill=L.c(BLANCO), width=4 * K)
    qe = prog(t, wt(e, "emergencia") - 0.4, 0.4)
    yb = y0 + 360 * s
    rect(L, x0 + 30 * s, yb - 18 * s, x0 + 190 * s, yb + 18 * s, ROJO if qe > 0 else (80, 90, 120), r=18 * s)
    texto(L, "EMERGENCIA", x0 + 110 * s, yb, 16, BLANCO, fuente="black", sombra=False)
    if qe > 0:
        for k in range(3):
            u = (t * 1.5 + k / 3) % 1
            rect(L, x0 + 30 * s - 20 * u, yb - 18 * s - 20 * u, x0 + 190 * s + 20 * u, yb + 18 * s + 20 * u, None,
                 outline=ROJO, w=3, a=qe * (1 - u), r=24)
    st["paso"] = (4, "CON EL MÓVIL BLOQUEADO")


def esc_red(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (190, 220, 240))
    rect(L, 0, 760, W, H, (120, 170, 110))
    qc = prog(t, wt(e, "cobertura") - 0.3, 0.3)
    qo = prog(t, wt(e, "otra") - 0.3, 0.3)
    antena(L, 120, 760, 1.0, col=(150, 150, 160))
    texto(L, "TU COMPAÑÍA", 120, 800, 16, (40, 40, 50), fuente="black", sombra=False)
    if qc > 0:
        texto(L, "✗", 120, 560, 60, ROJO, a=qc, fuente="sym")
    antena(L, 420, 760, 1.0, col=VERDE_112, ondas=qo, T=T)
    texto(L, "OTRA RED", 420, 800, 16, (40, 40, 50), fuente="black", sombra=False)
    if qo > 0:
        texto(L, "✓", 420, 560, 60, VERDE, a=qo, fuente="sym")
    persona(L, 270, 900 - 190 * 0.8, "movil_oreja", 0.8, ropa=PROTA, pelo=(60, 36, 24))
    qs = prog(t, wt(e, "saldo") - 0.3, 0.3)
    st["overlay"].append(("chip", "SIN SALDO TAMBIÉN", 0, qs))
    st["paso"] = (5, "SIN SALDO NI COBERTURA")


def esc_europa(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (0, 51, 153))
    for k in range(12):
        ang = k / 12 * 2 * math.pi
        q = prog(t, 0.1 + k * 0.05, 0.2)
        x, y = 270 + 170 * math.cos(ang), 600 + 170 * math.sin(ang)
        texto(L, "★", x, y, 34 * eob(q) + 1, (255, 204, 0), a=q, fuente="sym", sombra=False)
    q = prog(t, wt(e, "mismo") - 0.3, 0.4)
    texto(L, "112", 270, 600, 90 * eob(q) + 1, BLANCO, a=q, fuente="black")
    st["paso"] = (6, "EN TODA LA UE")


def esc_final(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (24, 28, 40))
    mapa(L, 0, 300, W, H, T)
    pin(L, 270, 640, T, 1.6)
    st["tinte"] = ((0, 0, 0), 0.45)
    st["overlay"].append(("final", t, prog(t, wt(e, "Guarda") - 0.2, 0.3), prog(t, wt(e, "mándaselo") - 0.2, 0.3),
                          prog(t, wt(e, "sígueme") - 0.2, 0.3)))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "como": esc_como, "precision": esc_precision, "gratis": esc_gratis, "like": esc_like,
         "bloqueado": esc_bloqueado, "red": esc_red, "europa": esc_europa, "final": esc_final}


def efectos(fx, E):
    g = E["gancho"]
    colocar(fx, tono(2), 0.1, 0.5)
    colocar(fx, braam() * 0.7, g["t0"] + wt(g, "dice") - 0.4, 0.6)
    c = E["como"]
    for pal in ("AML", "GPS", "wifi"):
        colocar(fx, pop(), c["t0"] + wt(c, pal) - 0.3, 0.5)
    colocar(fx, whoosh(5, 1.0), c["t0"] + wt(c, "envía") - 0.3, 0.5)
    colocar(fx, dingdong(), c["t0"] + wt(c, "envía") + 0.9, 0.4)
    p = E["precision"]
    colocar(fx, golpe() * 0.5, p["t0"] + wt(p, "kilómetros") - 0.3, 0.5)
    colocar(fx, whoosh(8, 0.8), p["t0"] + wt(p, "metros") - 0.5, 0.5)
    colocar(fx, pop(), p["t0"] + wt(p, "metros") + 0.2, 0.6)
    gr = E["gratis"]
    for pal in ("apagada", "gratis", "datos"):
        colocar(fx, pop(), gr["t0"] + wt(gr, pal) - 0.3, 0.5)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.6)
    b = E["bloqueado"]
    colocar(fx, tic(), b["t0"] + wt(b, "emergencia") - 0.4, 0.6)
    colocar(fx, tono(2), b["t0"] + wt(b, "emergencia") + 0.2, 0.4)
    r = E["red"]
    colocar(fx, golpe() * 0.4, r["t0"] + wt(r, "cobertura") - 0.3, 0.5)
    colocar(fx, pop(), r["t0"] + wt(r, "otra") - 0.3, 0.6)
    eu = E["europa"]
    for k in range(12):
        colocar(fx, tic() * 0.5, eu["t0"] + 0.1 + k * 0.05, 0.4)
    colocar(fx, golpe() * 0.6, eu["t0"] + wt(eu, "mismo") - 0.3, 0.6)
