# --- Escenas del TikTok «Imagínate que te quedas encerrado en un ascensor» ---
METAL = (176, 182, 194)
METAL_S = (150, 156, 170)
METAL_O = (120, 126, 140)
SUELO_C = (84, 86, 96)
POSES.update({
    "pulsa": dict(rodilla=(4, 95), pie=(2, 190), cuello=(2, -150), cabeza=(8, -196), codo=(48, -122), mano=(96, -118),
                  codo2=(-8, -74), mano2=(-4, -10)),
    "fuerza": dict(rodilla=(24, 92), pie=(30, 188), cuello=(20, -146), cabeza=(30, -190), codo=(60, -106), mano=(104, -98),
                   codo2=(58, -84), mano2=(102, -76)),
    "miedo": dict(rodilla=(4, 95), pie=(2, 190), cuello=(-4, -146), cabeza=(-8, -190), codo=(26, -120), mano=(16, -170),
                  codo2=(-30, -116), mano2=(-14, -166)),
})


def cabina(L, T, luz=1.0, panel=True, puertas=0.0, fuera=(14, 14, 18)):
    """Interior del ascensor visto de frente. puertas: 0 cerradas -> 1 abiertas (hueco oscuro)."""
    rect(L, 0, 0, W, H, METAL_O)
    rect(L, 30, 280, 510, 800, METAL)
    for x in (30, 150, 390):
        rect(L, x, 280, x + 4, 800, METAL_S)
    rect(L, 30, 280, 510, 300, (220, 226, 236))
    rect(L, 80, 286, 460, 296, (255, 250, 220), a=luz)
    rect(L, 0, 800, W, H, SUELO_C)
    for k in range(6):
        linea(L, [(0, 820 + k * 24), (W, 820 + k * 24)], (74, 76, 86), w=1)
    # puertas
    ab = 110 * puertas
    if puertas > 0:
        rect(L, 160, 340, 380, 800, fuera)
    rect(L, 160 - ab, 340, 270 - ab, 800, (196, 202, 214))
    rect(L, 270 + ab, 340, 380 + ab, 800, (196, 202, 214))
    linea(L, [(270 - ab, 340), (270 - ab, 800)], METAL_O, w=2)
    linea(L, [(270 + ab, 340), (270 + ab, 800)], METAL_O, w=2)
    rect(L, 150, 330, 390, 342, METAL_S)
    if panel:
        rect(L, 412, 450, 470, 680, (60, 64, 76), r=8)
        for k in range(6):
            circ(L, 441, 474 + k * 30, 10, fill=(200, 204, 214))
            texto(L, str(6 - k), 441, 474 + k * 30, 10, (40, 40, 40), fuente="black", sombra=False)
        circ(L, 441, 654, 13, fill=AMARILLO)
        campana(L, 441, 654, 0.6)


def campana(L, x, y, s=1.0, col=(60, 40, 10), a=1.0):
    L.d.chord(P(x - 10 * s, y - 12 * s, x + 10 * s, y + 10 * s), 180, 360, fill=L.c(col, a))
    rect(L, x - 10 * s, y - 2 * s, x + 10 * s, y + 4 * s, col, a=a)
    circ(L, x, y + 6 * s, 3 * s, fill=col, a=a)


SHAFT_X0, SHAFT_X1 = 140, 400


def hueco(L, T, cab_y=420, cables=6, resalta=-1, freno=0.0, desplaza=0.0):
    """Corte del hueco del ascensor: guías, plantas, cabina colgando de cables, contrapeso y polea."""
    rect(L, 0, 0, W, H, (26, 28, 36))
    rect(L, SHAFT_X0 - 30, 0, SHAFT_X1 + 100, H, (44, 46, 58))
    # plantas (se desplazan para simular movimiento)
    for k in range(-2, 5):
        y = ((k * 300 + desplaza) % 1500) - 300
        rect(L, 0, y, SHAFT_X0 - 30, y + 30, (70, 72, 86))
        rect(L, SHAFT_X1 + 100, y, W, y + 30, (70, 72, 86))
        texto(L, f"PLANTA {4 - k}", 60, y - 14, 11, (150, 154, 170), fuente="black", sombra=False)
    # guías
    for x in (SHAFT_X0 - 6, SHAFT_X1 + 2):
        rect(L, x, 0, x + 4, H, (110, 114, 130))
    # polea / motor
    rect(L, 150, 40, 470, 120, (60, 62, 76), r=10)
    circ(L, 270, 100, 34, fill=(90, 94, 110))
    circ(L, 270, 100, 10, fill=(40, 40, 50))
    texto(L, "MOTOR", 400, 70, 13, (170, 174, 190), fuente="black", sombra=False)
    # cables
    x0 = 232
    for k in range(cables):
        x = x0 + k * 15
        col = AMARILLO if k == resalta else (200, 204, 214)
        linea(L, [(x, 100), (x, cab_y)], col, w=3 if k == resalta else 2)
    # contrapeso
    linea(L, [(304, 66), (450, 66), (450, 300)], (200, 204, 214), w=2)
    rect(L, 432, 300, 468, 420, (90, 92, 104), r=4)
    texto(L, "CONTRAPESO", 450, 436, 10, (150, 154, 170), fuente="black", sombra=False)
    # cabina
    rect(L, SHAFT_X0, cab_y, SHAFT_X1, cab_y + 230, METAL, r=6)
    rect(L, SHAFT_X0 + 10, cab_y + 10, SHAFT_X1 - 10, cab_y + 220, (210, 216, 226), r=4)
    rect(L, 220, cab_y + 40, 320, cab_y + 220, (196, 202, 214))
    linea(L, [(270, cab_y + 40), (270, cab_y + 220)], METAL_O, w=2)
    # cuñas del freno
    if freno > 0:
        for x, s in ((SHAFT_X0 - 4, -1), (SHAFT_X1, 1)):
            poly(L, [(x, cab_y + 200), (x + 14 * s, cab_y + 180), (x + 14 * s, cab_y + 230), (x, cab_y + 230)], ROJO, a=freno)
        for k in range(8):
            u = (T * 3 + k / 8) % 1
            for xx, s in ((SHAFT_X0 - 4, -1), (SHAFT_X1 + 2, 1)):
                circ(L, xx + s * 30 * u, cab_y + 230 - 60 * u + 20 * math.sin(k), 2.5, fill=(255, 210, 80), a=freno * (1 - u))


# ================================================================== escenas
def esc_gancho(L, e, t, D, T, st):
    parpadeo = 1.0 if (T % 1.3) > 0.12 and (T % 2.9) > 0.2 else 0.15
    cabina(L, T, luz=parpadeo)
    persona(L, 100, 800 - 190 * 0.95, "miedo", 0.95, ropa=PROTA, pelo=(60, 36, 24), ojos=1.6, boca=0.6)
    st["cam"] = (1.3 - 0.15 * eio(t / D), 230, 560)
    st["alarma"] = t
    st["tinte"] = ((0, 0, 0), 0.35 * (1 - parpadeo))
    st["shake"] = 3 if t < 0.5 else 0
    st["overlay"].append(("titular", t, "ENCERRADO EN UN ASCENSOR", "¿SE VA A CAER?",
                          1.0))
    st["sin_cabecera"] = True


def esc_cables(L, e, t, D, T, st):
    q = prog(t, wt(e, "cada") - 0.2, 0.3)
    k = int(t * 3) % 6 if q <= 0 else 2
    hueco(L, T, resalta=k if prog(t, wt(e, "cables") - 0.3, 0.2) > 0 else -1)
    qc = prog(t, wt(e, "cables") - 0.3, 0.3)
    if qc > 0:
        texto(L, "6 CABLES", 400, 330, 26 * eob(qc) + 1, AMARILLO, a=qc, fuente="black")
        linea(L, [(350, 340), (312, 360)], AMARILLO, w=2, a=qc)
    if q > 0:
        st["overlay"].append(("sello", "1 SOLO YA LO AGUANTA", q, 760, VERDE))
    st["cam"] = (1.06, 270, 420)
    st["paso"] = ("✓", "NO SE CAE")


def esc_freno(L, e, t, D, T, st):
    t_f = wt(e, "freno") - 0.2
    if t < t_f:
        v = 600 * prog(t, 0.3, t_f - 0.3) ** 1.5
        desp = 300 * prog(t, 0.3, t_f - 0.3) ** 2.5 * 4
        st["shake"] = 2
    else:
        desp = 1200 + 0
        v = 0
    hueco(L, T, cab_y=440, desplaza=-desp if t < t_f else -1200, freno=prog(t, t_f, 0.2))
    if v > 50:
        for k in range(6):
            linea(L, [(SHAFT_X0 + 20 + k * 40, 380), (SHAFT_X0 + 20 + k * 40, 380 - v * 0.1)], BLANCO, w=2, a=0.4)
    qf = prog(t, t_f, 0.3)
    if qf > 0:
        st["overlay"].append(("sello", "FRENO DE EMERGENCIA", qf, 770, AMARILLO))
        st["shake"] = 6 * (1 - prog(t, t_f, 0.6))
    st["cam"] = (1.08, 270, 520)
    st["paso"] = ("✓", "NO SE CAE")


def esc_aire(L, e, t, D, T, st):
    cabina(L, T)
    persona(L, 100, 800 - 190 * 0.95, "de_pie", 0.95, ropa=PROTA, pelo=(60, 36, 24))
    q = prog(t, wt(e, "aire") - 0.3, 0.5)
    for k in range(10):
        u = (t * 0.6 + k / 10) % 1
        y = 300 + 40 * math.sin(k)
        x = 60 + k * 42
        linea(L, [(x, y + 20 + u * 60), (x + 8, y + 36 + u * 60), (x, y + 52 + u * 60)], (120, 200, 255), w=3,
              a=q * math.sin(u * math.pi))
        linea(L, [(170 + k * 20, 800 - u * 50), (176 + k * 20, 786 - u * 50)], (120, 200, 255), w=3, a=q * math.sin(u * math.pi) * 0.7)
    qh = prog(t, wt(e, "herméticos") - 0.3, 0.3)
    if qh > 0:
        st["overlay"].append(("sello", "SIEMPRE ENTRA AIRE", qh, 520, VERDE))
    st["paso"] = ("✓", "HAY AIRE")


def esc_like(L, e, t, D, T, st):
    cabina(L, T)
    persona(L, 100, 800 - 190 * 0.95, "de_pie", 0.95, ropa=PROTA, pelo=(60, 36, 24), boca=0.3)
    st["tinte"] = ((0, 0, 0), 0.45)
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    st["sin_cabecera"] = True


def esc_alarma(L, e, t, D, T, st):
    cabina(L, T)
    pul = prog(t, wt(e, "pulsa") - 0.3, 0.4)
    persona(L, lerp(100, 340, eio(pul)), 800 - 190 * 0.95, "pulsa" if pul >= 1 else "de_pie", 0.95, ropa=PROTA,
            pelo=(60, 36, 24))
    qb = prog(t, wt(e, "campana") - 0.3, 0.3)
    if qb > 0:
        for k in range(3):
            u = (t * 1.5 + k / 3) % 1
            circ(L, 441, 654, 16 + 50 * u, outline=AMARILLO, w=3, a=qb * (1 - u))
    qm = prog(t, wt(e, "segundos") - 0.4, 2.0)
    if 0 < qm < 1:
        rect(L, 380, 700, 500, 716, (0, 0, 0), a=0.6, r=8)
        rect(L, 382, 702, 382 + 116 * qm, 714, AMARILLO, r=6)
        texto(L, f"{qm * 3:.0f} s", 440, 734, 14, BLANCO, fuente="black")
    qv = prog(t, wt(e, "contacto") - 0.3, 0.4)
    if qv > 0:
        s = eob(qv)
        rect(L, 60, 360, 400, 440, BLANCO, a=qv, r=20)
        poly(L, [(330, 438), (360, 438), (380, 470)], BLANCO, a=qv)
        texto(L, "«Te oímos. Vamos", 230, 384, 20 * s, (30, 30, 30), a=qv, fuente="black", sombra=False)
        texto(L, "para allá.»", 230, 414, 20 * s, (40, 140, 80), a=qv, fuente="black", sombra=False)
    st["cam"] = (1.04 + 0.1 * eio(pul), 330, 560)
    st["paso"] = (1, "BOTÓN DE ALARMA")


def esc_puertas(L, e, t, D, T, st):
    if t < wt(e, "dos") - 0.5:
        cabina(L, T, puertas=0.15 + 0.05 * math.sin(t * 9))
        persona(L, 200, 800 - 190 * 0.95, "fuerza", 0.95, ropa=PROTA, pelo=(60, 36, 24))
        q = prog(t, wt(e, "forzar") - 0.3, 0.3)
        if q > 0:
            st["overlay"].append(("regla", "NO FUERCES LAS PUERTAS", 0, q, False))
    else:
        hueco(L, T, cab_y=470, desplaza=-130)
        # hueco bajo la cabina entre plantas
        qh = prog(t, wt(e, "hueco") - 0.4, 0.4)
        if qh > 0:
            rect(L, SHAFT_X0, 700, SHAFT_X1, 760, (0, 0, 0), a=qh * 0.7)
            texto(L, "↓ HUECO", 270, 730, 22, ROJO, a=qh, fuente="sym")
        st["overlay"].append(("sello", "ENTRE DOS PLANTAS", prog(t, wt(e, "dos") - 0.4, 0.3), 380, ROJO))
    st["paso"] = (2, "NO SALGAS SOLO")


def esc_movil(L, e, t, D, T, st):
    cabina(L, T)
    persona(L, 140, 800 - 190 * 0.95, "movil_oreja", 0.95, ropa=PROTA, pelo=(60, 36, 24))
    x0, y0 = 280, 380
    q = prog(t, wt(e, "uno") - 0.3, 0.4)
    if q > 0:
        s = eob(q)
        rect(L, x0, y0, x0 + 200 * s, y0 + 300 * s, (16, 16, 20), a=q, r=22)
        rect(L, x0 + 10 * s, y0 + 14 * s, x0 + 190 * s, y0 + 286 * s, (30, 120, 70), a=q, r=16)
        texto(L, "112", x0 + 100 * s, y0 + 70 * s, 44 * s, BLANCO, a=q, fuente="black", sombra=False)
        qd = prog(t, wt(e, "dirección") - 0.3, 0.3)
        if qd > 0:
            rect(L, x0 + 20, y0 + 140, x0 + 180, y0 + 230, BLANCO, a=qd, r=10)
            texto(L, "📍", x0 + 100, y0 + 160, 1, BLANCO, a=0)
            texto(L, "Calle Mayor, 14", x0 + 100, y0 + 172, 16, (30, 30, 30), a=qd, fuente="black", sombra=False)
            texto(L, "Ascensor B", x0 + 100, y0 + 200, 14, (90, 90, 90), a=qd, fuente="bold", sombra=False)
    st["paso"] = (3, "SI NADIE RESPONDE")


def esc_final(L, e, t, D, T, st):
    cabina(L, T, puertas=eio(prog(t, 0.2, 1.2)), fuera=(250, 240, 210))
    persona(L, lerp(100, 270, eio(prog(t, 1.0, 1.5))), 800 - 190 * 0.95, camina(t) if 1.0 < t < 2.5 else "de_pie", 0.95,
            ropa=PROTA, pelo=(60, 36, 24), boca=0.4)
    st["tinte"] = ((0, 0, 0), 0.35)
    st["overlay"].append(("final", t, prog(t, wt(e, "Guarda") - 0.2, 0.3), prog(t, wt(e, "mándaselo") - 0.2, 0.3),
                          prog(t, wt(e, "sígueme") - 0.2, 0.3)))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "cables": esc_cables, "freno": esc_freno, "aire": esc_aire, "like": esc_like,
         "alarma": esc_alarma, "puertas": esc_puertas, "movil": esc_movil, "final": esc_final}


def efectos(fx, E):
    g = E["gancho"]
    t_ = 0.0
    while t_ < g["dur"]:
        colocar(fx, latido(0.9), t_, 0.5)
        t_ += 0.62
    colocar(fx, braam(), g["t0"] + wt(g, "caer") - 0.3, 0.7)
    c = E["cables"]
    colocar(fx, pop(), c["t0"] + wt(c, "cables") - 0.3, 0.5)
    colocar(fx, pop(), c["t0"] + wt(c, "cada") - 0.2, 0.5)
    f = E["freno"]
    colocar(fx, ruido_filtrado(int(2.0 * SR), 30, 3) * np.linspace(0, 1, int(2.0 * SR)) * 0.4, f["t0"] + 0.3, 0.6)
    colocar(fx, golpe(), f["t0"] + wt(f, "freno") - 0.2, 0.9)
    colocar(fx, cristal() * 0.5, f["t0"] + wt(f, "freno") - 0.2, 0.5)
    a = E["aire"]
    colocar(fx, ruido_filtrado(int(a["dur"] * SR), 60, 5) * 0.12, a["t0"], 0.5)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.6)
    al = E["alarma"]
    colocar(fx, dingdong(), al["t0"] + wt(al, "campana") - 0.2, 0.7)
    colocar(fx, tono(2), al["t0"] + wt(al, "contacto") - 1.0, 0.5)
    p = E["puertas"]
    colocar(fx, golpe() * 0.5, p["t0"] + wt(p, "forzar") - 0.3, 0.6)
    colocar(fx, braam(), p["t0"] + wt(p, "hueco") - 0.4, 0.6)
    m = E["movil"]
    colocar(fx, tono(2), m["t0"] + wt(m, "uno") - 0.2, 0.5)
