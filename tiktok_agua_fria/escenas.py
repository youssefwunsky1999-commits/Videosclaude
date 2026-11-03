# --- Escenas del TikTok «Si caes al agua fría, NO nades» ---
NIVEL = 470          # superficie del agua
POSES.update({
    "nada1": dict(rodilla=(-70, 10), pie=(-150, 20), cuello=(100, -30), cabeza=(140, -44), codo=(150, -70), mano=(200, -60),
                  codo2=(70, 20), mano2=(30, 50)),
    "nada2": dict(rodilla=(-70, -6), pie=(-150, -16), cuello=(100, -30), cabeza=(140, -44), codo=(70, 20), mano=(30, 50),
                  codo2=(150, -70), mano2=(200, -60)),
    "lanza": dict(rodilla=(10, 94), pie=(14, 190), cuello=(6, -150), cabeza=(14, -196), codo=(50, -170), mano=(90, -200),
                  codo2=(-30, -90), mano2=(-40, -40)),
    "grita": dict(rodilla=(10, 94), pie=(14, 190), cuello=(8, -150), cabeza=(16, -196), codo=(50, -150), mano=(100, -176),
                  codo2=(-10, -80), mano2=(-4, -20)),
})


def agua(L, T, nivel=NIVEL, cielo=(170, 206, 232), oscura=False):
    rect(L, 0, 0, W, nivel, cielo)
    circ(L, 430, 150, 40, fill=(255, 240, 200), a=0.8)
    for k in range(10):
        y0 = nivel + k * (H - nivel) / 10
        c = mezcla((60, 130, 170), (14, 40, 70), k / 9)
        if oscura:
            c = mezcla(c, (10, 20, 40), 0.4)
        rect(L, 0, y0, W, y0 + (H - nivel) / 10 + 1, c)
    pts = [(x, nivel + 6 * math.sin(T * 2 + x / 40)) for x in range(0, W + 10, 10)]
    poly(L, pts + [(W, nivel + 30), (0, nivel + 30)], (90, 160, 200))
    linea(L, pts, (220, 240, 255), w=2, a=0.8)


def burbujas(L, x, y, T, n=10, a=1.0):
    for k in range(n):
        u = (T * 0.8 + k / n) % 1
        circ(L, x + 14 * math.sin(k * 2 + T * 3), y - 200 * u, 3 + (k % 3) * 2, outline=(220, 240, 255), w=2, a=a * (1 - u))


def estrella(L, x, y, T, s=1.0, a=1.0):
    """Persona flotando boca arriba vista desde arriba: brazos y piernas abiertos."""
    rr = lambda v: v * s  # noqa: E731
    mov = 4 * math.sin(T * 2)
    capsula(L, (x, y + rr(30)), (x - rr(60), y + rr(150)), rr(30), PROTA[2], a)
    capsula(L, (x, y + rr(30)), (x + rr(60), y + rr(150)), rr(30), PROTA[2], a)
    capsula(L, (x, y - rr(50)), (x - rr(110), y - rr(110) + mov), rr(22), PROTA[0], a)
    capsula(L, (x, y - rr(50)), (x + rr(110), y - rr(110) - mov), rr(22), PROTA[0], a)
    circ(L, x - rr(116), y - rr(114) + mov, rr(12), fill=PIEL, a=a)
    circ(L, x + rr(116), y - rr(114) - mov, rr(12), fill=PIEL, a=a)
    capsula(L, (x, y + rr(30)), (x, y - rr(70)), rr(58), PROTA[0], a)
    circ(L, x, y - rr(110), rr(34), fill=PIEL, a=a)
    L.d.chord(P(x - rr(36), y - rr(150), x + rr(36), y - rr(90)), 180, 360, fill=L.c((60, 36, 24), a))


def esc_gancho(L, e, t, D, T, st):
    agua(L, T)
    caida = eio(prog(t, 0, 0.6))
    y = lerp(470, 640, caida)
    if caida < 1:
        persona(L, 270, y - 190 * 0.85, "grita", 0.85, ropa=PROTA, pelo=(60, 36, 24), ojos=1.6, boca=0.8)
    else:
        x = 270 + 30 * math.sin(t * 5)
        persona(L, x, 560, pose_mix("nada1", "nada2", 0.5 + 0.5 * math.sin(t * 9)), 0.9, ropa=PROTA, pelo=(60, 36, 24),
                ojos=1.6, boca=0.6)
        burbujas(L, x + 80, 620, T, 8)
    if t < 1.0:
        for k in range(12):
            ang = k / 12 * math.pi
            r = 60 + 160 * prog(t, 0.5, 0.5)
            circ(L, 270 + r * math.cos(ang), NIVEL - r * 0.7 * math.sin(ang), 8, fill=(230, 245, 255),
                 a=1 - prog(t, 0.5, 0.5))
    st["cam"] = (1.08 - 0.04 * eio(t / D), 270, 500)
    st["alarma"] = t
    st["overlay"].append(("titular", t, "SI CAES AL AGUA FRÍA…", "NO NADES", 1.0))
    st["sin_cabecera"] = True


def esc_choque(L, e, t, D, T, st):
    agua(L, T, oscura=True)
    x = 260 + 20 * math.sin(t * 6)
    persona(L, x, 540, "nada1", 0.9, ropa=PROTA, pelo=(60, 36, 24), ojos=1.8, boca=0.9)
    burbujas(L, x + 90, 600, T, 14)
    lat = 0.5 + 0.5 * math.sin(T * 14)
    for j, (pal, txt) in enumerate((("jadeas", "JADEO SIN CONTROL"), ("corazón", "CORAZÓN DISPARADO"), ("pánico", "PÁNICO"))):
        q = prog(t, wt(e, pal) - 0.3, 0.3)
        st["overlay"].append(("regla", txt, j, q, False))
    qc = prog(t, wt(e, "corazón") - 0.3, 0.3)
    if qc > 0:
        corazon(L, 440, 700, 30 * (1 + 0.25 * lat), ROJO, a=qc)
    st["shake"] = 3
    st["tinte"] = ((20, 40, 90), 0.15)
    st["paso"] = ("!", "EL CHOQUE POR FRÍO")


def esc_minuto(L, e, t, D, T, st):
    agua(L, T)
    persona(L, 270, 560, pose_mix("nada1", "nada2", 0.5), 0.9, ropa=PROTA, pelo=(60, 36, 24), ojos=1.2)
    q = prog(t, wt(e, "minuto") - 0.4, 0.4)
    seg = int(60 * prog(t, wt(e, "minuto") - 0.4, D - wt(e, "minuto")))
    if q > 0:
        cx, cy, r = 270, 380, 80
        circ(L, cx, cy, r + 10, fill=BLANCO, a=q)
        circ(L, cx, cy, r, fill=(30, 34, 46), a=q)
        L.d.pieslice(P(cx - r, cy - r, cx + r, cy + r), -90, -90 + 6 * seg, fill=L.c(VERDE, q))
        circ(L, cx, cy, r * 0.7, fill=(30, 34, 46), a=q)
        texto(L, f"{seg} s", cx, cy, 40, BLANCO, a=q, fuente="black")
    qa = prog(t, wt(e, "aguantar") - 0.3, 0.3)
    if qa > 0:
        st["overlay"].append(("sello", "AGUANTA 1 MINUTO", qa, 780, AMARILLO))
    st["paso"] = (1, "SOLO 1 MINUTO")


def esc_flota(L, e, t, D, T, st):
    # vista cenital del agua
    rect(L, 0, 0, W, H, (40, 110, 160))
    for k in range(14):
        y = (k * 80 + T * 12) % (H + 80) - 40
        linea(L, [(x, y + 6 * math.sin(x / 30 + T)) for x in range(0, W + 10, 20)], (90, 160, 200), w=2, a=0.5)
    q = eio(prog(t, 0.2, 1.2))
    estrella(L, 270, 700, T, s=lerp(0.6, 1.15, q))
    for j, (pal, txt) in enumerate((("boca", "BOCA ARRIBA"), ("cabeza", "CABEZA ATRÁS"), ("estrella", "COMO UNA ESTRELLA"))):
        qq = prog(t, wt(e, pal) - 0.3, 0.3)
        st["overlay"].append(("chip", txt, j, qq))
    qr = prog(t, wt(e, "despacio") - 0.3, 0.4)
    if qr > 0:
        st["overlay"].append(("sello", "RESPIRA DESPACIO", qr, 880, VERDE))
    st["paso"] = (2, "FLOTA")


def esc_like(L, e, t, D, T, st):
    agua(L, T)
    st["tinte"] = ((0, 0, 0), 0.45)
    st["overlay"].append(("like", t, wt(e, "like") - 0.3))
    st["sin_cabecera"] = True


def esc_despues(L, e, t, D, T, st):
    agua(L, T)
    # boya / roca
    rect(L, 400, NIVEL - 30, 520, NIVEL + 40, (110, 100, 90), r=30)
    q = prog(t, wt(e, "ayuda") - 0.3, 0.3)
    x = lerp(150, 330, eio(prog(t, wt(e, "nada") - 0.3, 2.0)))
    persona(L, x, 540, pose_mix("nada1", "nada2", 0.5 + 0.5 * math.sin(t * 4)), 0.85, ropa=PROTA, pelo=(60, 36, 24), boca=0.5)
    if q > 0:
        texto(L, "¡AYUDA!", 230, 425, 40 * eob(q) + 1, BLANCO, a=q, fuente="black")
    st["overlay"].append(("chip", "AGÁRRATE A ALGO", 0, prog(t, wt(e, "agarrarte") - 0.3, 0.3)))
    st["paso"] = (3, "DESPUÉS")


def esc_otro(L, e, t, D, T, st):
    N2 = 620
    agua(L, T, nivel=N2)
    rect(L, 0, N2 - 10, 200, H, (200, 180, 140))
    rect(L, 0, N2 - 16, 200, N2 - 4, (170, 150, 110))
    lanza = prog(t, wt(e, "lánzale") - 0.3, 0.8)
    persona(L, 90, N2 - 10 - 190 * 0.7, "lanza" if lanza > 0 else "movil_oreja", 0.7,
            ropa=((90, 150, 210), (70, 120, 180), (50, 50, 60), (40, 40, 50)), pelo=(150, 100, 50))
    persona(L, 400, N2 + 70, "nada1", 0.8, ropa=PROTA, pelo=(60, 36, 24), flip=True)
    if lanza > 0:
        bx = lerp(170, 370, lanza)
        by = lerp(N2 - 200, N2 + 20, lanza) - 100 * math.sin(lanza * math.pi)
        circ(L, bx, by, 30, fill=(240, 90, 60))
        circ(L, bx, by, 14, fill=(60, 130, 170))
    qn = prog(t, wt(e, "tires") - 0.3, 0.3)
    st["overlay"].append(("regla", "NO TE TIRES", 0, qn, False))
    q1 = prog(t, wt(e, "uno") - 0.3, 0.3)
    st["overlay"].append(("regla", "LLAMA AL 112", 1, q1, True))
    st["overlay"].append(("regla", "LÁNZALE ALGO QUE FLOTE", 2, prog(t, wt(e, "flote") - 0.3, 0.3), True))
    st["paso"] = (4, "SI VES A ALGUIEN")


def esc_grados(L, e, t, D, T, st):
    agua(L, T, cielo=(250, 220, 160))
    # termómetro
    x, y0, y1 = 270, 560, 880
    rect(L, x - 22, y0, x + 22, y1, BLANCO, r=22)
    circ(L, x, y1, 40, fill=BLANCO)
    q = prog(t, wt(e, "quince") - 0.4, 0.8)
    nivel = lerp(y1, y1 - 170, eo3(q))
    rect(L, x - 12, nivel, x + 12, y1, (90, 170, 255), r=10)
    circ(L, x, y1, 30, fill=(90, 170, 255))
    if q > 0:
        texto(L, "15 °C", x + 50, y1 - 170, 34, BLANCO, a=q, fuente="black", anchor="lm")
        linea(L, [(x + 22, y1 - 170), (x + 44, y1 - 170)], BLANCO, w=3, a=q)
    qi = prog(t, wt(e, "invierno") - 0.3, 0.3)
    if qi > 0:
        st["overlay"].append(("sello", "TAMBIÉN EN VERANO", qi, 400, AMARILLO))
    st["paso"] = ("!", "OJO")


def esc_final(L, e, t, D, T, st):
    rect(L, 0, 0, W, H, (40, 110, 160))
    estrella(L, 270, 640, T, s=1.1)
    st["tinte"] = ((0, 0, 0), 0.35)
    st["overlay"].append(("final", t, prog(t, wt(e, "Guarda") - 0.2, 0.3), prog(t, wt(e, "mándaselo") - 0.2, 0.3),
                          prog(t, wt(e, "sígueme") - 0.2, 0.3)))
    st["sin_cabecera"] = True


FUNCS = {"gancho": esc_gancho, "choque": esc_choque, "minuto": esc_minuto, "flota": esc_flota, "like": esc_like,
         "despues": esc_despues, "otro": esc_otro, "grados": esc_grados, "final": esc_final}


def olas(dur, seed=3):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    return (ruido_filtrado(n, 80, seed) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * tt)) * 0.25).astype(np.float32)


def efectos(fx, E):
    colocar(fx, olas(TOTAL + 1), 0.0, 0.6)
    g = E["gancho"]
    colocar(fx, splash(), g["t0"] + 0.5, 0.9)
    colocar(fx, braam(), g["t0"] + wt(g, "nades") - 0.3, 0.6)
    c = E["choque"]
    t_ = c["t0"]
    while t_ < c["t0"] + c["dur"]:
        colocar(fx, latido(1.0), t_, 0.6)
        t_ += 0.45
    for k in range(10):
        colocar(fx, burbuja(k), c["t0"] + k * 0.5, 0.4)
    m = E["minuto"]
    t0 = m["t0"] + wt(m, "minuto") - 0.4
    k = 0
    while t0 + k * 0.5 < m["t0"] + m["dur"]:
        colocar(fx, tic(), t0 + k * 0.5, 0.4)
        k += 1
    f = E["flota"]
    for pal in ("boca", "cabeza", "estrella", "despacio"):
        colocar(fx, pop(), f["t0"] + wt(f, pal) - 0.3, 0.4)
    lk = E["like"]
    colocar(fx, pop(), lk["t0"] + wt(lk, "like") - 0.3, 0.6)
    o = E["otro"]
    colocar(fx, tono(2), o["t0"] + wt(o, "uno") - 0.2, 0.4)
    colocar(fx, whoosh(9, 0.6), o["t0"] + wt(o, "lánzale") - 0.3, 0.5)
    colocar(fx, splash() * 0.5, o["t0"] + wt(o, "lánzale") + 0.5, 0.5)
    gr = E["grados"]
    colocar(fx, golpe() * 0.5, gr["t0"] + wt(gr, "quince") - 0.4, 0.5)
