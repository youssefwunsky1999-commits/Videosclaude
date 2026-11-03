# --- Escenas del TikTok «¿Sabías que en un incendio mata más el humo que el fuego?» ---
POSES.update({
    "gatas1": dict(rodilla=(-6, 64), pie=(-86, 70), cuello=(104, -14), cabeza=(146, -26), codo=(112, 30), mano=(124, 70),
                   codo2=(96, 30), mano2=(98, 70)),
    "gatas2": dict(rodilla=(10, 64), pie=(-70, 70), cuello=(104, -10), cabeza=(146, -22), codo=(100, 30), mano=(100, 70),
                   codo2=(114, 30), mano2=(128, 70)),
    "toca": dict(rodilla=(4, 95), pie=(2, 190), cuello=(6, -150), cabeza=(12, -196), codo=(50, -116), mano=(96, -104),
                 codo2=(-8, -74), mano2=(-4, -10)),
    "tose": dict(rodilla=(8, 94), pie=(4, 190), cuello=(20, -142), cabeza=(36, -180), codo=(40, -100), mano=(44, -150),
                 codo2=(-10, -76), mano2=(-4, -16)),
    "ventana": dict(rodilla=(4, 95), pie=(2, 190), cuello=(4, -150), cabeza=(10, -196), codo=(34, -140), mano=(14, -190),
                    codo2=(46, -170), mano2=(70, -226)),
})
PARED_H = (214, 206, 190)
SUELO_H = (150, 112, 80)


def salon(L, T, puerta_x=None):
    rect(L, 0, 0, W, 780, PARED_H)
    rect(L, 0, 760, W, 780, (180, 170, 150))
    rect(L, 0, 780, W, H, SUELO_H)
    for k in range(7):
        linea(L, [(0, 790 + k * k * 4), (W, 790 + k * k * 4)], (126, 92, 64), w=1.2)
    rect(L, 330, 420, 470, 540, (120, 90, 60), r=4)
    rect(L, 340, 430, 460, 530, (230, 200, 150))
    # sofá
    rect(L, 300, 640, 520, 720, (110, 132, 170), r=14)
    rect(L, 300, 700, 520, 760, (88, 106, 140), r=10)
    if puerta_x is not None:
        puerta(L, puerta_x)


def puerta(L, x, abierta=0.0, calor=0.0, T=0.0):
    rect(L, x - 6, 430, x + 146, 780, (150, 140, 120))
    rect(L, x, 436, x + 140, 780, (140, 96, 60))
    if calor > 0:
        rect(L, x, 436, x + 140, 780, (255, 90, 40), a=calor * (0.35 + 0.1 * math.sin(T * 6)))
    rect(L, x + 14, 456, x + 126, 590, (156, 108, 70))
    rect(L, x + 14, 610, x + 126, 760, (156, 108, 70))
    circ(L, x + 118, 620, 8, fill=(220, 190, 110))
    if calor > 0:
        rect(L, x + 20, 772, x + 120, 780, (255, 170, 60), a=calor)


def humo(L, T, nivel=400, dens=0.85):
    """Capa de humo que baja del techo; nivel = y del borde inferior."""
    pts = [(0, 0), (W, 0)]
    for k in range(13, -1, -1):
        x = k * W / 13
        pts.append((x, nivel + 22 * math.sin(T * 1.3 + k * 0.9) + 10 * math.sin(T * 2.7 + k * 1.7)))
    poly(L, pts, (70, 70, 76), dens)
    for k in range(12):
        x = (k * 61 + T * 18 * (1 if k % 2 else -1)) % (W + 120) - 60
        circ(L, x, nivel - 10 + 14 * math.sin(T + k), 40 + 10 * (k % 3), fill=(90, 90, 96), a=dens * 0.8)
    rect(L, 0, 0, W, nivel * 0.6, (40, 40, 46), a=dens * 0.6)


def fuego(L, x, y, s=1.0, T=0.0):
    for k, col in enumerate(((235, 70, 40), (255, 150, 40), (255, 220, 90))):
        h = (110 - k * 28) * s * (1 + 0.08 * math.sin(T * 9 + k))
        w = (60 - k * 15) * s
        poly(L, [(x - w, y), (x - w * 0.5, y - h * 0.6), (x - w * 0.2 + 8 * math.sin(T * 7), y - h),
                 (x + w * 0.3, y - h * 0.55), (x + w, y)], col)


def esc_gancho(L, e, t, D, T, st):
    salon(L, T)
    fuego(L, 440, 780, 1.1, T)
    humo(L, T, nivel=lerp(250, 470, eio(t / D)))
    persona(L, 170, 860 - 190, "tose", 1.0, ropa=PROTA, pelo=(60, 36, 24), ojos=1.5, boca=0.7)
    st["cam"] = (1.25 - 0.12 * eio(t / D), 270, 560)
    st["alarma"] = t
    st["overlay"].append(("titular", t, "¿SABÍAS QUE EN UN INCENDIO…", "MATA MÁS EL HUMO", 1.0))
    st["sin_cabecera"] = True


def esc_porque(L, e, t, D, T, st):
    salon(L, T)
    fuego(L, 440, 780, 1.0, T)
    humo(L, T, nivel=480)
    persona(L, 170, 860 - 190, "tose", 1.0, ropa=PROTA, pelo=(60, 36, 24), ojos=1.2, boca=0.6)
    for j, (pal, txt) in enumerate((("caliente", "CALIENTE"), ("tóxico", "TÓXICO"), ("sube", "SUBE ↑"))):
        q = prog(t, wt(e, pal) - 0.3, 0.3)
        st["overlay"].append(("regla", txt, j, q, False))
    qi = prog(t, wt(e, "inconsciente") - 0.4, 0.3)
    if qi > 0:
        st["overlay"].append(("sello", "POCAS BOCANADAS", qi, 900, ROJO))
    st["paso"] = ("!", "POR QUÉ MATA")


def esc_agachate(L, e, t, D, T, st):
    salon(L, T)
    humo(L, T, nivel=560)
    q = prog(t, wt(e, "agáchate") - 0.3, 0.5)
    if q <= 0:
        persona(L, 200, 860 - 190, "tose", 1.0, ropa=PROTA, pelo=(60, 36, 24), boca=0.6)
    else:
        x = lerp(80, 260, eio(prog(t, wt(e, "agáchate"), D)))
        persona(L, x, 860 - 70, pose_mix("gatas1", "gatas2", 0.5 + 0.5 * math.sin(t * 6)), 1.0, ropa=PROTA, pelo=(60, 36, 24))
    ql = prog(t, wt(e, "limpio") - 0.4, 0.4)
    if ql > 0:
        rect(L, 0, 700, W, 860, (150, 220, 255), a=0.18 * ql)
        texto(L, "AIRE MÁS LIMPIO", 270, 640, 26, (190, 236, 255), a=ql, fuente="black")
        texto(L, "HUMO", 270, 470, 30, (220, 220, 220), a=ql, fuente="black")
    st["paso"] = (1, "AGÁCHATE")


def esc_puerta(L, e, t, D, T, st):
    salon(L, T, puerta_x=None)
    calor = prog(t, wt(e, "quema") - 0.4, 0.5)
    puerta(L, 300, calor=calor, T=T)
    humo(L, T, nivel=440, dens=0.6)
    toca = prog(t, wt(e, "dorso") - 0.6, 0.4)
    persona(L, 210, 860 - 190, "toca" if toca > 0 else "de_pie", 1.0, ropa=PROTA, pelo=(60, 36, 24),
            ojos=1.0 + 0.6 * calor)
    qd = prog(t, wt(e, "dorso") - 0.3, 0.3)
    if qd > 0:
        texto(L, "DORSO DE LA MANO", 160, 520, 18, BLANCO, a=qd, fuente="black")
    if calor > 0:
        for k in range(5):
            u = (t * 0.8 + k / 5) % 1
            linea(L, [(330 + k * 22, 560 - u * 80), (336 + k * 22, 540 - u * 80), (330 + k * 22, 520 - u * 80)],
                  (255, 160, 80), w=3, a=calor * math.sin(u * math.pi))
        st["overlay"].append(("regla", "SI QUEMA, NO ABRAS", 0, prog(t, wt(e, "abras") - 0.3, 0.3), False))
    st["paso"] = (2, "TOCA LA PUERTA")


def esc_like(L, e, t, D, T, st):
    salon(L, T)
    st["tinte"] = ((0, 0, 0), 0.45)
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    st["sin_cabecera"] = True


def esc_cierra(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (40, 40, 46))
    # pasillo en corte con puertas que se cierran
    rect(L, 0, 300, W, 780, PARED_H)
    rect(L, 0, 780, W, H, SUELO_H)
    for j, x in enumerate((40, 300)):
        cierre = eio(prog(t, 0.4 + j * 0.9, 0.5))
        rect(L, x, 430, x + 140, 780, (30, 30, 34))
        ancho_ = 140 * cierre
        rect(L, x, 436, x + ancho_, 780, (140, 96, 60))
        if cierre >= 1:
            texto(L, "✓", x + 70, 400, 40, VERDE, fuente="sym")
    humo(L, T, nivel=lerp(560, 360, eio(prog(t, 0, 2.0))), dens=0.5)
    qa = prog(t, wt(e, "ascensor") - 0.3, 0.3)
    if qa > 0:
        rect(L, 160, 470, 380, 760, (0, 0, 0), a=0.6 * qa, r=10)
        texto(L, "ASCENSOR", 270, 560, 28, BLANCO, a=qa, fuente="black")
        circ(L, 270, 660, 60 * eob(qa), outline=ROJO, w=10, a=qa)
        linea(L, [(228, 618), (312, 702)], ROJO, w=10, a=qa)
    st["overlay"].append(("chip", "CIERRA PUERTAS", 0, prog(t, wt(e, "cierras") - 0.3, 0.3)))
    st["paso"] = (3, "CIERRA Y BAJA ANDANDO")


def esc_atrapado(L, e, t, D, T, st):
    rect(L, 0, 0, W, 780, (200, 210, 220))
    rect(L, 0, 780, W, H, SUELO_H)
    # ventana
    rect(L, 280, 330, 500, 560, (120, 90, 60), r=4)
    rect(L, 292, 342, 488, 548, (60, 80, 120))
    for k in range(6):
        circ(L, 300 + k * 36, 380 + 30 * math.sin(k), 3, fill=(255, 240, 200))
    # puerta con toalla
    rect(L, 20, 430, 160, 780, (140, 96, 60))
    qt = prog(t, wt(e, "toallas") - 0.4, 0.4)
    if qt > 0:
        rect(L, 10, 760, 170, 790, (90, 170, 220), a=qt, r=8)
        texto(L, "TOALLA MOJADA", 90, 820, 15, BLANCO, a=qt, fuente="black")
        for k in range(6):
            circ(L, 30 + k * 26, 796 + 6 * ((t * 3 + k) % 1), 3, fill=(120, 200, 255), a=qt)
    qv = prog(t, wt(e, "ventana") - 0.4, 0.4)
    persona(L, lerp(220, 380, eio(qv)), 860 - 190, "ventana" if qv >= 1 else "de_pie", 1.0, ropa=PROTA, pelo=(60, 36, 24),
            flip=False)
    q1 = prog(t, wt(e, "uno") - 0.3, 0.3)
    if q1 > 0:
        st["overlay"].append(("numero", "112", "", q1, 470))
    st["paso"] = (4, "SI NO PUEDES SALIR")


def esc_detector(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (40, 44, 60))
    rect(L, 0, 0, W, 300, (230, 226, 216))
    # detector en el techo
    L.d.ellipse(P(190, 270, 350, 330), fill=L.c(BLANCO))
    rect(L, 200, 290, 340, 300, (220, 220, 220))
    on = (T * 2) % 1 < 0.3
    circ(L, 300, 310, 6, fill=ROJO if on else (120, 40, 40))
    q = prog(t, wt(e, "detector") - 0.3, 0.4)
    if q > 0:
        for k in range(3):
            u = (t * 1.2 + k / 3) % 1
            L.d.arc(P(270 - 80 - 120 * u, 300 - 40 - 60 * u, 270 + 80 + 120 * u, 300 + 120 + 120 * u), 30, 150,
                    fill=L.c(ROJO, q * (1 - u)), width=4 * K)
    # cama y persona que se despierta
    rect(L, 60, 720, 480, 800, (220, 220, 230), r=12)
    rect(L, 60, 690, 160, 740, BLANCO, r=10)
    rect(L, 140, 700, 480, 780, (90, 120, 190), r=14)
    qd = prog(t, wt(e, "despierta") - 0.3, 0.4)
    circ(L, 110, 680 - 40 * qd, 30, fill=PIEL)
    L.d.pieslice(P(80, 646 - 40 * qd, 140, 706 - 40 * qd), 180, 360, fill=L.c((60, 36, 24)))
    if qd > 0:
        texto(L, "!", 160, 590, 60, AMARILLO, a=qd, fuente="black")
    qe = prog(t, wt(e, "euros") - 0.3, 0.3)
    if qe > 0:
        st["overlay"].append(("sello", "UNOS POCOS EUROS", qe, 460, VERDE))
    st["paso"] = (5, "DETECTOR DE HUMO")


def esc_final(L, e, t, D, T, st):
    salon(L, T)
    persona(L, 200, 860 - 190, "de_pie", 1.0, ropa=PROTA, pelo=(60, 36, 24), boca=0.3)
    st["tinte"] = ((0, 0, 0), 0.4)
    st["overlay"].append(("final", t, prog(t, wt(e, "Guarda") - 0.2, 0.3), prog(t, wt(e, "mándaselo") - 0.2, 0.3),
                          prog(t, wt(e, "sígueme") - 0.2, 0.3)))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "porque": esc_porque, "agachate": esc_agachate, "puerta": esc_puerta, "like": esc_like,
         "cierra": esc_cierra, "atrapado": esc_atrapado, "detector": esc_detector, "final": esc_final}


def crepitar(dur, seed=7):
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(seed)
    for _ in range(int(dur * 25)):
        p = rng.integers(0, max(1, n - 400))
        out[p:p + 300] += rng.standard_normal(300).astype(np.float32) * np.exp(-np.arange(300) / 40) * rng.uniform(0.1, 0.5)
    return out + ruido_filtrado(n, 50, seed) * 0.15


def efectos(fx, E):
    g = E["gancho"]
    colocar(fx, crepitar(g["dur"] + E["porque"]["dur"]), 0.0, 0.5)
    colocar(fx, braam(), g["t0"] + wt(g, "humo") - 0.3, 0.6)
    p = E["porque"]
    for pal in ("caliente", "tóxico", "sube"):
        colocar(fx, pop(), p["t0"] + wt(p, pal) - 0.3, 0.5)
    colocar(fx, golpe() * 0.6, p["t0"] + wt(p, "inconsciente") - 0.4, 0.6)
    pu = E["puerta"]
    colocar(fx, crepitar(3.0, 9), pu["t0"] + wt(pu, "quema") - 0.4, 0.5)
    colocar(fx, braam(), pu["t0"] + wt(pu, "quema") - 0.3, 0.5)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.6)
    c = E["cierra"]
    for k in range(2):
        colocar(fx, golpe() * 0.4, c["t0"] + 0.9 + k * 0.9, 0.5)
    colocar(fx, golpe() * 0.5, c["t0"] + wt(c, "ascensor") - 0.3, 0.5)
    a = E["atrapado"]
    colocar(fx, tono(2), a["t0"] + wt(a, "uno") - 0.2, 0.5)
    d = E["detector"]
    for k in range(int(d["dur"] * 2)):
        colocar(fx, bip_detector(), d["t0"] + wt(d, "detector") - 0.3 + k * 0.5, 0.35)


def bip_detector():
    m = int(0.18 * SR)
    u = np.arange(m) / SR
    return (np.sign(np.sin(2 * np.pi * 3100 * u)) * 0.15 * np.clip((0.18 - u) / 0.02, 0, 1)).astype(np.float32)
